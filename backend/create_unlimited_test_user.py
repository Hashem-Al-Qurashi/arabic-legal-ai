#!/usr/bin/env python3
"""
Script to create an unlimited test user for testing purposes.
"""

import os
import sys
from sqlalchemy.orm import Session

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_unlimited_test_user():
    """Create a test user with unlimited access."""
    
    # Test user credentials
    test_email = "test@unlimited.local"
    test_password = "test123456"  # Simple password for testing
    test_name = "Unlimited Test User"
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            print(f"Test user {test_email} already exists!")
            print(f"User ID: {existing_user.id}")
            print(f"Subscription tier: {existing_user.subscription_tier}")
            
            # Update to unlimited if not already
            if existing_user.subscription_tier != "unlimited":
                existing_user.subscription_tier = "unlimited"
                existing_user.questions_used_this_month = 0
                existing_user.questions_used_current_cycle = 0
                existing_user.cycle_reset_time = None
                existing_user.is_active = True
                existing_user.is_verified = True
                db.commit()
                print("Updated existing user to unlimited tier!")
            
            return existing_user.id
        
        # Create new unlimited test user
        hashed_password = get_password_hash(test_password)
        
        test_user = User(
            email=test_email,
            hashed_password=hashed_password,
            full_name=test_name,
            is_active=True,
            is_verified=True,  # Pre-verified for testing
            subscription_tier="unlimited",  # Special tier for unlimited access
            questions_used_this_month=0,
            questions_used_current_cycle=0,
            cycle_reset_time=None
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Unlimited test user created successfully!")
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print(f"User ID: {test_user.id}")
        print(f"Subscription tier: {test_user.subscription_tier}")
        print("\nThis user will have unlimited questions for testing purposes.")
        
        return test_user.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test user: {str(e)}")
        return None
        
    finally:
        db.close()


if __name__ == "__main__":
    user_id = create_unlimited_test_user()
    if user_id:
        print(f"\n🎉 Test user ready! Use email 'test@unlimited.local' and password 'test123456' to login.")