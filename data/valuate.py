"""
Valuation + deal scoring pipeline.

Loads all active listings from the DB, trains a Ridge regression model,
writes estimated values to the `valuations` table, and deal scores to
`deal_scores`.

Usage:
    python data/valuate.py
    python data/valuate.py --dry-run   # prints stats without writing to DB
"""

import sys
import os
import argparse
import uuid
import joblib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

from sqlalchemy import text
from app.database import SessionLocal
from app.models import Listing, Valuation, DealScore, MarketSnapshot

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_VERSION = "v1.0"


# ── Load data ─────────────────────────────────────────────────────────────────

def load_listings(db) -> pd.DataFrame:
    rows = db.query(
        Listing.id, Listing.make, Listing.model, Listing.year,
        Listing.mileage, Listing.condition, Listing.price,
        Listing.body_style, Listing.location_state,
    ).filter(Listing.is_active == True).all()

    df = pd.DataFrame(rows, columns=[
        "id", "make", "model", "year", "mileage",
        "condition", "price", "body_style", "location_state",
    ])
    print(f"Loaded {len(df)} listings from DB")
    return df


# ── Preprocessing ─────────────────────────────────────────────────────────────

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["mileage"] = df["mileage"].astype(float)
    df["price"] = df["price"].astype(float)

    # Fill missing mileage with median per condition
    for cond in df["condition"].unique():
        mask = (df["condition"] == cond) & df["mileage"].isna()
        median = df.loc[df["condition"] == cond, "mileage"].median()
        df.loc[mask, "mileage"] = median

    df["mileage"] = df["mileage"].fillna(df["mileage"].median())
    df["condition"] = df["condition"].fillna("used")
    df["body_style"] = df["body_style"].fillna("sedan")
    df["location_state"] = df["location_state"].fillna("CA")

    # Log-transform price and mileage — improves regression on skewed distributions
    df["log_price"] = np.log1p(df["price"])
    df["log_mileage"] = np.log1p(df["mileage"])

    return df


# ── Model ─────────────────────────────────────────────────────────────────────

def build_pipeline() -> Pipeline:
    categorical_features = ["make", "model", "condition", "body_style", "location_state"]
    numerical_features = ["year", "log_mileage"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", "passthrough", numerical_features),
        ],
        remainder="drop",
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", Ridge(alpha=10.0)),
    ])


