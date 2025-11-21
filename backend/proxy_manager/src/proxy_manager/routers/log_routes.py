"""Activity log routes."""

from fastapi import APIRouter, Depends, Query, HTTPException, status, Header
from sqlmodel import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import secrets

from ..database import get_session
from ..models import User, ActivityLogResponse, ActivityLogFilter
from ..auth import get_current_user, get_current_user_or_service
from ..crud import get_user_logs, create_activity_log
from ..utils.csv_exporter import export_logs_to_csv
from ..utils.config import settings
from ..routers.rate_limit import check_rate_limit

router = APIRouter(prefix="/logs", tags=["logs"])
activity_router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("", response_model=list[ActivityLogResponse])
def get_my_logs(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    endpoint: Optional[str] = Query(None, description="Endpoint filter"),
    method: Optional[str] = Query(None, description="HTTP method filter"),
    status_code: Optional[int] = Query(None, description="Status code filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get current user's activity logs with optional filtering.
    
    Args:
        start_date: Filter logs from this date
        end_date: Filter logs until this date
        endpoint: Filter by endpoint
        method: Filter by HTTP method
        status_code: Filter by status code
        limit: Maximum number of logs to return
        offset: Number of logs to skip
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        List of activity logs
    """
    # Check rate limit
    check_rate_limit(current_user)
    
    # Create filter
    filter_params = ActivityLogFilter(
        start_date=start_date,
        end_date=end_date,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        limit=limit,
        offset=offset
    )
    
    logs = get_user_logs(session, current_user.id, filter_params)
    
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


@router.get("/export")
def export_my_logs(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    endpoint: Optional[str] = Query(None, description="Endpoint filter"),
    method: Optional[str] = Query(None, description="HTTP method filter"),
    status_code: Optional[int] = Query(None, description="Status code filter"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Export current user's activity logs as CSV.
    
    Args:
        start_date: Filter logs from this date
        end_date: Filter logs until this date
        endpoint: Filter by endpoint
        method: Filter by HTTP method
        status_code: Filter by status code
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        CSV file download
    """
    # Check rate limit
    check_rate_limit(current_user)
    
    # Create filter (no limit for export)
    filter_params = ActivityLogFilter(
        start_date=start_date,
        end_date=end_date,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        limit=10000,  # Large limit for export
        offset=0
    )
    
    logs = get_user_logs(session, current_user.id, filter_params)
    filename = f"my_activity_logs_{current_user.username}.csv"
    
    return export_logs_to_csv(logs, filename)


# Activity log creation schema for POST /activity
class ActivityLogCreate(BaseModel):
    """Schema for creating activity log from mitm_forwarder."""
    
    user_id: Optional[int] = None
    endpoint: str
    method: str
    status_code: int
    target_url: Optional[str] = None
    proxy_id: Optional[int] = None
    timestamp: Optional[float] = None  # Unix timestamp


@activity_router.post("", status_code=201)
def create_activity(
    activity_data: ActivityLogCreate,
    current_user: User = Depends(get_current_user_or_service),
    session: Session = Depends(get_session)
):
    """
    Create an activity log entry (called by mitm_forwarder).
    
    This endpoint accepts activity logs from the mitm_forwarder service.
    Authentication is done via API Key or Bearer token.
    
    Args:
        activity_data: Activity log data
        current_user: Authenticated user (service or human)
        session: Database session
        
    Returns:
        Success message
    """
    # No manual token check needed anymore
    
    # Handle user_id - if None, we might need to create a system user or skip
    # For now, we'll require user_id to be provided or use a default system user
    user_id = activity_data.user_id
    if user_id is None:
        # Try to get a default system user or create one
        from ..crud import get_user_by_username
        system_user = get_user_by_username(session, username="system")
        if system_user is None:
            # Create a system user if it doesn't exist
            from ..models import User, UserRole
            from ..auth import get_password_hash
            system_user = User(
                username="system",
                email="system@internal",
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                role=UserRole.USER,
                is_active=True
            )
            session.add(system_user)
            session.commit()
            session.refresh(system_user)
        user_id = system_user.id
    
    # Create activity log
    try:
        create_activity_log(
            session=session,
            user_id=user_id,
            endpoint=activity_data.endpoint,
            method=activity_data.method,
            status_code=activity_data.status_code,
            target_url=activity_data.target_url,
            ip_address=None  # IP address not provided by mitm_forwarder
        )
    except Exception as e:
        # Log error but don't fail - activity logging should be fire-and-forget
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create activity log: {e}")
    
    return {"status": "ok", "message": "Activity log created"}

