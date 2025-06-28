"""
Database models package.
"""

from sqlalchemy.orm import relationship
from app.models.user import User
from app.models.consultation import Consultation

# Add the relationship after both models are defined
User.consultations = relationship("Consultation", back_populates="user")

__all__ = ["User", "Consultation"]