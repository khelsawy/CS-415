"""Ollama provider implementation."""

from typing import Any

import requests

from ..config import LLMConfig


class OllamaProvider:
    """Communicate with Ollama locally or through ngrok."""

    def __init__(self, config: LLMConfig):
        self.config = config

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Send messages to Ollama and return the assistant message."""

        url = f"{self.config.base_url.rstrip('/')}/api/chat"

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_ctx": 8192,
            },
        }

        if tools is not None:
            payload["tools"] = tools

        headers = {}
        auth = None

        if self.config.provider == "ollama_colab":
            if not url.startswith("https://"):
                raise ValueError("Colab endpoint must use HTTPS")

            auth = (
                self.config.username,
                self.config.password,
            )

            headers["ngrok-skip-browser-warning"] = "true"

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth,
            timeout=600,
        )

        response.raise_for_status()

        return response.json()["message"]