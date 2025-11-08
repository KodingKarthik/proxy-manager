"""Configuration management using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
from dotenv import load_dotenv
import secrets

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Proxy testing settings
    test_url: str = Field(
        default="https://httpbin.org/ip",
        description="URL to test proxies against"
    )
    check_interval: int = Field(
        default=300,
        description="Health check interval in seconds"
    )
    max_threads: int = Field(
        default=20,
        description="Maximum number of threads for concurrent proxy testing"
    )
    rotation_strategy: Literal["random", "round_robin", "lru", "best", "health_score"] = Field(
        default="health_score",
        description="Default rotation strategy: random, round_robin, lru, best (lowest latency), health_score (best health)"
    )
    db_url: str = Field(
        default="sqlite:///./proxy_manager.db",
        description="Database connection URL"
    )
    
    # JWT settings
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT token signing"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    
    # Rate limiting settings
    rate_limit_per_minute: int = Field(
        default=60,
        description="Rate limit per minute per user"
    )
    
    # Logging settings
    log_dir: str = Field(
        default="./logs",
        description="Directory for log files"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Blacklist settings
    blacklist_enabled: bool = Field(
        default=True,
        description="Enable blacklist enforcement"
    )
    
    # System token for internal service authentication
    system_token: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="System token for internal service authentication (mitm_forwarder)"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

