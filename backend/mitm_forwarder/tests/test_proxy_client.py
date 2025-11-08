"""Tests for FastAPI proxy client."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from mitm_forwarder.proxy_client import get_proxy, fetch_blacklist, post_activity
from mitm_forwarder.config import Settings


@pytest.fixture
def mock_client():
    """Mock httpx async client."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.mark.asyncio
async def test_get_proxy_success(mock_client, sample_proxy_response):
    """Test successful proxy fetch."""
    # Mock successful response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=sample_proxy_response)
    mock_client.get = AsyncMock(return_value=mock_response)
    
    # Get proxy
    result = await get_proxy(mock_client, target_url="https://example.com")
    
    # Verify result
    assert result is not None
    assert result["proxy"] == "1.2.3.4:8080"
    assert result["proxy_id"] == 42
    
    # Verify request was made with correct headers
    mock_client.get.assert_called_once()
    call_args = mock_client.get.call_args
    assert "Authorization" in call_args.kwargs["headers"]
    assert "Bearer" in call_args.kwargs["headers"]["Authorization"]


@pytest.mark.asyncio
async def test_get_proxy_with_user_jwt(mock_client, sample_proxy_response):
    """Test proxy fetch with user JWT."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=sample_proxy_response)
    mock_client.get = AsyncMock(return_value=mock_response)
    
    # Get proxy with user JWT
    result = await get_proxy(
        mock_client,
        target_url="https://example.com",
        user_jwt="Bearer user-token-123"
    )
    
    assert result is not None
    
    # Verify X-Client-Authorization header was set
    call_args = mock_client.get.call_args
    assert "X-Client-Authorization" in call_args.kwargs["headers"]
    assert call_args.kwargs["headers"]["X-Client-Authorization"] == "Bearer user-token-123"


@pytest.mark.asyncio
async def test_get_proxy_blacklisted(mock_client):
    """Test proxy fetch when URL is blacklisted."""
    mock_response = AsyncMock()
    mock_response.status_code = 403
    mock_client.get = AsyncMock(return_value=mock_response)
    
    result = await get_proxy(mock_client, target_url="https://facebook.com")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_proxy_no_proxy_available(mock_client):
    """Test proxy fetch when no proxy is available."""
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_client.get = AsyncMock(return_value=mock_response)
    
    result = await get_proxy(mock_client)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_proxy_timeout(mock_client):
    """Test proxy fetch timeout handling."""
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
    
    result = await get_proxy(mock_client)
    
    assert result is None


@pytest.mark.asyncio
async def test_fetch_blacklist_success(mock_client, sample_blacklist_response):
    """Test successful blacklist fetch."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=sample_blacklist_response)
    mock_client.get = AsyncMock(return_value=mock_response)
    
    result = await fetch_blacklist(mock_client)
    
    assert result == sample_blacklist_response
    assert len(result) == 2


@pytest.mark.asyncio
async def test_fetch_blacklist_error(mock_client):
    """Test blacklist fetch error handling."""
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_client.get = AsyncMock(return_value=mock_response)
    
    result = await fetch_blacklist(mock_client)
    
    assert result == []


@pytest.mark.asyncio
async def test_post_activity_success(mock_client):
    """Test successful activity log posting."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_client.post = AsyncMock(return_value=mock_response)
    
    # Should not raise
    await post_activity(
        mock_client,
        user_id=7,
        endpoint="https://example.com",
        method="GET",
        status_code=200,
        target_url="https://example.com",
        proxy_id=42
    )
    
    # Verify POST was called
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert "json" in call_args.kwargs
    payload = call_args.kwargs["json"]
    assert payload["user_id"] == 7
    assert payload["method"] == "GET"
    assert payload["status_code"] == 200


@pytest.mark.asyncio
async def test_post_activity_error_handling(mock_client):
    """Test activity log posting error handling (should not raise)."""
    mock_client.post = AsyncMock(side_effect=Exception("Network error"))
    
    # Should not raise, just log
    await post_activity(
        mock_client,
        user_id=7,
        endpoint="https://example.com",
        method="GET",
        status_code=200
    )

