# backend/shared/src/schemas/auth.py
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email_or_username: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_token_expires_in: int
