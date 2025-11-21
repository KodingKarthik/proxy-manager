"""Tests for blacklist cache."""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from mitm_forwarder.blacklist_cache import BlacklistCache
from mitm_forwarder.config import Settings


@pytest.fixture
def mock_client():
    """Mock httpx client."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def blacklist_cache(mock_client):
    """Create blacklist cache instance."""
    return BlacklistCache(mock_client)


@pytest.mark.asyncio
async def test_blacklist_cache_refresh(blacklist_cache, mock_client, sample_blacklist_response):
    """Test blacklist cache refresh."""
    # Mock fetch_blacklist response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=sample_blacklist_response)
    mock_client.get = AsyncMock(return_value=mock_response)
    
    # Refresh cache
    await blacklist_cache.refresh()
    
    # Check patterns were loaded
    assert blacklist_cache._patterns
    assert len(blacklist_cache._patterns) == 2
    assert blacklist_cache._last_refresh > 0


@pytest.mark.asyncio
async def test_blacklist_matching(blacklist_cache, mock_client, sample_blacklist_response):
    """Test URL matching against blacklist."""
    # Load patterns
    blacklist_cache._compile_patterns(sample_blacklist_response)
    blacklist_cache._patterns = blacklist_cache._compile_patterns(sample_blacklist_response)
    blacklist_cache._pattern_data = sample_blacklist_response
    
    # Test matching URLs
    is_blacklisted, pattern = blacklist_cache.is_blacklisted("https://facebook.com/page")
    assert is_blacklisted
    assert "facebook" in pattern.lower()
    
    is_blacklisted, pattern = blacklist_cache.is_blacklisted("https://twitter.com/user")
    assert is_blacklisted
    assert "twitter" in pattern.lower()
    
    # Test non-matching URL
    is_blacklisted, pattern = blacklist_cache.is_blacklisted("https://example.com/page")
    assert not is_blacklisted
    assert pattern is None


def test_blacklist_needs_refresh(blacklist_cache):
    """Test refresh TTL check."""
    # Initially needs refresh (never refreshed)
    assert blacklist_cache.needs_refresh()
    
    # Set last refresh to now
    blacklist_cache._last_refresh = time.time()
    assert not blacklist_cache.needs_refresh()
    
    # Set last refresh to past (beyond TTL)
    with patch('mitm_forwarder.blacklist_cache.settings') as mock_settings:
        mock_settings.blacklist_refresh_seconds = 60
        blacklist_cache._last_refresh = time.time() - 120
        assert blacklist_cache.needs_refresh()


@pytest.mark.asyncio
async def test_blacklist_invalid_pattern(blacklist_cache):
    """Test handling of invalid regex patterns."""
    invalid_rules = [
        {"id": 1, "pattern": "[invalid regex"},
        {"id": 2, "pattern": "^.*valid\\.com.*$"}
    ]
    
    compiled = blacklist_cache._compile_patterns(invalid_rules)
    # Should only compile valid patterns
    assert len(compiled) == 1


@pytest.mark.asyncio
async def test_blacklist_case_insensitive(blacklist_cache):
    """Test case-insensitive matching."""
    rules = [{"id": 1, "pattern": "^.*example\\.com.*$"}]
    blacklist_cache._patterns = blacklist_cache._compile_patterns(rules)
    blacklist_cache._pattern_data = rules
    
    # Should match regardless of case
    assert blacklist_cache.is_blacklisted("https://EXAMPLE.COM/page")[0]
    assert blacklist_cache.is_blacklisted("https://Example.Com/page")[0]
    assert blacklist_cache.is_blacklisted("https://example.com/page")[0]

