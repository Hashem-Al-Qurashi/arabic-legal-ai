"""
ENSEMBLE LEGAL AI SYSTEM - Full Implementation
Combines 4 AI models + 3 judges for superior legal responses

Architecture:
1. Query Processing & Context Retrieval (existing RAG)
2. Multi-Model Response Generation (4 models in parallel)  
3. Component Extraction (3 judge models)
4. Consensus Building (voting system)
5. Response Assembly (coherent final response)
6. Quality Verification (automated checks)
7. Data Collection (training data pipeline)
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass
from enum import Enum

from openai import AsyncOpenAI
import httpx
import os
from dotenv import load_dotenv

# Import existing RAG system
from rag_engine import get_rag_engine
from app.storage.vector_store import Chunk

load_dotenv()

logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

@dataclass
class EnsembleConfig:
    """Ensemble system configuration"""
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY")  
    grok_api_key: str = os.getenv("GROK_API_KEY")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    claude_api_key: str = os.getenv("ANTHROPIC_API_KEY")
    
    # Model settings
    temperature: float = 0.7
    max_tokens: int = 2000
    context_chunks: int = 20  # 15-25 chunks as specified
    
    # Cost tracking
    track_costs: bool = True
    max_cost_per_query: float = 0.50  # Safety limit
    
    # Data collection
    save_training_data: bool = True
    training_data_path: str = "data/ensemble_training_data.jsonl"

config = EnsembleConfig()

class ComponentType(Enum):
    """7 components to extract from responses"""
    DIRECT_ANSWER = "direct_answer"
    LEGAL_FOUNDATION = "legal_foundation"  
    ARTICLE_CITATIONS = "article_citations"
    NUMERICAL_EXAMPLES = "numerical_examples"
    STEP_PROCEDURES = "step_procedures"
    EDGE_CASES = "edge_cases"
    PRACTICAL_ADVICE = "practical_advice"

# ==================== MODEL CLIENTS ====================

class ModelClients:
    """Initialize all 4 generator models + 3 judge models"""
    
    def __init__(self):
        # Generator models (4)
        self.chatgpt = AsyncOpenAI(
            api_key=config.openai_api_key,
            http_client=httpx.AsyncClient()
        ) if config.openai_api_key else None
        
        self.deepseek = AsyncOpenAI(
            api_key=config.deepseek_api_key,
            base_url="https://api.deepseek.com/v1",
            http_client=httpx.AsyncClient()
        ) if config.deepseek_api_key else None
        
        # Note: Using OpenAI client format for all - adjust base_url for each provider
        self.grok = AsyncOpenAI(
            api_key=config.grok_api_key,
            base_url="https://api.x.ai/v1",  # Grok API endpoint
            http_client=httpx.AsyncClient()
        ) if config.grok_api_key else None
        
        # Note: Gemini requires different client setup - disabled for now
        # Will add proper Gemini integration in future iteration
        self.gemini = None  # Temporarily disabled - needs proper Google AI SDK
        
        # Judge models (3)
        self.judge_claude = AsyncOpenAI(
            api_key=config.claude_api_key,
            base_url="https://api.anthropic.com/v1",
            http_client=httpx.AsyncClient()
        ) if config.claude_api_key else None
        
        self.judge_gpt = self.chatgpt  # Same as generator ChatGPT
        self.judge_gemini = None  # Disabled until proper Gemini integration
        
        logger.info(f"🤖 Model clients initialized:")
        logger.info(f"  Generators: ChatGPT={bool(self.chatgpt)}, DeepSeek={bool(self.deepseek)}")
        logger.info(f"              Grok={bool(self.grok)}, Gemini={bool(self.gemini)}")
        logger.info(f"  Judges: Claude={bool(self.judge_claude)}, GPT={bool(self.judge_gpt)}, Gemini={bool(self.judge_gemini)}")
    
    def get_available_generators(self) -> Dict[str, AsyncOpenAI]:
        """Get available generator models"""
        generators = {}
        if self.chatgpt:
            generators["chatgpt"] = self.chatgpt
        if self.deepseek:
            generators["deepseek"] = self.deepseek
        if self.grok:
            generators["grok"] = self.grok
        if self.gemini:
            generators["gemini"] = self.gemini
        return generators
    
    def get_available_judges(self) -> Dict[str, AsyncOpenAI]:
        """Get available judge models"""
        judges = {}
        if self.judge_claude:
            judges["claude"] = self.judge_claude
        if self.judge_gpt:
            judges["gpt4o"] = self.judge_gpt
        if self.judge_gemini:
            judges["gemini"] = self.judge_gemini
        return judges

# ==================== LAYER 1: CONTEXT RETRIEVAL ====================

class ContextRetriever:
    """Use existing RAG system to get 15-25 legal chunks"""
    
    def __init__(self):
        self.rag_engine = get_rag_engine()
        logger.info("📚 Context retriever initialized with existing RAG system")
    
    async def get_legal_context(self, query: str) -> Dict[str, Any]:
        """
        Get legal context using existing RAG system
        
        Returns:
            Dict with query, context chunks, and intent classification
        """
        try:
            # Get intent classification (from existing system)
            classification = await self.rag_engine.classifier.classify_intent(query)
            intent = classification.get("category", "GENERAL_QUESTION")
            
            # Get relevant legal chunks (15-25 as specified)
            chunks = await self.rag_engine.retriever.get_relevant_documents(
                query=query,
                top_k=config.context_chunks,
                user_intent=intent
            )
            
            # Format context for models
            formatted_context = self._format_context_for_models(chunks)
            
            logger.info(f"📄 Retrieved {len(chunks)} legal chunks for intent: {intent}")
            
            return {
                "query": query,
                "intent": intent,
                "chunks": chunks,
                "formatted_context": formatted_context,
                "chunk_count": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return {
                "query": query,
                "intent": "GENERAL_QUESTION", 
                "chunks": [],
                "formatted_context": "",
                "chunk_count": 0
            }
    
    def _format_context_for_models(self, chunks: List[Chunk]) -> str:
        """Format legal chunks for model consumption"""
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"""
📄 مرجع قانوني {i}: {chunk.title}
{chunk.content}
""")
        
        return "📚 النصوص القانونية المتاحة:\n" + "\n".join(context_parts)

# ==================== LAYER 2: MULTI-MODEL GENERATION ====================

class MultiModelGenerator:
    """Generate responses from 4 different models in parallel"""
    
    def __init__(self, clients: ModelClients):
        self.clients = clients
        self.generators = clients.get_available_generators()
        
        # Model-specific configurations
        self.model_configs = {
            "chatgpt": {"model": "gpt-4o", "description": "Best overall reasoning"},
            "deepseek": {"model": "deepseek-chat", "description": "Cost-effective, strong on structured tasks"},
            "grok": {"model": "grok-2", "description": "Alternative perspective"},  
            "gemini": {"model": "gemini-1.5-pro", "description": "Comprehensive responses"}
        }
        
        logger.info(f"🎭 Multi-model generator initialized with {len(self.generators)} models")
    
    async def generate_parallel_responses(self, context_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Send IDENTICAL input to all 4 models in parallel
        
        Critical requirement: All models get same context and prompt
        """
        query = context_data["query"]
        formatted_context = context_data["formatted_context"]
        
        # Create identical system prompt for all models
        system_prompt = """أنت خبير قانوني سعودي متخصص. أجب بناءً على النصوص القانونية المقدمة فقط.

🎯 مهمتك:
- قدم استشارة قانونية دقيقة ومفصلة
- استخدم فقط المراجع القانونية المقدمة
- اذكر أرقام المواد والقوانين عند الاستشهاد
- قدم أمثلة رقمية عند الإمكان
- اشرح الإجراءات خطوة بخطوة
- تطرق للحالات الاستثنائية
- قدم نصائح عملية

⚖️ قواعد الاستشهاد:
- أشر للمادة المحددة: "وفقاً للمادة X من نظام..."
- لا تستخدم معلومات من خارج النصوص المقدمة
- إذا لم تجد المعلومة في النصوص، قل ذلك بوضوح"""

        # Create identical user prompt for all models  
        user_prompt = f"""{formatted_context}

❓ السؤال القانوني:
{query}

أجب بناءً على النصوص القانونية المقدمة أعلاه فقط."""

        # Generate responses in parallel
        tasks = []
        for model_name, client in self.generators.items():
            task = self._generate_single_response(
                model_name=model_name,
                client=client,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            tasks.append((model_name, task))
        
        # Wait for all responses
        logger.info(f"🚀 Generating responses from {len(tasks)} models in parallel...")
        start_time = time.time()
        
        responses = {}
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (model_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Model {model_name} failed: {result}")
                responses[model_name] = f"خطأ في النموذج: {str(result)}"
            else:
                responses[model_name] = result
                logger.info(f"✅ {model_name}: {len(result)} characters")
        
        generation_time = time.time() - start_time
        logger.info(f"⏱️ All models completed in {generation_time:.2f} seconds")
        
        return responses
    
    async def _generate_single_response(self, model_name: str, client: AsyncOpenAI, 
                                      system_prompt: str, user_prompt: str) -> str:
        """Generate response from a single model"""
        try:
            model_config = self.model_configs.get(model_name, {})
            model_id = model_config.get("model", "gpt-4o")  # Fallback
            
            response = await client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.debug(f"📝 {model_name} generated {len(content)} characters")
            
            return content
            
        except Exception as e:
            logger.error(f"Model {model_name} generation failed: {e}")
            raise

# ==================== LAYER 3: COMPONENT EXTRACTION JUDGES ====================

@dataclass
class ComponentEvaluation:
    """Single component evaluation by one judge"""
    component: ComponentType
    evaluations: Dict[str, Dict[str, Any]]  # model_name -> {score, reasoning}
    winner: str  # winning model name
    extracted_text: str  # exact text from winning response
    winner_score: float
    reasoning: str

class ComponentJudge:
    """Single judge that evaluates all 7 components"""
    
    def __init__(self, judge_name: str, client: AsyncOpenAI):
        self.judge_name = judge_name
        self.client = client
        self.components = list(ComponentType)
        
        logger.info(f"⚖️ Judge {judge_name} initialized for {len(self.components)} components")
    
    async def evaluate_all_components(self, query: str, responses: Dict[str, str]) -> List[ComponentEvaluation]:
        """Evaluate all 7 components across all 4 responses"""
        
        logger.info(f"⚖️ Judge {self.judge_name} evaluating {len(self.components)} components...")
        
        evaluations = []
        for component in self.components:
            try:
                evaluation = await self._evaluate_single_component(component, query, responses)
                evaluations.append(evaluation)
                logger.debug(f"  ✅ {component.value}: Winner = {evaluation.winner} (score: {evaluation.winner_score:.1f})")
            except Exception as e:
                logger.error(f"Component {component.value} evaluation failed: {e}")
                # Create fallback evaluation
                fallback = ComponentEvaluation(
                    component=component,
                    evaluations={},
                    winner="chatgpt",  # Safe fallback
                    extracted_text="[تعذر استخراج هذا المكون]",
                    winner_score=5.0,
                    reasoning=f"خطأ في التقييم: {str(e)}"
                )
                evaluations.append(fallback)
        
        logger.info(f"⚖️ Judge {self.judge_name} completed all component evaluations")
        return evaluations
    
    async def _evaluate_single_component(self, component: ComponentType, query: str, 
                                       responses: Dict[str, str]) -> ComponentEvaluation:
        """Evaluate a single component across all responses"""
        
        # Create component-specific evaluation prompt
        evaluation_prompt = self._create_component_prompt(component, query, responses)
        
        # Get judge's evaluation
        response = await self.client.chat.completions.create(
            model="gpt-4o",  # Use consistent model for judges
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.1,  # Low temperature for consistent evaluation
            max_tokens=1500
        )
        
        evaluation_text = response.choices[0].message.content
        
        # Parse evaluation result
        return self._parse_evaluation_result(component, evaluation_text, responses)
    
    def _create_component_prompt(self, component: ComponentType, query: str, 
                               responses: Dict[str, str]) -> str:
        """Create evaluation prompt for specific component"""
        
        component_descriptions = {
            ComponentType.DIRECT_ANSWER: {
                "name": "الإجابة المباشرة",
                "description": "الجواب الواضح والمباشر على السؤال في 2-3 جمل",
                "example": "مدة الإجازة السنوية 21 يوماً، تزيد إلى 30 بعد 5 سنوات خدمة"
            },
            ComponentType.LEGAL_FOUNDATION: {
                "name": "الأساس القانوني", 
                "description": "شرح القوانين والمواد المطبقة والإطار القانوني",
                "example": "وفقاً للمادة 84 من نظام العمل السعودي..."
            },
            ComponentType.ARTICLE_CITATIONS: {
                "name": "الاستشهادات القانونية",
                "description": "جميع أرقام المواد والقوانين المذكورة",
                "example": "المواد 84، 85، 109 من نظام العمل"
            },
            ComponentType.NUMERICAL_EXAMPLES: {
                "name": "الأمثلة الرقمية",
                "description": "حسابات بأرقام حقيقية وصيغ رياضية",
                "example": "إذا كان الراتب 6000 ريال: المكافأة = 0.5 × 6000 × 5 = 15,000 ريال"
            },
            ComponentType.STEP_PROCEDURES: {
                "name": "الإجراءات المتسلسلة",
                "description": "خطوات واضحة قابلة للتنفيذ",
                "example": "الخطوة 1: تقديم شكوى لمكتب العمل..."
            },
            ComponentType.EDGE_CASES: {
                "name": "الحالات الاستثنائية",
                "description": "ظروف خاصة، تعقيدات، استثناءات",
                "example": "في حالة الاستقالة للزواج، تستحق المكافأة كاملة"
            },
            ComponentType.PRACTICAL_ADVICE: {
                "name": "النصائح العملية", 
                "description": "توصيات عملية، تحذيرات، نصائح واقعية",
                "example": "يُفضل الاحتفاظ بنسخ من جميع المراسلات"
            }
        }
        
        comp_info = component_descriptions[component]
        
        # Build responses section
        responses_text = ""
        for model_name, response in responses.items():
            responses_text += f"\n--- استجابة {model_name.upper()} ---\n{response}\n"
        
        prompt = f"""أنت خبير تقييم قانوني. قيم جودة مكون محدد في 4 استجابات مختلفة.

السؤال الأصلي: {query}

المكون المطلوب تقييمه: {comp_info['name']}
الوصف: {comp_info['description']}
مثال: {comp_info['example']}

الاستجابات الأربعة:{responses_text}

📋 مهمتك:
1. قيم جودة "{comp_info['name']}" في كل استجابة (درجة من 0-10)
2. اختر الاستجابة الأفضل
3. استخرج النص الدقيق للمكون من الاستجابة الفائزة
4. اشرح سبب اختيارك

📊 صيغة الإجابة (JSON فقط):
{{
  "evaluations": {{
    "chatgpt": {{"score": 8.5, "reasoning": "سبب التقييم"}},
    "deepseek": {{"score": 6.0, "reasoning": "سبب التقييم"}},
    "grok": {{"score": 9.0, "reasoning": "سبب التقييم"}}, 
    "gemini": {{"score": 7.5, "reasoning": "سبب التقييم"}}
  }},
  "winner": "grok",
  "extracted_text": "النص الدقيق للمكون من الاستجابة الفائزة",
  "reasoning": "سبب اختيار هذه الاستجابة كأفضل"
}}

أجب بـ JSON فقط، لا نص إضافي."""

        return prompt
    
    def _parse_evaluation_result(self, component: ComponentType, evaluation_text: str, 
                               responses: Dict[str, str]) -> ComponentEvaluation:
        """Parse judge's evaluation result"""
        
        try:
            # Clean and parse JSON
            clean_text = evaluation_text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(clean_text)
            
            evaluations = result.get("evaluations", {})
            winner = result.get("winner", "chatgpt")
            extracted_text = result.get("extracted_text", "[لم يتم العثور على النص]")
            reasoning = result.get("reasoning", "لم يتم تقديم تبرير")
            
            # Get winner score
            winner_score = 5.0  # Default
            if winner in evaluations:
                winner_score = float(evaluations[winner].get("score", 5.0))
            
            return ComponentEvaluation(
                component=component,
                evaluations=evaluations,
                winner=winner,
                extracted_text=extracted_text,
                winner_score=winner_score,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Failed to parse evaluation for {component.value}: {e}")
            logger.error(f"Raw evaluation text: {evaluation_text[:300]}...")
            
            # Fallback evaluation
            return ComponentEvaluation(
                component=component,
                evaluations={},
                winner="chatgpt",
                extracted_text="[خطأ في تحليل النتيجة]",
                winner_score=5.0,
                reasoning=f"خطأ في تحليل النتيجة: {str(e)}"
            )

class ThreeJudgeSystem:
    """Coordinate 3 judges to evaluate all components"""
    
    def __init__(self, clients: ModelClients):
        self.judges = {}
        available_judges = clients.get_available_judges()
        
        for judge_name, client in available_judges.items():
            self.judges[judge_name] = ComponentJudge(judge_name, client)
        
        logger.info(f"⚖️ Three-judge system initialized with {len(self.judges)} judges: {list(self.judges.keys())}")
    
    async def evaluate_responses(self, query: str, responses: Dict[str, str]) -> Dict[str, List[ComponentEvaluation]]:
        """All 3 judges evaluate all responses"""
        
        logger.info("⚖️ Starting 3-judge evaluation process...")
        start_time = time.time()
        
        # Run all judges in parallel
        judge_tasks = []
        for judge_name, judge in self.judges.items():
            task = judge.evaluate_all_components(query, responses)
            judge_tasks.append((judge_name, task))
        
        # Wait for all judges
        judge_results = {}
        results = await asyncio.gather(*[task for _, task in judge_tasks], return_exceptions=True)
        
        for (judge_name, _), result in zip(judge_tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Judge {judge_name} failed: {result}")
                judge_results[judge_name] = []
            else:
                judge_results[judge_name] = result
                logger.info(f"⚖️ Judge {judge_name}: {len(result)} component evaluations")
        
        evaluation_time = time.time() - start_time
        logger.info(f"⚖️ All judges completed in {evaluation_time:.2f} seconds")
        
        return judge_results

# ==================== LAYER 4: CONSENSUS BUILDING ====================

@dataclass  
class ConsensusResult:
    """Final consensus for one component"""
    component: ComponentType
    final_text: str
    winning_model: str
    consensus_type: str  # "strong_consensus", "highest_score", "missing"
    judge_votes: List[str]  # Which models each judge chose
    final_score: float

class ConsensusBuilder:
    """Build consensus from 3 judge evaluations using voting rules"""
    
    def __init__(self):
        logger.info("🗳️ Consensus builder initialized")
    
    def build_consensus(self, judge_evaluations: Dict[str, List[ComponentEvaluation]]) -> List[ConsensusResult]:
        """Apply voting rules to select best components"""
        
        if not judge_evaluations:
            logger.warning("No judge evaluations provided")
            return []
        
        # Get all components to process
        components = list(ComponentType)
        consensus_results = []
        
        for component in components:
            try:
                consensus = self._build_component_consensus(component, judge_evaluations)
                consensus_results.append(consensus)
                
                logger.info(f"🗳️ {component.value}: {consensus.consensus_type} -> {consensus.winning_model} (score: {consensus.final_score:.1f})")
                
            except Exception as e:
                logger.error(f"Consensus building failed for {component.value}: {e}")
                # Create fallback consensus
                fallback = ConsensusResult(
                    component=component,
                    final_text="[تعذر بناء الإجماع لهذا المكون]",
                    winning_model="chatgpt",
                    consensus_type="error",
                    judge_votes=[],
                    final_score=0.0
                )
                consensus_results.append(fallback)
        
        logger.info(f"🗳️ Consensus building completed for {len(consensus_results)} components")
        return consensus_results
    
    def _build_component_consensus(self, component: ComponentType, 
                                 judge_evaluations: Dict[str, List[ComponentEvaluation]]) -> ConsensusResult:
        """Build consensus for a single component"""
        
        # Extract evaluations for this component from all judges
        component_evaluations = []
        for judge_name, evaluations in judge_evaluations.items():
            for eval_item in evaluations:
                if eval_item.component == component:
                    component_evaluations.append((judge_name, eval_item))
                    break
        
        if not component_evaluations:
            # Component missing from all judges
            return ConsensusResult(
                component=component,
                final_text="",
                winning_model="none",
                consensus_type="missing",
                judge_votes=[],
                final_score=0.0
            )
        
        # Extract votes and scores
        judge_votes = [eval_item.winner for _, eval_item in component_evaluations]
        judge_scores = [eval_item.winner_score for _, eval_item in component_evaluations]
        
        # Apply voting rules
        
        # Rule 1: Strong Consensus (2+ judges agree)
        vote_counts = {}
        for vote in judge_votes:
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        # Find if any model has 2+ votes
        consensus_winner = None
        for model, count in vote_counts.items():
            if count >= 2:
                consensus_winner = model
                break
        
        if consensus_winner:
            # Strong consensus found
            winning_evaluation = None
            for _, eval_item in component_evaluations:
                if eval_item.winner == consensus_winner:
                    winning_evaluation = eval_item
                    break
            
            return ConsensusResult(
                component=component,
                final_text=winning_evaluation.extracted_text if winning_evaluation else "",
                winning_model=consensus_winner,
                consensus_type="strong_consensus",
                judge_votes=judge_votes,
                final_score=winning_evaluation.winner_score if winning_evaluation else 0.0
            )
        
        # Rule 2: No Consensus - Use Highest Individual Score
        best_score = max(judge_scores)
        best_judge_idx = judge_scores.index(best_score)
        best_winner = judge_votes[best_judge_idx]
        best_evaluation = component_evaluations[best_judge_idx][1]
        
        return ConsensusResult(
            component=component,
            final_text=best_evaluation.extracted_text,
            winning_model=best_winner,
            consensus_type="highest_score",
            judge_votes=judge_votes,
            final_score=best_score
        )
    
    def _handle_special_citations(self, judge_evaluations: Dict[str, List[ComponentEvaluation]]) -> str:
        """Rule 4: Special handling for citations - take union of all"""
        
        all_citations = set()
        
        for judge_name, evaluations in judge_evaluations.items():
            for eval_item in evaluations:
                if eval_item.component == ComponentType.ARTICLE_CITATIONS:
                    # Extract article numbers from the text
                    citations = self._extract_article_numbers(eval_item.extracted_text)
                    all_citations.update(citations)
        
        if all_citations:
            sorted_citations = sorted(all_citations, key=lambda x: int(x) if x.isdigit() else 999)
            return f"المواد: {', '.join(sorted_citations)}"
        
        return ""
    
    def _extract_article_numbers(self, text: str) -> List[str]:
        """Extract article numbers from text"""
        import re
        
        # Pattern to match Arabic and English article numbers
        patterns = [
            r'المادة\s+(\d+)',
            r'مادة\s+(\d+)', 
            r'Article\s+(\d+)',
            r'(?:^|[^\d])(\d{1,3})(?:[^\d]|$)'  # Standalone numbers 1-999
        ]
        
        found_articles = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            found_articles.extend(matches)
        
        # Remove duplicates and return
        return list(set(found_articles))

# ==================== LAYER 5: RESPONSE ASSEMBLY ====================

class ResponseAssembler:
    """Assemble final response from consensus components"""
    
    def __init__(self, clients: ModelClients):
        # Use ChatGPT for assembly (reliable for text editing)
        self.assembler_client = clients.chatgpt
        logger.info("🔧 Response assembler initialized")
    
    async def assemble_final_response(self, consensus_results: List[ConsensusResult], 
                                    query: str, use_smooth_transitions: bool = True) -> str:
        """Assemble final response from winning components"""
        
        if use_smooth_transitions:
            return await self._assemble_with_transitions(consensus_results, query)
        else:
            return self._assemble_simple_concatenation(consensus_results)
    
    def _assemble_simple_concatenation(self, consensus_results: List[ConsensusResult]) -> str:
        """Option A: Simple concatenation with section breaks"""
        
        # Assembly order as specified
        order = [
            ComponentType.DIRECT_ANSWER,
            ComponentType.LEGAL_FOUNDATION, 
            ComponentType.ARTICLE_CITATIONS,
            ComponentType.NUMERICAL_EXAMPLES,
            ComponentType.STEP_PROCEDURES,
            ComponentType.EDGE_CASES,
            ComponentType.PRACTICAL_ADVICE
        ]
        
        sections = []
        
        for component_type in order:
            # Find consensus result for this component
            component_result = None
            for result in consensus_results:
                if result.component == component_type:
                    component_result = result
                    break
            
            if component_result and component_result.final_text.strip():
                # Add section header
                section_headers = {
                    ComponentType.DIRECT_ANSWER: "## الإجابة المباشرة",
                    ComponentType.LEGAL_FOUNDATION: "## الأساس القانوني",
                    ComponentType.ARTICLE_CITATIONS: "## الاستشهادات القانونية",
                    ComponentType.NUMERICAL_EXAMPLES: "## الأمثلة الرقمية", 
                    ComponentType.STEP_PROCEDURES: "## الإجراءات المطلوبة",
                    ComponentType.EDGE_CASES: "## الحالات الاستثنائية",
                    ComponentType.PRACTICAL_ADVICE: "## النصائح العملية"
                }
                
                header = section_headers.get(component_type, f"## {component_type.value}")
                sections.append(f"{header}\n\n{component_result.final_text}")
        
        final_response = "\n\n---\n\n".join(sections)
        
        if not final_response.strip():
            final_response = "عذراً، لم أتمكن من تجميع استجابة مناسبة من النماذج المتاحة."
        
        logger.info(f"🔧 Simple assembly completed: {len(sections)} sections, {len(final_response)} characters")
        return final_response
    
    async def _assemble_with_transitions(self, consensus_results: List[ConsensusResult], query: str) -> str:
        """Option B: Smooth transitions with AI assembly"""
        
        if not self.assembler_client:
            logger.warning("No assembler client available, falling back to simple concatenation")
            return self._assemble_simple_concatenation(consensus_results)
        
        try:
            # Collect all components
            component_texts = {}
            
            for result in consensus_results:
                if result.final_text.strip():
                    component_texts[result.component.value] = result.final_text
            
            if not component_texts:
                return "عذراً، لم أتمكن من استخراج أي مكونات مناسبة من النماذج."
            
            # Create assembly prompt
            assembly_prompt = self._create_assembly_prompt(component_texts, query)
            
            # Generate assembled response
            response = await self.assembler_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": assembly_prompt}],
                temperature=0.3,  # Low temperature for consistent assembly
                max_tokens=3000
            )
            
            assembled_response = response.choices[0].message.content.strip()
            
            logger.info(f"🔧 Smooth assembly completed: {len(component_texts)} components, {len(assembled_response)} characters")
            
            return assembled_response
            
        except Exception as e:
            logger.error(f"Smooth assembly failed: {e}, falling back to simple concatenation")
            return self._assemble_simple_concatenation(consensus_results)
    
    def _create_assembly_prompt(self, component_texts: Dict[str, str], query: str) -> str:
        """Create prompt for smooth assembly"""
        
        components_section = ""
        for component_name, text in component_texts.items():
            components_section += f"\n[{component_name}]\n{text}\n"
        
        return f"""أنت محرر قانوني متخصص في تجميع الاستجابات القانونية.

السؤال الأصلي: {query}

المكونات المستخرجة من أفضل النماذج:{components_section}

🎯 مهمتك:
- اجمع هذه المكونات في استجابة واحدة متماسكة
- أضف جمل ربط بسيطة بين الأقسام حسب الحاجة
- احتفظ بالنص المستخرج بالضبط كما هو (لا تعدل المحتوى)
- رتب المكونات منطقياً (الإجابة المباشرة أولاً، النصائح أخيراً)
- تأكد من التدفق الطبيعي للنص

⚠️ قواعد حاسمة:
- لا تغير أو تعيد صياغة النصوص المستخرجة
- أضف فقط جمل ربط قصيرة عند الضرورة
- لا تضف معلومات قانونية جديدة
- الهدف: تدفق طبيعي للمكونات الموجودة

أجب بالاستجابة النهائية المجمعة فقط."""

# ==================== LAYER 6: QUALITY VERIFICATION ====================

@dataclass
class QualityReport:
    """Quality verification report"""
    passed: bool
    length_check: bool
    citation_check: bool  
    completeness_check: bool
    coherence_check: bool
    duplication_check: bool
    issues: List[str]
    metrics: Dict[str, Any]

class QualityVerifier:
    """Verify quality of assembled response before saving"""
    
    def __init__(self):
        logger.info("🔍 Quality verifier initialized")
    
    def verify_quality(self, final_response: str, original_responses: Dict[str, str],
                      consensus_results: List[ConsensusResult], context_chunks: List[Chunk]) -> QualityReport:
        """Run all quality checks"""
        
        issues = []
        
        # Check 1: Length Check
        length_check = self._check_length(final_response, original_responses)
        if not length_check:
            issues.append("Final response is shorter than longest individual response")
        
        # Check 2: Citation Verification  
        citation_check = self._check_citations(final_response, context_chunks)
        if not citation_check:
            issues.append("Some citations not found in provided context")
        
        # Check 3: Completeness Check
        completeness_check = self._check_completeness(final_response, consensus_results)
        if not completeness_check:
            issues.append("Some extracted components missing from final response")
        
        # Check 4: Coherence Check
        coherence_check = self._check_coherence(final_response)
        if not coherence_check:
            issues.append("Response appears disjointed or incoherent")
        
        # Check 5: No Duplication
        duplication_check = self._check_duplication(final_response)
        if not duplication_check:
            issues.append("Response contains repeated information")
        
        passed = all([length_check, citation_check, completeness_check, coherence_check, duplication_check])
        
        # Calculate metrics
        metrics = {
            "final_length": len(final_response),
            "max_original_length": max(len(resp) for resp in original_responses.values()) if original_responses else 0,
            "component_count": len([r for r in consensus_results if r.final_text.strip()]),
            "citation_count": self._count_citations(final_response),
            "coherence_score": self._calculate_coherence_score(final_response)
        }
        
        report = QualityReport(
            passed=passed,
            length_check=length_check,
            citation_check=citation_check,
            completeness_check=completeness_check, 
            coherence_check=coherence_check,
            duplication_check=duplication_check,
            issues=issues,
            metrics=metrics
        )
        
        if passed:
            logger.info("✅ Quality verification passed")
        else:
            logger.warning(f"⚠️ Quality issues found: {', '.join(issues)}")
        
        return report
    
    def _check_length(self, final_response: str, original_responses: Dict[str, str]) -> bool:
        """Check if final response is comprehensive enough"""
        if not original_responses:
            return True
        
        final_length = len(final_response)
        max_original = max(len(resp) for resp in original_responses.values())
        
        # Final should be at least 80% of longest original (allowing for some compression)
        return final_length >= max_original * 0.8
    
    def _check_citations(self, final_response: str, context_chunks: List[Chunk]) -> bool:
        """Check if all cited articles exist in provided context"""
        import re
        
        # Extract article numbers from final response
        cited_articles = set()
        patterns = [r'المادة\s+(\d+)', r'مادة\s+(\d+)']
        
        for pattern in patterns:
            matches = re.findall(pattern, final_response)
            cited_articles.update(matches)
        
        if not cited_articles:
            return True  # No citations to verify
        
        # Extract available articles from context
        available_articles = set()
        for chunk in context_chunks:
            for pattern in patterns:
                matches = re.findall(pattern, chunk.content)
                available_articles.update(matches)
        
        # Check if all cited articles are available
        missing_articles = cited_articles - available_articles
        
        if missing_articles:
            logger.warning(f"Missing article citations: {missing_articles}")
            return False
        
        return True
    
    def _check_completeness(self, final_response: str, consensus_results: List[ConsensusResult]) -> bool:
        """Check if extracted components made it to final response"""
        
        missing_components = 0
        total_components = 0
        
        for result in consensus_results:
            if result.final_text.strip():
                total_components += 1
                
                # Check if component text appears in final response (allowing for minor edits)
                component_words = set(result.final_text.split()[:10])  # First 10 words
                final_words = set(final_response.split())
                
                overlap = len(component_words.intersection(final_words))
                if overlap < len(component_words) * 0.5:  # At least 50% word overlap
                    missing_components += 1
        
        if total_components == 0:
            return True
        
        completion_rate = (total_components - missing_components) / total_components
        return completion_rate >= 0.8  # At least 80% of components present
    
    def _check_coherence(self, final_response: str) -> bool:
        """Basic coherence check"""
        
        # Check for signs of poor assembly
        incoherence_indicators = [
            "## ##",  # Double headers
            "\n\n\n\n\n",  # Too many line breaks
            "[تعذر",  # Error messages
            "خطأ في",  # Error indicators
        ]
        
        for indicator in incoherence_indicators:
            if indicator in final_response:
                return False
        
        # Check minimum length for coherent response
        if len(final_response) < 100:
            return False
        
        return True
    
    def _check_duplication(self, final_response: str) -> bool:
        """Check for repeated information"""
        
        sentences = final_response.split('.')
        sentence_counts = {}
        
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 20:  # Only check meaningful sentences
                # Simple similarity check
                for existing in sentence_counts:
                    if len(set(clean_sentence.split()).intersection(set(existing.split()))) > len(clean_sentence.split()) * 0.7:
                        return False  # High similarity = likely duplication
                
                sentence_counts[clean_sentence] = sentence_counts.get(clean_sentence, 0) + 1
        
        # Check for exact duplicates
        for count in sentence_counts.values():
            if count > 1:
                return False
        
        return True
    
    def _count_citations(self, text: str) -> int:
        """Count legal citations in text"""
        import re
        patterns = [r'المادة\s+\d+', r'مادة\s+\d+', r'القانون', r'النظام']
        
        total_citations = 0
        for pattern in patterns:
            matches = re.findall(pattern, text)
            total_citations += len(matches)
        
        return total_citations
    
    def _calculate_coherence_score(self, text: str) -> float:
        """Calculate basic coherence score"""
        
        # Simple heuristics for coherence
        score = 1.0
        
        # Penalty for too short
        if len(text) < 200:
            score -= 0.3
        
        # Penalty for too many line breaks
        line_break_ratio = text.count('\n\n') / max(len(text) / 100, 1)
        if line_break_ratio > 5:
            score -= 0.2
        
        # Bonus for proper Arabic structure
        if 'أولاً' in text and 'ثانياً' in text:
            score += 0.1
        
        if any(phrase in text for phrase in ['وفقاً ل', 'استناداً إلى', 'بناءً على']):
            score += 0.1
        
        return max(0.0, min(1.0, score))

# ==================== LAYER 7: DATA COLLECTION ====================

@dataclass
class EnsembleTrainingData:
    """Training data format for fine-tuning"""
    query: str
    retrieved_context: List[str]
    generator_responses: Dict[str, str]
    judge_evaluations: Dict[str, List[ComponentEvaluation]]
    component_winners: Dict[str, str]
    final_response: str
    quality_scores: Dict[str, Any]
    timestamp: str
    processing_time_ms: int
    cost_estimate: float

class DataCollector:
    """Collect ensemble data for fine-tuning"""
    
    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.data_file = config.training_data_path
        logger.info(f"💾 Data collector initialized: {self.data_file}")
    
    def collect_training_example(self, query: str, context_data: Dict[str, Any],
                               responses: Dict[str, str], judge_evaluations: Dict[str, List[ComponentEvaluation]],
                               consensus_results: List[ConsensusResult], final_response: str,
                               quality_report: QualityReport, processing_time_ms: int,
                               cost_estimate: float) -> EnsembleTrainingData:
        """Create training data example"""
        
        # Convert context chunks to strings
        context_strings = []
        if "chunks" in context_data:
            for chunk in context_data["chunks"]:
                context_strings.append(f"{chunk.title}: {chunk.content}")
        
        # Extract component winners
        component_winners = {}
        for result in consensus_results:
            component_winners[result.component.value] = result.winning_model
        
        training_example = EnsembleTrainingData(
            query=query,
            retrieved_context=context_strings,
            generator_responses=responses,
            judge_evaluations=judge_evaluations,
            component_winners=component_winners,
            final_response=final_response,
            quality_scores=quality_report.metrics,
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time_ms,
            cost_estimate=cost_estimate
        )
        
        if self.config.save_training_data:
            self._save_training_example(training_example)
        
        return training_example
    
    def _save_training_example(self, example: EnsembleTrainingData):
        """Save training example to JSONL file"""
        
        try:
            # Convert to dict for JSON serialization
            data_dict = {
                "query": example.query,
                "retrieved_context": example.retrieved_context,
                "generator_responses": example.generator_responses,
                "judge_evaluations": self._serialize_judge_evaluations(example.judge_evaluations),
                "component_winners": example.component_winners,
                "final_response": example.final_response,
                "quality_scores": example.quality_scores,
                "timestamp": example.timestamp,
                "processing_time_ms": example.processing_time_ms,
                "cost_estimate": example.cost_estimate
            }
            
            # Append to JSONL file
            import os
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data_dict, ensure_ascii=False) + '\n')
            
            logger.debug(f"💾 Training example saved to {self.data_file}")
            
        except Exception as e:
            logger.error(f"Failed to save training example: {e}")
    
    def _serialize_judge_evaluations(self, judge_evaluations: Dict[str, List[ComponentEvaluation]]) -> Dict:
        """Convert ComponentEvaluation objects to dict for JSON"""
        
        serialized = {}
        for judge_name, evaluations in judge_evaluations.items():
            serialized[judge_name] = []
            for eval_item in evaluations:
                serialized[judge_name].append({
                    "component": eval_item.component.value,
                    "evaluations": eval_item.evaluations,
                    "winner": eval_item.winner,
                    "extracted_text": eval_item.extracted_text,
                    "winner_score": eval_item.winner_score,
                    "reasoning": eval_item.reasoning
                })
        
        return serialized
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get statistics about collected training data"""
        
        if not os.path.exists(self.data_file):
            return {"total_examples": 0}
        
        try:
            line_count = 0
            total_cost = 0.0
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        line_count += 1
                        try:
                            data = json.loads(line)
                            total_cost += data.get("cost_estimate", 0.0)
                        except:
                            continue
            
            return {
                "total_examples": line_count,
                "total_cost_estimate": total_cost,
                "data_file": self.data_file
            }
            
        except Exception as e:
            logger.error(f"Failed to get training stats: {e}")
            return {"total_examples": 0, "error": str(e)}

# ==================== MAIN ENSEMBLE ENGINE ====================

class EnsembleLegalAI:
    """
    Main Ensemble Legal AI System
    Orchestrates all 7 layers of the ensemble pipeline
    """
    
    def __init__(self):
        """Initialize all ensemble components"""
        
        logger.info("🚀 Initializing Ensemble Legal AI System...")
        
        # Initialize all components
        self.config = config
        self.clients = ModelClients()
        
        # Layer 1: Context Retrieval (existing RAG)
        self.context_retriever = ContextRetriever()
        
        # Layer 2: Multi-Model Generation  
        self.multi_generator = MultiModelGenerator(self.clients)
        
        # Layer 3: 3-Judge System
        self.judge_system = ThreeJudgeSystem(self.clients)
        
        # Layer 4: Consensus Building
        self.consensus_builder = ConsensusBuilder()
        
        # Layer 5: Response Assembly
        self.assembler = ResponseAssembler(self.clients)
        
        # Layer 6: Quality Verification
        self.quality_verifier = QualityVerifier()
        
        # Layer 7: Data Collection
        self.data_collector = DataCollector(config)
        
        logger.info("✅ Ensemble Legal AI System initialized successfully")
        logger.info(f"🤖 Available generators: {len(self.clients.get_available_generators())}")
        logger.info(f"⚖️ Available judges: {len(self.clients.get_available_judges())}")
    
    async def process_legal_query(self, query: str) -> Dict[str, Any]:
        """
        Main ensemble processing pipeline
        
        Returns complete ensemble result with all intermediate data
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Processing ensemble query [{request_id}]: {query[:50]}...")
        
        try:
            # Layer 1: Get legal context from existing RAG
            logger.info("📚 Layer 1: Context Retrieval")
            context_data = await self.context_retriever.get_legal_context(query)
            
            if not context_data["chunks"]:
                logger.warning("No legal context found, proceeding with general knowledge")
            
            # Layer 2: Generate responses from 4 models in parallel
            logger.info("🎭 Layer 2: Multi-Model Generation")
            responses = await self.multi_generator.generate_parallel_responses(context_data)
            
            if not responses:
                raise Exception("No responses generated from any model")
            
            # Layer 3: 3-Judge Component Extraction
            logger.info("⚖️ Layer 3: Component Extraction (3 Judges)")
            judge_evaluations = await self.judge_system.evaluate_responses(query, responses)
            
            # Layer 4: Consensus Building
            logger.info("🗳️ Layer 4: Consensus Building")
            consensus_results = self.consensus_builder.build_consensus(judge_evaluations)
            
            # Layer 5: Response Assembly
            logger.info("🔧 Layer 5: Response Assembly")
            final_response = await self.assembler.assemble_final_response(consensus_results, query)
            
            # Layer 6: Quality Verification
            logger.info("🔍 Layer 6: Quality Verification")
            quality_report = self.quality_verifier.verify_quality(
                final_response, responses, consensus_results, context_data["chunks"]
            )
            
            # Calculate processing metrics
            processing_time_ms = int((time.time() - start_time) * 1000)
            cost_estimate = self._estimate_cost(responses, judge_evaluations)
            
            # Layer 7: Data Collection
            logger.info("💾 Layer 7: Data Collection")
            training_data = self.data_collector.collect_training_example(
                query=query,
                context_data=context_data,
                responses=responses,
                judge_evaluations=judge_evaluations,
                consensus_results=consensus_results,
                final_response=final_response,
                quality_report=quality_report,
                processing_time_ms=processing_time_ms,
                cost_estimate=cost_estimate
            )
            
            # Compile final result
            result = {
                "request_id": request_id,
                "query": query,
                "final_response": final_response,
                "processing_time_ms": processing_time_ms,
                "cost_estimate": cost_estimate,
                "quality_report": {
                    "passed": quality_report.passed,
                    "issues": quality_report.issues,
                    "metrics": quality_report.metrics
                },
                "ensemble_data": {
                    "context_chunks": len(context_data["chunks"]),
                    "generator_responses": len(responses),
                    "judge_evaluations": len(judge_evaluations),
                    "consensus_components": len([r for r in consensus_results if r.final_text.strip()]),
                    "component_winners": {r.component.value: r.winning_model for r in consensus_results}
                },
                "intermediate_data": {
                    "responses": responses,
                    "consensus_results": consensus_results,
                    "judge_evaluations": judge_evaluations
                } if self.config.save_training_data else None
            }
            
            logger.info(f"✅ Ensemble processing completed [{request_id}]: {processing_time_ms}ms, ${cost_estimate:.3f}")
            
            return result
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"❌ Ensemble processing failed [{request_id}]: {e}")
            
            return {
                "request_id": request_id,
                "query": query,
                "final_response": f"عذراً، حدث خطأ في معالجة استفسارك: {str(e)}",
                "processing_time_ms": processing_time_ms,
                "cost_estimate": 0.0,
                "quality_report": {"passed": False, "issues": [str(e)], "metrics": {}},
                "ensemble_data": {},
                "error": str(e)
            }
    
    def _estimate_cost(self, responses: Dict[str, str], judge_evaluations: Dict[str, List[ComponentEvaluation]]) -> float:
        """Estimate API costs for this query"""
        
        # Generation costs (rough estimates based on token usage)
        generation_cost = 0.0
        
        cost_per_model = {
            "chatgpt": 0.06,    # GPT-4o
            "deepseek": 0.01,   # DeepSeek  
            "grok": 0.05,       # Grok-2
            "gemini": 0.04      # Gemini 1.5 Pro
        }
        
        for model_name in responses.keys():
            generation_cost += cost_per_model.get(model_name, 0.03)  # Default
        
        # Judging costs
        judging_cost = len(judge_evaluations) * 0.04  # ~$0.04 per judge
        
        # Assembly cost
        assembly_cost = 0.02
        
        total_cost = generation_cost + judging_cost + assembly_cost
        
        return round(total_cost, 3)
    
    async def process_streaming(self, query: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Streaming version that yields progress updates
        """
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            yield {"type": "start", "request_id": request_id, "query": query}
            
            # Layer 1
            yield {"type": "progress", "layer": 1, "status": "Context Retrieval"}
            context_data = await self.context_retriever.get_legal_context(query)
            yield {"type": "progress", "layer": 1, "status": "Complete", "chunks": len(context_data["chunks"])}
            
            # Layer 2  
            yield {"type": "progress", "layer": 2, "status": "Multi-Model Generation"}
            responses = await self.multi_generator.generate_parallel_responses(context_data)
            yield {"type": "progress", "layer": 2, "status": "Complete", "models": len(responses)}
            
            # Layer 3
            yield {"type": "progress", "layer": 3, "status": "Judge Evaluation"}
            judge_evaluations = await self.judge_system.evaluate_responses(query, responses)
            yield {"type": "progress", "layer": 3, "status": "Complete", "judges": len(judge_evaluations)}
            
            # Layer 4
            yield {"type": "progress", "layer": 4, "status": "Consensus Building"}
            consensus_results = self.consensus_builder.build_consensus(judge_evaluations)
            yield {"type": "progress", "layer": 4, "status": "Complete", "components": len(consensus_results)}
            
            # Layer 5
            yield {"type": "progress", "layer": 5, "status": "Response Assembly"}
            final_response = await self.assembler.assemble_final_response(consensus_results, query)
            yield {"type": "progress", "layer": 5, "status": "Complete"}
            
            # Layer 6
            yield {"type": "progress", "layer": 6, "status": "Quality Verification"}
            quality_report = self.quality_verifier.verify_quality(
                final_response, responses, consensus_results, context_data["chunks"]
            )
            yield {"type": "progress", "layer": 6, "status": "Complete", "passed": quality_report.passed}
            
            # Layer 7
            yield {"type": "progress", "layer": 7, "status": "Data Collection"}
            processing_time_ms = int((time.time() - start_time) * 1000)
            cost_estimate = self._estimate_cost(responses, judge_evaluations)
            
            training_data = self.data_collector.collect_training_example(
                query=query, context_data=context_data, responses=responses,
                judge_evaluations=judge_evaluations, consensus_results=consensus_results,
                final_response=final_response, quality_report=quality_report,
                processing_time_ms=processing_time_ms, cost_estimate=cost_estimate
            )
            yield {"type": "progress", "layer": 7, "status": "Complete"}
            
            # Final result
            yield {
                "type": "complete",
                "request_id": request_id,
                "final_response": final_response,
                "processing_time_ms": processing_time_ms,
                "cost_estimate": cost_estimate,
                "quality_passed": quality_report.passed,
                "ensemble_stats": {
                    "context_chunks": len(context_data["chunks"]),
                    "models_used": len(responses),
                    "judges_used": len(judge_evaluations),
                    "components_extracted": len([r for r in consensus_results if r.final_text.strip()])
                }
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "request_id": request_id,
                "error": str(e),
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }

# ==================== GLOBAL INSTANCE ====================

# Initialize ensemble system
ensemble_engine = EnsembleLegalAI()

# Export functions for integration
async def process_ensemble_query(query: str) -> Dict[str, Any]:
    """Main ensemble processing function"""
    return await ensemble_engine.process_legal_query(query)

async def process_ensemble_streaming(query: str) -> AsyncIterator[Dict[str, Any]]:
    """Streaming ensemble processing"""
    async for update in ensemble_engine.process_streaming(query):
        yield update

# Utility functions
def get_ensemble_stats() -> Dict[str, Any]:
    """Get ensemble system statistics"""
    training_stats = ensemble_engine.data_collector.get_training_stats()
    
    return {
        "system_status": "active",
        "available_generators": len(ensemble_engine.clients.get_available_generators()),
        "available_judges": len(ensemble_engine.clients.get_available_judges()),
        "training_data": training_stats,
        "config": {
            "temperature": ensemble_engine.config.temperature,
            "max_tokens": ensemble_engine.config.max_tokens,
            "context_chunks": ensemble_engine.config.context_chunks
        }
    }

def get_ensemble_engine():
    """Get ensemble engine instance"""
    return ensemble_engine

logger.info("🚀 Ensemble Legal AI System loaded and ready!")

# ==================== TESTING FRAMEWORK ====================

async def test_ensemble_system():
    """Test ensemble system with sample queries"""
    
    test_queries = [
        "ما هي مكافأة نهاية الخدمة للموظف الذي عمل 5 سنوات براتب 6000 ريال؟",
        "موظف رفع عليه دعوى من شركته بزعم إفشاء أسرار، كيف يرد على هذه الدعوى؟", 
        "أريد فصل موظف لسوء السلوك، ما هي الإجراءات المطلوبة؟"
    ]
    
    logger.info("🧪 Starting ensemble system tests...")
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n🧪 Test {i}: {query}")
        
        try:
            result = await ensemble_engine.process_legal_query(query)
            
            logger.info(f"✅ Test {i} completed:")
            logger.info(f"  Processing time: {result['processing_time_ms']}ms")
            logger.info(f"  Cost estimate: ${result['cost_estimate']:.3f}")
            logger.info(f"  Quality passed: {result['quality_report']['passed']}")
            logger.info(f"  Response length: {len(result['final_response'])} chars")
            
            if result['ensemble_data']:
                logger.info(f"  Models used: {result['ensemble_data']['generator_responses']}")
                logger.info(f"  Components: {result['ensemble_data']['consensus_components']}")
            
        except Exception as e:
            logger.error(f"❌ Test {i} failed: {e}")
    
    logger.info("🧪 Ensemble testing completed")

if __name__ == "__main__":
    asyncio.run(test_ensemble_system())