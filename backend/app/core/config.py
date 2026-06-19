"""
Trader Copilot AI — Configuration Management

Uses Pydantic Settings to load configuration from environment variables.
All config is centralized here for type-safe access across the application.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────────
    app_name: str = "Trader Copilot AI"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"  # development | staging | production

    # ── Server ───────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Database ─────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/trader_copilot"
    database_echo: bool = False

    # ── JWT Authentication ───────────────────────────────────
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: List[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    # ── Google Gemini AI ─────────────────────────────────────
    gemini_api_key: str = ""

    # ── Binance API ──────────────────────────────────────────
    binance_base_url: str = "https://api.binance.com"

    # ── Screenshot Storage ───────────────────────────────────
    screenshot_storage_path: str = "./screenshots"
    max_screenshot_size_mb: int = 10

    # ── Logging ──────────────────────────────────────────────
    log_level: str = "INFO"
    log_format: str = "json"  # json | console

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance. Call once at startup."""
    return Settings()
