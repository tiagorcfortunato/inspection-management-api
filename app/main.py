"""
app.main — FastAPI Application Entry Point

Creates and configures the FastAPI application instance:
- CORS middleware (origins from environment config)
- Rate limiting via SlowAPI
- Router registration (auth, inspections, users, admin)
- Health check and root redirect to Swagger docs

This is the file that Uvicorn loads: `uvicorn app.main:app`
"""

import logging

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.routers import auth, inspections, users, admin


app = FastAPI(
    title="Inspection Management API",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(inspections.router)
app.include_router(users.router)
app.include_router(admin.router)