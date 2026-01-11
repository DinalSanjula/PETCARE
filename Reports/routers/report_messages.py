from fastapi import APIRouter, Depends, status
from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db import get_db
from Users.auth.security import get_current_active_user
from Clinics.utils.helpers import require_roles
from Users.models import User, UserRole

from Reports.schemas.schemas import (
    ReportMessageCreate,
    ReportMessageResponse,
)

from Reports.services.report_messages import (
    create_report_message,
    list_messages_for_report,
)
router = APIRouter(tags=["report messages"])

@router.post(
    "/{report_id}/messages",
    response_model=ReportMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_report_message(
    report_id: int,
    payload: ReportMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
   msg = await create_report_message(
       session=db,
       report_id=report_id,
       sender_user_id=current_user.id,
       message=payload.message
   )

   return ReportMessageResponse(
       id=msg.id,
       report_id=msg.report_id,
       message=msg.message,
       sender_user_id=msg.sender_user_id,
       sender_name=current_user.name,
       created_at=msg.created_at,
       is_read=False
   )


@router.get(
    "/{report_id}/messages",
    response_model=List[ReportMessageResponse],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def read_report_messages(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    messages = await list_messages_for_report(db, report_id)

    return [
        ReportMessageResponse(
            id=msg.id,
            report_id=msg.report_id,
            message=msg.message,
            sender_user_id=msg.sender_user_id,
            sender_name=msg.sender.name,
            created_at=msg.created_at,
            is_read=msg.is_read
        )
        for msg in messages
    ]