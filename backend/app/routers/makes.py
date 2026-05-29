from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Listing
from app.schemas import MakeCount, ModelCount
from app.cache import cache_get, cache_set, make_cache_key

router = APIRouter(prefix="/api/v1", tags=["makes"])

MAKES_TTL = 300  # 5 minutes — makes list rarely changes


@router.get("/makes", response_model=list[MakeCount])
def get_makes(db: Session = Depends(get_db)):
    cache_key = make_cache_key("makes", "all")
    cached = cache_get(cache_key)
    if cached:
        return cached

    rows = (
        db.query(Listing.make, func.count(Listing.id).label("count"))
        .filter(Listing.is_active == True)
        .group_by(Listing.make)
        .order_by(func.count(Listing.id).desc())
        .all()
    )
    result = [{"make": r.make, "count": r.count} for r in rows]
    cache_set(cache_key, result, ttl=MAKES_TTL)
    return result


@router.get("/makes/{make}/models", response_model=list[ModelCount])
def get_models_for_make(make: str, db: Session = Depends(get_db)):
    cache_key = make_cache_key("makes", make.lower(), "models")
    cached = cache_get(cache_key)
    if cached:
        return cached

    rows = (
        db.query(Listing.model, func.count(Listing.id).label("count"))
        .filter(
            func.lower(Listing.make) == make.lower(),
            Listing.is_active == True,
        )
        .group_by(Listing.model)
        .order_by(func.count(Listing.id).desc())
        .all()
    )
    result = [{"model": r.model, "count": r.count} for r in rows]
    cache_set(cache_key, result, ttl=MAKES_TTL)
    return result