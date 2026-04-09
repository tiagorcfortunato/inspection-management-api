"""
app.core.config — Environment-Based Application Settings

Uses Pydantic Settings to load configuration from environment variables
and .env files. Sensitive values (API keys) use SecretStr to prevent
accidental logging. Provides typed, validated access to all config values.
"""

from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_EMAIL: str | None = None
    ALLOWED_ORIGINS: list[str] = ["https://inspection-dashboard.vercel.app"]

    GROQ_API_KEY: SecretStr | None = None
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: SecretStr | None = None
    LANGSMITH_PROJECT: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
