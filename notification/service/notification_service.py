from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from Users.schemas.service_schema import NotificationMsgResponse
from notification.model.notification_model import Notification


async def create_notification(db: AsyncSession, user_id: int, title: str, message: str)-> NotificationMsgResponse[Notification]:

    notification = Notification(
        user_id=user_id,
        title=title,
        message=message
    )

    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    return NotificationMsgResponse(
        success=True,
        message="Notification created",
        data=notification
    )

async def get_notifications_by_user(db: AsyncSession , user_id: int) -> NotificationMsgResponse[list[Notification]]:

    stmt = select(Notification).where(Notification.user_id == user_id)
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    return NotificationMsgResponse(
        success=True,
        message="Notifications retrieved",
        data=notifications
    )