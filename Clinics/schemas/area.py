from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from Clinics.schemas.coordinates import Coordinates
from Clinics.schemas.timezone import TimezoneAwareResponse


class AreaBase(Coordinates,BaseModel):
    name : str = Field(..., max_length=100)
    normalized_name: Optional[str] = Field(None, max_length=100, description="store if provided, unless generate")
    main_region : str = Field(..., max_length=100)
    formatted_address : Optional[str] = Field(None, max_length=255)



class AreaCreate(AreaBase):
    pass

class AreaUpdate(Coordinates, BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    normalized_name: Optional[str] = Field(None, max_length=100)
    main_region: Optional[str] = Field(None, max_length=100)
    formatted_address : Optional[str] = Field(None, max_length=255)


class AreaResponse(TimezoneAwareResponse, AreaBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    created_at : datetime
