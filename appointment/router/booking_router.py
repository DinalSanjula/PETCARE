from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from datetime import date
from typing import List

from appointment.schema.booking_schema import (
    BookingCreate,
    BookingResponse,
    TimeSlotCreate,
    TimeSlotOut,
    AvailableSlot,
    RescheduleRequest
)
from appointment.service import booking_service


router = APIRouter(prefix="/appointment", tags=["appointment"])


@router.post("/slots", response_model=TimeSlotOut, status_code=status.HTTP_201_CREATED)
async def create_slot(slot_data: TimeSlotCreate, db: AsyncSession = Depends(get_db)):
    return await booking_service.create_time_slot(db, slot_data)

@router.get("/slots/{clinic_id}/available", response_model=List[AvailableSlot])
async def get_available_slots(clinic_id: int, date: date, db: AsyncSession = Depends(get_db)):
    return await booking_service.get_available_time_slots(db, clinic_id, date)

@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(booking_data: BookingCreate, db: AsyncSession = Depends(get_db)):
    return await booking_service.create_booking(db, booking_data)

@router.post("/bookings/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    return await booking_service.cancel_booking(db, booking_id)

@router.post("/bookings/{booking_id}/reschedule", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: int,
    reschedule_data: RescheduleRequest,
    db: AsyncSession = Depends(get_db)
):
    return await booking_service.reschedule_booking(
        db,
        booking_id,
        reschedule_data.start_time,
        reschedule_data.end_time
    )
