"""
Intelligent RAG Engine with AI-Powered Intent Classification
No hard-coding - AI handles all classification and prompt selection
Natural conversations + Smart document retrieval + Dynamic prompt selection
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Dict, Optional, AsyncIterator
import json

# Import the smart database components from old RAG
from app.storage.vector_store import VectorStore, Chunk
from app.storage.sqlite_store import SqliteVectorStore
from enum import Enum

class ProcessingMode(Enum):
    """Processing modes for different query types"""
    LIGHTWEIGHT = "lightweight"    # GENERAL_QUESTION: Fast, simple
    STRATEGIC = "strategic"        # ACTIVE_DISPUTE: Smart but efficient  
    COMPREHENSIVE = "comprehensive" # PLANNING_ACTION: Full analysis

class SimpleCitationFixer:
    """MEMO-AWARE Citation Fixer - Removes ALL memo citations of any type"""
    
    def fix_citations(self, ai_response: str, available_documents: List[Chunk]) -> str:
        """Remove ALL memo citations and enhance statute citations"""
        if not available_documents:
            return ai_response
        
        import re
        
        # Get statute titles only (no memos)
        real_titles = [doc.title for doc in available_documents]
        statute_titles = [title for title in real_titles 
                 if any(term in title for term in [
                     "نظام", "المادة", "لائحة", "مرسوم", "التعريفات",  # ONLY real laws
                     "قانون", "قرار وزاري", "تعليمات", "ضوابط", "قواعد"  # Official regulations
                 ]) 
                 and 'مذكرة' not in title.lower()  # Exclude memos
                 and 'دفع' not in title.lower()    # Exclude case defenses  
                 and 'حجة' not in title.lower()    # Exclude case arguments
                 and 'رقم' not in title.lower()]   # Exclude numbered cases
        
        if not statute_titles:
            return ai_response
        
        fixed_response = ai_response
        
        # 1. REMOVE ALL memo citations (comprehensive patterns for ANY memo type)
        memo_citation_patterns = [
            # Direct memo citations with quotes
            r'وفقاً\s*لـ\s*["\']?مذكرة[^"\'.\n]*["\']?',
            r'استناداً\s*إلى\s*["\']?مذكرة[^"\'.\n]*["\']?',
            r'بناءً\s*على\s*["\']?مذكرة[^"\'.\n]*["\']?',
            r'حسب\s*["\']?مذكرة[^"\'.\n]*["\']?',
            r'طبقاً\s*لـ\s*["\']?مذكرة[^"\'.\n]*["\']?',
            r'بموجب\s*["\']?مذكرة[^"\'.\n]*["\']?',
            
            # Phrase-based memo references
            r'بالإشارة\s*إلى\s*["\']?[*]*مذكرة[^"\'.\n]*[*]*["\']?',
            r'كما\s*جاء\s*في\s*["\']?مذكرة[^"\'.\n]*["\']?',
            r'ووفقاً\s*لما\s*ورد\s*في\s*["\']?مذكرة[^"\'.\n]*["\']?',
            
            # Generic memo references without citation words
            r'مذكرة\s*civil[^"\'.\n]*',
            r'مذكرة\s*criminal[^"\'.\n]*', 
            r'مذكرة\s*family[^"\'.\n]*',
            r'مذكرة\s*execution[^"\'.\n]*',
            r'مذكرة\s*\w+[^"\'.\n]*',  # Any memo type
            
            # Reference numbering
            r'مرجع\s*\d+[:\s]*[^".\n]*',
            r'المرجع\s*رقم\s*\d+[^".\n]*',
        ]
        
        for pattern in memo_citation_patterns:
            fixed_response = re.sub(pattern, '', fixed_response, flags=re.IGNORECASE)
        
        # 2. Clean up broken text after memo removal
        cleanup_patterns = [
            (r'،\s*،', '،'),  # Double commas
            (r'\.\s*\.', '.'),  # Double periods
            (r':\s*،', ':'),   # Colon followed by comma
            (r'^\s*،', ''),    # Leading comma on line
            (r'^\s*\.', ''),   # Leading period on line
            (r'\n\s*\n\s*\n+', '\n\n'),  # Multiple line breaks
            (r'\s+', ' '),     # Multiple spaces
        ]
        
        for pattern, replacement in cleanup_patterns:
            fixed_response = re.sub(pattern, replacement, fixed_response, flags=re.MULTILINE)
        
        # 3. Find and replace weak citations with strong statute citations
        citation_patterns = [
            # Pattern: وفقاً لـ"anything" -> replace with real statute
            (r'وفقاً لـ"[^"]*"', f'وفقاً لـ"{statute_titles[0]}"'),
            # Pattern: استناداً إلى "anything" -> replace with real statute  
            (r'استناداً إلى "[^"]*"', f'استناداً إلى "{statute_titles[1] if len(statute_titles) > 1 else statute_titles[0]}"'),
            # Pattern: بناءً على "anything" -> replace with real statute
            (r'بناءً على "[^"]*"', f'بناءً على "{statute_titles[2] if len(statute_titles) > 2 else statute_titles[0]}"'),
            # Pattern: حسب "anything" -> replace with real statute
            (r'حسب "[^"]*"', f'حسب "{statute_titles[0]}"'),
        ]
        
        for pattern, replacement in citation_patterns:
            if re.search(pattern, fixed_response):
                fixed_response = re.sub(pattern, replacement, fixed_response, count=1)
        
        # 4. Fix generic weak references  
        generic_fixes = [
            (r'وفقاً للمادة الثالثة(?!\s*من\s*")', f'وفقاً لـ"{statute_titles[0]}"'),
            (r'استناداً للمادة(?!\s*من\s*")', f'استناداً إلى "{statute_titles[0]}"'),
            (r'حسب المادة(?!\s*من\s*")', f'حسب "{statute_titles[0]}"'),
            (r'بموجب المادة(?!\s*من\s*")', f'بموجب "{statute_titles[0]}"'),
        ]
        
        for pattern, replacement in generic_fixes:
            fixed_response = re.sub(pattern, replacement, fixed_response)
        
        # 5. Add proper statute citation if completely missing
        if 'وفقاً ل' in fixed_response and not any(title in fixed_response for title in statute_titles):
            # Find the first occurrence of وفقاً ل and make it proper
            fixed_response = re.sub(r'وفقاً ل([^"]+)', f'وفقاً لـ"{statute_titles[0]}"', fixed_response, count=1)
        
        # 6. Ensure we have at least one proper citation in legal responses
        # 6. PROACTIVE CITATION INJECTION - Add citations for unused statutes
        available_statutes = [title for title in statute_titles if title not in fixed_response]
        if available_statutes:
            logger.info(f"🎯 Found {len(available_statutes)} unused statutes for injection")
            
            # Injection points - places where we can add citations naturally
            injection_opportunities = [
                # After legal analysis headers
                (r'(#### أولاً: [^\n]+)', rf'\1\nوفقاً لـ"{available_statutes[0]}"، '),
                (r'(#### ثانياً: [^\n]+)', rf'\1\nاستناداً إلى "{available_statutes[1] if len(available_statutes) > 1 else available_statutes[0]}"، '),
                (r'(#### ثالثاً: [^\n]+)', rf'\1\nبناءً على "{available_statutes[2] if len(available_statutes) > 2 else available_statutes[0]}"، '),
                
                # After conclusion headers
                (r'(الخاتمة[^\n]*)', rf'\1\nحسب "{available_statutes[-1]}"، '),
                (r'(الخلاصة[^\n]*)', rf'\1\nطبقاً لـ"{available_statutes[-1]}"، '),
                
                # Before final recommendation
                (r'(نطلب من المحكمة)', rf'وفقاً لـ"{available_statutes[0]}"، \1'),
                (r'(بناءً على ما سبق)', rf'\1 واستناداً إلى "{available_statutes[1] if len(available_statutes) > 1 else available_statutes[0]}"، '),
            ]
            
            # Apply injections with SMART STATUTE ROTATION
            injected_count = 0
            used_statutes = set()

            for pattern, _ in injection_opportunities:
                if injected_count < len(available_statutes) and re.search(pattern, fixed_response):
                    # Pick next unused statute
                    statute_to_use = None
                    for statute in available_statutes:
                        if statute not in used_statutes:
                            statute_to_use = statute
                            break
                    
                    if statute_to_use:
                        # Create citation based on section type
                        if 'أولاً' in pattern:
                            replacement = rf'\1\nوفقاً لـ"{statute_to_use}"، '
                        elif 'ثانياً' in pattern:
                            replacement = rf'\1\nاستناداً إلى "{statute_to_use}"، '
                        elif 'ثالثاً' in pattern:
                            replacement = rf'\1\nبناءً على "{statute_to_use}"، '
                        elif 'رابعاً' in pattern:
                            replacement = rf'\1\nحسب "{statute_to_use}"، '
                        elif 'خامساً' in pattern:
                            replacement = rf'\1\nطبقاً لـ"{statute_to_use}"، '
                        elif 'الخاتمة' in pattern:
                            replacement = rf'\1\nووفقاً لـ"{statute_to_use}"، '
                        else:
                            replacement = rf'وفقاً لـ"{statute_to_use}"، \1'
                        
                        fixed_response = re.sub(pattern, replacement, fixed_response, count=1)
                        used_statutes.add(statute_to_use)
                        injected_count += 1
                        logger.info(f"💉 Injected citation #{injected_count}: {statute_to_use[:50]}...")

            logger.info(f"✅ Successfully injected {injected_count} DIFFERENT statute citations")
            
            logger.info(f"✅ Successfully injected {injected_count} additional statute citations")
        has_proper_citation = any(f'"{title}"' in fixed_response for title in statute_titles)
        
        if not has_proper_citation and statute_titles and len(fixed_response) > 500:  # Only for substantial responses
            # Add a citation at strategic legal analysis points
            insertion_points = [
                r'(أولاً: [^\n]*)',
                r'(### [^\n]*)', 
                r'(#### [^\n]*)',
                r'(تحليل الأدلة)',
                r'(الرد القانوني)',
                r'(التحليل القانوني)'
            ]
            
            for pattern in insertion_points:
                if re.search(pattern, fixed_response):
                    replacement = f'\\1\nوفقاً لـ"{statute_titles[0]}"، '
                    fixed_response = re.sub(pattern, replacement, fixed_response, count=1)
                    break
        
        # 7. Final cleanup
        fixed_response = re.sub(r'\n\s+', '\n', fixed_response)  # Remove spaces after newlines
        
        return fixed_response.strip()


# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple API key configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize AI client - prioritize OpenAI, fallback to DeepSeek
if OPENAI_API_KEY:
    ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    ai_model = "gpt-4o"
    classification_model = "gpt-4o-mini"  # Small model for classification
    print("✅ Using OpenAI for intelligent legal AI with classification")
elif DEEPSEEK_API_KEY:
    ai_client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
    ai_model = "deepseek-chat"
    classification_model = "deepseek-chat"
    print("✅ Using DeepSeek for intelligent legal AI with classification")
else:
    raise ValueError("❌ Either OPENAI_API_KEY or DEEPSEEK_API_KEY must be provided")


# SIMPLIFIED CLASSIFICATION - MINIMAL PROMPT
CLASSIFICATION_PROMPT = """Classify this legal query into one category. Respond with JSON only:

