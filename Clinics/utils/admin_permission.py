from fastapi import Depends

from app.auth.security import get_current_active_user


async def require_admin(user=Depends(get_current_active_user)):
    return user
