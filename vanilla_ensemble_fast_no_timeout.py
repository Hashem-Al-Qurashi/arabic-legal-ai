"""Fast OpenRouter ensemble - NO TIMEOUTS, replacing DeepSeek with Claude"""

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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FastEnsemble')

@dataclass
class ModelResponse:
    model_name: str
    response: str
    cost: float
    response_time: float
    success: bool
    error: str = None

class FastEnsemble:
    def __init__(self):
        logger.info("🚀 Initializing Fast Ensemble (No Timeouts)")
        
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        self.async_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # Fast models - replacing slow DeepSeek with Claude
        self.generation_models = [
            "openai/gpt-4o",
            "anthropic/claude-3.5-haiku",  # Replaces DeepSeek
            "google/gemini-2.5-flash"
        ]
        
        logger.info(f"✅ System ready with {len(self.generation_models)} models")

    async def call_model(self, model: str, prompt: str) -> ModelResponse:
        """Call model WITHOUT timeout - let it complete naturally"""
        logger.info(f"🤖 Calling {model}")
        start_time = time.time()
        
        try:
            # NO TIMEOUT - wait for full response
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,  # Full token limit
                temperature=0.3
            )
            
            response_time = time.time() - start_time
            content = response.choices[0].message.content
            
            # Estimate cost
            input_chars = len(prompt) / 4
            output_chars = len(content) / 4
            
            costs = {
                "openai/gpt-4o": 0.005/1000,
                "anthropic/claude-3.5-haiku": 0.0008/1000,
                "google/gemini-2.5-flash": 0.00075/1000
            }
            
            cost_rate = costs.get(model, 0.001/1000)
            cost = (input_chars + output_chars) * cost_rate
            
            logger.info(f"✅ {model} completed in {response_time:.2f}s ({len(content)} chars)")
            
            return ModelResponse(
                model_name=model,
                response=content,
                cost=cost,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ {model} failed after {response_time:.2f}s: {str(e)[:100]}")
            return ModelResponse(
                model_name=model,
                response="",
                cost=0.0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    async def generate_responses(self, question: str) -> List[ModelResponse]:
        """Generate responses from all models in parallel"""
        logger.info("📝 Starting parallel generation (no timeouts)")
        
        # Original vanilla ensemble prompt
        saudi_prompt = f"""Answer this question based on Saudi law and regulations. Provide a comprehensive legal response:

{question}

Please provide your answer based on Saudi legal framework, including relevant laws, regulations, and procedures."""
        
        # Launch all models in parallel
        tasks = [self.call_model(model, saudi_prompt) for model in self.generation_models]
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful = [r for r in responses if r.success]
        logger.info(f"✅ Generation complete in {total_time:.2f}s ({len(successful)}/{len(responses)} succeeded)")
        
        for r in responses:
            if r.success:
                logger.info(f"  • {r.model_name}: {r.response_time:.2f}s, {len(r.response)} chars")
        
        return responses

    async def direct_synthesis(self, responses: List[ModelResponse]) -> str:
        """Direct synthesis like original vanilla ensemble"""
        logger.info("🔧 Starting direct synthesis")
        
        successful_responses = [r for r in responses if r.success]
        if not successful_responses:
            return "لم يتم الحصول على إجابات صالحة من النماذج."
        
        # Combine all responses
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
            logger.info("🤖 Running synthesis with GPT-4o")
            start_time = time.time()
            
            # NO TIMEOUT on synthesis either
            response = await self.async_client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=2500,
                temperature=0.3
            )
            
            processing_time = time.time() - start_time
            final_response = response.choices[0].message.content
            
            logger.info(f"✅ Synthesis complete in {processing_time:.2f}s")
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Synthesis failed: {e}")
            # Fallback: return the longest response
            best_response = max(successful_responses, key=lambda r: len(r.response))
            return best_response.response

    async def process_question(self, question: str) -> Dict:
        """Main processing function"""
        logger.info("="*80)
        logger.info(f"🎯 PROCESSING: {question}")
        logger.info("="*80)
        
        total_start = time.time()
        
        # Step 1: Generate responses from all models
        responses = await self.generate_responses(question)
        generation_cost = sum(r.cost for r in responses if r.success)
        
        # Step 2: Direct synthesis
        final_response = await self.direct_synthesis(responses)
        synthesis_cost = 0.02  # Estimated
        
        total_time = time.time() - total_start
        total_cost = generation_cost + synthesis_cost
        
        logger.info("="*80)
        logger.info(f"✅ COMPLETE")
        logger.info(f"⏱️  Total time: {total_time:.2f}s")
        logger.info(f"💰 Total cost: ${total_cost:.4f}")
        logger.info(f"🤖 Models used: {len([r for r in responses if r.success])}/{len(responses)}")
        logger.info(f"📄 Response length: {len(final_response)} chars")
        logger.info("="*80)
        
        return {
            "final_response": final_response,
            "processing_time_ms": int(total_time * 1000),
            "cost_estimate": round(total_cost, 4),
            "models_used": len([r for r in responses if r.success]),
            "generation_responses": len(responses),
            "successful_generations": len([r for r in responses if r.success]),
            "response_details": {
                model.model_name: {
                    "time": model.response_time,
                    "chars": len(model.response),
                    "success": model.success
                }
                for model in responses
            }
        }

# Test function
async def test_fast_ensemble():
    print("\n🚀 Testing Fast Ensemble (No Timeouts)\n")
    
    ensemble = FastEnsemble()
    
    # Test questions
    questions = [
        "ما هي عقوبة التهرب الضريبي في السعودية وما هي الإجراءات القانونية المتبعة؟",
        "ما هي أحكام الحضانة في القانون السعودي؟"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {question[:50]}...")
        print('='*60)
        
        result = await ensemble.process_question(question)
        
        print(f"\n📊 Results:")
        print(f"  • Time: {result['processing_time_ms']/1000:.2f}s")
        print(f"  • Cost: ${result['cost_estimate']}")
        print(f"  • Models: {result['successful_generations']}/{result['generation_responses']}")
        print(f"  • Response: {len(result['final_response'])} chars")
        
        print(f"\n📈 Model Performance:")
        for model_name, details in result['response_details'].items():
            if details['success']:
                print(f"  • {model_name}: {details['time']:.2f}s, {details['chars']} chars ✅")
            else:
                print(f"  • {model_name}: Failed ❌")
        
        print(f"\n📝 Response Preview:")
        print(f"{result['final_response'][:300]}...")
        
        if i == 1:  # After first test
            print(f"\n⚡ Comparison:")
            print(f"  • Original system (with DeepSeek): ~53 seconds")
            print(f"  • This system (with Claude): {result['processing_time_ms']/1000:.2f} seconds")
            improvement = 53 / (result['processing_time_ms']/1000)
            print(f"  • Speed improvement: {improvement:.1f}x faster!")

if __name__ == "__main__":
    os.environ['OPENROUTER_API_KEY'] = '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'
    asyncio.run(test_fast_ensemble())