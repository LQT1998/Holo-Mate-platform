# backend/shared/src/schemas/user.py

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True  # để Pydantic đọc trực tiếp từ SQLAlchemy model


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
