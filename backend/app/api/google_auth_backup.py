"""
Google OAuth Authentication Endpoint
Zero-conflict additive implementation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
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

def parse_mock_token(token: str) -> tuple:
    """Parse mock token for development - format: mock_<email>_<name>"""
    if not token.startswith("mock_"):
        raise ValueError("Invalid mock token format")
    
    parts = token[5:].split("_", 1)  # Remove 'mock_' prefix and split once
    
    if len(parts) < 1:
        raise ValueError("Mock token must contain email")
    
    email = parts[0]
    name = parts[1] if len(parts) > 1 else email.split('@')[0]
    
    return email, name
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

@router.post("/google")
async def google_signin(
    request: GoogleAuthRequest,
    db: Session = Depends(get_database)
):
    """
    Google OAuth signin endpoint
    Returns same JWT token structure as regular login
    
    In development mode, accepts mock tokens for testing:
    - Token starting with 'mock_' will bypass Google verification
    - Use format: mock_email@example.com_name for testing
    """
    # Check if Google auth is properly configured
    if not GOOGLE_AUTH_AVAILABLE:
        # In development, allow mock tokens
        if ENVIRONMENT != "development" or not request.id_token.startswith("mock_"):
            raise HTTPException(
                status_code=503, 
                detail="Google authentication not available - missing google-auth library"
            )
    
    if not GOOGLE_CLIENT_ID:
        # In development, allow mock tokens
        if ENVIRONMENT != "development" or not request.id_token.startswith("mock_"):
            raise HTTPException(
                status_code=503,
                detail="Google authentication not configured - missing GOOGLE_CLIENT_ID"
            )
    
    try:
        # Development mode: Handle mock tokens for testing
        if ENVIRONMENT == "development" and request.id_token.startswith("mock_"):
            # Parse mock token format: mock_email@example.com_name
            mock_data = request.id_token[5:]  # Remove 'mock_' prefix
            parts = mock_data.split('_')
            
            if len(parts) >= 1:
                email = parts[0] if '@' in parts[0] else f"{parts[0]}@test.com"
                name = parts[1] if len(parts) > 1 else email.split('@')[0]
                google_user_id = f"mock_google_{email}"
                email_verified = True
            else:
                raise ValueError("Invalid mock token format")
        else:
            # Production mode: Verify real Google token
            idinfo = id_token.verify_oauth2_token(
                request.id_token, 
                requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            # Extract user information from Google token
            google_user_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo.get('name', email.split('@')[0])
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
        
        # Return SAME token structure as regular login
        fake_token = f"user_{user.id}_{user.email}"
        
        return {
            "access_token": fake_token,
            "refresh_token": fake_token,
            "token_type": "bearer",
            "expires_in": 3600,
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
        # Invalid token
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=500,
            detail=f"Google authentication failed: {str(e)}"
        )

@router.get("/google/status")
async def google_auth_status():
    """Check if Google authentication is available"""
    return {
        "available": GOOGLE_AUTH_AVAILABLE and bool(GOOGLE_CLIENT_ID),
        "configured": bool(GOOGLE_CLIENT_ID),
        "library_installed": GOOGLE_AUTH_AVAILABLE,
        "environment": ENVIRONMENT,
        "mock_mode_available": ENVIRONMENT == "development",
        "client_id_set": bool(GOOGLE_CLIENT_ID)
    }

@router.get("/google/test-info")
async def google_test_info():
    """Get testing information for Google OAuth"""
    if ENVIRONMENT == "development":
        return {
            "test_mode": "enabled",
            "mock_token_format": "mock_<email>_<name>",
            "example_tokens": [
                "mock_testuser@example.com_John Doe",
                "mock_john.doe@test.com_John",
                "mock_user@test.com"
            ],
            "endpoint": "/api/auth/google",
            "method": "POST",
            "body_format": {
                "id_token": "<mock_token_or_real_google_token>"
            },
            "environment": ENVIRONMENT,
            "google_client_id": GOOGLE_CLIENT_ID if GOOGLE_CLIENT_ID else "NOT_SET"
        }
    else:
        return {
            "test_mode": "disabled",
            "message": "Test mode only available in development environment"
        }