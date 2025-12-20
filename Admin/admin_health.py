from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import time
from datetime import datetime, timezone

from db import get_db
from Users.auth.security import require_admin

router = APIRouter(
    tags=["Admin Health"],
    dependencies=[Depends(require_admin)],
)


@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    response = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {},
    }

    start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        latency_ms = int((time.perf_counter() - start) * 1000)
        response["database"] = {
            "status": "ok",
            "latency_ms": latency_ms,
        }
    except Exception as e:
        response["status"] = "degraded"
        response["database"] = {
            "status": "down",
            "error": str(e),
        }

    return response