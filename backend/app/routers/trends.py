from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Listing, DealScore, MarketSnapshot

router = APIRouter(prefix="/api/v1", tags=["trends"])


@router.get("/trends")
def get_trends(
    make: str | None = Query(None),
    model: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(MarketSnapshot)
    if make:
        q = q.filter(func.lower(MarketSnapshot.make) == make.lower())
    if model:
        q = q.filter(func.lower(MarketSnapshot.model) == model.lower())

    rows = q.order_by(MarketSnapshot.make, MarketSnapshot.model).all()

    data = [
        {
            "make": r.make,
            "model": r.model,
            "snapshot_date": r.snapshot_date.isoformat() if r.snapshot_date else None,
            "avg_price": float(r.avg_price) if r.avg_price else None,
            "median_price": float(r.median_price) if r.median_price else None,
            "listing_count": r.listing_count,
            "avg_mileage": r.avg_mileage,
            "avg_deal_score": float(r.avg_deal_score) if r.avg_deal_score else None,
        }
        for r in rows
    ]
    return {"data": data, "total": len(data)}


@router.get("/trends/summary")
def get_trends_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(Listing.id)).filter(Listing.is_active == True).scalar()
    avg_price = db.query(func.avg(Listing.price)).filter(Listing.is_active == True).scalar()
    avg_score = db.query(func.avg(DealScore.score)).scalar()
    top_make = (
        db.query(Listing.make, func.count(Listing.id).label("cnt"))
        .filter(Listing.is_active == True)
        .group_by(Listing.make)
        .order_by(func.count(Listing.id).desc())
        .first()
    )

    return {
        "total_listings": total or 0,
        "avg_price": round(float(avg_price), 2) if avg_price else 0,
        "avg_deal_score": round(float(avg_score), 1) if avg_score else 0,
        "top_make": top_make.make if top_make else None,
    }