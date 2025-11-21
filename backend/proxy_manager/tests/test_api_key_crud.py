"""Tests for API key CRUD operations."""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session

from proxy_manager.crud import (
    create_api_key,
    get_user_api_keys,
    get_api_key_by_id,
    revoke_api_key,
    deactivate_api_key,
    create_user,
)
from proxy_manager.auth import verify_password
from proxy_manager.models import UserRole


@pytest.fixture
def test_user(test_session: Session):
    """Create a test user."""
    user = create_user(
        session=test_session,
        username="testuser",
        email="test@example.com",
        password="password123",
        role=UserRole.USER
    )
    return user


@pytest.fixture
def test_user_2(test_session: Session):
    """Create a second test user."""
    user = create_user(
        session=test_session,
        username="testuser2",
        email="test2@example.com",
        password="password123",
        role=UserRole.USER
    )
    return user


def test_create_api_key(test_session: Session, test_user):
    """Test API key creation with secure key generation."""
    # Act
    api_key, raw_key = create_api_key(
        session=test_session,
        user_id=test_user.id,
        name="Test Key",
        expires_at=None
    )
    
    # Assert
    assert api_key.id is not None
    assert api_key.name == "Test Key"
    assert api_key.user_id == test_user.id
    assert api_key.is_active is True
    assert api_key.expires_at is None
    assert len(raw_key) > 40  # Token should be long
    assert api_key.prefix == raw_key[:8]  # Prefix matches
    assert verify_password(raw_key, api_key.key_hash)  # Hash verifies


def test_create_api_key_with_expiry(test_session: Session, test_user):
    """Test API key creation with expiration date."""
    # Arrange
    expiry = datetime.now() + timedelta(days=30)
    
    # Act
    api_key, raw_key = create_api_key(
        session=test_session,
        user_id=test_user.id,
        name="Expiring Key",
        expires_at=expiry
    )
    
    # Assert
    assert api_key.expires_at is not None
    # Compare dates (not exact time due to precision)
    assert api_key.expires_at.date() == expiry.date()


def test_get_user_api_keys(test_session: Session, test_user):
    """Test retrieving all API keys for a user."""
    # Arrange - Create multiple keys
    create_api_key(test_session, test_user.id, "Key 1")
    create_api_key(test_session, test_user.id, "Key 2")
    create_api_key(test_session, test_user.id, "Key 3")
    
    # Act
    keys = get_user_api_keys(test_session, test_user.id)
    
    # Assert
    assert len(keys) == 3
    # Should be ordered by created_at DESC (most recent first)
    assert keys[0].name == "Key 3"
    assert keys[1].name == "Key 2"
    assert keys[2].name == "Key 1"


def test_get_user_api_keys_empty(test_session: Session, test_user):
    """Test retrieving API keys when user has none."""
    # Act
    keys = get_user_api_keys(test_session, test_user.id)
    
    # Assert
    assert len(keys) == 0


def test_get_api_key_by_id(test_session: Session, test_user):
    """Test retrieving a specific API key by ID."""
    # Arrange
    api_key, _ = create_api_key(test_session, test_user.id, "Test Key")
    
    # Act
    retrieved_key = get_api_key_by_id(test_session, api_key.id)
    
    # Assert
    assert retrieved_key is not None
    assert retrieved_key.id == api_key.id
    assert retrieved_key.name == "Test Key"


def test_get_api_key_by_id_nonexistent(test_session: Session):
    """Test retrieving a non-existent API key."""
    # Act
    key = get_api_key_by_id(test_session, 99999)
    
    # Assert
    assert key is None


def test_revoke_api_key_success(test_session: Session, test_user):
    """Test successful API key revocation (hard delete)."""
    # Arrange
    api_key, _ = create_api_key(test_session, test_user.id, "Test Key")
    
    # Act
    result = revoke_api_key(test_session, api_key.id, test_user.id)
    
    # Assert
    assert result is True
    keys = get_user_api_keys(test_session, test_user.id)
    assert len(keys) == 0
    # Verify it's actually deleted
    assert get_api_key_by_id(test_session, api_key.id) is None


