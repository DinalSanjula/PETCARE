from pydantic import BaseModel, Field
class AreaCreate(BaseModel):
    pass
class AreaResponse(AreaCreate):
    pass
class AreaCreate(AreaBase):
    pass