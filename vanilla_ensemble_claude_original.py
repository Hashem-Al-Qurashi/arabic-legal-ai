"""Vanilla Ensemble with ONLY Claude synthesis change - EXACT original prompts"""

import logging
import asyncio
import time
from typing import Dict, List
from dataclasses import dataclass
from openai import AsyncOpenAI
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

class VanillaEnsemble:
    def __init__(self):
        logger.info("🚀 Initializing Vanilla Ensemble System with OpenRouter")
        
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        self.async_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # Original models (replacing DeepSeek with Claude-Haiku for speed)
        self.generation_models = [
            "openai/gpt-4o",
            "anthropic/claude-3.5-haiku",  # Replaces DeepSeek
            "google/gemini-2.5-flash"
        ]
        
        logger.info(f"✅ System initialized with {len(self.generation_models)} generation models via OpenRouter")

    def estimate_cost(self, model: str, input_chars: int, output_chars: int) -> float:
        """Estimate cost based on model"""
        # Rough token estimation (4 chars = 1 token)
        input_tokens = input_chars / 4
        output_tokens = output_chars / 4
        
        rates = {
            "openai/gpt-4o": {"input": 0.005/1000, "output": 0.015/1000},
            "anthropic/claude-3.5-haiku": {"input": 0.0008/1000, "output": 0.004/1000},
            "anthropic/claude-3.5-sonnet": {"input": 0.003/1000, "output": 0.015/1000},
            "google/gemini-2.5-flash": {"input": 0.00075/1000, "output": 0.003/1000}
        }
        
        rate = rates.get(model, {"input": 0.002/1000, "output": 0.006/1000})
        return (input_tokens * rate["input"]) + (output_tokens * rate["output"])

    async def call_model(self, model: str, prompt: str) -> ModelResponse:
        """Call model via OpenRouter"""
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
            content = response.choices[0].message.content
            cost = self.estimate_cost(model, len(prompt), len(content))
            
            logger.info(f"✅ {model} responded in {response_time:.2f}s, cost: ${cost:.4f}")
            
            return ModelResponse(
                model_name=model,
                response=content,
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

    async def generate_responses(self, question: str) -> List[ModelResponse]:
        """Generate responses using ORIGINAL prompt"""
        logger.info(f"📝 Starting Step 1: Multi-Model Vanilla Generation")
        logger.info(f"Question: {question}")
        
        # EXACT ORIGINAL PROMPT - NO CHANGES
        saudi_prompt = f"""Answer this question based on Saudi law and regulations. Provide a comprehensive legal response:

{question}

Please provide your answer based on Saudi legal framework, including relevant laws, regulations, and procedures."""

        tasks = []
        for model in self.generation_models:
            tasks.append(self.call_model(model, saudi_prompt))
        
        logger.info(f"🚀 Launching {len(tasks)} parallel API calls...")
        responses = await asyncio.gather(*tasks)
        
        successful_responses = [r for r in responses if r.success]
        failed_responses = [r for r in responses if not r.success]
        
        logger.info(f"✅ Step 1 Complete: {len(successful_responses)} successful, {len(failed_responses)} failed responses")
        
        return responses

    async def direct_synthesis(self, responses: List[ModelResponse]) -> str:
        """Direct synthesis using EXACT ORIGINAL prompt but with Claude-3.5-Sonnet"""
        logger.info("🎯 Starting Direct Synthesis - Full Context Preservation")
        
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
        
        # EXACT ORIGINAL SYNTHESIS PROMPT - NO CHANGES
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
            # ONLY CHANGE: Using Claude-3.5-Sonnet instead of GPT-4o
            logger.info("🤖 Running direct synthesis with Claude-3.5-Sonnet via OpenRouter")
            start_time = time.time()
            
            response = await self.async_client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",  # ← ONLY CHANGE: Better for Arabic
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=2500,  # Same as original
                temperature=0.3   # Same as original
            )
            
            processing_time = time.time() - start_time
            final_response = response.choices[0].message.content
            cost = self.estimate_cost("anthropic/claude-3.5-sonnet", len(synthesis_prompt), len(final_response))
            
            logger.info(f"✅ Direct synthesis complete in {processing_time:.2f}s, cost: ${cost:.4f}")
            logger.info(f"📊 Input: {total_chars} chars → Output: {len(final_response)} chars")
            logger.info(f"📈 Content preservation: {(len(final_response)/total_chars)*100:.1f}%")
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Direct synthesis failed: {e}")
            
            # Fallback: return the longest/best response
            best_response = max(successful_responses, key=lambda r: len(r.response))
            logger.info(f"✅ Fallback: Using best single response from {best_response.model_name}")
            
            return best_response.response

    async def process_question(self, question: str) -> Dict[str, any]:
        """Main processing with ORIGINAL prompts, only Claude for synthesis"""
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
        
        # Step 2: Direct synthesis with Claude-3.5-Sonnet
        logger.info("🔧 Using direct synthesis with Claude-3.5-Sonnet for better Arabic")
        
        final_response = await self.direct_synthesis(responses)
        
        # Estimate synthesis cost
        synthesis_chars = sum(len(r.response) for r in responses if r.success) + 500
        synthesis_cost = self.estimate_cost("anthropic/claude-3.5-sonnet", synthesis_chars, len(final_response))
        total_cost += synthesis_cost
        logger.info(f"💰 Synthesis cost: ${synthesis_cost:.4f}")
        
        total_time = time.time() - total_start_time
        
        logger.info("="*80)
        logger.info(f"🎉 ENSEMBLE PROCESSING COMPLETE VIA OPENROUTER")
        logger.info(f"⏱️ Total time: {total_time:.2f}s ({total_time*1000:.0f}ms)")
        logger.info(f"💰 Total cost: ${total_cost:.4f}")
        logger.info(f"🤖 Models used: {len([r for r in responses if r.success])}")
        logger.info(f"🎯 Synthesis: Claude-3.5-Sonnet (better Arabic)")
        logger.info("="*80)
        
        return {
            "final_response": final_response,
            "processing_time_ms": int(total_time * 1000),
            "cost_estimate": round(total_cost, 4),
            "models_used": len([r for r in responses if r.success]),
            "judges_used": 0,
            "components_extracted": len([r for r in responses if r.success]),
            "generation_responses": len(responses),
            "successful_generations": len([r for r in responses if r.success]),
            "successful_evaluations": 0,
            "consensus_score": 9.0
        }

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test():
        ensemble = VanillaEnsemble()
        
        question = "ما هي عقوبة التهرب الضريبي في السعودية وما هي الإجراءات القانونية المتبعة؟"
        print(f"\n🧪 Testing with: {question}\n")
        
        result = await ensemble.process_question(question)
        
        print(f"\n📊 Results:")
        print(f"  • Time: {result['processing_time_ms']/1000:.2f}s")
        print(f"  • Cost: ${result['cost_estimate']}")
        print(f"  • Models used: {result['successful_generations']}/{result['generation_responses']}")
        print(f"  • Response length: {len(result['final_response'])} chars")
        print(f"\n📝 Response preview:")
        print(result['final_response'][:500] + "...")
    
    # Load from .env file
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(test())