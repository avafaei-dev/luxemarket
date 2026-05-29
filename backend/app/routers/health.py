from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import get_settings
from app.cache import get_redis

router = APIRouter(prefix="/api/v1", tags=["health"])
settings = get_settings()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    # DB check
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    # Redis check
    try:
        r = get_redis()
        if r:
            r.ping()
            redis_status = "connected"
        else:
            redis_status = "unavailable"
    except Exception as e:
        redis_status = f"error: {e}"

    return {
        "status": "ok",
        "db": db_status,
        "redis": redis_status,
        "environment": settings.app_env,
    }