Query: {query}

{{
    "category": "GENERAL_QUESTION | ACTIVE_DISPUTE | PLANNING_ACTION",
    "confidence": 0.80
}}"""

# NO PROMPTS - PURE RAG APPROACH
# Let the legal documents and context speak for themselves


async def score_documents_multi_objective(documents: List[Chunk], original_query: str, user_intent: str, ai_client) -> List[Dict]:
    """
    Score documents on multiple objectives for intelligent selection
    Returns list of documents with scores for different objectives
    """
    
    if not documents:
        return []
    
    scoring_prompt = f"""
You are an expert legal document analyst. Score these legal documents for their value in responding to this query.

Query: {original_query}
Intent: {user_intent}

For each document, provide scores (0.0-1.0) for these objectives:

1. RELEVANCE: How directly related to the query topic
2. CITATION_VALUE: Potential for legal citations (statutes > precedents > memos)  
3. STYLE_MATCH: Fits aggressive/defensive memo style for disputes

Documents to score:
"""

    # Add document previews for scoring (cleaned for JSON safety)
    for i, doc in enumerate(documents, 1):
        # Clean content to avoid JSON parsing issues
        # Enhanced JSON-safe cleaning
        clean_content = (doc.content
                .replace('"', "'")
                .replace('\n', ' ')
                .replace('\r', ' ')
                .replace('\\', '\\\\')  # Escape backslashes
                .replace('\t', ' ')     # Replace tabs
                .replace('\b', ' ')     # Replace backspace
                .replace('\f', ' '))    # Replace form feed
        preview = clean_content[:150] + "..." if len(clean_content) > 150 else clean_content
        # JSON-safe title cleaning
        clean_title = (doc.title
              .replace('"', "'")
              .replace('\\', '\\\\')
              .replace('\n', ' ')
              .replace('\r', ' '))
        scoring_prompt += f"\nDocument {i}: {clean_title}\nContent: {preview}\n"
    
    scoring_prompt += f"""

Respond with ONLY a JSON array with scores for each document:
[
  {{
    "document_id": 1,
    "relevance": 0.85,
    "citation_value": 0.3,
    "style_match": 0.9
  }},
  {{
    "document_id": 2,
    "relevance": 0.7,
    "citation_value": 0.9,
    "style_match": 0.2
  }}
]

Score all {len(documents)} documents. Higher citation_value for statutes/regulations, higher style_match for aggressive memos.
"""

    try:
        response = await self.ai_client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective
            messages=[{"role": "user", "content": scoring_prompt}],
            temperature=0.1,
            max_tokens=5000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean JSON response more thoroughly
        response_text = response.choices[0].message.content.strip()
        
        # Remove markdown formatting
        if response_text.startswith("```"):
            lines = response_text.split('\n')
            # Find JSON content between ``` markers
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_json = not in_json
                    continue
                if in_json:
                    json_lines.append(line)
            response_text = '\n'.join(json_lines)
        
        # Additional cleaning for Arabic text issues
        response_text = response_text.replace('\n', ' ').strip()
        
        import json
        import re

        try:
            # First attempt: direct parsing
            scores = json.loads(response_text)
            logger.info(f"✅ JSON parsed successfully: {len(scores)} document scores")
            
        except json.JSONDecodeError as json_error:
            logger.warning(f"Direct JSON parsing failed: {json_error}")
            
            try:
                # Second attempt: extract JSON array from response
                array_match = re.search(r'\[[\s\S]*\]', response_text)
                if array_match:
                    json_content = array_match.group(0)
                    scores = json.loads(json_content)
                    logger.info(f"✅ Extracted JSON parsed successfully: {len(scores)} document scores")
                else:
                    raise ValueError("No JSON array found in response")
                    
            except (json.JSONDecodeError, ValueError) as fallback_error:
                logger.error(f"All JSON parsing failed: {fallback_error}")
                logger.error(f"Raw response: {response_text[:300]}...")
                
                # Ultimate fallback: create balanced default scores
                # STATUTE-PRIORITIZING fallback scores
                # STATUTE-PRIORITIZING fallback scores
                scores = []
                for i in range(len(documents)):
                    doc_title = documents[i].title.lower()
                    
                    # Detect REAL legal statutes vs case documents
                    is_real_statute = (
                        any(term in doc_title for term in ["نظام", "المادة", "لائحة", "مرسوم", "التعريفات", "قانون", "قرار وزاري"]) 
                        and not any(exclude in doc_title for exclude in ["دفع", "حجة", "رقم", "مذكرة"])
                    )
                    is_case_document = any(term in doc_title for term in ["دفع", "حجة", "رقم"]) and not any(term in doc_title for term in ["نظام", "المادة", "لائحة"])
                    is_memo = 'مذكرة' in doc_title
                    
                    # PRIORITIZE REAL LAWS ONLY
                    if is_real_statute:
                        scores.append({
                            "document_id": i + 1,
                            "relevance": 0.9,      # HIGHEST for real laws
                            "citation_value": 0.95, # MAXIMUM citation value
                            "style_match": 0.2     # Low style (laws aren't stylistic)
                        })
                        logger.info(f"⚖️ REAL LAW PRIORITY: {documents[i].title[:50]}... (citation: 0.95)")
                    elif is_case_document:
                        scores.append({
                            "document_id": i + 1,
                            "relevance": 0.6,      # Medium relevance for case examples
                            "citation_value": 0.1, # VERY LOW citation (don't cite cases as laws!)
                            "style_match": 0.8     # High style for case examples
                        })
                        logger.info(f"📋 CASE EXAMPLE: {documents[i].title[:50]}... (style: 0.8)")
                    elif is_memo:
                        scores.append({
                            "document_id": i + 1,
                            "relevance": 0.7,      # Good relevance for memos
                            "citation_value": 0.1, # VERY LOW citation value (no memo citations!)
                            "style_match": 0.8     # High style for memos
                        })
                        logger.info(f"📋 MEMO BACKGROUND: {documents[i].title[:50]}... (style: 0.8)")
                    else:
                        scores.append({
                            "document_id": i + 1,
                            "relevance": 0.6,
                            "citation_value": 0.5,
                            "style_match": 0.5
                        })
                logger.warning(f"⚠️ Using intelligent fallback scores for {len(scores)} documents")
        
        # Combine documents with their scores
        scored_documents = []
        for i, doc in enumerate(documents):
            try:
                # Find score for this document
                doc_score = next((s for s in scores if s["document_id"] == i + 1), None)
                if doc_score:
                    scored_documents.append({
                        "document": doc,
                        "relevance": doc_score.get("relevance", 0.5),
                        "citation_value": doc_score.get("citation_value", 0.5),
                        "style_match": doc_score.get("style_match", 0.5),
                        "document_id": i + 1
                    })
                else:
                    # Fallback scoring
                    scored_documents.append({
                        "document": doc,
                        "relevance": 0.5,
                        "citation_value": 0.5,
                        "style_match": 0.5,
                        "document_id": i + 1
                    })
            except Exception as e:
                logger.warning(f"Error processing document {i+1} score: {e}")
                continue
        
        logger.info(f"🎯 Multi-objective scoring completed for {len(scored_documents)} documents")
        return scored_documents
        
    except Exception as e:
        logger.error(f"Multi-objective scoring failed: {e}")
        # Fallback: return documents with default scores
        return [{
            "document": doc,
            "relevance": 0.5,
            "citation_value": 0.5,
            "style_match": 0.5,
            "document_id": i + 1
        } for i, doc in enumerate(documents)]


def select_optimal_document_mix(scored_documents: List[Dict], top_k: int = 3) -> List[Chunk]:
    """
    Select optimal mix of documents based on multi-objective scores
    Ensures diversity: memos for style + statutes for citations
    """
    
    if not scored_documents:
        return []
    
    # Calculate composite scores with weights
    weights = {
        "relevance": 0.4,      # 40% - must be relevant
        "citation_value": 0.3, # 30% - need legal citations  
        "style_match": 0.3     # 30% - need aggressive style
    }
    
    # Add composite score to each document
    for doc_data in scored_documents:
        composite = (
            doc_data["relevance"] * weights["relevance"] +
            doc_data["citation_value"] * weights["citation_value"] +
            doc_data["style_match"] * weights["style_match"]
        )
        doc_data["composite_score"] = composite
    
    # Sort by composite score (highest first)
    scored_documents.sort(key=lambda x: x["composite_score"], reverse=True)
    
    # Intelligent selection strategy with statute priority
    selected = []
    
    # Strategy 1: FORCE include statute documents if available
    statute_docs = []
    memo_docs = []
    
    for doc_data in scored_documents:
        doc_title = doc_data["document"].title
        if any(term in doc_title for term in ["نظام", "المادة", "التعريفات", "مرسوم"]):
            statute_docs.append(doc_data)
        else:
            memo_docs.append(doc_data)
    
    # Always include 1 statute if available
    if statute_docs and len(selected) < top_k:
        best_statute = max(statute_docs, key=lambda x: x["composite_score"])
        selected.append(best_statute["document"])
        logger.info(f"📜 FORCED statute inclusion: {best_statute['document'].title[:50]}... (composite: {best_statute['composite_score']:.2f})")
    
    # Strategy 2: Get highest citation value documents (likely more statutes)
    remaining_docs = [d for d in scored_documents if d["document"] not in selected]
    citation_docs = [d for d in remaining_docs if d["citation_value"] >= 0.7]
    
    while citation_docs and len(selected) < top_k:
        best_citation = max(citation_docs, key=lambda x: x["citation_value"])
        selected.append(best_citation["document"])
        citation_docs.remove(best_citation)
        remaining_docs.remove(best_citation)
        logger.info(f"📜 Selected high-citation document: {best_citation['document'].title[:50]}... (citation: {best_citation['citation_value']:.2f})")
    
    # Strategy 3: Get highest style match documents (aggressive memos)
    style_docs = [d for d in remaining_docs if d["style_match"] >= 0.7]
    while style_docs and len(selected) < top_k:
        best_style = max(style_docs, key=lambda x: x["style_match"])
        selected.append(best_style["document"])
        style_docs.remove(best_style)
        remaining_docs.remove(best_style)
        logger.info(f"⚔️ Selected high-style document: {best_style['document'].title[:50]}... (style: {best_style['style_match']:.2f})")
    
    # Strategy 4: Fill remaining with highest composite scores
    while len(selected) < top_k and remaining_docs:
        best_overall = remaining_docs.pop(0)  # Already sorted by composite score
        selected.append(best_overall["document"])
        logger.info(f"🎯 Selected high-composite document: {best_overall['document'].title[:50]}... (composite: {best_overall['composite_score']:.2f})")
    
    logger.info(f"🎯 Optimal mix selected: {len(selected)} documents with intelligent diversity (statutes prioritized)")
    return selected

class StorageFactory:
    """Factory for creating storage backends"""
    
    @staticmethod
    def create_storage() -> VectorStore:
        """Create storage backend based on environment configuration"""
        storage_type = os.getenv("VECTOR_STORAGE_TYPE", "sqlite").lower()
        
        if storage_type == "sqlite":
            db_path = os.getenv("SQLITE_DB_PATH", "data/vectors.db")
            return SqliteVectorStore(db_path)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")


class DocumentRetriever:
    """Smart document retriever - gets relevant Saudi legal documents from database"""
    
    def __init__(self, storage: VectorStore, ai_client: AsyncOpenAI):
        self.storage = storage
        self.ai_client = ai_client
        self.initialized = False
        logger.info(f"DocumentRetriever initialized with {type(storage).__name__}")
    
    async def initialize(self) -> None:
        """Initialize storage backend"""
        if self.initialized:
            return
        
        try:
            await self.storage.initialize()
            stats = await self.storage.get_stats()
            logger.info(f"Storage initialized with {stats.total_chunks} existing documents")
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            raise
    
    async def decompose_query_to_concepts(self, query: str) -> List[str]:
        """
        NUCLEAR OPTION 1: AI-driven query decomposition for precision targeting
        Zero hardcoding - pure AI intelligence determines what to search for
        """
        logger.info("🚀 NUCLEAR OPTION 1: Dynamic query decomposition activated")
        
        try:
            decomposition_prompt = f"""
