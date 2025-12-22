from pydantic import BaseModel

class AdminStatsResponse(BaseModel):
    active_users : int
    inactive_users : int
    pending_clinics : int
    active_clinics : int
    reports_today : int
    appointments : int
