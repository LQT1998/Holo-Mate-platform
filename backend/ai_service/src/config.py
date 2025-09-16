from functools import lru_cache
from pydantic import AnyUrl, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"

    DATABASE_URL: AnyUrl | None = None
    REDIS_URL: AnyUrl | None = None

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
