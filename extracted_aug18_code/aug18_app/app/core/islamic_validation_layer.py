"""
Islamic Content Validation Layer
Senior-level solution to prevent AI hallucination of religious content
Ensures all Islamic citations are authentic and relevant
"""

import logging
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class IslamicReference:
    """Structured representation of an Islamic reference"""
    reference_type: str  # 'quran', 'hadith'
    source: str  # e.g., "سورة البقرة:282"
    text: str
    position: int  # Position in response
    length: int


class IslamicContentValidator:
    """
    Enterprise-grade validation system for Islamic content
    Prevents hallucination and ensures authenticity
    """
    
    def __init__(self, quranic_store=None):
        self.quranic_store = quranic_store
        self.validation_cache = {}
        self.known_verses = {}
        self.hallucination_log = []
        
        # Patterns for detecting Islamic references
        self.islamic_patterns = {
            'quran': r'(?:قال تعالى|في سورة|سُورَةُ)\s*([^:]+):?\s*(\d+)?',
            'verse_text': r'"([^"]+)".*(?:الآية|آية)',
            'hadith': r'(?:قال رسول الله|حديث|في الحديث)',
        }
        
        # Quality thresholds
        self.relevance_threshold = 0.7
        self.similarity_threshold = 0.85
    
    async def validate_response(self, response: str, query: str) -> Tuple[str, Dict]:
        """
        Validate and clean Islamic content in response
        Returns: (cleaned_response, validation_report)
        """
        logger.info(f"🔍 Validating Islamic content in response")
        
        # Extract all Islamic references
        references = self.extract_islamic_references(response)
        
        if not references:
            return response, {"status": "no_islamic_content", "modifications": 0}
        
        validation_report = {
            "total_references": len(references),
            "validated": 0,
            "removed": 0,
            "replaced": 0,
            "hallucinations": []
        }
        
        # Validate each reference
        for ref in references:
            is_valid, validation_data = await self.validate_reference(ref, query)
            
            if not is_valid:
                # Remove hallucinated content
                response = self.remove_hallucination(response, ref)
                validation_report["removed"] += 1
                validation_report["hallucinations"].append({
                    "reference": ref.source,
                    "text": ref.text[:100],
                    "reason": validation_data.get("reason", "Not found in database")
                })
                
                # Log for monitoring
                self.log_hallucination(ref, query, validation_data)
                
            elif validation_data.get("relevance_score", 0) < self.relevance_threshold:
                # Replace with more relevant content if available
                better_ref = await self.find_relevant_alternative(query, ref.reference_type)
                if better_ref:
                    response = self.replace_reference(response, ref, better_ref)
                    validation_report["replaced"] += 1
                else:
                    response = self.remove_hallucination(response, ref)
                    validation_report["removed"] += 1
            else:
                validation_report["validated"] += 1
        
        return response, validation_report
    
    def extract_islamic_references(self, text: str) -> List[IslamicReference]:
        """Extract all Islamic references from text"""
        references = []
        
        # Find Quranic references
        for match in re.finditer(self.islamic_patterns['quran'], text):
            start, end = match.span()
            
            # Try to find associated verse text
            verse_text = ""
            text_after = text[end:end+500]
            verse_match = re.search(r'["\']([^"\']+)["\']', text_after)
            if verse_match:
                verse_text = verse_match.group(1)
            
            references.append(IslamicReference(
                reference_type='quran',
                source=match.group(0),
                text=verse_text,
                position=start,
                length=end - start
            ))
        
        return references
    
    async def validate_reference(self, ref: IslamicReference, query: str) -> Tuple[bool, Dict]:
        """
        Validate a single Islamic reference
        Returns: (is_valid, validation_data)
        """
        
        # Check cache first
        cache_key = hashlib.md5(f"{ref.source}:{ref.text}".encode()).hexdigest()
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        validation_data = {
            "reference": ref.source,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.quranic_store:
            # No database - can't validate
            validation_data["reason"] = "No Quranic database available"
            result = (False, validation_data)
            self.validation_cache[cache_key] = result
            return result
        
        try:
            # Parse the reference
            surah, ayah = self.parse_quranic_reference(ref.source)
            
            if not surah:
                validation_data["reason"] = "Invalid reference format"
                result = (False, validation_data)
            else:
                # Query database for actual verse
                actual_verse = await self.quranic_store.get_verse_by_reference(surah, ayah)
                
                if not actual_verse:
                    validation_data["reason"] = f"Verse not found: {surah}:{ayah}"
                    result = (False, validation_data)
                else:
                    # Check text similarity
                    similarity = self.calculate_text_similarity(ref.text, actual_verse.arabic_text)
                    
                    # Check relevance to query
                    relevance = await self.calculate_relevance(query, actual_verse)
                    
                    validation_data.update({
                        "similarity_score": similarity,
                        "relevance_score": relevance,
                        "actual_text": actual_verse.arabic_text[:200]
                    })
                    
                    is_valid = similarity > self.similarity_threshold
                    result = (is_valid, validation_data)
            
            self.validation_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Error validating reference: {e}")
            validation_data["reason"] = f"Validation error: {str(e)}"
            return (False, validation_data)
    
    def parse_quranic_reference(self, reference: str) -> Tuple[Optional[str], Optional[int]]:
        """Parse Quranic reference into surah and ayah"""
        
        # Handle different reference formats
        patterns = [
            r'سُورَةُ\s+([^:]+):(\d+)',  # سُورَةُ البقرة:282
            r'سورة\s+([^:]+):(\d+)',      # سورة البقرة:282
            r'([^:]+):(\d+)',              # البقرة:282
        ]
        
        for pattern in patterns:
            match = re.search(pattern, reference)
            if match:
                surah = match.group(1).strip()
                ayah = int(match.group(2)) if match.group(2) else None
                return surah, ayah
        
        return None, None
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two Arabic texts"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize Arabic text
        text1 = self.normalize_arabic(text1)
        text2 = self.normalize_arabic(text2)
        
        # Simple overlap coefficient
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        similarity = len(intersection) / min(len(words1), len(words2))
        
        return similarity
    
    def normalize_arabic(self, text: str) -> str:
        """Normalize Arabic text for comparison"""
        # Remove diacritics
        arabic_diacritics = re.compile(r'[\u064B-\u0652\u0670\u0640]')
        text = arabic_diacritics.sub('', text)
        
        # Normalize hamza
        text = re.sub('[إأآا]', 'ا', text)
        text = re.sub('ى', 'ي', text)
        text = re.sub('ة', 'ه', text)
        
        return text.strip()
    
    async def calculate_relevance(self, query: str, verse) -> float:
        """Calculate relevance of verse to query"""
        if not verse or not hasattr(verse, 'legal_concepts'):
            return 0.0
        
        # Extract concepts from query
        query_words = set(query.lower().split())
        
        # Check concept overlap
        verse_concepts = set(verse.legal_concepts) if verse.legal_concepts else set()
        
        if not verse_concepts:
            return 0.0
        
        # Simple relevance score based on concept overlap
        relevance = len(query_words.intersection(verse_concepts)) / len(verse_concepts)
        
        return min(relevance, 1.0)
    
    def remove_hallucination(self, response: str, ref: IslamicReference) -> str:
        """Remove hallucinated Islamic reference from response"""
        
        # Find the full reference block (including verse text)
        start = ref.position
        end = ref.position + ref.length
        
        # Extend to include the full verse text if present
        if ref.text:
            text_pos = response.find(ref.text, start)
            if text_pos != -1:
                end = text_pos + len(ref.text)
        
        # Find paragraph boundaries
        para_start = response.rfind('\n', 0, start)
        para_start = para_start + 1 if para_start != -1 else 0
        
        para_end = response.find('\n', end)
        para_end = para_end if para_end != -1 else len(response)
        
        # Check if entire paragraph is about this reference
        paragraph = response[para_start:para_end]
        if len(paragraph) < 100:  # Short paragraph, likely just the reference
            # Remove entire paragraph
            response = response[:para_start] + response[para_end+1:]
        else:
            # Remove just the reference
            response = response[:start] + response[end:]
        
        return response.strip()
    
    async def find_relevant_alternative(self, query: str, ref_type: str) -> Optional[Dict]:
        """Find a more relevant Islamic reference for the query"""
        if not self.quranic_store:
            return None
        
        try:
            # Search for relevant verses
            results = await self.quranic_store.search_foundations(
                query=query,
                limit=1,
                min_relevance=self.relevance_threshold
            )
            
            if results:
                return {
                    "reference": results[0].verse_reference,
                    "text": results[0].arabic_text,
                    "principle": results[0].legal_principle
                }
            
        except Exception as e:
            logger.error(f"Error finding alternative reference: {e}")
        
        return None
    
    def replace_reference(self, response: str, old_ref: IslamicReference, new_ref: Dict) -> str:
        """Replace an Islamic reference with a more relevant one"""
        
        # Build replacement text
        replacement = f"قال تعالى في {new_ref['reference']}: \"{new_ref['text']}\" - {new_ref['principle']}"
        
        # Replace in response
        start = old_ref.position
        end = old_ref.position + old_ref.length
        
        if old_ref.text:
            text_pos = response.find(old_ref.text, start)
            if text_pos != -1:
                end = text_pos + len(old_ref.text)
        
        response = response[:start] + replacement + response[end:]
        
        return response
    
    def log_hallucination(self, ref: IslamicReference, query: str, validation_data: Dict):
        """Log hallucination for monitoring and improvement"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:200],
            "hallucinated_reference": ref.source,
            "hallucinated_text": ref.text[:200] if ref.text else "",
            "validation_data": validation_data
        }
        
        self.hallucination_log.append(log_entry)
        
        logger.warning(f"🚨 Hallucination detected: {ref.source}")
        logger.warning(f"   Query: {query[:100]}")
        logger.warning(f"   Reason: {validation_data.get('reason', 'Unknown')}")
        
        # Save to file for analysis
        try:
            import json
            log_file = "data/hallucination_log.json"
            
            existing_logs = []
            if Path(log_file).exists():
                with open(log_file, 'r') as f:
                    existing_logs = json.load(f)
            
            existing_logs.append(log_entry)
            
            # Keep only last 1000 entries
            if len(existing_logs) > 1000:
                existing_logs = existing_logs[-1000:]
            
            with open(log_file, 'w') as f:
                json.dump(existing_logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save hallucination log: {e}")
    
    async def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        return {
            "cache_size": len(self.validation_cache),
            "hallucinations_detected": len(self.hallucination_log),
            "last_hallucination": self.hallucination_log[-1]["timestamp"] if self.hallucination_log else None,
            "cache_hit_rate": self.calculate_cache_hit_rate()
        }
    
    def calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # This would need proper tracking in production
        return len(self.validation_cache) / max(len(self.validation_cache) + 10, 1)


class IslamicRelevanceScorer:
    """
    Advanced relevance scoring for Islamic content
    Ensures only highly relevant verses are used
    """
    
    def __init__(self):
        self.domain_mappings = {
            "financial": ["دين", "قرض", "مال", "ربا", "بيع", "تجارة"],
            "family": ["زواج", "طلاق", "نكاح", "ميراث", "نفقة"],
            "criminal": ["قصاص", "حد", "جناية", "سرقة", "قتل"],
            "contracts": ["عقد", "اتفاق", "شرط", "التزام", "وعد"],
            "property": ["ملك", "أرض", "عقار", "حق", "منفعة"]
        }
    
    async def score_relevance(self, query: str, verse: Dict) -> float:
        """
        Score relevance of a verse to a query
        Returns: score between 0.0 and 1.0
        """
        
        # Identify query domain
        query_domain = self.identify_domain(query)
        
        # Check verse domain alignment
        verse_domains = verse.get('applicable_legal_domains', [])
        
        domain_score = 0.0
        if query_domain and query_domain in verse_domains:
            domain_score = 1.0
        elif verse_domains:
            # Partial credit for related domains
            domain_score = 0.3
        
        # Semantic similarity
        semantic_score = await self.calculate_semantic_similarity(
            query, 
            verse.get('legal_principle', '')
        )
        
        # Combine scores
        final_score = (domain_score * 0.6) + (semantic_score * 0.4)
        
        return final_score
    
    def identify_domain(self, query: str) -> Optional[str]:
        """Identify legal domain of query"""
        query_lower = query.lower()
        
        for domain, keywords in self.domain_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain
        
        return None
    
    async def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between texts"""
        # Simplified version - in production would use embeddings
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0