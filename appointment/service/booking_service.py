from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from appointment.model.booking_models import BookingStatus , Booking
from appointment.schema.booking_schema import BookingCreate

from fastapi import HTTPException, status


async def has_conflict(db: AsyncSession , clinic_id: int , start_time , end_time ) -> bool:

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

async def create_booking(db: AsyncSession , booking_data : BookingCreate):
    conflict = await has_conflict(db,
        booking_data.clinic_id,
        booking_data.start_time,
        booking_data.end_time
    )

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

    return booking