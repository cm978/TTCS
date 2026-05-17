from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./ttcs.db"
    redis_url: str = "redis://127.0.0.1:6379/0"
    jwt_secret_key: str = Field(default="dev-only-change-me", min_length=8)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

