from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from Reports.models.models import Report
from Appointments.model.booking_models import Booking
from Users.models.user_model import User
from Clinics.models.models import Clinic


today = date.today()
start_of_today = datetime.combine(today, datetime.min.time())

async def get_admin_stats(db : AsyncSession) -> dict:
    active_users = (await db.execute(select(func.count(User.id)).where(User.is_active.is_(True)))).scalar() or 0
    inactive_users = (await db.execute(select(func.count(User.id)).where(User.is_active.is_(False)))).scalar() or 0
    active_clinics = (await db.execute(select(func.count(Clinic.id)).where(Clinic.is_active.is_(True)))).scalar() or 0
    pending_clinics = (await db.execute(select(func.count(Clinic.id)).where(Clinic.is_active.is_(False)))).scalar() or 0
    reports_today =  (await db.execute(select(func.count(Report.id)).where(Report.created_at >= start_of_today))).scalar() or 0
    appointments = (await db.execute(select(func.count(Booking.id)))).scalar() or 0

    return {
        "active_users": active_users,
        "inactive_users": inactive_users,
        "active_clinics": active_clinics,
        "pending_clinics": pending_clinics,
        "reports_today": reports_today,
        "appointments": appointments
    }

