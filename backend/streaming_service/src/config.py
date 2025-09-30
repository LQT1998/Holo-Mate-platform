from functools import lru_cache
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings
from shared.src.config import DatabaseUrl, RedisUrl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    ENV: str = "dev"
    DEV_MODE: bool = True
    AUTH_ENABLED: bool = False

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

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
