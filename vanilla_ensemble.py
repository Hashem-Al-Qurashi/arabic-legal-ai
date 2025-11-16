import logging
import asyncio
import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import openai
import google.generativeai as genai
import requests
import json
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
        logger.info("🚀 Initializing Vanilla Ensemble System")
        
        self.openai_client = None
        self.genai_client = None
        
        self.setup_api_clients()
        
        self.generation_models = [
            "gpt-4o",
            "deepseek-chat", 
            # "grok-2",  # Commented out - no API key available
            "gemini-2.5-flash"
        ]
        
        self.judge_models = [
            # "claude-3-5-sonnet",  # Commented out - no API key available
            "gpt-4o",
            "gemini-2.5-flash"
        ]
        
        logger.info(f"✅ System initialized with {len(self.generation_models)} generation models and {len(self.judge_models)} judge models")

    def setup_api_clients(self):
        logger.info("🔧 Setting up API clients...")
        
        try:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized")
            else:
                logger.warning("⚠️ OpenAI API key not found")
            
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                genai.configure(api_key=gemini_key)
                logger.info("✅ Gemini client initialized")
            else:
                logger.warning("⚠️ Gemini API key not found")
                
        except Exception as e:
            logger.error(f"❌ Error setting up API clients: {e}")

    async def call_openai_model(self, model: str, prompt: str) -> ModelResponse:
        logger.info(f"🤖 Calling OpenAI model: {model}")
        start_time = time.time()
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            
            response_time = time.time() - start_time
            cost = self.estimate_openai_cost(model, len(prompt), len(response.choices[0].message.content))
            
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

    async def call_deepseek_model(self, prompt: str) -> ModelResponse:
        logger.info("🤖 Calling DeepSeek model")
        start_time = time.time()
        
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1500
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            response_time = time.time() - start_time
            cost = 0.04
            
            logger.info(f"✅ DeepSeek responded in {response_time:.2f}s, cost: ${cost:.4f}")
            
            return ModelResponse(
                model_name="deepseek-chat",
                response=result['choices'][0]['message']['content'],
                cost=cost,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ DeepSeek failed after {response_time:.2f}s: {e}")
            
            return ModelResponse(
                model_name="deepseek-chat",
                response="",
                cost=0.0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    async def call_gemini_model(self, prompt: str) -> ModelResponse:
        logger.info("🤖 Calling Gemini model")
        start_time = time.time()
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            response_time = time.time() - start_time
            cost = 0.03
            
            logger.info(f"✅ Gemini responded in {response_time:.2f}s, cost: ${cost:.4f}")
            
            return ModelResponse(
                model_name="gemini-2.5-flash",
                response=response.text,
                cost=cost,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ Gemini failed after {response_time:.2f}s: {e}")
            
            return ModelResponse(
                model_name="gemini-2.5-flash",
                response="",
                cost=0.0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    async def call_grok_model(self, prompt: str) -> ModelResponse:
        logger.info("🤖 Calling Grok model (simulated)")
        start_time = time.time()
        
        await asyncio.sleep(2)
        response_time = time.time() - start_time
        
        logger.info(f"⚠️ Grok simulated response in {response_time:.2f}s")
        
        return ModelResponse(
            model_name="grok-2",
            response="[Grok simulation] Based on Saudi labor law, this requires specific regulatory compliance...",
            cost=0.05,
            response_time=response_time,
            success=True
        )

    def estimate_openai_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        rates = {
            "gpt-4o": {"input": 0.005/1000, "output": 0.015/1000},
            "gpt-4": {"input": 0.03/1000, "output": 0.06/1000}
        }
        
        rate = rates.get(model, rates["gpt-4o"])
        return (input_tokens * rate["input"]) + (output_tokens * rate["output"])

    async def generate_responses(self, question: str) -> List[ModelResponse]:
        logger.info(f"📝 Starting Step 1: Multi-Model Vanilla Generation")
        logger.info(f"Question: {question}")
        
        saudi_prompt = f"""Answer this question based on Saudi law and regulations. Provide a comprehensive legal response:

{question}

Please provide your answer based on Saudi legal framework, including relevant laws, regulations, and procedures."""

        tasks = []
        
        for model in self.generation_models:
            if model == "gpt-4o":
                tasks.append(self.call_openai_model(model, saudi_prompt))
            elif model == "deepseek-chat":
                tasks.append(self.call_deepseek_model(saudi_prompt))
            elif model == "gemini-2.5-flash":
                tasks.append(self.call_gemini_model(saudi_prompt))
            # elif model == "grok-2":  # Commented out - no API key available
            #     tasks.append(self.call_grok_model(saudi_prompt))
        
        logger.info(f"🚀 Launching {len(tasks)} parallel API calls...")
        responses = await asyncio.gather(*tasks)
        
        successful_responses = [r for r in responses if r.success]
        failed_responses = [r for r in responses if not r.success]
        
        logger.info(f"✅ Step 1 Complete: {len(successful_responses)} successful, {len(failed_responses)} failed responses")
        
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
            if judge == "gpt-4o":  # Removed claude-3-5-sonnet - no API key available
                judge_tasks.append(self.judge_with_openai(judge, judge_prompt))
            elif judge == "gemini-2.5-flash":
                judge_tasks.append(self.judge_with_gemini(judge_prompt))
        
        logger.info(f"⚖️ Launching {len(judge_tasks)} judge evaluations...")
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

    async def judge_with_openai(self, model: str, prompt: str) -> JudgeEvaluation:
        logger.info(f"⚖️ Judge evaluation with {model}")
        start_time = time.time()
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a legal expert judge. You MUST respond with ONLY valid JSON. No other text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            processing_time = time.time() - start_time
            cost = self.estimate_openai_cost("gpt-4o", len(prompt), len(response.choices[0].message.content))
            
            content = response.choices[0].message.content.strip()
            logger.info(f"📄 Judge response content: {content[:200]}...")
            
            # Try to extract JSON from response if it contains other text
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

    async def judge_with_gemini(self, prompt: str) -> JudgeEvaluation:
        logger.info("⚖️ Judge evaluation with Gemini")
        start_time = time.time()
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            enhanced_prompt = f"You MUST respond with ONLY valid JSON. No other text. {prompt}"
            response = model.generate_content(enhanced_prompt)
            
            processing_time = time.time() - start_time
            cost = 0.03
            
            content = response.text.strip()
            logger.info(f"📄 Gemini judge response: {content[:200]}...")
            
            # Try to extract JSON from response if it contains other text
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
                judge_name="gemini-2.5-flash",
                best_elements=best_elements,
                processing_time=processing_time,
                cost=cost,
                success=True
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Judge Gemini failed: {e}")
            
            empty_elements = BestElements("", "", "", 0.0)
            return JudgeEvaluation(
                judge_name="gemini-2.5-flash",
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
        logger.info("🔧 Starting Step 4: AI Synthesis")
        
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
            logger.info("🤖 Synthesizing final response with GPT-4o")
            start_time = time.time()
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=1500
            )
            
            processing_time = time.time() - start_time
            cost = self.estimate_openai_cost("gpt-4o", len(synthesis_prompt), len(response.choices[0].message.content))
            
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

    async def process_question(self, question: str) -> Dict[str, Any]:
        logger.info("="*80)
        logger.info(f"🎯 STARTING VANILLA ENSEMBLE PROCESSING")
        logger.info(f"Question: {question}")
        logger.info("="*80)
        
        total_start_time = time.time()
        total_cost = 0.0
        
        responses = await self.generate_responses(question)
        generation_cost = sum(r.cost for r in responses if r.success)
        total_cost += generation_cost
        logger.info(f"💰 Generation cost: ${generation_cost:.4f}")
        
        evaluations = await self.extract_components(responses)
        judging_cost = sum(e.cost for e in evaluations if e.success)
        total_cost += judging_cost
        logger.info(f"💰 Judging cost: ${judging_cost:.4f}")
        
        best_elements = self.consensus_voting(evaluations)
        
        final_response = await self.synthesize_response(best_elements)
        assembly_cost = 0.02
        total_cost += assembly_cost
        logger.info(f"💰 Assembly cost: ${assembly_cost:.4f}")
        
        total_time = time.time() - total_start_time
        
        logger.info("="*80)
        logger.info(f"🎉 ENSEMBLE PROCESSING COMPLETE")
        logger.info(f"⏱️ Total time: {total_time:.2f}s ({total_time*1000:.0f}ms)")
        logger.info(f"💰 Total cost: ${total_cost:.4f}")
        logger.info(f"🤖 Models used: {len([r for r in responses if r.success])}")
        logger.info(f"⚖️ Judges used: {len([e for e in evaluations if e.success])}")
        logger.info("="*80)
        
        return {
            "final_response": final_response,
            "processing_time_ms": int(total_time * 1000),
            "cost_estimate": round(total_cost, 4),
            "models_used": len([r for r in responses if r.success]),
            "judges_used": len([e for e in evaluations if e.success]),
            "components_extracted": len([e for e in evaluations if e.success]) * 3,  # 3 elements per successful judge
            "generation_responses": len(responses),
            "successful_generations": len([r for r in responses if r.success]),
            "successful_evaluations": len([e for e in evaluations if e.success]),
            "consensus_score": round(best_elements.get('avg_score', 0), 1)
        }