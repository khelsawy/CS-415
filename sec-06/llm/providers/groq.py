"""Groq provider implementation."""

from typing import Any

import requests

from ..config import LLMConfig


class GroqProvider:
    """Communicate with the Groq Chat Completions API."""

    def __init__(self, config: LLMConfig):
        self.config = config

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Send messages to Groq and return the assistant message."""

        url = (
            f"{self.config.base_url.rstrip('/')}"
            "/chat/completions"
        )

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
        }

        if tools is not None:
            payload["tools"] = tools

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
            },
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        return response.json()["choices"][0]["message"]