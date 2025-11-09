import asyncio
import httpx
from mitmproxy import http
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from .config import settings
from .proxy_client import get_proxy, post_activity
from .blacklist_cache import BlacklistCache
from .logger import logger


class ForwarderAddon:
    HOP_BY_HOP_HEADERS: set[str] = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }

    def __init__(self) -> None:
        self.http_client: httpx.AsyncClient = httpx.AsyncClient(
            timeout=settings.httpx_timeout, verify=True
        )
        self.blacklist_cache: BlacklistCache = BlacklistCache(self.http_client)
        # Semaphore for rate limiting
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(
            settings.max_concurrent_requests
        )

    async def running(self):
        # Initial blacklist fetch
        _ = asyncio.create_task(self.blacklist_cache.refresh())
        _ = asyncio.create_task(self.blacklist_cache.start_auto_refresh())

        logger.info("mitmproxy forwarder addon loaded")

    async def done(self):
        """Called when addon is unloaded."""
        self.blacklist_cache.stop_auto_refresh()
        _ = asyncio.create_task(self.http_client.aclose())

        logger.info("mitmproxy forwarder addon unloaded")

    async def _forward_request_with_proxy(
        self,
        flow: http.HTTPFlow,
        target_url: str,
        user_jwt: str,
        strategy: str,
    ) -> tuple[bool, dict | None]:
        """
        Forward request through a proxy using the specified strategy.

        Args:
            flow: mitmproxy HTTP flow
            target_url: Target URL to forward
            user_jwt: User JWT token
            strategy: Rotation strategy to use

        Returns:
            Tuple of (success: bool, proxy_info: dict | None)
            On success, returns (True, proxy_info)
            On failure, returns (False, proxy_info) where proxy_info may be None
        """
        # Get proxy with specified strategy
        proxy_info = await get_proxy(
            self.http_client, target_url=target_url, user_jwt=user_jwt, strategy=strategy
        )

        if not proxy_info:
            logger.warning(f"No proxy available with strategy: {strategy}")
            return (False, None)

        proxy_url = proxy_info.get("proxy")
        proxy_id = proxy_info.get("proxy_id")
        user_id = proxy_info.get("user_id")

        logger.debug(f"Using proxy: {proxy_url} (proxy_id: {proxy_id}, strategy: {strategy})")

        try:
            # Build request headers (exclude hop-by-hop headers)
            upstream_headers = {}
            for key, value in flow.request.headers.items():
                if key.lower() not in self.HOP_BY_HOP_HEADERS:
                    upstream_headers[key] = value

            # Prepare request body
            body = flow.request.content if flow.request.content else None

            # Make request through upstream proxy
            proxies = {
                "http://": httpx.AsyncHTTPTransport(proxy=proxy_url),
                "https://": httpx.AsyncHTTPTransport(proxy=proxy_url),
            }

            async with httpx.AsyncClient(
                mounts=proxies,
                timeout=settings.httpx_timeout,
                follow_redirects=False,  # Let mitmproxy handle redirects
            ) as proxy_client:
                response = await proxy_client.request(
                    method=flow.request.method,
                    url=target_url,
                    headers=upstream_headers,
                    content=body,
                )

                # Read response
                response_body = b""
                async for chunk in response.aiter_bytes():
                    response_body += chunk

                # Build mitmproxy response
                # Filter hop-by-hop headers
                response_headers = {}
                for key, value in response.headers.items():
                    if key.lower() not in self.HOP_BY_HOP_HEADERS:
                        response_headers[key] = value

                flow.response = http.Response.make(
                    response.status_code, response_body, response_headers
                )

                # Log activity (fire-and-forget)
                _ = asyncio.create_task(
                    post_activity(
                        self.http_client,
                        user_id=int(user_id) if user_id else None,
                        endpoint=target_url,
                        method=flow.request.method,
                        status_code=response.status_code,
                        target_url=target_url,
                        proxy_id=int(proxy_id) if proxy_id else None,
                    )
                )

                return (True, proxy_info)

        except (httpx.ProxyError, httpx.TimeoutException, httpx.RequestError) as e:
            # Connection errors - these are retryable
            logger.warning(
                f"Connection error with proxy {proxy_url} (strategy: {strategy}): {e}"
            )
            return (False, proxy_info)
        except Exception as e:
            # Other errors - log but don't retry
            logger.error(f"Unexpected error while forwarding request: {e}")
            return (False, proxy_info)

    async def request(self, flow: http.HTTPFlow) -> None:
        """
        Handle incoming HTTP request.

        Args:
            flow: mitmproxy HTTP flow
        """
        if not self.http_client or not self.blacklist_cache:
            logger.error("Addon not properly initialized")
            flow.response = http.Response.make(500, b"Internal Server Error")
            return

        # Extract client authorization header
        client_auth: str | None = flow.request.headers.get("Authorization")
        user_jwt = client_auth if client_auth else settings.default_user_jwt

        if not user_jwt and settings.require_user_jwt:
            logger.warning(
                "Request rejected: No Authorization header provided and REQUIRE_USER_JWT is True"
            )
            flow.response = http.Response.make(
                401,
                b"Unauthorized: Authorization header with JWT token is required",
                {"Content-Type": "text/plain", "WWW-Authenticate": "Bearer"},
            )

            # Log activity (fire-and-forget)
            _ = asyncio.create_task(
                post_activity(
                    self.http_client,
                    user_id=None,
                    endpoint=flow.request.pretty_url,
                    method=flow.request.method,
                    status_code=401,
                    target_url=flow.request.pretty_url,
                    proxy_id=None,
                )
            )
            return

        target_url = flow.request.pretty_url

        await self.blacklist_cache.ensure_fresh()

        # Check blacklist
        is_blacklisted, matching_pattern = self.blacklist_cache.is_blacklisted(
            target_url
        )
        if is_blacklisted:
            logger.warning(
                f"Request blacklisted: {target_url} (pattern: {matching_pattern})"
            )
            flow.response = http.Response.make(
                403,
                b"Forbidden: URL matches blacklist pattern",
                {"Content-Type": "text/plain"},
            )

            # Log activity (fire-and-forget)
            _ = asyncio.create_task(
                post_activity(
                    self.http_client,
                    user_id=None,  # Will be extracted from JWT by FastAPI if needed
                    endpoint=target_url,
                    method=flow.request.method,
                    status_code=403,
                    target_url=target_url,
                    proxy_id=None,
                )
            )
            return

        # Acquire semaphore for rate limiting
        async with self.semaphore:
            # Try with configured rotation strategy first
            strategy = settings.rotation_strategy
            retry_count = settings.retry_count
            fallback_strategy = settings.fallback_strategy

            # Attempt with primary strategy (initial attempt + retries)
            success = False
            last_proxy_info = None
            for attempt in range(retry_count + 1):  # +1 for initial attempt
                if attempt > 0:
                    logger.info(
                        f"Retry attempt {attempt}/{retry_count} with strategy: {strategy}"
                    )

                success, proxy_info = await self._forward_request_with_proxy(
                    flow, target_url, user_jwt, strategy
                )

                if success:
                    logger.debug(
                        f"Request succeeded on attempt {attempt + 1} with strategy: {strategy}"
                    )
                    return

                last_proxy_info = proxy_info
                if proxy_info is None:
                    # No proxy available with this strategy, try fallback immediately
                    logger.warning(
                        f"No proxy available with strategy: {strategy}, trying fallback"
                    )
                    break

            # If all retries failed, try fallback strategy
            if not success and fallback_strategy != strategy:
                logger.info(
                    f"All attempts with strategy '{strategy}' failed, trying fallback strategy: {fallback_strategy}"
                )
                success, proxy_info = await self._forward_request_with_proxy(
                    flow, target_url, user_jwt, fallback_strategy
                )

                if success:
                    logger.debug(f"Request succeeded with fallback strategy: {fallback_strategy}")
                    return

                last_proxy_info = proxy_info

            # All attempts failed - return error response
            proxy_id = last_proxy_info.get("proxy_id") if last_proxy_info else None
            user_id = last_proxy_info.get("user_id") if last_proxy_info else None

            logger.error(
                f"All proxy attempts failed for {target_url} (tried {strategy} with {retry_count} retries, then {fallback_strategy})"
            )
            flow.response = http.Response.make(
                502,
                b"Bad Gateway: All proxy attempts failed",
                {"Content-Type": "text/plain"},
            )

            # Log activity
            _ = asyncio.create_task(
                post_activity(
                    self.http_client,
                    user_id=int(user_id) if user_id else None,
                    endpoint=target_url,
                    method=flow.request.method,
                    status_code=502,
                    target_url=target_url,
                    proxy_id=int(proxy_id) if proxy_id else None,
                )
            )


if __name__ == "__main__":
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    opts = Options(listen_port=settings.mitm_listen_port)
    mitmproxy_master = DumpMaster(
        opts, loop=loop, with_termlog=False, with_dumper=False
    )

    # Add the firewall addon
    forwarder_addon = ForwarderAddon()
    mitmproxy_master.addons.add(forwarder_addon)

    logger.info(f"Starting mitmproxy on port {settings.mitm_listen_port}")
    # Run the async run() method in the event loop
    loop.run_until_complete(mitmproxy_master.run())
