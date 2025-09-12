from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Default values for testing
    access_token_expires_minutes: int = 15
    refresh_token_expires_days: int = 7
    SECRET_KEY: str = "a_very_secret_key_for_testing"
    ALGORITHM: str = "HS256"
    
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
