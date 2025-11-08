"""Configuration management using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings
from pydantic import Field
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
    # TODO: CHANGE THIS!
    system_token: str = Field(
        default="", description="System token for FastAPI authentication (required)"
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
    default_user_jwt: str | None = Field(
        default=None,
        description="Default user JWT to use if client doesn't provide Authorization header",
    )

    class Config:
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        case_sensitive: bool = False


# Global settings instance
settings = Settings()
