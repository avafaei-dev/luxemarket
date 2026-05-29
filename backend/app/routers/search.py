from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.database import get_db
from app.models import Listing, DealScore
from app.schemas import SearchFilters, ListingsResponse
from app.cache import cache_get, cache_set, make_cache_key
import json

router = APIRouter(prefix="/api/v1", tags=["search"])

SEARCH_TTL = 45  # slightly shorter TTL — search results feel more dynamic


@router.post("/listings/search", response_model=ListingsResponse)
def search_listings(filters: SearchFilters, db: Session = Depends(get_db)):
    # Cache key from the full filter payload
    cache_key = make_cache_key("search", json.dumps(filters.model_dump(), sort_keys=True, default=str))
    cached = cache_get(cache_key)
    if cached:
        return cached

    q = (
        db.query(Listing)
        .options(joinedload(Listing.deal_score), joinedload(Listing.valuation))
        .filter(Listing.is_active.is_(True))
    )

    # Free-text search across make, model, description
    if filters.query:
        term = f"%{filters.query.lower()}%"
        q = q.filter(
            or_(
                func.lower(Listing.make).like(term),
                func.lower(Listing.model).like(term),
                func.lower(Listing.description).like(term),
                func.lower(Listing.location_city).like(term),
            )
        )

    # Multi-value filters
    if filters.make:
        makes_lower = [m.lower() for m in filters.make]
        q = q.filter(func.lower(Listing.make).in_(makes_lower))

    if filters.model:
        models_lower = [m.lower() for m in filters.model]
        q = q.filter(func.lower(Listing.model).in_(models_lower))

    if filters.condition:
        q = q.filter(Listing.condition.in_(filters.condition))

    if filters.location_state:
        states_lower = [s.lower() for s in filters.location_state]
        q = q.filter(func.lower(Listing.location_state).in_(states_lower))

    # Range filters
    if filters.year_min:
        q = q.filter(Listing.year >= filters.year_min)
    if filters.year_max:
        q = q.filter(Listing.year <= filters.year_max)
    if filters.price_min is not None:
        q = q.filter(Listing.price >= filters.price_min)
    if filters.price_max is not None:
        q = q.filter(Listing.price <= filters.price_max)
    if filters.mileage_max is not None:
        q = q.filter(Listing.mileage <= filters.mileage_max)

    # Deal score filter — requires join
    if filters.min_deal_score is not None:
        q = q.join(DealScore).filter(DealScore.score >= filters.min_deal_score)

    # Sorting
    sort = filters.sort
    if sort == "price_asc":
        q = q.order_by(Listing.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Listing.price.desc())
    elif sort == "listed_at_desc":
        q = q.order_by(Listing.listed_at.desc().nullsfirst())
    else:  # score_desc (default)
        if filters.min_deal_score is None:
            q = q.join(DealScore, isouter=True)
        q = q.order_by(DealScore.score.desc().nullslast())

    total = q.count()
    items = q.offset((filters.page - 1) * filters.limit).limit(filters.limit).all()

    result = ListingsResponse(data=items, total=total, page=filters.page, limit=filters.limit)
    result_dict = result.model_dump(mode="json")
    cache_set(cache_key, result_dict, ttl=SEARCH_TTL)
    return result
