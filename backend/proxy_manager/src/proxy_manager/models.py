"""SQLModel Proxy model and Pydantic schemas."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"
    SERVICE = "service"


class User(SQLModel, table=True):
    """User database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    activity_logs: List["ActivityLog"] = Relationship(back_populates="user")
    created_blacklists: List["Blacklist"] = Relationship(
        back_populates="created_by_user"
    )


class Proxy(SQLModel, table=True):
    """Proxy database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    ip: str = Field(index=True)
    port: int
    protocol: str = Field(
        default="http", description="Protocol: http, https, or socks5"
    )
    username: Optional[str] = None
    password: Optional[str] = None
    latency: Optional[float] = Field(
        default=None, description="Latency in milliseconds"
    )
    last_checked: Optional[datetime] = Field(default=None)
    is_working: bool = Field(default=False, index=True)
    fail_count: int = Field(default=0)
    last_used: Optional[datetime] = Field(default=None, description="For LRU strategy")

    @property
    def address(self) -> str:
        """Get proxy address as ip:port string."""
        return f"{self.ip}:{self.port}"

    @property
    def proxy_url(self) -> str:
        """Get proxy URL for httpx."""
        auth_part = ""
        if self.username and self.password:
            username = self.username.strip() if isinstance(self.username, str) else ""
            password = self.password.strip() if isinstance(self.password, str) else ""
            if username and password:
                auth_part = f"{username}:{password}@"

        protocol = self.protocol.lower() if self.protocol else "http"
        return f"{protocol}://{auth_part}{self.ip}:{self.port}"

    def calculate_health_score(self) -> float:
        """
        Calculate health score based on multiple factors.
        Score ranges from 0.0 (worst) to 100.0 (best).

        Factors considered:
        - Working status (40 points)
        - Latency (30 points) - lower is better
        - Failure count (20 points) - lower is better
        - Recency of health check (10 points) - more recent is better
        """
        score = 0.0

        # Factor 1: Working status (40 points)
        if self.is_working:
            score += 40.0
        else:
            return 0.0  # If not working, health score is 0

        # Factor 2: Latency (30 points)
        # Lower latency = higher score
        # Ideal: < 100ms = 30 points
        # Good: 100-300ms = 20 points
        # Fair: 300-500ms = 10 points
        # Poor: > 500ms = 5 points
        if self.latency is not None:
            if self.latency < 100:
                score += 30.0
            elif self.latency < 300:
                score += 20.0
            elif self.latency < 500:
                score += 10.0
            else:
                score += 5.0
        else:
            score += 15.0  # No latency data = medium score

        # Factor 3: Failure count (20 points)
        # No failures = 20 points
        # 1-2 failures = 15 points
        # 3-5 failures = 10 points
        # > 5 failures = 5 points
        if self.fail_count == 0:
            score += 20.0
        elif self.fail_count <= 2:
            score += 15.0
        elif self.fail_count <= 5:
            score += 10.0
        else:
            score += 5.0

        # Factor 4: Recency of health check (10 points)
        # Checked within last hour = 10 points
        # Checked within last day = 7 points
        # Checked within last week = 5 points
        # Older = 2 points
        if self.last_checked:
            time_since_check = (datetime.now() - self.last_checked).total_seconds()
            hours = time_since_check / 3600
            if hours < 1:
                score += 10.0
            elif hours < 24:
                score += 7.0
            elif hours < 168:  # 7 days
                score += 5.0
            else:
                score += 2.0
        else:
            score += 1.0  # Never checked = very low score

        return min(score, 100.0)  # Cap at 100


class ActivityLog(SQLModel, table=True):
    """Activity log database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    endpoint: str
    method: str
    timestamp: datetime = Field(default_factory=datetime.now, index=True)
    status_code: int
    target_url: Optional[str] = None
    ip_address: Optional[str] = None

    # Relationships
    user: User = Relationship(back_populates="activity_logs")


class Blacklist(SQLModel, table=True):
    """Blacklist regex pattern model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    pattern: str = Field(description="Regex pattern to match against URLs")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: int = Field(foreign_key="user.id")

    # Relationships
    created_by_user: User = Relationship(back_populates="created_blacklists")


class ApiKey(SQLModel, table=True):
    """API Key model for service authentication."""

    id: Optional[int] = Field(default=None, primary_key=True)
    key_hash: str = Field(index=True)
    prefix: str = Field(index=True, description="First 8 characters of the key")
    name: str = Field(description="Friendly name for the key")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)

    # Relationships
    user: User = Relationship()


class ProxyCreate(BaseModel):
    """Schema for creating a new proxy."""

    ip: str
    port: int
    protocol: str = Field(
        default="http", description="Protocol: http, https, or socks5"
    )
    username: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ip": "192.168.1.1",
                "port": 8080,
                "protocol": "http",
                "username": "user",
                "password": "pass",
            }
        }
    )


class ProxyResponse(BaseModel):
    """Schema for proxy response."""

    id: int
    ip: str
    port: int
    username: Optional[str] = None
    latency: Optional[float] = None
    last_checked: Optional[datetime] = None
    is_working: bool
    fail_count: int
    last_used: Optional[datetime] = None
    address: str
    health_score: Optional[float] = None
    protocol: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProxyUpdate(BaseModel):
    """Schema for updating proxy metadata."""

    latency: Optional[float] = None
    last_checked: Optional[datetime] = None
    is_working: Optional[bool] = None
    fail_count: Optional[int] = None
    last_used: Optional[datetime] = None


class ProxyTestResult(BaseModel):
    """Result of a proxy test."""

    proxy_id: int
    success: bool
    latency: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None


# User schemas
class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword123",
            }
        }
    )


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""

    username: Optional[str] = None
    user_id: Optional[int] = None


# Activity log schemas
class ActivityLogResponse(BaseModel):
    """Schema for activity log response."""

    id: int
    user_id: int
    endpoint: str
    method: str
    timestamp: datetime
    status_code: int
    target_url: Optional[str] = None
    ip_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ActivityLogFilter(BaseModel):
    """Schema for filtering activity logs."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    limit: int = 100
    offset: int = 0


# Blacklist schemas
class BlacklistCreate(BaseModel):
    """Schema for creating a blacklist rule."""

    pattern: str = Field(description="Regex pattern to match against URLs")
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pattern": ".*\\.example\\.com.*",
                "description": "Block all example.com domains",
            }
        }
    )


class BlacklistResponse(BaseModel):
    """Schema for blacklist response."""

    id: int
    pattern: str
    description: Optional[str] = None
    created_at: datetime
    created_by: int


    model_config = ConfigDict(from_attributes=True)


# API Key schemas
class ApiKeyCreate(BaseModel):
    """Schema for creating an API key."""

    name: str = Field(description="Friendly name for the API key")
    expires_at: Optional[datetime] = Field(
        default=None, description="Optional expiration date for the key"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Production Service",
                "expires_at": "2025-12-31T23:59:59",
            }
        }
    )


class ApiKeyResponse(BaseModel):
    """Schema for API key response (never includes the actual key)."""

    id: int
    prefix: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ApiKeyCreateResponse(BaseModel):
    """Response when creating a new API key (includes the raw key once)."""

    api_key: ApiKeyResponse
    raw_key: str = Field(
        description="The full API key - save this! It will only be shown once."
    )
