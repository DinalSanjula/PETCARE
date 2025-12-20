from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from Admin.admin_stats_schema import AdminStatsResponse
from Admin.admin_stats_service import get_admin_stats
from Users.auth.security import require_admin

router = APIRouter(tags=["Admin"], dependencies=[Depends(require_admin)])

@router.get("/", response_model=AdminStatsResponse)
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin)
):
    return await get_admin_stats(db)