from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from db import Base


class BookingStatus(enum.Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"

class Booking(Base):
    __tablename__ = "booking"

    id = Column(Integer , primary_key=True , index=True)
    clinic_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id = Column()
    pet_id = Column()
    start_time = Column()
    end_time = Column()
    status = Column()
    created_at = Column()
    updated_at = Column()