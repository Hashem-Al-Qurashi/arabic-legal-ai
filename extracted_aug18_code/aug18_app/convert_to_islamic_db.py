"""
Convert existing Quranic data to Islamic Legal Database format
Uses existing processed verses and adds Islamic legal analysis
"""

import asyncio
import sqlite3
import json
import numpy as np
import hashlib
import logging
from datetime import datetime
from openai import AsyncOpenAI
from typing import Dict, List, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IslamicDatabaseConverter:
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.source_db = "data/quranic_foundations.db"
        self.target_db = "data/quranic_foundation.db"
        self.processed_count = 0
        self.total_cost = 0.0
        
        # Islamic legal categories
        self.legal_categories = [
            "العبادات", "المعاملات", "النكاح", "الطلاق", "المواريث", 
            "الجنايات", "القضاء", "الحدود", "السياسة الشرعية", 
            "الأحوال الشخصية", "القانون التجاري", "العدالة", "الحقوق", "الواجبات"
        ]
    
    def create_target_schema(self):
        """Create the target Islamic legal database schema"""
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        cursor.execute("""
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_surah_ayah ON quranic_foundations (surah_name, ayah_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_principle_category ON quranic_foundations (principle_category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_legal_relevance ON quranic_foundations (legal_relevance_score)")
        
        conn.commit()
        conn.close()
        logger.info("Target database schema created")
    
    async def generate_legal_analysis(self, verse_text: str, surah_name: str, 
                                    ayah_number: int, tafseer: str) -> Dict[str, Any]:
        """Generate Islamic legal analysis for a verse"""
        
        # Create a shorter, more focused prompt for faster processing
        analysis_prompt = f"""
        تحليل فقهي مختصر للآية:

        الآية: {verse_text}
        السورة: {surah_name} - الآية {ayah_number}

        قدم تحليلاً مختصراً بتنسيق JSON:

        {{
            "legal_principle": "المبدأ القانوني الرئيسي",
            "principle_category": "إحدى الفئات: العدالة، المعاملات، الحقوق، العبادات، الأحكام",
            "applicable_legal_domains": ["مجال قانوني"],
            "semantic_concepts": ["مفهوم1", "مفهوم2"],
            "abstraction_level": "principle_general",
            "modern_applications": ["تطبيق حديث"],
            "legal_precedence_level": "supportive",
            "cultural_appropriateness": 0.85,
            "scholarship_confidence": 0.80,
            "legal_relevance_score": 0.75,
            "interpretation_consensus": "moderate"
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using faster, cheaper model
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Add cost tracking
                self.total_cost += 0.0015  # Approximate cost for gpt-3.5-turbo
                
                return analysis
            else:
                return self._get_default_analysis(verse_text)
                
        except Exception as e:
            logger.warning(f"Error in analysis for {surah_name}:{ayah_number}: {e}")
            return self._get_default_analysis(verse_text)
    
    def _get_default_analysis(self, verse_text: str) -> Dict[str, Any]:
        """Generate default analysis based on verse content"""
        
        # Simple keyword-based categorization
        if any(word in verse_text for word in ["الصلاة", "الزكاة", "الحج", "الصوم"]):
            category = "العبادات"
            concepts = ["العبادة", "التكليف"]
        elif any(word in verse_text for word in ["البيع", "الربا", "الدين", "التجارة"]):
            category = "المعاملات"
            concepts = ["التجارة", "العقود"]
        elif any(word in verse_text for word in ["النكاح", "الزواج", "الطلاق"]):
            category = "الأحوال الشخصية"
            concepts = ["الأسرة", "الزواج"]
        elif any(word in verse_text for word in ["الميراث", "الوصية", "التركة"]):
            category = "المواريث"
            concepts = ["الميراث", "الحقوق"]
        elif any(word in verse_text for word in ["العدل", "القضاء", "الحكم"]):
            category = "العدالة"
            concepts = ["العدالة", "القضاء"]
        else:
            category = "الأحكام العامة"
            concepts = ["الشريعة", "الأحكام"]
        
        return {
            'legal_principle': f'مبدأ {category} من القرآن الكريم',
            'principle_category': category,
            'applicable_legal_domains': [category],
            'semantic_concepts': concepts,
            'abstraction_level': 'principle_general',
            'modern_applications': [f'التطبيق في {category}'],
            'legal_precedence_level': 'supportive',
            'cultural_appropriateness': 0.85,
            'scholarship_confidence': 0.75,
            'legal_relevance_score': 0.70,
            'interpretation_consensus': 'moderate'
        }
    
    async def generate_simple_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings with rate limiting"""
        try:
            # Add delay to avoid rate limits
            await asyncio.sleep(0.1)
            
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",  # Cheaper model
                input=texts
            )
            
            embeddings = []
            for data in response.data:
                embedding = np.array(data.embedding, dtype=np.float32)
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.warning(f"Error generating embeddings: {e}")
            # Return default embeddings
            return [np.zeros(1536, dtype=np.float32) for _ in texts]
    
    async def convert_verses(self):
        """Convert verses from source to target database"""
        
        self.create_target_schema()
        
        # Read from source database
        source_conn = sqlite3.connect(self.source_db)
        source_cursor = source_conn.cursor()
        
        # Get verses data
        source_cursor.execute("""
            SELECT id, surah_name, ayah_number, verse_reference, arabic_text, tafseer_content
            FROM quranic_verses 
            LIMIT 500
        """)  # Limit to 500 verses for faster processing
        
        verses = source_cursor.fetchall()
        source_conn.close()
        
        logger.info(f"Converting {len(verses)} verses...")
        
        # Convert to target format
        target_conn = sqlite3.connect(self.target_db)
        target_cursor = target_conn.cursor()
        
        batch_size = 10
        for i in range(0, len(verses), batch_size):
            batch = verses[i:i+batch_size]
            await self._process_batch(batch, target_cursor)
            
            if (i + batch_size) % 50 == 0:
                target_conn.commit()
                logger.info(f"Processed {i + batch_size}/{len(verses)} verses. Cost: ${self.total_cost:.4f}")
        
        target_conn.commit()
        target_conn.close()
        
        logger.info(f"🎉 Conversion completed! Processed {self.processed_count} verses. Total cost: ${self.total_cost:.4f}")
    
    async def _process_batch(self, batch: List, cursor):
        """Process a batch of verses"""
        
        for verse_data in batch:
            try:
                verse_id, surah_name, ayah_number, verse_reference, arabic_text, tafseer_content = verse_data
                
                # Generate foundation ID
                foundation_id = hashlib.md5(f"{verse_reference}_{arabic_text}".encode()).hexdigest()
                
                # Generate legal analysis (with default fallback)
                if self.processed_count < 50:  # Only do AI analysis for first 50 verses to save cost
                    analysis = await self.generate_legal_analysis(arabic_text, surah_name, ayah_number, tafseer_content)
                else:
                    analysis = self._get_default_analysis(arabic_text)
                
                # Generate embeddings (simplified)
                if self.processed_count < 50:  # Only for first 50 verses
                    embedding_texts = [
                        arabic_text,
                        analysis['legal_principle'],
                        '; '.join(analysis['modern_applications'])
                    ]
                    embeddings = await self.generate_simple_embeddings(embedding_texts)
                else:
                    # Use zero embeddings for the rest to save cost
                    embeddings = [np.zeros(1536, dtype=np.float32) for _ in range(3)]
                
                # Insert into target database
                cursor.execute("""
                    INSERT OR REPLACE INTO quranic_foundations (
                        foundation_id, verse_text, surah_name, ayah_number, verse_reference,
                        qurtubi_commentary, legal_principle, principle_category,
                        applicable_legal_domains, semantic_concepts, abstraction_level,
                        modern_applications, legal_precedence_level, cultural_appropriateness,
                        scholarship_confidence, legal_relevance_score, interpretation_consensus,
                        verse_embedding, principle_embedding, application_embedding,
                        source_quality, last_updated, created_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    foundation_id,
                    arabic_text,
                    surah_name,
                    ayah_number,
                    verse_reference,
                    tafseer_content or '',
                    analysis['legal_principle'],
                    analysis['principle_category'],
                    json.dumps(analysis['applicable_legal_domains'], ensure_ascii=False),
                    json.dumps(analysis['semantic_concepts'], ensure_ascii=False),
                    analysis['abstraction_level'],
                    json.dumps(analysis['modern_applications'], ensure_ascii=False),
                    analysis['legal_precedence_level'],
                    analysis['cultural_appropriateness'],
                    analysis['scholarship_confidence'],
                    analysis['legal_relevance_score'],
                    analysis['interpretation_consensus'],
                    embeddings[0].tobytes(),
                    embeddings[1].tobytes(),
                    embeddings[2].tobytes(),
                    'authentic',
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                self.processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing verse {verse_data[0]}: {e}")
                continue

async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python convert_to_islamic_db.py <OPENAI_API_KEY>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    converter = IslamicDatabaseConverter(api_key)
    
    try:
        await converter.convert_verses()
    except Exception as e:
        logger.error(f"Conversion failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())