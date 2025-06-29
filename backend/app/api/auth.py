from app.core.config import settings
from app.dependencies.auth import get_current_user
"""
Authentication API endpoints for registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_database
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.user import User as UserSchema
from app.services.auth_service import AuthService
from app.core.config import settings
from app.dependencies.auth import get_current_user  # 🔧 ADD THIS LINE

router = APIRouter(prefix="/auth", tags=["authentication"])

# ... rest of the file stays the same

"""
Authentication API endpoints for registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_database
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.user import User as UserSchema
from app.services.auth_service import AuthService
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_register: UserRegister,
    db: Session = Depends(get_database)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (will be used for login)
    - **password**: Strong password (minimum 8 characters)  
    - **full_name**: User's full name (Arabic names supported)
    
    Returns the created user information (without password).
    """
    # Check if user already exists
    existing_user = AuthService.authenticate_user(
        db, user_register.email, "dummy_password"
    )
    
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Register new user
    new_user = AuthService.register_user(db, user_register)
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )
    
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    user_login: UserLogin,
    db: Session = Depends(get_database)
):
    """
    Login with email and password to get access tokens.
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns JWT tokens for authentication.
    """
    login_result = AuthService.login_user(db, user_login)
    
    if not login_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user, access_token, refresh_token = login_result
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60  # Convert to seconds
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_database)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid JWT refresh token
    
    Returns new access and refresh tokens.
    """
    token_result = AuthService.refresh_access_token(db, refresh_token)
    
    if not token_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    new_access_token, new_refresh_token = token_result
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """
    Get current user profile information.
    
    Requires valid authentication token.
    Returns current user details including subscription info.
    """
    return current_user


@router.post("/logout")
async def logout_user():
    """
    Logout user (client should discard tokens).
    
    Since we use stateless JWT tokens, logout is handled client-side
    by discarding the tokens. This endpoint is for consistency.
    """
    return {"message": "Successfully logged out"}