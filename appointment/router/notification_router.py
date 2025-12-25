from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from appointment.service.notification_service import get_notifications_by_user
from db import get_db

from appointment.schema.notification_schema import NotificationResponse


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/notify", response_model=List[NotificationResponse])
async def get_notifications(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_notifications_by_user(db, user_id)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return result.data