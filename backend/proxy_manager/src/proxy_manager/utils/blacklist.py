"""Blacklist URL checking using regex patterns."""

import re
from typing import List, Optional
from urllib.parse import urlparse
import logging

from ..models import Blacklist

logger = logging.getLogger(__name__)


class BlacklistChecker:
    """Check URLs against blacklist regex patterns."""
    
    def __init__(self):
        """Initialize blacklist checker."""
        self._compiled_patterns: List[re.Pattern] = []
        self._patterns: List[Blacklist] = []
    
    def load_patterns(self, blacklist_rules: List[Blacklist]):
        """
        Load and compile blacklist patterns.
        
        Args:
            blacklist_rules: List of Blacklist objects
        """
        self._patterns = blacklist_rules
        self._compiled_patterns = []
        
        for rule in blacklist_rules:
            try:
                compiled = re.compile(rule.pattern, re.IGNORECASE)
                self._compiled_patterns.append(compiled)
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{rule.pattern}': {e}")
    
    def is_blacklisted(self, url: str) -> bool:
        """
        Check if a URL matches any blacklist pattern.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is blacklisted, False otherwise
        """
        if not url:
            return False
        
        # Check against all compiled patterns
        for pattern in self._compiled_patterns:
            if pattern.search(url):
                return True
        
        return False
    
    def check_url(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Check URL and return blacklist status with matching pattern.
        
        Args:
            url: URL to check
            
        Returns:
            Tuple of (is_blacklisted, matching_pattern)
        """
        if not url:
            return False, None
        
        # Extract hostname and full URL for matching
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc or parsed.path.split('/')[0]
            full_url = url
        except Exception as e:
            logger.warning(f"Error parsing URL '{url}': {e}")
            hostname = url
            full_url = url
        
        # Check both hostname and full URL
        for i, pattern in enumerate(self._compiled_patterns):
            if pattern.search(full_url) or pattern.search(hostname):
                matching_rule = self._patterns[i]
                return True, matching_rule.pattern
        
        return False, None


# Global blacklist checker instance
blacklist_checker = BlacklistChecker()

