"""Configuration management using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
from dotenv import load_dotenv

# Load environment variables from .env file
_ = load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    fastapi_base_url: str = Field(
        default="http://127.0.0.1:8000", description="FastAPI backend base URL"
    )
    fastapi_proxy_endpoint: str = Field(
        default="/proxy", description="FastAPI proxy endpoint"
    )
    fastapi_blacklist_endpoint: str = Field(
        default="/blacklist", description="FastAPI blacklist endpoint"
    )
    fastapi_activity_endpoint: str = Field(
        default="/activity", description="FastAPI activity logging endpoint"
    )
    system_token: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsImV4cCI6MTc2MjY4NzM5MCwidHlwZSI6ImFjY2VzcyJ9.hqiId44Ci6lIz0scolFk7P8QVpMICbe79oEysG_SYA8",
        description="System token for FastAPI authentication (required)",
    )
    blacklist_refresh_seconds: int = Field(
        default=60, description="Blacklist cache refresh interval in seconds"
    )
    httpx_timeout: float = Field(
        default=30.0, description="HTTP request timeout in seconds"
    )
    mitm_listen_port: int = Field(
        default=8080, description="Port for mitmproxy to listen on"
    )
    max_concurrent_requests: int = Field(
        default=100, description="Maximum concurrent outbound requests"
    )
    require_user_jwt: bool = Field(
        default=True,
        description="Require user JWT in Authorization header (reject if missing)",
    )
    default_user_jwt: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsImV4cCI6MTc2MjY4NzM5MCwidHlwZSI6ImFjY2VzcyJ9.hqiId44Ci6lIz0scolFk7P8QVpMICbe79oEysG_SYA8",
        description="Default user JWT to use if client doesn't provide Authorization header",
    )
    rotation_strategy: Literal[
        "random", "round_robin", "lru", "best", "health_score"
    ] = Field(
        default="best",
        description="Rotation strategy for proxy selection: random, round_robin, lru, best (lowest latency), health_score (best health)",
    )
    retry_count: int = Field(
        default=1,
        description="Number of retries with the same strategy on connection errors",
    )
    fallback_strategy: Literal[
        "random", "round_robin", "lru", "best", "health_score"
    ] = Field(
        default="health_score",
        description="Fallback rotation strategy to use after all retries fail",
    )

    class Config:
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        case_sensitive: bool = False


# Global settings instance
settings = Settings()
