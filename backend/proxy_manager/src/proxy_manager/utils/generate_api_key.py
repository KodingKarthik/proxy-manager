"""CLI script to generate API keys for service users."""

import secrets
import sys
from sqlmodel import Session, select

from ..database import engine
from ..models import User, UserRole, ApiKey
from ..auth import get_password_hash


def generate_api_key(username: str, key_name: str) -> str:
    """
    Generate an API key for a service user.
    
    Args:
        username: Username of the service user
        key_name: Friendly name for the API key
        
    Returns:
        The generated API key (prefix.secret)
    """
    # Generate a secure random key
    prefix = secrets.token_urlsafe(8)
    secret = secrets.token_urlsafe(32)
    raw_key = f"{prefix}.{secret}"
    
    with Session(engine) as session:
        # Find or create service user
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        
        if not user:
            print(f"Creating new service user: {username}")
            user = User(
                username=username,
                email=f"{username}@internal",
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                role=UserRole.SERVICE,
                is_active=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # Create API key
        api_key = ApiKey(
            key_hash=get_password_hash(raw_key),
            prefix=prefix,
            name=key_name,
            user_id=user.id,
            is_active=True
        )
        session.add(api_key)
        session.commit()
        
        print(f"✓ API Key generated for user '{username}'")
        print(f"  Name: {key_name}")
        print(f"  Prefix: {prefix}")
        print(f"\n  API Key: {raw_key}")
        print(f"\n⚠️  Save this key securely - it won't be shown again!")
        
        return raw_key


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m proxy_manager.utils.generate_api_key <username> <key_name>")
        print("Example: python -m proxy_manager.utils.generate_api_key mitm-forwarder 'MITM Forwarder Key'")
        sys.exit(1)
    
    username = sys.argv[1]
    key_name = sys.argv[2]
    
    generate_api_key(username, key_name)
