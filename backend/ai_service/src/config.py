from functools import lru_cache
from typing import Annotated
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from shared.src.config import DatabaseUrl, RedisUrl


class Settings(BaseSettings):
    ENV: str = "dev"

    DATABASE_URL: Annotated[DatabaseUrl, Field(..., env="DATABASE_URL")]
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    REDIS_URL: Annotated[RedisUrl, Field(..., env="REDIS_URL")]

    JWT_SECRET: str | None = None
    OPENAI_API_KEY: str | None = None
    ELEVENLABS_API_KEY: str | None = None

    # New: flag to check if running in dev mode
    @computed_field
    @property
    def DEV_MODE(self) -> bool:
        return self.ENV.lower() in {"dev", "development", "test"}

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
