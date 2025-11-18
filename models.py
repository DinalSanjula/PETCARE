from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    CLINIC = "clinic"

class UserBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    role: UserRole
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime

class UserReplace(UserBase):
    pass

class UserPatch(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None