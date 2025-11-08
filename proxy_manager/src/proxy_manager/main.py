"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_and_tables
from .routers import proxy_routes, health_routes, auth_routes, admin_routes, blacklist_routes, log_routes
from .scheduler import health_check_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    - Startup: Initialize database tables and start health check scheduler
    - Shutdown: Stop health check scheduler
    """
    # Startup
    logger.info("Starting Proxy Manager application")
    create_db_and_tables()
    logger.info("Database tables initialized")
    
    health_check_scheduler.start()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Proxy Manager application")
    health_check_scheduler.stop(wait=True)
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Multi-Threaded Rotating Proxy Manager",
    description="A production-ready FastAPI application for managing and rotating HTTP/HTTPS proxies",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(proxy_routes.proxies_router)
app.include_router(proxy_routes.proxy_router)
app.include_router(health_routes.router)
app.include_router(blacklist_routes.router)
app.include_router(log_routes.router)
app.include_router(log_routes.activity_router)  # POST /activity endpoint
app.include_router(admin_routes.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Multi-Threaded Rotating Proxy Manager API",
        "docs": "/docs",
        "health": "/health"
    }

