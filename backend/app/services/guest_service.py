"""
Guest session management for tracking question limits.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


class GuestService:
    """Service for managing guest user question limits"""
    
    # In-memory storage for guest sessions (in production, use Redis)
    guest_sessions = {}
    
    @staticmethod
    def get_guest_session(session_id: str) -> Dict:
        """Get or create guest session data"""
        if session_id not in GuestService.guest_sessions:
            GuestService.guest_sessions[session_id] = {
                "questions_used": 0,
                "reset_time": None,
                "created_at": datetime.utcnow()
            }
        return GuestService.guest_sessions[session_id]
    
    @staticmethod
    def can_guest_ask_question(session_id: str) -> Tuple[bool, str, Optional[datetime]]:
        """Check if guest can ask a question"""
        from app.services.cooldown_service import CooldownService
        
        session = GuestService.get_guest_session(session_id)
        now = datetime.utcnow()
        
        # Check if reset time has passed
        if session["reset_time"] and now >= session["reset_time"]:
            session["questions_used"] = 0
            session["reset_time"] = None
        
        questions_available = CooldownService.GUEST_QUESTION_LIMIT - session["questions_used"]
        
        if questions_available > 0:
            return True, "OK", None
        
        if session["reset_time"]:
            return False, f"Questions will refill at {session['reset_time'].strftime('%I:%M %p')}", session["reset_time"]
        
        return False, "Question limit reached", None
    
    @staticmethod
    def use_guest_question(session_id: str) -> bool:
        """Use one question for guest user"""
        from app.services.cooldown_service import CooldownService
        
        can_ask, message, reset_time = GuestService.can_guest_ask_question(session_id)
        
        if not can_ask:
            return False
        
        session = GuestService.get_guest_session(session_id)
        session["questions_used"] += 1
        
        # Check if they've hit the limit
        if session["questions_used"] >= CooldownService.GUEST_QUESTION_LIMIT:
            session["reset_time"] = datetime.utcnow() + timedelta(hours=CooldownService.COOLDOWN_DURATION_HOURS)
        
        return True