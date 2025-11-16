# backend/app/api/chat.py - CLEAN REWRITE - ZERO TECH DEBT
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Form, Query, Header
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import json
import uuid
from datetime import datetime

from app.database import get_database
from app.dependencies.simple_auth import get_current_active_user, get_optional_current_user
from app.services.chat_service import ChatService
from app.services.cooldown_service import CooldownService
from app.services.guest_service import GuestService
from app.services.user_service import UserService
from app.models.user import User
from app.models.conversation import Conversation, Message
from rag_engine import get_rag_engine

router = APIRouter(prefix="/chat", tags=["chat"])

# ===== UTILITY FUNCTIONS =====

def _serialize_user_message(user_message) -> Dict[str, Any]:
    """Convert user message object to serializable dictionary"""
    return {
        'id': str(user_message.id),
        'content': str(user_message.content),
        'timestamp': user_message.created_at.isoformat() if hasattr(user_message, 'created_at') else datetime.utcnow().isoformat(),
        'role': 'user'
    }

def _serialize_ai_message(ai_message) -> Dict[str, Any]:
    """Convert AI message object to serializable dictionary"""
    return {
        'id': str(ai_message.id),
        'content': str(ai_message.content),
        'timestamp': ai_message.created_at.isoformat() if hasattr(ai_message, 'created_at') else datetime.utcnow().isoformat(),
        'role': 'assistant',
        'processing_time_ms': str(getattr(ai_message, 'processing_time_ms', 0))
    }

def _serialize_user_data(current_user: Optional[User]) -> Optional[Dict[str, Any]]:
    """Convert user object to serializable dictionary"""
    if not current_user:
        return None
    
    return {
        'id': str(current_user.id),
        'email': str(current_user.email),
        'full_name': str(current_user.full_name),
        'questions_used_current_cycle': int(current_user.questions_used_current_cycle),
        'cycle_reset_time': current_user.cycle_reset_time.isoformat() if current_user.cycle_reset_time else None,
        'subscription_tier': str(current_user.subscription_tier),
        'is_active': bool(current_user.is_active),
        'is_verified': bool(current_user.is_verified),
        'questions_remaining': int(_calculate_questions_remaining(current_user))
    }

def _calculate_questions_remaining(user: User) -> int:
    """Calculate remaining questions for user based on subscription."""
    if user.subscription_tier == "free":
        return max(0, 20 - user.questions_used_current_cycle)
    elif user.subscription_tier == "pro":
        return 999999
    else:  # enterprise
        return 999999

# ===== MAIN API ENDPOINT =====

