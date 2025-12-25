from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from Reports.models.models import Report, ReportMessage
from Clinics.utils.helpers import get_or_404
from sqlalchemy import select, update



async def create_report_message(
    session: AsyncSession,
    report_id: int,
    sender_user_id: int,
    message: str,
) -> ReportMessage:

    await get_or_404(session, Report, report_id, name="Report")

    msg = ReportMessage(
        report_id=report_id,
        sender_user_id=sender_user_id,
        message=message,
    )

    session.add(msg)

    try:
        await session.commit()
        await session.refresh(msg)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.orig),
        )

    return msg


async def list_messages_for_report(
    session: AsyncSession,
    report_id: int,
) -> List[ReportMessage]:

    await get_or_404(session, Report, report_id, name="Report")

    # Fetch messages
    result = await session.execute(
        select(ReportMessage)
        .where(ReportMessage.report_id == report_id)
        .order_by(ReportMessage.created_at.asc())
    )

    messages = list(result.scalars().all())

    # Mark unread messages as read
    unread_ids = [m.id for m in messages if not m.is_read]

    if unread_ids:
        await session.execute(
            update(ReportMessage)
            .where(ReportMessage.id.in_(unread_ids))
            .values(is_read=True)
        )
        await session.commit()

        # Reflect updated state in objects
        for m in messages:
            m.is_read = True

    return messages