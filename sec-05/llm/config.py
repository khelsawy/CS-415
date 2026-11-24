"""Configuration management for LLM providers."""

import os

from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(ENV_PATH)


@dataclass(frozen=True)
class LLMConfig:
    """Store configuration for the selected LLM provider."""

    provider: str
    model: str
    base_url: str

    api_key: str | None = None
    username: str | None = None
    password: str | None = None


def required_env(name: str) -> str:
    """Read a required environment variable."""

    value = os.getenv(name)

    if not value or not value.strip():
        raise ValueError(
            f"Missing environment variable: {name}"
        )

    return value


def load_config() -> LLMConfig:
    """Load and validate the selected provider configuration."""

    provider = required_env("LLM_PROVIDER").lower()

    if provider == "ollama_local":
        return LLMConfig(
            provider=provider,
            model=required_env("OLLAMA_LOCAL_MODEL"),
            base_url=required_env("OLLAMA_LOCAL_URL"),
        )

    elif provider == "ollama_colab":
        return LLMConfig(
            provider=provider,
            model=required_env("OLLAMA_COLAB_MODEL"),
            base_url=required_env("OLLAMA_COLAB_URL"),
            username=required_env("OLLAMA_COLAB_USERNAME"),
            password=required_env("OLLAMA_COLAB_PASSWORD"),
        )

    elif provider == "groq":
        return LLMConfig(
            provider=provider,
            model=required_env("GROQ_MODEL"),
            base_url=required_env("GROQ_BASE_URL"),
            api_key=required_env("GROQ_API_KEY"),
        )

    elif provider == "sovereign":
        return LLMConfig(
            provider=provider,
            model=required_env("SOVEREIGN_MODEL"),
            base_url=required_env("SOVEREIGN_BASE_URL"),
            api_key=required_env("SOVEREIGN_API_KEY"),
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )