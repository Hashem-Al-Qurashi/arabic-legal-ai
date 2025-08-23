"""
Simple Islamic Database Manager
RULE: No over-engineering - just basic database connection
RULE: Zero impact on existing legal system
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class IslamicDatabaseManager:
    """
    Simple Islamic database connection manager
    Only connects to Islamic databases, never touches existing civil law DBs
    """
    
    def __init__(self, db_path: str = "data/quranic_foundations.db"):
        """Simple initialization - just store path, don't connect yet"""
        self.db_path = db_path
        self.connection = None
        
    def connect(self) -> bool:
        """Simple connection test - returns True/False"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Dict-like access
            logger.info(f"✅ Islamic DB connected: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Islamic DB connection failed: {e}")
            return False
    
    def test_connection(self) -> Dict[str, any]:
        """Simple connection test with basic stats - updated for actual DB structure"""
        if not self.connect():
            return {"status": "failed", "error": "Cannot connect to Islamic database"}
        
        try:
            cursor = self.connection.cursor()
            
            # Check actual tables that exist
            cursor.execute("SELECT COUNT(*) FROM quranic_verses")
            total_verses = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tafseer_chunks")
            total_chunks = cursor.fetchone()[0]
            
            # Test one record from each table
            cursor.execute("SELECT id, surah_name, verse_reference FROM quranic_verses LIMIT 1")
            sample_verse = cursor.fetchone()
            
            cursor.execute("SELECT chunk_id, content FROM tafseer_chunks LIMIT 1")
            sample_chunk = cursor.fetchone()
            
            return {
                "status": "success",
                "total_verses": total_verses,
                "total_chunks": total_chunks,
                "sample_verse": dict(sample_verse) if sample_verse else None,
                "sample_chunk": dict(sample_chunk) if sample_chunk else None,
                "database_path": self.db_path
            }
            
        except Exception as e:
            logger.error(f"❌ Islamic DB test failed: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            if self.connection:
                self.connection.close()
    
    def get_foundation_by_id(self, foundation_id: str) -> Optional[Dict]:
        """Simple foundation retrieval by ID"""
        if not self.connect():
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT foundation_id, verse_text, surah_name, ayah_number, verse_reference,
                       qurtubi_commentary, legal_principle, principle_category,
                       applicable_legal_domains, modern_applications,
                       cultural_appropriateness, scholarship_confidence, legal_relevance_score
                FROM quranic_foundations 
                WHERE foundation_id = ?
            """, (foundation_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"❌ Get foundation failed: {e}")
            return None
        finally:
            if self.connection:
                self.connection.close()
    
    def close(self):
        """Simple cleanup"""
        if self.connection:
            self.connection.close()
            self.connection = None

# Simple test function - no over-engineering
async def test_islamic_database():
    """Simple test to verify Islamic database works independently"""
    logger.info("🧪 Testing Islamic Database Manager...")
    
    db_manager = IslamicDatabaseManager()
    test_result = db_manager.test_connection()
    
    if test_result["status"] == "success":
        logger.info(f"✅ Islamic DB working - {test_result['total_foundations']} foundations available")
        return True
    else:
        logger.error(f"❌ Islamic DB test failed: {test_result.get('error', 'Unknown error')}")
        return False

# Only export what we need - keep it simple
__all__ = ["IslamicDatabaseManager", "test_islamic_database"]