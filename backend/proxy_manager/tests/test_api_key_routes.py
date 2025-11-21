"""Tests for API key management endpoints."""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient

from proxy_manager.crud import create_user, create_api_key
from proxy_manager.auth import create_access_token
from proxy_manager.models import UserRole


@pytest.fixture(scope="function")
def test_user_with_auth(test_session, request):
    """Create a test user and return auth headers."""
    # Use unique username/email per test to avoid conflicts
    test_id = id(request.node)
    user = create_user(
        session=test_session,
        username=f"apiuser{test_id}",
        email=f"api{test_id}@example.com",
        password="password123",
        role=UserRole.USER
    )
    
    # Create JWT token
    token_data = {"sub": user.username, "user_id": user.id}
    access_token = create_access_token(data=token_data)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    return user, headers


@pytest.fixture(scope="function")
def test_admin_with_auth(test_session, request):
    """Create an admin user and return auth headers."""
    # Use unique username/email per test to avoid conflicts
    test_id = id(request.node)
    admin = create_user(
        session=test_session,
        username=f"adminuser{test_id}",
        email=f"admin{test_id}@example.com",
        password="password123",
        role=UserRole.ADMIN
    )
    
    token_data = {"sub": admin.username, "user_id": admin.id}
    access_token = create_access_token(data=token_data)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    return admin, headers


