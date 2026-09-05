"""FastAPI application entry point for Q-Sign Shield."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from api.auth_routes import router as auth_router
from api.database import init_db
from api.models import HealthResponse, RootResponse
from api.routes import router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize persistent tables without exposing connection details."""
    try:
        init_db()
    except (RuntimeError, SQLAlchemyError):
        logger.error("Authentication database initialization failed.")
    yield


app = FastAPI(
    title="Q-Sign Shield API",
    description=(
        "Quantum-inspired digital signature and multi-attack security "
        "verification simulator with educational channel forensics for "
        "SIH26141."
    ),
    version="0.6",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://qsign-shield.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", response_model=RootResponse, tags=["System"])
def project_info() -> RootResponse:
    """Return basic API identity and runtime status."""
    return RootResponse(project="Q-Sign Shield", version="0.6", status="running")


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    """Return a lightweight health response."""
    return HealthResponse(status="healthy")


app.include_router(auth_router)
app.include_router(router)
