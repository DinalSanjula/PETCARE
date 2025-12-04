from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from Clinics.schemas.area import AreaResponse, AreaCreate, AreaUpdate
from Clinics.utils.admin_permission import require_admin
from db import get_db
from Clinics.crud.area_crud import create_area as create, get_area, re_geocode_area, update_area as update, delete_area as delete, list_areas, autocomplete

router = APIRouter()

@router.get("/areas", response_model=List[AreaResponse])
async def list_multiple_areas(q : Optional[str] = Query(None, description="Search text for area name"),
                     main_region : Optional[str] = Query(None, description="Filter by region"),
                     limit : int = Query(50, ge=1, le=200),
                     offset : int = Query(0, ge=0),
                     session: AsyncSession = Depends(get_db)):

    areas = await list_areas(session=session, q=q, main_region=main_region, limit=limit, offset=offset)
    return areas

@router.get("/autocomplete", response_model=List[AreaResponse])
async def autocomplete_areas(q: str = Query(..., max_length=100, description="query for autocomplete"),
                             session : AsyncSession = Depends(get_db),
                             limit : int = Query(10, ge=1, le=50)):

    items = await autocomplete(session=session, q=q, limit=limit)
    return items

@router.get("/{area_id}", response_model=AreaResponse)
async def get_area_by_id(area_id : int , session: AsyncSession = Depends(get_db)):
    area = await get_area(session=session, area_id=area_id)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found")
    return area

@router.post("/admin" , response_model=AreaResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_area(area_in:AreaCreate, session : AsyncSession = Depends(get_db)):
    return await create(session=session, area_in=area_in)

@router.patch("/admin/{area_id}", response_model=AreaResponse, dependencies=[Depends(require_admin)])
async def update_area(area_id:int, area_up:AreaUpdate, session : AsyncSession = Depends(get_db)):
    area = await update(session=session, area_id=area_id, area_up=area_up)
    return area

@router.post("/admin/{area_id}/re-geocode", response_model=AreaResponse, dependencies=[Depends(require_admin)])
async def re_geocode(area_id:int, session : AsyncSession = Depends(get_db)):
    area = await re_geocode_area(session=session, area_id=area_id)
    return area

@router.delete("/admin/{area_id}",status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends (require_admin)])

async def delete_area(area_id: int , session: AsyncSession = Depends(get_db)):
    await delete(session=session, area_id=area_id)
    return None



