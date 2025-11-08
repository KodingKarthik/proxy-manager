"""Blacklist caching with auto-refresh."""

import re
import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from threading import Lock
import httpx

from .config import settings
from .proxy_client import fetch_blacklist

logger = logging.getLogger(__name__)


class BlacklistCache:
    """Thread-safe blacklist cache with auto-refresh."""
    
    def __init__(self, client: httpx.AsyncClient):
        """
        Initialize blacklist cache.
        
        Args:
            client: httpx async client for fetching blacklist
        """
        self.client = client
        self._patterns: List[re.Pattern] = []
        self._pattern_data: List[Dict[str, Any]] = []
        self._last_refresh: float = 0
        self._lock = Lock()
        self._refresh_task: Optional[asyncio.Task] = None
    
    def _compile_patterns(self, rules: List[Dict[str, Any]]) -> List[re.Pattern]:
        """
        Compile regex patterns from blacklist rules.
        
        Args:
            rules: List of blacklist rule dicts with "pattern" key
            
        Returns:
            List of compiled regex patterns
        """
        compiled = []
        for rule in rules:
            pattern_str = rule.get("pattern")
            if not pattern_str:
                continue
            try:
                compiled.append(re.compile(pattern_str, re.IGNORECASE))
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern_str}': {e}")
        return compiled
    
    async def refresh(self) -> None:
        """Fetch and update blacklist patterns from FastAPI."""
        try:
            rules = await fetch_blacklist(self.client)
            if rules:
                compiled = self._compile_patterns(rules)
                with self._lock:
                    self._patterns = compiled
                    self._pattern_data = rules
                    self._last_refresh = time.time()
                logger.info(f"Refreshed blacklist cache with {len(compiled)} patterns")
            else:
                logger.warning("Received empty blacklist from FastAPI")
        except Exception as e:
            logger.error(f"Error refreshing blacklist: {e}")
    
    def is_blacklisted(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Check if URL matches any blacklist pattern.
        
        Args:
            url: URL to check
            
        Returns:
            Tuple of (is_blacklisted, matching_pattern)
        """
        if not url:
            return False, None
        
        with self._lock:
            patterns = self._patterns.copy()
            pattern_data = self._pattern_data.copy()
        
        # Check against all patterns
        for i, pattern in enumerate(patterns):
            if pattern.search(url):
                matching_rule = pattern_data[i] if i < len(pattern_data) else None
                pattern_str = matching_rule.get("pattern") if matching_rule else str(pattern.pattern)
                return True, pattern_str
        
        return False, None
    
    def needs_refresh(self) -> bool:
        """Check if cache needs refresh based on TTL."""
        with self._lock:
            elapsed = time.time() - self._last_refresh
            return elapsed >= settings.blacklist_refresh_seconds
    
    async def ensure_fresh(self) -> None:
        """Ensure blacklist is fresh (non-blocking refresh if needed)."""
        if self.needs_refresh():
            # Start refresh in background (don't await)
            asyncio.create_task(self.refresh())
    
    async def start_auto_refresh(self) -> None:
        """Start background task to auto-refresh blacklist."""
        async def refresh_loop():
            while True:
                try:
                    await asyncio.sleep(settings.blacklist_refresh_seconds)
                    await self.refresh()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in blacklist refresh loop: {e}")
        
        self._refresh_task = asyncio.create_task(refresh_loop())
        logger.info("Started blacklist auto-refresh task")
    
    def stop_auto_refresh(self) -> None:
        """Stop auto-refresh task."""
        if self._refresh_task and not self._refresh_task.done():
            self._refresh_task.cancel()
            logger.info("Stopped blacklist auto-refresh task")

