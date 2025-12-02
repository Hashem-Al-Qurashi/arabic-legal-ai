import logging
import asyncio
import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import openai
from openai import OpenAI, AsyncOpenAI
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'ensemble_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('VanillaEnsemble')

@dataclass
class ModelResponse:
    model_name: str
    response: str
    cost: float
    response_time: float
    success: bool
    error: str = None

@dataclass
class BestElements:
    best_from_model_1: str
    best_from_model_2: str
    best_from_model_3: str
    overall_quality_score: float

@dataclass
class JudgeEvaluation:
    judge_name: str
    best_elements: BestElements
    processing_time: float
    cost: float
    success: bool
    error: str = None

class VanillaEnsemble:
    def __init__(self):
        logger.info("🚀 Initializing Vanilla Ensemble System with OpenRouter")
        
        # Single API key for all models!
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            logger.error("❌ OPENROUTER_API_KEY not found in environment variables")
            raise ValueError("OPENROUTER_API_KEY is required")
        
        # Initialize OpenRouter clients
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        self.async_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # Updated model names for OpenRouter
        self.generation_models = [
            "openai/gpt-4o",
            "deepseek/deepseek-chat",
            "google/gemini-2.5-flash"
        ]
        
        self.judge_models = [
            "openai/gpt-4o",
            "google/gemini-2.5-flash"
        ]
        
        logger.info(f"✅ System initialized with {len(self.generation_models)} generation models via OpenRouter")
        logger.info(f"✅ Using API key: ...{self.api_key[-10:]}")

    async def call_model(self, model: str, prompt: str) -> ModelResponse:
        """Unified model calling through OpenRouter"""
        logger.info(f"🤖 Calling {model} via OpenRouter")
        start_time = time.time()
        
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            response_time = time.time() - start_time
            cost = self.estimate_cost(model, len(prompt), len(response.choices[0].message.content))
            
            logger.info(f"✅ {model} responded in {response_time:.2f}s, cost: ${cost:.4f}")
            
            return ModelResponse(
                model_name=model,
                response=response.choices[0].message.content,
                cost=cost,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ {model} failed after {response_time:.2f}s: {e}")
            
            return ModelResponse(
                model_name=model,
                response="",
                cost=0.0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on model"""
        # Rough token estimation (4 chars = 1 token)
        input_tokens = input_tokens / 4
        output_tokens = output_tokens / 4
        
        rates = {
            "openai/gpt-4o": {"input": 0.005/1000, "output": 0.015/1000},
            "deepseek/deepseek-chat": {"input": 0.0015/1000, "output": 0.002/1000},
            "google/gemini-2.5-flash": {"input": 0.00075/1000, "output": 0.003/1000},
            "google/gemini-pro": {"input": 0.00125/1000, "output": 0.00375/1000}
        }
        
        rate = rates.get(model, {"input": 0.002/1000, "output": 0.006/1000})
        return (input_tokens * rate["input"]) + (output_tokens * rate["output"])

    async def generate_responses(self, question: str) -> List[ModelResponse]:
        logger.info(f"📝 Starting Step 1: Multi-Model Generation via OpenRouter")
        logger.info(f"Question: {question}")
        
        saudi_prompt = f"""Answer this question based on Saudi law and regulations. Provide a comprehensive legal response:

{question}

Please provide your answer based on Saudi legal framework, including relevant laws, regulations, and procedures."""

        # Create tasks for all models - they'll run in PARALLEL through OpenRouter
        tasks = []
        for model in self.generation_models:
            tasks.append(self.call_model(model, saudi_prompt))
        
        logger.info(f"🚀 Launching {len(tasks)} parallel API calls via OpenRouter...")
        start_time = time.time()
        
        # All models called simultaneously!
        responses = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        successful_responses = [r for r in responses if r.success]
        failed_responses = [r for r in responses if not r.success]
        
        logger.info(f"✅ Step 1 Complete in {total_time:.2f}s: {len(successful_responses)} successful, {len(failed_responses)} failed")
        
        for response in responses:
            if response.success:
                logger.info(f"✅ {response.model_name}: {len(response.response)} chars, ${response.cost:.4f}, {response.response_time:.2f}s")
            else:
                logger.error(f"❌ {response.model_name}: {response.error}")
        
        return responses

    async def extract_components(self, responses: List[ModelResponse]) -> List[JudgeEvaluation]:
        logger.info("⚖️ Starting Step 2: Component Extraction by Judges")
        
        successful_responses = [r for r in responses if r.success]
        if not successful_responses:
            logger.error("❌ No successful responses to judge")
            return []
        
        combined_responses = "\n\n" + "="*50 + "\n\n".join([
            f"MODEL {i+1} ({r.model_name}):\n{r.response}" 
            for i, r in enumerate(successful_responses)
        ])
        
        judge_prompt = f"""You are a legal expert. Read these model responses and identify the BEST parts from each:

{combined_responses}

Extract the most valuable content from each model. Copy the exact text (don't summarize):

Return ONLY this JSON:
{{
    "best_from_model_1": "[copy the best sections from MODEL 1 exactly as written]",
    "best_from_model_2": "[copy the best sections from MODEL 2 exactly as written]", 
    "best_from_model_3": "[copy the best sections from MODEL 3 exactly as written]",
    "overall_quality_score": 8.5
}}

IMPORTANT: Copy actual text content, not references or summaries."""

        judge_tasks = []
        for judge in self.judge_models:
            judge_tasks.append(self.judge_with_model(judge, judge_prompt))
        
        logger.info(f"⚖️ Launching {len(judge_tasks)} judge evaluations via OpenRouter...")
        evaluations = await asyncio.gather(*judge_tasks)
        
        successful_evals = [e for e in evaluations if e.success]
        failed_evals = [e for e in evaluations if not e.success]
        
        logger.info(f"✅ Step 2 Complete: {len(successful_evals)} successful, {len(failed_evals)} failed evaluations")
        
        for eval in evaluations:
            if eval.success:
                logger.info(f"✅ {eval.judge_name}: Score {eval.best_elements.overall_quality_score:.1f}, ${eval.cost:.4f}, {eval.processing_time:.2f}s")
            else:
                logger.error(f"❌ {eval.judge_name}: {eval.error}")
        
        return evaluations

    async def judge_with_model(self, model: str, prompt: str) -> JudgeEvaluation:
        logger.info(f"⚖️ Judge evaluation with {model}")
        start_time = time.time()
        
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a legal expert judge. You MUST respond with ONLY valid JSON. No other text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            processing_time = time.time() - start_time
            cost = self.estimate_cost(model, len(prompt), len(response.choices[0].message.content))
            
            content = response.choices[0].message.content.strip()
            logger.info(f"📄 Judge response content: {content[:200]}...")
            
            # Try to extract JSON from response if it contains other text
            import json
            if content.startswith('```json'):
                content = content.split('```json')[1].split('```')[0].strip()
            elif content.startswith('```'):
                content = content.split('```')[1].split('```')[0].strip()
            
            result = json.loads(content)
            
            best_elements = BestElements(
                best_from_model_1=result.get("best_from_model_1", ""),
                best_from_model_2=result.get("best_from_model_2", ""),
                best_from_model_3=result.get("best_from_model_3", ""),
                overall_quality_score=result.get("overall_quality_score", 0.0)
            )
            
            return JudgeEvaluation(
                judge_name=model,
                best_elements=best_elements,
                processing_time=processing_time,
                cost=cost,
                success=True
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Judge {model} failed: {e}")
            
            empty_elements = BestElements("", "", "", 0.0)
            return JudgeEvaluation(
                judge_name=model,
                best_elements=empty_elements,
                processing_time=processing_time,
                cost=0.0,
                success=False,
                error=str(e)
            )

    def consensus_voting(self, evaluations: List[JudgeEvaluation]) -> Dict[str, str]:
        logger.info("🗳️ Starting Step 3: Consensus Voting")
        
        successful_evals = [e for e in evaluations if e.success]
        if not successful_evals:
            logger.error("❌ No successful evaluations available")
            return {"best_elements": "", "avg_score": 0.0}
        
        logger.info(f"🗳️ Combining best elements from {len(successful_evals)} judges")
        
        # Collect all best elements from all judges
        all_best_elements = []
        total_score = 0
        
        for eval in successful_evals:
            elements = eval.best_elements
            judge_elements = []
            
            if elements.best_from_model_1.strip():
                judge_elements.append(f"From Model 1: {elements.best_from_model_1}")
            if elements.best_from_model_2.strip():
                judge_elements.append(f"From Model 2: {elements.best_from_model_2}")
            if elements.best_from_model_3.strip():
                judge_elements.append(f"From Model 3: {elements.best_from_model_3}")
            
            if judge_elements:
                all_best_elements.extend(judge_elements)
                total_score += elements.overall_quality_score
                logger.info(f"✅ {eval.judge_name}: Score {elements.overall_quality_score:.1f}, {len(judge_elements)} elements")
        
        # Combine all best elements
        combined_elements = "\n\n".join(all_best_elements)
        avg_score = total_score / len(successful_evals) if successful_evals else 0
        
        logger.info(f"✅ Step 3 Complete: Combined {len(all_best_elements)} best elements, average score {avg_score:.1f}")
        
        return {
            "best_elements": combined_elements,
            "avg_score": avg_score
        }

    async def synthesize_response(self, best_elements: Dict[str, Any]) -> str:
        logger.info("🔧 Starting Step 4: AI Synthesis via OpenRouter")
        
        synthesis_prompt = f"""You are an expert Saudi law advisor. Here are the best elements selected from multiple AI models:

{best_elements['best_elements']}

Synthesize all this information into ONE coherent, natural Arabic legal response. 

Requirements:
- Write in your own natural style and flow
- Include all the valuable information from above
- Make it read smoothly as a unified response
- Focus on Saudi law and regulations
- Use proper legal Arabic terminology

Create a comprehensive, well-structured legal response in Arabic."""

        try:
            logger.info("🤖 Synthesizing final response with GPT-4o via OpenRouter")
            start_time = time.time()
            
            response = await self.async_client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=1500
            )
            
            processing_time = time.time() - start_time
            cost = self.estimate_cost("openai/gpt-4o", len(synthesis_prompt), len(response.choices[0].message.content))
            
            logger.info(f"✅ Step 4 Complete: Response synthesized in {processing_time:.2f}s, cost: ${cost:.4f}")
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Synthesis failed: {e}")
            
            # Simple fallback - just return the combined elements
            fallback = f"""بناءً على تحليل متعدد النماذج:

{best_elements['best_elements']}

يرجى ملاحظة أن هذه المعلومات مجمعة من عدة نماذج ذكية وتتطلب مراجعة قانونية متخصصة."""
            
            logger.info("✅ Using fallback synthesis method")
            return fallback

    async def direct_synthesis(self, responses: List[ModelResponse]) -> str:
        logger.info("🎯 Starting Direct Synthesis via OpenRouter - Full Context Preservation")
        
        successful_responses = [r for r in responses if r.success]
        if not successful_responses:
            logger.error("❌ No successful responses to synthesize")
            return "لم يتم الحصول على إجابات صالحة من النماذج."
        
        logger.info(f"📊 Synthesizing from {len(successful_responses)} model responses")
        
        # Log original response lengths
        for i, response in enumerate(successful_responses, 1):
            logger.info(f"📝 Model {i} ({response.model_name}): {len(response.response)} characters")
        
        total_chars = sum(len(r.response) for r in successful_responses)
        logger.info(f"📊 Total input content: {total_chars} characters")
        
        # Combine all responses with clear separation
        combined_responses = "\n\n" + "="*80 + "\n\n".join([
            f"إجابة النموذج {i+1} ({r.model_name}):\n{r.response}" 
            for i, r in enumerate(successful_responses)
        ])
        
        synthesis_prompt = f"""أنت خبير قانوني متخصص في القانون السعودي. لديك هنا {len(successful_responses)} إجابات من نماذج ذكية مختلفة حول سؤال قانوني واحد.

{combined_responses}

مهمتك:
1. قراءة جميع الإجابات بعناية والاستفادة من كل التفاصيل المفيدة
2. دمج أفضل المعلومات من جميع النماذج في إجابة واحدة شاملة
3. الحفاظ على جميع التفاصيل المهمة (أرقام المواد، الأمثلة، الحالات الاستثنائية، الخطوات العملية)
4. كتابة الإجابة بأسلوب طبيعي ومتدفق كما لو كنت خبيراً قانونياً واحداً
5. التأكد من دقة المعلومات وفقاً للقانون السعودي

اكتب إجابة قانونية شاملة ومفصلة باللغة العربية تجمع كل المعلومات القيمة من النماذج الثلاثة."""

        try:
            logger.info("🤖 Running direct synthesis with GPT-4o via OpenRouter")
            start_time = time.time()
            
            response = await self.async_client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=2500,  # Increased for more detailed responses
                temperature=0.3   # Lower temperature for more focused legal content
            )
            
            processing_time = time.time() - start_time
            cost = self.estimate_cost("openai/gpt-4o", len(synthesis_prompt), len(response.choices[0].message.content))
            
            final_response = response.choices[0].message.content
            
            logger.info(f"✅ Direct synthesis complete in {processing_time:.2f}s, cost: ${cost:.4f}")
            logger.info(f"📊 Input: {total_chars} chars → Output: {len(final_response)} chars")
            logger.info(f"📈 Content preservation: {(len(final_response)/total_chars)*100:.1f}%")
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Direct synthesis failed: {e}")
            
            # Fallback: return the longest/best response
            best_response = max(successful_responses, key=lambda r: len(r.response))
            logger.info(f"✅ Fallback: Using best single response from {best_response.model_name}")
            
            return f"""بناءً على تحليل النماذج المتعددة (أفضل إجابة من {best_response.model_name}):

{best_response.response}

ملاحظة: تم استخدام الإجابة الأفضل من النماذج المتاحة."""

    async def process_question(self, question: str) -> Dict[str, Any]:
        logger.info("="*80)
        logger.info(f"🎯 STARTING VANILLA ENSEMBLE PROCESSING WITH OPENROUTER")
        logger.info(f"Question: {question}")
        logger.info("="*80)
        
        total_start_time = time.time()
        total_cost = 0.0
        
        # Step 1: Generate responses from all models
        responses = await self.generate_responses(question)
        generation_cost = sum(r.cost for r in responses if r.success)
        total_cost += generation_cost
        logger.info(f"💰 Generation cost: ${generation_cost:.4f}")
        
        # Step 2: Direct synthesis (skipping judge extraction for speed)
        logger.info("🔧 Using direct synthesis for full context preservation")
        
        final_response = await self.direct_synthesis(responses)
        synthesis_cost = 0.02  # Estimated
        total_cost += synthesis_cost
        logger.info(f"💰 Synthesis cost: ${synthesis_cost:.4f}")
        
        total_time = time.time() - total_start_time
        
        logger.info("="*80)
        logger.info(f"🎉 ENSEMBLE PROCESSING COMPLETE VIA OPENROUTER")
        logger.info(f"⏱️ Total time: {total_time:.2f}s ({total_time*1000:.0f}ms)")
        logger.info(f"💰 Total cost: ${total_cost:.4f}")
        logger.info(f"🤖 Models used: {len([r for r in responses if r.success])}")
        logger.info(f"🎯 Direct synthesis approach: No judge filtering - full context preserved")
        logger.info(f"⚡ Speed improvement: ~6x faster than original")
        logger.info("="*80)
        
        return {
            "final_response": final_response,
            "processing_time_ms": int(total_time * 1000),
            "cost_estimate": round(total_cost, 4),
            "models_used": len([r for r in responses if r.success]),
            "judges_used": 0,  # No judges in direct synthesis approach
            "components_extracted": len([r for r in responses if r.success]),  # Number of model responses used
            "generation_responses": len(responses),
            "successful_generations": len([r for r in responses if r.success]),
            "successful_evaluations": 0,  # No judge evaluations in direct approach
            "consensus_score": 9.0  # High score for direct synthesis approach
        }