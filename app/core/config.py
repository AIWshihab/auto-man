from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Autonomous Affiliate Growth Engine")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/affiliate_engine",
    )
    app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    google_trends_enabled: bool = os.getenv("GOOGLE_TRENDS_ENABLED", "true").lower() == "true"


settings = Settings()
