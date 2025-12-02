"""Optimized OpenRouter ensemble - FAST version without DeepSeek"""

import logging
import asyncio
import time
from typing import Dict, List
from dataclasses import dataclass
import openai
from openai import AsyncOpenAI
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OptimizedEnsemble')

@dataclass
class ModelResponse:
    model_name: str
    response: str
    cost: float
    response_time: float
    success: bool
    error: str = None

class OptimizedEnsemble:
    def __init__(self):
        logger.info("🚀 Initializing OPTIMIZED Ensemble (Fast Version)")
        
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        self.async_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # OPTIMIZED: Remove slow DeepSeek, add fast Claude
        self.generation_models = [
            "openai/gpt-4o",              # 3-9s
            "anthropic/claude-3.5-haiku", # 2-6s (replaces DeepSeek)
            "google/gemini-2.5-flash"     # 1-9s
        ]
        
        logger.info(f"✅ Optimized system ready with {len(self.generation_models)} fast models")

    async def call_model(self, model: str, prompt: str) -> ModelResponse:
        """Call model with timeout protection"""
        logger.info(f"🤖 Calling {model}")
        start_time = time.time()
        
        try:
            # Add timeout - don't wait more than 15 seconds for any model
            response = await asyncio.wait_for(
                self.async_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,  # Reduced from 1500
                    temperature=0.3
                ),
                timeout=15.0  # 15 second timeout
            )
            
            response_time = time.time() - start_time
            content = response.choices[0].message.content
            
            # Simple cost estimation
            cost = len(content) * 0.000001  # Simplified
            
            logger.info(f"✅ {model} done in {response_time:.2f}s ({len(content)} chars)")
            
            return ModelResponse(
                model_name=model,
                response=content,
                cost=cost,
                response_time=response_time,
                success=True
            )
            
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            logger.warning(f"⏱️ {model} timed out after {response_time:.2f}s")
            return ModelResponse(
                model_name=model,
                response="",
                cost=0.0,
                response_time=response_time,
                success=False,
                error="Timeout"
            )
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ {model} failed: {str(e)[:50]}")
            return ModelResponse(
                model_name=model,
                response="",
                cost=0.0,
                response_time=response_time,
                success=False,
                error=str(e)[:100]
            )

    async def generate_responses_fast(self, question: str) -> List[ModelResponse]:
        """Generate responses with smart optimization"""
        logger.info("⚡ Fast parallel generation starting...")
        
        # Simpler, more direct prompt
        prompt = f"""أنت خبير قانوني سعودي. أجب على هذا السؤال بشكل شامل ومفصل:

{question}

اذكر القوانين والعقوبات والإجراءات المطبقة في السعودية."""
        
        # Launch all models in parallel
        tasks = [self.call_model(model, prompt) for model in self.generation_models]
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful = [r for r in responses if r.success]
        logger.info(f"⚡ Generation complete in {total_time:.2f}s ({len(successful)}/{len(responses)} succeeded)")
        
        return responses

    async def fast_synthesis(self, responses: List[ModelResponse]) -> str:
        """Ultra-fast synthesis - no API call needed"""
        successful = [r for r in responses if r.success and len(r.response) > 100]
        
        if not successful:
            return "عذراً، لم نتمكن من الحصول على إجابة مناسبة."
        
        # Option 1: Return best (longest) response immediately
        best = max(successful, key=lambda r: len(r.response))
        
        # Option 2: Simple combination without API call
        if len(successful) >= 2:
            combined = f"""بناءً على تحليل قانوني شامل:

{best.response}

معلومات إضافية:
{successful[1].response if len(successful) > 1 else ''}"""
            return combined
        
        return best.response

    async def smart_synthesis(self, responses: List[ModelResponse]) -> str:
        """Smarter synthesis with API call but optimized"""
        successful = [r for r in responses if r.success]
        
        if not successful:
            return "عذراً، لم نتمكن من الحصول على إجابة."
        
        if len(successful) == 1:
            return successful[0].response
        
        # Only synthesize if we have multiple good responses
        combined = "\n---\n".join([f"تحليل {i+1}:\n{r.response}" for i, r in enumerate(successful)])
        
        synthesis_prompt = f"""لديك {len(successful)} تحليلات قانونية. اكتب إجابة واحدة شاملة تجمع أهم المعلومات:

{combined}

اكتب الإجابة النهائية بالعربية:"""
        
        try:
            response = await asyncio.wait_for(
                self.async_client.chat.completions.create(
                    model="openai/gpt-4o",
                    messages=[{"role": "user", "content": synthesis_prompt}],
                    max_tokens=1500,
                    temperature=0.2
                ),
                timeout=10.0  # 10 second timeout for synthesis
            )
            return response.choices[0].message.content
        except:
            # If synthesis fails, return best original
            return successful[0].response

    async def process_question(self, question: str, skip_synthesis: bool = False) -> Dict:
        """Main processing with options"""
        logger.info("="*60)
        logger.info(f"⚡ OPTIMIZED PROCESSING: {question[:50]}...")
        
        total_start = time.time()
        
        # Step 1: Fast parallel generation
        responses = await self.generate_responses_fast(question)
        
        # Step 2: Synthesis (optional)
        if skip_synthesis or len(question) < 30:
            # For simple questions, skip synthesis
            final_response = await self.fast_synthesis(responses)
            logger.info("⚡ Using fast synthesis (no API call)")
        else:
            # For complex questions, do smart synthesis
            final_response = await self.smart_synthesis(responses)
            logger.info("🔧 Using smart synthesis")
        
        total_time = time.time() - total_start
        
        logger.info(f"✅ COMPLETE in {total_time:.2f}s")
        logger.info("="*60)
        
        return {
            "final_response": final_response,
            "processing_time_ms": int(total_time * 1000),
            "cost_estimate": sum(r.cost for r in responses if r.success) + 0.01,
            "models_used": len([r for r in responses if r.success]),
            "generation_responses": len(responses),
            "successful_generations": len([r for r in responses if r.success])
        }

