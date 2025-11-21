"""Shared pytest fixtures for proxy_manager tests."""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from proxy_manager.__main__ import app
from proxy_manager.database import get_session
from proxy_manager import database as db_module
# Import all models to ensure they're registered with SQLModel.metadata
from proxy_manager.models import User, UserRole, ApiKey, Blacklist, Proxy, ActivityLog  # noqa: F401


@pytest.fixture(scope="module")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    
    # Patch global engine to ensure all code uses test DB
    original_engine = db_module.engine
    db_module.engine = engine
    
    yield engine
    
    # Cleanup
    db_module.engine = original_engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a fresh database session for each test function."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def test_client(test_engine):
    """Create a test client with overridden database dependencies."""
    from proxy_manager import scheduler
    
    # Override create_db_and_tables to do nothing (tables already created)
    original_create_db = db_module.create_db_and_tables
    original_scheduler_start = scheduler.health_check_scheduler.start
    original_scheduler_stop = scheduler.health_check_scheduler.stop
    
    # Mock scheduler to prevent it from running during tests
    scheduler.health_check_scheduler.start = lambda: None
    scheduler.health_check_scheduler.stop = lambda wait=True: None
    db_module.create_db_and_tables = lambda: None
    
    # Override get_session to use test engine
    def get_test_session():
        with Session(test_engine) as session:
            yield session
    
    app.dependency_overrides[get_session] = get_test_session
    
    # Create client - this will trigger lifespan but our mocks will prevent issues
    client = TestClient(app, raise_server_exceptions=True)
    
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()
    db_module.create_db_and_tables = original_create_db
    scheduler.health_check_scheduler.start = original_scheduler_start
    scheduler.health_check_scheduler.stop = original_scheduler_stop


@pytest.fixture(scope="module")
async def async_test_client(test_engine):
    """Create an async test client with overridden database dependencies.
    
    This uses httpx.AsyncClient which properly handles database session overrides
    with FastAPI lifespan events, unlike TestClient.
    """
    import httpx
    from httpx import ASGITransport
    from proxy_manager import scheduler
    
    # Override create_db_and_tables to do nothing (tables already created)
    original_create_db = db_module.create_db_and_tables
    original_scheduler_start = scheduler.health_check_scheduler.start
    original_scheduler_stop = scheduler.health_check_scheduler.stop
    
    # Mock scheduler to prevent it from running during tests
    scheduler.health_check_scheduler.start = lambda: None
    scheduler.health_check_scheduler.stop = lambda wait=True: None
    db_module.create_db_and_tables = lambda: None
    
    # Override get_session to use test engine
    def get_test_session():
        with Session(test_engine) as session:
            yield session
    
    app.dependency_overrides[get_session] = get_test_session
    
    # Create async client with ASGI transport
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client
    
    # Cleanup
    app.dependency_overrides.clear()
    db_module.create_db_and_tables = original_create_db
    scheduler.health_check_scheduler.start = original_scheduler_start
    scheduler.health_check_scheduler.stop = original_scheduler_stop


# Sample data fixtures
@pytest.fixture
def sample_proxy_response():
    """Sample proxy response data for tests."""
    return {
        "id": 42,
        "ip": "1.2.3.4",
        "port": 8080,
        "protocol": "http",
        "username": None,
        "password": None,
        "is_working": True,
        "address": "1.2.3.4:8080",
    }


@pytest.fixture
def sample_blacklist_response():
    """Sample blacklist response data for tests."""
    return [
        {
            "id": 1,
            "pattern": "^.*facebook\\.com.*$",
            "description": "Block Facebook",
            "created_at": "2024-01-01T00:00:00",
            "created_by": 1,
        },
        {
            "id": 2,
            "pattern": "^.*twitter\\.com.*$",
            "description": "Block Twitter",
            "created_at": "2024-01-01T00:00:00",
            "created_by": 1,
        },
    ]
