from functools import lru_cache
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings
from shared.src.config import DatabaseUrl, RedisUrl


class Settings(BaseSettings):
    ENV: str = "dev"
    DEV_MODE: bool = True
    AUTH_ENABLED: bool = False

    DATABASE_URL: Annotated[DatabaseUrl, Field(..., env="DATABASE_URL")]
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    REDIS_URL: Annotated[RedisUrl, Field(..., env="REDIS_URL")]

    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
