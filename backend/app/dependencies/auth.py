"""
Authentication dependencies for FastAPI routes.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_database
from app.services.auth_service import AuthService
from app.models.user import User

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    print(f"🔍 DEBUG: Received token: {credentials.credentials[:20]}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        print(f"🔍 DEBUG: Calling AuthService.get_current_user...")
        user = AuthService.get_current_user(db, token)
        
        if user is None:
            print(f"❌ DEBUG: AuthService returned None")
            raise credentials_exception
            
        print(f"✅ DEBUG: Found user: {user.email}")
        return user
        
    except Exception as e:
        print(f"❌ DEBUG: Exception in get_current_user: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (must be active and verified).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_database)
) -> Optional[User]:
    """
    Get current user if token provided (optional authentication).
    
    Args:
        credentials: Optional HTTP Authorization header
        db: Database session
        
    Returns:
        Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return AuthService.get_current_user(db, token)
    except:
        return None