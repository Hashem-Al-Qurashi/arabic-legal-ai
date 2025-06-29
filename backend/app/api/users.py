"""
User management API endpoints.
Following enterprise best practices with clean separation of concerns.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_database
from app.schemas.user import User as UserSchema, UserUpdate
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_active_user
from app.models.user import User

# ✅ BEST PRACTICE: Clean router with no prefix (controlled in main.py)
router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserSchema)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile information."""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_my_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile information."""
    updated_user = UserService.update_user(db, current_user.id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    return updated_user


@router.get("/me/stats", response_model=Dict[str, Any])
async def get_my_stats(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's usage statistics."""
    stats = UserService.get_user_stats(db, current_user.id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User statistics not found"
        )
    
    return stats


@router.post("/me/check-limits")
async def check_my_limits(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """Check current user's subscription limits."""
    can_proceed, message = AuthService.check_user_limits(db, current_user.id)
    
    return {
        "can_proceed": can_proceed,
        "message": message,
        "questions_used": current_user.questions_used_this_month,
        "subscription_tier": current_user.subscription_tier
    }