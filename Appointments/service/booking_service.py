from typing import Optional
from zoneinfo import ZoneInfo

from asyncpg import UniqueViolationError
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from Clinics.models.models import Clinic
from Users.schemas.service_schema import BookingServiceResponse
from Appointments.model.booking_models import BookingStatus, Booking, TimeSlot
from Appointments.schema.booking_schema import BookingCreate, TimeSlotCreate, AvailableSlot
from datetime import datetime, date, time, timedelta
from sqlalchemy import select, func
from fastapi import HTTPException, status
from Notification.service.notification_service import create_notification
from Users.models.user_model import User, UserRole


SL_TZ = ZoneInfo("Asia/Colombo")
now_sl = datetime.now(SL_TZ)

def assert_booking_access(booking: Booking, current_user: User):
    if current_user.role == UserRole.ADMIN:
        return

    if current_user.role in (UserRole.OWNER, UserRole.WELFARE):
        if booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your booking"
            )
        return

    if current_user.role == UserRole.CLINIC:
        if booking.clinic.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your clinic booking"
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )

async def generate_slot_index(
    db: AsyncSession,
    clinic_id: int,
    day_of_week
) -> int:
    result = await db.execute(
        select(func.max(TimeSlot.slot_index))
        .where(
            TimeSlot.clinic_id == clinic_id,
            TimeSlot.day_of_week == day_of_week
        )
    )
    max_index = result.scalar()
    return (max_index or 0) + 1


async def has_conflict(db: AsyncSession, clinic_id: int,
                       start_time : datetime, end_time: datetime,
                       exclude_booking_id : Optional[int]) -> bool:

    conditions = [
        Booking.clinic_id == clinic_id,
        Booking.status.in_([
            BookingStatus.CONFIRMED,
            BookingStatus.RESCHEDULED
        ]),
        Booking.start_time < end_time,
        Booking.end_time > start_time
    ]

    if exclude_booking_id is not None:
        conditions.append(Booking.id != exclude_booking_id)
    stmt = select(Booking).where(and_(*conditions))

    result = await db.execute(stmt)
    return result.scalars().first() is not None


async def create_time_slot(db: AsyncSession , slot_data: TimeSlotCreate, current_user : User) -> BookingServiceResponse[TimeSlot]:


    result = await db.execute(select(Clinic).where(
        Clinic.id == slot_data.clinic_id
    ))

    clinic = result.scalars().first()

    if not clinic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")

    if not clinic.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive clinics cannot create time slots")

    if current_user.role == UserRole.CLINIC:
        if clinic.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create slot for another clinic")


    MIN_SLOT_DURATION = timedelta(minutes=10)

    start_hour, start_minute = map(int, slot_data.start_time.split(":"))
    end_hour, end_minute = map(int, slot_data.end_time.split(":"))

    start_t = time(hour=start_hour, minute=start_minute)
    end_t = time(hour=end_hour, minute=end_minute)

    if start_t >= end_t:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be before end_time"
        )

    start_dt = datetime.combine(date.today(), start_t)
    end_dt = datetime.combine(date.today(), end_t)

    if end_dt - start_dt < MIN_SLOT_DURATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot duration must be at least 10 minutes"
        )

    slot_index = await generate_slot_index(db, slot_data.clinic_id, slot_data.day_of_week)
    slot = TimeSlot(
        clinic_id=clinic.id,
        day_of_week=slot_data.day_of_week,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time,
        slot_index=slot_index,
        is_active=True
    )

    try:
        db.add(slot)
        await db.commit()
        await db.refresh(slot)

    except IntegrityError as e:
        await db.rollback()

        if isinstance(e.orig, UniqueViolationError):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Time slot already exists for this clinic and day")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid timeslot data"
        )
    return BookingServiceResponse(
        success=True,
        message="Time slot created",
        data=slot
    )


async def get_available_time_slots(db: AsyncSession, clinic_id: int, target_date: date) -> BookingServiceResponse[list[dict]]:

    day_name = target_date.strftime("%A").upper()

    stmt = (select(TimeSlot).where(
        and_(
            TimeSlot.clinic_id == clinic_id,
            TimeSlot.day_of_week == day_name,
            TimeSlot.is_active == True
        )
    ).order_by(TimeSlot.start_time))

    result = await db.execute(stmt)
    slots = result.scalars().all()

    available_slots = []

    for slot in slots:
        start_hour, start_minute = map(int, slot.start_time.split(':'))
        end_hour, end_minute = map(int, slot.end_time.split(':'))

        slot_start_dt = datetime.combine(target_date, time(hour=start_hour, minute=start_minute), tzinfo=SL_TZ)
        slot_end_dt = datetime.combine(target_date, time(hour=end_hour, minute=end_minute), tzinfo=SL_TZ)

        is_booked = await has_conflict(db, clinic_id, slot_start_dt, slot_end_dt, exclude_booking_id=None)

        available_slots.append(AvailableSlot(
            start_time=slot_start_dt,
            end_time=slot_end_dt,
            is_booked=is_booked,
            slot_id=slot.id ))

    return BookingServiceResponse(
        success=True,
        message="Available slots retrieved",
        data=available_slots
    )


