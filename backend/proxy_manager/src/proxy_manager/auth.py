"""Authentication and authorization utilities."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from .database import get_session
from .models import User, TokenData, UserRole
from .utils.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme for Swagger UI (simpler, shows "Value" field)
http_bearer = HTTPBearer(auto_error=False)

# OAuth2 scheme for OAuth2 flow (kept for compatibility)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """Verify and decode a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        token_type_in_payload: str = payload.get("type")

        if username is None:
            raise credentials_exception

        if token_type_in_payload != token_type:
            raise credentials_exception

        token_data = TokenData(username=username, user_id=payload.get("user_id"))
        return token_data

    except JWTError:
        raise credentials_exception


async def get_token_from_request(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    oauth2_token: Optional[str] = Depends(oauth2_scheme),
) -> str:
    """
    Get token from either HTTP Bearer or OAuth2 scheme.
    This allows Swagger UI to work with both methods.
    """
    # Try HTTP Bearer first (works better with Swagger UI)
    if credentials:
        return credentials.credentials

    # Fall back to OAuth2 token
    if oauth2_token:
        return oauth2_token

    # No token found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: str = Depends(get_token_from_request),
    session: Session = Depends(get_session),
) -> User:
    """Get the current authenticated user."""
    token_data = verify_token(token, "access")

    from .crud import get_user_by_username

    user = get_user_by_username(session, username=token_data.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get the current user and verify they are an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
