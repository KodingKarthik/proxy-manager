"""Database CRUD operations for proxies, users, logs, and blacklist."""

from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from .models import (
    Proxy,
    ProxyUpdate,
    User,
    UserRole,
    ActivityLog,
    Blacklist,
    ActivityLogFilter,
)
from .auth import get_password_hash


def create_proxy(session: Session, proxy: Proxy) -> Proxy:
    """Add a new proxy to the database."""
    session.add(proxy)
    session.commit()
    session.refresh(proxy)
    return proxy


def get_proxy(session: Session, proxy_id: int) -> Optional[Proxy]:
    """Get a proxy by ID."""
    return session.get(Proxy, proxy_id)


def get_all_proxies(
    session: Session, working_only: bool = False, limit: int = 100, offset: int = 0
) -> List[Proxy]:
    """List all proxies with optional filtering."""
    statement = select(Proxy)

    if working_only:
        statement = statement.where(Proxy.is_working == True)

    statement = statement.offset(offset).limit(limit)

    return list(session.exec(statement).all())


def get_working_proxies(session: Session) -> List[Proxy]:
    """Get all working proxies."""
    statement = select(Proxy).where(Proxy.is_working == True)
    return list(session.exec(statement).all())


def delete_proxy(session: Session, proxy_id: int) -> bool:
    """Delete a proxy by ID."""
    proxy = session.get(Proxy, proxy_id)
    if proxy:
        session.delete(proxy)
        session.commit()
        return True
    return False


def update_proxy(session: Session, proxy: Proxy, proxy_update: ProxyUpdate) -> Proxy:
    """Update proxy metadata."""
    update_data = proxy_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(proxy, field, value)
    session.add(proxy)
    session.commit()
    session.refresh(proxy)
    return proxy


def increment_fail_count(session: Session, proxy: Proxy) -> Proxy:
    """Increment the failure counter for a proxy."""
    proxy.fail_count += 1
    session.add(proxy)
    session.commit()
    session.refresh(proxy)
    return proxy


def reset_fail_count(session: Session, proxy: Proxy) -> Proxy:
    """Reset the failure counter for a proxy."""
    proxy.fail_count = 0
    session.add(proxy)
    session.commit()
    session.refresh(proxy)
    return proxy


def update_proxy_after_test(
    session: Session, proxy: Proxy, is_working: bool, latency: Optional[float] = None
) -> Proxy:
    """Update proxy after a health check test."""
    proxy.is_working = is_working
    proxy.last_checked = datetime.now()

    if is_working:
        if latency is not None:
            proxy.latency = latency
        proxy.fail_count = 0
    else:
        proxy.fail_count += 1

    session.add(proxy)
    session.commit()
    session.refresh(proxy)
    return proxy


def update_last_used(session: Session, proxy: Proxy) -> Proxy:
    """Update the last_used timestamp for a proxy."""
    proxy.last_used = datetime.now()
    session.add(proxy)
    session.commit()
    session.refresh(proxy)
    return proxy


