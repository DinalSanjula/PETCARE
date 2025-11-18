from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    CLINIC = "clinic"

class UserBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    role: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

class UserReplace(UserBase):
    pass

class UserPatch(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None