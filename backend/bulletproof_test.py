#!/usr/bin/env python3
"""
🧠 ELITE LEGAL INFERENCE TESTING FRAMEWORK
=========================================

Tests EXACTLY the inference failures identified in expert review:
- Context-to-Article connection capability
- Legal judgment formation
- Authority language generation
- Cross-document reasoning

NO HARDCODING - Pure intelligence measurement
"""

import asyncio
import aiohttp
import json
import time
import uuid
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InferenceType(Enum):
    CONTEXT_TO_ARTICLE = "context_to_article"
    LEGAL_JUDGMENT = "legal_judgment" 
    AUTHORITY_LANGUAGE = "authority_language"
    CROSS_DOCUMENT = "cross_document"

@dataclass
class InferenceTest:
    """Single inference capability test"""
    id: str
    query: str
    inference_type: InferenceType
    expected_article: str
    expected_judgment: str
    expected_authority_words: List[str]
    context_clues: List[str]  # What should trigger the inference
    description: str

@dataclass
class InferenceResult:
    """Test result with detailed analysis"""
    test_id: str
    query: str
    response: str
    response_time: float
    
    # Inference Capabilities
    article_connected: bool
    judgment_formed: bool
    authority_language_used: bool
    context_synthesized: bool
    
    # Detailed Analysis
    found_articles: List[str]
    authority_words_found: List[str]
    judgment_strength: str  # "none", "weak", "moderate", "strong"
    inference_score: float  # 0-100
    
    # Failure Analysis
    missing_connections: List[str]
    weak_areas: List[str]

