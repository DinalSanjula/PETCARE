from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from Clinics.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicResponse
from Clinics.crud.clinic_crud import create_clinic, update_clinic, get_clinic_by_id, get_clinic_by_name, \
    get_clinic_by_owner, get_clinic_by_phone, delete_clinic, list_clinics
from db import get_db
from Clinics.utils.auth import get_current_user

router = APIRouter(prefix="/clinics", tags=["clinics"])

@router.post("/", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED)
async def create_new_clinic(clinic: ClinicCreate,
                            session : AsyncSession = Depends(get_db),
                            current_user = Depends(get_current_user)):

    if clinic.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access")
    created = await create_clinic(session=session, clinic_data=clinic)
    return created


@router.get("/{clinic_id}", response_model=ClinicResponse)
async def read_clinic_by_id(clinic_id: int, session : AsyncSession = Depends(get_db), with_related: bool = Query(True)):
    clinic = await get_clinic_by_id(session=session, clinic_id=clinic_id, with_related=with_related)
    return clinic

@router.get("/by-name/{name}", response_model=ClinicResponse)
async def read_clinic_by_name(name: str, session : AsyncSession = Depends(get_db), with_related: bool = Query(True)):
    clinic = await get_clinic_by_name(session=session, name=name, with_related=with_related)
    return clinic

@router.get("/by-phone/{phone}", response_model=ClinicResponse)
async def read_clinic_by_phone(phone: str, session : AsyncSession = Depends(get_db), with_related: bool = Query(True)):
    clinic = await get_clinic_by_phone(session=session, phone=phone, with_related=with_related)
    return clinic

@router.get("/owner/{owner_id}", response_model=List[ClinicResponse])
async def read_clinic_by_owner(owner_id: int, session : AsyncSession = Depends(get_db), with_related: bool = Query(True),
                               limit : int = Query(20, ge=1, le=100), offset : int = Query(0, ge=0)):
    clinics = await get_clinic_by_owner(session=session, owner_id=owner_id, limit=limit, offset=offset, with_related=with_related)
    return clinics

@router.get("/", response_model=List[ClinicResponse])
async def list_of_clinics(
        session : AsyncSession = Depends(get_db),
        limit : int = Query(20, ge=1, le=100),
        offset : int = Query(0, ge=0),
        owner_id : Optional[int] = Query(None),
        area_id : Optional[int] = Query(None),
        name : Optional[str] = Query(None),
        phone : Optional[str] = Query(None),
        is_active : Optional[bool] = Query(None),
        with_related : bool = Query(True)
):
    clinics = await list_clinics(
        session=session,
        limit=limit,
        offset=offset,
        owner_id=owner_id,
        area_id=area_id,
        name=name,
        phone=phone,
        is_active=is_active,
        with_related=with_related
    )
    return clinics

@router.patch("/{clinic_id}", response_model=ClinicResponse)
async def patch_clinics(clinic_id : int, clinic_data : ClinicUpdate, session:AsyncSession =  Depends(get_db),
                        current_user = Depends(get_current_user)):
    clinic_obj = await get_clinic_by_id(session, clinic_id, with_related=False)
    if clinic_obj.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    updated = await update_clinic(session=session, clinic_id=clinic_id, clinic_data=clinic_data)
    return updated

@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clinic(clinic_id:int, session:AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    clinic_obj = await get_clinic_by_id(session, clinic_id, with_related=False)
    if clinic_obj.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await delete_clinic(session=session, clinic_id=clinic_id)
    return None






