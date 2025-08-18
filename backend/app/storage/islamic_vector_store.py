"""
Islamic Vector Store Implementation
Separate database for Islamic sources with same interface as existing vector store
Zero conflicts with existing civil law database
"""
import pickle
import json
import sqlite3
import aiosqlite
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import logging

from .vector_store import VectorStore, Chunk, SearchResult, StorageStats

logger = logging.getLogger(__name__)


class IslamicChunk(Chunk):
    """Enhanced chunk for Islamic sources with additional metadata"""
    
    def __init__(self, id: str, content: str, title: str, embedding: Optional[np.ndarray] = None, 
                 metadata: Optional[Dict[str, Any]] = None, **islamic_fields):
        super().__init__(id, content, title, embedding, metadata)
        
        # Islamic-specific fields
        self.surah_name = islamic_fields.get('surah_name')
        self.ayah_number = islamic_fields.get('ayah_number')
        self.verse_reference = islamic_fields.get('verse_reference')
        self.qurtubi_commentary = islamic_fields.get('qurtubi_commentary')
        self.legal_principle = islamic_fields.get('legal_principle')
        self.source_type = islamic_fields.get('source_type', 'qurtubi')
        self.legal_confidence = islamic_fields.get('legal_confidence', 0.0)


class IslamicVectorStore(VectorStore):
    """
    Islamic Vector Store - Inherits from existing store but uses separate database
    ZERO conflicts with existing civil law system
    """
    
    def __init__(self, db_path: str = "data/islamic_vectors.db"):
        """
        Initialize Islamic SQLite vector store
        
        Args:
            db_path: Path to Islamic SQLite database file (separate from civil law)
        """
        self.db_path = db_path
        self.initialized = False
        self.source_type = "islamic"
        
        # Ensure data directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(exist_ok=True)
        
        logger.info(f"Islamic Vector Store initialized with path: {db_path}")
    
    async def initialize(self) -> None:
        """Initialize Islamic SQLite database with Islamic-specific schema"""
        if self.initialized:
            return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Enable JSON extension if available
                try:
                    await db.execute("SELECT json('{}');")
                except sqlite3.OperationalError:
                    logger.warning("JSON extension not available - using TEXT for metadata")
                
                # Create Islamic-specific chunks table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS islamic_chunks (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        title TEXT NOT NULL,
                        
                        -- Islamic-specific fields
                        surah_name TEXT,
                        ayah_number INTEGER,
                        verse_reference TEXT,
                        arabic_verse TEXT,
                        qurtubi_commentary TEXT,
                        legal_principle TEXT,
                        fiqh_applications TEXT,
                        modern_relevance TEXT,
                        
                        -- Standard fields (same as existing system)
                        embedding BLOB,
                        metadata TEXT,
                        
                        -- Source tracking
                        source_type TEXT DEFAULT 'qurtubi',
                        legal_confidence REAL DEFAULT 0.0,
                        
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_islamic_surah 
                    ON islamic_chunks(surah_name)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_islamic_confidence 
                    ON islamic_chunks(legal_confidence)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_islamic_source 
                    ON islamic_chunks(source_type)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_islamic_created_at 
                    ON islamic_chunks(created_at)
                """)
                
                await db.commit()
                
            self.initialized = True
            logger.info("Islamic vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Islamic SQLite store: {e}")
            raise
    
    async def store_islamic_chunks(self, chunks: List[IslamicChunk]) -> bool:
        """Store Islamic chunks in separate database"""
        if not self.initialized:
            await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for chunk in chunks:
                    # Serialize embedding
                    embedding_blob = pickle.dumps(chunk.embedding) if chunk.embedding is not None else None
                    
                    # Serialize metadata
                    metadata_json = json.dumps(chunk.metadata) if chunk.metadata else "{}"
                    
                    await db.execute("""
                        INSERT OR REPLACE INTO islamic_chunks (
                            id, content, title,
                            surah_name, ayah_number, verse_reference, arabic_verse,
                            qurtubi_commentary, legal_principle, fiqh_applications, modern_relevance,
                            embedding, metadata, source_type, legal_confidence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        chunk.id, chunk.content, chunk.title,
                        chunk.surah_name, chunk.ayah_number, chunk.verse_reference,
                        getattr(chunk, 'arabic_verse', ''),
                        chunk.qurtubi_commentary, chunk.legal_principle,
                        getattr(chunk, 'fiqh_applications', ''),
                        getattr(chunk, 'modern_relevance', ''),
                        embedding_blob, metadata_json,
                        chunk.source_type, chunk.legal_confidence
                    ))
                
                await db.commit()
                logger.info(f"Stored {len(chunks)} Islamic chunks successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store Islamic chunks: {e}")
            return False
    
    async def search(self, query: str, limit: int = 10, threshold: float = 0.0) -> List[SearchResult]:
        """
        Search Islamic vector store using same interface as existing system
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # For now, implement simple text search
            # TODO: Add proper vector similarity search when embeddings are ready
            async with aiosqlite.connect(self.db_path) as db:
                # Simple keyword search in Islamic content
                query_terms = query.lower().split()
                
                async with db.execute("""
                    SELECT id, content, title, surah_name, ayah_number, verse_reference,
                           qurtubi_commentary, legal_principle, source_type, legal_confidence,
                           metadata, embedding
                    FROM islamic_chunks
                    WHERE (
                        LOWER(content) LIKE ? OR 
                        LOWER(title) LIKE ? OR 
                        LOWER(qurtubi_commentary) LIKE ? OR
                        LOWER(legal_principle) LIKE ?
                    )
                    AND legal_confidence >= ?
                    ORDER BY legal_confidence DESC
                    LIMIT ?
                """, (
                    f"%{query.lower()}%", f"%{query.lower()}%", 
                    f"%{query.lower()}%", f"%{query.lower()}%",
                    threshold, limit
                )) as cursor:
                    
                    rows = await cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        # Deserialize embedding if exists
                        embedding = None
                        if row[11]:  # embedding column
                            try:
                                embedding = pickle.loads(row[11])
                            except:
                                embedding = None
                        
                        # Create Islamic chunk
                        chunk = IslamicChunk(
                            id=row[0],
                            content=row[1],
                            title=row[2],
                            embedding=embedding,
                            metadata=json.loads(row[10]) if row[10] else {},
                            surah_name=row[3],
                            ayah_number=row[4],
                            verse_reference=row[5],
                            qurtubi_commentary=row[6],
                            legal_principle=row[7],
                            source_type=row[8],
                            legal_confidence=row[9]
                        )
                        
                        # Create search result
                        result = SearchResult(
                            chunk=chunk,
                            similarity_score=float(row[9])  # Use legal_confidence as score
                        )
                        result.metadata = {'source': 'islamic', 'type': 'qurtubi'}
                        
                        results.append(result)
                    
                    logger.info(f"Found {len(results)} Islamic results for query: {query}")
                    return results
                    
        except Exception as e:
            logger.error(f"Islamic search failed: {e}")
            return []
    
    async def get_stats(self) -> StorageStats:
        """Get Islamic database statistics"""
        if not self.initialized:
            await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get total count
                async with db.execute("SELECT COUNT(*) FROM islamic_chunks") as cursor:
                    total_count = (await cursor.fetchone())[0]
                
                # Get average confidence
                async with db.execute("SELECT AVG(legal_confidence) FROM islamic_chunks") as cursor:
                    avg_confidence = (await cursor.fetchone())[0] or 0.0
                
                # Get latest update
                async with db.execute("SELECT MAX(created_at) FROM islamic_chunks") as cursor:
                    latest_update = (await cursor.fetchone())[0]
                
                return StorageStats(
                    total_chunks=total_count,
                    total_size=0,  # TODO: Calculate actual size
                    last_updated=latest_update,
                    metadata={'avg_legal_confidence': avg_confidence, 'source': 'islamic'}
                )
                
        except Exception as e:
            logger.error(f"Failed to get Islamic stats: {e}")
            return StorageStats(total_chunks=0, total_size=0, last_updated=None)
    
    async def store_chunks(self, chunks: List[Chunk]) -> bool:
        """Convert regular chunks to Islamic chunks and store"""
        islamic_chunks = []
        for chunk in chunks:
            islamic_chunk = IslamicChunk(
                id=chunk.id,
                content=chunk.content,
                title=chunk.title,
                embedding=chunk.embedding,
                metadata=chunk.metadata
            )
            islamic_chunks.append(islamic_chunk)
        
        return await self.store_islamic_chunks(islamic_chunks)
    
    async def delete_chunks(self, chunk_ids: List[str]) -> bool:
        """Delete Islamic chunks by IDs"""
        if not self.initialized:
            await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                placeholders = ','.join(['?' for _ in chunk_ids])
                await db.execute(f"DELETE FROM islamic_chunks WHERE id IN ({placeholders})", chunk_ids)
                await db.commit()
                logger.info(f"Deleted {len(chunk_ids)} Islamic chunks")
                return True
        except Exception as e:
            logger.error(f"Failed to delete Islamic chunks: {e}")
            return False
    
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[IslamicChunk]:
        """Get Islamic chunk by ID"""
        if not self.initialized:
            await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, content, title, surah_name, ayah_number, verse_reference,
                           qurtubi_commentary, legal_principle, source_type, legal_confidence,
                           metadata, embedding
                    FROM islamic_chunks WHERE id = ?
                """, (chunk_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        # Deserialize embedding if exists
                        embedding = None
                        if row[11]:  # embedding column
                            try:
                                embedding = pickle.loads(row[11])
                            except:
                                embedding = None
                        
                        return IslamicChunk(
                            id=row[0],
                            content=row[1],
                            title=row[2],
                            embedding=embedding,
                            metadata=json.loads(row[10]) if row[10] else {},
                            surah_name=row[3],
                            ayah_number=row[4],
                            verse_reference=row[5],
                            qurtubi_commentary=row[6],
                            legal_principle=row[7],
                            source_type=row[8],
                            legal_confidence=row[9]
                        )
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get chunk by ID: {e}")
            return None
    
    async def search_similar(self, embedding: np.ndarray, limit: int = 10, threshold: float = 0.0) -> List[SearchResult]:
        """Search for similar Islamic chunks using embedding"""
        # For now, return empty list - will implement proper vector search later
        logger.warning("Vector similarity search not yet implemented for Islamic store")
        return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for Islamic vector store"""
        try:
            stats = await self.get_stats()
            return {
                "status": "healthy",
                "store_type": "islamic",
                "total_chunks": stats.total_chunks,
                "avg_legal_confidence": stats.metadata.get('avg_legal_confidence', 0),
                "last_updated": stats.last_updated
            }
        except Exception as e:
            return {
                "status": "error",
                "store_type": "islamic", 
                "error": str(e)
            }


# Utility functions for Islamic content processing
def create_islamic_citation(chunk: IslamicChunk) -> str:
    """Create properly formatted Islamic citation"""
    if chunk.verse_reference and chunk.arabic_verse:
        # For Quranic verses
        verse_excerpt = chunk.arabic_verse[:50] + "..." if len(chunk.arabic_verse) > 50 else chunk.arabic_verse
        return f"قال تعالى: «{verse_excerpt}» [{chunk.verse_reference}]"
    elif chunk.legal_principle:
        # For legal principles
        return f"المبدأ الشرعي: {chunk.legal_principle}"
    else:
        return f"المرجع الإسلامي: {chunk.title}"


def extract_legal_keywords(text: str) -> List[str]:
    """Extract legal keywords from Arabic text"""
    legal_keywords = [
        "حكم", "فقه", "شريعة", "أحكام", "قضاء",
        "حلال", "حرام", "واجب", "مندوب", "مكروه", "مباح",
        "أجمع العلماء", "قال الفقهاء", "في المذاهب",
        "الحكم الشرعي", "نص القرآن", "دليل",
        "في القضاء", "في المحاكم", "في التطبيق", "عملياً"
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for keyword in legal_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def calculate_legal_confidence(content: str, commentary: str = "") -> float:
    """Calculate how legal-focused this content is (0.0 to 1.0)"""
    combined_text = f"{content} {commentary}".lower()
    
    # Count legal indicators
    legal_indicators = extract_legal_keywords(combined_text)
    
    # Base confidence from keyword count
    base_confidence = min(len(legal_indicators) * 0.1, 0.8)
    
    # Boost for strong legal phrases
    strong_phrases = ["أجمع العلماء", "الحكم الشرعي", "في القضاء"]
    for phrase in strong_phrases:
        if phrase in combined_text:
            base_confidence += 0.1
    
    # Cap at 1.0
    return min(base_confidence, 1.0)