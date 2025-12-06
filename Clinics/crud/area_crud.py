# crud/area.py
from typing import List, Optional, Tuple, cast
from fastapi import HTTPException, status
from sqlalchemy import select, ColumnElement
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from Clinics.models import Area
from Clinics.schemas.area import AreaCreate, AreaUpdate  # AreaResponse is used by FastAPI response_model
from Clinics.crud.geocode import geocode_async, OpenCageUnknownError, OpenCageRateLimitError, OpenCageInvalidInputError
from Clinics.utils.helpers import normalize_address, now_utc


async def _try_geocode_for_area(base_q: str, main_region: Optional[str]) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:

    tried = [base_q]
    if main_region:
        tried.append(f"{base_q}, {main_region}")
    tried.append(f"{base_q}, Sri Lanka")

    for q in tried:
        try:
            geo_lat, geo_lng, geo_formatted = await geocode_async(q, countrycode="lk")
        except OpenCageRateLimitError:
            return None, None, None, None
        except (OpenCageInvalidInputError, OpenCageUnknownError):
            continue

        if geo_lat is not None:
            return geo_lat, geo_lng, geo_formatted, "opencage"

    return None, None, None, None


async def create_area(session: AsyncSession, area_in: AreaCreate) -> Area:

    name_raw = area_in.name
    main_region = area_in.main_region
    normalized_name = area_in.normalized_name or name_raw.lower().replace(" ", "-")

    base_q = area_in.formatted_address or normalize_address(name_raw) or name_raw

    lat = None
    lng = None
    formatted = area_in.formatted_address
    geocoded_at = None
    geocode_source = None

    geo_lat, geo_lng, geo_formatted, source = await _try_geocode_for_area(base_q, main_region)
    if geo_lat is not None:
        lat, lng = geo_lat, geo_lng
        formatted = formatted or geo_formatted
        geocoded_at = now_utc()
        geocode_source = source

    area = Area(
        name=name_raw,
        normalized_name=normalized_name,
        main_region=main_region,
        formatted_address=formatted,
        latitude=lat,
        longitude=lng,
        geocoded_at=geocoded_at,
        geocode_source=geocode_source,
    )

    session.add(area)
    try:
        await session.commit()
        await session.refresh(area)
    except IntegrityError as e:
        await session.rollback()
        detail = str(e.orig) if getattr(e, "orig", None) else "Integrity error"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return area


async def list_areas(session: AsyncSession, q: Optional[str] = None, main_region: Optional[str] = None,
                     limit: int = 50, offset: int = 0) -> List[Area]:

    query = select(Area).order_by(Area.name)
    if q:
        q_norm = f"%{q.strip().lower()}%"
        query = query.where((Area.name.ilike(q_norm)) | (Area.normalized_name.ilike(q_norm)))
    if main_region:
        cond = cast(ColumnElement[bool], Area.main_region == main_region)
        query = query.where(cond)


    query = query.limit(limit).offset(offset)
    res = await session.execute(query)
    return list(res.scalars().all())


async def autocomplete(session: AsyncSession, q: str, limit: int = 10) -> List[Area]:

    q = q.strip()
    if not q:
        return []

    # try prefix matches first
    prefix = f"{q}%"
    stmt = select(Area).where(Area.name.ilike(prefix)).order_by(Area.name).limit(limit)
    res = await session.execute(stmt)
    rows = list(res.scalars().all())
    if len(rows) >= limit:
        return rows

    # fallback to substring search to fill results
    remaining = limit - len(rows)
    substr = f"%{q}%"
    stmt2 = select(Area).where(Area.name.ilike(substr)).order_by(Area.name).limit(remaining)
    res2 = await session.execute(stmt2)
    rows2 = res2.scalars().all()

    ids = {r.id for r in rows}
    for r in rows2:
        if r.id not in ids:
            rows.append(r)
            ids.add(r.id)
    return rows


async def get_area(session: AsyncSession, area_id: int) -> Optional[Area]:
    return await session.get(Area, area_id)


async def update_area(session: AsyncSession, area_id: int, area_up: AreaUpdate) -> Area:

    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found")

    data = area_up.model_dump(exclude_unset=True)
    if not data:
        return area

    for key, val in data.items():
        # Allow admin to override coordinates directly
        setattr(area, key, val)

    if any(k in data for k in ("name", "main_region", "formatted_address")) and not ("latitude" in data and "longitude" in data):
        base_q = area.formatted_address or normalize_address(area.name)
        geo_lat, geo_lng, geo_formatted, source = await _try_geocode_for_area(base_q, area.main_region)
        if geo_lat is not None:
            area.latitude = geo_lat
            area.longitude = geo_lng
            area.formatted_address = area.formatted_address or geo_formatted
            area.geocoded_at = now_utc()
            area.geocode_source = source

    session.add(area)
    try:
        await session.commit()
        await session.refresh(area)
    except IntegrityError as e:
        await session.rollback()
        detail = str(e.orig) if getattr(e, "orig", None) else "Integrity error"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return area


async def re_geocode_area(session: AsyncSession, area_id: int) -> Area:

    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found")

    base_q = area.formatted_address or normalize_address(area.name)
    g_lat, g_lng, g_formatted, source = await _try_geocode_for_area(base_q, area.main_region)
    if g_lat is None:
        return area

    area.latitude = g_lat
    area.longitude = g_lng
    area.formatted_address = area.formatted_address or g_formatted
    area.geocoded_at = now_utc()
    area.geocode_source = source

    session.add(area)
    try:
        await session.commit()
        await session.refresh(area)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return area


async def delete_area(session: AsyncSession, area_id: int) -> None:
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found")
    try:
        await session.delete(area)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete this area")