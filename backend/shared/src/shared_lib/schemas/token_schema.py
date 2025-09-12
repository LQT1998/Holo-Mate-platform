from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Lifetime of the access token in seconds
    refresh_token_expires_in: int # Lifetime of the refresh token in seconds
