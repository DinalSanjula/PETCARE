from fastapi import HTTPException, status, Depends, APIRouter
from fastapi.responses import JSONResponse
import logging

from Users.auth import security
from Users.models.logout_and_forgetpw_model import RefreshToken
from Users.schemas.user_schema import UserCreate, UserLogin
from sqlalchemy.ext.asyncio import AsyncSession
from Users.services.auth_service import register_user, login_user, forgot_password, reset_password, logout_user
from db import get_db


router = APIRouter()


#Register endpoint
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await register_user(user, db)

    if not result.success:
        logging.warning("REGISTER FAILED - message: %s, data: %s", getattr(result, "message", None), getattr(result, "data", None))
        if result.message and "exists" in result.message.lower():
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"success": False, "message": result.message})
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"success": False, "message": result.message or "Registration failed"})

    tokens_obj = getattr(result, "data", {}) or {}
    try:
        if hasattr(tokens_obj, "dict") and callable(getattr(tokens_obj, "dict")):
            tokens = tokens_obj.model_dump()
        elif isinstance(tokens_obj, dict):
            tokens = tokens_obj
        else:
            tokens = dict(vars(tokens_obj)) if not isinstance(tokens_obj, (str, int, float)) else {}
    except Exception:
        tokens = {}

    access = tokens.get("access_token") if isinstance(tokens, dict) else None
    if not access:
        access = tokens.get("accessToken") if isinstance(tokens, dict) else None
    if not access:
        access = tokens.get("token") if isinstance(tokens, dict) else None
    if not access:
        access = getattr(tokens_obj, "access_token", None) or getattr(tokens_obj, "accessToken", None) or getattr(tokens_obj, "token", None)

    refresh = tokens.get("refresh_token") if isinstance(tokens, dict) else None
    if not refresh:
        refresh = tokens.get("refreshToken") if isinstance(tokens, dict) else None
    if not refresh:
        refresh = getattr(tokens_obj, "refresh_token", None) or getattr(tokens_obj, "refreshToken", None) or getattr(tokens_obj, "refresh", None)

    if not access:
        # Prefer email from tokens, else from request payload
        email_for_token = None
        if isinstance(tokens, dict):
            email_for_token = tokens.get("email")
        if not email_for_token:
            email_for_token = getattr(tokens_obj, "email", None)
        if not email_for_token:
            email_for_token = user.email  # request payload contains email

        access = security.create_access_token({"sub": email_for_token})
    if not refresh:
        refresh = security.create_refresh_token({"sub": email_for_token if 'email_for_token' in locals() else user.email})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"success": True, "data": {"access_token": access, "refresh_token": refresh}})


#Login endpoint
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await login_user(user_login, db)

    if not result.success:
        logging.warning("LOGIN FAILED - message: %s, data: %s", getattr(result, "message", None), getattr(result, "data", None))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result.message or "Invalid credentials")

    tokens_obj = getattr(result, "data", {}) or {}
    try:
        if hasattr(tokens_obj, "dict") and callable(getattr(tokens_obj, "dict")):
            tokens = tokens_obj.model_dump()
        elif isinstance(tokens_obj, dict):
            tokens = tokens_obj
        else:
            tokens = dict(vars(tokens_obj)) if not isinstance(tokens_obj, (str, int, float)) else {}
    except Exception:
        tokens = {}

    access = tokens.get("access_token") if isinstance(tokens, dict) else None
    if not access:
        access = tokens.get("accessToken") if isinstance(tokens, dict) else None
    if not access:
        access = tokens.get("token") if isinstance(tokens, dict) else None
    if not access:
        access = getattr(tokens_obj, "access_token", None) or getattr(tokens_obj, "accessToken", None) or getattr(tokens_obj, "token", None)

    refresh = tokens.get("refresh_token") if isinstance(tokens, dict) else None
    if not refresh:
        refresh = tokens.get("refreshToken") if isinstance(tokens, dict) else None
    if not refresh:
        refresh = getattr(tokens_obj, "refresh_token", None) or getattr(tokens_obj, "refreshToken", None) or getattr(tokens_obj, "refresh", None)

    if not access:
        email_for_token = None
        if isinstance(tokens, dict):
            email_for_token = tokens.get("email")
        if not email_for_token:
            email_for_token = getattr(tokens_obj, "email", None)
        if not email_for_token:
            email_for_token = user_login.email
        access = security.create_access_token({"sub": email_for_token})
    if not refresh:
        refresh = security.create_refresh_token({"sub": email_for_token if 'email_for_token' in locals() else user_login.email})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True, "data": {"access_token": access, "refresh_token": refresh}})

@router.post("/logout")
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    await logout_user(refresh_token, db)
    return {"success": True, "message": "Logged out successfully"}

@router.post("/forgot-password")
async def forgot_password_endpoint(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    await forgot_password(email, db)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password_endpoint(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    success = await reset_password(token, new_password, db)

    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    return {"message": "Password reset successful"}