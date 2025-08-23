"""
Complete Quranic Embedding System
Enterprise-grade processor for embedding entire Quran with Al-Qurtubi tafseer
"""

import asyncio
import aiosqlite
import json
import logging
import pickle
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np
import re

# OpenAI for embeddings
from openai import AsyncOpenAI

# HuggingFace for dataset
try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    print("⚠️  Install datasets: pip install datasets")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/quranic_embedding.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for Quranic embedding processing"""
    
    # Embedding settings
    embedding_model: str = "text-embedding-3-large"
    cost_per_1k_tokens: float = 0.00013
    
    # Processing settings
    batch_size: int = 50  # verses per batch
    max_chunk_size: int = 25000  # characters per chunk (roughly 6000 tokens for Arabic)
    chunk_overlap: int = 1000   # overlap between chunks (increased for better context)
    
    # Quality settings
    min_tafseer_length: int = 50  # minimum tafseer length
    relevance_threshold: float = 0.7
    
    # Cost controls
    max_total_cost: float = 200.0
    cost_alert_threshold: float = 0.8
    
    # Database settings
    db_path: str = "data/quranic_foundations.db"
    checkpoint_dir: str = "data/checkpoints"
    
    # Dataset settings
    dataset_name: str = "MohamedRashad/Quran-Tafseer"
    tafseer_filter: str = "* تفسير الجامع لاحكام القرآن/ القرطبي (ت 671 هـ)"


@dataclass
class QuranicVerse:
    """Represents a Quranic verse with Al-Qurtubi tafseer"""
    
    id: str
    surah_number: int
    surah_name: str
    ayah_number: int
    verse_reference: str
    arabic_text: str
    tafseer_content: str
    
    # Processed data
    chunks: List[Dict] = None
    embeddings: List[np.ndarray] = None
    legal_concepts: List[str] = None
    
    # Metadata
    processing_time: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0


@dataclass
class ProcessingSession:
    """Tracks processing session state"""
    
    session_id: str
    start_time: datetime
    total_verses: int
    processed_verses: int = 0
    failed_verses: int = 0
    total_cost: float = 0.0
    total_tokens: int = 0
    
    # Progress tracking
    current_batch: int = 0
    last_checkpoint: datetime = None
    estimated_completion: datetime = None
    
    # Results
    successful_embeddings: int = 0
    total_chunks_created: int = 0
    
    def get_progress_percentage(self) -> float:
        return (self.processed_verses / self.total_verses) * 100 if self.total_verses > 0 else 0.0
    
    def get_verses_per_minute(self) -> float:
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        return self.processed_verses / elapsed if elapsed > 0 else 0.0


class SemanticChunker:
    """Smart chunking that preserves Islamic scholarly boundaries"""
    
    # Islamic scholarly boundary markers
    BOUNDARY_MARKERS = [
        "وقوله تعالى",      # "And His saying (new verse discussion)"
        "قال القرطبي",      # "Al-Qurtubi said"
        "واختلف العلماء",    # "Scholars disagreed"
        "والحكم في هذا",    # "The ruling in this"
        "وفي هذه الآية",    # "In this verse"
        "مسألة:",           # "Issue:"
        "فأما",             # "As for"
        "وأما",             # "And as for"
        "واعلم أن",         # "Know that"
        "والدليل على ذلك",  # "The evidence for this"
        "وقال بعض العلماء",  # "Some scholars said"
        "وذهب المفسرون",    # "The interpreters went"
        "والصحيح في هذا",   # "The correct view in this"
    ]
    
    def __init__(self, max_chunk_size: int = 1500, overlap_size: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
    
    def chunk_tafseer(self, tafseer: str, verse_ref: str) -> List[Dict]:
        """
        Intelligent chunking preserving scholarly structure
        """
        
        if not tafseer or len(tafseer) < 100:
            return []
        
        # Clean and normalize text
        cleaned_tafseer = self._clean_arabic_text(tafseer)
        
        # If short enough, return as single chunk
        if len(cleaned_tafseer) <= self.max_chunk_size:
            return [{
                "chunk_id": f"{verse_ref}_full",
                "content": cleaned_tafseer,
                "chunk_type": "complete",
                "start_pos": 0,
                "end_pos": len(cleaned_tafseer),
                "boundary_type": "complete_tafseer"
            }]
        
        # Smart chunking for longer texts
        return self._intelligent_chunk(cleaned_tafseer, verse_ref)
    
    def _intelligent_chunk(self, text: str, verse_ref: str) -> List[Dict]:
        """
        Chunk at semantic boundaries
        """
        
        chunks = []
        current_chunk = ""
        current_pos = 0
        chunk_count = 0
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            # Check if adding this sentence would exceed size limit
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            # Check for semantic boundary
            is_boundary = self._is_semantic_boundary(sentence)
            
            if len(potential_chunk) > self.max_chunk_size and current_chunk and is_boundary:
                # Create chunk at semantic boundary
                chunk_count += 1
                chunks.append({
                    "chunk_id": f"{verse_ref}_chunk_{chunk_count}",
                    "content": current_chunk.strip(),
                    "chunk_type": "semantic_section",
                    "start_pos": current_pos,
                    "end_pos": current_pos + len(current_chunk),
                    "boundary_type": self._get_boundary_type(sentence)
                })
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + sentence
                current_pos += len(current_chunk) - len(overlap_text)
                
            else:
                current_chunk = potential_chunk
        
        # Add final chunk
        if current_chunk:
            chunk_count += 1
            chunks.append({
                "chunk_id": f"{verse_ref}_chunk_{chunk_count}",
                "content": current_chunk.strip(),
                "chunk_type": "final_section",
                "start_pos": current_pos,
                "end_pos": current_pos + len(current_chunk),
                "boundary_type": "end_of_tafseer"
            })
        
        return chunks
    
    def _clean_arabic_text(self, text: str) -> str:
        """Clean and normalize Arabic text"""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Arabic diacritics
        text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s\.\:\;\،\؟\!]', '', text)
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split Arabic text into sentences"""
        
        # Arabic sentence endings
        sentence_endings = ['\.', '؟', '!', '؛']
        pattern = '([' + ''.join(sentence_endings) + '])'
        
        sentences = re.split(pattern, text)
        
        # Rejoin sentence endings with sentences
        result = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]
            if sentence.strip():
                result.append(sentence.strip())
        
        return result
    
    def _is_semantic_boundary(self, sentence: str) -> bool:
        """Check if sentence starts a new semantic section"""
        
        return any(marker in sentence for marker in self.BOUNDARY_MARKERS)
    
    def _get_boundary_type(self, sentence: str) -> str:
        """Identify the type of semantic boundary"""
        
        for marker in self.BOUNDARY_MARKERS:
            if marker in sentence:
                return marker
        return "general_boundary"
    
    def _get_overlap_text(self, chunk: str) -> str:
        """Get overlap text from end of chunk"""
        
        if len(chunk) <= self.overlap_size:
            return chunk
        
        # Try to find a good breaking point for overlap
        overlap_start = len(chunk) - self.overlap_size
        
        # Find sentence boundary for clean overlap
        sentences = self._split_into_sentences(chunk)
        if len(sentences) > 1:
            # Use last sentence as overlap
            return sentences[-1]
        
        # Fallback to character-based overlap
        return chunk[overlap_start:]


