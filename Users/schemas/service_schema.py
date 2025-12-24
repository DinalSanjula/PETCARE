from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, ConfigDict


T = TypeVar("T")

class ServiceResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool
    message: str
    data: Optional[T] = None


class ServiceListResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool
    message: str
    data: List[T] = []
    total: int
    limit: int
    offset: int


class ServiceDeleteResponse(BaseModel):
    success: bool
    message: str


class BookingServiceResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool
    message: str
    data: Optional[T] = None