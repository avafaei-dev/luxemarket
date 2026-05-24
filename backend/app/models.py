import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean,
    Text, DateTime, Date, ForeignKey, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (
        Index("ix_listings_make_model_year", "make", "model", "year"),
        Index("ix_listings_price", "price"),
        Index("ix_listings_listed_at", "listed_at"),
        Index("ix_listings_is_active", "is_active"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False, default="mock")
    external_id = Column(String(255), nullable=True)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    trim = Column(String(100), nullable=True)
    year = Column(Integer, nullable=False)
    mileage = Column(Integer, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    location_city = Column(String(100), nullable=True)
    location_state = Column(String(50), nullable=True)
    location_country = Column(String(50), default="US")
    color_exterior = Column(String(50), nullable=True)
    color_interior = Column(String(50), nullable=True)
    vin = Column(String(17), nullable=True)
    condition = Column(String(20), nullable=True)   # new, used, cpo
    body_style = Column(String(50), nullable=True)
    transmission = Column(String(50), nullable=True)
    fuel_type = Column(String(50), nullable=True)
    images = Column(JSON, nullable=True)            # list of URL strings
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    listed_at = Column(DateTime(timezone=True), nullable=True)
    ingested_at = Column(DateTime(timezone=True), default=utcnow)
    is_active = Column(Boolean, default=True)

    valuation = relationship("Valuation", back_populates="listing", uselist=False)
    deal_score = relationship("DealScore", back_populates="listing", uselist=False)


class Valuation(Base):
    __tablename__ = "valuations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    estimated_value = Column(Numeric(12, 2), nullable=True)
    confidence = Column(Numeric(4, 3), nullable=True)   # 0.0–1.0
    comp_count = Column(Integer, nullable=True)
    method = Column(String(50), default="ridge_regression")
    model_version = Column(String(50), nullable=True)
    computed_at = Column(DateTime(timezone=True), default=utcnow)

    listing = relationship("Listing", back_populates="valuation")


class DealScore(Base):
    __tablename__ = "deal_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    score = Column(Numeric(5, 2), nullable=True)        # 0–100, higher = better deal
    discount_pct = Column(Numeric(6, 3), nullable=True) # negative = overpriced
    price_delta = Column(Numeric(12, 2), nullable=True) # price - estimated_value
    computed_at = Column(DateTime(timezone=True), default=utcnow)

    listing = relationship("Listing", back_populates="deal_score")


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    snapshot_date = Column(Date, nullable=False)
    avg_price = Column(Numeric(12, 2), nullable=True)
    median_price = Column(Numeric(12, 2), nullable=True)
    listing_count = Column(Integer, nullable=True)
    avg_mileage = Column(Integer, nullable=True)
    avg_deal_score = Column(Numeric(5, 2), nullable=True)


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    filters = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)