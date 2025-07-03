"""
Enhanced Chat API endpoints with proper user data updates.
Save this as: backend/app/api/chat.py
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session

from app.database import get_database
from app.dependencies.auth import get_current_active_user
from app.services.chat_service import ChatService
from app.models.user import User
from app.models.conversation import Conversation, Message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message")
async def send_chat_message(
    message: str = Form(..., description="User message"),
    conversation_id: Optional[str] = Form(None, description="Existing conversation ID (optional)"),
    db: Session = Depends(get_database)
):
    """Send a message in a chat conversation with full context history."""
    try:
        print(f"🔍 DEBUG: Received message: {message}")
        print(f"🔍 DEBUG: Conversation ID: {conversation_id}")
        
        # Get first user for testing (temporary fix)
        current_user = db.query(User).first()
        print(f"🔍 DEBUG: Found user: {current_user.email if current_user else 'None'}")
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found - please register first"
            )
        
        print(f"🔍 DEBUG: User questions before: {current_user.questions_used_this_month}")
        
        result = await ChatService.process_chat_message(
            db=db,
            user=current_user,
            conversation_id=conversation_id,
            message_content=message.strip()
        )
        
        # 🔧 FIX: Refresh user data after processing
        db.refresh(current_user)
        print(f"🔍 DEBUG: User questions after: {current_user.questions_used_this_month}")
        
        # 🔧 FIX: Add updated user data to response
        result["updated_user"] = {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "subscription_tier": current_user.subscription_tier,
            "questions_used_this_month": current_user.questions_used_this_month,
            "is_verified": current_user.is_verified,
            "questions_remaining": _calculate_questions_remaining(current_user)
        }
        
        print(f"🔍 DEBUG: Response includes updated user data")
        return result
        
    except Exception as e:
        print(f"❌ DEBUG: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def _calculate_questions_remaining(user: User) -> int:
    """Calculate remaining questions for user based on subscription."""
    if user.subscription_tier == "free":
        return max(0, 20 - user.questions_used_this_month)  # Free tier: 20 questions
    elif user.subscription_tier == "pro":
        return max(0, 100 - user.questions_used_this_month)  # Pro tier: 100 questions
    else:  # enterprise
        return 999999  # "unlimited"

def _calculate_questions_remaining(user: User) -> int:
    """Calculate remaining questions for user based on subscription."""
    if user.subscription_tier == "free":
        return max(0, 20 - user.questions_used_this_month)  # Free tier: 20 questions
    elif user.subscription_tier == "pro":
        return max(0, 100 - user.questions_used_this_month)  # Pro tier: 100 questions
    else:  # enterprise
        return 999999  # "unlimited"


@router.get("/conversations")
async def get_user_conversations(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_database)
):
    """Get user's conversation list with pagination."""
    
    # Get first user for testing (temporary fix)
    current_user = db.query(User).first()
    if not current_user:
        return {"conversations": [], "total": 0, "limit": limit, "offset": offset}
    
    print(f"🔍 DEBUG: Loading conversations for user: {current_user.email}")
    
    conversations = ChatService.get_user_conversations(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    print(f"🔍 DEBUG: Found {len(conversations)} conversations")
    
    # Format response with conversation previews
    conversation_list = []
    for conv in conversations:
        # Get last message for preview
        messages = ChatService.get_conversation_messages(db, conv.id, limit=1)
        last_message = messages[-1] if messages else None
        
        conversation_list.append({
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "last_message_preview": last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None,
            "message_count": len(ChatService.get_conversation_messages(db, conv.id))
        })
    
    return {
        "conversations": conversation_list,
        "total": len(conversation_list),
        "limit": limit,
        "offset": offset,
        # 🔧 FIX: Include current user data in conversations response
        "current_user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "subscription_tier": current_user.subscription_tier,
            "questions_used_this_month": current_user.questions_used_this_month,
            "questions_remaining": _calculate_questions_remaining(current_user)
        }
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    db: Session = Depends(get_database)
):
    """Get all messages in a conversation."""
    
    print(f"🔍 DEBUG: Loading messages for conversation: {conversation_id}")
    
    # Get first user for testing
    current_user = db.query(User).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        print(f"❌ DEBUG: Conversation {conversation_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = ChatService.get_conversation_messages(db, conversation_id, limit)
    print(f"✅ DEBUG: Found {len(messages)} messages in conversation")
    
    # Format messages for frontend
    message_list = []
    for msg in messages:
        message_list.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat(),
            "confidence_score": msg.confidence_score,
            "processing_time_ms": msg.processing_time_ms
        })
    
    return {
        "conversation_id": conversation_id,
        "conversation_title": conversation.title,
        "messages": message_list,
        "total_messages": len(message_list),
        # 🔧 FIX: Include current user data
        "current_user": {
            "id": current_user.id,
            "questions_used_this_month": current_user.questions_used_this_month,
            "questions_remaining": _calculate_questions_remaining(current_user)
        }
    }


@router.delete("/conversations/{conversation_id}")
async def archive_conversation(
    conversation_id: str,
    db: Session = Depends(get_database)
):
    """Archive (soft delete) a conversation."""
    
    print(f"🔍 DEBUG: Deleting conversation: {conversation_id}")
    
    # Get first user for testing
    current_user = db.query(User).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    
    success = ChatService.archive_conversation(db, conversation_id, current_user.id)
    
    if not success:
        print(f"❌ DEBUG: Failed to delete conversation {conversation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    print(f"✅ DEBUG: Conversation deleted successfully")
    
    return {
        "message": "Conversation archived successfully",
        "conversation_id": conversation_id
    }


@router.put("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    new_title: str = Form(...),
    db: Session = Depends(get_database)
):
    """Update conversation title."""
    
    print(f"🔍 DEBUG: Updating title for conversation: {conversation_id}")
    print(f"🔍 DEBUG: New title: {new_title}")
    
    # Get first user for testing
    current_user = db.query(User).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        print(f"❌ DEBUG: Conversation {conversation_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    updated_conversation = ChatService.update_conversation_title(
        db, conversation_id, new_title.strip()
    )
    
    print(f"✅ DEBUG: Title updated successfully")
    
    return {
        "conversation_id": conversation_id,
        "new_title": updated_conversation.title,
        "updated_at": updated_conversation.updated_at.isoformat()
    }


@router.get("/stats")
async def get_chat_stats(
    db: Session = Depends(get_database)
):
    """Get user's chat statistics with updated data."""
    
    # Get first user for testing
    current_user = db.query(User).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    
    conversations = ChatService.get_user_conversations(db, current_user.id, limit=1000)
    
    total_conversations = len(conversations)
    total_messages = 0
    
    for conv in conversations:
        messages = ChatService.get_conversation_messages(db, conv.id)
        total_messages += len(messages)
    
    return {
        "user_id": current_user.id,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "questions_used_this_month": current_user.questions_used_this_month,
        "subscription_tier": current_user.subscription_tier,
        "questions_remaining": _calculate_questions_remaining(current_user)
    }