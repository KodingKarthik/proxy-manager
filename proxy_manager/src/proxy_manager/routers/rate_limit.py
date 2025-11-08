"""Rate limiting dependency for FastAPI."""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, status, Request
from threading import Lock

from ..utils.config import settings
from ..models import User


class RateLimiter:
    """In-memory rate limiter using sliding window."""
    
    def __init__(self, requests_per_minute: int = None):
        """Initialize rate limiter."""
        self.requests_per_minute = requests_per_minute or settings.rate_limit_per_minute
        self._requests: Dict[int, List[float]] = defaultdict(list)
        self._lock = Lock()
        self._cleanup_interval = 60  # Clean up old entries every 60 seconds
        self._last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove old request timestamps to prevent memory leaks."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff_time = current_time - 120  # Keep last 2 minutes of data
        
        with self._lock:
            for user_id in list(self._requests.keys()):
                self._requests[user_id] = [
                    ts for ts in self._requests[user_id] if ts > cutoff_time
                ]
                if not self._requests[user_id]:
                    del self._requests[user_id]
            
            self._last_cleanup = current_time
    
    def check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if within limit, False if exceeded
        """
        self._cleanup_old_entries()
        
        current_time = time.time()
        window_start = current_time - 60  # Last 60 seconds
        
        with self._lock:
            # Get requests in the current window
            user_requests = [
                ts for ts in self._requests[user_id]
                if ts > window_start
            ]
            
            if len(user_requests) >= self.requests_per_minute:
                return False
            
            # Add current request
            user_requests.append(current_time)
            self._requests[user_id] = user_requests
        
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_rate_limit(user: User) -> None:
    """
    FastAPI dependency to check rate limit for a user.
    
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    if not rate_limiter.check_rate_limit(user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {rate_limiter.requests_per_minute} requests per minute"
        )