async def create_booking(db: AsyncSession, booking_data: BookingCreate, current_user: User) -> BookingServiceResponse[Booking]:

    if booking_data.start_time <= now_sl:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot book a past time slot")

    if booking_data.start_time.tzinfo is None or booking_data.end_time.tzinfo is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking times must include timezone")

    if booking_data.start_time <= now_sl + timedelta(minutes=10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bookings must be made at least 10 minutes in advance")

    user_id = current_user.id
    day_name = booking_data.start_time.strftime("%A").upper()
    start_time_str = booking_data.start_time.strftime("%H:%M")
    end_time_str = booking_data.end_time.strftime("%H:%M")

    slot_stmt = select(TimeSlot).where(
        and_(
            TimeSlot.clinic_id == booking_data.clinic_id,
            TimeSlot.day_of_week == day_name,
            TimeSlot.start_time == start_time_str,
            TimeSlot.end_time == end_time_str,
            TimeSlot.is_active == True
        )
    )
    slot_result = await db.execute(slot_stmt)
    slot = slot_result.scalars().first()

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time slot for the selected date"
        )

    conflict = await has_conflict(db , booking_data.clinic_id , booking_data.start_time , booking_data.end_time, exclude_booking_id=None)

    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot is already booked"
        )

    booking = Booking(
        clinic_id=booking_data.clinic_id,
        user_id=user_id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        status=BookingStatus.CONFIRMED
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    await create_notification(
        db,
        booking.user_id,
        "Booking Confirmed",
        "Your Appointments has been successfully booked."
    )

    return BookingServiceResponse(
        success=True,
        message="Booking create",
        data=booking
    )


async def cancel_booking(db: AsyncSession, booking_id: int, current_user: User) -> BookingServiceResponse[Booking]:


    stmt = select(Booking).options(selectinload(Booking.clinic)).where(Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        return BookingServiceResponse(success=False, message="Booking not found", data=None)

    assert_booking_access(booking=booking, current_user=current_user)

    if booking.status == BookingStatus.CANCELLED:
        return BookingServiceResponse(success=False, message="Booking already cancelled", data=None)

    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)

    await create_notification(
        db,
        booking.user_id,
        "Booking Cancelled",
        "Your Appointments has been cancelled."
    )

    return BookingServiceResponse(
        success=True,
        message="Booking cancelled",
        data=booking
    )


async def reschedule_booking(
    db: AsyncSession,
    booking_id: int,
    new_start_time: datetime,
    new_end_time: datetime,
    current_user: User
) -> BookingServiceResponse[Booking]:

    if new_start_time.tzinfo is None or new_end_time.tzinfo is None:
        raise HTTPException(
            status_code=400,
            detail="start_time and end_time must include timezone"
        )

    if new_start_time <= now_sl:
        raise HTTPException(
            status_code=400,
            detail="Cannot reschedule to a past time"
        )

    if new_start_time >= new_end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be before end_time"
        )

    stmt = select(Booking).options(selectinload(Booking.clinic)).where(Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        return BookingServiceResponse(
            success=False,
            message="Booking not found",
            data=None
        )

    assert_booking_access(booking=booking, current_user=current_user)

    if booking.status != BookingStatus.CONFIRMED:
        return BookingServiceResponse(
            success=False,
            message="Only confirmed bookings can be rescheduled",
            data=None
        )

    if booking.start_time <= now_sl + timedelta(minutes=30):
        raise HTTPException(
            status_code=400,
            detail="Cannot reschedule booking less than 30 mins before start time"
        )

    day_name = new_start_time.strftime("%A").upper()
    start_time_str = new_start_time.strftime("%H:%M")
    end_time_str = new_end_time.strftime("%H:%M")

    slot_stmt = select(TimeSlot).where(
        and_(
            TimeSlot.clinic_id == booking.clinic_id,
            TimeSlot.day_of_week == day_name,
            TimeSlot.start_time == start_time_str,
            TimeSlot.end_time == end_time_str,
            TimeSlot.is_active == True
        )
    )

    slot_result = await db.execute(slot_stmt)
    slot = slot_result.scalars().first()

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time slot for the selected date"
        )


    if await has_conflict(
        db,
        booking.clinic_id,
        new_start_time,
        new_end_time,
        exclude_booking_id=booking.id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="New slot already booked"
        )

    booking.start_time = new_start_time
    booking.end_time = new_end_time
    booking.status = BookingStatus.RESCHEDULED

    await db.commit()
    await db.refresh(booking)

    await create_notification(
        db,
        booking.user_id,
        "Booking Rescheduled",
        "Your appointment time has been changed."
    )

    return BookingServiceResponse(
        success=True,
        message="Booking rescheduled",
        data=booking
    )