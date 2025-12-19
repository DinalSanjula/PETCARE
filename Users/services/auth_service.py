from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from Users.models.user_model import User
from Users.schemas.user_schema import UserCreate, UserLogin, Token
from Users.schemas.service_schema import ServiceResponse
from Users.auth.security import (verify_password, get_password_hash, create_access_token, create_refresh_token, )
from Users.services.user_service import get_user_by_email, create_user


#Register new user and return access & refresh tokens
async def register_user(user: UserCreate, db: AsyncSession) -> ServiceResponse[Token]:

    try:
        # Check if user exists
        existing = await get_user_by_email(user.email, db)
        if existing:
            return ServiceResponse(
                success=False,
                message="User with this email already exists",
                data=None
            )

        # Create user (ensure hashing is done inside create_user)
        result = await create_user(user, db)
        if not result.success:
            return ServiceResponse(
                success=False,
                message=result.message,
                data=None
            )

        user_obj = result.data  # ORM User model

        # Create tokens
        expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user_obj.email, "user_id": user_obj.id},
            expires_delta=expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user_obj.email, "user_id": user_obj.id}
        )

        tokens = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

        return ServiceResponse(
            success=True,
            message="User registered successfully",
            data=tokens
        )

    except Exception as e:
        return ServiceResponse(
            success=False,
            message=f"Registration failed: {str(e)}",
            data=None
        )


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:

    user = await get_user_by_email(email, db)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def login_user(user_login: UserLogin, db: AsyncSession) -> ServiceResponse[Token]:

    try:
        user = await authenticate_user(user_login.email, user_login.password, db)
        if not user:
            return ServiceResponse(
                success=False,
                message="Incorrect email or password",
                data=None
            )

        # Create tokens
        expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )

        tokens = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

        return ServiceResponse(
            success=True,
            message="Login successful",
            data=tokens
        )

    except Exception as e:
        return ServiceResponse(
            success=False,
            message=f"Login failed: {str(e)}",
            data=None
        )
