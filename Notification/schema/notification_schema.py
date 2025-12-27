from pydantic import BaseModel, ConfigDict
from datetime import datetime

from Clinics.schemas.timezone import TimezoneAwareResponse


class NotificationResponse(TimezoneAwareResponse, BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)