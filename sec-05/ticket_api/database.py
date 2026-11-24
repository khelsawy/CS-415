import os

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(ENV_PATH)


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Create and return a Supabase client."""

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Missing Supabase configuration."
        )

    client = create_client(url, key)

    return client