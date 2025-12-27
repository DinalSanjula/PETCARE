from zoneinfo import ZoneInfo
from pydantic import BaseModel, field_validator
from datetime import datetime


SL_TZ = ZoneInfo("Asia/Colombo")


class TimezoneAwareResponse(BaseModel):

    @field_validator("*", mode="before")
    def convert_datetime_to_sl(cls, v):
        if isinstance(v, datetime):
            if v.tzinfo is None:
                v = v.replace(tzinfo=ZoneInfo("UTC"))
            return v.astimezone(SL_TZ)
        return v
