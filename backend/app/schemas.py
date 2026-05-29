from __future__ import annotations
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict


# ── Valuation ────────────────────────────────────────────────────────────────

class ValuationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    estimated_value: Decimal | None
    confidence: Decimal | None
    comp_count: int | None
    method: str | None
    computed_at: datetime | None


# ── Deal Score ────────────────────────────────────────────────────────────────

class DealScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    score: Decimal | None
    discount_pct: Decimal | None
    price_delta: Decimal | None
    computed_at: datetime | None


# ── Listing ───────────────────────────────────────────────────────────────────

class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: str
    make: str
    model: str
    trim: str | None
    year: int
    mileage: int | None
    price: Decimal
    currency: str
    location_city: str | None
    location_state: str | None
    location_country: str | None
    color_exterior: str | None
    color_interior: str | None
    condition: str | None
    body_style: str | None
    transmission: str | None
    fuel_type: str | None
    images: list[str] | None
    description: str | None
    url: str | None
    listed_at: datetime | None
    ingested_at: datetime | None
    is_active: bool

    valuation: ValuationOut | None = None
    deal_score: DealScoreOut | None = None


class ListingBrief(BaseModel):
    """Lightweight version for list views — no heavy text fields."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    make: str
    model: str
    trim: str | None
    year: int
    mileage: int | None
    price: Decimal
    location_city: str | None
    location_state: str | None
    condition: str | None
    images: list[str] | None
    listed_at: datetime | None
    deal_score: DealScoreOut | None = None
    valuation: ValuationOut | None = None


class ListingsResponse(BaseModel):
    data: list[ListingBrief]
    total: int
    page: int
    limit: int


# ── Makes ─────────────────────────────────────────────────────────────────────

class MakeCount(BaseModel):
    make: str
    count: int


class ModelCount(BaseModel):
    model: str
    count: int


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    db: str
    redis: str
    environment: str


# ── Search ────────────────────────────────────────────────────────────────────

class SearchFilters(BaseModel):
    """Body payload for POST /listings/search"""
    query: str | None = None          # free-text search against make, model, description
    make: list[str] | None = None     # e.g. ["BMW", "Porsche"]
    model: list[str] | None = None
    year_min: int | None = None
    year_max: int | None = None
    price_min: float | None = None
    price_max: float | None = None
    mileage_max: int | None = None
    condition: list[str] | None = None   # ["new", "used", "cpo"]
    location_state: list[str] | None = None
    min_deal_score: float | None = None
    sort: str = "score_desc"
    page: int = 1
    limit: int = 20


# ── Valuation detail ──────────────────────────────────────────────────────────

class ValuationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    estimated_value: Decimal | None
    confidence: Decimal | None
    comp_count: int | None
    method: str | None
    model_version: str | None
    computed_at: datetime | None
    listing: ListingBrief | None = None