# Test function
async def test_optimized():
    print("\n🚀 Testing OPTIMIZED Ensemble\n")
    
    ensemble = OptimizedEnsemble()
    
    # Test with your question
    question = "ما هي عقوبة التهرب الضريبي في السعودية وما هي الإجراءات القانونية المتبعة؟"
    
    print(f"Question: {question}\n")
    print("Testing 3 modes:\n")
    
    # Mode 1: With synthesis
    print("1️⃣ With Smart Synthesis:")
    result1 = await ensemble.process_question(question, skip_synthesis=False)
    print(f"   Time: {result1['processing_time_ms']/1000:.2f}s")
    print(f"   Response length: {len(result1['final_response'])} chars\n")
    
    # Mode 2: Without synthesis  
    print("2️⃣ Without Synthesis (Fastest):")
    result2 = await ensemble.process_question(question, skip_synthesis=True)
    print(f"   Time: {result2['processing_time_ms']/1000:.2f}s")
    print(f"   Response length: {len(result2['final_response'])} chars\n")
    
    # Mode 3: Simple question
    simple = "ما هي عقوبة السرقة؟"
    print(f"3️⃣ Simple Question: {simple}")
    result3 = await ensemble.process_question(simple, skip_synthesis=True)
    print(f"   Time: {result3['processing_time_ms']/1000:.2f}s")
    print(f"   Response length: {len(result3['final_response'])} chars\n")
    
    print("="*60)
    print("📊 Summary:")
    print(f"  • Original system: ~53 seconds")
    print(f"  • Optimized with synthesis: {result1['processing_time_ms']/1000:.2f}s")
    print(f"  • Optimized no synthesis: {result2['processing_time_ms']/1000:.2f}s")
    print(f"  • Simple questions: {result3['processing_time_ms']/1000:.2f}s")
    
    improvement = 53 / (result2['processing_time_ms']/1000)
    print(f"\n⚡ Speed improvement: {improvement:.1f}x faster!")
    
    return result1

if __name__ == "__main__":
    # Load from .env file
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(test_optimized())