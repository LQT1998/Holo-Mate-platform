from functools import lru_cache
from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"

    DATABASE_URL: AnyUrl | None = None
    REDIS_URL: AnyUrl | None = None

    JWT_SECRET: str | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    OPENAI_API_KEY: str | None = None
    ELEVENLABS_API_KEY: str | None = None
    STRIPE_SECRET_KEY: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Convenience singleton for modules expecting a `settings` object
settings = get_settings()
