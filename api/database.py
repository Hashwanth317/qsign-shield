"""SQLAlchemy database configuration for Q-Sign Shield authentication."""

from __future__ import annotations

import os
from collections.abc import Generator

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv


DATABASE_UNAVAILABLE_MESSAGE = "Authentication database is unavailable."
load_dotenv()


class Base(DeclarativeBase):
    """Base class shared by persistent SQLAlchemy models."""


def normalize_database_url(database_url: str) -> str:
    """Use psycopg 3 for Render/Neon PostgreSQL connection strings."""
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def _create_database_engine() -> Engine | None:
    raw_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_url:
        return None

    database_url = normalize_database_url(raw_url)
    if database_url.startswith("sqlite"):
        options: dict[str, object] = {
            "connect_args": {"check_same_thread": False},
        }
        if database_url.endswith(":memory:"):
            options["poolclass"] = StaticPool
        return create_engine(database_url, **options)

    return create_engine(database_url, pool_pre_ping=True, pool_recycle=300)


engine = _create_database_engine()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
if engine is not None:
    SessionLocal.configure(bind=engine)


def init_db() -> None:
    """Create prototype tables after all model metadata has been imported."""
    if engine is None:
        raise RuntimeError("DATABASE_URL is not configured.")

    # Import registers the model with Base.metadata without creating a cycle.
    from api import user_models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Provide a request-scoped database session with safe error handling."""
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_UNAVAILABLE_MESSAGE,
        )

    database = SessionLocal()
    try:
        yield database
    except SQLAlchemyError as error:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_UNAVAILABLE_MESSAGE,
        ) from error
    finally:
        database.close()
