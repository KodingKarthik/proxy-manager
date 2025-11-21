import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from fastapi import HTTPException

from proxy_manager.models import User, UserRole, ApiKey
from proxy_manager.auth import get_password_hash, verify_password, get_api_key_user

@pytest.fixture
def auth_session():
    """Create an in-memory database session for auth tests."""
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args=connect_args,
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def service_user(auth_session):
    """Create a service user for testing."""
    user = User(
        username="mitm-forwarder",
        email="forwarder@internal",
        hashed_password=get_password_hash("unused"),
        role=UserRole.SERVICE,
        is_active=True
    )
    auth_session.add(user)
    auth_session.commit()
    auth_session.refresh(user)
    return user

def test_create_api_key(auth_session, service_user):
    """Test creating an API key model."""
    raw_key = "secret_key_123"
    key_hash = get_password_hash(raw_key)
    
    api_key = ApiKey(
        key_hash=key_hash,
        prefix=raw_key[:8],
        name="Test Key",
        user_id=service_user.id
    )
    auth_session.add(api_key)
    auth_session.commit()
    
    stored_key = auth_session.exec(select(ApiKey).where(ApiKey.name == "Test Key")).first()
    assert stored_key is not None
    assert stored_key.prefix == "secret_k"
    assert verify_password(raw_key, stored_key.key_hash)

@pytest.mark.asyncio
async def test_authenticate_api_key(auth_session, service_user):
    """Test authenticating with a valid API key."""
    # Create key
    raw_key = "valid_prefix.secret_part"
    api_key = ApiKey(
        key_hash=get_password_hash(raw_key),
        prefix=raw_key.split(".")[0],
        name="Auth Key",
        user_id=service_user.id
    )
    auth_session.add(api_key)
    auth_session.commit()

    # Test valid auth
    user = await get_api_key_user(api_key=raw_key, session=auth_session)
    assert user is not None
    assert user.id == service_user.id
    assert user.role == UserRole.SERVICE

@pytest.mark.asyncio
async def test_authenticate_invalid_key(auth_session, service_user):
    """Test authenticating with an invalid API key."""
    # Create key
    raw_key = "real_key_789"
    api_key = ApiKey(
        key_hash=get_password_hash(raw_key),
        prefix=raw_key[:8],
        name="Real Key",
        user_id=service_user.id
    )
    auth_session.add(api_key)
    auth_session.commit()

    # Test invalid key
    user = await get_api_key_user(api_key="wrong_key_000", session=auth_session)
    assert user is None

@pytest.mark.asyncio
async def test_authenticate_expired_key(auth_session, service_user):
    """Test authenticating with an expired API key."""
    raw_key = "expired_key"
    api_key = ApiKey(
        key_hash=get_password_hash(raw_key),
        prefix=raw_key[:8],
        name="Expired Key",
        user_id=service_user.id,
        expires_at=datetime.now() - timedelta(days=1)
    )
    auth_session.add(api_key)
    auth_session.commit()

    user = await get_api_key_user(api_key=raw_key, session=auth_session)
    assert user is None
