"""
Seed script — generates realistic luxury vehicle listings.

Usage:
    python data/seeds/seed.py                  # seeds 1500 listings
    python data/seeds/seed.py --count 500      # seeds 500 listings
    python data/seeds/seed.py --reset          # truncates + re-seeds
    python data/seeds/seed.py --count 100 --reset
"""

import sys
import os
import uuid
import random
import argparse
from datetime import datetime, timedelta, timezone

# Add backend/ to path so can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from faker import Faker
from sqlalchemy import text
from app.database import SessionLocal
from app.models import Listing

fake = Faker()
Faker.seed(42)
random.seed(42)

# ── Luxury makes and models ───────────────────────────────────────────────────

MAKES = {
    "BMW": {
        "models": ["M3 Competition", "M5 Competition", "M8 Gran Coupe", "X5 M Competition", "7 Series", "i7"],
        "base_price": 68000,
        "price_spread": 0.4,
    },
    "Mercedes-Benz": {
        "models": ["S-Class", "AMG GT 63", "GLE 63 AMG", "G-Class", "EQS 580", "SL 55 AMG"],
        "base_price": 85000,
        "price_spread": 0.45,
    },
    "Porsche": {
        "models": ["911 Carrera S", "911 Turbo S", "Cayenne Turbo", "Panamera Turbo S", "Taycan Turbo S"],
        "base_price": 105000,
        "price_spread": 0.5,
    },
    "Audi": {
        "models": ["RS7 Sportback", "RS6 Avant", "R8 V10", "Q8 e-tron", "S8", "A8 L"],
        "base_price": 72000,
        "price_spread": 0.38,
    },
    "Bentley": {
        "models": ["Continental GT", "Bentayga", "Flying Spur", "Mulliner"],
        "base_price": 210000,
        "price_spread": 0.35,
    },
    "Rolls-Royce": {
        "models": ["Ghost", "Cullinan", "Spectre", "Phantom"],
        "base_price": 350000,
        "price_spread": 0.4,
    },
    "Lamborghini": {
        "models": ["Huracan Tecnica", "Urus Performante", "Revuelto"],
        "base_price": 260000,
        "price_spread": 0.5,
    },
    "Ferrari": {
        "models": ["Roma", "296 GTB", "SF90 Stradale", "Purosangue", "812 Superfast"],
        "base_price": 280000,
        "price_spread": 0.55,
    },
    "McLaren": {
        "models": ["720S", "Artura", "GT", "765LT"],
        "base_price": 220000,
        "price_spread": 0.45,
    },
    "Aston Martin": {
        "models": ["DB12", "Vantage", "DBX707", "DBS 770 Ultimate"],
        "base_price": 195000,
        "price_spread": 0.4,
    },
    "Maserati": {
        "models": ["Ghibli Trofeo", "Quattroporte", "Grecale Trofeo", "GranTurismo"],
        "base_price": 100000,
        "price_spread": 0.38,
    },
    "Lexus": {
        "models": ["LC 500", "LX 600", "LS 500h", "RX 500h F Sport"],
        "base_price": 78000,
        "price_spread": 0.3,
    },
}

# ── US cities ─────────────────────────────────────────────────────────────────

CITIES = [
    ("Beverly Hills", "CA"), ("Miami", "FL"), ("New York", "NY"),
    ("Greenwich", "CT"), ("Scottsdale", "AZ"), ("Dallas", "TX"),
    ("Houston", "TX"), ("Chicago", "IL"), ("Atlanta", "GA"),
    ("Las Vegas", "NV"), ("Newport Beach", "CA"), ("San Francisco", "CA"),
    ("Seattle", "WA"), ("Boston", "MA"), ("Denver", "CO"),
    ("Naples", "FL"), ("Palm Beach", "FL"), ("Austin", "TX"),
    ("Nashville", "TN"), ("Charlotte", "NC"), ("Phoenix", "AZ"),
    ("San Diego", "CA"), ("Portland", "OR"), ("Minneapolis", "MN"),
    ("Detroit", "MI"), ("Pittsburgh", "PA"), ("Raleigh", "NC"),
    ("Salt Lake City", "UT"), ("Kansas City", "MO"), ("Tampa", "FL"),
]

# ── Supporting data ───────────────────────────────────────────────────────────

EXTERIOR_COLORS = [
    "Midnight Black", "Arctic White", "Frozen Silver", "Deep Blue Metallic",
    "Nardo Grey", "San Marino Blue", "Rosso Corsa", "British Racing Green",
    "Cognac Brown", "Champagne Gold", "Graphite Metallic", "Pearl White",
]

INTERIOR_COLORS = [
    "Black Leather", "Ivory Leather", "Cognac Leather", "Navy Blue Leather",
    "Red Leather", "Beige Leather", "Dark Brown Leather", "Grey Leather",
]

BODY_STYLES = {
    "sedan": ["S-Class", "7 Series", "A8 L", "Flying Spur", "Ghost", "Phantom",
              "Panamera Turbo S", "Taycan Turbo S", "Quattroporte", "Ghibli Trofeo", "LS 500h"],
    "coupe": ["911 Carrera S", "911 Turbo S", "M3 Competition", "M8 Gran Coupe",
              "Continental GT", "DB12", "Vantage", "720S", "Artura", "GT", "765LT",
              "Roma", "296 GTB", "SF90 Stradale", "812 Superfast", "Huracan Tecnica",
              "Revuelto", "AMG GT 63", "RS7 Sportback", "DBS 770 Ultimate", "LC 500",
              "GranTurismo", "Spectre", "Mulliner", "SL 55 AMG", "R8 V10"],
    "suv": ["X5 M Competition", "GLE 63 AMG", "G-Class", "Cayenne Turbo", "Bentayga",
            "Cullinan", "Urus Performante", "Purosangue", "DBX707", "Q8 e-tron",
            "Grecale Trofeo", "LX 600", "RX 500h F Sport"],
    "wagon": ["RS6 Avant"],
    "convertible": [],
}

