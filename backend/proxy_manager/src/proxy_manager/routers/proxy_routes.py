"""Proxy management and rotation API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import Session
from typing import List, Optional, Literal

from ..database import get_session
from ..models import Proxy, ProxyCreate, ProxyResponse, ProxyTestResult, User
from ..crud import (
    create_proxy,
    get_proxy,
    get_all_proxies,
    delete_proxy,
    update_proxy_after_test,
)
from ..utils.rotation import rotation_manager
from ..utils.proxy_tester import ProxyTester
from ..utils.config import settings
from ..auth import get_current_user, get_current_user_or_service
from ..utils.logger import log_activity, get_client_ip
from ..utils.blacklist import blacklist_checker
from ..routers.rate_limit import check_rate_limit
from ..crud import get_all_blacklist_rules

# Router for /proxies endpoints
proxies_router = APIRouter(prefix="/proxies", tags=["proxies"])

# Router for /proxy endpoints
proxy_router = APIRouter(prefix="/proxy", tags=["proxy"])

# Global proxy tester instance
proxy_tester = ProxyTester()


@proxies_router.post("", response_model=ProxyResponse, status_code=201)
def add_proxy(
    proxy_data: ProxyCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Add a new proxy to the pool.

    Args:
        proxy_data: Proxy creation data (ip, port, protocol, username, password)
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session

    Returns:
        Created proxy
    """
    check_rate_limit(current_user)

    # Check if proxy already exists
    existing = get_all_proxies(session, working_only=False, limit=1000)
    for p in existing:
        if (
            p.ip == proxy_data.ip
            and p.port == proxy_data.port
            and (proxy_data.username is None or p.username == proxy_data.username)
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Proxy {proxy_data.ip}:{proxy_data.port} already exists",
            )

    proxy = Proxy(
        ip=proxy_data.ip,
        port=proxy_data.port,
        protocol=proxy_data.protocol,
        username=proxy_data.username,
        password=proxy_data.password,
    )

    created_proxy = create_proxy(session, proxy)

    # Log activity
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=current_user,
        endpoint="/proxies",
        method="POST",
        status_code=201,
        ip_address=ip_address,
    )

    health_score = created_proxy.calculate_health_score()

    return ProxyResponse(
        id=created_proxy.id,
        ip=created_proxy.ip,
        port=created_proxy.port,
        username=created_proxy.username,
        latency=created_proxy.latency,
        last_checked=created_proxy.last_checked,
        is_working=created_proxy.is_working,
        fail_count=created_proxy.fail_count,
        last_used=created_proxy.last_used,
        address=created_proxy.address,
        health_score=health_score,
        protocol=created_proxy.protocol,
    )


@proxies_router.get("", response_model=List[ProxyResponse])
def list_proxies(
    working_only: bool = Query(
        default=False, description="Filter to working proxies only"
    ),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of proxies to return"
    ),
    offset: int = Query(default=0, ge=0, description="Number of proxies to skip"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    List all proxies with optional filtering.

    Args:
        working_only: If True, only return working proxies
        limit: Maximum number of proxies to return
        offset: Number of proxies to skip
        current_user: Current authenticated user
        session: Database session

    Returns:
        List of proxies
    """
    check_rate_limit(current_user)

    proxies = get_all_proxies(
        session, working_only=working_only, limit=limit, offset=offset
    )
    return [
        ProxyResponse(
            id=p.id,
            ip=p.ip,
            port=p.port,
            username=p.username,
            latency=p.latency,
            last_checked=p.last_checked,
            is_working=p.is_working,
            fail_count=p.fail_count,
            last_used=p.last_used,
            address=p.address,
            health_score=p.calculate_health_score(),
            protocol=p.protocol,
        )
        for p in proxies
    ]


@proxies_router.delete("/{proxy_id}", status_code=204)
def delete_proxy_by_id(
    proxy_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a proxy by ID.

    Args:
        proxy_id: ID of the proxy to delete
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session
    """
    check_rate_limit(current_user)

    success = delete_proxy(session, proxy_id)
    if not success:
        raise HTTPException(
            status_code=404, detail=f"Proxy with ID {proxy_id} not found"
        )

    # Log activity
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=current_user,
        endpoint=f"/proxies/{proxy_id}",
        method="DELETE",
        status_code=204,
        ip_address=ip_address,
    )


