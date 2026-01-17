from typing import Optional

from pydantic import BaseModel, ConfigDict
from datetime import datetime

from Appointments.model.booking_models import BookingStatus
from Clinics.schemas.timezone import TimezoneAwareResponse


class BookingBase(BaseModel):
    clinic_id: int
    start_time: datetime
    end_time: datetime

class BookingCreate(BookingBase):
    pass

class BookingResponse(TimezoneAwareResponse, BookingBase):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class TimeSlotBase(BaseModel):
    clinic_id: int
    day_of_week: str
    start_time: str
    end_time: str

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotOut(TimeSlotBase):
    id: int
    slot_index : int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class AvailableSlot(TimezoneAwareResponse, BaseModel):
    start_time: datetime
    end_time: datetime
    is_booked: bool = False
    slot_id: int | None = None

class RescheduleRequest(BaseModel):
    start_time: datetime
    end_time: datetime

class ClinicBookingResponse(TimezoneAwareResponse, BaseModel):
    booking_id: int

    owner_id: int
    owner_name: str
    owner_email: Optional[str]

    start_time: datetime
    end_time: datetime
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)

class BookingListResponse(TimezoneAwareResponse, BaseModel):
    booking_id: int
    clinic_id: int
    clinic_name: str

    start_time: datetime
    end_time: datetime
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)

class TimeSlotUpdate(BaseModel):
    is_active: bool


class TimeSlotClinicOut(TimezoneAwareResponse, BaseModel):
    id: int
    clinic_id: int
    start_time: datetime
    end_time: datetime
    slot_index: Optional[int]
    is_active: bool
    has_bookings: bool

    model_config = ConfigDict(from_attributes=True)

