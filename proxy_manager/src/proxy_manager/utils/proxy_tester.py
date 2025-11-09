"""Multi-threaded proxy tester using ThreadPoolExecutor and httpx async client."""

import asyncio
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional

import httpx

from ..models import Proxy, ProxyTestResult
from .config import settings

logger = logging.getLogger(__name__)


async def test_proxy_async(proxy: Proxy, timeout: float = 10.0) -> ProxyTestResult:
    """
    Test a single proxy asynchronously.

    Args:
        proxy: Proxy object to test
        timeout: Request timeout in seconds

    Returns:
        ProxyTestResult with test outcome
    """
    start_time = datetime.now()

    try:
        proxy_url = proxy.proxy_url
        proxies = {
            "http://": httpx.AsyncHTTPTransport(proxy=proxy_url),
            "https://": httpx.AsyncHTTPTransport(proxy=proxy_url),
        }

        async with httpx.AsyncClient(
            mounts=proxies, timeout=timeout, follow_redirects=True
        ) as client:
            response = await client.get(settings.test_url)
            elapsed = (
                datetime.now() - start_time
            ).total_seconds() * 1000  # Convert to milliseconds

            if response.status_code == 200:
                return ProxyTestResult(
                    proxy_id=proxy.id,
                    success=True,
                    latency=elapsed,
                    status_code=response.status_code,
                )
            else:
                return ProxyTestResult(
                    proxy_id=proxy.id,
                    success=False,
                    latency=elapsed,
                    status_code=response.status_code,
                    error=f"HTTP {response.status_code}",
                )

    except httpx.TimeoutException:
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return ProxyTestResult(
            proxy_id=proxy.id,
            success=False,
            latency=elapsed,
            error="Connection timeout",
        )

    except httpx.ProxyError as e:
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return ProxyTestResult(
            proxy_id=proxy.id,
            success=False,
            latency=elapsed,
            error=f"Proxy error: {str(e)}",
        )

    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Error testing proxy {proxy.id}: {str(e)}")
        traceback.print_exc()
        return ProxyTestResult(
            proxy_id=proxy.id,
            success=False,
            latency=elapsed,
            error=f"Unexpected error: {str(e)}",
        )


def test_proxy_sync(proxy: Proxy, timeout: float = 10.0) -> ProxyTestResult:
    """
    Wrapper to run async test_proxy_async in a thread.

    Args:
        proxy: Proxy object to test
        timeout: Request timeout in seconds

    Returns:
        ProxyTestResult with test outcome
    """
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(test_proxy_async(proxy, timeout))
    finally:
        loop.close()


class ProxyTester:
    """Multi-threaded proxy tester using ThreadPoolExecutor."""

    def __init__(self, max_workers: Optional[int] = None, timeout: float = 10.0):
        """
        Initialize the proxy tester.

        Args:
            max_workers: Maximum number of worker threads (defaults to settings.max_threads)
            timeout: Request timeout in seconds
        """
        self.max_workers = max_workers or settings.max_threads
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def test_proxy(self, proxy: Proxy) -> ProxyTestResult:
        """
        Test a single proxy using a worker thread.

        Args:
            proxy: Proxy object to test

        Returns:
            ProxyTestResult with test outcome
        """
        future = self.executor.submit(test_proxy_sync, proxy, self.timeout)
        return future.result()

    def test_proxies_batch(self, proxies: List[Proxy]) -> Dict[int, ProxyTestResult]:
        """
        Test multiple proxies concurrently.

        Args:
            proxies: List of Proxy objects to test

        Returns:
            Dictionary mapping proxy_id to ProxyTestResult
        """
        results = {}

        # Submit all proxy tests
        future_to_proxy = {
            self.executor.submit(test_proxy_sync, proxy, self.timeout): proxy
            for proxy in proxies
        }

        # Collect results as they complete
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                results[proxy.id] = result
                logger.debug(f"Proxy {proxy.id} test completed: {result.success}")
            except Exception as e:
                logger.error(f"Error testing proxy {proxy.id}: {str(e)}")
                traceback.print_exc()
                results[proxy.id] = ProxyTestResult(
                    proxy_id=proxy.id,
                    success=False,
                    error=f"Test execution error: {str(e)}",
                )

        return results

    def shutdown(self, wait: bool = True):
        """Shutdown the thread pool executor."""
        self.executor.shutdown(wait=wait)
