"""
Simple auth dependency that works with both fake tokens and JWT tokens
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jose import jwt
from app.database import get_database
from app.models.user import User
from app.core.config import settings

security = HTTPBearer()

def get_current_user_simple(
    credentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """Get current user from either fake token or JWT token"""
    token = credentials.credentials
    
    # Try JWT token first
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id and token_type == "access":
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user
    except:
        pass  # Fall back to fake token parsing
    
    # Fallback: Extract user email from fake token format: user_{id}_{email}
    if token.startswith("user_"):
        parts = token.split("_")
        if len(parts) >= 3:
            email = "_".join(parts[2:])  # Handle emails with underscores
            user = db.query(User).filter(User.email == email).first()
            if user:
                return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials"
    )

def get_current_active_user_simple(
    current_user: User = Depends(get_current_user_simple)
) -> User:
    """Get current active user (simple version)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_optional_current_user(
    db: Session = Depends(get_database),
    credentials = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """Get current user from token, but return None if no token provided"""
    if not credentials:
        return None
    
    try:
        return get_current_user_simple(credentials, db)
    except HTTPException:
        return None

# Aliases for compatibility with chat.py
get_current_active_user = get_current_active_user_simple
get_current_user = get_current_user_simple
