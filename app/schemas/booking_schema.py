from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BookingBase(BaseModel):
    clinic_id: int
    user_id: int
    start_time: datetime
    end_time: datetime

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)