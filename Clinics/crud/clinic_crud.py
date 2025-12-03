from typing import List, cast, Set, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, inspect, ColumnElement, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import  selectinload

from Clinics.crud.geocode import geocode_async, OpenCageRateLimitError, OpenCageInvalidInputError, OpenCageUnknownError
from Clinics.models import Clinic, Area
from Clinics.schemas.clinic import ClinicCreate, ClinicUpdate
from Clinics.utils.helpers import normalize_address, get_or_404, now_utc


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

    raw_address = clinic_data.address or None
    address_norm = normalize_address(raw_address) if raw_address else None

    lat = getattr(clinic_data, "latitude", None)
    lng = getattr(clinic_data, "longitude", None)
    formatted_address = None
    geocoded_at = None
    geocode_source = None

    if (lat is None or lng is None) and address_norm:
        queries = []
        if clinic_data.area_id:
            area = await session.get(Area, clinic_data.area_id)
            if area and getattr(area, "name", None):
                addr = f"{address_norm}, {area.name}"
                queries.append(addr)

        queries.append(address_norm)
        queries.append(f"{address_norm}, Sri Lanka")

        for q in queries:
            try:
                geo_lat, geo_lng, geo_formatted = await geocode_async(q, countrycode="lk")
            except OpenCageRateLimitError:
                geo_lat, geo_lng, geo_formatted = None, None, None
                break
            except(OpenCageInvalidInputError, OpenCageUnknownError):
                continue

            if geo_lat is not None:
                lat = lat or geo_lat
                lng = lng or geo_lng
                formatted_address = formatted_address or geo_formatted
                geocoded_at = now_utc()
                geocode_source = "opencage"
                break

            if (lat is None or lng is None) and clinic_data.area_id:
                area = await session.get(Area, clinic_data.area_id)
                if area:
                    lat = lat or getattr(area, "latitude", None)
                    lng = lng or getattr(area, "longitude", None)
                    formatted_address = formatted_address or getattr(area, "formatted_address", None)

                    if lat is not None and lng is not None and geocode_source is None:
                        geocoded_at = now_utc()
                        geocode_source = "area_fallback"


    data = Clinic(
        owner_id = clinic_data.owner_id, #maybe current user from users
        name = clinic_data.name,
        description = clinic_data.description,
        phone = clinic_data.phone,
        address =raw_address and normalize_address(raw_address),
        formatted_address=formatted_address,
        profile_pic_url = str(clinic_data.profile_pic_url) if clinic_data.profile_pic_url else None,
        area_id = clinic_data.area_id,
        latitude = lat,
        longitude = lng,
        geocoded_at=geocoded_at,
        geocode_source=geocode_source
    )
    session.add(data)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))

    cond = cast(ColumnElement[bool], Clinic.id == data.id)
    q = (select(Clinic).options(selectinload(Clinic.images), selectinload(Clinic.area)).where(cond))
    res = await session.execute(q)
    data = res.scalar_one()
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


    if "latitude" in data and "longitude" in data:
        if data.get("latitude")is not None and data.get("longitude") is not None:
            coordinates_provided = True
        else:
            coordinates_provided = False
    else:
        coordinates_provided = False

    address_and_area_changed = any(k in data for k in ("address", "area_id"))

    if coordinates_provided:
        clinic.geocoded_at = now_utc()
        clinic.geocode_source = "user_pin"
        changed = True

    elif address_and_area_changed:
        addr = clinic.address
        lat = clinic.latitude
        lng = clinic.longitude
        formatted_address = None
        geocoded_at = None
        geocode_source = None

        if (lat is None or lng is None) and addr:
            queries = []
            if clinic_data.area_id:
                area = await session.get(Area, clinic_data.area_id)
                if area and getattr(area, "name", None):
                    queries.append(
                        f"{addr}, {area.name}"
                    )
            queries.append(addr)
            queries.append(f"{addr}, Sri Lanka")

            for q in queries:
                try:
                    geo_lat, geo_lng, geo_formatted = await geocode_async(q, countrycode="lk")
                except OpenCageRateLimitError:
                    geo_lat, geo_lng, geo_formatted = None, None, None
                    break
                except(OpenCageInvalidInputError, OpenCageUnknownError):
                    continue

                if geo_lat is not None:
                    clinic.latitude = lat or geo_lat
                    clinic.longitude = lng or geo_lng
                    clinic.formatted_address = formatted_address or geo_formatted
                    clinic.geocoded_at = now_utc()
                    clinic.geocode_source = "opencage"
                    changed = True
                    break

        if (clinic.latitude is None or clinic.longitude is None) and clinic.area_id:
            area = await session.get(Area, clinic.area_id)
            if area and area.latitude is not None and area.longitude is not None:
                clinic.latitude = clinic.latitude or area.latitude
                clinic.longitude = clinic.longitude or area.longitude
                clinic.formatted_address = clinic.formatted_address or area.formatted_address

                if clinic.geocode_source is None:
                    clinic.geocoded_at = now_utc()
                    clinic.geocode_source = "area_fallback"
                changed = True

    if changed:
        session.add(clinic)
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))

        cond = cast(ColumnElement[bool], Clinic.id == clinic.id)
        q = (select(Clinic).options(selectinload(Clinic.images), selectinload(Clinic.area)).where(cond))
        res = await session.execute(q)
        clinic = res.scalar_one()
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