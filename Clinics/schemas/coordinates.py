from pydantic import field_validator, Field
from typing import Optional

class Coordinates:
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)

    @field_validator("latitude")
    def latitude_range(cls, v):
        if v is None:
            return v
        if not -90 <= v <= 90:
            raise ValueError("latitude range must be between -90 and 90")
        return v

    @field_validator("longitude")
    def longitude_range(cls, v):
        if v is None:
            return v
        if not -180 <= v <= 180:
            raise ValueError("longitude range must be between -180 and 180")
        return v