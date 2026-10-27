# Ollama + Google Colab

Run a model in Colab and call it from a local Python script:

```text
Colab → Ollama server → downloaded model
            ↕
     ngrok (HTTPS + authentication)
            ↕
     Local test_ollama.py + .env → model response
```

- [Ollama_Colab.ipynb](Ollama_Colab.ipynb): upload to Colab and run Steps 1–8 in order. It checks hardware, installs Ollama, starts the server, downloads and tests a model, and verifies a protected tunnel.
- [test_ollama.py](test_ollama.py): run on your **own computer**, with Python 3.10+, `requests`, and `python-dotenv`. It reads `.env` beside the script automatically, checks authentication and model availability, and prints a chat response and execution time. It has no interactive prompts. Your computer does not need a GPU or Ollama.
- [.env.example](.env.example): shareable configuration template. `.env` is your private local copy and is ignored by Git.

The notebook's default model is `qwen3.5:4b`; its `small` profile uses `qwen3.5:0.8b`. The optional instructor profile uses `gpt-oss:120b` with an 80 GB-class GPU. That profile requires at least 75 GiB free on one GPU and 80 GiB free disk. An A100 40 GB is insufficient for this setup, and Colab does not guarantee suitable hardware.

## Configure the local client

Keep Colab connected after Step 8. **Skip cleanup until after your local test; do not run the entire notebook with “Run all.”**

From the repository root, create your local configuration if you do not already have one:

```bash
cp references/ollama-colab/.env.example references/ollama-colab/.env
```

Windows PowerShell:

```powershell
Copy-Item references/ollama-colab/.env.example references/ollama-colab/.env
```

This working copy already includes an ignored `.env` containing placeholders only. Edit it rather than copying over a configuration you have already filled in. For a downloaded copy, save both `test_ollama.py` and `.env.example` into the same folder, then copy `.env.example` to `.env` there. The instructor must publish the materials before GitHub downloads are available.

Open `.env` in your editor and replace the placeholders:

| Variable | Value to use |
|---|---|
| `OLLAMA_URL` | Current **Protected API URL** from Colab, starting with `https://`; no `/api/chat`, query string, or credentials. |
| `OLLAMA_USERNAME` | Username printed by Colab. The notebook uses `colab`. |
| `OLLAMA_PASSWORD` | API password created in notebook Step 8, **not** the ngrok authtoken. |
| `OLLAMA_MODEL` | Exact downloaded model name from `ollama list`: `qwen3.5:4b`, `qwen3.5:0.8b`, or `gpt-oss:120b`, matching your runtime. |

The template selects `gpt-oss:120b`; **students using the default notebook profile must change `OLLAMA_MODEL` to `qwen3.5:4b`**. For passwords containing spaces or `#`, quote the value in `.env` using single or double quotes. Use a password that you can quote without changing its characters.

The script loads this specific file even when launched from another directory. Values in `.env` override existing environment variables with the same names; `${...}` expansion is disabled so password characters are preserved. Missing, empty, invalid, or unchanged example settings fail before any HTTP request.

## Run the local client

From the repository root, using uv:

```bash
uv run --no-project --with requests --with python-dotenv python references/ollama-colab/test_ollama.py
```

Alternatively, open a terminal in `references/ollama-colab/` (or the folder containing your downloaded files).

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install requests python-dotenv
python test_ollama.py
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install requests python-dotenv
.\.venv\Scripts\python.exe test_ollama.py
```

The client expects HTTP 401 without credentials, then authenticates and calls `GET /api/tags` to verify `OLLAMA_MODEL` exists. It sends a non-streaming `POST /api/chat` and prints the final answer and elapsed time, including network travel, loading, and generation. The chat read timeout is 600 seconds.

## Secrets, troubleshooting, and cleanup

The **ngrok authtoken** stays in Colab. Your local `.env` stores the separate API password in plain text: keep it private, never commit it, and never share it with the notebook. `.env.example` contains placeholders only and remains eligible for Git tracking. The script does not print credentials or write them elsewhere. The tunnel protects the entire Ollama API, including model management; clear notebook outputs before sharing.

For missing/invalid configuration, edit `.env` beside the script. For 401/403, check its username and API password. For an unavailable model, match `OLLAMA_MODEL` to `ollama list` or download it in Colab. For an expired session, recreate the tunnel and update `.env` with the current URL and password. For timeouts, check Colab/Ollama or use a smaller model. The client skips ngrok's browser warning, rejects redirects, verifies TLS, and uses direct internet access without environment proxies or `.netrc` credentials.

After testing, run the notebook's cleanup cell, then **Runtime → Disconnect and delete runtime**. Files and models in Colab are temporary. Follow [Colab's usage restrictions](https://research.google.com/colaboratory/faq.html#limitations-and-restrictions) for this interactive exercise.

These materials demonstrate API calls. Local checks do not establish that a live Colab/GPU/ngrok run succeeds; an instructor should run the demonstration before class.
