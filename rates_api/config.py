# config.py
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="app.dev.env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: PostgresDsn

    redis_url: str
    redis_prefix: str = "fastapi-cache"

    cache_default_expire: int = 300

    min_prices_per_day: int = 3
    max_days_interval: int = 31

    log_level: str = "INFO"


settings = Settings()
