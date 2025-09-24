"""Shared settings for backend services."""

from functools import lru_cache
from typing import Annotated
from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic_settings import BaseSettings


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


class SharedSettings(BaseSettings):
    ENV: str = "dev"
    DATABASE_URL: Annotated[DatabaseUrl, Field(..., env="DATABASE_URL")]
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_shared_settings() -> SharedSettings:
    return SharedSettings()


settings = get_shared_settings()