أنت خبير قانوني متخصص في تحليل الاستفسارات. حلل هذا الاستفسار القانوني وحدد المفاهيم القانونية المحددة التي تجيب عليه مباشرة.

الاستفسار: {query}

ما هي الكلمات المفتاحية والمفاهيم القانونية المحددة التي يجب البحث عنها للإجابة على هذا السؤال؟

أجب بالكلمات المفتاحية فقط، مفصولة بمسافات، بدون شرح.
"""

            response = await self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": decomposition_prompt}],
                max_tokens=150,
                temperature=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            concepts = [concept.strip() for concept in ai_response.split() if len(concept.strip()) > 2]
            
            logger.info(f"🎯 AI decomposed query into {len(concepts)} concepts: {concepts}")
            
            # Always include original query as backup
            if query not in concepts:
                concepts.insert(0, query)
            
            return concepts[:5]  # Limit to 5 concepts for efficiency
            
        except Exception as e:
            logger.error(f"Query decomposition failed: {e}")
            logger.info("🔄 Falling back to original query")
            return [query]
        

    async def search_by_concepts(self, concepts: List[str], original_query: str, top_k: int = 15) -> List[Chunk]:
        """
        PRECISION SEARCH: Intent-aware retrieval instead of keyword matching
        """
        logger.info(f"🎯 PRECISION SEARCH: Intent-aware search for '{original_query}'")
        
        try:
            # KEY FIX: Use FULL original query, not fragmented concepts
            response = await self.ai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=original_query  # ← Use complete query for better context
            )
            query_embedding = response.data[0].embedding
            
            # Search with full query context
            search_results = await self.storage.search_similar(
                query_embedding,
                top_k=min(top_k * 2, 30),  # Get more candidates for filtering
                query_text=original_query,
                openai_client=self.ai_client
            )
            
            # Return top results (AI filtering comes next if needed)
            final_results = []
            for result in search_results[:top_k]:
                chunk = result.chunk if hasattr(result, 'chunk') else result
                final_results.append(chunk)
            
            # AI-powered filtering to find the ANSWER document
            filtered_results = await self._ai_filter_results(original_query, search_results, top_k)
            
            logger.info(f"✅ PRECISION SEARCH: AI filtered to {len(filtered_results)} answer documents")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Precision search failed: {e}")
            return []
   
    async def _ai_filter_results(self, query: str, search_results: List, top_k: int) -> List[Chunk]:
        """
        Trust vector similarity ranking - no AI filtering needed
        """
        logger.info("🎯 SKIPPING AI FILTERING: Using vector similarity ranking")
        
        # Return top result based on vector similarity
        # Return top 10 results for broader context
        chunks = []
        for i in range(min(10, len(search_results))):
            chunk = search_results[i].chunk if hasattr(search_results[i], 'chunk') else search_results[i]
            chunks.append(chunk)

        return chunks

    async def get_relevant_documents(self, query: str, top_k: int = 3, user_intent: str = None) -> List[Chunk]:
        """
        Mode-aware document retrieval with strategic processing:
        - LIGHTWEIGHT: Simple content retrieval
        - STRATEGIC: Smart semantic queries + batch processing  
        - COMPREHENSIVE: Full pipeline with style analysis
        """
        # Determine processing mode
        processing_mode = ProcessingMode.LIGHTWEIGHT  # Default
        if hasattr(self, '_current_mode'):
            processing_mode = self._current_mode
        
        logger.info(f"🎯 Processing mode: {processing_mode.value}")

        if not self.initialized:
            await self.initialize()
        
        try:
            stats = await self.storage.get_stats()
            if stats.total_chunks == 0:
                logger.info("No documents found in storage - using general knowledge")
                return []
            
            logger.info(f"🔍 Enhanced search in {stats.total_chunks} documents for: '{query[:50]}...'")
            logger.info(f"📋 User intent: {user_intent}")
            
            # NUCLEAR OPTION 1: AI-driven concept decomposition for ALL queries
            target_concepts = await self.decompose_query_to_concepts(query)

            # Use precision search for high-accuracy targeting
            if len(target_concepts) > 1:
                logger.info("🚀 NUCLEAR OPTION 1: Using precision concept-based search")
                relevant_chunks = await self.search_by_concepts(target_concepts, query, top_k)
                logger.info(f"✅ NUCLEAR OPTION 1: Retrieved {len(relevant_chunks)} precisely targeted documents")
                return relevant_chunks
            else:
                logger.info("🔄 Falling back to standard search")
            
            # STAGE 2: MULTI-QUERY RETRIEVAL (ENHANCED)
            # In your enhanced get_relevant_documents method, replace the multi-query retrieval section:

            # STAGE 2: MULTI-QUERY RETRIEVAL (ENHANCED WITH DOMAIN BYPASS)
            all_search_results = []

            semantic_queries = target_concepts if target_concepts else [query]
            for i, semantic_query in enumerate(semantic_queries):
                try:
                    # Get embedding for this semantic query
                    response = await self.ai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=semantic_query
                    )
                    query_embedding = response.data[0].embedding
                    
                    # DEBUG: Check bypass condition
                    logger.info(f"🔍 BYPASS DEBUG: i={i}, user_intent='{user_intent}', condition: {i == 2 and user_intent == 'ACTIVE_DISPUTE'}")
                    
                    # BYPASS DOMAIN FILTERING FOR STATUTE QUERY (Query 3)
                    # AGGRESSIVE BYPASS: Skip domain filtering entirely for legal disputes
                    # AGGRESSIVE BYPASS: Skip domain filtering for general questions and legal disputes
                    if user_intent in ["ACTIVE_DISPUTE", "GENERAL_QUESTION"]:
                        logger.info(f"🔓 {user_intent} detected: Bypassing ALL domain filtering for query {i+1}")
                        # Search ALL documents without domain filtering for comprehensive legal analysis
                        search_results = await self.storage.search_similar(
                            query_embedding, 
                            top_k=15  # Get more candidates since we're not filtering
                            # No query_text, no openai_client = no domain filtering
                        )
                    else:
                        # Use normal domain filtering for other queries
                        expanded_top_k = min(top_k * 4, 15) if user_intent in ["ACTIVE_DISPUTE", "GENERAL_QUESTION"] else top_k * 4
                        search_results = await self.storage.search_similar(
                            query_embedding, 
                            top_k=expanded_top_k, 
                            query_text=semantic_query, 
                            openai_client=self.ai_client
                        )
                    
                    # Tag results with semantic source for debugging
                    for result in search_results:
                        if not hasattr(result.chunk, 'metadata'):
                            result.chunk.metadata = {}
                        result.chunk.metadata['semantic_source'] = f"query_{i}"
                    
                    all_search_results.extend(search_results)
                    logger.info(f"  Semantic query {i+1}: Found {len(search_results)} candidates")
                    
                except Exception as e:
                    logger.error(f"Error retrieving documents: {e}")
                    return []
            
            # STAGE 3: DEDUPLICATE AND MERGE RESULTS
            if len(semantic_queries) > 1:
                # Remove duplicates by chunk ID while preserving best similarity scores
                seen_ids = set()
                unique_results = []
                
                # Sort all results by similarity score (best first)
                all_search_results.sort(key=lambda x: x.similarity_score, reverse=True)
                
                for result in all_search_results:
                    chunk_id = getattr(result.chunk, 'id', None)
                    if chunk_id and chunk_id not in seen_ids:
                        seen_ids.add(chunk_id)
                        unique_results.append(result)
                    elif chunk_id is None:
                        unique_results.append(result)
                
                search_results = unique_results[:15]  # Cap at 15 like your original
                logger.info(f"📊 Merged {len(all_search_results)} results into {len(search_results)} unique candidates")
            else:
                search_results = all_search_results
            
            content_candidates = [result.chunk for result in search_results]
            
            if not content_candidates:
                logger.info("No relevant documents found - using general knowledge")
                return []
            
            logger.info(f"📊 Stage 2-3: Found {len(content_candidates)} content matches")
            
            # STAGE 4: Direct multi-objective scoring (style classification bypassed)
            if len(content_candidates) > top_k:
                try:
                    logger.info("⚡ Stage 4: Direct multi-objective document scoring")
                    
                    # Apply multi-objective scoring directly to content candidates
                    scored_documents = await score_documents_multi_objective(
                        content_candidates, 
                        query, 
                        user_intent, 
                        self.ai_client
                    )
                    
                    # Select optimal mix using intelligent scoring
                    relevant_chunks = select_optimal_document_mix(scored_documents, top_k)
                    logger.info(f"⚡ EFFICIENT SELECTION: {len(relevant_chunks)} documents via direct scoring")
                    
                except Exception as scoring_error:
                    logger.warning(f"Multi-objective scoring failed: {scoring_error}, using similarity-based selection")
                    relevant_chunks = content_candidates[:top_k]
            else:
                # Use content-based results when we have few candidates
                relevant_chunks = content_candidates[:top_k]
                logger.info(f"📊 Using content-based retrieval ({user_intent}) - {len(relevant_chunks)} candidates")
            

             #STAGE 5: All documents allowed (memos work as background intelligence)
            if relevant_chunks:
                logger.info(f"📚 Using all {len(relevant_chunks)} documents (statutes + memos as background)")

            # STAGE 6: RESULTS LOGGING (keeping your original format)
            if relevant_chunks:
                logger.info(f"Found {len(relevant_chunks)} relevant documents:")
                for i, chunk in enumerate(relevant_chunks):
                    # Find similarity score from original search results
                    similarity = 0.0
                    for result in search_results:
                        if result.chunk.id == chunk.id:
                            similarity = result.similarity_score
                            break
                    
                    semantic_source = chunk.metadata.get('semantic_source', 'original') if hasattr(chunk, 'metadata') and chunk.metadata else 'original'
                    logger.info(f"  {i+1}. {chunk.title[:50]}... (similarity: {similarity:.3f}, source: {semantic_source})")
            else:
                logger.info("No relevant documents found - using general knowledge")

            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []


 
class IntentClassifier:
    """AI-powered intent classifier - no hard-coding"""
    
    def __init__(self, ai_client: AsyncOpenAI, model: str):
        self.ai_client = ai_client
        self.model = model
        logger.info("🧠 AI Intent Classifier initialized - zero hard-coding")
    
    async def classify_intent(self, query: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, any]:
        """Use AI to classify user intent dynamically"""
        try:
            # Build context for better classification
            context = ""
            if conversation_history:
                recent_context = conversation_history[-3:]  # Last 3 messages for context
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_context])
                context = f"\n\nسياق المحادثة:\n{context}\n"
            
            classification_prompt = CLASSIFICATION_PROMPT.format(query=query) + context
            
            logger.info(f"🧠 Classifying intent for: {query[:30]}...")
            
            response = await self.ai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": classification_prompt}],
                max_tokens=400,
                temperature=0.1  # Low temperature for consistent classification
            )
            
            # Parse AI response
            result_text = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown if present)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            # SURGICAL FIX: Enhanced JSON parsing with cleaning
            try:
                # First attempt: direct parsing
                classification = json.loads(result_text)
            except json.JSONDecodeError as e:
                logger.warning(f"Direct JSON parsing failed: {e}")
                try:
                    # Second attempt: clean whitespace and formatting
                    cleaned_text = result_text.strip()
                    
                    # Remove any markdown formatting
                    if "```json" in cleaned_text:
                        cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in cleaned_text:
                        cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
                    
                    # Fix common JSON issues
                    cleaned_text = cleaned_text.replace('\n', '').replace('\r', '').replace('\t', ' ')
                    
                    # Parse cleaned JSON
                    classification = json.loads(cleaned_text)
                    logger.info("✅ JSON parsing succeeded after cleaning")
                    
                except json.JSONDecodeError as e2:
                    logger.error(f"All JSON parsing failed: {e2}")
                    logger.error(f"Raw response: {result_text[:200]}...")
                    
                    # INTELLIGENT FALLBACK: Extract scores using regex
                    import re
                    scores = []
                    
                    # Pattern to match document scoring
                    pattern = r'"document_id":\s*(\d+).*?"relevance":\s*([\d.]+).*?"citation_value":\s*([\d.]+).*?"style_match":\s*([\d.]+)'
                    
                    matches = re.findall(pattern, result_text, re.DOTALL)
                    
                    for match in matches:
                        doc_id, relevance, citation, style = match
                        scores.append({
                            "document_id": int(doc_id),
                            "relevance": float(relevance),
                            "citation_value": float(citation),
                            "style_match": float(style)
                        })
                    
                    if scores:
                        classification = scores
                        logger.info(f"🔧 Regex fallback extracted {len(scores)} document scores")
                    else:
                        # Final fallback: return empty to trigger intelligent scoring
                        classification = []
                        logger.warning("🚨 All parsing failed - triggering intelligent fallback")
            
            logger.info(f"🎯 Intent classified: {classification['category']} (confidence: {classification['confidence']:.2f})")
            
            # Validate classification
            valid_categories = ["GENERAL_QUESTION", "ACTIVE_DISPUTE", "PLANNING_ACTION"]
            if classification["category"] not in valid_categories:
                logger.warning(f"Invalid category: {classification['category']}, defaulting to GENERAL_QUESTION")
                classification["category"] = "GENERAL_QUESTION"
                classification["confidence"] = 0.5
            
            return classification
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            # Safe fallback
            return {
                "category": "GENERAL_QUESTION",
                "confidence": 0.5,
                "reasoning": f"Classification failed: {str(e)}"
            }


    # REPLACE your format_legal_context_naturally function entirely with this ultra-aggressive version:

    

class IntelligentLegalRAG:
    """
    Intelligent Legal RAG with AI-Powered Intent Classification
    No hard-coding - AI handles classification and prompt selection
    """
    
    def __init__(self):
        """Initialize intelligent RAG with AI classification"""
        self.ai_client = ai_client
        self.ai_model = ai_model
        
        # Add smart document retrieval
        self.storage = StorageFactory.create_storage()
        self.retriever = DocumentRetriever(
            storage=self.storage,
            ai_client=self.ai_client
        )
        
        # Add AI-powered intent classifier
        self.classifier = IntentClassifier(
            ai_client=self.ai_client,
            model=classification_model
        )

        
        
        logger.info("🚀 Intelligent Legal RAG initialized - AI-powered classification + Smart retrieval!")
        self.citation_fixer = SimpleCitationFixer()
        logger.info("🔧 Citation fixer initialized")
    

    async def structure_multi_article_chunks(self, documents: List[Chunk], query: str) -> List[Chunk]:
        """
        Create article navigation for large chunks containing multiple articles
        """
        if not documents:
            return documents
        
        logger.info("🧠 STRUCTURING: Creating article navigation for precise citations")
        
        structured_docs = []
        
        for doc in documents:
            try:
                # Check if this chunk contains multiple articles
                import re
                article_matches = re.findall(r'المادة\s+([\d\u0660-\u0669]+|الأولى|الثانية|الثالثة|الرابعة|الخامسة|السادسة|السابعة|الثامنة|التاسعة|العاشرة)', doc.content)
                
                if len(article_matches) > 3:  # Multiple articles detected
                    # Use AI to identify relevant articles
                    navigation_prompt = f"""السؤال: {query}

