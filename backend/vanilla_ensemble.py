"""
VANILLA ENSEMBLE SYSTEM
No RAG, no context - just pure model comparison + component extraction

Flow:
1. Send SAME question to 4 models (vanilla responses like using ChatGPT directly)
2. 3 judges extract best components from each response  
3. Assemble best parts into superior final response

This is the EXACT system you specified!
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

load_dotenv()

logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

@dataclass
class VanillaEnsembleConfig:
    """Pure vanilla ensemble configuration"""
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY")  
    grok_api_key: str = os.getenv("GROK_API_KEY")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    claude_api_key: str = os.getenv("ANTHROPIC_API_KEY")
    
    # Model settings
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # Cost tracking
    track_costs: bool = True
    max_cost_per_query: float = 0.50
    
    # Data collection
    save_training_data: bool = True
    training_data_path: str = "data/vanilla_ensemble_training.jsonl"

config = VanillaEnsembleConfig()

class ComponentType(Enum):
    """7 components to extract from vanilla responses"""
    DIRECT_ANSWER = "direct_answer"
    LEGAL_FOUNDATION = "legal_foundation"  
    ARTICLE_CITATIONS = "article_citations"
    NUMERICAL_EXAMPLES = "numerical_examples"
    STEP_PROCEDURES = "step_procedures"
    EDGE_CASES = "edge_cases"
    PRACTICAL_ADVICE = "practical_advice"

# ==================== VANILLA MODEL CLIENTS ====================

class VanillaModelClients:
    """4 Vanilla models + 3 judges (no RAG involved)"""
    
    def __init__(self):
        # Generator models (4) - Pure vanilla clients
        self.chatgpt = AsyncOpenAI(
            api_key=config.openai_api_key,
            http_client=httpx.AsyncClient()
        ) if config.openai_api_key else None
        
        self.deepseek = AsyncOpenAI(
            api_key=config.deepseek_api_key,
            base_url="https://api.deepseek.com/v1",
            http_client=httpx.AsyncClient()
        ) if config.deepseek_api_key else None
        
        self.grok = AsyncOpenAI(
            api_key=config.grok_api_key,
            base_url="https://api.x.ai/v1",
            http_client=httpx.AsyncClient()
        ) if config.grok_api_key else None
        
        # Note: Will add Gemini when we get proper API setup
        self.gemini = None
        
        # Judge models (3)
        self.judge_claude = AsyncOpenAI(
            api_key=config.claude_api_key,
            base_url="https://api.anthropic.com/v1",
            http_client=httpx.AsyncClient()
        ) if config.claude_api_key else None
        
        self.judge_gpt = self.chatgpt
        self.judge_gemini = None  # Will add when Gemini is working
        
        logger.info(f"🍦 Vanilla model clients initialized:")
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

# ==================== VANILLA MULTI-MODEL GENERATION ====================

class VanillaMultiModelGenerator:
    """Generate PURE vanilla responses from 4 different models"""
    
    def __init__(self, clients: VanillaModelClients):
        self.clients = clients
        self.generators = clients.get_available_generators()
        
        # Model-specific configurations for vanilla responses
        self.model_configs = {
            "chatgpt": {
                "model": "gpt-4o", 
                "description": "Best overall reasoning",
                "system_prompt": "أنت مستشار قانوني سعودي خبير. قدم استشارة قانونية دقيقة ومفصلة."
            },
            "deepseek": {
                "model": "deepseek-chat", 
                "description": "Cost-effective, strong on structured tasks",
                "system_prompt": "أنت خبير في القانون السعودي. قدم استشارة شاملة مع أمثلة رقمية وإجراءات واضحة."
            },
            "grok": {
                "model": "grok-2", 
                "description": "Alternative perspective",
                "system_prompt": "أنت محامي سعودي متمرس. قدم استشارة عملية مع نصائح قانونية واقعية."
            },
            "gemini": {
                "model": "gemini-1.5-pro", 
                "description": "Comprehensive responses",
                "system_prompt": "أنت استشاري قانوني متخصص في القانون السعودي. قدم إجابة شاملة تغطي جميع الجوانب."
            }
        }
        
        logger.info(f"🍦 Vanilla multi-model generator initialized with {len(self.generators)} models")
    
    async def generate_vanilla_responses(self, query: str) -> Dict[str, str]:
        """
        Send SAME vanilla query to all models (no RAG context)
        Each model responds as if user asked them directly
        """
        
        logger.info(f"🍦 Generating vanilla responses to: {query[:50]}...")
        
        # Generate responses in parallel
        tasks = []
        for model_name, client in self.generators.items():
            task = self._generate_single_vanilla_response(
                model_name=model_name,
                client=client,
                query=query
            )
            tasks.append((model_name, task))
        
        # Wait for all responses
        start_time = time.time()
        responses = {}
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (model_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Vanilla model {model_name} failed: {result}")
                responses[model_name] = f"خطأ في النموذج: {str(result)}"
            else:
                responses[model_name] = result
                logger.info(f"✅ {model_name}: {len(result)} characters")
        
        generation_time = time.time() - start_time
        logger.info(f"⏱️ All vanilla models completed in {generation_time:.2f} seconds")
        
        return responses
    
    async def _generate_single_vanilla_response(self, model_name: str, client: AsyncOpenAI, query: str) -> str:
        """Generate vanilla response from a single model (no RAG context)"""
        try:
            model_config = self.model_configs.get(model_name, {})
            model_id = model_config.get("model", "gpt-4o")
            system_prompt = model_config.get("system_prompt", "أنت مستشار قانوني سعودي.")
            
            # Pure vanilla - just system prompt + user question
            response = await client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.debug(f"📝 Vanilla {model_name}: {len(content)} characters")
            
            return content
            
        except Exception as e:
            logger.error(f"Vanilla model {model_name} generation failed: {e}")
            raise

# ==================== 3-JUDGE COMPONENT EXTRACTION (SAME AS BEFORE) ====================

@dataclass
class ComponentEvaluation:
    """Single component evaluation by one judge"""
    component: ComponentType
    evaluations: Dict[str, Dict[str, Any]]
    winner: str
    extracted_text: str
    winner_score: float
    reasoning: str

class VanillaComponentJudge:
    """Judge that evaluates vanilla responses for component extraction"""
    
    def __init__(self, judge_name: str, client: AsyncOpenAI):
        self.judge_name = judge_name
        self.client = client
        self.components = list(ComponentType)
        
        logger.info(f"⚖️ Vanilla Judge {judge_name} initialized for {len(self.components)} components")
    
    async def evaluate_vanilla_responses(self, query: str, vanilla_responses: Dict[str, str]) -> List[ComponentEvaluation]:
        """Evaluate vanilla responses (no RAG context) for component extraction"""
        
        logger.info(f"⚖️ Vanilla Judge {self.judge_name} evaluating {len(self.components)} components...")
        
        evaluations = []
        for component in self.components:
            try:
                evaluation = await self._evaluate_single_component(component, query, vanilla_responses)
                evaluations.append(evaluation)
                logger.debug(f"  ✅ {component.value}: Winner = {evaluation.winner} (score: {evaluation.winner_score:.1f})")
            except Exception as e:
                logger.error(f"Component {component.value} evaluation failed: {e}")
                # Create fallback evaluation
                fallback = ComponentEvaluation(
                    component=component,
                    evaluations={},
                    winner="chatgpt",
                    extracted_text="[تعذر استخراج هذا المكون]",
                    winner_score=5.0,
                    reasoning=f"خطأ في التقييم: {str(e)}"
                )
                evaluations.append(fallback)
        
        logger.info(f"⚖️ Vanilla Judge {self.judge_name} completed all component evaluations")
        return evaluations
    
    async def _evaluate_single_component(self, component: ComponentType, query: str, 
                                       vanilla_responses: Dict[str, str]) -> ComponentEvaluation:
        """Evaluate a single component across vanilla responses"""
        
        # Create component-specific evaluation prompt for vanilla responses
        evaluation_prompt = self._create_vanilla_component_prompt(component, query, vanilla_responses)
        
        # Get judge's evaluation
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.1,
            max_tokens=1500
        )
        
        evaluation_text = response.choices[0].message.content
        
        # Parse evaluation result
        return self._parse_evaluation_result(component, evaluation_text, vanilla_responses)
    
    def _create_vanilla_component_prompt(self, component: ComponentType, query: str, 
                                       vanilla_responses: Dict[str, str]) -> str:
        """Create evaluation prompt for vanilla responses"""
        
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
        
        # Build vanilla responses section
        responses_text = ""
        for model_name, response in vanilla_responses.items():
            responses_text += f"\n--- استجابة {model_name.upper()} (بدون سياق) ---\n{response}\n"
        
        prompt = f"""أنت خبير تقييم قانوني. قيم جودة مكون محدد في استجابات مختلفة من 4 نماذج ذكية.

