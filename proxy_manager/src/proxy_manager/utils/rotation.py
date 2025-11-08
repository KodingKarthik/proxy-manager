"""Rotation strategy manager for proxy selection."""

import random
import logging
from typing import List, Optional, Literal
from datetime import datetime
import threading

from ..models import Proxy
from ..crud import get_working_proxies, update_last_used
from sqlmodel import Session

logger = logging.getLogger(__name__)


class RotationManager:
    """Manages proxy rotation strategies."""
    
    def __init__(self):
        """Initialize the rotation manager."""
        self.round_robin_index = 0
        self.lock = threading.Lock()  # Thread-safe round-robin index
    
    def get_proxy(
        self,
        session: Session,
        strategy: Literal["random", "round_robin", "lru", "best", "health_score"] = "round_robin"
    ) -> Optional[Proxy]:
        """
        Get a proxy based on the specified strategy.
        
        Args:
            session: Database session
            strategy: Rotation strategy to use
            
        Returns:
            Selected Proxy or None if no working proxies available
        """
        working_proxies = get_working_proxies(session)
        
        if not working_proxies:
            return None
        
        if strategy == "random":
            return self._get_random(working_proxies, session)
        elif strategy == "round_robin":
            return self._get_round_robin(working_proxies, session)
        elif strategy == "lru":
            return self._get_lru(working_proxies, session)
        elif strategy == "best":
            return self._get_best(working_proxies, session)
        elif strategy == "health_score":
            return self._get_by_health_score(working_proxies, session)
        else:
            logger.warning(f"Unknown strategy: {strategy}, using health_score")
            return self._get_by_health_score(working_proxies, session)
    
    def _get_random(self, proxies: List[Proxy], session: Session) -> Optional[Proxy]:
        """Select a random working proxy."""
        if not proxies:
            return None
        proxy = random.choice(proxies)
        update_last_used(session, proxy)
        return proxy
    
    def _get_round_robin(self, proxies: List[Proxy], session: Session) -> Optional[Proxy]:
        """Select next proxy in round-robin fashion."""
        if not proxies:
            return None
        
        with self.lock:
            # Sort proxies by ID for consistent ordering
            sorted_proxies = sorted(proxies, key=lambda p: p.id)
            proxy = sorted_proxies[self.round_robin_index % len(sorted_proxies)]
            self.round_robin_index += 1
        
        update_last_used(session, proxy)
        return proxy
    
    def _get_lru(self, proxies: List[Proxy], session: Session) -> Optional[Proxy]:
        """Select the least recently used proxy."""
        if not proxies:
            return None
        
        # Sort by last_used (None values first, then oldest)
        sorted_proxies = sorted(
            proxies,
            key=lambda p: p.last_used if p.last_used else datetime.min
        )
        proxy = sorted_proxies[0]
        update_last_used(session, proxy)
        return proxy
    
    def _get_best(self, proxies: List[Proxy], session: Session) -> Optional[Proxy]:
        """Select the proxy with the lowest latency."""
        if not proxies:
            return None
        
        # Filter proxies with latency data
        proxies_with_latency = [p for p in proxies if p.latency is not None]
        
        if proxies_with_latency:
            # Sort by latency (lowest first)
            sorted_proxies = sorted(proxies_with_latency, key=lambda p: p.latency)
            proxy = sorted_proxies[0]
        else:
            # If no latency data, return first proxy
            proxy = proxies[0]
        
        update_last_used(session, proxy)
        return proxy
    
    def _get_by_health_score(self, proxies: List[Proxy], session: Session) -> Optional[Proxy]:
        """Select the proxy with the highest health score."""
        if not proxies:
            return None
        
        # Calculate health score for all proxies and sort by score (highest first)
        proxies_with_scores = [(p, p.calculate_health_score()) for p in proxies]
        sorted_proxies = sorted(proxies_with_scores, key=lambda x: x[1], reverse=True)
        
        # Get the proxy with the highest health score
        proxy = sorted_proxies[0][0]
        
        update_last_used(session, proxy)
        return proxy


# Global rotation manager instance
rotation_manager = RotationManager()

