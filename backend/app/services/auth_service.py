"""
Minimal AuthService class - Just what we need for chat functionality
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.user import User

# Simple password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Minimal auth service for chat functionality"""

    @staticmethod
    def check_user_limits(db: Session, user_id: str) -> Tuple[bool, str]:
        """
        Check if user can make more requests based on subscription.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Tuple of (can_proceed, message)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"
        
        # Free tier limits
        if user.subscription_tier == "free":
            if user.questions_used_this_month >= 20:
                return False, "Free tier limit reached (3 questions/month). Please upgrade to Pro."
        
        # Pro tier limits (example: 100 questions/month)
        elif user.subscription_tier == "pro":
            if user.questions_used_this_month >= 100:
                return False, "Pro tier limit reached (100 questions/month)."
        
        # Enterprise tier: unlimited
        return True, "OK"

    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """
        Minimal implementation - just for compatibility
        Your existing auth system handles this
        """
        # This is just a placeholder - your actual auth uses different logic
        return None

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)