def train(df: pd.DataFrame) -> tuple[Pipeline, float]:
    pipe = build_pipeline()
    features = ["make", "model", "year", "log_mileage", "condition", "body_style", "location_state"]
    X = df[features]
    y = df["log_price"]

    # Cross-validation R² score
    cv_scores = cross_val_score(pipe, X, y, cv=5, scoring="r2")
    print(f"Cross-val R² scores: {cv_scores.round(3)}")
    print(f"Mean R²: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    pipe.fit(X, y)

    train_r2 = r2_score(y, pipe.predict(X))
    print(f"Train R²: {train_r2:.3f}")

    return pipe, cv_scores.mean()


# ── Score ─────────────────────────────────────────────────────────────────────

def compute_scores(df: pd.DataFrame, pipe: Pipeline) -> pd.DataFrame:
    features = ["make", "model", "year", "log_mileage", "condition", "body_style", "location_state"]
    X = df[features]

    log_pred = pipe.predict(X)
    df = df.copy()
    df["estimated_value"] = np.expm1(log_pred).round(2)

    # discount_pct: positive = underpriced (good deal), negative = overpriced
    df["discount_pct"] = (
        (df["estimated_value"] - df["price"]) / df["estimated_value"] * 100
    ).round(3)

    # Score: 0–100
    # 100 = 20%+ below market (great deal)
    # 50  = at market value
    # 0   = 20%+ above market (bad deal)
    df["score"] = (
        (df["discount_pct"] + 20) / 40 * 100
    ).clip(0, 100).round(2)

    df["price_delta"] = (df["price"] - df["estimated_value"]).round(2)

    return df


# ── Write to DB ───────────────────────────────────────────────────────────────

def write_results(db, df: pd.DataFrame, model_r2: float, dry_run: bool = False):
    now = datetime.now(timezone.utc)

    if dry_run:
        print("\n[DRY RUN] Would write:")
        print(df[["make", "model", "price", "estimated_value", "discount_pct", "score"]].head(10))
        return

    # Clear existing valuations + scores
    print("Clearing existing valuations and deal scores...")
    db.execute(text("DELETE FROM deal_scores"))
    db.execute(text("DELETE FROM valuations"))
    db.commit()

    # Build bulk insert lists
    valuations = []
    deal_scores = []

    comp_count = len(df) // 12  # approx comps per make

    for _, row in df.iterrows():
        lid = str(row["id"])
        valuations.append({
            "id": str(uuid.uuid4()),
            "listing_id": lid,
            "estimated_value": float(row["estimated_value"]),
            "confidence": float(round(min(model_r2, 0.99), 3)),
            "comp_count": comp_count,
            "method": "ridge_regression",
            "model_version": MODEL_VERSION,
            "computed_at": now,
        })
        deal_scores.append({
            "id": str(uuid.uuid4()),
            "listing_id": lid,
            "score": float(row["score"]),
            "discount_pct": float(row["discount_pct"]),
            "price_delta": float(row["price_delta"]),
            "computed_at": now,
        })

    print(f"Writing {len(valuations)} valuations...")
    db.bulk_insert_mappings(Valuation, valuations)

    print(f"Writing {len(deal_scores)} deal scores...")
    db.bulk_insert_mappings(DealScore, deal_scores)

    db.commit()
    print("Done writing valuations and deal scores.")


def write_market_snapshots(db, df: pd.DataFrame, dry_run: bool = False):
    """Aggregate market snapshots per make/model for the trends endpoint."""
    from datetime import date

    today = date.today()

    if not dry_run:
        db.execute(text("DELETE FROM market_snapshots"))

    snapshots = []
    for (make, model), group in df.groupby(["make", "model"]):
        scores = group["score"].dropna()
        snapshots.append({
            "id": str(uuid.uuid4()),
            "make": make,
            "model": model,
            "year": None,
            "snapshot_date": today,
            "avg_price": round(float(group["price"].mean()), 2),
            "median_price": round(float(group["price"].median()), 2),
            "listing_count": len(group),
            "avg_mileage": int(group["mileage"].mean()) if not group["mileage"].isna().all() else None,
            "avg_deal_score": round(float(scores.mean()), 2) if len(scores) > 0 else None,
        })

    if dry_run:
        print(f"\n[DRY RUN] Would write {len(snapshots)} market snapshots")
        return

    db.bulk_insert_mappings(MarketSnapshot, snapshots)
    db.commit()
    print(f"Wrote {len(snapshots)} market snapshots.")


# ── Main ──────────────────────────────────────────────────────────────────────

def run(dry_run: bool = False):
    db = SessionLocal()
    try:
        df = load_listings(db)
        df = clean(df)
        

        print("\nTraining valuation model...")
        pipe, r2 = train(df)

        print("\nComputing deal scores...")
        df = compute_scores(df, pipe)

        # Stats
        print(f"\nDeal score distribution:")
        print(f"  Mean score:   {df['score'].mean():.1f}")
        print(f"  Median score: {df['score'].median():.1f}")
        print(f"  Great deals (score > 70): {(df['score'] > 70).sum()}")
        print(f"  Fair deals  (score 40-70): {((df['score'] >= 40) & (df['score'] <= 70)).sum()}")
        print(f"  Overpriced  (score < 40): {(df['score'] < 40).sum()}")

        print(f"\nTop 5 deals by score:")
        top = df.nlargest(5, "score")[["make", "model", "year", "price", "estimated_value", "score"]]
        print(top.to_string(index=False))

        write_results(db, df, r2, dry_run=dry_run)
        write_market_snapshots(db, df, dry_run=dry_run)

        if not dry_run:
            # Save model artifact
            model_path = MODEL_DIR / "valuation_model.joblib"
            joblib.dump(pipe, model_path)
            print(f"\nModel saved to {model_path}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run valuation and deal scoring pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Print stats without writing to DB")
    args = parser.parse_args()

    run(dry_run=args.dry_run)