from typing import Type, cast, TypeVar

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import select, inspect, ColumnElement
from fastapi import HTTPException, status


import re
from datetime import datetime, timezone
from typing import Optional

from Users.auth.security import get_current_active_user
from Users.models import UserRole, User

T = TypeVar("T", bound=DeclarativeMeta)

async def get_or_404(session : AsyncSession, model:Type[T], pk:int, name:str = "item") -> T:
    pk_col = inspect(model).primary_key[0]
    cond = cast(ColumnElement[bool], pk_col == pk)
    q = select(model).where(cond)
    result = await session.execute(q)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} not found")
    return obj



def normalize_address(s: Optional[str]) -> Optional[str]:
    if not s:
        return s
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s

def now_utc():
    return datetime.now(timezone.utc)

def require_roles(*roles: UserRole):
    def checker(user: User = Depends(get_current_active_user)):
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return checker


from datetime import timezone
from zoneinfo import ZoneInfo

SL_TZ = ZoneInfo("Asia/Colombo")

def to_local_time(dt):
    if dt is None:
        return None
    return dt.astimezone(SL_TZ)