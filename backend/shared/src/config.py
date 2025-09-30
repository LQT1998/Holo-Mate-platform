"""Shared settings for backend services."""

from functools import lru_cache
from typing import Annotated

from pydantic import Field, GetCoreSchemaHandler, ConfigDict
from pydantic_core import CoreSchema, core_schema
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseUrl(str):
    """Custom database URL type that accepts SQLAlchemy schemes."""
    
    ALLOWED_SCHEMES = {
        "postgresql",
        "postgresql+asyncpg", 
        "postgresql+psycopg2",
        "sqlite",
        "sqlite+aiosqlite",
        "mysql",
        "mysql+aiomysql",
        "mysql+pymysql",
    }
    
    def __new__(cls, value: str) -> "DatabaseUrl":
        if not isinstance(value, str):
            raise ValueError("Database URL must be a string")
        
        # Extract scheme
        if "://" not in value:
            raise ValueError("Database URL must contain '://'")
        
        scheme = value.split("://")[0]
        if scheme not in cls.ALLOWED_SCHEMES:
            raise ValueError(
                f"Unsupported database scheme: {scheme}. "
                f"Allowed schemes: {', '.join(cls.ALLOWED_SCHEMES)}"
            )
        
        return super().__new__(cls, value)
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )
    
    @classmethod
    def _validate(cls, value: str) -> "DatabaseUrl":
        return cls(value)


class RedisUrl(str):
    """Custom Redis URL type supporting common schemes."""

    ALLOWED_SCHEMES = {"redis", "rediss"}

    def __new__(cls, value: str) -> "RedisUrl":
        if not isinstance(value, str):
            raise ValueError("Redis URL must be a string")

        if "://" not in value:
            raise ValueError("Redis URL must contain '://'")

        scheme = value.split("://")[0]
        if scheme not in cls.ALLOWED_SCHEMES:
            raise ValueError(
                f"Unsupported Redis scheme: {scheme}. "
                f"Allowed schemes: {', '.join(sorted(cls.ALLOWED_SCHEMES))}"
            )

        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def _validate(cls, value: str) -> "RedisUrl":
        return cls(value)


class SharedSettings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    ENV: str = "dev"
    DATABASE_URL: Annotated[DatabaseUrl, Field(...)]
    DB_ECHO: bool = Field(default=False)
    REDIS_URL: Annotated[RedisUrl, Field(...)]
    JWT_SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRES_MINUTES: int = Field(default=30)
    
    # Alias for backward compatibility
    @property
    def JWT_SECRET(self) -> str:
        return self.JWT_SECRET_KEY
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.ACCESS_TOKEN_EXPIRES_MINUTES


@lru_cache
def get_shared_settings() -> SharedSettings:
    return SharedSettings()


settings = get_shared_settings()
