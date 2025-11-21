"""Tests for MITM forwarder proxy_client with API Key authentication."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from mitm_forwarder.proxy_client import fetch_blacklist, post_activity
from mitm_forwarder.config import settings


class TestProxyClientAuth:
    """Test proxy_client functions with API Key authentication."""
    
    @pytest.mark.asyncio
    async def test_fetch_blacklist_sends_api_key_header(self):
        """Test that fetch_blacklist sends X-API-Key header."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "pattern": ".*\\.blocked\\.com.*", "description": "Test"}
        ]
        mock_client.get.return_value = mock_response
        
        # Call function
        result = await fetch_blacklist(mock_client)
        
        # Verify API key header was sent
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        
        assert "headers" in call_args.kwargs
        assert "X-API-Key" in call_args.kwargs["headers"]
        assert call_args.kwargs["headers"]["X-API-Key"] == settings.system_api_key
        
        # Verify result
        assert len(result) == 1
        assert result[0]["pattern"] == ".*\\.blocked\\.com.*"
    
    @pytest.mark.asyncio
    async def test_fetch_blacklist_handles_401(self):
        """Test that fetch_blacklist handles 401 Unauthorized."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_client.get.return_value = mock_response
        
        result = await fetch_blacklist(mock_client)
        
        # Should return empty list on auth failure
        assert result == []
    
    @pytest.mark.asyncio
    async def test_fetch_blacklist_handles_timeout(self):
        """Test that fetch_blacklist handles timeout gracefully."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        
        result = await fetch_blacklist(mock_client)
        
        # Should return empty list on timeout
        assert result == []
    
    @pytest.mark.asyncio
    async def test_fetch_blacklist_handles_connection_error(self):
        """Test that fetch_blacklist handles connection errors."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        
        result = await fetch_blacklist(mock_client)
        
        # Should return empty list on connection error
        assert result == []
    
    @pytest.mark.asyncio
    async def test_post_activity_sends_api_key_header(self):
        """Test that post_activity sends X-API-Key header."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_client.post.return_value = mock_response
        
        # Call function
        await post_activity(
            client=mock_client,
            user_id=1,
            endpoint="/test",
            method="GET",
            status_code=200,
            target_url="https://example.com",
            proxy_id=1
        )
        
        # Verify API key header was sent
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        
        assert "headers" in call_args.kwargs
        assert "X-API-Key" in call_args.kwargs["headers"]
        assert call_args.kwargs["headers"]["X-API-Key"] == settings.system_api_key
        assert call_args.kwargs["headers"]["Content-Type"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_post_activity_sends_correct_payload(self):
        """Test that post_activity sends correct JSON payload."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_client.post.return_value = mock_response
        
        # Call function
        await post_activity(
            client=mock_client,
            user_id=5,
            endpoint="/api/test",
            method="POST",
            status_code=201,
            target_url="https://api.example.com",
            proxy_id=3
        )
        
        # Verify payload
        call_args = mock_client.post.call_args
        payload = call_args.kwargs["json"]
        
        assert payload["user_id"] == 5
        assert payload["endpoint"] == "/api/test"
        assert payload["method"] == "POST"
        assert payload["status_code"] == 201
        assert payload["target_url"] == "https://api.example.com"
        assert payload["proxy_id"] == 3
        assert "timestamp" in payload
    
    @pytest.mark.asyncio
    async def test_post_activity_handles_failure_gracefully(self):
        """Test that post_activity doesn't raise on failure (fire-and-forget)."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = Exception("Network error")
        
        # Should not raise exception
        try:
            await post_activity(
                client=mock_client,
                user_id=1,
                endpoint="/test",
                method="GET",
                status_code=200
            )
        except Exception as e:
            pytest.fail(f"post_activity should not raise: {e}")
    
    @pytest.mark.asyncio
    async def test_post_activity_with_none_values(self):
        """Test post_activity with None values for optional fields."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_client.post.return_value = mock_response
        
        # Call with None values
        await post_activity(
            client=mock_client,
            user_id=None,
            endpoint="/test",
            method="GET",
            status_code=200,
            target_url=None,
            proxy_id=None
        )
        
        # Verify it still works
        call_args = mock_client.post.call_args
        payload = call_args.kwargs["json"]
        
        assert payload["user_id"] is None
        assert payload["target_url"] == "/test"  # Falls back to endpoint
        assert payload["proxy_id"] is None
    
    @pytest.mark.asyncio
    async def test_missing_api_key_config(self):
        """Test behavior when system_api_key is not configured."""
        # Temporarily clear the API key
        original_key = settings.system_api_key
        settings.system_api_key = ""
        
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_client.get.return_value = mock_response
        
        result = await fetch_blacklist(mock_client)
        
        # Should send empty string and get 401
        assert result == []
        
        # Restore original key
        settings.system_api_key = original_key
    
    @pytest.mark.asyncio
    async def test_fetch_blacklist_correct_url(self):
        """Test that fetch_blacklist uses correct URL."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response
        
        await fetch_blacklist(mock_client)
        
        # Verify URL
        call_args = mock_client.get.call_args
        expected_url = f"{settings.fastapi_base_url}{settings.fastapi_blacklist_endpoint}"
        assert call_args.args[0] == expected_url or call_args.kwargs.get("url") == expected_url
    
    @pytest.mark.asyncio
    async def test_post_activity_correct_url(self):
        """Test that post_activity uses correct URL."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_client.post.return_value = mock_response
        
        await post_activity(
            client=mock_client,
            user_id=1,
            endpoint="/test",
            method="GET",
            status_code=200
        )
        
        # Verify URL
        call_args = mock_client.post.call_args
        expected_url = f"{settings.fastapi_base_url}{settings.fastapi_activity_endpoint}"
        assert call_args.args[0] == expected_url or call_args.kwargs.get("url") == expected_url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
