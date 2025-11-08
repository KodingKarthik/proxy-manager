"""mitmproxy addon for forwarding requests through FastAPI-managed proxies."""

import asyncio
import httpx
import logging
from typing import Optional
from mitmproxy import http

from .config import settings
from .proxy_client import get_proxy, post_activity
from .blacklist_cache import BlacklistCache
from .logger import logger

# Global state
blacklist_cache: Optional[BlacklistCache] = None
http_client: Optional[httpx.AsyncClient] = None
semaphore: Optional[asyncio.Semaphore] = None


# Hop-by-hop headers that should not be forwarded
HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate",
    "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
}


def load(loader):
    """Called when addon is loaded."""
    global blacklist_cache, http_client, semaphore
    
    # Create HTTP client
    http_client = httpx.AsyncClient(
        timeout=settings.httpx_timeout,
        verify=True  # Verify SSL certificates
    )
    
    # Create blacklist cache
    blacklist_cache = BlacklistCache(http_client)
    
    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
    
    # Initial blacklist fetch
    asyncio.create_task(blacklist_cache.refresh())
    
    # Start auto-refresh
    asyncio.create_task(blacklist_cache.start_auto_refresh())
    
    logger.info("mitmproxy forwarder addon loaded")


def done():
    """Called when addon is unloaded."""
    global blacklist_cache, http_client
    
    if blacklist_cache:
        blacklist_cache.stop_auto_refresh()
    
    if http_client:
        asyncio.create_task(http_client.aclose())
    
    logger.info("mitmproxy forwarder addon unloaded")


