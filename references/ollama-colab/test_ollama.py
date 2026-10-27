"""Run locally using .env beside this file (requires requests and python-dotenv)."""

import os
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    sys.exit("Install the dependencies first: python -m pip install requests python-dotenv")


ENV_PATH = Path(__file__).resolve().parent / ".env"
CONNECT_TIMEOUT = 10
API_TIMEOUT = 30
CHAT_TIMEOUT = 600  # A cold model can take several minutes to load.


def load_config():
    """Load the script's .env and reject incomplete configuration before HTTP."""
    if not ENV_PATH.is_file():
        raise ValueError("Missing .env beside test_ollama.py. Copy .env.example to .env and edit it.")
    # Explicit path avoids loading an unrelated .env from the current directory.
    # File values override existing variables; passwords are not interpolated.
    try:
        load_dotenv(dotenv_path=ENV_PATH, override=True, interpolate=False)
    except (OSError, UnicodeError):
        raise ValueError("Could not read .env. Check its permissions and save it as UTF-8.") from None
    required = ("OLLAMA_URL", "OLLAMA_USERNAME", "OLLAMA_PASSWORD", "OLLAMA_MODEL")
    missing = [name for name in required if not os.getenv(name, "").strip()]
    if missing:
        raise ValueError("Set these required variables in .env: " + ", ".join(missing))

    url = os.environ["OLLAMA_URL"].strip()
    username = os.environ["OLLAMA_USERNAME"].strip()
    password = os.environ["OLLAMA_PASSWORD"]  # Preserve intentional spaces.
    model = os.environ["OLLAMA_MODEL"].strip()
    try:
        parts = urlsplit(url)
        valid_url = (
            parts.scheme == "https"
            and parts.hostname
            and parts.username is None
            and parts.password is None
            and parts.port in (None, 443)
            and parts.path in ("", "/")
            and not parts.query
            and not parts.fragment
            and not any(character.isspace() for character in url)
            and "\\" not in url
        )
    except ValueError:
        valid_url = False
    if not valid_url:
        raise ValueError("OLLAMA_URL must be an HTTPS base URL without paths, queries, or login details.")
    if parts.hostname == "your-domain.ngrok-free.dev" or password == "your-password":
        raise ValueError("Replace the example URL and password in .env with your Colab tunnel settings.")
    if not username.isascii() or not username.isprintable() or ":" in username:
        raise ValueError("OLLAMA_USERNAME must contain printable ASCII characters without a colon.")
    if not password.isascii() or not password.isprintable():
        raise ValueError("OLLAMA_PASSWORD must contain printable ASCII characters matching Colab.")
    if any(character.isspace() for character in model):
        raise ValueError("OLLAMA_MODEL must be an exact model name without whitespace.")
    return url.rstrip("/"), username, password, model


def check_status(response):
    """Explain failures without printing response bodies or request credentials."""
    status = response.status_code
    if status in (401, 403):
        raise ValueError(
            "Authentication failed or access was denied. Use the API password "
            "created in Colab (not the ngrok authtoken), and check OLLAMA_USERNAME in .env."
        )
    if response.headers.get("ngrok-error-code") or status in (404, 410, 502, 503, 504):
        raise ValueError(
            "The tunnel, server, or requested model is unavailable. Check that "
            "Colab is connected, Ollama is running, and the model is downloaded. "
            "If the ngrok session expired, recreate it and use its current URL."
        )
    if 300 <= status < 400:
        raise ValueError("The URL redirected. Copy the current HTTPS URL from Colab.")
    if status == 429:
        raise ValueError("A service limit was reached. Wait and check your ngrok quota.")
    if status != 200:
        raise ValueError(
            f"The API returned HTTP {status}. Check the model and Ollama log in Colab."
        )


def read_json(response):
    check_status(response)
    try:
        data = response.json()
    except ValueError:
        raise ValueError(
            "Expected JSON but received another page. The ngrok session may have "
            "expired; check Colab and copy the current URL."
        ) from None
    if not isinstance(data, dict) or "error" in data:
        raise ValueError("Ollama returned an unexpected response. Check its log in Colab.")
    return data


def verify_model(data, model_name):
    """Require the configured model to be downloaded on the server."""
    models = data.get("models")
    if not isinstance(models, list):
        raise ValueError("The server did not return an Ollama model list.")
    names = [
        model["name"] for model in models
        if isinstance(model, dict) and isinstance(model.get("name"), str)
        and model["name"]
    ]
    if not names:
        raise ValueError("No models are downloaded. Run the model download cell in Colab.")

    if model_name not in names:
        raise ValueError(
            "OLLAMA_MODEL is not available on the server. Use an exact name from "
            "ollama list in Colab, or download that model there first."
        )
    print("Configured model is available.")


def main():
    url, username, password, model = load_config()

    with requests.Session() as session:
        # Avoid .netrc silently adding credentials to the unauthenticated test.
        # This also disables environment proxies; use a direct internet connection.
        session.trust_env = False
        session.headers.update({"ngrok-skip-browser-warning": "true"})

        print("Checking connectivity and authentication...")
        response = session.get(
            f"{url}/api/tags", timeout=(CONNECT_TIMEOUT, API_TIMEOUT),
            allow_redirects=False,
        )
        if response.status_code != 401:
            check_status(response)
            raise ValueError(
                "Security check failed: the endpoint allowed access without a "
                "password. Stop the tunnel and rerun its protected setup in Colab."
            )

        # Read credentials from .env; never print them or write them elsewhere.
        session.auth = (username, password)
        del username
        del password
        try:
            response = session.get(
                f"{url}/api/tags", timeout=(CONNECT_TIMEOUT, API_TIMEOUT),
                allow_redirects=False,
            )
            data = read_json(response)
            print("Authentication succeeded.")
            verify_model(data, model)

            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": "Explain what an API is in two short sentences.",
                }],
                "stream": False,  # Return one complete JSON response.
                "options": {"num_ctx": 4096, "num_predict": 1024},
            }
            # The reference models use different thinking controls.
            if model.split(":")[0] == "gpt-oss":
                payload["think"] = "low"
            elif model.split(":")[0] == "qwen3.5":
                payload["think"] = False

            print("Sending a chat request; the first response may take a few minutes...")
            start = time.perf_counter()
            response = session.post(
                f"{url}/api/chat", json=payload,
                timeout=(CONNECT_TIMEOUT, CHAT_TIMEOUT), allow_redirects=False,
            )
            elapsed = time.perf_counter() - start
            result = read_json(response)
            message = result.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, str):
                raise ValueError("Ollama did not return a chat message. Check the model in Colab.")
            print("\nModel response:")
            print(content.strip() or "(No final text. Try a higher num_predict or a smaller model.)")
            if result.get("done_reason") == "length":
                print("The token limit was reached; the answer may be incomplete.")
            print(f"\nExecution time: {elapsed:.2f} seconds (network + loading + generation)")
        finally:
            session.auth = None


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
    except requests.exceptions.SSLError:
        print("HTTPS certificate verification failed. Check the URL and system clock; keep TLS verification enabled.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("The request timed out. Check Colab and Ollama; try a smaller model or retry after loading finishes.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Could not connect. Check your internet connection and Colab runtime. Recreate an expired ngrok session.")
        sys.exit(1)
    except requests.exceptions.RequestException:
        print("The HTTP request failed. Check Colab and the current ngrok URL, then retry.")
        sys.exit(1)
    except ValueError as error:
        print(error)
        sys.exit(1)
