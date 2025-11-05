#!/usr/bin/env python3
"""
Manual migration script to add Google OAuth fields to the database.
This script directly modifies the SQLite database to add the necessary columns.
"""

import sqlite3
import sys

def add_google_oauth_fields():
    """Add Google OAuth fields to the users table if they don't exist"""
    try:
        # Connect to database
        conn = sqlite3.connect('data/arabic_legal.db')
        cursor = conn.cursor()
        
        # Check if google_id column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'google_id' not in columns:
            print("Adding google_id column...")
            cursor.execute("ALTER TABLE users ADD COLUMN google_id VARCHAR(255)")
            print("✅ Added google_id column")
        else:
            print("✓ google_id column already exists")
        
        if 'auth_provider' not in columns:
            print("Adding auth_provider column...")
            cursor.execute("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(50) DEFAULT 'email'")
            print("✅ Added auth_provider column")
        else:
            print("✓ auth_provider column already exists")
        
        # Create index on google_id if it doesn't exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='ix_users_google_id'
        """)
        if not cursor.fetchone():
            print("Creating index on google_id...")
            cursor.execute("CREATE UNIQUE INDEX ix_users_google_id ON users(google_id)")
            print("✅ Created index on google_id")
        else:
            print("✓ Index on google_id already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        print("\n📊 Current users table schema:")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            if col[1] in ['google_id', 'auth_provider']:
                print(f"  - {col[1]}: {col[2]} {'(NEW)' if col[1] in ['google_id', 'auth_provider'] else ''}")
        
        conn.close()
        print("\n✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_google_oauth_fields()
    sys.exit(0 if success else 1)