class CostMonitor:
    """Real-time cost monitoring and controls"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.total_cost = 0.0
        self.total_tokens = 0
        self.cost_history = []
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: 1 token ≈ 3-4 characters for Arabic
        return len(text) // 3
    
    def calculate_cost(self, tokens: int) -> float:
        """Calculate cost for given tokens"""
        return (tokens / 1000) * self.config.cost_per_1k_tokens
    
    def track_usage(self, tokens: int):
        """Track token usage and cost"""
        cost = self.calculate_cost(tokens)
        self.total_cost += cost
        self.total_tokens += tokens
        
        self.cost_history.append({
            'timestamp': datetime.now(),
            'tokens': tokens,
            'cost': cost,
            'cumulative_cost': self.total_cost
        })
    
    def check_budget_limits(self) -> Dict[str, Any]:
        """Check if we're approaching budget limits"""
        
        alerts = []
        
        # Check total budget
        budget_percentage = (self.total_cost / self.config.max_total_cost) * 100
        
        if budget_percentage >= 90:
            alerts.append({
                'level': 'CRITICAL',
                'message': f'Budget 90% exhausted: ${self.total_cost:.2f}/${self.config.max_total_cost:.2f}'
            })
        elif budget_percentage >= self.config.cost_alert_threshold * 100:
            alerts.append({
                'level': 'WARNING',
                'message': f'Budget {budget_percentage:.1f}% used: ${self.total_cost:.2f}/${self.config.max_total_cost:.2f}'
            })
        
        return {
            'total_cost': self.total_cost,
            'budget_percentage': budget_percentage,
            'alerts': alerts,
            'should_continue': budget_percentage < 95
        }


