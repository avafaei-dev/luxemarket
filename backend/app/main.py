from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, listings, makes, trends

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

app.include_router(health.router)
app.include_router(listings.router)
app.include_router(makes.router)
app.include_router(trends.router)


@app.get("/")
def root():
    return {"name": "LuxeMarket Intelligence API", "docs": "/docs"}