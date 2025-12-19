from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from Users.schemas.user_schema import UserAdminResponse, UserRoleUpdate
from Users.schemas.service_schema import ServiceResponse, ServiceListResponse
from Users.auth.security import require_admin
from Users.services.user_service import set_user_active, set_user_role, get_all_users
from db import get_db

router = APIRouter(tags=["Admin Users"], dependencies=[Depends(require_admin)])

@router.patch("/{user_id}/block", response_model=ServiceResponse[UserAdminResponse])
async def block_user( user_id: int, db: AsyncSession = Depends(get_db)):
    result = await set_user_active(user_id=user_id, active=False, db=db)
    if not result.success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.message)

    return result


@router.patch("/{user_id}/unblock", response_model=ServiceResponse[UserAdminResponse])
async def unblock_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await set_user_active(user_id=user_id, active=True, db=db)
    if not result.success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.message)

    return result

@router.patch("/{user_id}/role", response_model=ServiceResponse[UserAdminResponse])
async def set_role(user_id: int,payload: UserRoleUpdate,  db: AsyncSession = Depends(get_db)):
    result = await set_user_role(user_id=user_id, role=payload.role, db=db)
    if not result.success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.message)

    return result

@router.get("/", status_code=status.HTTP_200_OK, response_model=ServiceListResponse[UserAdminResponse])
async def get_all_users_endpoint(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    return await get_all_users(limit, offset, db)


