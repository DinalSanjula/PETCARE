from pydantic import BaseModel

class AppointmentStatsOut(BaseModel):
    total_bookings: int
    confirmed: int
    cancelled: int
    rescheduled: int
    upcoming: int