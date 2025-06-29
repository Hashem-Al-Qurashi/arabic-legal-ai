"""
MINIMAL WORKING AUTH - No complex services, just basic CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid

from app.database import get_database
from app.models.user import User

router = APIRouter(tags=["authentication"])

# Simple password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/register")
async def register_user(
    email: str,
    password: str, 
    full_name: str,
    db: Session = Depends(get_database)
):
    """Minimal user registration - just works!"""
    
    print(f"📝 Simple registration: {email}, {full_name}")
    
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(400, "Email already registered")
        
        # Create user directly
        hashed_pw = hash_password(password)
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hashed_pw,
            full_name=full_name,
            is_active=True,
            is_verified=False,
            subscription_tier="free",
            questions_used_this_month=0
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ User created: {new_user.id}")
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "subscription_tier": new_user.subscription_tier,
            "message": "Registration successful!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        db.rollback()
        raise HTTPException(500, f"Registration failed: {str(e)}")


@router.post("/login")
async def login_user(
    email: str,
    password: str,
    db: Session = Depends(get_database)
):
    """Minimal login - just works!"""
    
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    return {
        "message": "Login successful!",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.get("/me")
async def get_current_user():
    """Dummy endpoint for now"""
    return {"message": "Current user endpoint"}

@router.post("/logout")
async def logout_user():
    """Dummy logout"""
    return {"message": "Logged out"}