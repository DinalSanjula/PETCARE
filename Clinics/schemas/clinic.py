from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict

from Clinics.schemas.area import AreaResponse
from Clinics.schemas.clinic_image import ClinicImageResponse
from Clinics.schemas.coordinates import Coordinates


class ClinicBase(Coordinates, BaseModel):

    name : str = Field(..., min_length=1, max_length=100, description="Name of the Clinic")
    description : Optional[str] = Field(None, min_length=1, max_length=500, description="A description about the clinic")
    phone : Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    address: Optional[str] = Field(None, min_length=1, max_length=120, description="Address of the clinic")
    profile_pic_url : Optional[HttpUrl] = Field(None, min_length=1, max_length=255, description="Profile photo")
    area_id : Optional[int] = Field(None)



class ClinicCreate(ClinicBase):
    owner_id: int = Field(...,description="owner id that came from owner/user table")

class ClinicUpdate(Coordinates, BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the Clinic")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="A description about the clinic")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    address: Optional[str] = Field(None, min_length=1, max_length=120, description="Address of the clinic")
    profile_pic_url: Optional[HttpUrl] = Field(None, min_length=1, max_length=255, description="Profile photo")
    area_id: Optional[int] = Field(None)

class ClinicResponse(ClinicBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    formatted_address : Optional[str] = None
    created_at : datetime
    updated_at : datetime
    is_active : bool
    area : Optional[AreaResponse] = None
    images : Optional[List[ClinicImageResponse]] = None



