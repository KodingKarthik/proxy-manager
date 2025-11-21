"""SQLModel engine and session setup."""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from .utils.config import settings

# Import all models to ensure they're registered with SQLModel
from .models import User, Proxy, ActivityLog, Blacklist, ApiKey  # noqa: F401

# Create database engine
engine = create_engine(
    settings.db_url,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL query logging
)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    with Session(engine) as session:
        yield session

