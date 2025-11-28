from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.user_schema import UserCreate, UserLogin, Token
from app.schemas.service_schema import ServiceResponse
from app.services.auth_service import register_user, login_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ServiceResponse[Token], status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Register a new user"""
    result = await register_user(user, db)

    if not result.success:
        # normalized message check (case-insensitive)
        if "exists" in result.message.lower():
            raise HTTPException(status_code=409, detail=result.message)
        raise HTTPException(status_code=400, detail=result.message)

    return result


@router.post("/login", response_model=ServiceResponse[Token], status_code=status.HTTP_200_OK)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db_session)
):
    """Login user and return JWT tokens"""
    result = await login_user(user_login, db)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.message
        )

    return result




# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.database.session import get_db_session
# from app.schemas.user_schema import UserCreate, UserLogin, Token
# from app.services.auth_service import register_user, login_user
# from app.schemas.service_schema import ServiceResponse
#
# router = APIRouter(prefix="/auth", tags=["Authentication"])
#
#
# @router.post("/register", status_code=status.HTTP_201_CREATED, response_model=ServiceResponse[Token])
# async def register(
#     user: UserCreate,
#     db: AsyncSession = Depends(get_db_session)
# ):
#     """Register a new user"""
#     result = await register_user(user, db)
#     if not result.success:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT if "already exists" in result.message else status.HTTP_400_BAD_REQUEST,
#             detail=result.message
#         )
#     return result
#
#
# @router.post("/login", status_code=status.HTTP_200_OK, response_model=ServiceResponse[Token])
# async def login(
#     user_login: UserLogin,
#     db: AsyncSession = Depends(get_db_session)
# ):
#     """Login user and get JWT tokens"""
#     result = await login_user(user_login, db)
#     if not result.success:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=result.message
#         )
#     return result
#
