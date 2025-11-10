#!/usr/bin/env python3
"""
Create unlimited admin/testing accounts for production testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
import uuid

# Database URL for production
DATABASE_URL = "sqlite:///./backend/arabic_legal.db"

def create_admin_accounts():
    """Create admin accounts with unlimited access"""
    
    # Create database connection
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Admin accounts to create
        admin_accounts = [
            {
                "email": "admin@hokm.ai",
                "password": "AdminTest123!",
                "full_name": "Admin User",
                "subscription_tier": "admin"
            },
            {
                "email": "test1@hokm.ai", 
                "password": "TestUser123!",
                "full_name": "Test User 1",
                "subscription_tier": "testing"
            },
            {
                "email": "test2@hokm.ai",
                "password": "TestUser123!",
                "full_name": "Test User 2", 
                "subscription_tier": "testing"
            },
            {
                "email": "test3@hokm.ai",
                "password": "TestUser123!",
                "full_name": "Test User 3",
                "subscription_tier": "testing"
            },
            {
                "email": "colleague1@hokm.ai",
                "password": "Colleague123!",
                "full_name": "Colleague 1",
                "subscription_tier": "unlimited"
            },
            {
                "email": "colleague2@hokm.ai",
                "password": "Colleague123!",
                "full_name": "Colleague 2",
                "subscription_tier": "unlimited"
            }
        ]
        
        created_accounts = []
        
        for account_data in admin_accounts:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == account_data["email"]).first()
            
            if existing_user:
                # Update existing user to admin tier
                existing_user.subscription_tier = account_data["subscription_tier"]
                existing_user.is_active = True
                existing_user.is_verified = True
                db.commit()
                print(f"✅ Updated existing user: {account_data['email']} -> {account_data['subscription_tier']} tier")
                created_accounts.append(account_data)
            else:
                # Create new admin user
                hashed_password = get_password_hash(account_data["password"])
                
                new_user = User(
                    id=str(uuid.uuid4()),
                    email=account_data["email"],
                    hashed_password=hashed_password,
                    full_name=account_data["full_name"],
                    is_active=True,
                    is_verified=True,
                    subscription_tier=account_data["subscription_tier"],
                    questions_used_this_month=0,
                    questions_used_current_cycle=0,
                    auth_provider="email"
                )
                
                db.add(new_user)
                db.commit()
                print(f"✅ Created admin user: {account_data['email']} -> {account_data['subscription_tier']} tier")
                created_accounts.append(account_data)
        
        print(f"\n🎉 Successfully created/updated {len(created_accounts)} admin accounts!")
        print("\n📋 Admin Account Details:")
        print("=" * 60)
        
        for account in created_accounts:
            print(f"Email: {account['email']}")
            print(f"Password: {account['password']}")
            print(f"Tier: {account['subscription_tier']} (UNLIMITED ACCESS)")
            print(f"Name: {account['full_name']}")
            print("-" * 40)
        
        print("\n🚀 These accounts have:")
        print("   • Unlimited questions (999,999 per cycle)")
        print("   • No cooldown restrictions")
        print("   • No monthly limits")
        print("   • Full access to all features")
        print("   • Can test Google OAuth and regular auth")
        
        print("\n🌐 Test on production:")
        print("   • Visit your CloudFront domain")
        print("   • Login with any of the above credentials")
        print("   • Test unlimited chat functionality")
        
        return created_accounts
        
    except Exception as e:
        print(f"❌ Error creating admin accounts: {e}")
        db.rollback()
        return []
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Creating unlimited admin accounts for production testing...")
    print("=" * 70)
    
    accounts = create_admin_accounts()
    
    if accounts:
        print("\n✅ Admin account creation completed successfully!")
        print("🚀 You can now test unlimited access on production!")
    else:
        print("\n❌ Failed to create admin accounts")
        sys.exit(1)