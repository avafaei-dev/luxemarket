from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/api/v1", tags=["trends"])


@router.get("/trends")
def get_trends(
    make: str | None = Query(None),
    model: str | None = Query(None),
    db: Session = Depends(get_db),
):
    # Full implementation Day 6 after market_snapshots are populated
    return {"data": [], "message": "trends endpoint — populated after valuation job runs"}


@router.get("/trends/summary")
def get_trends_summary(db: Session = Depends(get_db)):
    from sqlalchemy import func
    from app.models import Listing, DealScore

    total = db.query(func.count(Listing.id)).filter(Listing.is_active == True).scalar()
    avg_price = db.query(func.avg(Listing.price)).filter(Listing.is_active == True).scalar()
    avg_score = db.query(func.avg(DealScore.score)).scalar()

    return {
        "total_listings": total or 0,
        "avg_price": round(float(avg_price), 2) if avg_price else 0,
        "avg_deal_score": round(float(avg_score), 1) if avg_score else 0,
    }