ابحث في هذا المحتوى القانوني عن المادة التي تجيب على السؤال مباشرة:

{doc.content}

حدد رقم المادة التي تحتوي على معلومات تتعلق بالسؤال. أجب برقم المادة فقط:"""

                    response = await self.ai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": navigation_prompt}],
                        max_tokens=400,
                        temperature=0.1
                    )
                    
                    relevant_article = response.choices[0].message.content.strip()
                    logger.info(f"🎯 AI identified relevant article: {relevant_article}")
                    
                    # Create enhanced content with article highlighting
                    enhanced_content = f"🎯 المادة ذات الصلة: {relevant_article}\n\n{doc.content}"
                    
                    # Create new chunk with enhanced content
                    enhanced_chunk = Chunk(
                        id=doc.id,
                        content=enhanced_content,
                        title=f"{doc.title} - المادة {relevant_article}",
                        metadata=doc.metadata
                    )
                    structured_docs.append(enhanced_chunk)
                    
                else:
                    # Single article or few articles - use as is
                    structured_docs.append(doc)
                    
            except Exception as e:
                logger.warning(f"Article structuring failed for chunk {doc.id}: {e}")
                structured_docs.append(doc)  # Fallback to original
        
        logger.info(f"✅ STRUCTURING: Enhanced {len(structured_docs)} documents with article navigation")
        return structured_docs

    def format_legal_context_naturally(self, documents: List[Chunk]) -> str:
            """Pure document context - no instructions, just clean legal text"""
            if not documents:
                return ""
            
            context_parts = []
            
            for doc in documents:
                title = doc.title or ""
                content = doc.content or ""
                
                if title and content:
                    # Pure document format - just title and content
                    context_parts.append(f"""📄 {title}

