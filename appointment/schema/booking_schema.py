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


class TimeSlotBase(BaseModel):
    clinic_id: int
    day_of_week: str
    start_time: str
    end_time: str
    slot_index: int | None = None
    is_active: bool = True

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotOut(TimeSlotBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class AvailableSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    is_booked: bool = False
    slot_id: int | None = None

class RescheduleRequest(BaseModel):
    start_time: datetime
    end_time: datetime