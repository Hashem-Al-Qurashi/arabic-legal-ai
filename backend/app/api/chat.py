"""
Chat API endpoints for conversation management.
Handles chat history, messages, and context-aware responses.
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
        
        # Get first user for testing
        current_user = db.query(User).first()
        print(f"🔍 DEBUG: Found user: {current_user.email if current_user else 'None'}")
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found - please register first"
            )
        
        print(f"🔍 DEBUG: About to call ChatService.process_chat_message")
        
        result = await ChatService.process_chat_message(
            db=db,
            user=current_user,
            conversation_id=conversation_id,
            message_content=message.strip()
        )
        
        print(f"🔍 DEBUG: ChatService returned: {result}")
        return result
        
    except Exception as e:
        print(f"❌ DEBUG: Exception occurred: {str(e)}")
        print(f"❌ DEBUG: Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/conversations")
async def get_user_conversations(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's conversation list with pagination.
    
    Returns conversations ordered by most recent activity.
    """
    conversations = ChatService.get_user_conversations(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
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
        "offset": offset
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all messages in a conversation.
    
    Verifies user owns the conversation before returning messages.
    """
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = ChatService.get_conversation_messages(db, conversation_id, limit)
    
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
        "total_messages": len(message_list)
    }


@router.put("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    new_title: str = Form(...),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """Update conversation title."""
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    updated_conversation = ChatService.update_conversation_title(
        db, conversation_id, new_title.strip()
    )
    
    return {
        "conversation_id": conversation_id,
        "new_title": updated_conversation.title,
        "updated_at": updated_conversation.updated_at.isoformat()
    }


@router.delete("/conversations/{conversation_id}")
async def archive_conversation(
    conversation_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """Archive (soft delete) a conversation."""
    success = ChatService.archive_conversation(db, conversation_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {
        "message": "Conversation archived successfully",
        "conversation_id": conversation_id
    }


@router.get("/stats")
async def get_chat_stats(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's chat statistics."""
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
        "questions_remaining": ChatService._get_remaining_questions(current_user)
    }