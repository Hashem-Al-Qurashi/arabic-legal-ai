"""
Authentication API endpoints for registration, login, and token management.
Following enterprise best practices with clean separation of concerns.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_database
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.user import User as UserSchema
from app.services.auth_service import AuthService
from app.core.config import settings
from app.dependencies.auth import get_current_user

# ✅ BEST PRACTICE: Clean router with no prefix (controlled in main.py)
router = APIRouter(tags=["authentication"])


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_register: UserRegister,
    db: Session = Depends(get_database)
):
    """Register a new user account."""
    
    # 🔧 DEBUG: Print what we received
    print(f"🔍 DEBUG: Received registration data:")
    print(f"  Email: {user_register.email}")
    print(f"  Full name: {user_register.full_name}")
    print(f"  Password length: {len(user_register.password)}")
    
    try:
        # Check if user already exists
        print(f"🔄 DEBUG: Checking if user exists...")
        existing_user = AuthService.authenticate_user(
            db, user_register.email, "dummy_password"
        )
        
        if existing_user is not None:
            print(f"❌ DEBUG: User already exists!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        print(f"✅ DEBUG: User doesn't exist, proceeding with registration...")
        
        # Register new user
        print(f"🔄 DEBUG: Calling AuthService.register_user...")
        new_user = AuthService.register_user(db, user_register)
        
        if not new_user:
            print(f"❌ DEBUG: AuthService.register_user returned None!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
        
        print(f"✅ DEBUG: User created successfully!")
        return new_user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"💥 DEBUG: Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


# ... rest of the endpoints stay the same ...

@router.post("/login", response_model=Token)
async def login_user(
    user_login: UserLogin,
    db: Session = Depends(get_database)
):
    """Login with email and password to get access tokens."""
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
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_database)
):
    """Refresh access token using refresh token."""
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
    """Get current user profile information."""
    return current_user


@router.post("/logout")
async def logout_user():
    """Logout user (client should discard tokens)."""
    return {"message": "Successfully logged out"}