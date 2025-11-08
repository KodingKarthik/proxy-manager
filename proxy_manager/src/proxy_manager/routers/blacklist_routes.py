"""Blacklist management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from ..database import get_session
from ..models import User, BlacklistCreate, BlacklistResponse
from ..auth import get_current_user
from ..crud import (
    create_blacklist_rule, get_all_blacklist_rules,
    delete_blacklist_rule, get_blacklist_rule
)
from ..utils.logger import log_activity, get_client_ip
from ..utils.blacklist import blacklist_checker
from ..routers.rate_limit import check_rate_limit
from fastapi import Request

router = APIRouter(prefix="/blacklist", tags=["blacklist"])


@router.get("", response_model=List[BlacklistResponse])
def list_blacklist_rules(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all blacklist rules.
    
    Args:
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        List of blacklist rules
    """
    check_rate_limit(current_user)
    
    rules = get_all_blacklist_rules(session)
    
    # Reload patterns in blacklist checker
    blacklist_checker.load_patterns(rules)
    
    return [
        BlacklistResponse(
            id=rule.id,
            pattern=rule.pattern,
            description=rule.description,
            created_at=rule.created_at,
            created_by=rule.created_by
        )
        for rule in rules
    ]


@router.post("", response_model=BlacklistResponse, status_code=201)
def add_blacklist_rule(
    rule_data: BlacklistCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Add a new blacklist regex pattern.
    
    Args:
        rule_data: Blacklist rule data
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Created blacklist rule
    """
    check_rate_limit(current_user)
    
    # Validate regex pattern
    import re
    try:
        re.compile(rule_data.pattern)
    except re.error as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid regex pattern: {str(e)}"
        )
    
    # Create rule
    rule = create_blacklist_rule(
        session=session,
        pattern=rule_data.pattern,
        created_by=current_user.id,
        description=rule_data.description
    )
    
    # Reload patterns in blacklist checker
    all_rules = get_all_blacklist_rules(session)
    blacklist_checker.load_patterns(all_rules)
    
    # Log activity
    ip_address = get_client_ip(request)
    log_activity(
        session=session,
        user=current_user,
        endpoint="/blacklist",
        method="POST",
        status_code=201,
        ip_address=ip_address
    )
    
    return BlacklistResponse(
        id=rule.id,
        pattern=rule.pattern,
        description=rule.description,
        created_at=rule.created_at,
        created_by=rule.created_by
    )


@router.delete("/{rule_id}", status_code=204)
def delete_blacklist_rule_by_id(
    rule_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a blacklist rule by ID.
    
    Args:
        rule_id: ID of rule to delete
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session
    """
    check_rate_limit(current_user)
    
    rule = get_blacklist_rule(session, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blacklist rule with ID {rule_id} not found"
        )
    
    success = delete_blacklist_rule(session, rule_id)
    
    if success:
        # Reload patterns in blacklist checker
        all_rules = get_all_blacklist_rules(session)
        blacklist_checker.load_patterns(all_rules)
        
        # Log activity
        ip_address = get_client_ip(request)
        log_activity(
            session=session,
            user=current_user,
            endpoint=f"/blacklist/{rule_id}",
            method="DELETE",
            status_code=204,
            ip_address=ip_address
        )

