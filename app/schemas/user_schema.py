from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user_model import UserRole


class UserBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=200)
    role: UserRole = UserRole.OWNER  # keep default if required


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ORM mode


class UserReplace(UserBase):
    password: str = Field(..., min_length=8)


class UserPatch(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=200)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None  # remove if not used