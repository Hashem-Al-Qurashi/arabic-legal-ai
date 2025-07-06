"""
MINIMAL WORKING AUTH - JSON Input Version
"""
from app.dependencies.auth import get_current_active_user
from fastapi import Form
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
import uuid
from app.dependencies.auth import get_current_active_user
from app.database import get_database
from app.models.user import User

router = APIRouter(tags=["authentication"])

# Request schemas
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Simple password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/register")
async def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_database)
):
    """Minimal user registration - accepts JSON"""
    
    print(f"📝 Simple registration: {request.email}, {request.full_name}")
    
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise HTTPException(400, "Email already registered")
        
        # Create user directly
        hashed_pw = hash_password(request.password)
        new_user = User(
            id=str(uuid.uuid4()),
            email=request.email,
            hashed_password=hashed_pw,
            full_name=request.full_name,  # 🔧 Make sure this is properly saved
            is_active=True,
            is_verified=False,
            subscription_tier="free",
            questions_used_this_month=0
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ User created: {new_user.id} with name: {new_user.full_name}")
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,  # 🔧 Return the actual name
            "subscription_tier": new_user.subscription_tier,
            "is_active": new_user.is_active,
            "questions_used_this_month": new_user.questions_used_this_month,
            "is_verified": new_user.is_verified
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        db.rollback()
        raise HTTPException(500, f"Registration failed: {str(e)}")

@router.post("/login")
async def login_user(
    request: LoginRequest,
    db: Session = Depends(get_database)
):
    """Minimal login - returns token-like response"""
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    # 🔧 FIXED: Return token-like response for frontend compatibility
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

@router.post("/ask")
async def ask_legal_question(
    query: str = Form(..., description="Legal question in Arabic"),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ask a legal question and get AI-powered advice with proper authentication.
    
    - **query**: Your legal question in Arabic
    
    Returns AI-generated legal advice based on Saudi law.
    """
    try:
        # Import RAG engine
        import sys
        import os
        sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')
        from rag_engine import ask_question
        
        print(f"🤖 Processing legal question: {query[:50]}...")
        print(f"🔍 User before question: {current_user.email}, questions: {current_user.questions_used_this_month}")
        
        # Check user limits before processing
        if current_user.subscription_tier == "free" and current_user.questions_used_this_month >= 20:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="لقد وصلت إلى الحد الأقصى من الأسئلة المجانية (20 سؤال شهرياً)"
            )
        elif current_user.subscription_tier == "pro" and current_user.questions_used_this_month >= 100:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="لقد وصلت إلى الحد الأقصى من الأسئلة (100 سؤال شهرياً)"
            )
        
        # Increment question count BEFORE processing (to prevent abuse)
        current_user.questions_used_this_month += 1
        db.commit()
        db.refresh(current_user)
        
        print(f"✅ User after increment: {current_user.email}, questions: {current_user.questions_used_this_month}")
        
        # Process the question with AI
        start_time = datetime.now()
        answer = ask_question(query.strip())
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"✅ Question processed in {processing_time:.0f}ms")
        
        # Calculate remaining questions
        if current_user.subscription_tier == "free":
            questions_remaining = max(0, 20 - current_user.questions_used_this_month)
        elif current_user.subscription_tier == "pro":
            questions_remaining = max(0, 100 - current_user.questions_used_this_month)
        else:  # enterprise
            questions_remaining = 999999
        
        response = {
            "id": str(uuid.uuid4()),
            "question": query.strip(),
            "answer": answer,
            "category": "general",
            "processing_time_ms": int(processing_time),
            "timestamp": datetime.now().isoformat(),
            "user_questions_remaining": questions_remaining
        }
        
        # Add updated user data to response for frontend
        response["updated_user"] = {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "subscription_tier": current_user.subscription_tier,
            "questions_used_this_month": current_user.questions_used_this_month,
            "is_verified": current_user.is_verified,
            "questions_remaining": questions_remaining
        }
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (like rate limits) as-is
        raise
    except Exception as e:
        print(f"❌ Error processing question: {e}")
        import traceback
        traceback.print_exc()
        
        # Rollback the question count increment if processing failed
        try:
            current_user.questions_used_this_month -= 1
            db.commit()
            print(f"🔄 Rolled back question count for {current_user.email}")
        except:
            pass
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ في معالجة السؤال: {str(e)}"
        )