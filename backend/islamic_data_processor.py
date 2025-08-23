"""
Al-Qurtubi Islamic Data Processor
Fetches and processes Al-Qurtubi tafsir from HuggingFace dataset
Extracts legal verses and creates structured Islamic database
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import re
from datetime import datetime

try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    print("⚠️  HuggingFace datasets not installed. Run: pip install datasets")

from app.storage.islamic_vector_store import IslamicVectorStore, IslamicChunk, calculate_legal_confidence, extract_legal_keywords

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlQurtubiProcessor:
    """
    Process Al-Qurtubi tafsir dataset for legal content extraction
    """
    
    def __init__(self):
        self.dataset_name = "MohamedRashad/Quran-Tafseer"
        self.target_tafsir = "* تفسير الجامع لاحكام القرآن/ القرطبي (ت 671 هـ)"
        
        # Legal indicators for filtering
        self.legal_keywords = [
            # Direct legal terms
            "حكم", "فقه", "شريعة", "أحكام", "قضاء", "قانون",
            "حلال", "حرام", "واجب", "مندوب", "مكروه", "مباح",
            
            # Legal contexts  
            "أجمع العلماء", "قال الفقهاء", "في المذاهب", "اختلف العلماء",
            "الحكم الشرعي", "نص القرآن", "دليل", "برهان", "حجة",
            
            # Practical applications
            "في القضاء", "في المحاكم", "في التطبيق", "عملياً", "تطبيق",
            "معاملات", "عبادات", "جنايات", "حدود", "قصاص",
            
            # Contract and family law
            "عقد", "بيع", "شراء", "زواج", "طلاق", "نكاح", "ميراث", "وصية",
            "ربا", "فوائد", "شهادة", "إثبات", "بينة"
        ]
        
        # Minimum confidence threshold for legal relevance
        self.min_legal_confidence = 0.3
        
        self.processed_data = []
        self.stats = {
            "total_verses": 0,
            "legal_verses": 0,
            "high_confidence_verses": 0,
            "processing_errors": 0
        }
    
    async def load_qurtubi_dataset(self) -> List[Dict]:
        """
        Load Al-Qurtubi tafsir from HuggingFace dataset
        """
        if not DATASETS_AVAILABLE:
            raise ImportError("HuggingFace datasets library not available")
        
        logger.info("Loading Al-Qurtubi dataset from HuggingFace...")
        
        try:
            # Load the full dataset
            dataset = load_dataset(self.dataset_name)
            
            # Filter for Al-Qurtubi only
            qurtubi_data = []
            for row in dataset['train']:
                if row['tafsir_book'] == self.target_tafsir:
                    qurtubi_data.append(row)
            
            logger.info(f"Loaded {len(qurtubi_data)} Al-Qurtubi entries")
            self.stats["total_verses"] = len(qurtubi_data)
            
            return qurtubi_data
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise
    
    def is_legal_content(self, content: str) -> tuple[bool, float]:
        """
        Determine if content contains legal information
        Returns (is_legal, confidence_score)
        """
        if not content:
            return False, 0.0
        
        content_lower = content.lower()
        
        # Count legal keywords
        legal_keyword_count = sum(1 for keyword in self.legal_keywords if keyword in content_lower)
        
        # Calculate base confidence
        confidence = calculate_legal_confidence(content)
        
        # Additional scoring for legal phrases
        legal_phrases = [
            "أجمع العلماء", "قال الفقهاء", "الحكم الشرعي",
            "في هذه المسألة", "والصحيح أن", "وقد اختلف العلماء"
        ]
        
        for phrase in legal_phrases:
            if phrase in content_lower:
                confidence += 0.1
        
        # Check for practical legal applications
        practical_indicators = [
            "في المحاكم", "في القضاء", "تطبيق", "عملياً", "واقعياً"
        ]
        
        for indicator in practical_indicators:
            if indicator in content_lower:
                confidence += 0.05
        
        # Normalize confidence to 0-1 range
        confidence = min(confidence, 1.0)
        
        # Determine if content is legal
        is_legal = confidence >= self.min_legal_confidence
        
        return is_legal, confidence
    
    def extract_legal_principle(self, commentary: str) -> str:
        """
        Extract the main legal principle from Al-Qurtubi commentary
        """
        if not commentary:
            return ""
        
        # Patterns for legal principles
        principle_patterns = [
            r"الحكم في هذه الآية[:\s]+(.*?)(?:\.|$)",
            r"والمعنى[:\s]+(.*?)(?:\.|$)", 
            r"وحكم هذا[:\s]+(.*?)(?:\.|$)",
            r"فإن قيل[:\s]+(.*?)(?:\.|$)",
            r"وقد أجمع العلماء على[:\s]+(.*?)(?:\.|$)"
        ]
        
        for pattern in principle_patterns:
            match = re.search(pattern, commentary, re.IGNORECASE)
            if match:
                principle = match.group(1).strip()
                if len(principle) > 10:  # Valid principle
                    return principle[:200]  # Limit length
        
        # If no specific pattern, extract first meaningful sentence
        sentences = commentary.split('.')
        for sentence in sentences[:3]:  # Check first 3 sentences
            if any(keyword in sentence.lower() for keyword in self.legal_keywords[:10]):
                return sentence.strip()[:200]
        
        return ""
    
    def extract_modern_applications(self, commentary: str, legal_principle: str) -> List[str]:
        """
        Extract or infer modern applications from legal principle
        """
        applications = []
        
        # Direct applications mentioned in commentary
        if "في زماننا" in commentary or "اليوم" in commentary or "حالياً" in commentary:
            # Extract modern context if mentioned
            pass
        
        # Infer applications based on legal principle
        if any(term in legal_principle.lower() for term in ["عقد", "بيع", "شراء"]):
            applications.extend(["العقود التجارية", "البيع والشراء", "المعاملات المصرفية"])
        
        if any(term in legal_principle.lower() for term in ["شهادة", "إثبات", "بينة"]):
            applications.extend(["الإثبات في المحاكم", "الشهادة القضائية", "البينات"])
        
        if any(term in legal_principle.lower() for term in ["زواج", "نكاح", "طلاق"]):
            applications.extend(["قوانين الأحوال الشخصية", "عقود الزواج", "إجراءات الطلاق"])
        
        if any(term in legal_principle.lower() for term in ["ميراث", "وراثة", "وصية"]):
            applications.extend(["قوانين الميراث", "توزيع التركات", "الوصايا"])
        
        if any(term in legal_principle.lower() for term in ["ربا", "فوائد"]):
            applications.extend(["البنوك الإسلامية", "التمويل الإسلامي", "العقود المصرفية"])
        
        return list(set(applications))  # Remove duplicates
    
    def create_verse_reference(self, surah_name: str, ayah_number: int) -> str:
        """Create standardized verse reference"""
        return f"{surah_name}:{ayah_number}"
    
    async def process_qurtubi_entry(self, entry: Dict) -> Optional[IslamicChunk]:
        """
        Process a single Al-Qurtubi entry into IslamicChunk
        """
        try:
            # Extract basic information
            surah_name = entry.get('surah_name', '')
            ayah_number = entry.get('ayah', 0)
            tafsir_content = entry.get('tafsir_content', '')
            
            # Check if this content is legal
            is_legal, confidence = self.is_legal_content(tafsir_content)
            
            if not is_legal:
                return None
            
            # Extract legal information
            legal_principle = self.extract_legal_principle(tafsir_content)
            modern_applications = self.extract_modern_applications(tafsir_content, legal_principle)
            
            # Create verse reference
            verse_reference = self.create_verse_reference(surah_name, ayah_number)
            
            # Create unique ID
            chunk_id = f"qurtubi_{surah_name}_{ayah_number}"
            
            # Create title
            title = f"تفسير القرطبي - {verse_reference}"
            if legal_principle:
                title += f" - {legal_principle[:50]}"
            
            # Create content summary (for embedding)
            content_summary = f"""
            الآية: {verse_reference}
            المبدأ القانوني: {legal_principle}
            تفسير القرطبي: {tafsir_content[:300]}
            التطبيقات المعاصرة: {', '.join(modern_applications)}
            """.strip()
            
            # Create Islamic chunk
            islamic_chunk = IslamicChunk(
                id=chunk_id,
                content=content_summary,
                title=title,
                surah_name=surah_name,
                ayah_number=ayah_number,
                verse_reference=verse_reference,
                qurtubi_commentary=tafsir_content,
                legal_principle=legal_principle,
                source_type="qurtubi",
                legal_confidence=confidence,
                metadata={
                    'fiqh_applications': modern_applications,
                    'legal_keywords': extract_legal_keywords(tafsir_content),
                    'processed_at': datetime.now().isoformat(),
                    'original_entry': entry
                }
            )
            
            self.stats["legal_verses"] += 1
            if confidence > 0.7:
                self.stats["high_confidence_verses"] += 1
            
            return islamic_chunk
            
        except Exception as e:
            logger.error(f"Error processing entry for {entry.get('surah_name', 'unknown')}:{entry.get('ayah', 'unknown')}: {e}")
            self.stats["processing_errors"] += 1
            return None
    
    async def process_all_data(self) -> List[IslamicChunk]:
        """
        Process all Al-Qurtubi data and create Islamic chunks
        """
        logger.info("Starting Al-Qurtubi data processing...")
        
        # Load dataset
        qurtubi_data = await self.load_qurtubi_dataset()
        
        # Process each entry
        processed_chunks = []
        
        for i, entry in enumerate(qurtubi_data):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(qurtubi_data)} entries...")
            
            chunk = await self.process_qurtubi_entry(entry)
            if chunk:
                processed_chunks.append(chunk)
        
        logger.info(f"Processing complete. Stats: {self.stats}")
        self.processed_data = processed_chunks
        
        return processed_chunks
    
    async def save_to_database(self, chunks: List[IslamicChunk]) -> bool:
        """
        Save processed chunks to Islamic vector store
        """
        logger.info(f"Saving {len(chunks)} Islamic chunks to database...")
        
        try:
            # Initialize Islamic vector store
            islamic_store = IslamicVectorStore()
            await islamic_store.initialize()
            
            # Store chunks
            success = await islamic_store.store_islamic_chunks(chunks)
            
            if success:
                logger.info(f"✅ Successfully saved {len(chunks)} Islamic chunks")
                return True
            else:
                logger.error("❌ Failed to save Islamic chunks")
                return False
                
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return False
    
    def export_statistics(self) -> Dict:
        """Export processing statistics"""
        return {
            "processing_stats": self.stats,
            "legal_coverage_percentage": (self.stats["legal_verses"] / max(self.stats["total_verses"], 1)) * 100,
            "high_confidence_percentage": (self.stats["high_confidence_verses"] / max(self.stats["legal_verses"], 1)) * 100,
            "error_rate": (self.stats["processing_errors"] / max(self.stats["total_verses"], 1)) * 100
        }


async def build_islamic_database():
    """
    Main function to build Islamic database from Al-Qurtubi dataset
    """
    logger.info("🕌 Starting Islamic Database Build Process...")
    
    try:
        # Initialize processor
        processor = AlQurtubiProcessor()
        
        # Process all data
        chunks = await processor.process_all_data()
        
        if not chunks:
            logger.warning("⚠️  No legal content found in Al-Qurtubi dataset")
            return False
        
        # Save to database
        success = await processor.save_to_database(chunks)
        
        # Export statistics
        stats = processor.export_statistics()
        logger.info(f"📊 Processing Statistics: {json.dumps(stats, indent=2)}")
        
        # Save stats to file
        with open("data/islamic_processing_stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        if success:
            logger.info("✅ Islamic database build completed successfully!")
            return True
        else:
            logger.error("❌ Islamic database build failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Islamic database build failed with error: {e}")
        return False


if __name__ == "__main__":
    # Run the build process
    asyncio.run(build_islamic_database())