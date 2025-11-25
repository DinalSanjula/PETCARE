from typing import List, cast, Set, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, inspect, ColumnElement, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import  selectinload
from Clinics.models import Clinic, Area
from Clinics.schemas.clinic import ClinicCreate, ClinicUpdate
from Clinics.utils.helpers import normalize_address, get_or_404


async def create_formatted_address(session: AsyncSession, clinic: Clinic)-> str | None:
    if clinic.address:
        address = normalize_address(clinic.address)
    else:
        address = None


    area_name = None
    if clinic.area_id:
        area = await session.get(Area, clinic.area_id)
        if area:
            area_name = area.name


    if address and area_name:
        return f"{address}, {area_name}"
    return address



async def create_clinic(session : AsyncSession, clinic_data : ClinicCreate) -> Clinic:


    data = Clinic(
        owner_id = clinic_data.owner_id, #maybe current user from users
        name = clinic_data.name,
        description = clinic_data.description,
        phone = clinic_data.phone,
        address =clinic_data.address and normalize_address(clinic_data.address),
        profile_pic_url = str(clinic_data.profile_pic_url) if clinic_data.profile_pic_url else None,
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



async def get_clinic_by_id(session: AsyncSession, clinic_id: int, with_related: bool = True) -> Clinic:

    pk_col = inspect(Clinic).primary_key[0]
    cond = cast(ColumnElement[bool], pk_col == clinic_id)
    q = select(Clinic).where(cond)

    if with_related:
        q = q.options(selectinload(Clinic.area), selectinload(Clinic.images))

    result = await session.execute(q)
    clinic = result.scalar_one_or_none()

    if clinic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
    return clinic



async def get_clinic_by_phone(session : AsyncSession, phone : str, with_related: bool = True) -> Clinic:

    cond = cast(ColumnElement[bool], Clinic.phone == phone)
    q = select(Clinic).where(cond)

    if with_related:
        q = q.options(selectinload(Clinic.area), selectinload(Clinic.images))

    result = await session.execute(q)
    clinic = result.scalar_one_or_none()

    if clinic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
    return clinic



async def get_clinic_by_name(session: AsyncSession, name: str, with_related: bool = True) -> Clinic:

    cond = cast(ColumnElement[bool], Clinic.name == name)
    q = select(Clinic).where(cond)

    if with_related:
        q= q.options(selectinload(Clinic.area), selectinload(Clinic.images))

    result = await session.execute(q)
    clinic = result.scalar_one_or_none()

    if clinic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
    return clinic



async def get_clinic_by_owner(session: AsyncSession, owner_id: int, limit: int, offset: int,  with_related: bool = True) -> List[Clinic]:
    cond = cast(ColumnElement[bool], Clinic.owner_id == owner_id)
    q = select(Clinic).where(cond)

    if with_related:
        q = q.options(selectinload(Clinic.area), selectinload(Clinic.images))

    q = q.limit(limit).offset(offset)

    result = await session.execute(q)
    clinics = list(result.scalars().unique().all())

    return clinics


UPDATABLE_FIELDS : Set[str] = {
    "name", "description", "phone", "address", "profile_pic_url", "area_id", "latitude", "longitude", "is_active"
}

async def update_clinic(session : AsyncSession, clinic_id:int, clinic_data: ClinicUpdate) -> Clinic:

    clinic = await get_or_404(session, Clinic, clinic_id , name="Clinic")

    data = clinic_data.model_dump(exclude_unset=True)

    if not data:
        return clinic

    changed = False

    if "profile_pic_url" in data:
        if data["profile_pic_url"] is not None:
            data["profile_pic_url"] = str(data["profile_pic_url"])

    for key, val in data.items():
        if key not in UPDATABLE_FIELDS:
            continue
        if key == "address" and isinstance(val, str):
            val = normalize_address(val)
        setattr(clinic, key, val)
        changed = True

    if any(k in data for k in( "address" , "latitude", "longitude", "area_id")):
        clinic.formatted_address = await create_formatted_address(session, clinic)
        changed = True

    if changed:
        session.add(clinic)
        try:
            await session.commit()
            await session.refresh(clinic)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    return clinic



async def delete_clinic(session:AsyncSession, clinic_id : int)-> None:
    clinic = await get_or_404(session, Clinic, clinic_id, name="Clinic")
    try:
        await session.delete(clinic)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete clinic")


async def list_clinics(
        session: AsyncSession,
        limit : int = 20,
        offset : int = 0,
        *,
        owner_id: Optional[int] = None,
        area_id : Optional[int] = None,
        name : Optional[str] = None,
        phone : Optional[str] = None,
        is_active : Optional[bool] = None,
        with_related : bool = True
)-> List[Clinic]:

    conditions = []

    if owner_id is not None:
        conditions.append(Clinic.owner_id == owner_id)
    if area_id is not None:
        conditions.append(Clinic.area_id == area_id)
    if name is not None:
        conditions.append(Clinic.name.ilike(f"%{name}%"))
    if phone is not None:
        conditions.append(Clinic.phone == phone)
    if is_active is not None:
        conditions.append(Clinic.is_active == is_active)

    q = select(Clinic)
    if conditions:
        q = q.where(and_(*conditions))
    if with_related:
        q = q.options(selectinload(Clinic.area), selectinload(Clinic.images))

    q = q.limit(limit).offset(offset)

    result = await session.execute(q)
    clinics = list(result.scalars().unique().all())
    return clinics