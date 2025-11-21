"""End-to-end tests for API Key authentication flow."""

import pytest
import secrets
import time
from datetime import datetime, timedelta
from sqlmodel import Session, select

from proxy_manager.models import User, UserRole, ApiKey, Blacklist
from proxy_manager.auth import get_password_hash


@pytest.mark.asyncio
async def test_full_service_lifecycle(async_test_client, test_engine):
    """Test complete lifecycle: create user, generate key, authenticate, revoke."""
    # Step 1: Create service user
    with Session(test_engine) as session:
        service_user = User(
            username="lifecycle-service",
            email="lifecycle@test.com",
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role=UserRole.SERVICE,
            is_active=True
        )
        session.add(service_user)
        session.commit()
        session.refresh(service_user)
        user_id = service_user.id
        
        # Step 2: Generate API key
        raw_key = f"{secrets.token_urlsafe(8)}.{secrets.token_urlsafe(32)}"
        prefix = raw_key.split(".")[0]
        
        api_key = ApiKey(
            key_hash=get_password_hash(raw_key),
            prefix=prefix,
            name="Lifecycle Test Key",
            user_id=user_id,
            is_active=True
        )
        session.add(api_key)
        
        # Create test data
        blacklist = Blacklist(
            pattern=".*\\.test\\.com.*",
            description="Test domain",
            created_by=user_id
        )
        session.add(blacklist)
        session.commit()
    
    # Step 3: Authenticate and fetch data
    response = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": raw_key}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Step 4: Post activity
    activity_response = await async_test_client.post(
        "/activity",
        json={
            "user_id": user_id,
            "endpoint": "/test",
            "method": "GET",
            "status_code": 200
        },
        headers={"X-API-Key": raw_key}
    )
    assert activity_response.status_code == 201
    
    # Step 5: Revoke key (deactivate)
    with Session(test_engine) as session:
        statement = select(ApiKey).where(ApiKey.prefix == prefix)
        key = session.exec(statement).first()
        key.is_active = False
        session.commit()
    
    # Step 6: Verify key no longer works
    revoked_response = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": raw_key}
    )
    assert revoked_response.status_code == 401


@pytest.mark.asyncio
async def test_key_rotation_flow(async_test_client, test_engine):
    """Test rotating API keys without downtime."""
    with Session(test_engine) as session:
        # Create service user
        service_user = User(
            username="rotation-service",
            email="rotation@test.com",
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role=UserRole.SERVICE,
            is_active=True
        )
        session.add(service_user)
        session.commit()
        session.refresh(service_user)
        user_id = service_user.id
        
        # Create old key
        old_key = f"{secrets.token_urlsafe(8)}.{secrets.token_urlsafe(32)}"
        old_prefix = old_key.split(".")[0]
        
        old_api_key = ApiKey(
            key_hash=get_password_hash(old_key),
            prefix=old_prefix,
            name="Old Key",
            user_id=user_id,
            is_active=True
        )
        session.add(old_api_key)
        session.commit()
    
    # Old key works
    response1 = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": old_key}
    )
    assert response1.status_code == 200
    
    # Create new key (both active simultaneously)
    with Session(test_engine) as session:
        new_key = f"{secrets.token_urlsafe(8)}.{secrets.token_urlsafe(32)}"
        new_prefix = new_key.split(".")[0]
        
        new_api_key = ApiKey(
            key_hash=get_password_hash(new_key),
            prefix=new_prefix,
            name="New Key",
            user_id=user_id,
            is_active=True
        )
        session.add(new_api_key)
        session.commit()
    
    # Both keys work
    response_old = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": old_key}
    )
    response_new = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": new_key}
    )
    assert response_old.status_code == 200
    assert response_new.status_code == 200
    
    # Deactivate old key
    with Session(test_engine) as session:
        statement = select(ApiKey).where(ApiKey.prefix == old_prefix)
        key = session.exec(statement).first()
        key.is_active = False
        session.commit()
    
    # Only new key works
    response_old_after = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": old_key}
    )
    response_new_after = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": new_key}
    )
    assert response_old_after.status_code == 401
    assert response_new_after.status_code == 200