class EliteLegalInferenceTester:
    """Tests legal inference capabilities with surgical precision"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    def create_inference_tests(self) -> List[InferenceTest]:
        """Create tests based on expert review failures"""
        return [
            # EXACT FAILURES FROM EXPERT REVIEW
            InferenceTest(
                id="CONTEXT_001",
                query="عقد بالإنجليزية فقط مع نسخة عربية غير رسمية. ما الحكم القانوني؟",
                inference_type=InferenceType.CONTEXT_TO_ARTICLE,
                expected_article="المادة 9",
                expected_judgment="باطل",
                expected_authority_words=["باطل", "غير معتمد قانونياً", "النسخة الرسمية"],
                context_clues=["لغة أجنبية", "عقد", "عربية غير رسمية"],
                description="Contract language requirement inference - Expert said system failed to connect to Article 9"
            ),
            
            InferenceTest(
                id="CONTEXT_002", 
                query="تم حسم 60% من أجر عامل دون موافقة كتابية. هل هذا قانوني؟",
                inference_type=InferenceType.CONTEXT_TO_ARTICLE,
                expected_article="المادة 93",
                expected_judgment="غير قانوني",
                expected_authority_words=["لا يزيد على النصف", "غير قانوني", "مخالفة"],
                context_clues=["حسم", "60%", "أجر", "موافقة كتابية"],
                description="Wage deduction limits - Expert said system mentioned half but didn't cite article"
            ),
            
            InferenceTest(
                id="CONTEXT_003",
                query="عامل عمره سنة وعشرة أشهر يعمل في منجم. هل هذا قانوني؟",
                inference_type=InferenceType.CONTEXT_TO_ARTICLE, 
                expected_article="المادة 86",
                expected_judgment="غير قانوني",
                expected_authority_words=["ممنوع", "لا يجوز", "العمل الخطر"],
                context_clues=["منجم", "سن", "عمل خطر"],
                description="Age restrictions for dangerous work - Expert said system failed to mention mining/dangerous work"
            ),
            
            InferenceTest(
                id="CONTEXT_004",
                query="ما الفرق بين الإيقاف عن العمل والفصل من حيث الأثر القانوني؟",
                inference_type=InferenceType.CROSS_DOCUMENT,
                expected_article="المادة 75",
                expected_judgment="فروق جوهرية",
                expected_authority_words=["إيقاف مؤقت", "فصل نهائي", "استمرار العلاقة"],
                context_clues=["إيقاف", "فصل", "أثر قانوني"],
                description="Legal consequence differentiation - Expert said system described but didn't cite article"
            ),
            
            # AUTHORITY LANGUAGE TESTS
            InferenceTest(
                id="AUTHORITY_001",
                query="شركة تضع عقود عمل بالإنجليزية فقط. ما الحكم؟",
                inference_type=InferenceType.AUTHORITY_LANGUAGE,
                expected_article="المادة 9", 
                expected_judgment="باطل",
                expected_authority_words=["باطل", "مخالفة", "غير معتمد"],
                context_clues=["عقود", "إنجليزية فقط"],
                description="Test if system uses definitive legal language vs descriptive language"
            ),
            
            InferenceTest(
                id="AUTHORITY_002",
                query="مفتش عمل يطلب أخذ عينات من شركة كيميائية. هل يمكن الرفض؟",
                inference_type=InferenceType.AUTHORITY_LANGUAGE,
                expected_article="المادة 129",
                expected_judgment="لا يمكن الرفض",
                expected_authority_words=["لا يمكن الرفض", "إلزامي", "صلاحية المفتش"],
                context_clues=["مفتش", "عينات", "شركة كيميائية"],
                description="Test if system gives definitive answer vs 'المفتش لديه صلاحيات'"
            ),
            
            # CROSS-DOCUMENT REASONING TESTS
            InferenceTest(
                id="CROSS_001",
                query="المنشآت ذات المخاطر الكبرى والتفتيش العمالي - ما العلاقة؟",
                inference_type=InferenceType.CROSS_DOCUMENT,
                expected_article="المادة 28+29+30",
                expected_judgment="أولوية في التفتيش",
                expected_authority_words=["أولوية", "تفتيش مشدد", "منشآت خطرة"],
                context_clues=["منشآت خطرة", "تفتيش"],
                description="Expert said system failed to connect hazardous facilities with inspection priority"
            )
        ]
    
    async def run_inference_tests(self) -> Dict[str, Any]:
        """Run complete inference testing suite"""
        logger.info("🧠 STARTING ELITE LEGAL INFERENCE TESTING")
        logger.info("🎯 Testing exact failures from expert review")
        
        tests = self.create_inference_tests()
        results = []
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            for i, test in enumerate(tests, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"🧪 TEST {i}/{len(tests)}: {test.id}")
                logger.info(f"📋 TYPE: {test.inference_type.value}")
                logger.info(f"❓ QUERY: {test.query}")
                logger.info(f"📖 DESCRIPTION: {test.description}")
                
                result = await self.execute_inference_test(test)
                results.append(result)
                
                self.log_inference_result(result)
                await asyncio.sleep(1)
        
        # Calculate overall inference capabilities
        inference_analysis = self.analyze_inference_capabilities(results)
        
        return {
            "test_results": results,
            "inference_analysis": inference_analysis,
            "recommendations": self.generate_recommendations(inference_analysis)
        }
    
    async def execute_inference_test(self, test: InferenceTest) -> InferenceResult:
        """Execute single inference test with detailed analysis"""
        start_time = time.time()
        
        try:
            response = await self.query_legal_system(test.query)
            response_time = time.time() - start_time
            
            # Analyze inference capabilities
            analysis = self.analyze_response_inference(test, response)
            
            return InferenceResult(
                test_id=test.id,
                query=test.query,
                response=response,
                response_time=response_time,
                article_connected=analysis["article_connected"],
                judgment_formed=analysis["judgment_formed"], 
                authority_language_used=analysis["authority_language_used"],
                context_synthesized=analysis["context_synthesized"],
                found_articles=analysis["found_articles"],
                authority_words_found=analysis["authority_words_found"],
                judgment_strength=analysis["judgment_strength"],
                inference_score=analysis["inference_score"],
                missing_connections=analysis["missing_connections"],
                weak_areas=analysis["weak_areas"]
            )
            
        except Exception as e:
            return InferenceResult(
                test_id=test.id,
                query=test.query,
                response=f"ERROR: {str(e)}",
                response_time=time.time() - start_time,
                article_connected=False,
                judgment_formed=False,
                authority_language_used=False,
                context_synthesized=False,
                found_articles=[],
                authority_words_found=[],
                judgment_strength="none",
                inference_score=0.0,
                missing_connections=["System error"],
                weak_areas=["Complete failure"]
            )
    
    async def query_legal_system(self, question: str) -> str:
        """Query the legal AI system"""
        url = f"{self.base_url}/api/chat/message"
        
        form_data = aiohttp.FormData()
        form_data.add_field('message', question)
        form_data.add_field('session_id', f"test_session_{uuid.uuid4().hex[:8]}")
        
        headers = {'Accept': 'text/event-stream'}
        
        async with self.session.post(url, data=form_data, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API error: {response.status} - {error_text}")
            
            content = ""
            async for line in response.content:
                if line:
                    try:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith('data: '):
                            data = decoded[6:]
                            if data != '[DONE]':
                                try:
                                    parsed = json.loads(data)
                                    if parsed.get('type') == 'chunk' and 'content' in parsed:
                                        content += parsed['content']
                                except json.JSONDecodeError:
                                    content += data
                    except:
                        continue
            
            return content.strip() if content else "No response received"
    
    def analyze_response_inference(self, test: InferenceTest, response: str) -> Dict[str, Any]:
        """Analyze response for inference capabilities"""
        response_lower = response.lower()
        
        # 1. Article Connection Analysis
        found_articles = self.extract_articles(response)
        expected_article_found = any(test.expected_article.lower() in article.lower() 
                                   for article in found_articles)
        article_connected = expected_article_found or test.expected_article.lower() in response_lower
        
        # 2. Authority Language Analysis
        authority_words_found = [word for word in test.expected_authority_words 
                               if word.lower() in response_lower]
        authority_language_used = len(authority_words_found) > 0
        
        # 3. Judgment Formation Analysis
        judgment_indicators = ["باطل", "غير قانوني", "ممنوع", "لا يجوز", "إلزامي", "واجب"]
        judgment_words_found = [word for word in judgment_indicators if word in response_lower]
        judgment_formed = len(judgment_words_found) > 0
        
        # Judgment strength assessment
        if test.expected_judgment.lower() in response_lower:
            judgment_strength = "strong"
        elif judgment_words_found:
            judgment_strength = "moderate" 
        elif any(word in response_lower for word in ["يُفضل", "يُمكن", "ربما"]):
            judgment_strength = "weak"
        else:
            judgment_strength = "none"
        
        # 4. Context Synthesis Analysis
        context_clues_found = [clue for clue in test.context_clues 
                             if clue.lower() in response_lower]
        context_synthesized = len(context_clues_found) >= len(test.context_clues) // 2
        
        # 5. Missing Connections
        missing_connections = []
        if not article_connected:
            missing_connections.append(f"Missing connection to {test.expected_article}")
        if not authority_language_used:
            missing_connections.append("Missing authoritative language")
        if not judgment_formed:
            missing_connections.append("No clear legal judgment")
        
        # 6. Weak Areas
        weak_areas = []
        if judgment_strength in ["weak", "none"]:
            weak_areas.append("Weak or missing legal judgment")
        if len(authority_words_found) < len(test.expected_authority_words) // 2:
            weak_areas.append("Insufficient authoritative language")
        if not context_synthesized:
            weak_areas.append("Poor context synthesis")
        
        # 7. Overall Inference Score
        score = 0
        if article_connected: score += 30
        if judgment_formed: score += 25
        if authority_language_used: score += 25
        if context_synthesized: score += 20
        
        return {
            "article_connected": article_connected,
            "judgment_formed": judgment_formed,
            "authority_language_used": authority_language_used,
            "context_synthesized": context_synthesized,
            "found_articles": found_articles,
            "authority_words_found": authority_words_found,
            "judgment_strength": judgment_strength,
            "inference_score": score,
            "missing_connections": missing_connections,
            "weak_areas": weak_areas
        }
    
    def extract_articles(self, text: str) -> List[str]:
        """Extract article references from text"""
        patterns = [
            r'المادة\s*\(?\s*(\d+)\s*\)?',
            r'وفقاً\s+للمادة\s+(\d+)',
            r'استناداً\s+للمادة\s+(\d+)',
            r'بموجب\s+المادة\s+(\d+)'
        ]
        
        articles = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                articles.append(f"المادة {match}")
        
        return list(set(articles))
    
    def analyze_inference_capabilities(self, results: List[InferenceResult]) -> Dict[str, Any]:
        """Analyze overall inference capabilities"""
        total_tests = len(results)
        
        # Capability metrics
        article_connection_rate = sum(1 for r in results if r.article_connected) / total_tests * 100
        judgment_formation_rate = sum(1 for r in results if r.judgment_formed) / total_tests * 100
        authority_language_rate = sum(1 for r in results if r.authority_language_used) / total_tests * 100
        context_synthesis_rate = sum(1 for r in results if r.context_synthesized) / total_tests * 100
        
        # Average inference score
        avg_inference_score = sum(r.inference_score for r in results) / total_tests
        
        # Most common weaknesses
        all_weak_areas = []
        for result in results:
            all_weak_areas.extend(result.weak_areas)
        
        weakness_counts = {}
        for weakness in all_weak_areas:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        top_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "overall_inference_score": avg_inference_score,
            "article_connection_rate": article_connection_rate,
            "judgment_formation_rate": judgment_formation_rate, 
            "authority_language_rate": authority_language_rate,
            "context_synthesis_rate": context_synthesis_rate,
            "top_weaknesses": top_weaknesses[:3],
            "total_tests": total_tests,
            "failed_tests": len([r for r in results if r.inference_score < 70])
        }
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on test results"""
        recommendations = []
        
        if analysis["article_connection_rate"] < 70:
            recommendations.append("🔗 CRITICAL: Implement cross-document article connection system")
        
        if analysis["judgment_formation_rate"] < 70:
            recommendations.append("⚖️ CRITICAL: Enhance legal judgment formation capabilities")
            
        if analysis["authority_language_rate"] < 70:
            recommendations.append("💪 CRITICAL: Implement authoritative legal language generation")
            
        if analysis["context_synthesis_rate"] < 70:
            recommendations.append("🧠 CRITICAL: Improve context synthesis across multiple documents")
        
        # Specific recommendations based on weaknesses
        top_weaknesses = analysis.get("top_weaknesses", [])
        for weakness, count in top_weaknesses:
            if "judgment" in weakness.lower():
                recommendations.append("📋 Implement legal judgment confidence calibration")
            elif "language" in weakness.lower():
                recommendations.append("🗣️ Add authoritative legal language templates")
            elif "synthesis" in weakness.lower():
                recommendations.append("🔄 Enhance cross-document reasoning capabilities")
        
        return recommendations
    
    def log_inference_result(self, result: InferenceResult):
        """Log detailed inference test result"""
        logger.info(f"⏱️  Response Time: {result.response_time:.2f}s")
        logger.info(f"📊 Inference Score: {result.inference_score:.1f}/100")
        logger.info(f"🔗 Article Connected: {'✅' if result.article_connected else '❌'}")
        logger.info(f"⚖️  Judgment Formed: {'✅' if result.judgment_formed else '❌'}")
        logger.info(f"💪 Authority Language: {'✅' if result.authority_language_used else '❌'}")
        logger.info(f"🧠 Context Synthesized: {'✅' if result.context_synthesized else '❌'}")
        
        if result.found_articles:
            logger.info(f"📖 Articles Found: {', '.join(result.found_articles)}")
        
        if result.authority_words_found:
            logger.info(f"💬 Authority Words: {', '.join(result.authority_words_found)}")
            
        if result.missing_connections:
            logger.info("❌ Missing Connections:")
            for missing in result.missing_connections:
                logger.info(f"   - {missing}")
        
        logger.info(f"💭 Response Preview: {result.response[:150]}...")

