from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from Clinics.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicResponse, ClinicBase
from Clinics.crud.clinic_crud import (create_clinic as create_clinic_crud,
                                      update_clinic as update_clinic_crud,
                                      get_clinic_by_id as get_clinic_by_id_crud,
                                      get_clinic_by_name,
                                      get_clinic_by_owner,
                                      get_clinic_by_phone,
                                      delete_clinic as delete_clinic_crud,
                                      list_clinics)
from Clinics.utils.helpers import require_roles
from Users.models import UserRole

from db import get_db
from Users.auth.security import get_current_active_user
from Users.models.user_model import User

router = APIRouter(tags=["Clinics"])

@router.post("/", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))])
async def create_new_clinic(clinic: ClinicCreate,
                            session : AsyncSession = Depends(get_db),
                            current_user :User = Depends(get_current_active_user)):

    clinic_data = clinic.model_copy(update={"owner_id":current_user.id})
    created = await create_clinic_crud(session=session, clinic_data=clinic_data)
    return created


@router.get("/{clinic_id}", response_model=ClinicResponse)
async def read_clinic_by_id(clinic_id: int, session : AsyncSession = Depends(get_db), with_related: bool = Query(True)):
    clinic = await get_clinic_by_id_crud(session=session, clinic_id=clinic_id, with_related=with_related)
    return clinic

@router.get("/by-name/{name}", response_model=ClinicResponse)
async def read_clinic_by_name(name: str, session : AsyncSession = Depends(get_db), with_related: bool = Query(True)):
    clinic = await get_clinic_by_name(session=session, name=name, with_related=with_related)
    return clinic

@router.get("/by-phone/{phone}", response_model=ClinicResponse)
async def read_clinic_by_phone(phone: str, session : AsyncSession = Depends(get_db), with_related: bool = Query(True)):
    try:
        phone = ClinicBase.validate_phone(phone)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone")

    clinic = await get_clinic_by_phone(session=session, phone=phone, with_related=with_related)
    return clinic

@router.get("/owner/{owner_id}", response_model=List[ClinicResponse], dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))])
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
        is_active=True,
        with_related=with_related
    )
    return clinics

@router.patch("/{clinic_id}", response_model=ClinicResponse, dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))])
async def patch_clinics(clinic_id : int, clinic_data : ClinicUpdate, session:AsyncSession =  Depends(get_db),
                        current_user : User = Depends(get_current_active_user)):

    clinic_obj = await get_clinic_by_id_crud(session, clinic_id, with_related=False)
    if clinic_obj.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    updated = await update_clinic_crud(session=session, clinic_id=clinic_id, clinic_data=clinic_data)
    return updated


@router.delete("/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))])
async def delete_clinic(clinic_id:int, session:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    clinic_obj = await get_clinic_by_id_crud(session, clinic_id, with_related=False)
    if clinic_obj.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await delete_clinic_crud(session=session, clinic_id=clinic_id)
    return None






