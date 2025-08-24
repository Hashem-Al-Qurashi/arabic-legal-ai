# backend/app/core/session_config.py - Enterprise Session Configuration
"""
Centralized configuration for all session management
Eliminates hardcoding - enterprise approach
"""
import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class SessionConfig:
    """Enterprise session configuration - NO HARDCODING"""
    
    # Guest limits (configurable)
    GUEST_QUESTION_LIMIT: int = int(os.getenv('GUEST_QUESTION_LIMIT', '5'))
    GUEST_MESSAGE_HISTORY_LIMIT: int = int(os.getenv('GUEST_MESSAGE_HISTORY_LIMIT', '20'))
    GUEST_SESSION_TTL_MINUTES: int = int(os.getenv('GUEST_SESSION_TTL_MINUTES', '60'))
    
    # User limits (configurable) 
    USER_QUESTION_LIMIT: int = int(os.getenv('USER_QUESTION_LIMIT', '20'))
    USER_MESSAGE_HISTORY_LIMIT: int = int(os.getenv('USER_MESSAGE_HISTORY_LIMIT', '100'))
    
    # Cooldown configuration (configurable)
    COOLDOWN_DURATION_MINUTES: int = int(os.getenv('COOLDOWN_DURATION_MINUTES', '90'))
    
    # Memory management (configurable)
    MAX_GUEST_SESSIONS: int = int(os.getenv('MAX_GUEST_SESSIONS', '10000'))
    CLEANUP_INTERVAL_MINUTES: int = int(os.getenv('CLEANUP_INTERVAL_MINUTES', '30'))
    
    # Session ID configuration
    SESSION_ID_PREFIX: str = os.getenv('SESSION_ID_PREFIX', 'guest')
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary for monitoring"""
        return {
            'guest_question_limit': self.GUEST_QUESTION_LIMIT,
            'guest_message_limit': self.GUEST_MESSAGE_HISTORY_LIMIT,
            'guest_session_ttl_minutes': self.GUEST_SESSION_TTL_MINUTES,
            'user_question_limit': self.USER_QUESTION_LIMIT,
            'cooldown_duration_minutes': self.COOLDOWN_DURATION_MINUTES,
            'max_guest_sessions': self.MAX_GUEST_SESSIONS,
            'cleanup_interval_minutes': self.CLEANUP_INTERVAL_MINUTES
        }


# Global configuration instance
session_config = SessionConfig()