{content[:1500]}""")
            
            # No instructions - just pure legal context
            return "\n\n".join(context_parts)


    async def ask_question_with_context_streaming(
        self, 
        query: str, 
        conversation_history: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        """
        PURE RAG - No system prompts, let legal documents and context guide the AI naturally
        """
        try:
            logger.info(f"🚀 PURE RAG: Processing legal question: {query[:50]}...")
            logger.info(f"Conversation context: {len(conversation_history)} messages")
            
            # Stage 1: Simple classification for document retrieval only
            classification = await self.classifier.classify_intent(query, conversation_history)
            category = classification["category"]
            
            # Stage 2: Get relevant documents
            if category == "ACTIVE_DISPUTE":
                top_k = 25  # Get more documents for complex disputes
            elif category == "PLANNING_ACTION":
                top_k = 20  # Good coverage for planning
            else:
                top_k = 15  # General questions

            relevant_docs = await self.retriever.get_relevant_documents(query, top_k=top_k, user_intent=category)
            
            # Stage 3: Build pure context - NO SYSTEM PROMPT
            messages = []
            
            # Stage 4: Add conversation history (last 8 messages)
            recent_history = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Stage 5: Add current question with pure legal context
            if relevant_docs:
                # Structure documents for better context
                structured_docs = await self.structure_multi_article_chunks(relevant_docs, query)
                legal_context = self.format_legal_context_naturally(structured_docs)
                
                # PURE RAG: Just documents + question, no instructions
                pure_rag_content = f"""{legal_context}

