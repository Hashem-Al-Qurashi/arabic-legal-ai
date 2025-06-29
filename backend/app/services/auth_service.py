"""
Authentication service for login, registration, and token management.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    verify_refresh_token
)
from app.core.config import settings


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user

    @staticmethod
    def register_user(db: Session, user_register: UserRegister) -> Optional[User]:
        """
        Register a new user account.
        
        Args:
            db: Database session
            user_register: Registration data
            
        Returns:
            Created user or None if registration failed
        """
        # Convert registration schema to user creation schema
        user_create = UserCreate(
            email=user_register.email,
            password=user_register.password,
            full_name=user_register.full_name,
            is_active=True
        )
        
        return UserService.create_user(db, user_create)

    @staticmethod
    def login_user(db: Session, user_login: UserLogin) -> Optional[Tuple[User, str, str]]:
        """
        Login user and create tokens.
        
        Args:
            db: Database session
            user_login: Login credentials
            
        Returns:
            Tuple of (user, access_token, refresh_token) or None if login failed
        """
        # Authenticate user
        user = AuthService.authenticate_user(
            db, user_login.email, user_login.password
        )
        
        if not user:
            return None
        
        # Create tokens
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        refresh_token = create_refresh_token(subject=user.id)
        
        return user, access_token, refresh_token

    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """
        Get current user from JWT token.
        
        Args:
            db: Database session
            token: JWT access token
            
        Returns:
            Current user or None if token invalid
        """
        user_id = verify_token(token)
        if not user_id:
            return None
        
        user = UserService.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            return None
        
        return user

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[Tuple[str, str]]:
        """
        Refresh access token using refresh token.
        
        Args:
            db: Database session
            refresh_token: JWT refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token) or None if invalid
        """
        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            return None
        
        # Verify user still exists and is active
        user = UserService.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            return None
        
        # Create new tokens
        new_access_token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        new_refresh_token = create_refresh_token(subject=user_id)
        
        return new_access_token, new_refresh_token

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
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False, "User not found"
        
        # Free tier limits
        if user.subscription_tier == "free":
            if user.questions_used_this_month >= 3:
                return False, "Free tier limit reached (3 questions/month). Please upgrade to Pro."
        
        # Pro tier limits (example: 100 questions/month)
        elif user.subscription_tier == "pro":
            if user.questions_used_this_month >= 100:
                return False, "Pro tier limit reached (100 questions/month)."
        
        # Enterprise tier: unlimited
        return True, "OK"