"""
API route handlers for the Arabic Legal Assistant.
"""

from app.api.auth import router as auth_router
from app.api.users import router as users_router

__all__ = ["auth_router", "users_router"]