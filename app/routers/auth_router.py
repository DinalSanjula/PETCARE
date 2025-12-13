from fastapi import HTTPException, status, Depends, APIRouter
from fastapi.responses import JSONResponse
import logging

# Make sure these imports match your project
from app.auth import security
from app.schemas.user_schema import UserCreate, UserLogin
from sqlalchemy.ext.asyncio import AsyncSession
# from app.database.session import get_db_session
from app.services.auth_service import register_user, login_user
from db import get_db

router = APIRouter()

# ---- Register endpoint (defensive, tolerant) ----
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Defensive register endpoint:
      - returns 201 with {"success": True, "data": {"access_token":..., "refresh_token":...}}
      - returns 409 on duplicate
      - returns 400 on other service-level failures
    """
    result = await register_user(user, db)

    if not result.success:
        logging.warning("REGISTER FAILED - message: %s, data: %s", getattr(result, "message", None), getattr(result, "data", None))
        if result.message and "exists" in result.message.lower():
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"success": False, "message": result.message})
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"success": False, "message": result.message or "Registration failed"})

    # Normalize result.data into a dict (handle Pydantic model or dict)
    tokens_obj = getattr(result, "data", {}) or {}
    try:
        if hasattr(tokens_obj, "dict") and callable(getattr(tokens_obj, "dict")):
            tokens = tokens_obj.model_dump()
        elif isinstance(tokens_obj, dict):
            tokens = tokens_obj
        else:
            # fallback: try to convert via vars()
            tokens = dict(vars(tokens_obj)) if not isinstance(tokens_obj, (str, int, float)) else {}
    except Exception:
        tokens = {}

    # Try to extract tokens in several common naming conventions
    access = tokens.get("access_token") if isinstance(tokens, dict) else None
    if not access:
        access = tokens.get("accessToken") if isinstance(tokens, dict) else None
    if not access:
        access = tokens.get("token") if isinstance(tokens, dict) else None
    if not access:
        # attribute-style fallback
        access = getattr(tokens_obj, "access_token", None) or getattr(tokens_obj, "accessToken", None) or getattr(tokens_obj, "token", None)

    refresh = tokens.get("refresh_token") if isinstance(tokens, dict) else None
    if not refresh:
        refresh = tokens.get("refreshToken") if isinstance(tokens, dict) else None
    if not refresh:
        refresh = getattr(tokens_obj, "refresh_token", None) or getattr(tokens_obj, "refreshToken", None) or getattr(tokens_obj, "refresh", None)

    # If still missing access/refresh, create them using SECURITY fallback
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
        # Use same email_for_token
        refresh = security.create_refresh_token({"sub": email_for_token if 'email_for_token' in locals() else user.email})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"success": True, "data": {"access_token": access, "refresh_token": refresh}})


# ---- Login endpoint (defensive) ----
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Defensive login endpoint:
      - returns 200 with {"success": True, "data": {"access_token":..., "refresh_token":...}}
      - returns 401 on invalid credentials
    """
    result = await login_user(user_login, db)

    if not result.success:
        logging.warning("LOGIN FAILED - message: %s, data: %s", getattr(result, "message", None), getattr(result, "data", None))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result.message or "Invalid credentials")

    # Normalize tokens similarly to register
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

    # fallback token creation if needed
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