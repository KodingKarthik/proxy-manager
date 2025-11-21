"""Integration tests for API Key authentication with FastAPI TestClient."""

import pytest
import secrets
from datetime import datetime, timedelta
from sqlmodel import Session, select

from proxy_manager.models import User, UserRole, ApiKey, Blacklist
from proxy_manager.auth import get_password_hash


@pytest.fixture(scope="function")
def service_user_with_key(test_engine):
    """Create a service user with API key for integration tests."""
    with Session(test_engine) as session:
        # Check/Create service user
        service_user = session.exec(select(User).where(User.username == "test-service")).first()
        if not service_user:
            service_user = User(
                username="test-service",
                email="service@test.com",
                hashed_password=get_password_hash("unused"),
                role=UserRole.SERVICE,
                is_active=True
            )
            session.add(service_user)
        else:
            # Reset state
            service_user.is_active = True
            session.add(service_user)
            
        # Check/Create admin user
        admin_user = session.exec(select(User).where(User.username == "admin")).first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@test.com",
                hashed_password=get_password_hash("adminpass"),
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(admin_user)
        else:
            # Reset state and password
            admin_user.is_active = True
            admin_user.hashed_password = get_password_hash("adminpass")
            session.add(admin_user)
        
        session.commit()
        session.refresh(service_user)
        session.refresh(admin_user)
        
        # Check/Create API key
        raw_key = "testprefix.testsecret123456789"
        api_key = session.exec(select(ApiKey).where(ApiKey.prefix == "testprefix")).first()
        if not api_key:
            api_key = ApiKey(
                key_hash=get_password_hash(raw_key),
                prefix="testprefix",
                name="Test Service Key",
                user_id=service_user.id,
                is_active=True
            )
            session.add(api_key)
        else:
            # Reset state
            api_key.is_active = True
            api_key.expires_at = None
            session.add(api_key)
        
        # Check/Create blacklist rule
        blacklist = session.exec(select(Blacklist).where(Blacklist.pattern == ".*\\.blocked\\.com.*")).first()
        if not blacklist:
            blacklist = Blacklist(
                pattern=".*\\.blocked\\.com.*",
                description="Test blocked domain",
                created_by=admin_user.id
            )
            session.add(blacklist)
        
        session.commit()
        
        # Return data for tests
        return {
            "service_user_id": service_user.id,
            "admin_user_id": admin_user.id,
            "raw_key": raw_key
        }


@pytest.mark.asyncio
async def test_blacklist_with_api_key(async_test_client, service_user_with_key):
    """Test fetching blacklist with valid API key."""
    response = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": service_user_with_key["raw_key"]}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["pattern"] == ".*\\.blocked\\.com.*"


@pytest.mark.asyncio
async def test_blacklist_without_auth(async_test_client):
    """Test blacklist endpoint rejects requests without auth."""
    response = await async_test_client.get("/blacklist")
    
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_blacklist_with_invalid_api_key(async_test_client):
    """Test blacklist endpoint rejects invalid API key."""
    response = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": "invalid.key"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_activity_with_api_key(async_test_client, service_user_with_key):
    """Test posting activity log with API key."""
    activity_data = {
        "user_id": service_user_with_key["service_user_id"],
        "endpoint": "/test",
        "method": "GET",
        "status_code": 200,
        "target_url": "https://example.com"
    }
    
    response = await async_test_client.post(
        "/activity",
        json=activity_data,
        headers={"X-API-Key": service_user_with_key["raw_key"]}
    )
    
    assert response.status_code == 201
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_activity_without_auth(async_test_client):
    """Test activity endpoint rejects requests without auth."""
    activity_data = {
        "user_id": 1,
        "endpoint": "/test",
        "method": "GET",
        "status_code": 200
    }
    
    response = await async_test_client.post("/activity", json=activity_data)
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_mixed_auth_jwt_and_api_key(async_test_client, service_user_with_key):
    """Test that both JWT and API Key work on same endpoint."""
    # First, login to get JWT
    login_response = await async_test_client.post(
        "/auth/login",
        json={"username": "admin", "password": "adminpass"}
    )
    assert login_response.status_code == 200
    jwt_token = login_response.json()["access_token"]
    
    # Test with JWT
    response_jwt = await async_test_client.get(
        "/blacklist",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response_jwt.status_code == 200
    
    # Test with API Key
    response_api = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": service_user_with_key["raw_key"]}
    )
    assert response_api.status_code == 200
    
    # Both should return same data
    assert response_jwt.json() == response_api.json()


@pytest.mark.asyncio
async def test_inactive_api_key_rejected(async_test_client, test_engine, service_user_with_key):
    """Test that inactive API keys are rejected."""
    with Session(test_engine) as session:
        # Deactivate the key
        statement = select(ApiKey).where(ApiKey.prefix == "testprefix")
        api_key = session.exec(statement).first()
        api_key.is_active = False
        session.commit()
    
    response = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": service_user_with_key["raw_key"]}
    )
    
    assert response.status_code == 401
    
    # Reactivate for other tests  
    with Session(test_engine) as session:
        statement = select(ApiKey).where(ApiKey.prefix == "testprefix")
        api_key = session.exec(statement).first()
        api_key.is_active = True
        session.commit()


@pytest.mark.asyncio
async def test_expired_api_key_rejected(async_test_client, test_engine, service_user_with_key):
    """Test that expired API keys are rejected."""
    with Session(test_engine) as session:
        # Create expired key
        expired_key = "expired.key123"
        expired_api_key = ApiKey(
            key_hash=get_password_hash(expired_key),
            prefix="expired",
            name="Expired Key",
            user_id=service_user_with_key["service_user_id"],
            is_active=True,
            expires_at=datetime.now() - timedelta(days=1)
        )
        session.add(expired_api_key)
        session.commit()
    
    response = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": expired_key}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_service_user_cannot_access_admin_endpoints(async_test_client, service_user_with_key):
    """Test that SERVICE role cannot access admin-only endpoints."""
    # Try to access admin endpoint with service API key
    response = await async_test_client.get(
        "/admin/users",
        headers={"X-API-Key": service_user_with_key["raw_key"]}
    )
    
    # Should be forbidden (403) or not found (404) if route doesn't exist
    # Or 401 if the endpoint doesn't support API Key auth
    assert response.status_code in [401, 403, 404]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
