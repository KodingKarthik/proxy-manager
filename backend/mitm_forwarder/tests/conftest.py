"""Test configuration and fixtures."""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator

from mitm_forwarder.config import Settings


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    monkeypatch.setenv("SYSTEM_TOKEN", "test-system-token")
    monkeypatch.setenv("FASTAPI_BASE_URL", "http://test-api:8000")
    return Settings()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx async client."""
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def sample_proxy_response():
    """Sample proxy response from FastAPI."""
    return {
        "id": 42,
        "ip": "1.2.3.4",
        "port": 8080,
        "address": "1.2.3.4:8080",
        "protocol": "http",
        "is_working": True,
        "latency": 50.5
    }


@pytest.fixture
def sample_blacklist_response():
    """Sample blacklist response from FastAPI."""
    return [
        {
            "id": 1,
            "pattern": "^.*facebook\\.com.*$",
            "description": "Block Facebook",
            "created_at": "2024-01-01T00:00:00",
            "created_by": 1
        },
        {
            "id": 2,
            "pattern": "^.*twitter\\.com.*$",
            "description": "Block Twitter",
            "created_at": "2024-01-01T00:00:00",
            "created_by": 1
        }
    ]

