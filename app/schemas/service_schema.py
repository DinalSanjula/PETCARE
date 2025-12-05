from typing import Generic, TypeVar, List, Optional
from pydantic.generics import GenericModel
from pydantic import BaseModel

T = TypeVar("T")


class ServiceResponse(GenericModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None


class ServiceListResponse(GenericModel, Generic[T]):
    success: bool
    message: str
    data: List[T] = []   # allow empty list
    total: int
    limit: int
    offset: int


class ServiceDeleteResponse(BaseModel):
    success: bool
    message: str