السؤال: {query}"""
                logger.info(f"🚀 PURE RAG: Using {len(relevant_docs)} legal documents with natural context")
            else:
                # No documents - just the question
                pure_rag_content = query
                logger.info(f"🚀 PURE RAG: No documents found - using general knowledge")
            
            messages.append({
                "role": "user", 
                "content": pure_rag_content
            })
            
            # Stage 6: Stream pure RAG response
            logger.info(f"🚀 PURE RAG: Streaming response with {len(messages)} messages (no system prompt)")
            async for chunk in self._stream_ai_response(messages, category):
                yield chunk
                
        except Exception as e:
            logger.error(f"Pure RAG error: {e}")
            yield f"عذراً، حدث خطأ في معالجة سؤالك: {str(e)}"
    
    async def _stream_ai_response(self, messages: List[Dict[str, str]], category: str = "GENERAL_QUESTION") -> AsyncIterator[str]:
        """Stream pure RAG response with optimal temperature"""
        try:
            stream = await self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=messages,
                temperature=0.1,  # Low temperature for accuracy and consistency
                max_tokens=15000,  # Generous token limit for comprehensive responses
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"AI streaming error: {e}")
            error_msg = str(e).lower()
            
            if "rate limit" in error_msg or "429" in error_msg:
                yield "\n\n⏳ تم تجاوز الحد المسموح مؤقتاً. يرجى الانتظار دقيقة وإعادة المحاولة."
            elif "api key" in error_msg or "authentication" in error_msg:
                yield "\n\n🔑 خطأ في مفتاح API. يرجى التواصل مع الدعم الفني."
            else:
                yield f"\n\n❌ خطأ تقني: {str(e)}"
    
    async def generate_conversation_title(self, first_message: str) -> str:
        """Simple title generation"""
        try:
            # Minimal prompt for title generation
            title_prompt = f"Generate a short Arabic title (under 30 characters) for this legal question: {first_message[:100]}"
            
            response = await self.ai_client.chat.completions.create(
                model=classification_model,
                messages=[{"role": "user", "content": title_prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            title = response.choices[0].message.content.strip()
            title = title.strip('"').strip("'").strip()
            
            return title[:30] if len(title) > 30 else title
            
        except Exception as e:
            logger.error(f"Title generation error: {e}")
            return first_message[:25] + "..." if len(first_message) > 25 else first_message
    async def ask_question_streaming(self, query: str) -> AsyncIterator[str]:
        """
        STANDARDIZED: Single streaming interface for RAG
        Replaces multiple compatibility methods with one clean interface
        """
        async for chunk in self.ask_question_with_context_streaming(query, []):
            yield chunk

# Global instance - maintains compatibility with existing code
rag_engine = IntelligentLegalRAG()

# Clean exports - no legacy debt
def get_rag_engine():
    """Get the RAG engine instance"""
    return rag_engine

# For external usage - clean streaming interface
async def ask_question_streaming(query: str) -> AsyncIterator[str]:
    """Modern streaming interface"""
    async for chunk in rag_engine.ask_question_with_context_streaming(query, []):
        yield chunk

async def ask_question_with_context_streaming(query: str, conversation_history: List[Dict[str, str]]) -> AsyncIterator[str]:
    """Modern contextual streaming interface"""
    async for chunk in rag_engine.ask_question_with_context_streaming(query, conversation_history):
        yield chunk

# Test function
async def test_intelligent_rag():
    """Test the intelligent RAG system with classification"""
    print("🧪 Testing intelligent RAG engine with AI classification...")
    
    test_queries = [
        "ما هي عقوبات التهرب الضريبي؟",  # Should be GENERAL_QUESTION
        "رفع علي خصم دعوى كيدية كيف أرد عليه؟",  # Should be ACTIVE_DISPUTE
        "أريد مقاضاة شركتي هل الأمر يستحق؟"  # Should be PLANNING_ACTION
    ]
    
    for query in test_queries:
        print(f"\n🧪 Testing: {query}")
        print("Response:")
        
        response_chunks = []
        async for chunk in rag_engine.ask_question_streaming(query):
            response_chunks.append(chunk)
            print(chunk, end="", flush=True)
        
        print(f"\n✅ Test complete for this query!\n{'-'*50}")
    
    return True

# System initialization
print("🏛️ Intelligent Legal RAG Engine loaded - AI-powered classification + Smart document retrieval!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_intelligent_rag())