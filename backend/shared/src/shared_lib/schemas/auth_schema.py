from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email_or_username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class GoogleLoginRequest(BaseModel):
    id_token: str