# User CRUD operations
def create_user(
    session: Session, username: str, email: str, password: str, role: UserRole = None
) -> User:
    """Create a new user. First user becomes admin."""
    # Check if this is the first user
    if role is None:
        existing_users = list(session.exec(select(User)).all())
        role = UserRole.ADMIN if len(existing_users) == 0 else UserRole.USER

    hashed_password = get_password_hash(password)
    user = User(
        username=username, email=email, hashed_password=hashed_password, role=role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return session.get(User, user_id)


def get_all_users(session: Session, limit: int = 100, offset: int = 0) -> List[User]:
    """Get all users."""
    statement = select(User).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def delete_user(session: Session, user_id: int) -> bool:
    """Delete a user by ID."""
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False


def update_user_role(session: Session, user: User, new_role: UserRole) -> User:
    """Update a user's role."""
    user.role = new_role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Activity Log CRUD operations
def create_activity_log(
    session: Session,
    user_id: int,
    endpoint: str,
    method: str,
    status_code: int,
    target_url: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> ActivityLog:
    """Create a new activity log entry."""
    log = ActivityLog(
        user_id=user_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        target_url=target_url,
        ip_address=ip_address,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def get_user_logs(
    session: Session, user_id: int, filter_params: Optional[ActivityLogFilter] = None
) -> List[ActivityLog]:
    """Get activity logs for a specific user."""
    statement = select(ActivityLog).where(ActivityLog.user_id == user_id)

    if filter_params:
        if filter_params.start_date:
            statement = statement.where(
                ActivityLog.timestamp >= filter_params.start_date
            )
        if filter_params.end_date:
            statement = statement.where(ActivityLog.timestamp <= filter_params.end_date)
        if filter_params.endpoint:
            statement = statement.where(ActivityLog.endpoint == filter_params.endpoint)
        if filter_params.method:
            statement = statement.where(ActivityLog.method == filter_params.method)
        if filter_params.status_code:
            statement = statement.where(
                ActivityLog.status_code == filter_params.status_code
            )

        statement = statement.offset(filter_params.offset).limit(filter_params.limit)
    else:
        statement = statement.limit(100)

    statement = statement.order_by(ActivityLog.timestamp.desc())
    return list(session.exec(statement).all())


def get_all_logs(
    session: Session, filter_params: Optional[ActivityLogFilter] = None
) -> List[ActivityLog]:
    """Get all activity logs (admin only)."""
    statement = select(ActivityLog)

    if filter_params:
        if filter_params.start_date:
            statement = statement.where(
                ActivityLog.timestamp >= filter_params.start_date
            )
        if filter_params.end_date:
            statement = statement.where(ActivityLog.timestamp <= filter_params.end_date)
        if filter_params.endpoint:
            statement = statement.where(ActivityLog.endpoint == filter_params.endpoint)
        if filter_params.method:
            statement = statement.where(ActivityLog.method == filter_params.method)
        if filter_params.status_code:
            statement = statement.where(
                ActivityLog.status_code == filter_params.status_code
            )

        statement = statement.offset(filter_params.offset).limit(filter_params.limit)
    else:
        statement = statement.limit(100)

    statement = statement.order_by(ActivityLog.timestamp.desc())
    return list(session.exec(statement).all())


# Blacklist CRUD operations
def create_blacklist_rule(
    session: Session, pattern: str, created_by: int, description: Optional[str] = None
) -> Blacklist:
    """Create a new blacklist rule."""
    rule = Blacklist(pattern=pattern, description=description, created_by=created_by)
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule


def get_all_blacklist_rules(session: Session) -> List[Blacklist]:
    """Get all blacklist rules."""
    statement = select(Blacklist).order_by(Blacklist.created_at.desc())
    return list(session.exec(statement).all())


def get_blacklist_rule(session: Session, rule_id: int) -> Optional[Blacklist]:
    """Get a blacklist rule by ID."""
    return session.get(Blacklist, rule_id)


def delete_blacklist_rule(session: Session, rule_id: int) -> bool:
    """Delete a blacklist rule by ID."""
    rule = session.get(Blacklist, rule_id)
    if rule:
        session.delete(rule)
        session.commit()
        return True
    return False


# API Key CRUD operations
def create_api_key(
    session: Session, user_id: int, name: str, expires_at: Optional[datetime] = None
) -> tuple["ApiKey", str]:
    """
    Create a new API key for a user.
    Returns (ApiKey, raw_key_string)
    
    The raw key is only returned once and should be saved by the caller.
    """
    import secrets
    from .models import ApiKey
    
    # Generate a secure random key (32 bytes = 43 chars in base64)
    raw_key = secrets.token_urlsafe(32)
    prefix = raw_key[:8]
    key_hash = get_password_hash(raw_key)

    api_key = ApiKey(
        key_hash=key_hash,
        prefix=prefix,
        name=name,
        user_id=user_id,
        expires_at=expires_at,
    )
    session.add(api_key)
    session.commit()
    session.refresh(api_key)

    return api_key, raw_key


def get_user_api_keys(session: Session, user_id: int) -> List["ApiKey"]:
    """Get all API keys for a user."""
    from .models import ApiKey
    
    statement = select(ApiKey).where(ApiKey.user_id == user_id).order_by(
        ApiKey.created_at.desc()
    )
    return list(session.exec(statement).all())


def get_api_key_by_id(session: Session, key_id: int) -> Optional["ApiKey"]:
    """Get an API key by ID."""
    from .models import ApiKey
    return session.get(ApiKey, key_id)


def revoke_api_key(session: Session, key_id: int, user_id: int) -> bool:
    """
    Revoke/delete an API key (only if owned by user).
    Returns True if successfully deleted, False otherwise.
    """
    from .models import ApiKey
    
    api_key = session.get(ApiKey, key_id)
    if api_key and api_key.user_id == user_id:
        session.delete(api_key)
        session.commit()
        return True
    return False


def deactivate_api_key(session: Session, key_id: int, user_id: int) -> Optional["ApiKey"]:
    """
    Deactivate an API key (soft delete - only if owned by user).
    Returns the updated ApiKey if successful, None otherwise.
    """
    from .models import ApiKey
    
    api_key = session.get(ApiKey, key_id)
    if api_key and api_key.user_id == user_id:
        api_key.is_active = False
        session.add(api_key)
        session.commit()
        session.refresh(api_key)
        return api_key
    return None
