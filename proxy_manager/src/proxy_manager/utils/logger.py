"""Unified logging setup for file and database logging."""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime
from fastapi import Request
from sqlmodel import Session

from ..utils.config import settings
from ..models import ActivityLog, User


def setup_logging():
    """Configure file and console logging."""
    # Create logs directory if it doesn't exist
    os.makedirs(settings.log_dir, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = os.path.join(settings.log_dir, "activity.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request."""
    # Check for forwarded IP (when behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    if request.client:
        return request.client.host
    
    return None


def log_activity(
    session: Session,
    user: User,
    endpoint: str,
    method: str,
    status_code: int,
    target_url: Optional[str] = None,
    ip_address: Optional[str] = None
) -> ActivityLog:
    """
    Log activity to both database and file.
    
    Args:
        session: Database session
        user: User who performed the action
        endpoint: API endpoint accessed
        method: HTTP method
        status_code: HTTP status code
        target_url: Optional target URL (for proxy requests)
        ip_address: Optional client IP address
        
    Returns:
        Created ActivityLog entry
    """
    from ..crud import create_activity_log
    
    # Create log entry
    activity_log = create_activity_log(
        session=session,
        user_id=user.id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        target_url=target_url,
        ip_address=ip_address
    )
    
    # Also log to file
    logger = logging.getLogger(__name__)
    log_message = (
        f"User: {user.username} ({user.id}) | "
        f"Method: {method} | Endpoint: {endpoint} | "
        f"Status: {status_code}"
    )
    if target_url:
        log_message += f" | Target: {target_url}"
    if ip_address:
        log_message += f" | IP: {ip_address}"
    
    logger.info(log_message)
    
    return activity_log

