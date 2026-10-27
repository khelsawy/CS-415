"""SovereignEG provider implementation."""

import json
from typing import Any, Iterator
import requests
from ..config import LLMConfig


class SovereignProvider:
    """Communicate with SovereignEG Chat Completions API."""

    def __init__(self, config: LLMConfig):
        self.config = config

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Send messages to SovereignEG."""

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
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        return response.json()["choices"][0]["message"]


    def chat_stream(self, messages: list[dict]) -> Iterator[str]:
        """Yield generated reply fragments from SovereignEG using SSE."""
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": True,
        }

        with requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            json=payload,
            stream=True,
            timeout=120,
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines(decode_unicode=True):
                if isinstance(line, bytes):
                    line = line.decode("utf-8")
                if not line or not line.startswith("data:"):
                    continue

                data = line[5:].strip()
                if data == "[DONE]":
                    break
                if not data:
                    continue

                chunk = json.loads(data)
                choices = chunk.get("choices") or []
                if not choices:
                    continue  # Some streaming chunks contain usage only.

                content = (choices[0].get("delta") or {}).get("content")
                if isinstance(content, str) and content:
                    yield content