def test_revoke_api_key_wrong_owner(test_session: Session, test_user, test_user_2):
    """Test that users cannot revoke other users' keys."""
    # Arrange
    api_key, _ = create_api_key(test_session, test_user.id, "User 1 Key")
    
    # Act - User 2 tries to revoke User 1's key
    result = revoke_api_key(test_session, api_key.id, test_user_2.id)
    
    # Assert
    assert result is False
    keys = get_user_api_keys(test_session, test_user.id)
    assert len(keys) == 1  # Key still exists


def test_revoke_nonexistent_key(test_session: Session, test_user):
    """Test revoking a key that doesn't exist."""
    # Act
    result = revoke_api_key(test_session, 99999, test_user.id)
    
    # Assert
    assert result is False


def test_deactivate_api_key(test_session: Session, test_user):
    """Test soft-deleting an API key (deactivation)."""
    # Arrange
    api_key, _ = create_api_key(test_session, test_user.id, "Test Key")
    
    # Act
    updated_key = deactivate_api_key(test_session, api_key.id, test_user.id)
    
    # Assert
    assert updated_key is not None
    assert updated_key.is_active is False
    # Key still exists in database
    keys = get_user_api_keys(test_session, test_user.id)
    assert len(keys) == 1
    assert keys[0].is_active is False


def test_deactivate_api_key_wrong_owner(test_session: Session, test_user, test_user_2):
    """Test that users cannot deactivate other users' keys."""
    # Arrange
    api_key, _ = create_api_key(test_session, test_user.id, "User 1 Key")
    
    # Act
    result = deactivate_api_key(test_session, api_key.id, test_user_2.id)
    
    # Assert
    assert result is None
    # Key should still be active
    keys = get_user_api_keys(test_session, test_user.id)
    assert keys[0].is_active is True


def test_unique_prefixes(test_session: Session, test_user):
    """Test that each key gets a unique prefix (probabilistically)."""
    # Arrange & Act
    keys_and_raw = [
        create_api_key(test_session, test_user.id, f"Key {i}") 
        for i in range(10)
    ]
    
    # Assert
    prefixes = [key.prefix for key, _ in keys_and_raw]
    # With a good random generator, all 10 8-character prefixes should be unique
    assert len(prefixes) == len(set(prefixes)), "Prefixes should be unique"


def test_raw_key_never_stored(test_session: Session, test_user):
    """Test that raw keys are never stored in plaintext."""
    # Arrange & Act
    api_key, raw_key = create_api_key(test_session, test_user.id, "Test Key")
    
    # Assert
    # Raw key should not appear anywhere in the hash
    assert raw_key not in api_key.key_hash
    assert api_key.key_hash != raw_key
    # Hash should be in bcrypt format
    assert api_key.key_hash.startswith("$2b$")


def test_multiple_users_can_have_same_key_name(test_session: Session, test_user, test_user_2):
    """Test that different users can use the same key name."""
    # Act
    key1, _ = create_api_key(test_session, test_user.id, "Production Key")
    key2, _ = create_api_key(test_session, test_user_2.id, "Production Key")
    
    # Assert
    assert key1.name == key2.name
    assert key1.user_id != key2.user_id
    assert key1.prefix != key2.prefix  # Different keys


def test_create_api_key_with_past_expiry(test_session: Session, test_user):
    """Test creating an API key that's already expired."""
    # Arrange
    past_date = datetime.now() - timedelta(days=1)
    
    # Act
    api_key, raw_key = create_api_key(
        test_session,
        test_user.id,
        "Already Expired",
        expires_at=past_date
    )
    
    # Assert - Key is created but expired
    assert api_key.expires_at < datetime.now()
    assert api_key.is_active is True  # Still marked active, but expired


def test_key_hash_verification(test_session: Session, test_user):
    """Test that key hash can be verified correctly."""
    # Arrange
    api_key, raw_key = create_api_key(test_session, test_user.id, "Test Key")
    
    # Act & Assert
    # Correct key should verify
    assert verify_password(raw_key, api_key.key_hash) is True
    
    # Wrong key should not verify
    assert verify_password("wrong.key.here", api_key.key_hash) is False
    assert verify_password(raw_key + "extra", api_key.key_hash) is False
