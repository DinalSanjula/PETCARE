from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from Clinics.schemas.clinic import ClinicAdminResponse
from Clinics.crud.clinic_crud import set_clinic_active, list_clinics
from Users.schemas.service_schema import ServiceResponse

from db import get_db
from Users.auth.security import get_current_active_user, require_admin

router = APIRouter(tags=["Admin Clinics"], dependencies=[Depends(require_admin)])

@router.patch("/{clinic_id}/suspend" , response_model=ServiceResponse[ClinicAdminResponse])
async def suspend_clinic(clinic_id : int, db: AsyncSession = Depends(get_db)):
    clinic = await set_clinic_active(session=db, clinic_id=clinic_id, active=False)

    return ServiceResponse(
        success=True,
        message="Clinic suspended or rejected successfully",
        data=ClinicAdminResponse.model_validate(clinic)
    )


@router.patch("/{clinic_id}/activate", response_model=ServiceResponse[ClinicAdminResponse])
async def activate_clinic(clinic_id: int, db: AsyncSession = Depends(get_db)):
    clinic = await set_clinic_active(session=db, clinic_id=clinic_id, active=True)

    return ServiceResponse(
        success=True,
        message="Clinic activated successfully",
        data=ClinicAdminResponse.model_validate(clinic)
    )

@router.get("/", response_model=List[ClinicAdminResponse])
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
