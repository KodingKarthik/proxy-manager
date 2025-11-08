"""APScheduler-based health check scheduler."""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session

from .database import engine
from .crud import get_all_proxies, update_proxy_after_test
from .utils.proxy_tester import ProxyTester
from .utils.config import settings

logger = logging.getLogger(__name__)


class HealthCheckScheduler:
    """Manages periodic health checks for proxies."""
    
    def __init__(self):
        """Initialize the health check scheduler."""
        self.scheduler = BackgroundScheduler()
        self.proxy_tester = ProxyTester()
        self.is_running = False
    
    def health_check_job(self):
        """
        Job function that tests all proxies and updates their status.
        This runs in a background thread.
        """
        logger.info("Starting scheduled health check for all proxies")
        
        try:
            # Create a new session for this job
            with Session(engine) as session:
                # Get all proxies
                proxies = get_all_proxies(session, working_only=False, limit=10000)
                
                if not proxies:
                    logger.info("No proxies to check")
                    return
                
                logger.info(f"Testing {len(proxies)} proxies")
                
                # Test all proxies concurrently
                results = self.proxy_tester.test_proxies_batch(proxies)
                
                # Update proxy statuses
                updated_count = 0
                working_count = 0
                
                for proxy in proxies:
                    if proxy.id in results:
                        result = results[proxy.id]
                        update_proxy_after_test(
                            session,
                            proxy,
                            result.success,
                            result.latency
                        )
                        updated_count += 1
                        if result.success:
                            working_count += 1
                
                logger.info(
                    f"Health check completed: {updated_count} proxies tested, "
                    f"{working_count} working, {updated_count - working_count} failed"
                )
        
        except Exception as e:
            logger.error(f"Error during health check: {str(e)}", exc_info=True)
    
    def start(self):
        """Start the health check scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Add the health check job
        self.scheduler.add_job(
            func=self.health_check_job,
            trigger=IntervalTrigger(seconds=settings.check_interval),
            id="health_check",
            name="Proxy Health Check",
            replace_existing=True
        )
        
        # Start the scheduler
        self.scheduler.start()
        self.is_running = True
        logger.info(
            f"Health check scheduler started with interval: {settings.check_interval} seconds"
        )
    
    def stop(self, wait: bool = True):
        """Stop the health check scheduler."""
        if not self.is_running:
            return
        
        self.scheduler.shutdown(wait=wait)
        self.is_running = False
        self.proxy_tester.shutdown(wait=wait)
        logger.info("Health check scheduler stopped")


# Global scheduler instance
health_check_scheduler = HealthCheckScheduler()

