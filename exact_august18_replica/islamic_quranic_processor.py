"""
Islamic Legal Quranic Foundation Processor
Generates embeddings with proper Islamic legal analysis and database structure
"""

import asyncio
import aiosqlite
import json
import logging
import numpy as np
import re
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from openai import AsyncOpenAI
from datasets import load_dataset
import tiktoken

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/islamic_quranic_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IslamicQuranicProcessor:
    """
    Advanced processor that creates Quranic foundations with Islamic legal analysis
    """
    
    def __init__(self, api_key: str, db_path: str = "data/quranic_foundation.db"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.processed_count = 0
        self.total_cost = 0.0
        
        # Islamic legal categories
        self.legal_categories = [
            "العبادات",  # Worship
            "المعاملات",  # Transactions
            "النكاح",  # Marriage
            "الطلاق",  # Divorce
            "المواريث",  # Inheritance
            "الجنايات",  # Criminal law
            "القضاء",  # Judiciary
            "الحدود",  # Prescribed punishments
            "السياسة الشرعية",  # Islamic governance
            "الأحوال الشخصية",  # Personal status
            "القانون التجاري",  # Commercial law
            "العدالة",  # Justice
            "الحقوق",  # Rights
            "الواجبات"  # Duties
        ]
        
    async def initialize_database(self):
        """Initialize the Islamic legal database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS quranic_foundations (
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
                    verse_embedding BLOB,                    -- Numpy array
                    principle_embedding BLOB,                -- Numpy array
                    application_embedding BLOB,              -- Numpy array
                    source_quality TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    usage_frequency INTEGER DEFAULT 0,
                    effectiveness_rating REAL DEFAULT 0.0,
                    created_date TEXT NOT NULL
                )
            """)
            
            # Create indices
            await db.execute("CREATE INDEX IF NOT EXISTS idx_surah_ayah ON quranic_foundations (surah_name, ayah_number)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_principle_category ON quranic_foundations (principle_category)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_legal_relevance ON quranic_foundations (legal_relevance_score)")
            
            await db.commit()
            logger.info("Islamic legal database schema initialized")
    
    async def analyze_islamic_legal_content(self, verse_text: str, surah_name: str, 
                                          ayah_number: int, qurtubi_commentary: str) -> Dict[str, Any]:
        """
        Use AI to analyze Islamic legal content and extract legal principles
        """
        
        analysis_prompt = f"""
        كخبير في الفقه الإسلامي والقانون السعودي، حلل هذه الآية القرآنية وتفسيرها:

        الآية: {verse_text}
        السورة: {surah_name} - الآية {ayah_number}
        تفسير القرطبي: {qurtubi_commentary[:2000]}...

        قدم تحليلاً فقهياً وقانونياً شاملاً بالتنسيق التالي (JSON):

        {{
            "legal_principle": "المبدأ القانوني الرئيسي مستخرج من الآية",
            "principle_category": "إحدى الفئات: العبادات، المعاملات، النكاح، الطلاق، المواريث، الجنايات، القضاء، الحدود، السياسة الشرعية، الأحوال الشخصية، القانون التجاري، العدالة، الحقوق، الواجبات",
            "applicable_legal_domains": ["مجال قانوني 1", "مجال قانوني 2"],
            "semantic_concepts": ["مفهوم 1", "مفهوم 2", "مفهوم 3"],
            "abstraction_level": "verse_specific أو principle_general أو universal_maxim",
            "modern_applications": ["تطبيق حديث 1", "تطبيق حديث 2"],
            "legal_precedence_level": "foundational أو supportive أو contextual",
            "cultural_appropriateness": 0.85,
            "scholarship_confidence": 0.90,
            "legal_relevance_score": 0.80,
            "interpretation_consensus": "strong أو moderate أو disputed"
        }}

        يجب أن يكون التحليل دقيقاً ومبنياً على المصادر الفقهية المعتبرة.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content
            # Find JSON block
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Validate required fields
                required_fields = [
                    'legal_principle', 'principle_category', 'applicable_legal_domains',
                    'semantic_concepts', 'abstraction_level', 'modern_applications',
                    'legal_precedence_level', 'cultural_appropriateness',
                    'scholarship_confidence', 'legal_relevance_score', 'interpretation_consensus'
                ]
                
                for field in required_fields:
                    if field not in analysis:
                        logger.warning(f"Missing field {field} in analysis")
                        analysis[field] = self._get_default_value(field)
                
                return analysis
            else:
                logger.error("No valid JSON found in response")
                return self._get_default_analysis()
                
        except Exception as e:
            logger.error(f"Error in Islamic legal analysis: {e}")
            return self._get_default_analysis()
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            'legal_principle': 'مبدأ عام',
            'principle_category': 'العدالة',
            'applicable_legal_domains': ['القانون العام'],
            'semantic_concepts': ['العدالة', 'الحق'],
            'abstraction_level': 'principle_general',
            'modern_applications': ['التطبيق في القضاء'],
            'legal_precedence_level': 'supportive',
            'cultural_appropriateness': 0.8,
            'scholarship_confidence': 0.7,
            'legal_relevance_score': 0.6,
            'interpretation_consensus': 'moderate'
        }
        return defaults.get(field, '')
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis when AI analysis fails"""
        return {
            'legal_principle': 'مبدأ عام من القرآن الكريم',
            'principle_category': 'العدالة',
            'applicable_legal_domains': ['القانون العام'],
            'semantic_concepts': ['العدالة', 'الحق', 'الشريعة'],
            'abstraction_level': 'principle_general',
            'modern_applications': ['التطبيق في القضاء السعودي'],
            'legal_precedence_level': 'supportive',
            'cultural_appropriateness': 0.8,
            'scholarship_confidence': 0.7,
            'legal_relevance_score': 0.6,
            'interpretation_consensus': 'moderate'
        }
    
    async def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-large",
                input=texts
            )
            
            embeddings = []
            for data in response.data:
                embedding = np.array(data.embedding, dtype=np.float32)
                embeddings.append(embedding)
            
            # Calculate cost
            total_tokens = sum(len(self.encoding.encode(text)) for text in texts)
            cost = total_tokens * 0.00013 / 1000
            self.total_cost += cost
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [np.zeros(3072, dtype=np.float32) for _ in texts]
    
    async def process_dataset(self):
        """Process the Quran dataset with Islamic legal analysis"""
        
        await self.initialize_database()
        
        logger.info("Loading Quran dataset...")
        dataset = load_dataset("MohamedRashad/Quran-Tafseer")
        verses = dataset['train']
        
        logger.info(f"Processing {len(verses)} verses...")
        
        batch_size = 10
        for i in range(0, len(verses), batch_size):
            batch = verses[i:i+batch_size]
            await self._process_batch(batch, i)
            
            # Log progress
            if (i + batch_size) % 100 == 0:
                logger.info(f"Processed {i + batch_size}/{len(verses)} verses. Cost: ${self.total_cost:.4f}")
        
        logger.info(f"🎉 Processing completed! Total cost: ${self.total_cost:.4f}")
    
    async def _process_batch(self, batch: List[Dict], start_idx: int):
        """Process a batch of verses"""
        
        foundations_to_insert = []
        
        for idx, verse_data in enumerate(batch):
            try:
                # Extract verse information
                verse_text = verse_data.get('arabic_text', '')
                surah_name = verse_data.get('surah_name', '')
                ayah_number = verse_data.get('ayah_number', 0)
                qurtubi_commentary = verse_data.get('qurtubi_tafseer', '')
                verse_reference = f"{surah_name}:{ayah_number}"
                
                # Generate foundation ID
                foundation_id = hashlib.md5(f"{verse_reference}_{verse_text}".encode()).hexdigest()
                
                # Perform Islamic legal analysis
                analysis = await self.analyze_islamic_legal_content(
                    verse_text, surah_name, ayah_number, qurtubi_commentary
                )
                
                # Prepare texts for embedding
                embedding_texts = [
                    verse_text,  # Verse embedding
                    analysis['legal_principle'],  # Principle embedding
                    '; '.join(analysis['modern_applications'])  # Application embedding
                ]
                
                # Generate embeddings
                embeddings = await self.generate_embeddings(embedding_texts)
                
                # Prepare foundation data
                foundation_data = {
                    'foundation_id': foundation_id,
                    'verse_text': verse_text,
                    'surah_name': surah_name,
                    'ayah_number': ayah_number,
                    'verse_reference': verse_reference,
                    'qurtubi_commentary': qurtubi_commentary,
                    'legal_principle': analysis['legal_principle'],
                    'principle_category': analysis['principle_category'],
                    'applicable_legal_domains': json.dumps(analysis['applicable_legal_domains'], ensure_ascii=False),
                    'semantic_concepts': json.dumps(analysis['semantic_concepts'], ensure_ascii=False),
                    'abstraction_level': analysis['abstraction_level'],
                    'modern_applications': json.dumps(analysis['modern_applications'], ensure_ascii=False),
                    'legal_precedence_level': analysis['legal_precedence_level'],
                    'cultural_appropriateness': analysis['cultural_appropriateness'],
                    'scholarship_confidence': analysis['scholarship_confidence'],
                    'legal_relevance_score': analysis['legal_relevance_score'],
                    'interpretation_consensus': analysis['interpretation_consensus'],
                    'verse_embedding': embeddings[0].tobytes(),
                    'principle_embedding': embeddings[1].tobytes(),
                    'application_embedding': embeddings[2].tobytes(),
                    'source_quality': 'authentic',
                    'last_updated': datetime.now().isoformat(),
                    'created_date': datetime.now().isoformat()
                }
                
                foundations_to_insert.append(foundation_data)
                self.processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing verse {start_idx + idx}: {e}")
                continue
        
        # Batch insert to database
        if foundations_to_insert:
            await self._insert_foundations(foundations_to_insert)
    
    async def _insert_foundations(self, foundations: List[Dict]):
        """Insert foundations into database"""
        
        async with aiosqlite.connect(self.db_path) as db:
            placeholders = ', '.join(['?' for _ in foundations[0].keys()])
            columns = ', '.join(foundations[0].keys())
            
            query = f"""
                INSERT OR REPLACE INTO quranic_foundations ({columns})
                VALUES ({placeholders})
            """
            
            values = [tuple(foundation.values()) for foundation in foundations]
            await db.executemany(query, values)
            await db.commit()
            
            logger.info(f"Inserted {len(foundations)} foundations into database")

async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python islamic_quranic_processor.py <OPENAI_API_KEY>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    processor = IslamicQuranicProcessor(api_key)
    
    try:
        await processor.process_dataset()
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    except Exception as e:
        logger.error(f"Processing failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())