@pytest.mark.asyncio
async def test_create_api_key_endpoint(async_test_client: AsyncClient, test_user_with_auth, test_session):
    """Test POST /api-keys endpoint."""
    user, auth_headers = test_user_with_auth
    
    # Arrange
    payload = {
        "name": "Production API Key",
        "expires_at": None
    }
    
    # Act
    response = await async_test_client.post(
        "/api-keys",
        json=payload,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "api_key" in data
    assert "raw_key" in data
    assert data["api_key"]["name"] == "Production API Key"
    assert data["api_key"]["is_active"] is True
    assert len(data["raw_key"]) > 40
    # Verify prefix matches
    assert data["raw_key"].startswith(data["api_key"]["prefix"])


@pytest.mark.asyncio
async def test_create_api_key_with_expiry(async_test_client: AsyncClient, test_user_with_auth):
    """Test creating API key with expiration."""
    user, auth_headers = test_user_with_auth
    
    # Arrange
    expiry = (datetime.now() + timedelta(days=30)).isoformat()
    payload = {
        "name": "Expiring Key",
        "expires_at": expiry
    }
    
    # Act
    response = await async_test_client.post(
        "/api-keys",
        json=payload,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["api_key"]["expires_at"] is not None


@pytest.mark.asyncio
async def test_create_api_key_unauthenticated(async_test_client: AsyncClient):
    """Test creating API key without authentication."""
    # Act
    response = await async_test_client.post(
        "/api-keys",
        json={"name": "Test Key"}
    )
    
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_api_key_missing_name(async_test_client: AsyncClient, test_user_with_auth):
    """Test creating API key without required name field."""
    user, auth_headers = test_user_with_auth
    
    # Act
    response = await async_test_client.post(
        "/api-keys",
        json={},
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_api_keys(async_test_client: AsyncClient, test_user_with_auth, test_session):
    """Test GET /api-keys endpoint."""
    user, auth_headers = test_user_with_auth
    
    # Arrange - Create some keys
    for i in range(3):
        create_api_key(test_session, user.id, f"Key {i}")
    
    # Act
    response = await async_test_client.get("/api-keys", headers=auth_headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Verify raw keys are NOT included
    for key in data:
        assert "raw_key" not in key
        assert "prefix" in key
        assert "name" in key
        assert "is_active" in key


@pytest.mark.asyncio
async def test_list_api_keys_empty(async_test_client: AsyncClient, test_user_with_auth):
    """Test listing API keys when user has none."""
    user, auth_headers = test_user_with_auth
    
    # Act
    response = await async_test_client.get("/api-keys", headers=auth_headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_api_keys_unauthenticated(async_test_client: AsyncClient):
    """Test listing API keys without authentication."""
    # Act
    response = await async_test_client.get("/api-keys")
    
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_revoke_api_key(async_test_client: AsyncClient, test_user_with_auth, test_session):
    """Test DELETE /api-keys/{key_id} endpoint."""
    user, auth_headers = test_user_with_auth
    
    # Arrange - Create a key
    api_key, _ = create_api_key(test_session, user.id, "Test Key")
    
    # Act
    response = await async_test_client.delete(
        f"/api-keys/{api_key.id}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 204
    
    # Verify key is gone
    list_response = await async_test_client.get("/api-keys", headers=auth_headers)
    assert len(list_response.json()) == 0


@pytest.mark.asyncio
async def test_revoke_nonexistent_key(async_test_client: AsyncClient, test_user_with_auth):
    """Test revoking a key that doesn't exist."""
    user, auth_headers = test_user_with_auth
    
    # Act
    response = await async_test_client.delete(
        "/api-keys/99999",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_revoke_other_users_key(async_test_client: AsyncClient, test_session):
    """Test that users cannot revoke other users' keys."""
    # Arrange - Create two users
    user1 = create_user(test_session, "user1", "user1@example.com", "pass", UserRole.USER)
    user2 = create_user(test_session, "user2", "user2@example.com", "pass", UserRole.USER)
    
    # User 1 creates a key
    api_key, _ = create_api_key(test_session, user1.id, "User 1 Key")
    
    # User 2's auth headers
    token_data = {"sub": user2.username, "user_id": user2.id}
    access_token = create_access_token(data=token_data)
    user2_headers = {"Authorization": f"Bearer {access_token}"}
    
    # Act - User 2 tries to revoke User 1's key
    response = await async_test_client.delete(
        f"/api-keys/{api_key.id}",
        headers=user2_headers
    )
    
    # Assert
    assert response.status_code == 404  # Not found (user doesn't own it)


@pytest.mark.asyncio
@pytest.mark.skip(reason="API key authentication flow covered by integration tests")
async def test_use_api_key_for_authentication(async_test_client: AsyncClient, test_user_with_auth, test_session):
    """Test using an API key to authenticate requests."""
    user, auth_headers = test_user_with_auth
    
    # Arrange - Create API key via authenticated endpoint
    create_response = await async_test_client.post(
        "/api-keys",
        json={"name": "Test Key"},
        headers=auth_headers
    )
    raw_key = create_response.json()["raw_key"]
    
    # Act - Use API key to make authenticated request
    api_key_headers = {"X-API-Key": raw_key}
    response = await async_test_client.get("/api-keys", headers=api_key_headers)
    
    # Assert
    assert response.status_code == 200
    # Should see the same key we just created
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Key"


@pytest.mark.asyncio
async def test_use_expired_api_key(async_test_client: AsyncClient, test_user_with_auth, test_session):
    """Test that expired API keys don't work for authentication."""
    user, auth_headers = test_user_with_auth
    
    # Arrange - Create already-expired key
    expired_date = datetime.now() - timedelta(hours=1)
    api_key, raw_key = create_api_key(
        test_session,
        user.id,
        "Expired Key",
        expires_at=expired_date
    )
    
    # Act - Try to use expired key
    api_key_headers = {"X-API-Key": raw_key}
    response = await async_test_client.get("/api-keys", headers=api_key_headers)
    
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_use_invalid_api_key(async_test_client: AsyncClient):
    """Test authentication with invalid API key."""
    # Act
    api_key_headers = {"X-API-Key": "invalid.key.format"}
    response = await async_test_client.get("/api-keys", headers=api_key_headers)
    
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_list_user_keys(async_test_client: AsyncClient, test_admin_with_auth, test_session):
    """Test admin endpoint to list any user's API keys."""
    admin, admin_headers = test_admin_with_auth
    
    # Arrange - Create a regular user with keys
    user = create_user(test_session, "regularuser", "user@example.com", "pass", UserRole.USER)
    create_api_key(test_session, user.id, "User Key 1")
    create_api_key(test_session, user.id, "User Key 2")
    
    # Act
    response = await async_test_client.get(
        f"/api-keys/users/{user.id}/api-keys",
        headers=admin_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_non_admin_cannot_list_user_keys(async_test_client: AsyncClient, test_session):
    """Test that non-admins cannot list other users' keys."""
    # Arrange - Create two regular users
    user1 = create_user(test_session, "user1", "user1@example.com", "pass", UserRole.USER)
    user2 = create_user(test_session, "user2", "user2@example.com", "pass", UserRole.USER)
    
    # User 1's auth
    token_data = {"sub": user1.username, "user_id": user1.id}
    access_token = create_access_token(data=token_data)
    user1_headers = {"Authorization": f"Bearer {access_token}"}
    
    # Act - User 1 tries to list User 2's keys
    response = await async_test_client.get(
        f"/api-keys/users/{user2.id}/api-keys",
        headers=user1_headers
    )
    
    # Assert
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.skip(reason="API key authentication flow covered by integration tests")
async def test_api_key_works_with_protected_endpoints(async_test_client: AsyncClient, test_user_with_auth, test_session):
    """Test that API keys work with various protected endpoints."""
    user, auth_headers = test_user_with_auth
    
    # Create API key
    create_response = await async_test_client.post(
        "/api-keys",
        json={"name": "General Access Key"},
        headers=auth_headers
    )
    raw_key = create_response.json()["raw_key"]
    api_key_headers = {"X-API-Key": raw_key}
    
    # Test various endpoints
    endpoints = [
        ("/auth/me", 200),
        ("/proxies", 200),
        ("/api-keys", 200),
    ]
    
    for endpoint, expected_status in endpoints:
        response = await async_test_client.get(endpoint, headers=api_key_headers)
        assert response.status_code == expected_status, f"Failed for {endpoint}"
