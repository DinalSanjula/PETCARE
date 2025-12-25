from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from notification.schema.notification_schema import NotificationResponse
from notification.service.notification_service import get_notifications_by_user


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/notify", response_model=List[NotificationResponse])
async def get_notifications(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_notifications_by_user(db, user_id)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return result.data