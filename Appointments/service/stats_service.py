from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from Appointments.model.booking_models import Booking, BookingStatus
from Appointments.schema.stats_schema import AppointmentStatsOut
from Clinics.models.models import Clinic
from Users.models.user_model import User, UserRole
from fastapi import HTTPException, status

from sqlalchemy import select, func
from datetime import datetime

async def get_clinic_appointment_stats(
    db: AsyncSession,
    current_user: User
) -> AppointmentStatsOut:

    result = await db.execute(
        select(Clinic).where(Clinic.owner_id == current_user.id)
    )
    clinic = result.scalars().first()

    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinic not found for current user"
        )

    clinic_id = clinic.id

    now = datetime.now(timezone.utc)

    total = await db.scalar(
        select(func.count()).where(Booking.clinic_id == clinic_id)
    )

    confirmed = await db.scalar(
        select(func.count()).where(
            Booking.clinic_id == clinic_id,
            Booking.status == BookingStatus.CONFIRMED
        )
    )

    cancelled = await db.scalar(
        select(func.count()).where(
            Booking.clinic_id == clinic_id,
            Booking.status == BookingStatus.CANCELLED
        )
    )

    rescheduled = await db.scalar(
        select(func.count()).where(
            Booking.clinic_id == clinic_id,
            Booking.status == BookingStatus.RESCHEDULED
        )
    )

    upcoming = await db.scalar(
        select(func.count()).where(
            Booking.clinic_id == clinic_id,
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.RESCHEDULED
            ]),
            Booking.start_time > now
        )
    )

    return AppointmentStatsOut(
        total_bookings=total or 0,
        confirmed=confirmed or 0,
        cancelled=cancelled or 0,
        rescheduled=rescheduled or 0,
        upcoming=upcoming or 0
    )
async def get_admin_appointment_stats(
    db: AsyncSession,
    current_user: User,
    clinic_id: int | None = None
) -> AppointmentStatsOut:

    now  = datetime.now(timezone.utc)

    filters = []
    if clinic_id:
        filters.append(Booking.clinic_id == clinic_id)

    def count(extra=None):
        stmt = select(func.count()).select_from(Booking)
        for f in filters + (extra or []):
            stmt = stmt.where(f)
        return stmt

    total = await db.scalar(count())
    confirmed = await db.scalar(count([Booking.status == BookingStatus.CONFIRMED]))
    cancelled = await db.scalar(count([Booking.status == BookingStatus.CANCELLED]))
    rescheduled = await db.scalar(count([Booking.status == BookingStatus.RESCHEDULED]))

    upcoming = await db.scalar(count([
        Booking.status == BookingStatus.CONFIRMED,
        Booking.start_time > now
    ]))

    return AppointmentStatsOut(
        total_bookings=total or 0,
        confirmed=confirmed or 0,
        cancelled=cancelled or 0,
        rescheduled=rescheduled or 0,
        upcoming=upcoming or 0
    )