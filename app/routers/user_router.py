from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserReplace, UserPatch, UserResponse
from app.schemas.service_schema import ServiceResponse, ServiceListResponse
from app.services.user_service import create_user, get_user_by_id, get_all_users, update_user, patch_user, delete_user
from app.auth.security import get_current_active_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ServiceResponse[UserResponse])
async def get_user_by_id_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)):
    result = await get_user_by_id(user_id, db)

    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)

    return result

@router.get("/", status_code=status.HTTP_200_OK, response_model=ServiceListResponse[UserResponse])
async def get_all_users_endpoint(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    return await get_all_users(limit, offset, db)


@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=ServiceResponse[UserResponse])
async def update_user_endpoint(
    user_id: int,
    user: UserReplace,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    result = await update_user(user_id, user, db)

    if not result.success:
        if "not found" in result.message.lower():
            raise HTTPException(status_code=404, detail=result.message)
        raise HTTPException(status_code=400, detail=result.message)

    return result


@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=ServiceResponse[UserResponse])
async def patch_user_endpoint(
    user_id: int,
    user: UserPatch,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    result = await patch_user(user_id, user, db)

    if not result.success:
        if "not found" in result.message.lower():
            raise HTTPException(status_code=404, detail=result.message)
        raise HTTPException(status_code=400, detail=result.message)

    return result


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=ServiceResponse[str])
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    result = await delete_user(user_id, db)

    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)

    return result