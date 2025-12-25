from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from Users.schemas.service_schema import BookingServiceResponse
from appointment.model.booking_models import BookingStatus, Booking, TimeSlot
from appointment.schema.booking_schema import BookingCreate, TimeSlotCreate, AvailableSlot
from datetime import datetime, date, time

from fastapi import HTTPException, status

from appointment.service.notification_service import create_notification


async def has_conflict(db: AsyncSession, clinic_id: int, start_time, end_time) -> bool:
    stmt = select(Booking).where(
        and_(
            Booking.clinic_id == clinic_id,
            Booking.status == BookingStatus.CONFIRMED,
            Booking.start_time < end_time,
            Booking.end_time > start_time
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first() is not None


async def create_time_slot(db: AsyncSession , slot_data: TimeSlotCreate) -> BookingServiceResponse[TimeSlot]:

    slot = TimeSlot(
        clinic_id=slot_data.clinic_id,
        day_of_week=slot_data.day_of_week,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time,
        slot_index=slot_data.slot_index,
        is_active=slot_data.is_active
    )

    db.add(slot)
    await db.commit()
    await db.refresh(slot)

    return BookingServiceResponse(
        success=True,
        message="Time slot created",
        data=slot
    )


async def get_available_time_slots(db: AsyncSession, clinic_id: int, target_date: date) -> BookingServiceResponse[list[dict]]:

    day_name = target_date.strftime("%A")  # e.g. "Sunday"

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

        slot_start_dt = datetime.combine(target_date, time(hour=start_hour, minute=start_minute))
        slot_end_dt = datetime.combine(target_date, time(hour=end_hour, minute=end_minute))

        is_booked = await has_conflict(db, clinic_id, slot_start_dt, slot_end_dt)

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


async def create_booking(db: AsyncSession, booking_data: BookingCreate) -> BookingServiceResponse[Booking]:

    day_name = booking_data.start_time.strftime("%A")
    start_time_str = booking_data.start_time.strftime("%H:%M")
    end_time_str = booking_data.end_time.strftime("%H:%M")

    # Check if a matching slot exists
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

    conflict = await has_conflict(db , booking_data.clinic_id , booking_data.start_time , booking_data.end_time)

    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot is already booked"
        )

    booking = Booking(
        clinic_id=booking_data.clinic_id,
        user_id=booking_data.user_id,
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
        "Your appointment has been successfully booked."
    )

    return BookingServiceResponse(
        success=True,
        message="Booking create",
        data=booking
    )


async def cancel_booking(db: AsyncSession, booking_id: int) -> BookingServiceResponse[Booking]:

    stmt = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        return BookingServiceResponse(success=False, message="Booking not found", data=None)

    if booking.status == BookingStatus.CANCELLED:
        return BookingServiceResponse(success=False, message="Booking already cancelled", data=None)

    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)

    await create_notification(
        db,
        booking.user_id,
        "Booking Cancelled",
        "Your appointment has been cancelled."
    )

    return BookingServiceResponse(
        success=True,
        message="Booking cancelled",
        data=booking
    )


async def reschedule_booking(db: AsyncSession , booking_id: int , new_start_time , new_end_time
                             )-> BookingServiceResponse[Booking]:

    stmt = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        return BookingServiceResponse(success=False, message="Booking not found", data=None)

    if booking.status != BookingStatus.CONFIRMED:
        return BookingServiceResponse(success=False, message="Only confirmed bookings can be rescheduled", data=None)

    if await has_conflict(db, booking.clinic_id, new_start_time, new_end_time):
        return BookingServiceResponse(success=False, message="New slot already booked", data=None)

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