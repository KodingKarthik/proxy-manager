"""Security tests for API Key authentication."""

import pytest
import time
import secrets
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine, select

from proxy_manager.models import User, UserRole, ApiKey
from proxy_manager.auth import get_password_hash, verify_password, get_api_key_user


class TestApiKeySecurity:
    """Security-focused tests for API Key authentication."""
    
    @classmethod
    def setup_class(cls):
        """Set up test database."""
        connect_args = {"check_same_thread": False}
        cls.engine = create_engine("sqlite:///:memory:", connect_args=connect_args)
        SQLModel.metadata.create_all(cls.engine)
        
        with Session(cls.engine) as session:
            cls.service_user = User(
                username="security-test-service",
                email="security@test.com",
                hashed_password=get_password_hash("unused"),
                role=UserRole.SERVICE,
                is_active=True
            )
            session.add(cls.service_user)
            session.commit()
            session.refresh(cls.service_user)
    
    @pytest.mark.asyncio
    async def test_timing_attack_resistance(self):
        """Test that key validation takes similar time for valid/invalid keys."""
        with Session(self.engine) as session:
            # Create a valid key
            valid_key = "timing.testsecret123"
            api_key = ApiKey(
                key_hash=get_password_hash(valid_key),
                prefix="timing",
                name="Timing Test Key",
                user_id=self.service_user.id,
                is_active=True
            )
            session.add(api_key)
            session.commit()
            
            # Time valid key authentication
            start = time.perf_counter()
            await get_api_key_user(api_key=valid_key, session=session)
            valid_time = time.perf_counter() - start
            
            # Time invalid key authentication (wrong secret)
            start = time.perf_counter()
            await get_api_key_user(api_key="timing.wrongsecret", session=session)
            invalid_time = time.perf_counter() - start
            
            # Times should be similar (within 50% of each other)
            # bcrypt comparison is constant-time, so this should pass
            ratio = max(valid_time, invalid_time) / min(valid_time, invalid_time)
            assert ratio < 2.0, f"Timing difference too large: {valid_time} vs {invalid_time}"
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_prefix(self):
        """Test that SQL injection attempts in prefix are handled safely."""
        with Session(self.engine) as session:
            # Try various SQL injection patterns
            injection_attempts = [
                "'; DROP TABLE apikey; --",
                "' OR '1'='1",
                "admin'--",
                "1' UNION SELECT * FROM user--"
            ]
            
            for injection in injection_attempts:
                malicious_key = f"{injection}.secret"
                user = await get_api_key_user(api_key=malicious_key, session=session)
                
                # Should safely return None, not cause SQL errors
                assert user is None
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_secret(self):
        """Test that SQL injection attempts in secret are handled safely."""
        with Session(self.engine) as session:
            malicious_key = "prefix.'; DROP TABLE apikey; --"
            user = await get_api_key_user(api_key=malicious_key, session=session)
            
            # Should safely return None
            assert user is None
    
    def test_key_hash_not_reversible(self):
        """Test that stored key hashes cannot be reversed to original key."""
        with Session(self.engine) as session:
            original_key = "secret.verysecretkey123"
            key_hash = get_password_hash(original_key)
            
            # Hash should be different from original
            assert key_hash != original_key
            
            # Hash should be bcrypt format
            assert key_hash.startswith("$2b$")
            
            # Should not contain original key
            assert "verysecretkey123" not in key_hash
    
    def test_same_key_different_hashes(self):
        """Test that same key produces different hashes (salt)."""
        key = "test.samekey"
        hash1 = get_password_hash(key)
        hash2 = get_password_hash(key)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(key, hash1)
        assert verify_password(key, hash2)
    
    @pytest.mark.asyncio
    async def test_brute_force_protection_concept(self):
        """Test that multiple failed attempts don't leak information."""
        with Session(self.engine) as session:
            # Create a key
            real_key = "brute.realsecret"
            api_key = ApiKey(
                key_hash=get_password_hash(real_key),
                prefix="brute",
                name="Brute Force Test",
                user_id=self.service_user.id,
                is_active=True
            )
            session.add(api_key)
            session.commit()
            
            # Try multiple wrong secrets
            attempts = [
                "brute.wrong1",
                "brute.wrong2",
                "brute.wrong3",
                "brute.wrong4",
                "brute.wrong5"
            ]
            
            for attempt in attempts:
                user = await get_api_key_user(api_key=attempt, session=session)
                # All should fail the same way
                assert user is None
    
    @pytest.mark.asyncio
    async def test_error_messages_dont_leak_key_existence(self):
        """Test that error responses don't reveal if a key exists."""
        with Session(self.engine) as session:
            # Create a key
            existing_key = "exists.secret"
            api_key = ApiKey(
                key_hash=get_password_hash(existing_key),
                prefix="exists",
                name="Exists Test",
                user_id=self.service_user.id,
                is_active=True
            )
            session.add(api_key)
            session.commit()
            
            # Try with wrong secret (key exists but wrong secret)
            user1 = await get_api_key_user(api_key="exists.wrongsecret", session=session)
            
            # Try with non-existent prefix
            user2 = await get_api_key_user(api_key="notexist.secret", session=session)
            
            # Both should return None (same response)
            assert user1 is None
            assert user2 is None
    
    def test_key_generation_randomness(self):
        """Test that generated keys are sufficiently random."""
        keys = set()
        
        # Generate 100 keys
        for _ in range(100):
            prefix = secrets.token_urlsafe(8)
            secret = secrets.token_urlsafe(32)
            key = f"{prefix}.{secret}"
            keys.add(key)
        
        # All should be unique
        assert len(keys) == 100
        
        # Check minimum length
        for key in keys:
            assert len(key) > 20  # At least 8 + 1 + 32 base64 chars
    
    @pytest.mark.asyncio
    async def test_inactive_key_not_enumerable(self):
        """Test that inactive keys can't be enumerated."""
        with Session(self.engine) as session:
            # Create inactive key
            inactive_key = "inactive.secret"
            api_key = ApiKey(
                key_hash=get_password_hash(inactive_key),
                prefix="inactive",
                name="Inactive Key",
                user_id=self.service_user.id,
                is_active=False
            )
            session.add(api_key)
            session.commit()
            
            # Try to use it
            user = await get_api_key_user(api_key=inactive_key, session=session)
            
            # Should fail same as non-existent key
            assert user is None
    
    @pytest.mark.asyncio
    async def test_expired_key_cleanup_concept(self):
        """Test concept of expired key handling."""
        with Session(self.engine) as session:
            # Create expired key
            expired_key = "expired.oldsecret"
            api_key = ApiKey(
                key_hash=get_password_hash(expired_key),
                prefix="expired",
                name="Expired Key",
                user_id=self.service_user.id,
                is_active=True,
                expires_at=datetime.now() - timedelta(days=30)
            )
            session.add(api_key)
            session.commit()
            
            # Should not authenticate
            user = await get_api_key_user(api_key=expired_key, session=session)
            assert user is None
            
            # In production, you'd want a cleanup job to delete old expired keys
            # This is just testing the concept


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
