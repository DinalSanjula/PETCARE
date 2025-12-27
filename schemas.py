from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    
    class Config:
        from_attributes = True


# Organization schemas
class OrganizationCreate(BaseModel):
    name: str
    description: str


class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: str
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Animal Report schemas
class AnimalReportCreate(BaseModel):
    title: str
    description: str
    location: str


class AnimalReportResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    status: str
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Login schema
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Status update schema
class StatusUpdate(BaseModel):
    status: str


# Dashboard response
class DashboardResponse(BaseModel):
    new_reports: list[AnimalReportResponse]
    in_progress_reports: list[AnimalReportResponse]
    resolved_reports: list[AnimalReportResponse]

