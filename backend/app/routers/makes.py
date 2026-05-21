from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Listing
from app.schemas import MakeCount, ModelCount

router = APIRouter(prefix="/api/v1", tags=["makes"])


@router.get("/makes", response_model=list[MakeCount])
def get_makes(db: Session = Depends(get_db)):
    rows = (
        db.query(Listing.make, func.count(Listing.id).label("count"))
        .filter(Listing.is_active == True)
        .group_by(Listing.make)
        .order_by(func.count(Listing.id).desc())
        .all()
    )
    return [MakeCount(make=r.make, count=r.count) for r in rows]


@router.get("/makes/{make}/models", response_model=list[ModelCount])
def get_models_for_make(make: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Listing.model, func.count(Listing.id).label("count"))
        .filter(
            func.lower(Listing.make) == make.lower(),
            Listing.is_active == True
        )
        .group_by(Listing.model)
        .order_by(func.count(Listing.id).desc())
        .all()
    )
    return [ModelCount(model=r.model, count=r.count) for r in rows]