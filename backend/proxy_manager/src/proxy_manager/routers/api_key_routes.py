"""API Key management routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session

from ..database import get_session
from ..models import ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse, User
from ..auth import get_current_user, get_current_admin
from ..crud import create_api_key, get_user_api_keys, revoke_api_key, get_api_key_by_id
from ..utils.logger import log_activity, get_client_ip

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreateResponse, status_code=201)
def create_user_api_key(
    api_key_data: ApiKeyCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new API key for the current user.
    
    The raw API key will only be shown once in the response.
    Make sure to save it securely!
    
    Args:
        api_key_data: API key creation data (name and optional expiration)
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Created API key metadata and the raw key (shown only once)
    """
    api_key, raw_key = create_api_key(
        session=session,
        user_id=current_user.id,
        name=api_key_data.name,
        expires_at=api_key_data.expires_at,
    )

    # Log API key creation
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=current_user,
        endpoint="/api-keys",
        method="POST",
        status_code=201,
        ip_address=ip_address,
    )

    return ApiKeyCreateResponse(
        api_key=ApiKeyResponse(
            id=api_key.id,
            prefix=api_key.prefix,
            name=api_key.name,
            created_at=api_key.created_at,
            expires_at=api_key.expires_at,
            is_active=api_key.is_active,
        ),
        raw_key=raw_key,
    )


@router.get("", response_model=List[ApiKeyResponse])
def list_my_api_keys(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    List all API keys for the current user.
    
    Note: The actual key values are never returned after creation.
    
    Args:
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        List of API key metadata
    """
    api_keys = get_user_api_keys(session, current_user.id)
    return [
        ApiKeyResponse(
            id=key.id,
            prefix=key.prefix,
            name=key.name,
            created_at=key.created_at,
            expires_at=key.expires_at,
            is_active=key.is_active,
        )
        for key in api_keys
    ]


@router.delete("/{key_id}", status_code=204)
def revoke_api_key_endpoint(
    key_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Revoke (delete) an API key.
    
    Users can only revoke their own API keys.
    
    Args:
        key_id: ID of the API key to revoke
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session
        
    Raises:
        HTTPException: If the API key is not found or doesn't belong to the user
    """
    success = revoke_api_key(session, key_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found or you don't have permission to revoke it",
        )

    # Log API key revocation
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=current_user,
        endpoint=f"/api-keys/{key_id}",
        method="DELETE",
        status_code=204,
        ip_address=ip_address,
    )


@router.get("/users/{user_id}/api-keys", response_model=List[ApiKeyResponse])
def list_user_api_keys_admin(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session),
):
    """
    List all API keys for a specific user (admin only).
    
    Args:
        user_id: ID of the user whose API keys to list
        current_admin: Current authenticated admin user
        session: Database session
        
    Returns:
        List of API key metadata for the specified user
    """
    api_keys = get_user_api_keys(session, user_id)
    return [
        ApiKeyResponse(
            id=key.id,
            prefix=key.prefix,
            name=key.name,
            created_at=key.created_at,
            expires_at=key.expires_at,
            is_active=key.is_active,
        )
        for key in api_keys
    ]
