from select import select
import secrets
from sqlalchemy import select

from Users.models.logout_and_forgetpw_model import PasswordResetToken
from Users.auth.security import hash_reset_token, verify_reset_token, get_password_hash
from Users.utils.email import send_reset_email

from typing import Optional
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from Users.models.user_model import User
from Users.models.logout_and_forgetpw_model import RefreshToken
from Users.schemas.user_schema import UserCreate, UserLogin, Token
from Users.schemas.service_schema import ServiceResponse
from Users.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from Users.services.user_service import get_user_by_email, create_user


RESET_TOKEN_EXPIRE_MINUTES = 15


async def register_user(user: UserCreate, db: AsyncSession) -> ServiceResponse[Token]:
    try:
        existing = await get_user_by_email(user.email, db)
        if existing:
            return ServiceResponse(
                success=False,
                message="User with this email already exists",
                data=None
            )

        result = await create_user(user, db)
        if not result.success:
            return ServiceResponse(
                success=False,
                message=result.message,
                data=None
            )

        user_obj: User = result.data

        access_token = create_access_token(
            data={"sub": user_obj.email, "user_id": user_obj.id},
            expires_delta=timedelta(minutes=30)
        )

        refresh_token = create_refresh_token(
            data={"sub": user_obj.email, "user_id": user_obj.id}
        )

        db_token = RefreshToken(
            user_id=user_obj.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        db.add(db_token)
        await db.commit()

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

async def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession
) -> Optional[User]:
    user = await get_user_by_email(email, db)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user

async def login_user(
    user_login: UserLogin,
    db: AsyncSession
) -> ServiceResponse[Token]:
    try:
        user = await authenticate_user(
            user_login.email,
            user_login.password,
            db
        )

        if not user:
            return ServiceResponse(
                success=False,
                message="Incorrect email or password",
                data=None
            )

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(minutes=30)
        )

        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )

        db_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        db.add(db_token)
        await db.commit()

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


async def logout_user(refresh_token: str, db: AsyncSession):
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    token_obj = result.scalars().first()

    if token_obj:
        token_obj.is_revoked = True
        await db.commit()


async def forgot_password(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)

    if not user:
        return

    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_reset_token(raw_token)

    reset = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    )

    db.add(reset)
    await db.commit()

    send_reset_email(user.email, raw_token)


async def reset_password(token: str, new_password: str, db: AsyncSession) -> bool:
    result = await db.execute(
        select(PasswordResetToken)
        .where(
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.now(timezone.utc)
        )
        .order_by(PasswordResetToken.created_at.desc())
    )

    tokens = result.scalars().all()

    for reset in tokens:
        if verify_reset_token(token, reset.token_hash):
            user = await db.get(User, reset.user_id)
            user.password_hash = get_password_hash(new_password)
            reset.used = True
            await db.commit()
            return True

    return False