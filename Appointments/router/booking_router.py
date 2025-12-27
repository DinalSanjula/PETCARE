from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from datetime import date
from typing import List
from Users.auth.security import get_current_active_user
from Clinics.utils.helpers import require_roles
from Users.models.user_model import User, UserRole

from Appointments.schema.booking_schema import (
    BookingCreate,
    BookingResponse,
    TimeSlotCreate,
    TimeSlotOut,
    AvailableSlot,
    RescheduleRequest
)
from Appointments.service import booking_service


router = APIRouter( tags=["Appointments"])


@router.post("/slots", response_model=TimeSlotOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))])

async def create_slot(slot_data: TimeSlotCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    result = await booking_service.create_time_slot(db, slot_data, current_user=current_user)

    if not result.success:
        raise HTTPException(400 , result.message)

@router.get("/slots/{clinic_id}/available", response_model=List[AvailableSlot])
async def get_available_slots(clinic_id: int, date: date, db: AsyncSession = Depends(get_db), current_user : User = Depends(get_current_active_user)):
    result = await booking_service.get_available_time_slots(db, clinic_id, date)

    if not result.success:
        raise HTTPException(400, result.message)

    return result.data

@router.post("/bookings", response_model=BookingResponse, status_code=201, dependencies=[Depends(require_roles(UserRole.OWNER, UserRole.WELFARE))])
async def create_booking(booking_data: BookingCreate, db: AsyncSession = Depends(get_db), current_user : User = Depends(get_current_active_user)):
    result = await booking_service.create_booking(db, booking_data, current_user=current_user)

    if not result.success:
        raise HTTPException(status.HTTP_409_CONFLICT, result.message)

    return result.data

@router.post("/bookings/{booking_id}/cancel", response_model=BookingResponse,
             dependencies=[Depends(require_roles(UserRole.OWNER, UserRole.CLINIC, UserRole.ADMIN, UserRole.WELFARE))])
async def cancel_booking(booking_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    result = await booking_service.cancel_booking(db, booking_id, current_user=current_user)

    if not result.success:
        raise HTTPException(400, result.message)

    return result.data

@router.post("/bookings/{booking_id}/reschedule", response_model=BookingResponse,
             dependencies=[Depends(require_roles(UserRole.OWNER, UserRole.CLINIC, UserRole.ADMIN, UserRole.WELFARE))])
async def reschedule_booking(
    booking_id: int,
    data: RescheduleRequest,
    db: AsyncSession = Depends(get_db), current_user : User = Depends(get_current_active_user)
):
    result = await booking_service.reschedule_booking(
        db, booking_id, data.start_time, data.end_time, current_user=current_user
    )

    if not result.success:
        raise HTTPException(400, result.message)

    return result.data