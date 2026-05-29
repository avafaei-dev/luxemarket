from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Valuation
from app.schemas import ValuationDetail

router = APIRouter(prefix="/api/v1", tags=["valuations"])


@router.get("/valuations/{listing_id}", response_model=ValuationDetail)
def get_valuation(listing_id: str, db: Session = Depends(get_db)):
    valuation = (
        db.query(Valuation)
        .options(joinedload(Valuation.listing))
        .filter(Valuation.listing_id == listing_id)
        .first()
    )
    if not valuation:
        raise HTTPException(status_code=404, detail="Valuation not found for this listing")
    return valuation