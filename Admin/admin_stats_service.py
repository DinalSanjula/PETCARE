from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from Users.models.user_model import User
from Clinics.models.models import Clinic

async def get_admin_stats(db : AsyncSession) -> dict:
    active_users = (await db.execute(select(func.count(User.id)).where(User.is_active.is_(True)))).scalar() or 0
    inactive_users = (await db.execute(select(func.count(User.id)).where(User.is_active.is_(False)))).scalar() or 0
    active_clinics = (await db.execute(select(func.count(Clinic.id)).where(Clinic.is_active.is_(True)))).scalar() or 0
    pending_clinics = (await db.execute(select(func.count(Clinic.id)).where(Clinic.is_active.is_(False)))).scalar() or 0
    # reports_today = (await db.execute(select(func.count(User.id)).where(User.is_active.is_(True)))).scalar() or 0
    # appointments = (await db.execute(select(func.count(User.id)).where(User.is_active.is_(True)))).scalar() or 0

    return {
        "active_users": active_users,
        "inactive_users": inactive_users,
        "active_clinics": active_clinics,
        "pending_clinics": pending_clinics,
        "reports_today": 0,
        "appointments": 0
    }