@proxies_router.post("/{proxy_id}/test", response_model=ProxyTestResult)
def test_proxy_by_id(
    proxy_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Manually test a specific proxy.

    Args:
        proxy_id: ID of the proxy to test
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session

    Returns:
        Test result
    """
    check_rate_limit(current_user)

    proxy = get_proxy(session, proxy_id)
    if not proxy:
        raise HTTPException(
            status_code=404, detail=f"Proxy with ID {proxy_id} not found"
        )

    result = proxy_tester.test_proxy(proxy)

    # Update proxy status in database
    update_proxy_after_test(session, proxy, result.success, result.latency)

    # Log activity
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=current_user,
        endpoint=f"/proxies/{proxy_id}/test",
        method="POST",
        status_code=200,
        ip_address=ip_address,
    )

    return result


@proxy_router.get("", response_model=ProxyResponse)
def get_proxy_by_strategy(
    request: Request,
    strategy: Literal["random", "round_robin", "lru", "best", "health_score"] = Query(
        default=None,
        description="Rotation strategy: random, round_robin, lru, best (lowest latency), health_score (best health)",
    ),
    target_url: Optional[str] = Query(
        None, description="Target URL to check against blacklist"
    ),
    current_user: User = Depends(get_current_user_or_service),
    session: Session = Depends(get_session),
):
    """
    Get a proxy using the specified rotation strategy.

    Args:
        strategy: Rotation strategy (defaults to configured strategy)
        target_url: Optional target URL to check against blacklist
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session

    Returns:
        Selected proxy
    """
    check_rate_limit(current_user)

    # Check blacklist if target_url is provided and blacklist is enabled
    if target_url and settings.blacklist_enabled:
        # Load blacklist rules
        blacklist_rules = get_all_blacklist_rules(session)
        blacklist_checker.load_patterns(blacklist_rules)

        is_blacklisted, matching_pattern = blacklist_checker.check_url(target_url)
        if is_blacklisted:
            raise HTTPException(
                status_code=403,
                detail=f"Blacklisted domain: URL matches pattern '{matching_pattern}'",
            )

    selected_strategy = strategy or settings.rotation_strategy
    proxy = rotation_manager.get_proxy(session, selected_strategy)

    if not proxy:
        raise HTTPException(status_code=404, detail="No working proxies available")

    # Log activity
    ip_address = get_client_ip(request) if request else None
    log_activity(
        session=session,
        user=current_user,
        endpoint="/proxy",
        method="GET",
        status_code=200,
        target_url=target_url,
        ip_address=ip_address,
    )

    health_score = proxy.calculate_health_score()

    return ProxyResponse(
        id=proxy.id,
        ip=proxy.ip,
        port=proxy.port,
        username=proxy.username,
        latency=proxy.latency,
        last_checked=proxy.last_checked,
        is_working=proxy.is_working,
        fail_count=proxy.fail_count,
        last_used=proxy.last_used,
        address=proxy.address,
        health_score=health_score,
        protocol=proxy.protocol,
    )


@proxy_router.get("/next", response_model=ProxyResponse)
def get_next_proxy(
    request: Request,
    target_url: Optional[str] = Query(
        None, description="Target URL to check against blacklist"
    ),
    current_user: User = Depends(get_current_user_or_service),
    session: Session = Depends(get_session),
):
    """
    Get the next proxy using round-robin strategy.

    Args:
        target_url: Optional target URL to check against blacklist
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session

    Returns:
        Next proxy in round-robin order
    """
    check_rate_limit(current_user)

    # Check blacklist if target_url is provided
    if target_url and settings.blacklist_enabled:
        blacklist_rules = get_all_blacklist_rules(session)
        blacklist_checker.load_patterns(blacklist_rules)
        is_blacklisted, matching_pattern = blacklist_checker.check_url(target_url)
        if is_blacklisted:
            raise HTTPException(
                status_code=403,
                detail=f"Blacklisted domain: URL matches pattern '{matching_pattern}'",
            )

    proxy = rotation_manager.get_proxy(session, "round_robin")

    if not proxy:
        raise HTTPException(status_code=404, detail="No working proxies available")

    # Log activity
    ip_address = get_client_ip(request) if request else None
    log_activity(
        session=session,
        user=current_user,
        endpoint="/proxy/next",
        method="GET",
        status_code=200,
        target_url=target_url,
        ip_address=ip_address,
    )

    health_score = proxy.calculate_health_score()

    return ProxyResponse(
        id=proxy.id,
        ip=proxy.ip,
        port=proxy.port,
        username=proxy.username,
        latency=proxy.latency,
        last_checked=proxy.last_checked,
        is_working=proxy.is_working,
        fail_count=proxy.fail_count,
        last_used=proxy.last_used,
        address=proxy.address,
        health_score=health_score,
        protocol=proxy.protocol,
    )


@proxy_router.get("/random", response_model=ProxyResponse)
def get_random_proxy(
    request: Request,
    target_url: Optional[str] = Query(
        None, description="Target URL to check against blacklist"
    ),
    current_user: User = Depends(get_current_user_or_service),
    session: Session = Depends(get_session),
):
    """
    Get a random working proxy.

    Args:
        target_url: Optional target URL to check against blacklist
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session

    Returns:
        Random proxy
    """
    check_rate_limit(current_user)

    # Check blacklist if target_url is provided
    if target_url and settings.blacklist_enabled:
        blacklist_rules = get_all_blacklist_rules(session)
        blacklist_checker.load_patterns(blacklist_rules)
        is_blacklisted, matching_pattern = blacklist_checker.check_url(target_url)
        if is_blacklisted:
            raise HTTPException(
                status_code=403,
                detail=f"Blacklisted domain: URL matches pattern '{matching_pattern}'",
            )

    proxy = rotation_manager.get_proxy(session, "random")

    if not proxy:
        raise HTTPException(status_code=404, detail="No working proxies available")

    # Log activity
    ip_address = get_client_ip(request) if request else None
    log_activity(
        session=session,
        user=current_user,
        endpoint="/proxy/random",
        method="GET",
        status_code=200,
        target_url=target_url,
        ip_address=ip_address,
    )

    health_score = proxy.calculate_health_score()

    return ProxyResponse(
        id=proxy.id,
        ip=proxy.ip,
        port=proxy.port,
        username=proxy.username,
        latency=proxy.latency,
        last_checked=proxy.last_checked,
        is_working=proxy.is_working,
        fail_count=proxy.fail_count,
        last_used=proxy.last_used,
        address=proxy.address,
        health_score=health_score,
        protocol=proxy.protocol,
    )


@proxy_router.get("/best", response_model=ProxyResponse)
def get_best_proxy(session: Session = Depends(get_session)):
    """
    Get the proxy with the lowest latency.

    Args:
        session: Database session

    Returns:
        Best proxy (lowest latency)
    """
    proxy = rotation_manager.get_proxy(session, "best")

    if not proxy:
        raise HTTPException(status_code=404, detail="No working proxies available")

    health_score = proxy.calculate_health_score()

    return ProxyResponse(
        id=proxy.id,
        ip=proxy.ip,
        port=proxy.port,
        username=proxy.username,
        latency=proxy.latency,
        last_checked=proxy.last_checked,
        is_working=proxy.is_working,
        fail_count=proxy.fail_count,
        last_used=proxy.last_used,
        address=proxy.address,
        health_score=health_score,
        protocol=proxy.protocol,
    )
