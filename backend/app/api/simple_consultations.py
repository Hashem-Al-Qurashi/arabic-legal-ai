"""
Simple consultations router - Legal Q&A endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import sys
import os

from app.database import get_database

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
        
        # Process the question with AI
        start_time = datetime.now()
        answer = ask_question(query.strip())
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"✅ Question processed in {processing_time:.0f}ms")
        
        return {
            "id": str(uuid.uuid4()),
            "question": query.strip(),
            "answer": answer,
            "category": "general",
            "processing_time_ms": int(processing_time),
            "timestamp": datetime.now().isoformat(),
            "user_questions_remaining": 999  # Simplified for now
        }
        
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