class CheckpointManager:
    """Manages processing checkpoints for recovery"""
    
    def __init__(self, checkpoint_dir: str):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    async def save_checkpoint(self, session: ProcessingSession, processed_verses: List[QuranicVerse]):
        """Save processing checkpoint"""
        
        checkpoint_data = {
            'session': asdict(session),
            'processed_verses': [asdict(verse) for verse in processed_verses],
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{session.session_id}.json"
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"💾 Checkpoint saved: {session.processed_verses}/{session.total_verses} verses")
    
    async def load_latest_checkpoint(self, session_id: str) -> Optional[Tuple[ProcessingSession, List[QuranicVerse]]]:
        """Load latest checkpoint for session"""
        
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{session_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            # Reconstruct session
            session_data = checkpoint_data['session']
            session = ProcessingSession(**session_data)
            
            # Reconstruct processed verses
            verses = [QuranicVerse(**verse_data) for verse_data in checkpoint_data['processed_verses']]
            
            logger.info(f"📂 Checkpoint loaded: {session.processed_verses}/{session.total_verses} verses")
            return session, verses
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None


class QuranicEmbeddingProcessor:
    """Main processor for Quranic embedding system"""
    
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()
        self.client = AsyncOpenAI()
        self.chunker = SemanticChunker(self.config.max_chunk_size, self.config.chunk_overlap)
        self.cost_monitor = CostMonitor(self.config)
        self.checkpoint_manager = CheckpointManager(self.config.checkpoint_dir)
        
        # Ensure directories exist
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path(self.config.checkpoint_dir).mkdir(exist_ok=True)
    
    async def initialize_database(self):
        """Initialize SQLite database for storing embeddings"""
        
        async with aiosqlite.connect(self.config.db_path) as db:
            # Create verses table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS quranic_verses (
                    id TEXT PRIMARY KEY,
                    surah_number INTEGER,
                    surah_name TEXT,
                    ayah_number INTEGER,
                    verse_reference TEXT,
                    arabic_text TEXT,
                    tafseer_content TEXT,
                    processing_time REAL,
                    tokens_used INTEGER,
                    cost REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create chunks table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tafseer_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    verse_id TEXT,
                    content TEXT,
                    chunk_type TEXT,
                    start_pos INTEGER,
                    end_pos INTEGER,
                    boundary_type TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (verse_id) REFERENCES quranic_verses (id)
                )
            """)
            
            # Create indices for fast searching
            await db.execute("CREATE INDEX IF NOT EXISTS idx_verse_reference ON quranic_verses(verse_reference)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_surah_ayah ON quranic_verses(surah_number, ayah_number)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_chunk_verse ON tafseer_chunks(verse_id)")
            
            await db.commit()
            logger.info("✅ Database initialized successfully")
    
    async def load_quran_dataset(self) -> List[Dict]:
        """Load Quran dataset from HuggingFace"""
        
        if not DATASETS_AVAILABLE:
            raise ImportError("HuggingFace datasets not available. Install with: pip install datasets")
        
        logger.info(f"📥 Loading dataset: {self.config.dataset_name}")
        
        try:
            # Load dataset
            dataset = load_dataset(self.config.dataset_name)
            
            # Filter for Al-Qurtubi tafseer
            qurtubi_verses = []
            for row in dataset['train']:
                if row.get('tafsir_book') == self.config.tafseer_filter:
                    qurtubi_verses.append(row)
            
            logger.info(f"📚 Loaded {len(qurtubi_verses)} verses with Al-Qurtubi tafseer")
            return qurtubi_verses
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise
    
    def process_raw_verse(self, raw_verse: Dict) -> QuranicVerse:
        """Convert raw dataset verse to QuranicVerse object"""
        
        # Extract data
        surah_name = raw_verse.get('surah_name', '')
        ayah_number = raw_verse.get('ayah', 0)
        verse_text = raw_verse.get('verse_text', '')
        tafseer = raw_verse.get('tafsir_content', '')
        
        # Create verse reference
        verse_reference = f"{surah_name}:{ayah_number}"
        
        # Create unique ID
        verse_id = hashlib.md5(verse_reference.encode('utf-8')).hexdigest()
        
        # Extract surah number (you might need to map names to numbers)
        surah_number = self._get_surah_number(surah_name)
        
        return QuranicVerse(
            id=verse_id,
            surah_number=surah_number,
            surah_name=surah_name,
            ayah_number=ayah_number,
            verse_reference=verse_reference,
            arabic_text=verse_text,
            tafseer_content=tafseer
        )
    
    def _get_surah_number(self, surah_name: str) -> int:
        """Map surah name to number"""
        
        # Basic mapping - you might want to expand this
        surah_mapping = {
            'الفاتحة': 1, 'البقرة': 2, 'آل عمران': 3, 'النساء': 4, 'المائدة': 5,
            'الأنعام': 6, 'الأعراف': 7, 'الأنفال': 8, 'التوبة': 9, 'يونس': 10,
            # Add more as needed...
        }
        
        return surah_mapping.get(surah_name, 0)
    
    async def generate_embeddings(self, chunks: List[Dict]) -> List[np.ndarray]:
        """Generate embeddings for text chunks"""
        
        embeddings = []
        total_tokens_used = 0
        
        try:
            # Process each chunk individually to avoid token limits
            for chunk in chunks:
                text = chunk['content']
                
                # More accurate token estimation for Arabic (4-5 chars per token)
                estimated_tokens = len(text) // 4  # Conservative estimate for Arabic
                
                if estimated_tokens > 7500:  # Safe margin below 8192 limit
                    logger.warning(f"⚠️ Chunk too large ({estimated_tokens} tokens), truncating...")
                    text = text[:30000]  # Roughly 7500 tokens with safe margin
                    # Re-estimate after truncation
                    estimated_tokens = len(text) // 4
                
                # Attempt embedding with automatic retry for token limit errors
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await self.client.embeddings.create(
                            model=self.config.embedding_model,
                            input=[text]
                        )
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        if "maximum context length" in str(e) and attempt < max_retries - 1:
                            # Token limit exceeded, reduce text size
                            logger.warning(f"🔄 Attempt {attempt + 1}: Token limit exceeded, reducing text size...")
                            text = text[:len(text) // 2]  # Halve the text size
                            continue
                        else:
                            # Non-recoverable error or max retries reached
                            logger.error(f"❌ Failed to generate embeddings: {e}")
                            raise e
                
                # Extract embedding
                embeddings.append(np.array(response.data[0].embedding))
                
                # Track usage
                tokens_used = response.usage.total_tokens
                total_tokens_used += tokens_used
                
                logger.debug(f"✅ Generated embedding for chunk {chunk['chunk_id']}: {tokens_used} tokens")
            
            # Track total usage
            self.cost_monitor.track_usage(total_tokens_used)
            
            logger.debug(f"✅ Generated {len(embeddings)} embeddings, {total_tokens_used} total tokens used")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def process_single_verse(self, raw_verse: Dict) -> QuranicVerse:
        """Process a single verse completely"""
        
        start_time = time.time()
        
        # Convert to QuranicVerse object
        verse = self.process_raw_verse(raw_verse)
        
        # Check if tafseer is substantial enough
        if len(verse.tafseer_content) < self.config.min_tafseer_length:
            logger.warning(f"⚠️ Skipping {verse.verse_reference}: tafseer too short")
            return None
        
        try:
            # Chunk the tafseer
            chunks = self.chunker.chunk_tafseer(verse.tafseer_content, verse.verse_reference)
            
            if not chunks:
                logger.warning(f"⚠️ No chunks created for {verse.verse_reference}")
                return None
            
            # Generate embeddings
            embeddings = await self.generate_embeddings(chunks)
            
            # Store in verse object
            verse.chunks = chunks
            verse.embeddings = embeddings
            verse.processing_time = time.time() - start_time
            verse.tokens_used = sum(self.cost_monitor.estimate_tokens(chunk['content']) for chunk in chunks)
            verse.cost = self.cost_monitor.calculate_cost(verse.tokens_used)
            
            logger.debug(f"✅ Processed {verse.verse_reference}: {len(chunks)} chunks, {len(embeddings)} embeddings")
            
            return verse
            
        except Exception as e:
            logger.error(f"Failed to process verse {verse.verse_reference}: {e}")
            return None
    
    async def store_verse_in_database(self, verse: QuranicVerse):
        """Store processed verse and chunks in database"""
        
        async with aiosqlite.connect(self.config.db_path) as db:
            # Store verse
            await db.execute("""
                INSERT OR REPLACE INTO quranic_verses 
                (id, surah_number, surah_name, ayah_number, verse_reference, 
                 arabic_text, tafseer_content, processing_time, tokens_used, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                verse.id, verse.surah_number, verse.surah_name, verse.ayah_number,
                verse.verse_reference, verse.arabic_text, verse.tafseer_content,
                verse.processing_time, verse.tokens_used, verse.cost
            ))
            
            # Store chunks with embeddings
            for chunk, embedding in zip(verse.chunks, verse.embeddings):
                embedding_blob = pickle.dumps(embedding)
                
                await db.execute("""
                    INSERT OR REPLACE INTO tafseer_chunks
                    (chunk_id, verse_id, content, chunk_type, start_pos, end_pos, 
                     boundary_type, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk['chunk_id'], verse.id, chunk['content'], chunk['chunk_type'],
                    chunk['start_pos'], chunk['end_pos'], chunk['boundary_type'],
                    embedding_blob
                ))
            
            await db.commit()
    
    async def process_all_verses(self, resume_session_id: str = None) -> ProcessingSession:
        """Process all verses with checkpointing and error recovery"""
        
        # Initialize database
        await self.initialize_database()
        
        # Load dataset
        raw_verses = await self.load_quran_dataset()
        
        # Create or resume session
        if resume_session_id:
            checkpoint_data = await self.checkpoint_manager.load_latest_checkpoint(resume_session_id)
            if checkpoint_data:
                session, processed_verses = checkpoint_data
                logger.info(f"🔄 Resuming session: {session.processed_verses}/{session.total_verses} completed")
            else:
                logger.warning(f"No checkpoint found for session {resume_session_id}, starting fresh")
                session = ProcessingSession(
                    session_id=resume_session_id,
                    start_time=datetime.now(),
                    total_verses=len(raw_verses)
                )
                processed_verses = []
        else:
            session_id = f"quran_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session = ProcessingSession(
                session_id=session_id,
                start_time=datetime.now(),
                total_verses=len(raw_verses)
            )
            processed_verses = []
        
        logger.info(f"🚀 Starting processing: {session.total_verses} verses to process")
        logger.info(f"💰 Using {self.config.embedding_model} at ${self.config.cost_per_1k_tokens}/1K tokens")
        
        # Process verses in batches
        verses_to_process = raw_verses[session.processed_verses:]
        
        for i in range(0, len(verses_to_process), self.config.batch_size):
            batch = verses_to_process[i:i + self.config.batch_size]
            batch_start_time = time.time()
            
            logger.info(f"📦 Processing batch {session.current_batch + 1}: verses {session.processed_verses + 1}-{session.processed_verses + len(batch)}")
            
            # Process batch
            batch_results = []
            for raw_verse in batch:
                try:
                    # Check budget before each verse
                    budget_check = self.cost_monitor.check_budget_limits()
                    if not budget_check['should_continue']:
                        logger.critical(f"🚨 Budget limit reached: ${self.cost_monitor.total_cost:.2f}")
                        break
                    
                    # Process verse
                    processed_verse = await self.process_single_verse(raw_verse)
                    
                    if processed_verse:
                        # Store in database
                        await self.store_verse_in_database(processed_verse)
                        batch_results.append(processed_verse)
                        
                        session.processed_verses += 1
                        session.successful_embeddings += len(processed_verse.embeddings)
                        session.total_chunks_created += len(processed_verse.chunks)
                        session.total_cost += processed_verse.cost
                        session.total_tokens += processed_verse.tokens_used
                        
                        logger.debug(f"✅ {processed_verse.verse_reference} completed")
                    else:
                        session.failed_verses += 1
                        logger.warning(f"❌ Failed to process verse")
                
                except Exception as e:
                    logger.error(f"Error processing verse: {e}")
                    session.failed_verses += 1
                    continue
            
            # Update session progress
            session.current_batch += 1
            session.last_checkpoint = datetime.now()
            
            # Calculate ETA
            if session.processed_verses > 0:
                elapsed_time = (datetime.now() - session.start_time).total_seconds()
                verses_per_second = session.processed_verses / elapsed_time
                remaining_verses = session.total_verses - session.processed_verses
                eta_seconds = remaining_verses / verses_per_second if verses_per_second > 0 else 0
                session.estimated_completion = datetime.now() + timedelta(seconds=eta_seconds)
            
            # Save checkpoint
            processed_verses.extend(batch_results)
            await self.checkpoint_manager.save_checkpoint(session, processed_verses)
            
            # Progress update
            progress = session.get_progress_percentage()
            verses_per_min = session.get_verses_per_minute()
            eta = session.estimated_completion.strftime('%H:%M:%S') if session.estimated_completion else "Unknown"
            
            logger.info(f"📊 Progress: {progress:.1f}% | {verses_per_min:.1f} verses/min | Cost: ${session.total_cost:.3f} | ETA: {eta}")
            
            # Short delay between batches to avoid rate limits
            await asyncio.sleep(1)
        
        # Final update
        session.last_checkpoint = datetime.now()
        logger.info(f"🎉 Processing completed!")
        logger.info(f"📊 Final Stats:")
        logger.info(f"   ✅ Processed: {session.processed_verses}/{session.total_verses} verses")
        logger.info(f"   ❌ Failed: {session.failed_verses} verses")
        logger.info(f"   🔢 Embeddings: {session.successful_embeddings}")
        logger.info(f"   📦 Chunks: {session.total_chunks_created}")
        logger.info(f"   💰 Total cost: ${session.total_cost:.3f}")
        logger.info(f"   🕒 Duration: {datetime.now() - session.start_time}")
        
        return session


# CLI entry point
async def main():
    """Main entry point for Quranic embedding processing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Process Quranic verses with Al-Qurtubi tafseer")
    parser.add_argument("--resume", help="Resume from checkpoint session ID")
    parser.add_argument("--budget", type=float, default=200.0, help="Maximum budget in USD")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ProcessingConfig(
        max_total_cost=args.budget,
        batch_size=args.batch_size
    )
    
    # Create processor
    processor = QuranicEmbeddingProcessor(config)
    
    try:
        # Start processing
        session = await processor.process_all_verses(resume_session_id=args.resume)
        
        print(f"\n🎉 Processing completed successfully!")
        print(f"Session ID: {session.session_id}")
        print(f"Processed: {session.processed_verses}/{session.total_verses} verses")
        print(f"Total cost: ${session.total_cost:.3f}")
        
    except KeyboardInterrupt:
        print("\n⏸️  Processing interrupted by user")
        print("You can resume later using the session ID from the logs")
        
    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        print("Check logs for details. You can resume from the last checkpoint.")


if __name__ == "__main__":
    asyncio.run(main())