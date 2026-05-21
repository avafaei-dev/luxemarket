from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Literal
from app.database import get_db
from app.models import Listing, DealScore
from app.schemas import ListingOut, ListingBrief, ListingsResponse

router = APIRouter(prefix="/api/v1", tags=["listings"])


@router.get("/listings", response_model=ListingsResponse)
def get_listings(
    make: str | None = Query(None),
    model: str | None = Query(None),
    year_min: int | None = Query(None, ge=1990),
    year_max: int | None = Query(None, le=2030),
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None),
    mileage_max: int | None = Query(None, ge=0),
    condition: str | None = Query(None, pattern="^(new|used|cpo)$"),
    location_state: str | None = Query(None),
    sort: Literal["price_asc", "price_desc", "score_desc", "listed_at_desc"] = "listed_at_desc",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Listing)
        .options(joinedload(Listing.deal_score), joinedload(Listing.valuation))
        .filter(Listing.is_active == True)
    )

    if make:
        q = q.filter(func.lower(Listing.make) == make.lower())
    if model:
        q = q.filter(func.lower(Listing.model) == model.lower())
    if year_min:
        q = q.filter(Listing.year >= year_min)
    if year_max:
        q = q.filter(Listing.year <= year_max)
    if price_min is not None:
        q = q.filter(Listing.price >= price_min)
    if price_max is not None:
        q = q.filter(Listing.price <= price_max)
    if mileage_max is not None:
        q = q.filter(Listing.mileage <= mileage_max)
    if condition:
        q = q.filter(Listing.condition == condition)
    if location_state:
        q = q.filter(func.lower(Listing.location_state) == location_state.lower())

    # Sorting
    if sort == "price_asc":
        q = q.order_by(Listing.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Listing.price.desc())
    elif sort == "listed_at_desc":
        q = q.order_by(Listing.listed_at.desc().nullsfirst())
    elif sort == "score_desc":
        q = q.join(DealScore, isouter=True).order_by(DealScore.score.desc().nullslast())

    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()

    return ListingsResponse(data=items, total=total, page=page, limit=limit)


@router.get("/listings/top-deals", response_model=ListingsResponse)
def get_top_deals(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Listing)
        .options(joinedload(Listing.deal_score), joinedload(Listing.valuation))
        .join(DealScore)
        .filter(Listing.is_active == True, DealScore.score >= 60)
        .order_by(DealScore.score.desc())
    )
    total = q.count()
    items = q.limit(limit).all()
    return ListingsResponse(data=items, total=total, page=1, limit=limit)


@router.get("/listings/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    listing = (
        db.query(Listing)
        .options(joinedload(Listing.deal_score), joinedload(Listing.valuation))
        .filter(Listing.id == listing_id, Listing.is_active == True)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing