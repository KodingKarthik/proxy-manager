"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Dict

from ..database import get_session
from ..models import Proxy

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Application health status."""

    status: str
    message: str


class ProxyStatsResponse(BaseModel):
    """Proxy pool statistics."""

    total: int
    working: int
    dead: int
    statistics: dict[str, float]


@router.get("", response_model=HealthResponse)
def health_check():
    """
    Application health check endpoint.

    Returns:
        Health status
    """
    return HealthResponse(status="healthy", message="Proxy manager is running")


@router.get("/proxies", response_model=ProxyStatsResponse)
def proxy_pool_statistics(session: Session = Depends(get_session)):
    """
    Get proxy pool statistics.

    Args:
        session: Database session

    Returns:
        Proxy pool statistics
    """
    # Get all proxies
    statement = select(Proxy)
    all_proxies = list(session.exec(statement).all())

    total = len(all_proxies)
    working = sum(1 for p in all_proxies if p.is_working)
    dead = total - working

    # Calculate additional statistics
    proxies_with_latency = [p for p in all_proxies if p.latency is not None]
    avg_latency = (
        sum(p.latency if p.latency else 0 for p in proxies_with_latency)
        / len(proxies_with_latency)
        if proxies_with_latency
        else None
    )

    stats = {
        "total": total,
        "working": working,
        "dead": dead,
    }

    if avg_latency is not None:
        stats["average_latency_ms"] = round(avg_latency, 2)

    if proxies_with_latency:
        min_latency = min(p.latency for p in proxies_with_latency)
        max_latency = max(p.latency for p in proxies_with_latency)
        stats["min_latency_ms"] = round(min_latency, 2)
        stats["max_latency_ms"] = round(max_latency, 2)

    return ProxyStatsResponse(total=total, working=working, dead=dead, statistics=stats)
