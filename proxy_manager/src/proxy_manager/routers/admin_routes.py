"""Admin-only routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional, List
from datetime import datetime

from ..database import get_session
from ..models import User, UserResponse, ActivityLogResponse, ActivityLogFilter, UserRole
from ..auth import get_current_admin
from ..crud import (
    get_all_users, delete_user, update_user_role,
    get_all_logs, get_user_by_id
)
from ..utils.csv_exporter import export_logs_to_csv
from ..utils.logger import log_activity, get_client_ip
from ..routers.rate_limit import check_rate_limit
from fastapi import Request

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """
    List all users (admin only).
    
    Args:
        limit: Maximum number of users to return
        offset: Number of users to skip
        admin: Current admin user
        session: Database session
        
    Returns:
        List of users
    """
    check_rate_limit(admin)
    
    users = get_all_users(session, limit=limit, offset=offset)
    
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]


@router.delete("/users/{user_id}", status_code=204)
def delete_user_by_id(
    user_id: int,
    request: Request,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """
    Delete a user by ID (admin only).
    
    Args:
        user_id: ID of user to delete
        request: FastAPI request object
        admin: Current admin user
        session: Database session
    """
    check_rate_limit(admin)
    
    # Prevent admin from deleting themselves
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user_to_delete = get_user_by_id(session, user_id)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    success = delete_user(session, user_id)
    
    if success:
        ip_address = get_client_ip(request)
        log_activity(
            session=session,
            user=admin,
            endpoint=f"/admin/users/{user_id}",
            method="DELETE",
            status_code=204,
            ip_address=ip_address
        )


@router.patch("/users/{user_id}/promote", response_model=UserResponse)
def promote_user_to_admin(
    user_id: int,
    request: Request,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """
    Promote a user to admin role (admin only).
    
    Args:
        user_id: ID of user to promote
        request: FastAPI request object
        admin: Current admin user
        session: Database session
        
    Returns:
        Updated user
    """
    check_rate_limit(admin)
    
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )
    
    updated_user = update_user_role(session, user, UserRole.ADMIN)
    
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=admin,
        endpoint=f"/admin/users/{user_id}/promote",
        method="PATCH",
        status_code=200,
        ip_address=ip_address
    )
    
    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        role=updated_user.role,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at
    )


@router.get("/logs", response_model=List[ActivityLogResponse])
def view_all_logs(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    endpoint: Optional[str] = Query(None, description="Endpoint filter"),
    method: Optional[str] = Query(None, description="HTTP method filter"),
    status_code: Optional[int] = Query(None, description="Status code filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """
    View all activity logs (admin only).
    
    Args:
        start_date: Filter logs from this date
        end_date: Filter logs until this date
        endpoint: Filter by endpoint
        method: Filter by HTTP method
        status_code: Filter by status code
        limit: Maximum number of logs to return
        offset: Number of logs to skip
        admin: Current admin user
        session: Database session
        
    Returns:
        List of all activity logs
    """
    check_rate_limit(admin)
    
    filter_params = ActivityLogFilter(
        start_date=start_date,
        end_date=end_date,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        limit=limit,
        offset=offset
    )
    
    logs = get_all_logs(session, filter_params)
    
    return [
        ActivityLogResponse(
            id=log.id,
            user_id=log.user_id,
            endpoint=log.endpoint,
            method=log.method,
            timestamp=log.timestamp,
            status_code=log.status_code,
            target_url=log.target_url,
            ip_address=log.ip_address
        )
        for log in logs
    ]


@router.get("/logs/export")
def export_all_logs(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    endpoint: Optional[str] = Query(None, description="Endpoint filter"),
    method: Optional[str] = Query(None, description="HTTP method filter"),
    status_code: Optional[int] = Query(None, description="Status code filter"),
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """
    Export all activity logs as CSV (admin only).
    
    Args:
        start_date: Filter logs from this date
        end_date: Filter logs until this date
        endpoint: Filter by endpoint
        method: Filter by HTTP method
        status_code: Filter by status code
        admin: Current admin user
        session: Database session
        
    Returns:
        CSV file download
    """
    check_rate_limit(admin)
    
    filter_params = ActivityLogFilter(
        start_date=start_date,
        end_date=end_date,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        limit=10000,  # Large limit for export
        offset=0
    )
    
    logs = get_all_logs(session, filter_params)
    filename = "all_activity_logs.csv"
    
    return export_logs_to_csv(logs, filename)

