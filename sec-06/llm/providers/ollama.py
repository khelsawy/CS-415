"""Ollama provider implementation."""

from typing import Any
from uuid import uuid4

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
            "messages": self._native_messages(messages),
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

        message = response.json()["message"]

        # Ollama identifies tool results by name. The shared agent uses call IDs.
        for call in message.get("tool_calls") or []:
            if not call.get("id"):
                call["id"] = uuid4().hex

        return message

    @staticmethod
    def _native_messages(messages: list[dict]) -> list[dict]:
        """Translate shared tool references to Ollama's native message format."""

        tool_names = {}
        native_messages = []

        for message in messages:
            calls = message.get("tool_calls") or []
            if calls:
                for call in calls:
                    tool_names[call["id"]] = call["function"]["name"]

                message = {
                    **message,
                    "tool_calls": [
                        {key: value for key, value in call.items() if key != "id"}
                        for call in calls
                    ],
                }

            if message["role"] == "tool":
                message = {
                    "role": "tool",
                    "content": message["content"],
                    "tool_name": tool_names[message["tool_call_id"]],
                }

            native_messages.append(message)

        return native_messages