MODEL_TO_BODY = {}
for style, models in BODY_STYLES.items():
    for m in models:
        MODEL_TO_BODY[m] = style


TRANSMISSIONS = ["8-speed automatic", "7-speed PDK", "8-speed DCT", "9-speed automatic"]
FUEL_TYPES = ["Gasoline", "Gasoline", "Gasoline", "Hybrid", "Electric"]  # weighted

# Unsplash placeholder images — use consistent car-category images
PLACEHOLDER_IMAGES = [
    "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800",
    "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800",
    "https://images.unsplash.com/photo-1616422285623-13ff0162193c?w=800",
    "https://images.unsplash.com/photo-1571607388263-1044f9ea01dd?w=800",
    "https://images.unsplash.com/photo-1606016159991-dfe4f2746ad5?w=800",
    "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800",
    "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800",
]


# ── Builder ───────────────────────────────────────────────────────────────────

def make_listing() -> dict:
    make_name = random.choice(list(MAKES.keys()))
    cfg = MAKES[make_name]
    model_name = random.choice(cfg["models"])

    year = random.randint(2018, 2024)
    condition = random.choices(
        ["new", "used", "cpo"],
        weights=[10, 72, 18],
    )[0]

    # Price logic: newer = more expensive, some random variance
    year_factor = 1 + (year - 2018) * 0.035
    condition_factor = {"new": 1.0, "cpo": 0.88, "used": 0.78}[condition]
    spread = cfg["price_spread"]
    noise = random.uniform(1 - spread / 2, 1 + spread / 2)
    price = cfg["base_price"] * year_factor * condition_factor * noise

    # Mileage by condition
    if condition == "new":
        mileage = random.randint(0, 800)
    elif condition == "cpo":
        mileage = random.randint(8000, 45000)
    else:
        mileage = random.randint(5000, 90000)

    city, state = random.choice(CITIES)

    # Listed sometime in the last 180 days
    listed_at = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, 180),
        hours=random.randint(0, 23),
    )

    body_style = MODEL_TO_BODY.get(model_name, "sedan")
    fuel_type = random.choice(FUEL_TYPES)

    images = random.sample(PLACEHOLDER_IMAGES, k=random.randint(2, 4))

    description = (
        f"{year} {make_name} {model_name} in excellent {condition} condition. "
        f"Located in {city}, {state}. "
        f"{mileage:,} miles. "
        f"Exterior: {random.choice(EXTERIOR_COLORS)}. "
        f"Interior: {random.choice(INTERIOR_COLORS)}. "
        f"{random.choice(TRANSMISSIONS)} transmission. "
        f"This vehicle has been meticulously maintained and is ready for its next owner."
    )

    return {
        "id": str(uuid.uuid4()),
        "source": "mock",
        "external_id": f"mock-{uuid.uuid4().hex[:8]}",
        "make": make_name,
        "model": model_name,
        "trim": None,
        "year": year,
        "mileage": mileage,
        "price": round(price, 2),
        "currency": "USD",
        "location_city": city,
        "location_state": state,
        "location_country": "US",
        "color_exterior": random.choice(EXTERIOR_COLORS),
        "color_interior": random.choice(INTERIOR_COLORS),
        "vin": None,
        "condition": condition,
        "body_style": body_style,
        "transmission": random.choice(TRANSMISSIONS),
        "fuel_type": fuel_type,
        "images": images,
        "description": description,
        "url": f"https://mock.luxemarket.com/listings/{uuid.uuid4().hex[:8]}",
        "listed_at": listed_at,
        "ingested_at": datetime.now(timezone.utc),
        "is_active": True,
    }


# ── Runner ────────────────────────────────────────────────────────────────────

def run(count: int = 1500, reset: bool = False):
    db = SessionLocal()
    try:
        if reset:
            print("Resetting listings table...")
            db.execute(text("TRUNCATE TABLE deal_scores, valuations, listings RESTART IDENTITY CASCADE"))
            db.commit()
            print("Done.")

        print(f"Generating {count} listings...")
        batch = [make_listing() for _ in range(count)]

        db.bulk_insert_mappings(Listing, batch)
        db.commit()

        total = db.query(Listing).count()
        print(f"✓ Seeded {count} listings. Total in DB: {total}")

        # Print a quick distribution summary
        from sqlalchemy import func
        rows = (
            db.query(Listing.make, func.count(Listing.id))
            .group_by(Listing.make)
            .order_by(func.count(Listing.id).desc())
            .all()
        )
        print("\nMake distribution:")
        for make_name, cnt in rows:
            print(f"  {make_name:<20} {cnt}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed luxury vehicle listings")
    parser.add_argument("--count", type=int, default=1500, help="Number of listings to generate")
    parser.add_argument("--reset", action="store_true", help="Truncate existing data before seeding")
    args = parser.parse_args()

    run(count=args.count, reset=args.reset)