from typing import Type, cast, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import select, inspect, ColumnElement
from fastapi import HTTPException, status





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


def remove_whitespaces(s : str) -> str:
    return " ".join(s.strip().split())
