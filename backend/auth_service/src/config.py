from functools import lru_cache
from typing import Annotated, Optional
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from shared.src.config import DatabaseUrl, RedisUrl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    ENV: str = "dev"

    DATABASE_URL: Annotated[DatabaseUrl, Field(..., env="DATABASE_URL")]
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    REDIS_URL: Annotated[RedisUrl, Field(..., env="REDIS_URL")]

    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRES_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRES_MINUTES")
    
    # Alias for backward compatibility
    def __getattr__(self, name: str):
        if name == "JWT_SECRET":
            return self.JWT_SECRET_KEY
        elif name == "ACCESS_TOKEN_EXPIRE_MINUTES":
            return self.ACCESS_TOKEN_EXPIRES_MINUTES
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    OPENAI_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None

    # New: flag to check if running in dev mode
    @computed_field
    @property
    def DEV_MODE(self) -> bool:
        return self.ENV.lower() in {"dev", "development", "test"}

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Convenience singleton for modules expecting a `settings` object
settings = get_settings()