async def request(flow: http.HTTPFlow) -> None:
    """
    Handle incoming HTTP request.
    
    Args:
        flow: mitmproxy HTTP flow
    """
    if not http_client or not blacklist_cache:
        logger.error("Addon not properly initialized")
        flow.response = http.Response.make(500, b"Internal Server Error")
        return
    
    # Extract client authorization header
    client_auth = flow.request.headers.get("Authorization")
    user_jwt = client_auth if client_auth else settings.default_user_jwt
    
    # Check if user JWT is required
    if not user_jwt and settings.require_user_jwt:
        logger.warning("Request rejected: No Authorization header provided and REQUIRE_USER_JWT is True")
        flow.response = http.Response.make(
            401,
            b"Unauthorized: Authorization header with JWT token is required",
            {"Content-Type": "text/plain", "WWW-Authenticate": "Bearer"}
        )
        
        # Log activity (fire-and-forget)
        asyncio.create_task(post_activity(
            http_client,
            user_id=None,
            endpoint=flow.request.pretty_url,
            method=flow.request.method,
            status_code=401,
            target_url=flow.request.pretty_url,
            proxy_id=None
        ))
        return
    
    # Get target URL
    target_url = flow.request.pretty_url
    
    # Ensure blacklist is fresh (non-blocking)
    await blacklist_cache.ensure_fresh()
    
    # Check blacklist
    is_blacklisted, matching_pattern = blacklist_cache.is_blacklisted(target_url)
    if is_blacklisted:
        logger.warning(f"Request blacklisted: {target_url} (pattern: {matching_pattern})")
        flow.response = http.Response.make(
            403,
            b"Forbidden: URL matches blacklist pattern",
            {"Content-Type": "text/plain"}
        )
        
        # Log activity (fire-and-forget)
        asyncio.create_task(post_activity(
            http_client,
            user_id=None,  # Will be extracted from JWT by FastAPI if needed
            endpoint=target_url,
            method=flow.request.method,
            status_code=403,
            target_url=target_url,
            proxy_id=None
        ))
        return
    
    # Acquire semaphore for rate limiting
    async with semaphore:
        # Get upstream proxy from FastAPI
        proxy_info = await get_proxy(
            http_client,
            target_url=target_url,
            user_jwt=user_jwt
        )
        
        if not proxy_info:
            logger.error("No upstream proxy available")
            flow.response = http.Response.make(
                502,
                b"Bad Gateway: No upstream proxy available",
                {"Content-Type": "text/plain"}
            )
            
            # Log activity
            asyncio.create_task(post_activity(
                http_client,
                user_id=None,
                endpoint=target_url,
                method=flow.request.method,
                status_code=502,
                target_url=target_url,
                proxy_id=None
            ))
            return
        
        proxy_url = proxy_info.get("proxy")
        proxy_id = proxy_info.get("proxy_id")
        user_id = proxy_info.get("user_id")
        
        logger.debug(f"Using proxy: {proxy_url} (proxy_id: {proxy_id})")
        
        # Prepare request for upstream
        try:
            # Build request headers (exclude hop-by-hop headers)
            upstream_headers = {}
            for key, value in flow.request.headers.items():
                if key.lower() not in HOP_BY_HOP_HEADERS:
                    upstream_headers[key] = value
            
            # Prepare request body
            body = flow.request.content if flow.request.content else None
            
            # Make request through upstream proxy
            proxies = {
                "http://": proxy_url,
                "https://": proxy_url
            }
            
            async with httpx.AsyncClient(
                proxies=proxies,
                timeout=settings.httpx_timeout,
                follow_redirects=False  # Let mitmproxy handle redirects
            ) as proxy_client:
                try:
                    response = await proxy_client.request(
                        method=flow.request.method,
                        url=target_url,
                        headers=upstream_headers,
                        content=body,
                        stream=True
                    )
                    
                    # Read response
                    response_body = b""
                    async for chunk in response.aiter_bytes():
                        response_body += chunk
                    
                    # Build mitmproxy response
                    # Filter hop-by-hop headers
                    response_headers = {}
                    for key, value in response.headers.items():
                        if key.lower() not in HOP_BY_HOP_HEADERS:
                            response_headers[key] = value
                    
                    flow.response = http.Response.make(
                        response.status_code,
                        response_body,
                        response_headers
                    )
                    
                    # Log activity (fire-and-forget)
                    asyncio.create_task(post_activity(
                        http_client,
                        user_id=user_id,
                        endpoint=target_url,
                        method=flow.request.method,
                        status_code=response.status_code,
                        target_url=target_url,
                        proxy_id=proxy_id
                    ))
                    
                except httpx.TimeoutException:
                    logger.error(f"Timeout while forwarding request to {target_url}")
                    flow.response = http.Response.make(
                        504,
                        b"Gateway Timeout",
                        {"Content-Type": "text/plain"}
                    )
                    
                    asyncio.create_task(post_activity(
                        http_client,
                        user_id=user_id,
                        endpoint=target_url,
                        method=flow.request.method,
                        status_code=504,
                        target_url=target_url,
                        proxy_id=proxy_id
                    ))
                    
                except httpx.ProxyError as e:
                    logger.error(f"Proxy error: {e}")
                    flow.response = http.Response.make(
                        502,
                        b"Bad Gateway: Proxy error",
                        {"Content-Type": "text/plain"}
                    )
                    
                    asyncio.create_task(post_activity(
                        http_client,
                        user_id=user_id,
                        endpoint=target_url,
                        method=flow.request.method,
                        status_code=502,
                        target_url=target_url,
                        proxy_id=proxy_id
                    ))
                    
                except Exception as e:
                    logger.error(f"Unexpected error while forwarding request: {e}")
                    flow.response = http.Response.make(
                        502,
                        b"Bad Gateway: Internal error",
                        {"Content-Type": "text/plain"}
                    )
                    
                    asyncio.create_task(post_activity(
                        http_client,
                        user_id=user_id,
                        endpoint=target_url,
                        method=flow.request.method,
                        status_code=502,
                        target_url=target_url,
                        proxy_id=proxy_id
                    ))
        
        except Exception as e:
            logger.error(f"Error preparing request: {e}")
            flow.response = http.Response.make(
                500,
                b"Internal Server Error",
                {"Content-Type": "text/plain"}
            )

