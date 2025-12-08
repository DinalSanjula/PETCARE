from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.schemas.user_schema import UserCreate, UserLogin, Token
from app.schemas.service_schema import ServiceResponse
from app.services.auth_service import register_user, login_user



router = APIRouter()


# REGISTER
@router.post("/register", response_model=ServiceResponse[Token], status_code=status.HTTP_201_CREATED
)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session)):

    result = await register_user(user, db)

    if not result.success:
        # If username/email already exists
        if "exists" in result.message.lower():
            raise HTTPException(status_code=409, detail=result.message)

        raise HTTPException(status_code=400, detail=result.message)

    return result


# Login
@router.post("/login", response_model=ServiceResponse[Token], status_code=status.HTTP_200_OK )
async def login(

    user_login: UserLogin,
    db: AsyncSession = Depends(get_db_session)):
    result = await login_user(user_login, db)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.message
        )

    return result

# LOGIN
# @router.post("/token", response_model=Token)
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: AsyncSession = Depends(get_db_session)):
#
#     # Reuse the same login logic but adapt the input
#     user_login = UserLogin(email=form_data.username, password=form_data.password)
#     result = await login_user(user_login, db)
#
#     if not result.success:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     return result.data