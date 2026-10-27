"""Unified client for LLM providers."""

from typing import Any, Iterator

from .config import load_config
from .providers.ollama import OllamaProvider
from .providers.groq import GroqProvider
from .providers.sovereign import SovereignProvider

class LLMClient:
    """Provide one interface for communicating with LLMs."""

    def __init__(self):
        self.config = load_config()

        if self.config.provider in (
            "ollama_local",
            "ollama_colab",
        ):
            self.provider = OllamaProvider(self.config)
        
        elif self.config.provider == "groq":
            self.provider = GroqProvider(self.config)
        elif self.config.provider == "sovereign":
            self.provider = SovereignProvider(self.config)
        else:
            raise NotImplementedError(
                f"Provider '{self.config.provider}' "
                "is not implemented yet."
            )

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Generate a response using the selected provider."""

        return self.provider.chat(
            messages=messages,
            tools=tools,
        )

    def chat_stream(self, messages: list[dict]) -> Iterator[str]:
        """Stream a response using the selected provider (if supported)."""
        stream_method = getattr(self.provider, "chat_stream", None)
        if stream_method is None:
            raise NotImplementedError(
                f"Streaming for '{self.config.provider}' is not implemented yet."
            )
        return stream_method(messages=messages)