async def main():
    """Run the elite inference testing suite"""
    print("🧠 ELITE LEGAL INFERENCE TESTING FRAMEWORK")
    print("📊 Testing exact inference failures from expert review")
    print("🎯 Measuring legal reasoning capabilities with surgical precision")
    
    tester = EliteLegalInferenceTester()
    results = await tester.run_inference_tests()
    
    # Print final analysis
    analysis = results["inference_analysis"]
    print(f"\n{'='*80}")
    print("🧠 INFERENCE CAPABILITY ANALYSIS")
    print(f"{'='*80}")
    print(f"📊 Overall Inference Score: {analysis['overall_inference_score']:.1f}/100")
    print(f"🔗 Article Connection Rate: {analysis['article_connection_rate']:.1f}%")
    print(f"⚖️  Judgment Formation Rate: {analysis['judgment_formation_rate']:.1f}%")
    print(f"💪 Authority Language Rate: {analysis['authority_language_rate']:.1f}%")
    print(f"🧠 Context Synthesis Rate: {analysis['context_synthesis_rate']:.1f}%")
    
    print(f"\n📋 TOP WEAKNESSES:")
    for weakness, count in analysis["top_weaknesses"]:
        print(f"   - {weakness} ({count} times)")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    for rec in results["recommendations"]:
        print(f"   {rec}")
    
    # Save detailed results
    with open("elite_inference_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: elite_inference_test_results.json")
    
    return analysis["overall_inference_score"] >= 70

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)