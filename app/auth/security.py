# app/auth/security.py
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import bcrypt
from jose import jwt, JWTError
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

# load .env
load_dotenv()

logger = logging.getLogger(__name__)

# Auth scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

from db import get_db as get_db_session
from app.models.user_model import User
from app.schemas.user_schema import TokenData

_FALLBACK_SECRET: Optional[str] = None

def _get_secret_key() -> str:
    global _FALLBACK_SECRET
    key = os.getenv("SECRET_KEY")
    if key and isinstance(key, str) and len(key) > 0:
        return key

    if os.getenv("ENV") == "production" or os.getenv("FASTAPI_ENV") == "production":
        # fail loudly in production
        raise RuntimeError(
            "Missing or invalid SECRET_KEY. Set SECRET_KEY in your environment."
        )

    if _FALLBACK_SECRET is None:
        _FALLBACK_SECRET = "test-" + secrets.token_urlsafe(32)
        logger.warning("SECRET_KEY not found in env.")
    return _FALLBACK_SECRET

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    SECRET_KEY = _get_secret_key()
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    SECRET_KEY = _get_secret_key()
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    SECRET_KEY = _get_secret_key()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise e


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        logger.debug("Decoded token payload: %s", payload)
        email: str = payload.get("sub")
        if email is None:
            logger.debug("Token payload missing 'sub' claim: %s", payload)
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.warning("Token decode/validation failed: %s", str(e))
        raise credentials_exception

    # Query user by email
    try:
        result = await db.execute(select(User).filter_by(email=token_data.email))
        user = result.scalars().first()
    except Exception as e:
        logger.exception("DB error while fetching user during token validation: %s", e)
        raise credentials_exception

    if user is None:
        logger.debug("No user found for email for token: %s", token_data.email)
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user