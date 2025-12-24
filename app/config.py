"""Configuration helpers for Azure OpenAI client."""
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field, AnyHttpUrl


class Settings(BaseSettings):
    azure_openai_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: AnyHttpUrl = Field(..., env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field("2024-02-15-preview", env="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Optional[Settings]:
    """Load settings; return None when mandatory env vars are missing."""
    try:
        return Settings()
    except Exception:
        # Environment may not be configured in local/test contexts.
        return None
