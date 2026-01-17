from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Appointments.model.booking_models import BookingStatus
from Appointments.service.booking_service import list_bookings_for_clinic, list_my_bookings, update_time_slot_status
from Clinics.crud.clinic_crud import get_clinic_by_id
from db import get_db
from datetime import date
from typing import List, Optional
from Users.auth.security import get_current_active_user
from Clinics.utils.helpers import require_roles
from Users.models.user_model import User, UserRole

from Appointments.schema.booking_schema import (
    BookingCreate,
    BookingResponse,
    TimeSlotCreate,
    TimeSlotOut,
    AvailableSlot,
    RescheduleRequest, ClinicBookingResponse, BookingListResponse, TimeSlotUpdate, TimeSlotClinicOut
)
from Appointments.service import booking_service


router = APIRouter( tags=["Appointments"])


@router.post("/slots", response_model=TimeSlotOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))])

async def create_slot(slot_data: TimeSlotCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    result = await booking_service.create_time_slot(db, slot_data, current_user=current_user)

    if not result.success:
        raise HTTPException(400 , result.message)
    return result.data

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

@router.get(
    "/clinic/{clinic_id}",
    response_model=List[ClinicBookingResponse],
    dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))],
)
async def view_clinic_bookings(
    clinic_id: int,
    booking_date: Optional[date] = Query(None),
    status: Optional[BookingStatus] = Query(None),
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    clinic = await get_clinic_by_id(db, clinic_id)

    if current_user.role == UserRole.CLINIC and clinic.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    bookings = await list_bookings_for_clinic(
        db=db,
        clinic_id=clinic_id,
        booking_date=booking_date,
        status=status,
        limit=limit,
        offset=offset,
    )

    return [
        ClinicBookingResponse(
            booking_id=b.id,
            owner_id=b.user.id,
            owner_name=b.user.name,
            owner_email=b.user.email,
            start_time=b.start_time,
            end_time=b.end_time,
            status=b.status,
        )
        for b in bookings
    ]

@router.get(
    "/my",
    response_model=List[BookingListResponse],
    dependencies=[Depends(require_roles(UserRole.OWNER, UserRole.ADMIN))],
)
async def my_appointments(
    status: Optional[BookingStatus] = Query(None),
    upcoming_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    bookings = await list_my_bookings(
        db=db,
        user_id=current_user.id,
        status=status,
        upcoming_only=upcoming_only,
    )

    return [
        BookingListResponse(
            booking_id=b.id,
            clinic_id=b.clinic.id,
            clinic_name=b.clinic.name,
            start_time=b.start_time,
            end_time=b.end_time,
            status=b.status,
        )
        for b in bookings
    ]


@router.patch(
    "/slots/{slot_id}",
    response_model=TimeSlotClinicOut,
    dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))]
)
async def update_slot(
    slot_id: int,
    update_data: TimeSlotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await booking_service.update_time_slot_status(
        db=db,
        slot_id=slot_id,
        update_data=update_data,
        current_user=current_user
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return result.data


@router.get(
    "/slots/clinic/{clinic_id}",
    response_model=List[TimeSlotClinicOut],
    dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))]
)
async def get_clinic_slots(
    clinic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await booking_service.get_clinic_time_slots(
        db=db,
        clinic_id=clinic_id,
        current_user=current_user
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return result.data