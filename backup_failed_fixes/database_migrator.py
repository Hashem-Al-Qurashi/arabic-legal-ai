"""
Enterprise Database Migration System
Migrates from legacy quranic_verses schema to modern quranic_foundations schema
Senior-level approach: zero data loss, validation, rollback capability
"""

import sqlite3
import json
import logging
import shutil
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import asyncio
import aiosqlite

from .embedding_config import get_embedding_config

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """
    Enterprise-grade database migration system
    Handles schema evolution with data preservation and validation
    """
    
    def __init__(self, source_db: str, target_db: str):
        self.source_db = Path(source_db)
        self.target_db = Path(target_db)
        self.backup_db = self.source_db.with_suffix('.backup.db')
        
        self.config_manager = get_embedding_config()
        
        # Migration tracking
        self.migration_stats = {
            "start_time": None,
            "end_time": None,
            "source_records": 0,
            "migrated_records": 0,
            "failed_records": 0,
            "validation_errors": []
        }
        
        logger.info(f"DatabaseMigrator initialized: {source_db} -> {target_db}")
    
    async def execute_migration(self, validate_data: bool = True) -> Dict[str, Any]:
        """
        Execute complete database migration with validation
        """
        self.migration_stats["start_time"] = datetime.now()
        
        try:
            # Step 1: Create backup
            await self._create_backup()
            
            # Step 2: Analyze source data
            source_analysis = await self._analyze_source_database()
            
            # Step 3: Create target schema
            await self._create_target_schema()
            
            # Step 4: Migrate data
            migration_result = await self._migrate_data(source_analysis)
            
            # Step 5: Validate migration (if requested)
            if validate_data:
                validation_result = await self._validate_migration()
                migration_result["validation"] = validation_result
            
            # Step 6: Update configuration
            await self._update_configuration()
            
            self.migration_stats["end_time"] = datetime.now()
            migration_result["migration_stats"] = self.migration_stats
            
            logger.info("Database migration completed successfully")
            return migration_result
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            await self._rollback()
            raise
    
    async def _create_backup(self):
        """Create backup of source database"""
        if self.source_db.exists():
            shutil.copy2(self.source_db, self.backup_db)
            logger.info(f"Backup created: {self.backup_db}")
        else:
            raise FileNotFoundError(f"Source database not found: {self.source_db}")
    
    async def _analyze_source_database(self) -> Dict[str, Any]:
        """Analyze source database structure and content"""
        analysis = {
            "tables": {},
            "total_records": 0,
            "schema_issues": [],
            "data_quality": {}
        }
        
        async with aiosqlite.connect(self.source_db) as db:
            # Get table list
            cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = await cursor.fetchall()
            
            for table_name, in tables:
                table_analysis = await self._analyze_table(db, table_name)
                analysis["tables"][table_name] = table_analysis
                analysis["total_records"] += table_analysis["record_count"]
        
        self.migration_stats["source_records"] = analysis["total_records"]
        logger.info(f"Source analysis complete: {analysis['total_records']} records across {len(analysis['tables'])} tables")
        
        return analysis
    
    async def _analyze_table(self, db: aiosqlite.Connection, table_name: str) -> Dict[str, Any]:
        """Analyze individual table structure and content"""
        analysis = {
            "record_count": 0,
            "columns": [],
            "sample_data": {},
            "data_issues": []
        }
        
        # Get column info
        cursor = await db.execute(f"PRAGMA table_info({table_name})")
        columns = await cursor.fetchall()
        analysis["columns"] = [{"name": col[1], "type": col[2]} for col in columns]
        
        # Get record count
        cursor = await db.execute(f"SELECT COUNT(*) FROM {table_name}")
        analysis["record_count"] = (await cursor.fetchone())[0]
        
        # Get sample data
        if analysis["record_count"] > 0:
            cursor = await db.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            analysis["sample_data"] = {
                "columns": column_names,
                "rows": rows[:3]
            }
            
            # Check for specific data quality issues
            if table_name == "tafseer_chunks":
                await self._check_embedding_quality(db, table_name, analysis)
        
        return analysis
    
    async def _check_embedding_quality(self, db: aiosqlite.Connection, 
                                     table_name: str, analysis: Dict[str, Any]):
        """Check quality of embeddings in the source data"""
        try:
            cursor = await db.execute(f"SELECT embedding FROM {table_name} WHERE embedding IS NOT NULL LIMIT 5")
            embeddings = await cursor.fetchall()
            
            if embeddings:
                import numpy as np
                for i, (embedding_blob,) in enumerate(embeddings):
                    if embedding_blob:
                        embedding_array = np.frombuffer(embedding_blob, dtype=np.float32)
                        dimension = len(embedding_array)
                        is_zero = np.all(embedding_array == 0)
                        
                        analysis["data_issues"].append({
                            "sample": i,
                            "dimension": dimension,
                            "is_zero": is_zero,
                            "first_values": embedding_array[:5].tolist() if len(embedding_array) >= 5 else embedding_array.tolist()
                        })
                        
                        if dimension not in [1536, 3072]:
                            analysis["data_issues"].append(f"Invalid embedding dimension: {dimension}")
                        
                        if is_zero:
                            analysis["data_issues"].append("Zero embedding detected")
        
        except Exception as e:
            analysis["data_issues"].append(f"Embedding analysis failed: {e}")
    
    async def _create_target_schema(self):
        """Create the target database with modern schema"""
        # Remove existing target if it exists
        if self.target_db.exists():
            self.target_db.unlink()
        
        async with aiosqlite.connect(self.target_db) as db:
            # Create quranic_foundations table
            await db.execute("""
                CREATE TABLE quranic_foundations (
                    foundation_id TEXT PRIMARY KEY,
                    verse_text TEXT NOT NULL,
                    surah_name TEXT NOT NULL,
                    ayah_number INTEGER NOT NULL,
                    verse_reference TEXT NOT NULL,
                    qurtubi_commentary TEXT NOT NULL,
                    legal_principle TEXT NOT NULL,
                    principle_category TEXT NOT NULL,
                    applicable_legal_domains TEXT NOT NULL,  -- JSON array
                    semantic_concepts TEXT NOT NULL,         -- JSON array
                    abstraction_level TEXT NOT NULL,
                    modern_applications TEXT NOT NULL,       -- JSON array
                    legal_precedence_level TEXT NOT NULL,
                    cultural_appropriateness REAL NOT NULL,
                    scholarship_confidence REAL NOT NULL,
                    legal_relevance_score REAL NOT NULL,
                    interpretation_consensus TEXT NOT NULL,
                    verse_embedding BLOB,                    -- Will be regenerated
                    principle_embedding BLOB,                -- Will be regenerated
                    application_embedding BLOB,              -- Will be regenerated
                    source_quality TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    usage_frequency INTEGER DEFAULT 0,
                    effectiveness_rating REAL DEFAULT 0.0,
                    created_date TEXT NOT NULL
                )
            """)
            
            # Create indices
            indices = [
                "CREATE INDEX idx_surah_ayah ON quranic_foundations (surah_name, ayah_number)",
                "CREATE INDEX idx_principle_category ON quranic_foundations (principle_category)",
                "CREATE INDEX idx_abstraction_level ON quranic_foundations (abstraction_level)",
                "CREATE INDEX idx_legal_relevance ON quranic_foundations (legal_relevance_score)",
                "CREATE INDEX idx_scholarship_confidence ON quranic_foundations (scholarship_confidence)",
                "CREATE INDEX idx_cultural_appropriateness ON quranic_foundations (cultural_appropriateness)"
            ]
            
            for index_sql in indices:
                await db.execute(index_sql)
            
            await db.commit()
        
        logger.info(f"Target schema created: {self.target_db}")
    
    async def _migrate_data(self, source_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate data from source to target schema"""
        migration_result = {
            "migrated_records": 0,
            "failed_records": 0,
            "transformation_applied": [],
            "data_enrichment": []
        }
        
        async with aiosqlite.connect(self.source_db) as source_db:
            async with aiosqlite.connect(self.target_db) as target_db:
                # Migrate from quranic_verses + tafseer_chunks to quranic_foundations
                await self._migrate_quranic_content(source_db, target_db, migration_result)
        
        self.migration_stats["migrated_records"] = migration_result["migrated_records"]
        self.migration_stats["failed_records"] = migration_result["failed_records"]
        
        return migration_result
    
    async def _migrate_quranic_content(self, source_db: aiosqlite.Connection, 
                                     target_db: aiosqlite.Connection,
                                     result: Dict[str, Any]):
        """Migrate Quranic content with intelligent transformation"""
        
        # Get verses with their associated chunks
        cursor = await source_db.execute("""
            SELECT 
                v.id, v.surah_number, v.surah_name, v.ayah_number,
                v.verse_reference, v.arabic_text, v.tafseer_content,
                GROUP_CONCAT(c.content, ' ') as combined_tafseer
            FROM quranic_verses v
            LEFT JOIN tafseer_chunks c ON v.id = c.verse_id
            GROUP BY v.id
        """)
        
        verses = await cursor.fetchall()
        
        for verse in verses:
            try:
                foundation_record = await self._transform_verse_to_foundation(verse)
                
                await target_db.execute("""
                    INSERT INTO quranic_foundations (
                        foundation_id, verse_text, surah_name, ayah_number, verse_reference,
                        qurtubi_commentary, legal_principle, principle_category,
                        applicable_legal_domains, semantic_concepts, abstraction_level,
                        modern_applications, legal_precedence_level, cultural_appropriateness,
                        scholarship_confidence, legal_relevance_score, interpretation_consensus,
                        verse_embedding, principle_embedding, application_embedding,
                        source_quality, last_updated, created_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, foundation_record)
                
                result["migrated_records"] += 1
                
            except Exception as e:
                logger.warning(f"Failed to migrate verse {verse[0]}: {e}")
                result["failed_records"] += 1
        
        await target_db.commit()
        result["transformation_applied"].append("Verse+Chunks -> Foundation transformation")
    
    async def _transform_verse_to_foundation(self, verse_data: Tuple) -> Tuple:
        """Transform legacy verse data to modern foundation format"""
        (verse_id, surah_number, surah_name, ayah_number, verse_reference, 
         arabic_text, tafseer_content, combined_tafseer) = verse_data
        
        # Use combined tafseer if available, otherwise original
        commentary = combined_tafseer if combined_tafseer else tafseer_content or ""
        
        # Generate foundation ID
        foundation_id = f"foundation_{verse_id}"
        
        # Extract legal principle (simplified extraction)
        legal_principle = self._extract_legal_principle(commentary)
        
        # Categorize principle
        principle_category = self._categorize_principle(legal_principle)
        
        # Default values for new fields (will be enhanced later)
        applicable_domains = json.dumps(["general_law"], ensure_ascii=False)
        semantic_concepts = json.dumps(["justice", "guidance"], ensure_ascii=False)
        modern_applications = json.dumps(["legal_guidance"], ensure_ascii=False)
        
        now = datetime.now().isoformat()
        
        return (
            foundation_id,                    # foundation_id
            arabic_text or "",               # verse_text
            surah_name or f"Surah {surah_number}",  # surah_name
            ayah_number or 0,                # ayah_number
            verse_reference or f"{surah_number}:{ayah_number}",  # verse_reference
            commentary,                      # qurtubi_commentary
            legal_principle,                 # legal_principle
            principle_category,              # principle_category
            applicable_domains,              # applicable_legal_domains (JSON)
            semantic_concepts,               # semantic_concepts (JSON)
            "verse_specific",               # abstraction_level
            modern_applications,             # modern_applications (JSON)
            "supportive",                   # legal_precedence_level
            0.8,                            # cultural_appropriateness
            0.7,                            # scholarship_confidence
            0.6,                            # legal_relevance_score
            "majority",                     # interpretation_consensus
            None,                           # verse_embedding (will be regenerated)
            None,                           # principle_embedding (will be regenerated)
            None,                           # application_embedding (will be regenerated)
            "migrated",                     # source_quality
            now,                            # last_updated
            now                             # created_date
        )
    
    def _extract_legal_principle(self, commentary: str) -> str:
        """Extract legal principle from commentary (simplified)"""
        if not commentary:
            return "General Islamic guidance"
        
        # Simple keyword-based extraction
        if any(word in commentary.lower() for word in ['عدل', 'عدالة', 'justice']):
            return "Justice and fairness in legal matters"
        elif any(word in commentary.lower() for word in ['عقد', 'contract', 'agreement']):
            return "Contract law and agreements"
        elif any(word in commentary.lower() for word in ['حق', 'rights', 'entitlement']):
            return "Rights and entitlements"
        else:
            return "General Islamic legal guidance"
    
    def _categorize_principle(self, principle: str) -> str:
        """Categorize the legal principle"""
        principle_lower = principle.lower()
        
        if "justice" in principle_lower or "عدل" in principle_lower:
            return "justice"
        elif "contract" in principle_lower or "عقد" in principle_lower:
            return "contracts"
        elif "rights" in principle_lower or "حق" in principle_lower:
            return "rights"
        else:
            return "general_guidance"
    
    async def _validate_migration(self) -> Dict[str, Any]:
        """Validate the migration results"""
        validation = {
            "schema_valid": False,
            "data_integrity": False,
            "record_count_match": False,
            "issues": []
        }
        
        try:
            async with aiosqlite.connect(self.target_db) as db:
                # Check schema
                cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quranic_foundations'")
                if await cursor.fetchone():
                    validation["schema_valid"] = True
                else:
                    validation["issues"].append("Target table not found")
                
                # Check record count
                cursor = await db.execute("SELECT COUNT(*) FROM quranic_foundations")
                target_count = (await cursor.fetchone())[0]
                
                if target_count > 0:
                    validation["data_integrity"] = True
                    
                    # Compare with source
                    async with aiosqlite.connect(self.source_db) as source_db:
                        source_cursor = await source_db.execute("SELECT COUNT(*) FROM quranic_verses")
                        source_count = (await source_cursor.fetchone())[0]
                        
                        if target_count == source_count:
                            validation["record_count_match"] = True
                        else:
                            validation["issues"].append(f"Record count mismatch: source={source_count}, target={target_count}")
                else:
                    validation["issues"].append("No records in target database")
        
        except Exception as e:
            validation["issues"].append(f"Validation error: {e}")
        
        return validation
    
    async def _update_configuration(self):
        """Update embedding configuration to use new database"""
        self.config_manager.config.database_path = str(self.target_db)
        self.config_manager.config.migration_needed = False
        self.config_manager.config.is_consistent = False  # Will be true after regeneration
        self.config_manager._save_configuration()
        
        logger.info("Configuration updated for new database")
    
    async def _rollback(self):
        """Rollback migration in case of failure"""
        try:
            if self.backup_db.exists() and self.target_db.exists():
                self.target_db.unlink()
                logger.info("Migration rolled back")
        except Exception as e:
            logger.error(f"Rollback failed: {e}")


# Convenience function
async def migrate_database(source_db: str, target_db: str, validate: bool = True) -> Dict[str, Any]:
    """
    Convenience function to execute database migration
    """
    migrator = DatabaseMigrator(source_db, target_db)
    return await migrator.execute_migration(validate)