السؤال الأصلي: {query}

المكون المطلوب تقييمه: {comp_info['name']}
الوصف: {comp_info['description']}
مثال: {comp_info['example']}

الاستجابات من 4 نماذج (بدون سياق خارجي):{responses_text}

📋 مهمتك:
1. قيم جودة "{comp_info['name']}" في كل استجابة (درجة من 0-10)
2. اختر الاستجابة الأفضل لهذا المكون تحديداً
3. استخرج النص الدقيق للمكون من الاستجابة الفائزة
4. اشرح سبب اختيارك

ملاحظة: هذه استجابات vanilla (بدون مراجع خارجية) - قيم المحتوى نفسه وليس المصادر.

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
                               vanilla_responses: Dict[str, str]) -> ComponentEvaluation:
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
            winner_score = 5.0
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
            logger.error(f"Failed to parse vanilla evaluation for {component.value}: {e}")
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

class VanillaThreeJudgeSystem:
    """3 judges evaluate vanilla responses"""
    
    def __init__(self, clients: VanillaModelClients):
        self.judges = {}
        available_judges = clients.get_available_judges()
        
        for judge_name, client in available_judges.items():
            self.judges[judge_name] = VanillaComponentJudge(judge_name, client)
        
        logger.info(f"⚖️ Vanilla three-judge system initialized with {len(self.judges)} judges: {list(self.judges.keys())}")
    
    async def evaluate_vanilla_responses(self, query: str, vanilla_responses: Dict[str, str]) -> Dict[str, List[ComponentEvaluation]]:
        """All 3 judges evaluate vanilla responses"""
        
        logger.info("⚖️ Starting vanilla 3-judge evaluation process...")
        start_time = time.time()
        
        # Run all judges in parallel
        judge_tasks = []
        for judge_name, judge in self.judges.items():
            task = judge.evaluate_vanilla_responses(query, vanilla_responses)
            judge_tasks.append((judge_name, task))
        
        # Wait for all judges
        judge_results = {}
        results = await asyncio.gather(*[task for _, task in judge_tasks], return_exceptions=True)
        
        for (judge_name, _), result in zip(judge_tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Vanilla Judge {judge_name} failed: {result}")
                judge_results[judge_name] = []
            else:
                judge_results[judge_name] = result
                logger.info(f"⚖️ Vanilla Judge {judge_name}: {len(result)} component evaluations")
        
        evaluation_time = time.time() - start_time
        logger.info(f"⚖️ All vanilla judges completed in {evaluation_time:.2f} seconds")
        
        return judge_results

# ==================== CONSENSUS BUILDING (SAME AS BEFORE) ====================

@dataclass  
class VanillaConsensusResult:
    """Consensus result for vanilla responses"""
    component: ComponentType
    final_text: str
    winning_model: str
    consensus_type: str
    judge_votes: List[str]
    final_score: float

class VanillaConsensusBuilder:
    """Build consensus from vanilla response evaluations"""
    
    def __init__(self):
        logger.info("🗳️ Vanilla consensus builder initialized")
    
    def build_vanilla_consensus(self, judge_evaluations: Dict[str, List[ComponentEvaluation]]) -> List[VanillaConsensusResult]:
        """Apply voting rules to vanilla response components"""
        
        if not judge_evaluations:
            logger.warning("No vanilla judge evaluations provided")
            return []
        
        # Get all components to process
        components = list(ComponentType)
        consensus_results = []
        
        for component in components:
            try:
                consensus = self._build_component_consensus(component, judge_evaluations)
                consensus_results.append(consensus)
                
                logger.info(f"🗳️ Vanilla {component.value}: {consensus.consensus_type} -> {consensus.winning_model} (score: {consensus.final_score:.1f})")
                
            except Exception as e:
                logger.error(f"Vanilla consensus building failed for {component.value}: {e}")
                # Create fallback consensus
                fallback = VanillaConsensusResult(
                    component=component,
                    final_text="[تعذر بناء الإجماع لهذا المكون]",
                    winning_model="chatgpt",
                    consensus_type="error",
                    judge_votes=[],
                    final_score=0.0
                )
                consensus_results.append(fallback)
        
        logger.info(f"🗳️ Vanilla consensus building completed for {len(consensus_results)} components")
        return consensus_results
    
    def _build_component_consensus(self, component: ComponentType, 
                                 judge_evaluations: Dict[str, List[ComponentEvaluation]]) -> VanillaConsensusResult:
        """Build consensus for a single component from vanilla responses"""
        
        # Extract evaluations for this component from all judges
        component_evaluations = []
        for judge_name, evaluations in judge_evaluations.items():
            for eval_item in evaluations:
                if eval_item.component == component:
                    component_evaluations.append((judge_name, eval_item))
                    break
        
        if not component_evaluations:
            # Component missing from all judges
            return VanillaConsensusResult(
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
            
            return VanillaConsensusResult(
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
        
        return VanillaConsensusResult(
            component=component,
            final_text=best_evaluation.extracted_text,
            winning_model=best_winner,
            consensus_type="highest_score",
            judge_votes=judge_votes,
            final_score=best_score
        )

# ==================== VANILLA RESPONSE ASSEMBLY ====================

class VanillaResponseAssembler:
    """Assemble final response from vanilla response components"""
    
    def __init__(self, clients: VanillaModelClients):
        # Use ChatGPT for assembly
        self.assembler_client = clients.chatgpt
        logger.info("🔧 Vanilla response assembler initialized")
    
    async def assemble_vanilla_response(self, consensus_results: List[VanillaConsensusResult], 
                                      query: str, use_smooth_transitions: bool = True) -> str:
        """Assemble final response from vanilla response components"""
        
        if use_smooth_transitions and self.assembler_client:
            return await self._assemble_with_transitions(consensus_results, query)
        else:
            return self._assemble_simple_concatenation(consensus_results)
    
    def _assemble_simple_concatenation(self, consensus_results: List[VanillaConsensusResult]) -> str:
        """Simple concatenation of vanilla components"""
        
        # Assembly order
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
                sections.append(component_result.final_text)
        
        final_response = "\n\n".join(sections)
        
        if not final_response.strip():
            final_response = "عذراً، لم أتمكن من تجميع استجابة مناسبة من النماذج المتاحة."
        
        logger.info(f"🔧 Vanilla simple assembly completed: {len(sections)} sections, {len(final_response)} characters")
        return final_response
    
    async def _assemble_with_transitions(self, consensus_results: List[VanillaConsensusResult], query: str) -> str:
        """Smooth transitions for vanilla components"""
        
        try:
            # Collect all components
            component_texts = {}
            
            for result in consensus_results:
                if result.final_text.strip():
                    component_texts[result.component.value] = result.final_text
            
            if not component_texts:
                return "عذراً، لم أتمكن من استخراج أي مكونات مناسبة من النماذج."
            
            # Create assembly prompt for vanilla responses
            assembly_prompt = self._create_vanilla_assembly_prompt(component_texts, query)
            
            # Generate assembled response
            response = await self.assembler_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": assembly_prompt}],
                temperature=0.3,
                max_tokens=3000
            )
            
            assembled_response = response.choices[0].message.content.strip()
            
            logger.info(f"🔧 Vanilla smooth assembly completed: {len(component_texts)} components, {len(assembled_response)} characters")
            
            return assembled_response
            
        except Exception as e:
            logger.error(f"Vanilla smooth assembly failed: {e}, falling back to simple concatenation")
            return self._assemble_simple_concatenation(consensus_results)
    
    def _create_vanilla_assembly_prompt(self, component_texts: Dict[str, str], query: str) -> str:
        """Create prompt for vanilla response assembly"""
        
        components_section = ""
        for component_name, text in component_texts.items():
            components_section += f"\n[{component_name}]\n{text}\n"
        
        return f"""أنت محرر قانوني متخصص في تجميع الاستجابات من نماذج ذكية مختلفة.

السؤال الأصلي: {query}

المكونات المستخرجة من أفضل النماذج (استجابات vanilla بدون سياق خارجي):{components_section}

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
- هذه استجابات vanilla (بدون مراجع) - لا تضف مراجع خارجية

أجب بالاستجابة النهائية المجمعة فقط."""

# ==================== MAIN VANILLA ENSEMBLE ENGINE ====================

class VanillaEnsembleLegalAI:
    """
    Pure Vanilla Ensemble System
    No RAG - Just 4 models + 3 judges + component extraction
    """
    
    def __init__(self):
        """Initialize vanilla ensemble components"""
        
        logger.info("🍦 Initializing Vanilla Ensemble Legal AI System...")
        
        self.config = config
        self.clients = VanillaModelClients()
        
        # Vanilla components
        self.multi_generator = VanillaMultiModelGenerator(self.clients)
        self.judge_system = VanillaThreeJudgeSystem(self.clients)
        self.consensus_builder = VanillaConsensusBuilder()
        self.assembler = VanillaResponseAssembler(self.clients)
        
        logger.info("✅ Vanilla Ensemble Legal AI System initialized successfully")
        logger.info(f"🤖 Available generators: {len(self.clients.get_available_generators())}")
        logger.info(f"⚖️ Available judges: {len(self.clients.get_available_judges())}")
    
    async def process_vanilla_query(self, query: str) -> Dict[str, Any]:
        """
        Pure vanilla processing pipeline
        
        1. Send query to 4 models (no RAG)
        2. 3 judges extract best components
        3. Assemble best parts into final response
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        logger.info(f"🍦 Processing vanilla query [{request_id}]: {query[:50]}...")
        
        try:
            # Step 1: Generate vanilla responses from 4 models
            logger.info("🍦 Step 1: Vanilla Multi-Model Generation")
            vanilla_responses = await self.multi_generator.generate_vanilla_responses(query)
            
            if not vanilla_responses:
                raise Exception("No vanilla responses generated from any model")
            
            # Step 2: 3-Judge Component Extraction
            logger.info("⚖️ Step 2: Vanilla Component Extraction (3 Judges)")
            judge_evaluations = await self.judge_system.evaluate_vanilla_responses(query, vanilla_responses)
            
            # Step 3: Consensus Building
            logger.info("🗳️ Step 3: Vanilla Consensus Building")
            consensus_results = self.consensus_builder.build_vanilla_consensus(judge_evaluations)
            
            # Step 4: Response Assembly
            logger.info("🔧 Step 4: Vanilla Response Assembly")
            final_response = await self.assembler.assemble_vanilla_response(consensus_results, query)
            
            # Calculate metrics
            processing_time_ms = int((time.time() - start_time) * 1000)
            cost_estimate = self._estimate_vanilla_cost(vanilla_responses, judge_evaluations)
            
            # Compile result
            result = {
                "request_id": request_id,
                "query": query,
                "final_response": final_response,
                "processing_time_ms": processing_time_ms,
                "cost_estimate": cost_estimate,
                "vanilla_data": {
                    "generator_responses": len(vanilla_responses),
                    "judge_evaluations": len(judge_evaluations),
                    "consensus_components": len([r for r in consensus_results if r.final_text.strip()]),
                    "component_winners": {r.component.value: r.winning_model for r in consensus_results}
                },
                "intermediate_data": {
                    "vanilla_responses": vanilla_responses,
                    "consensus_results": consensus_results,
                    "judge_evaluations": judge_evaluations
                } if self.config.save_training_data else None
            }
            
            logger.info(f"✅ Vanilla ensemble processing completed [{request_id}]: {processing_time_ms}ms, ${cost_estimate:.3f}")
            
            return result
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"❌ Vanilla ensemble processing failed [{request_id}]: {e}")
            
            return {
                "request_id": request_id,
                "query": query,
                "final_response": f"عذراً، حدث خطأ في معالجة استفسارك: {str(e)}",
                "processing_time_ms": processing_time_ms,
                "cost_estimate": 0.0,
                "vanilla_data": {},
                "error": str(e)
            }
    
    def _estimate_vanilla_cost(self, vanilla_responses: Dict[str, str], judge_evaluations: Dict[str, List[ComponentEvaluation]]) -> float:
        """Estimate costs for vanilla ensemble"""
        
        # Generation costs
        generation_cost = 0.0
        
        cost_per_model = {
            "chatgpt": 0.06,
            "deepseek": 0.01,
            "grok": 0.05,
            "gemini": 0.04
        }
        
        for model_name in vanilla_responses.keys():
            generation_cost += cost_per_model.get(model_name, 0.03)
        
        # Judging costs
        judging_cost = len(judge_evaluations) * 0.04
        
        # Assembly cost
        assembly_cost = 0.02
        
        total_cost = generation_cost + judging_cost + assembly_cost
        
        return round(total_cost, 3)
    
    async def process_vanilla_streaming(self, query: str) -> AsyncIterator[Dict[str, Any]]:
        """Streaming version of vanilla ensemble"""
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            yield {"type": "start", "request_id": request_id, "query": query, "mode": "vanilla"}
            
            # Step 1
            yield {"type": "progress", "step": 1, "status": "Vanilla Model Generation"}
            vanilla_responses = await self.multi_generator.generate_vanilla_responses(query)
            yield {"type": "progress", "step": 1, "status": "Complete", "models": len(vanilla_responses)}
            
            # Step 2
            yield {"type": "progress", "step": 2, "status": "Judge Evaluation"}
            judge_evaluations = await self.judge_system.evaluate_vanilla_responses(query, vanilla_responses)
            yield {"type": "progress", "step": 2, "status": "Complete", "judges": len(judge_evaluations)}
            
            # Step 3
            yield {"type": "progress", "step": 3, "status": "Consensus Building"}
            consensus_results = self.consensus_builder.build_vanilla_consensus(judge_evaluations)
            yield {"type": "progress", "step": 3, "status": "Complete", "components": len(consensus_results)}
            
            # Step 4
            yield {"type": "progress", "step": 4, "status": "Response Assembly"}
            final_response = await self.assembler.assemble_vanilla_response(consensus_results, query)
            yield {"type": "progress", "step": 4, "status": "Complete"}
            
            # Final result
            processing_time_ms = int((time.time() - start_time) * 1000)
            cost_estimate = self._estimate_vanilla_cost(vanilla_responses, judge_evaluations)
            
            yield {
                "type": "complete",
                "request_id": request_id,
                "final_response": final_response,
                "processing_time_ms": processing_time_ms,
                "cost_estimate": cost_estimate,
                "vanilla_stats": {
                    "models_used": len(vanilla_responses),
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

# ==================== GLOBAL VANILLA INSTANCE ====================

# Initialize vanilla ensemble system
vanilla_ensemble = VanillaEnsembleLegalAI()

# Export functions
async def process_vanilla_ensemble_query(query: str) -> Dict[str, Any]:
    """Main vanilla ensemble processing function"""
    return await vanilla_ensemble.process_vanilla_query(query)

async def process_vanilla_ensemble_streaming(query: str) -> AsyncIterator[Dict[str, Any]]:
    """Streaming vanilla ensemble processing"""
    async for update in vanilla_ensemble.process_vanilla_streaming(query):
        yield update

def get_vanilla_ensemble_stats() -> Dict[str, Any]:
    """Get vanilla ensemble system statistics"""
    
    return {
        "system_status": "active",
        "system_type": "pure vanilla ensemble",
        "available_generators": len(vanilla_ensemble.clients.get_available_generators()),
        "available_judges": len(vanilla_ensemble.clients.get_available_judges()),
        "config": {
            "temperature": vanilla_ensemble.config.temperature,
            "max_tokens": vanilla_ensemble.config.max_tokens,
            "rag_enabled": False
        },
        "process_flow": [
            "1. Send SAME question to 4 models (vanilla responses)",
            "2. 3 judges extract best components from each response",
            "3. Consensus voting to select best parts",
            "4. Assemble best components into final response"
        ]
    }

def get_vanilla_ensemble_engine():
    """Get vanilla ensemble engine instance"""
    return vanilla_ensemble

logger.info("🍦 Vanilla Ensemble Legal AI System loaded and ready!")
logger.info("📋 Process: 4 Vanilla Models → 3 Judge Component Extraction → Assembly")
logger.info("🚫 NO RAG: Pure model comparison with component extraction")

# ==================== VANILLA TESTING FRAMEWORK ====================

async def test_vanilla_ensemble():
    """Test vanilla ensemble with legal queries"""
    
    test_queries = [
        "ما هي مكافأة نهاية الخدمة في السعودية؟",
        "كيف أحسب الإجازة السنوية للموظف؟", 
        "ما عقوبة التأخير عن العمل؟"
    ]
    
    logger.info("🧪 Testing vanilla ensemble system...")
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n🧪 Vanilla Test {i}: {query}")
        
        try:
            result = await vanilla_ensemble.process_vanilla_query(query)
            
            logger.info(f"✅ Vanilla Test {i} completed:")
            logger.info(f"  Processing time: {result['processing_time_ms']}ms")
            logger.info(f"  Cost estimate: ${result['cost_estimate']:.3f}")
            logger.info(f"  Response length: {len(result['final_response'])} chars")
            
            if result['vanilla_data']:
                logger.info(f"  Models used: {result['vanilla_data']['generator_responses']}")
                logger.info(f"  Components: {result['vanilla_data']['consensus_components']}")
            
        except Exception as e:
            logger.error(f"❌ Vanilla Test {i} failed: {e}")
    
    logger.info("🧪 Vanilla ensemble testing completed")

if __name__ == "__main__":
    asyncio.run(test_vanilla_ensemble())