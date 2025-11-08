"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..database import get_session
from ..models import UserCreate, UserResponse, UserLogin, Token, User
from ..auth import (
    verify_password, create_access_token, create_refresh_token,
    verify_token, get_current_user
)
from ..crud import (
    create_user, get_user_by_username, get_user_by_email
)
from ..utils.logger import log_activity, get_client_ip
from fastapi import Request

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Register a new user. First user automatically becomes admin.
    
    Args:
        user_data: User registration data
        request: FastAPI request object
        session: Database session
        
    Returns:
        Created user
    """
    # Check if username already exists
    if get_user_by_username(session, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if get_user_by_email(session, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user (first user becomes admin automatically)
    user = create_user(
        session=session,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    # Log registration
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=user,
        endpoint="/auth/register",
        method="POST",
        status_code=201,
        ip_address=ip_address
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("/login", response_model=Token)
def login(
    user_credentials: UserLogin,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Login and obtain JWT tokens.
    
    Args:
        user_credentials: Username and password
        request: FastAPI request object
        session: Database session
        
    Returns:
        Access and refresh tokens
    """
    user = get_user_by_username(session, user_credentials.username)
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create tokens
    token_data = {"sub": user.username, "user_id": user.id}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    # Log login
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=user,
        endpoint="/auth/login",
        method="POST",
        status_code=200,
        ip_address=ip_address
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token
        request: FastAPI request object
        session: Database session
        
    Returns:
        New access and refresh tokens
    """
    token_data = verify_token(refresh_token, "refresh")
    user = get_user_by_username(session, token_data.username)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user"
        )
    
    # Create new tokens
    new_token_data = {"sub": user.username, "user_id": user.id}
    new_access_token = create_access_token(data=new_token_data)
    new_refresh_token = create_refresh_token(data=new_token_data)
    
    # Log token refresh
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=user,
        endpoint="/auth/refresh",
        method="POST",
        status_code=200,
        ip_address=ip_address
    )
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

