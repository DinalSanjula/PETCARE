from typing import Generic, TypeVar, List, Optional
from pydantic.generics import GenericModel
from pydantic import BaseModel

T = TypeVar("T")


class ServiceResponse(GenericModel, Generic[T]):
    """Generic service response"""
    success: bool
    message: str
    data: Optional[T] = None


class ServiceListResponse(GenericModel, Generic[T]):
    """Generic list response"""
    success: bool
    message: str
    data: List[T] = []   # allow empty list
    total: int
    limit: int
    offset: int


class ServiceDeleteResponse(BaseModel):
    """Delete response"""
    success: bool
    message: str
