from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Clinics.utils.helpers import require_roles
from Users.models import UserRole
from Users.models.user_model import User
from Users.schemas.user_schema import UserCreate, UserReplace, UserPatch, UserResponse
from Users.schemas.service_schema import ServiceResponse, ServiceListResponse
from Users.services.user_service import create_user, get_user_by_id, get_all_users, update_user, patch_user, delete_user
from Users.auth.security import get_current_active_user
from db import get_db


router = APIRouter(tags=["Users"])


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ServiceResponse[UserResponse])
async def get_user_by_id_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):

    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    result = await get_user_by_id(user_id, db)

    if not result.success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.message)

    return result

@router.get("/", status_code=status.HTTP_200_OK, response_model=ServiceListResponse[UserResponse], dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def get_all_users_endpoint(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    users, total = await get_all_users(limit, offset, db)
    return ServiceListResponse(
        success=True,
        message="Users retrieved successfully",
        data=users,
        total=total,
        limit=limit,
        offset=offset
    )


@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=ServiceResponse[UserResponse])
async def update_user_endpoint(
    user_id: int,
    user: UserReplace,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    result = await update_user(user_id, user, db)

    if not result.success:
        if "not found" in result.message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.message)

    return result


@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=ServiceResponse[UserResponse])
async def patch_user_endpoint(
    user_id: int,
    user: UserPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    result = await patch_user(user_id, user, db)

    if not result.success:
        if "not found" in result.message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.message)

    return result


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=ServiceResponse[str], dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await delete_user(user_id, db)

    if not result.success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.message)

    return result