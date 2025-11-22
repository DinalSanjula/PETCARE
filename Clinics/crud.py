from typing import Optional, List, Type, cast, Set, TypeVar
from fastapi import HTTPException, status
from sqlalchemy import select, inspect, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeMeta, selectinload

from Clinics.models import Clinic, Area, ClinicImage
from Clinics.schemas.clinic import ClinicCreate, ClinicUpdate

T = TypeVar("T", bound=DeclarativeMeta)

async def get_or_404(session : AsyncSession, model:Type[T], pk:int, name:str = "item") -> T:
    pk_col = inspect(model).primary_key[0]
    cond = cast(ColumnElement[bool], pk_col == pk)
    q = select(model).where(cond)
    result = await session.execute(q)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return obj


def remove_whitespaces(s : str) -> str:
    return " ".join(s.strip().split())


async def create_formatted_address(session: AsyncSession, clinic: Clinic)-> str | None:
    if clinic.address:
        address = remove_whitespaces(clinic.address)
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
        address = clinic_data.address and remove_whitespaces(clinic_data.address),
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

    if ["profile_pic_url"] in data:
        if data["profile_pic_url"] is not None:
            data["profile_pic_url"] = str(data["profile_pic_url"])

    for key, val in data.items():
        if key not in UPDATABLE_FIELDS:
            continue
        if key == "address" and isinstance(val, str):
            val = remove_whitespaces(val)
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
    clinic = get_or_404(session, Clinic, clinic_id, name="Clinic")
    try:
        await session.delete(clinic)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete clinic")



""" =============================================================================================================================  """

async def create_clinic_image(
        session:AsyncSession,
        clinic_id:int,
        filename:int,
        url:str ,
        content_type:str,
        original_filename: Optional[str] = None
) -> ClinicImage:

    await get_or_404(session, Clinic, clinic_id, name="Clinic")

    image = ClinicImage(
        clinic_id = clinic_id,
        filename = filename,
        original_filename = original_filename,
        url = url,
        content_type = content_type
    )

    session.add(image)
    try:
        await session.commit()
        await session.refresh(image)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))

    return image

async def get_image_by_id(session:AsyncSession, image_id:int)-> ClinicImage:
    cond = cast(ColumnElement[bool], ClinicImage.id == image_id)
    q = select(ClinicImage).where(cond)
    result = await session.execute(q)
    img = result.scalar_one_or_none()
    if img is None:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return img

async def list_images_for_clinic(session:AsyncSession, clinic_id:int)-> List[ClinicImage]:
    cond = cast(ColumnElement[bool], ClinicImage.clinic_id == clinic_id)
    q = select(ClinicImage).where(cond).order_by(ClinicImage.id.asc())
    result = await session.execute(q)
    return list(result.scalars().all())

async def update_clinic_image(
        session:AsyncSession,
        image_id:int,
        filename:Optional[int] = None,
        url:Optional[str] = None,
        content_type:Optional[str] = None,
        original_filename: Optional[str] = None
) -> ClinicImage:

    image = await get_image_by_id(session, image_id)
    changed = False

    if filename is not None:
        image.filename = filename
        changed = True

    if url is not None:
        image.url = url
        changed = True

    if content_type is not None:
        image.content_type = content_type
        changed = True

    if original_filename is not None:
        image.original_filename = original_filename
        changed = True

    if changed:
        session.add(image)
        try:
            await session.commit()
            await session.refresh(image)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return image

async def delete_image(session:AsyncSession, image_id:int) -> None:
    image = await get_image_by_id(session, image_id)

    # success = await storage.delete(image.filename)
    # if not success:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete image file from storage")
    #

    try:
        await session.delete(image)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete database record")