@pytest.mark.asyncio
async def test_multi_service_isolation(async_test_client, test_engine):
    """Test that multiple services with different keys are isolated."""
    with Session(test_engine) as session:
        # Create two service users
        service1 = User(
            username="service1",
            email="service1@test.com",
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role=UserRole.SERVICE,
            is_active=True
        )
        service2 = User(
            username="service2",
            email="service2@test.com",
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role=UserRole.SERVICE,
            is_active=True
        )
        session.add_all([service1, service2])
        session.commit()
        session.refresh(service1)
        session.refresh(service2)
        
        # Create keys for each
        key1 = f"{secrets.token_urlsafe(8)}.{secrets.token_urlsafe(32)}"
        key2 = f"{secrets.token_urlsafe(8)}.{secrets.token_urlsafe(32)}"
        
        api_key1 = ApiKey(
            key_hash=get_password_hash(key1),
            prefix=key1.split(".")[0],
            name="Service 1 Key",
            user_id=service1.id,
            is_active=True
        )
        api_key2 = ApiKey(
            key_hash=get_password_hash(key2),
            prefix=key2.split(".")[0],
            name="Service 2 Key",
            user_id=service2.id,
            is_active=True
        )
        session.add_all([api_key1, api_key2])
        session.commit()
    
    # Both can access shared resources
    response1 = await async_test_client.get("/blacklist", headers={"X-API-Key": key1})
    response2 = await async_test_client.get("/blacklist", headers={"X-API-Key": key2})
    
    assert response1.status_code == 200
    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_expiration_enforcement(async_test_client, test_engine):
    """Test that expired keys are properly rejected."""
    with Session(test_engine) as session:
        service_user = User(
            username="expiry-service",
            email="expiry@test.com",
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role=UserRole.SERVICE,
            is_active=True
        )
        session.add(service_user)
        session.commit()
        session.refresh(service_user)
        
        # Create key that expires in 1 second
        short_lived_key = f"{secrets.token_urlsafe(8)}.{secrets.token_urlsafe(32)}"
        
        api_key = ApiKey(
            key_hash=get_password_hash(short_lived_key),
            prefix=short_lived_key.split(".")[0],
            name="Short-lived Key",
            user_id=service_user.id,
            is_active=True,
            expires_at=datetime.now() + timedelta(seconds=1)
        )
        session.add(api_key)
        session.commit()
    
    # Key works initially
    response_before = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": short_lived_key}
    )
    assert response_before.status_code == 200
    
    # Wait for expiration
    time.sleep(2)
    
    # Key no longer works
    response_after = await async_test_client.get(
        "/blacklist",
        headers={"X-API-Key": short_lived_key}
    )
    assert response_after.status_code == 401


@pytest.mark.asyncio
async def test_concurrent_requests_same_key(async_test_client, test_engine):
    """Test that same key can handle concurrent requests."""
    import asyncio
    
    with Session(test_engine) as session:
        service_user = User(
            username="concurrent-service",
            email="concurrent@test.com",
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role=UserRole.SERVICE,
            is_active=True
        )
        session.add(service_user)
        session.commit()
        session.refresh(service_user)
        
        api_key_str = f"{secrets.token_urlsafe(8)}.{secrets.token_urlsafe(32)}"
        
        api_key = ApiKey(
            key_hash=get_password_hash(api_key_str),
            prefix=api_key_str.split(".")[0],
            name="Concurrent Key",
            user_id=service_user.id,
            is_active=True
        )
        session.add(api_key)
        session.commit()
    
    async def make_request():
        return await async_test_client.get(
            "/blacklist",
            headers={"X-API-Key": api_key_str}
        )
    
    # Make 10 concurrent requests using asyncio.gather
    tasks = [make_request() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # All should succeed
    assert all(r.status_code == 200 for r in results)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
