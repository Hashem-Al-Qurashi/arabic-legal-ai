"""
Enhanced simple consultations router with proper user tracking.
Save this as: backend/app/api/simple_consultations.py
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import sys
import os

from app.database import get_database
from app.models.user import User

router = APIRouter(tags=["consultations"])
@router.post("/ask")
async def ask_legal_question(
    query: str = Form(..., description="Legal question in Arabic"),
    db: Session = Depends(get_database)
):
    """
    Ask a legal question and get AI-powered advice.
    
    - **query**: Your legal question in Arabic
    
    Returns AI-generated legal advice based on Saudi law.
    """
    try:
        # Import RAG engine
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from rag_engine import ask_question
        
        print(f"🤖 Processing legal question: {query[:50]}...")
        
        # 🔧 FIX: Get the actual user and update their question count
        current_user = db.query(User).first()
        if current_user:
            print(f"🔍 User before question: {current_user.email}, questions: {current_user.questions_used_this_month}")
            
            # Increment question count
            current_user.questions_used_this_month += 1
            db.commit()
            db.refresh(current_user)
            
            print(f"✅ User after question: {current_user.email}, questions: {current_user.questions_used_this_month}")
        
        # Process the question with AI
        start_time = datetime.now()
        answer = ask_question(query.strip())
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"✅ Question processed in {processing_time:.0f}ms")
        
        # 🔧 FIX: Calculate remaining questions
        questions_remaining = 999
        if current_user:
            if current_user.subscription_tier == "free":
                questions_remaining = max(0, 20 - current_user.questions_used_this_month)
            elif current_user.subscription_tier == "pro":
                questions_remaining = max(0, 100 - current_user.questions_used_this_month)
        
        response = {
            "id": str(uuid.uuid4()),
            "question": query.strip(),
            "answer": answer,
            "category": "general",
            "processing_time_ms": int(processing_time),
            "timestamp": datetime.now().isoformat(),
            "user_questions_remaining": questions_remaining
        }
        
        # 🔧 FIX: Add updated user data to response
        if current_user:
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
        
    except Exception as e:
        print(f"❌ Error processing question: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"حدث خطأ في معالجة السؤال: {str(e)}"
        )

@router.get("/categories")
async def get_legal_categories():
    """Get available legal categories"""
    categories = [
        {"id": "commercial", "name": "القانون التجاري", "emoji": "💼"},
        {"id": "labor", "name": "قانون العمل", "emoji": "👷"},
        {"id": "real_estate", "name": "القانون العقاري", "emoji": "🏠"},
        {"id": "family", "name": "الأحوال الشخصية", "emoji": "👨‍👩‍👧‍👦"},
        {"id": "criminal", "name": "القانون الجنائي", "emoji": "⚖️"},
        {"id": "administrative", "name": "القانون الإداري", "emoji": "🏛️"},
        {"id": "general", "name": "استشارة عامة", "emoji": "📋"}
    ]
    return {"categories": categories}


@router.get("/user/stats")
async def get_user_stats(
    db: Session = Depends(get_database)
):
    """Get current user statistics"""
    current_user = db.query(User).first()
    
    if not current_user:
        return {
            "error": "No user found",
            "questions_used": 0,
            "questions_remaining": 20
        }
    
    questions_remaining = 20  # Default for free tier
    if current_user.subscription_tier == "free":
        questions_remaining = max(0, 20 - current_user.questions_used_this_month)
    elif current_user.subscription_tier == "pro":
        questions_remaining = max(0, 100 - current_user.questions_used_this_month)
    else:  # enterprise
        questions_remaining = 999999
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "subscription_tier": current_user.subscription_tier,
        "questions_used_this_month": current_user.questions_used_this_month,
        "questions_remaining": questions_remaining,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified
    }

@router.get("/user/stats")
async def get_user_stats(
    db: Session = Depends(get_database)
):
    """Get current user statistics"""
    current_user = db.query(User).first()
    
    if not current_user:
        return {
            "error": "No user found",
            "questions_used": 0,
            "questions_remaining": 20
        }
    
    questions_remaining = 20  # Default for free tier
    if current_user.subscription_tier == "free":
        questions_remaining = max(0, 20 - current_user.questions_used_this_month)
    elif current_user.subscription_tier == "pro":
        questions_remaining = max(0, 100 - current_user.questions_used_this_month)
    else:  # enterprise
        questions_remaining = 999999
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "subscription_tier": current_user.subscription_tier,
        "questions_used_this_month": current_user.questions_used_this_month,
        "questions_remaining": questions_remaining,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified
    }