from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db

from Users.auth.security import get_current_active_user
from Clinics.utils.helpers import require_roles
from Users.models.user_model import User, UserRole
from Appointments.schema.stats_schema import AppointmentStatsOut
from Appointments.service.stats_service import (
    get_clinic_appointment_stats,
    get_admin_appointment_stats
)

router = APIRouter(tags=["Appointment Stats"])

@router.get(
    "/appointments/stats/clinic",
    response_model=AppointmentStatsOut,
    dependencies=[Depends(require_roles(UserRole.CLINIC))]
)
async def clinic_appointment_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await get_clinic_appointment_stats(db, current_user)


@router.get(
    "/appointments/stats/admin",
    response_model=AppointmentStatsOut,
    dependencies=[Depends(require_roles(UserRole.ADMIN))]
)
async def admin_appointment_stats(
    clinic_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await get_admin_appointment_stats(
        db, current_user, clinic_id
    )