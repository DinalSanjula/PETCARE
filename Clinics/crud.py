from typing import Optional, List, Dict, Type
from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeMeta

from Clinics.models import Clinic
from Clinics.schemas.clinic import ClinicCreate


async def get_or_404(session : AsyncSession, model:Type[DeclarativeMeta], pk:int, name:str = "item"):
    q = select(model).where(model.id == pk)
    result = await session.execute(q)
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return obj

async def create_clinic(session : AsyncSession, clinic_data : ClinicCreate) -> Clinic:

    def remove_whitespaces(s : str) -> str:
        return " ".join(s.strip().split())


    data = Clinic(
        owner_id = clinic_data.owner_id, #maybe current user from users
        name = clinic_data.name,
        description = clinic_data.description,
        phone = clinic_data.phone,
        address = clinic_data.address and remove_whitespaces(clinic_data.address),
        profile_pic_url = clinic_data.profile_pic_url,
        area_id = clinic_data.area_id,
        latitude = clinic_data.latitude,
        longitude = clinic_data.longitude
    )
    session.add(data)
    try:
        await session.commit()
        await session.refresh(data)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    return data




