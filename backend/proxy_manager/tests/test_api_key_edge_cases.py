"""Edge case tests for API Key authentication."""

import pytest
import secrets
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine, select
from fastapi import HTTPException

from proxy_manager.models import User, UserRole, ApiKey
from proxy_manager.auth import get_password_hash, get_api_key_user


class TestApiKeyEdgeCases:
    """Test edge cases and error handling."""
    
    @classmethod
    def setup_class(cls):
        """Set up test database."""
        connect_args = {"check_same_thread": False}
        cls.engine = create_engine("sqlite:///:memory:", connect_args=connect_args)
        SQLModel.metadata.create_all(cls.engine)
        
        with Session(cls.engine) as session:
            cls.service_user = User(
                username="edge-test-service",
                email="edge@test.com",
                hashed_password=get_password_hash("unused"),
                role=UserRole.SERVICE,
                is_active=True
            )
            session.add(cls.service_user)
            session.commit()
            session.refresh(cls.service_user)
    
    @pytest.mark.asyncio
    async def test_malformed_key_no_dot(self):
        """Test API key without dot separator."""
        with Session(self.engine) as session:
            user = await get_api_key_user(api_key="nodotinkey", session=session)
            assert user is None
    
    @pytest.mark.asyncio
    async def test_malformed_key_empty_prefix(self):
        """Test API key with empty prefix."""
        with Session(self.engine) as session:
            user = await get_api_key_user(api_key=".secretonly", session=session)
            assert user is None
    
    @pytest.mark.asyncio
    async def test_malformed_key_empty_secret(self):
        """Test API key with empty secret."""
        with Session(self.engine) as session:
            user = await get_api_key_user(api_key="prefixonly.", session=session)
            assert user is None
    
    @pytest.mark.asyncio
    async def test_empty_string_key(self):
        """Test empty string as API key."""
        with Session(self.engine) as session:
            user = await get_api_key_user(api_key="", session=session)
            assert user is None
    
    @pytest.mark.asyncio
    async def test_none_key(self):
        """Test None as API key."""
        with Session(self.engine) as session:
            user = await get_api_key_user(api_key=None, session=session)
            assert user is None
    
    @pytest.mark.asyncio
    async def test_very_long_key(self):
        """Test very long API key (should still work)."""
        with Session(self.engine) as session:
            # Create a very long key
            long_secret = secrets.token_urlsafe(256)
            long_key = f"longpref.{long_secret}"
            
            api_key = ApiKey(
                key_hash=get_password_hash(long_key),
                prefix="longpref",
                name="Long Key",
                user_id=self.service_user.id,
                is_active=True
            )
            session.add(api_key)
            session.commit()
            
            # Should authenticate successfully
            user = await get_api_key_user(api_key=long_key, session=session)
            assert user is not None
            assert user.id == self.service_user.id
    
    @pytest.mark.asyncio
    async def test_special_characters_in_key(self):
        """Test API key with special characters."""
        with Session(self.engine) as session:
            special_key = "special!@#.secret$%^&*()"
            
            api_key = ApiKey(
                key_hash=get_password_hash(special_key),
                prefix="special!@#",
                name="Special Key",
                user_id=self.service_user.id,
                is_active=True
            )
            session.add(api_key)
            session.commit()
            
            # Should work with special characters
            user = await get_api_key_user(api_key=special_key, session=session)
            assert user is not None
    
    @pytest.mark.asyncio
    async def test_multiple_keys_same_user(self):
        """Test user with multiple active API keys."""
        with Session(self.engine) as session:
            key1 = "prefix1.secret1"
            key2 = "prefix2.secret2"
            
            api_key1 = ApiKey(
                key_hash=get_password_hash(key1),
                prefix="prefix1",
                name="Key 1",
                user_id=self.service_user.id,
                is_active=True
            )
            api_key2 = ApiKey(
                key_hash=get_password_hash(key2),
                prefix="prefix2",
                name="Key 2",
                user_id=self.service_user.id,
                is_active=True
            )
            session.add_all([api_key1, api_key2])
            session.commit()
            
            # Both keys should work
            user1 = await get_api_key_user(api_key=key1, session=session)
            user2 = await get_api_key_user(api_key=key2, session=session)
            
            assert user1 is not None
            assert user2 is not None
            assert user1.id == user2.id == self.service_user.id
    
    @pytest.mark.asyncio
    async def test_key_with_multiple_dots(self):
        """Test API key with multiple dots (should use first dot as separator)."""
        with Session(self.engine) as session:
            multi_dot_key = "prefix.secret.with.dots"
            
            api_key = ApiKey(
                key_hash=get_password_hash(multi_dot_key),
                prefix="prefix",
                name="Multi-dot Key",
                user_id=self.service_user.id,
                is_active=True
            )
            session.add(api_key)
            session.commit()
            
            # Should work - splits on first dot
            user = await get_api_key_user(api_key=multi_dot_key, session=session)
            assert user is not None
    
    @pytest.mark.asyncio
    async def test_case_sensitive_keys(self):
        """Test that API keys are case-sensitive."""
        with Session(self.engine) as session:
            original_key = "CaseSens.SecretKey"
            
            api_key = ApiKey(
                key_hash=get_password_hash(original_key),
                prefix="CaseSens",
                name="Case Sensitive Key",
                user_id=self.service_user.id,
                is_active=True
            )
            session.add(api_key)
            session.commit()
            
            # Correct case should work
            user_correct = await get_api_key_user(api_key=original_key, session=session)
            assert user_correct is not None
            
            # Wrong case should fail
            user_wrong = await get_api_key_user(api_key="casesens.secretkey", session=session)
            assert user_wrong is None
    
    @pytest.mark.asyncio
    async def test_whitespace_in_key(self):
        """Test API key with whitespace (should fail or be trimmed)."""
        with Session(self.engine) as session:
            # Key with leading/trailing whitespace
            user = await get_api_key_user(api_key=" prefix.secret ", session=session)
            assert user is None  # Should not match any key
    
    @pytest.mark.asyncio
    async def test_duplicate_prefix_different_users(self):
        """Test that different users can have keys with same prefix (edge case)."""
        with Session(self.engine) as session:
            # Create another user
            user2 = User(
                username="user2",
                email="user2@test.com",
                hashed_password=get_password_hash("unused"),
                role=UserRole.SERVICE,
                is_active=True
            )
            session.add(user2)
            session.commit()
            session.refresh(user2)
            
            # Both users have keys with same prefix (bad practice but possible)
            key1 = "sameprefix.secret1"
            key2 = "sameprefix.secret2"
            
            api_key1 = ApiKey(
                key_hash=get_password_hash(key1),
                prefix="sameprefix",
                name="User1 Key",
                user_id=self.service_user.id,
                is_active=True
            )
            api_key2 = ApiKey(
                key_hash=get_password_hash(key2),
                prefix="sameprefix",
                name="User2 Key",
                user_id=user2.id,
                is_active=True
            )
            session.add_all([api_key1, api_key2])
            session.commit()
            
            # Each key should authenticate to correct user
            auth_user1 = await get_api_key_user(api_key=key1, session=session)
            auth_user2 = await get_api_key_user(api_key=key2, session=session)
            
            # Note: This might fail if implementation only checks prefix
            # The hash verification should distinguish them
            assert auth_user1.id == self.service_user.id
            assert auth_user2.id == user2.id


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
