"""
Google OAuth Authentication Endpoint - FIXED VERSION
Proper JWT tokens, validation, and functionality focus
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
import uuid
import os
import re
from typing import Optional

try:
    from google.auth.transport import requests
    from google.oauth2 import id_token
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

from app.database import get_database
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token

router = APIRouter(tags=["google-authentication"])

# Request schema with validation
class GoogleAuthRequest(BaseModel):
    id_token: str
    
    @validator('id_token')
    def validate_id_token(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('ID token cannot be empty')
        return v.strip()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def is_real_google_client_id(client_id: str) -> bool:
    """Check if this is a real Google Client ID, not a placeholder"""
    if not client_id:
        return False
    
    # Check for placeholder values
    placeholder_indicators = [
        "your-google-client-id",
        "test-client-id",
        "placeholder",
        "example",
        "replace-me"
    ]
    
    client_id_lower = client_id.lower()
    if any(indicator in client_id_lower for indicator in placeholder_indicators):
        return False
    
    # Real Google Client IDs end with .apps.googleusercontent.com
    return client_id.endswith('.apps.googleusercontent.com')

# Helper functions for input validation
def validate_email(email: str) -> str:
    """Validate and sanitize email"""
    if not email or len(email.strip()) == 0:
        raise ValueError("Email cannot be empty")
    
    email = email.strip().lower()
    
    # Basic email format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")
    
    return email

def validate_name(name: str) -> str:
    """Validate and sanitize name"""
    if not name:
        name = "User"  # Default name
    
    name = name.strip()
    
    # Remove potentially harmful characters
    name = re.sub(r'[<>"\']', '', name)
    
    # Limit length
    if len(name) > 100:
        name = name[:100]
    
    return name


@router.post("/google")
async def google_signin(
    request: GoogleAuthRequest,
    db: Session = Depends(get_database)
):
    """
    Google OAuth signin endpoint with proper JWT tokens and validation
    """
    # Check if Google auth is properly configured
    if not GOOGLE_AUTH_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Google authentication not available - missing google-auth library"
        )
    
    if not GOOGLE_CLIENT_ID or not is_real_google_client_id(GOOGLE_CLIENT_ID):
        raise HTTPException(
            status_code=503,
            detail="Google authentication not configured - please add real Google Client ID from Google Cloud Console"
        )
    
    try:
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            request.id_token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Extract and validate user information from Google token
        google_user_id = idinfo['sub']
        email = validate_email(idinfo['email'])
        name = validate_name(idinfo.get('name', email.split('@')[0]))
        email_verified = idinfo.get('email_verified', False)
        
        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Existing user - update Google ID if not set
            if not user.google_id:
                user.google_id = google_user_id
                user.auth_provider = "google"
                db.commit()
                db.refresh(user)
        else:
            # New user from Google OAuth
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                hashed_password="",  # Empty for Google users
                full_name=name,
                is_active=True,
                is_verified=email_verified,
                subscription_tier="free",
                questions_used_this_month=0,
                google_id=google_user_id,
                auth_provider="google"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Generate proper JWT tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30 minutes
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "subscription_tier": user.subscription_tier,
                "questions_used_this_month": user.questions_used_this_month,
                "is_verified": user.is_verified,
                "is_active": user.is_active
            }
        }
        
    except ValueError as e:
        # Invalid token or validation error
        error_msg = str(e) if str(e) else "Invalid input data"
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {error_msg}"
        )
    except Exception as e:
        # Other errors - provide more detailed error info
        error_msg = str(e) if str(e) else "Unknown authentication error"
        print(f"Google auth error: {type(e).__name__}: {error_msg}")  # For debugging
        raise HTTPException(
            status_code=500,
            detail=f"Google authentication failed: {error_msg}"
        )

@router.get("/google/status")
async def google_auth_status():
    """Check if Google authentication is available"""
    is_properly_configured = GOOGLE_CLIENT_ID and is_real_google_client_id(GOOGLE_CLIENT_ID)
    
    return {
        "available": GOOGLE_AUTH_AVAILABLE and is_properly_configured,
        "configured": is_properly_configured,
        "library_installed": GOOGLE_AUTH_AVAILABLE,
        "client_id_is_real": is_real_google_client_id(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else False
    }

@router.get("/google/test-info")
async def google_test_info():
    """Endpoint to check Google OAuth configuration"""
    is_real_client_id = is_real_google_client_id(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else False
    
    return {
        "environment": ENVIRONMENT,
        "google_client_id_configured": is_real_client_id,
        "google_auth_available": GOOGLE_AUTH_AVAILABLE,
        "requires_real_google_token": True,
        "current_client_id": GOOGLE_CLIENT_ID[:20] + "..." if GOOGLE_CLIENT_ID else None,
        "setup_needed": not is_real_client_id
    }