@router.post("/message")
async def send_unified_chat_message(
    message: str = Form(..., description="User message"),
    conversation_id: Optional[str] = Form(None, description="Existing conversation ID (optional)"),
    session_id: Optional[str] = Form(None, description="Guest session ID (for guests only)"),
    enable_trust_trail: bool = Form(False, description="Enable multi-agent trust trail for transparency"),
    accept: str = Header("application/json", description="Response format: application/json or text/event-stream"),
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    UNIFIED CHAT API - Clean Implementation
    - Accept: application/json → Complete response
    - Accept: text/event-stream → Real-time streaming
    - Both modes support full conversation memory for guests and users
    """
    try:
        # 🛡️ SECURITY: Input validation to prevent injection attacks
        if not message or not isinstance(message, str):
            raise HTTPException(status_code=400, detail="Message is required and must be a string")
        
        # Sanitize message input
        message = message.strip()
        if len(message) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        if len(message) > 10000:  # Reasonable limit for legal questions
            raise HTTPException(status_code=400, detail="Message too long (max 10,000 characters)")
        
        # Validate conversation_id format if provided
        if conversation_id:
            if not isinstance(conversation_id, str) or len(conversation_id.strip()) == 0:
                raise HTTPException(status_code=400, detail="Invalid conversation ID format")
            # Basic UUID format validation
            import re
            if not re.match(r'^[a-f0-9-]{36}$', conversation_id.strip()):
                raise HTTPException(status_code=400, detail="Invalid conversation ID format")
            conversation_id = conversation_id.strip()
        
        # Validate session_id format if provided
        if session_id:
            if not isinstance(session_id, str) or len(session_id.strip()) == 0:
                raise HTTPException(status_code=400, detail="Invalid session ID format")
            session_id = session_id.strip()
        
        print(f"🔄 Processing unified message from {'user' if current_user else 'guest'}: {message[:50]}...")
        print(f"📡 Response format requested: {accept}")
        
        # ===== AUTHENTICATION & LIMITS =====
        if current_user:
            # Authenticated user flow
            user_type = "authenticated"
            
            # Check cooldown for authenticated users
            can_ask, cooldown_message, reset_time = CooldownService.can_ask_question(db, current_user)
            if not can_ask:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": cooldown_message,
                        "reset_time": reset_time.isoformat() if reset_time else None,
                        "user_type": user_type
                    }
                )
            
            # Use question for authenticated user
            if not CooldownService.use_question(db, current_user):
                raise HTTPException(status_code=500, detail="Failed to process question")
                
        else:
            # Guest user flow
            user_type = "guest"
            
            if not session_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session ID required for guest users"
                )
            
            # Check cooldown for guest users
            can_ask, cooldown_message, reset_time = GuestService.can_guest_ask_question(session_id)
            if not can_ask:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": cooldown_message,
                        "reset_time": reset_time.isoformat() if reset_time else None,
                        "user_type": user_type
                    }
                )
            
            # Use question for guest user
            if not GuestService.use_guest_question(session_id):
                raise HTTPException(status_code=500, detail="Failed to process question")
        
        # ===== CONTENT NEGOTIATION =====
        if "text/event-stream" in accept:
            # STREAMING MODE
            return StreamingResponse(
                _generate_streaming_response(
                    db, current_user, session_id, conversation_id, message, user_type
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        else:
            # JSON MODE (Complete Response)
            return await _generate_json_response(
                db, current_user, session_id, conversation_id, message, user_type
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions (cooldown, etc.)
        raise
    except Exception as e:
        # Rollback question usage on error
        if current_user:
            current_user.questions_used_current_cycle -= 1
            if current_user.questions_used_current_cycle <= 0:
                current_user.cycle_reset_time = None
            db.commit()
        elif session_id:
            guest_session = GuestService.get_guest_session(session_id)
            guest_session["questions_used"] -= 1
        
        print(f"❌ Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI processing failed: {str(e)}"
        )

# ===== STREAMING RESPONSE GENERATOR =====

async def _generate_streaming_response(
    db: Session,
    current_user: Optional[User],
    session_id: Optional[str],
    conversation_id: Optional[str],
    message_content: str,
    user_type: str
):
    """Generate real-time streaming response with conversation memory"""
    response_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    try:
        # ===== CONVERSATION SETUP =====
        if current_user:
            # Authenticated user: Database conversations
            if conversation_id:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == current_user.id
                ).first()
                if not conversation:
                    raise Exception("Conversation not found")
            else:
                # Create new conversation
                conversation = ChatService.create_conversation(
                    db, current_user.id,
                    title=message_content[:50] + "..." if len(message_content) > 50 else message_content
                )
                conversation_id = conversation.id
            
            # Add user message to database
            user_message = ChatService.add_message(
                db, conversation_id, "user", message_content
            )
            
            # Get conversation context
            context = ChatService.get_conversation_context(db, conversation_id, 10)
            
        else:
            # Guest user: Session-based conversations
            session = GuestService.get_guest_session(session_id)
            
            # Add conversation_history if it doesn't exist
            if "conversation_history" not in session:
                session["conversation_history"] = []
            
            # Add user message to session history
            session["conversation_history"].append({
                "role": "user",
                "content": message_content,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only last 20 messages to prevent memory bloat
            if len(session["conversation_history"]) > 20:
                session["conversation_history"] = session["conversation_history"][-20:]
            
            # Get context from session (last 10 messages, excluding current)
            history = session["conversation_history"]
            recent_messages = history[-11:-1] if len(history) > 10 else history[:-1]  # Exclude current message
            context = [{"role": msg["role"], "content": msg["content"]} for msg in recent_messages]
            
            # Create mock user message for response
            user_message = type('obj', (object,), {
                'id': f"guest_msg_{int(datetime.utcnow().timestamp())}",
                'content': message_content,
                'created_at': datetime.utcnow()
            })()
        
        # ===== SEND INITIAL METADATA =====
        metadata_payload = {
            'type': 'metadata', 
            'id': response_id, 
            'conversation_id': conversation_id, 
            'user_message': {
                'id': user_message.id, 
                'content': message_content, 
                'timestamp': user_message.created_at.isoformat()
            }
        }
        yield f"data: {json.dumps(metadata_payload)}\n\n"
        
        # ===== AI RESPONSE GENERATION =====
        full_response = ""
        chunk_count = 0
        
        # Get RAG engine and process
        rag_instance = get_rag_engine()
        
        print(f"🔄 Processing with RAG engine - context: {len(context)} messages")
        async for chunk in rag_instance.ask_question_with_context_streaming(message_content, context):
            if chunk and chunk.strip():
                full_response += chunk
                chunk_count += 1
                
                chunk_data = {
                    'type': 'chunk',
                    'content': chunk,
                    'chunk_id': chunk_count
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
        
        # ===== SAVE AI RESPONSE =====
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        if current_user:
            # Save to database
            ai_message = ChatService.add_message(
                db, conversation_id, "assistant", full_response,
                processing_time_ms=str(processing_time)
            )
            
            # Increment user question usage
            UserService.increment_question_usage(db, current_user.id)
            
            # Refresh user data
            db.refresh(current_user)
            
        else:
            # Save to session
            session["conversation_history"].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Create mock AI message
            ai_message = type('obj', (object,), {
                'id': f"guest_ai_{int(datetime.utcnow().timestamp())}",
                'content': full_response,
                'created_at': datetime.utcnow(),
                'processing_time_ms': str(processing_time)
            })()

        # ===== COMPLETION METADATA =====
        completion_data = {
            'type': 'complete',
            'id': str(response_id),
            'conversation_id': str(conversation_id) if conversation_id else None,
            'ai_message': _serialize_ai_message(ai_message),
            'updated_user': _serialize_user_data(current_user),
            'session_id': str(session_id) if session_id and not current_user else None,
            'user_type': str(user_type),
            'processing_time_ms': int(processing_time),
            'total_chunks': int(chunk_count),
            'processing_mode': 'standard'
        }
        
        yield f"data: {json.dumps(completion_data)}\n\n"
        yield "data: [DONE]\n\n"
        
        print(f"✅ Streaming completed: {chunk_count} chunks, {len(full_response)} characters")
        
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        import traceback
        traceback.print_exc()
        error_data = {
            'type': 'error',
            'error': str(e),
            'id': response_id,
            'processing_mode': 'error'
        }
        yield f"data: {json.dumps(error_data)}\n\n"
        yield "data: [DONE]\n\n"

# ===== JSON RESPONSE GENERATOR =====

async def _generate_json_response(
    db: Session,
    current_user: Optional[User],
    session_id: Optional[str],
    conversation_id: Optional[str],
    message_content: str,
    user_type: str
) -> JSONResponse:
    """Generate complete JSON response with conversation memory"""
    
    try:
        if current_user:
            # Use ChatService for authenticated users
            result = await ChatService.process_chat_message_with_multi_agent(
                db=db,
                user=current_user,
                conversation_id=conversation_id,
                message_content=message_content,
                enable_trust_trail=False,  # Simplified
                session_id=None
            )
            
            return JSONResponse(content=result)
            
        else:
            # Use ChatService for guest users
            result = await ChatService.process_chat_message_with_multi_agent(
                db=db,
                user=None,
                conversation_id=None,
                message_content=message_content,
                enable_trust_trail=False,
                session_id=session_id
            )
            
            return JSONResponse(content=result)
            
    except Exception as e:
        print(f"❌ JSON response error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )

# ===== CONVERSATION MANAGEMENT ENDPOINTS =====

@router.get("/conversations")
async def get_user_conversations(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's conversation list with pagination."""
    conversations = ChatService.get_user_conversations(db, current_user.id, limit)
    
    conversation_list = []
    for conv in conversations:
        messages = ChatService.get_conversation_messages(db, conv.id, limit=1)
        last_message = messages[-1] if messages else None
        
        conversation_list.append({
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "last_message_preview": (
                last_message.content[:100] + "..." 
                if last_message and len(last_message.content) > 100 
                else last_message.content if last_message else None
            ),
            "message_count": len(ChatService.get_conversation_messages(db, conv.id))
        })
    
    return {
        "conversations": conversation_list,
        "total": len(conversation_list),
        "current_user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "subscription_tier": current_user.subscription_tier,
            "questions_remaining": _calculate_questions_remaining(current_user)
        }
    }

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """Get messages from a specific conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = ChatService.get_conversation_messages(db, conversation_id, limit)
    
    message_list = []
    for msg in messages:
        message_list.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat(),
            "confidence_score": msg.confidence_score,
            "processing_time_ms": msg.processing_time_ms,
            "sources": json.loads(msg.sources) if msg.sources else []
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
    # 🛡️ SECURITY: Input validation
    if not new_title or not isinstance(new_title, str):
        raise HTTPException(status_code=400, detail="Title is required and must be a string")
    
    new_title = new_title.strip()
    if len(new_title) == 0:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if len(new_title) > 200:  # Reasonable limit for conversation titles
        raise HTTPException(status_code=400, detail="Title too long (max 200 characters)")
    
    # Validate conversation_id format
    import re
    if not re.match(r'^[a-f0-9-]{36}$', conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    updated_conversation = ChatService.update_conversation_title(db, conversation_id, new_title)
    
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
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "message": "Conversation archived successfully",
        "conversation_id": conversation_id
    }

@router.get("/status")
async def get_chat_status(
    session_id: Optional[str] = Query(None),
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get current chat status for both guests and signed-in users."""
    if current_user:
        return {
            "user_id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "subscription_tier": current_user.subscription_tier,
            "questions_used_current_cycle": current_user.questions_used_current_cycle,
            "questions_remaining": _calculate_questions_remaining(current_user),
            "user_type": "authenticated"
        }
    elif session_id:
        session = GuestService.get_guest_session(session_id)
        can_ask, message, reset_time = GuestService.can_guest_ask_question(session_id)
        
        return {
            "questions_available": CooldownService.GUEST_QUESTION_LIMIT - session["questions_used"],
            "questions_used": session["questions_used"],
            "max_questions": CooldownService.GUEST_QUESTION_LIMIT,
            "can_ask_question": can_ask,
            "reset_time": reset_time.isoformat() if reset_time else None,
            "user_type": "guest"
        }
    else:
        raise HTTPException(status_code=400, detail="Session ID required for guest users")

