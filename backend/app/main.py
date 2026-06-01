from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from app.routers import health, listings, makes, trends, search, valuations, jobs
from app.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)
setup_logging()


app = FastAPI(
    title="LuxeMarket Intelligence API",
    description="Market intelligence platform for luxury vehicles",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.get("/")
def root():
    return {"name": "LuxeMarket Intelligence API", "version": "0.2.0", "docs": "/docs"}
