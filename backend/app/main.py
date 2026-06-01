from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from app.routers import health, listings, makes, trends, search, valuations, jobs
from app.logging_config import setup_logging
import logging
import time

logger = logging.getLogger(__name__)
setup_logging()


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"
        return response
    

app = FastAPI(
    title="LuxeMarket Intelligence API",
    description="""
## Market Intelligence for Luxury Vehicles

A REST API providing deal scoring, valuation modeling, and market trend analytics
for luxury vehicle listings.

### Features
- **Deal Scoring** — Each listing is scored 0–100 vs estimated market value
- **Valuation Model** — Ridge regression trained on comparable listings (R² 0.947)
- **Market Trends** — Aggregated snapshots by make and model
- **Full-text Search** — Search across make, model, description, and location

### Data
Currently powered by 1,500 seeded luxury vehicle listings across 12 makes.
The ingestion pipeline is designed to accept real data sources.
    """,
    version="0.2.0",
    contact={
        "name": "LuxeMarket",
        "url": "https://github.com/avafaei-dev/luxemarket",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "listings", "description": "Browse and filter vehicle listings"},
        {"name": "search", "description": "Full-text and faceted search"},
        {"name": "valuations", "description": "Market valuation details per listing"},
        {"name": "makes", "description": "Available makes and models"},
        {"name": "trends", "description": "Market trend snapshots and summary stats"},
        {"name": "jobs", "description": "Background job management"},
        {"name": "health", "description": "Service health and liveness"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(request.url)},
    )

app.include_router(health.router)
app.include_router(listings.router)
app.include_router(makes.router)
app.include_router(trends.router)
app.include_router(search.router)
app.include_router(valuations.router)
app.include_router(jobs.router)
app.add_middleware(TimingMiddleware)


@app.get("/")
def root():
    return {"name": "LuxeMarket Intelligence API", "version": "0.2.0", "docs": "/docs"}