# ===== ENSEMBLE TESTING ENDPOINTS =====

@router.post("/message/ensemble")
async def send_ensemble_chat_message(
    message: str = Form(..., description="User message"),
    enable_streaming: bool = Form(False, description="Enable streaming responses"),
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    ENSEMBLE SYSTEM ENDPOINT - For Testing & Validation
    
    Process query using the complete ensemble pipeline:
    1. Context retrieval (existing RAG)
    2. 4-model parallel generation 
    3. 3-judge component extraction
    4. Consensus building & response assembly
    5. Quality verification & data collection
    
    ⚠️ EXPENSIVE: ~$0.29 per query - use for testing only!
    """
    try:
        # Import ensemble system
        from ensemble_engine import process_ensemble_query, process_ensemble_streaming
        
        # Basic validation
        if not message or not isinstance(message, str):
            raise HTTPException(status_code=400, detail="Message is required and must be a string")
        
        message = message.strip()
        if len(message) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        if len(message) > 5000:
            raise HTTPException(status_code=400, detail="Message too long for ensemble processing (max 5,000 characters)")
        
        print(f"🚀 ENSEMBLE: Processing query: {message[:50]}...")
        
        if enable_streaming:
            # Streaming response
            async def ensemble_stream():
                try:
                    async for update in process_ensemble_streaming(message):
                        yield f"data: {json.dumps(update, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    error_data = {
                        "type": "error",
                        "error": str(e),
                        "message": "Ensemble processing failed"
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                ensemble_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        else:
            # Complete response
            result = await process_ensemble_query(message)
            
            # Format for client compatibility
            response_data = {
                "conversation_id": result.get("request_id"),
                "user_message": {
                    "content": message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "role": "user"
                },
                "ai_message": {
                    "content": result["final_response"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "role": "assistant",
                    "processing_time_ms": result["processing_time_ms"]
                },
                "processing_time_ms": result["processing_time_ms"],
                "cost_estimate": result["cost_estimate"],
                "quality_report": result["quality_report"],
                "ensemble_data": result["ensemble_data"],
                "updated_user": _serialize_user_data(current_user),
                "user_questions_remaining": 999,  # Ensemble testing - no limits
                
                # Ensemble-specific metadata
                "processing_mode": "ensemble",
                "system_type": "4-model + 3-judge ensemble",
                "components_used": result["ensemble_data"].get("consensus_components", 0),
                "models_used": result["ensemble_data"].get("generator_responses", 0)
            }
            
            return JSONResponse(content=response_data)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ENSEMBLE ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Ensemble processing failed: {str(e)}",
                "system_type": "ensemble",
                "error_type": "processing_error"
            }
        )

@router.get("/ensemble/stats")
async def get_ensemble_stats():
    """Get ensemble system statistics and health"""
    try:
        from ensemble_engine import get_ensemble_stats
        stats = get_ensemble_stats()
        
        return {
            "ensemble_status": "active",
            "stats": stats,
            "endpoints": {
                "ensemble_query": "/api/chat/message/ensemble",
                "ensemble_streaming": "/api/chat/message/ensemble?enable_streaming=true"
            },
            "cost_warning": "⚠️ Ensemble costs ~$0.29 per query - use for testing only",
            "features": {
                "multi_model": "4 AI models (ChatGPT, DeepSeek, Grok, Gemini)",
                "judges": "3 judge models (Claude, GPT-4o, Gemini)", 
                "components": "7 component extraction types",
                "assembly": "AI-powered response assembly",
                "quality_verification": "Automated quality checks",
                "data_collection": "Training data pipeline for fine-tuning"
            }
        }
        
    except Exception as e:
        return {
            "ensemble_status": "error", 
            "error": str(e),
            "message": "Ensemble system not available"
        }

@router.post("/message/vanilla-ensemble")
async def send_vanilla_ensemble_message(
    message: str = Form(..., description="User message"),
    enable_streaming: bool = Form(False, description="Enable streaming responses"),
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    VANILLA ENSEMBLE ENDPOINT - Pure Model Comparison
    
    Process query using pure vanilla ensemble:
    1. Send SAME question to 4 models (no RAG context)
    2. 3 judges extract best components from each response
    3. Assemble best parts into superior final response
    
    🍦 VANILLA: No RAG, no context - just pure model comparison!
    💰 COST: ~$0.21 per query (with 2 models available)
    """
    try:
        # Import vanilla ensemble system
        from vanilla_ensemble import process_vanilla_ensemble_query, process_vanilla_ensemble_streaming
        
        # Basic validation
        if not message or not isinstance(message, str):
            raise HTTPException(status_code=400, detail="Message is required and must be a string")
        
        message = message.strip()
        if len(message) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        if len(message) > 5000:
            raise HTTPException(status_code=400, detail="Message too long for vanilla ensemble (max 5,000 characters)")
        
        print(f"🍦 VANILLA ENSEMBLE: Processing query: {message[:50]}...")
        
        if enable_streaming:
            # Streaming response
            async def vanilla_ensemble_stream():
                try:
                    async for update in process_vanilla_ensemble_streaming(message):
                        yield f"data: {json.dumps(update, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    error_data = {
                        "type": "error",
                        "error": str(e),
                        "message": "Vanilla ensemble processing failed"
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                vanilla_ensemble_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        else:
            # Complete response
            result = await process_vanilla_ensemble_query(message)
            
            # Format for client compatibility
            response_data = {
                "conversation_id": result.get("request_id"),
                "user_message": {
                    "content": message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "role": "user"
                },
                "ai_message": {
                    "content": result["final_response"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "role": "assistant",
                    "processing_time_ms": result["processing_time_ms"]
                },
                "processing_time_ms": result["processing_time_ms"],
                "cost_estimate": result["cost_estimate"],
                "vanilla_ensemble_data": result["vanilla_data"],
                "updated_user": _serialize_user_data(current_user),
                "user_questions_remaining": 999,
                
                # Vanilla ensemble metadata
                "processing_mode": "vanilla_ensemble",
                "system_type": "Pure vanilla 4-model + 3-judge ensemble",
                "rag_used": False,
                "context_provided": False,
                "models_used": result["vanilla_data"].get("generator_responses", 0),
                "judges_used": result["vanilla_data"].get("judge_evaluations", 0),
                "components_extracted": result["vanilla_data"].get("consensus_components", 0)
            }
            
            return JSONResponse(content=response_data)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ VANILLA ENSEMBLE ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Vanilla ensemble processing failed: {str(e)}",
                "system_type": "vanilla_ensemble",
                "error_type": "processing_error"
            }
        )

@router.get("/vanilla-ensemble/stats")
async def get_vanilla_ensemble_stats():
    """Get vanilla ensemble system statistics and health"""
    try:
        from vanilla_ensemble import get_vanilla_ensemble_stats
        stats = get_vanilla_ensemble_stats()
        
        return {
            "vanilla_ensemble_status": "active",
            "stats": stats,
            "endpoints": {
                "vanilla_ensemble_query": "/api/chat/message/vanilla-ensemble",
                "vanilla_ensemble_streaming": "/api/chat/message/vanilla-ensemble?enable_streaming=true"
            },
            "description": "🍦 Pure vanilla ensemble - no RAG, just 4 models + 3 judges + component extraction",
            "cost_info": "💰 ~$0.21 per query (with current models available)",
            "features": {
                "vanilla_models": "4 AI models respond to same question (no context)",
                "judges": "3 judge models extract best components", 
                "components": "7 component types extracted and assembled",
                "assembly": "AI-powered smooth response assembly",
                "no_rag": "Pure model comparison without document retrieval"
            }
        }
        
    except Exception as e:
        return {
            "vanilla_ensemble_status": "error", 
            "error": str(e),
            "message": "Vanilla ensemble system not available"
        }