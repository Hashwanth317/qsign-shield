"""FastAPI application entry point for Q-Sign Shield V0.6-V0.8."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api.models import HealthResponse, RootResponse
from api.routes import router


app = FastAPI(
    title="Q-Sign Shield API",
    description=(
        "Quantum-inspired digital signature and multi-attack security "
        "verification simulator with educational channel forensics for "
        "SIH26141."
    ),
    version="0.6",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173","https://qsign-shield.vercel.app",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=RootResponse, tags=["System"])
def project_info() -> RootResponse:
    """Return basic API identity and runtime status."""
    return RootResponse(project="Q-Sign Shield", version="0.6", status="running")


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    """Return a lightweight health response."""
    return HealthResponse(status="healthy")


app.include_router(router)
