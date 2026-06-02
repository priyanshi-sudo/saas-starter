"""Application settings."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/saas"
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"

    # Supabase auth — JWKS endpoint used to verify RS256 access tokens.
    supabase_jwks_url: str = "https://example.supabase.co/auth/v1/.well-known/jwks.json"

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Email (Resend)
    resend_api_key: str = ""
    email_from: str = "SaaS Starter <noreply@example.com>"

    # Background jobs
    redis_url: str = "redis://localhost:6379"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
