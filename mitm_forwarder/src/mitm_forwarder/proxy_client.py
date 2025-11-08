"""FastAPI client for proxy, blacklist, and activity endpoints."""

import httpx
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)


async def get_proxy(
    client: httpx.AsyncClient,
    target_url: Optional[str] = None,
    user_jwt: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get an upstream proxy from FastAPI backend.
    
    Args:
        client: httpx async client
        target_url: Optional target URL for blacklist checking
        user_jwt: User JWT token from client Authorization header (required)
        
    Returns:
        Dict with proxy info: {"proxy": str, "proxy_id": int, "user_id": int}
        Returns None if no proxy available or error occurred
    """
    if not user_jwt:
        logger.error("User JWT is required for proxy endpoint")
        return None
    
    url = f"{settings.fastapi_base_url}{settings.fastapi_proxy_endpoint}"
    headers = {
        "Authorization": user_jwt  # Send user JWT in Authorization header
    }
    
    params = {}
    if target_url:
        params["target_url"] = target_url
    
    try:
        response = await client.get(url, headers=headers, params=params, timeout=settings.httpx_timeout)
        
        if response.status_code == 200:
            data = response.json()
            # Map FastAPI response to expected format
            # FastAPI returns ProxyResponse with address field (ip:port)
            proxy_address = data.get("address") or f"{data.get('ip')}:{data.get('port')}"
            protocol = data.get("protocol", "http")
            username = data.get("username")
            password = data.get("password")
            
            # Build full proxy URL with auth if available
            if username and password:
                proxy_url = f"{protocol}://{username}:{password}@{proxy_address}"
            else:
                proxy_url = f"{protocol}://{proxy_address}"
            
            return {
                "proxy": proxy_url,
                "proxy_id": data.get("id"),
                "user_id": None  # FastAPI doesn't return user_id in proxy response
            }
        elif response.status_code == 403:
            logger.warning(f"Request blacklisted: {target_url}")
            return None
        elif response.status_code == 404:
            logger.warning("No working proxies available")
            return None
        else:
            logger.error(f"Unexpected status code from proxy endpoint: {response.status_code}")
            return None
    
    except httpx.TimeoutException:
        logger.error("Timeout while fetching proxy from FastAPI")
        return None
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching proxy: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching proxy: {e}")
        return None


async def fetch_blacklist(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """
    Fetch blacklist rules from FastAPI backend.
    
    Args:
        client: httpx async client
        
    Returns:
        List of blacklist rules: [{"id": int, "pattern": str, ...}, ...]
        Returns empty list on error
    """
    url = f"{settings.fastapi_base_url}{settings.fastapi_blacklist_endpoint}"
    headers = {
        "Authorization": f"Bearer {settings.system_token}"
    }
    
    try:
        response = await client.get(url, headers=headers, timeout=settings.httpx_timeout)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Unexpected status code from blacklist endpoint: {response.status_code}")
            return []
    
    except httpx.TimeoutException:
        logger.error("Timeout while fetching blacklist from FastAPI")
        return []
    except httpx.RequestError as e:
        logger.error(f"Request error while fetching blacklist: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching blacklist: {e}")
        return []


async def post_activity(
    client: httpx.AsyncClient,
    user_id: Optional[int],
    endpoint: str,
    method: str,
    status_code: int,
    target_url: Optional[str] = None,
    proxy_id: Optional[int] = None
) -> None:
    """
    Post activity log to FastAPI backend (fire-and-forget).
    
    Args:
        client: httpx async client
        user_id: User ID (may be None)
        endpoint: Request endpoint/URL
        method: HTTP method
        status_code: HTTP status code
        target_url: Target URL (same as endpoint typically)
        proxy_id: Proxy ID used (may be None)
    """
    url = f"{settings.fastapi_base_url}{settings.fastapi_activity_endpoint}"
    headers = {
        "Authorization": f"Bearer {settings.system_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "user_id": user_id,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "target_url": target_url or endpoint,
        "proxy_id": proxy_id,
        "timestamp": datetime.utcnow().timestamp()
    }
    
    try:
        # Fire-and-forget: don't wait for response
        await client.post(
            url,
            headers=headers,
            json=payload,
            timeout=settings.httpx_timeout
        )
    except Exception as e:
        # Log but don't raise - activity logging should never block
        logger.debug(f"Failed to post activity log (non-critical): {e}")

