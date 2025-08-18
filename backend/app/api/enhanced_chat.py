"""
Enhanced Chat API with Seamless Quranic Foundation Integration
Zero-downtime upgrade to existing chat system
Backward compatible with enterprise-grade Quranic integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from fastapi import HTTPException
import json

from app.core.retrieval_orchestrator import RetrievalOrchestrator, IntegratedResponse, IntegrationStrategy
from app.storage.quranic_foundation_store import QuranicFoundation
from app.core.semantic_concepts import LegalConcept

logger = logging.getLogger(__name__)


class EnhancedChatProcessor:
    """
    Enhanced chat processor with seamless Quranic foundation integration
    Maintains full backward compatibility with existing chat system
    """
    
    def __init__(self):
        self.orchestrator = RetrievalOrchestrator()
        self.integration_enabled = True
        self.response_enhancement_enabled = True
        
        # Feature flags for gradual rollout
        self.feature_flags = {
            "quranic_integration": True,
            "semantic_concepts": True,
            "intelligent_strategy": True,
            "cultural_adaptation": True,
            "quality_filtering": True
        }
        
        # Performance monitoring
        self.performance_metrics = {
            "total_queries": 0,
            "enhanced_queries": 0,
            "fallback_queries": 0,
            "average_response_time": 0.0,
            "user_satisfaction": 0.0
        }
        
        logger.info("EnhancedChatProcessor initialized with Quranic integration")
    
    async def initialize(self):
        """Initialize the enhanced chat processor"""
        try:
            await self.orchestrator.initialize()
            logger.info("✅ Enhanced chat processor fully initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced chat processor: {e}")
            # Disable integration on failure to maintain service
            self.integration_enabled = False
            raise
    
    async def process_chat_query(self, query: str, 
                               context: Optional[Dict[str, Any]] = None,
                               user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process chat query with enhanced Quranic integration
        Maintains backward compatibility with existing API
        """
        start_time = datetime.now()
        
        try:
            # Prepare enhanced context
            enhanced_context = self._prepare_enhanced_context(query, context, user_preferences)
            
            # Determine if enhancement should be applied
            should_enhance = self._should_enhance_query(query, enhanced_context)
            
            if should_enhance and self.integration_enabled:
                # Enhanced processing with Quranic integration
                response = await self._process_enhanced_query(query, enhanced_context)
                self.performance_metrics["enhanced_queries"] += 1
            else:
                # Fallback to traditional processing
                response = await self._process_traditional_query(query, enhanced_context)
                self.performance_metrics["fallback_queries"] += 1
            
            # Update performance metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_performance_metrics(processing_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Enhanced chat processing failed: {e}")
            # Graceful fallback to ensure service continuity
            return await self._emergency_fallback(query, context)
    
    async def _process_enhanced_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process query with full Quranic integration enhancement"""
        
        # Step 1: Retrieve integrated results
        integrated_response = await self.orchestrator.retrieve_integrated(
            query=query,
            context=context,
            limit=15
        )
        
        # Step 2: Format response for chat API
        formatted_response = await self._format_integrated_response(integrated_response)
        
        # Step 3: Apply cultural and quality enhancements
        enhanced_response = await self._apply_response_enhancements(formatted_response, context)
        
        # Step 4: Add integration metadata
        enhanced_response["enhancement_info"] = {
            "integration_strategy": integrated_response.strategy.value,
            "quranic_sources_count": len(integrated_response.quranic_results),
            "civil_sources_count": len(integrated_response.civil_results),
            "integration_quality": integrated_response.integration_quality,
            "cultural_appropriateness": integrated_response.cultural_appropriateness,
            "processing_time_ms": integrated_response.execution_time_ms
        }
        
        return enhanced_response
    
    async def _format_integrated_response(self, integrated_response: IntegratedResponse) -> Dict[str, Any]:
        """Format integrated response for chat API compatibility"""
        
        # Build enhanced answer
        answer_parts = []
        
        # Strategy-based response formatting
        if integrated_response.strategy == IntegrationStrategy.FOUNDATION_FIRST:
            answer_parts.extend(await self._format_foundation_first_response(integrated_response))
        elif integrated_response.strategy == IntegrationStrategy.CIVIL_WITH_FOUNDATION:
            answer_parts.extend(await self._format_civil_with_foundation_response(integrated_response))
        elif integrated_response.strategy == IntegrationStrategy.CONTEXTUAL_BLEND:
            answer_parts.extend(await self._format_contextual_blend_response(integrated_response))
        else:
            answer_parts.extend(await self._format_civil_only_response(integrated_response))
        
        # Combine answer parts
        full_answer = "\n\n".join(answer_parts)
        
        # Format sources
        sources = await self._format_enhanced_sources(integrated_response)
        
        # Calculate confidence
        confidence = await self._calculate_enhanced_confidence(integrated_response)
        
        return {
            "answer": full_answer,
            "sources": sources,
            "confidence": confidence,
            "response_type": "enhanced",
            "strategy": integrated_response.strategy.value
        }
    
    async def _format_foundation_first_response(self, response: IntegratedResponse) -> List[str]:
        """Format response with Islamic foundation first"""
        parts = []
        
        # Islamic Foundation Section
        if response.quranic_results:
            parts.append("## 🕌 الأساس الشرعي")
            
            for result in response.primary_sources[:2]:  # Top 2 Islamic sources
                if result.chunk.metadata.get("foundation_type") == "quranic":
                    verse_ref = result.chunk.metadata.get("verse_reference", "")
                    principle = result.chunk.metadata.get("legal_principle", "")
                    
                    if verse_ref and principle:
                        parts.append(f"**{verse_ref}**: {principle}")
        
        # Civil Implementation Section
        if response.civil_results:
            parts.append("## ⚖️ التطبيق في النظام السعودي")
            
            civil_sources = [r for r in response.supporting_sources 
                           if r.chunk.metadata.get("source_type") == "civil"]
            
            for result in civil_sources[:2]:  # Top 2 civil sources
                title = result.chunk.title
                content_preview = result.chunk.content[:200] + "..."
                parts.append(f"**{title}**: {content_preview}")
        
        return parts
    
    async def _format_civil_with_foundation_response(self, response: IntegratedResponse) -> List[str]:
        """Format response with civil law primary and Islamic support"""
        parts = []
        
        # Civil Law Primary Section
        if response.civil_results:
            parts.append("## ⚖️ الأحكام القانونية")
            
            for result in response.primary_sources[:2]:
                if result.chunk.metadata.get("source_type") == "civil":
                    title = result.chunk.title
                    content_preview = result.chunk.content[:200] + "..."
                    parts.append(f"**{title}**: {content_preview}")
        
        # Islamic Foundation Support
        if response.quranic_results:
            parts.append("## 🕌 المرجعية الشرعية")
            
            quranic_sources = [r for r in response.supporting_sources 
                             if r.chunk.metadata.get("foundation_type") == "quranic"]
            
            for result in quranic_sources[:2]:
                verse_ref = result.chunk.metadata.get("verse_reference", "")
                principle = result.chunk.metadata.get("legal_principle", "")
                
                if verse_ref and principle:
                    parts.append(f"**الأصل الشرعي ({verse_ref})**: {principle}")
        
        return parts
    
    async def _format_contextual_blend_response(self, response: IntegratedResponse) -> List[str]:
        """Format response with intelligent contextual blending"""
        parts = []
        
        # Integrated Analysis
        parts.append("## 📋 التحليل القانوني المتكامل")
        
        # Blend primary sources regardless of type
        for i, result in enumerate(response.primary_sources[:3]):
            source_type = "شرعي" if result.chunk.metadata.get("foundation_type") == "quranic" else "قانوني"
            title = result.chunk.title
            content_preview = result.chunk.content[:150] + "..."
            
            parts.append(f"**{i+1}. المصدر ال{source_type}**: {title}")
            parts.append(content_preview)
        
        return parts
    
    async def _format_civil_only_response(self, response: IntegratedResponse) -> List[str]:
        """Format civil-only response (for procedural matters)"""
        parts = []
        
        parts.append("## 📋 الإجراءات القانونية")
        
        for result in response.primary_sources[:3]:
            title = result.chunk.title
            content_preview = result.chunk.content[:200] + "..."
            parts.append(f"**{title}**: {content_preview}")
        
        return parts
    
    async def _format_enhanced_sources(self, response: IntegratedResponse) -> List[Dict[str, Any]]:
        """Format sources with enhanced metadata"""
        formatted_sources = []
        
        # Format all sources with enhanced information
        all_sources = response.primary_sources + response.supporting_sources + response.contextual_sources
        
        for source in all_sources:
            source_info = {
                "title": source.chunk.title,
                "content": source.chunk.content[:300],
                "confidence": source.similarity_score,
                "type": "quranic" if source.chunk.metadata.get("foundation_type") == "quranic" else "civil"
            }
            
            # Add Quranic-specific metadata
            if source_info["type"] == "quranic":
                metadata = source.chunk.metadata
                source_info.update({
                    "verse_reference": metadata.get("verse_reference", ""),
                    "surah": metadata.get("surah", ""),
                    "ayah": metadata.get("ayah", ""),
                    "legal_principle": metadata.get("legal_principle", ""),
                    "cultural_appropriateness": metadata.get("cultural_appropriateness", 0.0),
                    "modern_applications": metadata.get("modern_applications", [])
                })
            
            formatted_sources.append(source_info)
        
        return formatted_sources
    
    async def _calculate_enhanced_confidence(self, response: IntegratedResponse) -> float:
        """Calculate enhanced confidence score"""
        base_confidence = 0.7
        
        # Factor in integration quality
        integration_bonus = response.integration_quality * 0.2
        
        # Factor in cultural appropriateness
        cultural_bonus = response.cultural_appropriateness * 0.1
        
        # Factor in source quality
        if response.primary_sources:
            source_quality = sum(s.similarity_score for s in response.primary_sources) / len(response.primary_sources)
            source_bonus = source_quality * 0.15
        else:
            source_bonus = 0.0
        
        # Factor in legal completeness
        completeness_bonus = response.legal_completeness * 0.05
        
        total_confidence = base_confidence + integration_bonus + cultural_bonus + source_bonus + completeness_bonus
        return min(total_confidence, 1.0)
    
    async def _apply_response_enhancements(self, response: Dict[str, Any], 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply additional enhancements to the response"""
        
        if not self.response_enhancement_enabled:
            return response
        
        enhanced_response = response.copy()
        
        # Cultural adaptation
        if self.feature_flags.get("cultural_adaptation", False):
            enhanced_response = await self._apply_cultural_adaptation(enhanced_response, context)
        
        # Quality filtering
        if self.feature_flags.get("quality_filtering", False):
            enhanced_response = await self._apply_quality_filtering(enhanced_response)
        
        # User preference adaptation
        user_prefs = context.get("user_preferences", {})
        if user_prefs:
            enhanced_response = await self._apply_user_preferences(enhanced_response, user_prefs)
        
        return enhanced_response
    
    async def _apply_cultural_adaptation(self, response: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply cultural adaptation to the response"""
        # Ensure Islamic sources are presented respectfully
        if response.get("strategy") in ["foundation_first", "civil_with_foundation"]:
            # Add appropriate honorifics and Islamic formatting
            answer = response["answer"]
            
            # Add بسم الله if appropriate (for significant Islamic content)
            quranic_count = sum(1 for s in response.get("sources", []) if s.get("type") == "quranic")
            if quranic_count >= 2:
                if not answer.startswith("بسم الله"):
                    answer = "بسم الله الرحمن الرحيم\n\n" + answer
            
            response["answer"] = answer
        
        return response
    
    async def _apply_quality_filtering(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quality filtering to sources and content"""
        
        # Filter low-quality sources
        if "sources" in response:
            high_quality_sources = [
                source for source in response["sources"]
                if source.get("confidence", 0) >= 0.6
            ]
            
            # If we filtered too many, keep at least the top 3
            if len(high_quality_sources) < 3 and len(response["sources"]) >= 3:
                sorted_sources = sorted(response["sources"], 
                                      key=lambda s: s.get("confidence", 0), reverse=True)
                high_quality_sources = sorted_sources[:3]
            
            response["sources"] = high_quality_sources
        
        return response
    
    async def _apply_user_preferences(self, response: Dict[str, Any], 
                                    preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user preferences to the response"""
        
        # Islamic integration preference
        islamic_pref = preferences.get("islamic_integration", "balanced")
        
        if islamic_pref == "minimal":
            # Reduce Islamic content
            sources = response.get("sources", [])
            civil_sources = [s for s in sources if s.get("type") != "quranic"]
            quranic_sources = [s for s in sources if s.get("type") == "quranic"]
            
            # Keep only top 1 Quranic source if any
            limited_quranic = quranic_sources[:1] if quranic_sources else []
            response["sources"] = civil_sources + limited_quranic
            
        elif islamic_pref == "extensive":
            # Emphasize Islamic content
            sources = response.get("sources", [])
            quranic_sources = [s for s in sources if s.get("type") == "quranic"]
            civil_sources = [s for s in sources if s.get("type") != "quranic"]
            
            # Prioritize Quranic sources
            response["sources"] = quranic_sources + civil_sources
        
        # Response length preference
        length_pref = preferences.get("response_length", "standard")
        if length_pref == "concise":
            # Truncate answer
            answer = response.get("answer", "")
            if len(answer) > 500:
                response["answer"] = answer[:500] + "..."
        
        return response
    
    async def _process_traditional_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process query using traditional method (fallback compatibility)"""
        
        try:
            # Use civil law search only (maintaining backward compatibility)
            civil_results, _ = await self.orchestrator._search_civil_law(query, [], context, 10)
            
            # Format in traditional format
            if civil_results:
                best_result = civil_results[0]
                answer = best_result.chunk.content[:500]
                sources = [
                    {
                        "title": result.chunk.title,
                        "content": result.chunk.content[:200],
                        "confidence": result.similarity_score,
                        "type": "civil"
                    }
                    for result in civil_results[:5]
                ]
            else:
                answer = "لم يتم العثور على نتائج مناسبة لاستفسارك."
                sources = []
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.7,
                "response_type": "traditional"
            }
            
        except Exception as e:
            logger.error(f"Traditional query processing failed: {e}")
            raise
    
    def _prepare_enhanced_context(self, query: str, 
                                context: Optional[Dict[str, Any]], 
                                user_preferences: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare enhanced context for processing"""
        
        enhanced_context = context.copy() if context else {}
        
        # Add user preferences
        if user_preferences:
            enhanced_context["user_preferences"] = user_preferences
        
        # Add default cultural context
        enhanced_context.setdefault("cultural_context", "saudi_legal")
        enhanced_context.setdefault("preferred_abstraction", "medium")
        enhanced_context.setdefault("modern_context", True)
        
        # Analyze query complexity
        query_length = len(query.split())
        if query_length < 5:
            enhanced_context["complexity_level"] = "low"
        elif query_length > 20:
            enhanced_context["complexity_level"] = "high"
        else:
            enhanced_context["complexity_level"] = "medium"
        
        return enhanced_context
    
    def _should_enhance_query(self, query: str, context: Dict[str, Any]) -> bool:
        """Determine if query should be enhanced with Quranic integration"""
        
        # Check feature flags
        if not self.feature_flags.get("quranic_integration", False):
            return False
        
        # Check user preferences
        user_prefs = context.get("user_preferences", {})
        if user_prefs.get("disable_islamic_integration", False):
            return False
        
        # Simple heuristics (can be made more sophisticated)
        query_lower = query.lower()
        
        # Always enhance for legal queries
        legal_indicators = ["حكم", "قانون", "نظام", "قضية", "محكمة", "دعوى"]
        if any(indicator in query_lower for indicator in legal_indicators):
            return True
        
        # Skip purely procedural queries
        procedural_indicators = ["كيف أقدم", "أين أذهب", "ما الرسوم", "نموذج"]
        if any(indicator in query_lower for indicator in procedural_indicators):
            return False
        
        # Default to enhancement for most queries
        return True
    
    async def _emergency_fallback(self, query: str, 
                                context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Emergency fallback when all processing fails"""
        
        return {
            "answer": "عذراً، حدث خطأ في معالجة استفسارك. يرجى المحاولة مرة أخرى.",
            "sources": [],
            "confidence": 0.0,
            "response_type": "error_fallback",
            "error": "processing_failed"
        }
    
    def _update_performance_metrics(self, processing_time: float):
        """Update performance tracking metrics"""
        self.performance_metrics["total_queries"] += 1
        
        # Update average response time
        current_avg = self.performance_metrics["average_response_time"]
        total_queries = self.performance_metrics["total_queries"]
        new_avg = ((current_avg * (total_queries - 1)) + processing_time) / total_queries
        self.performance_metrics["average_response_time"] = new_avg
    
    def configure_features(self, feature_config: Dict[str, bool]):
        """Configure feature flags for gradual rollout"""
        self.feature_flags.update(feature_config)
        logger.info(f"Feature flags updated: {self.feature_flags}")
    
    def enable_integration(self, enabled: bool = True):
        """Enable or disable Quranic integration"""
        self.integration_enabled = enabled
        logger.info(f"Quranic integration {'enabled' if enabled else 'disabled'}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the enhanced chat processor"""
        
        health = {
            "status": "healthy",
            "integration_enabled": self.integration_enabled,
            "feature_flags": self.feature_flags,
            "performance_metrics": self.performance_metrics
        }
        
        # Check orchestrator health
        if self.integration_enabled:
            try:
                orchestrator_health = await self.orchestrator.get_health_status()
                health["orchestrator"] = orchestrator_health
                
                if orchestrator_health.get("status") != "healthy":
                    health["status"] = "degraded"
                    
            except Exception as e:
                health["orchestrator"] = {"status": "error", "error": str(e)}
                health["status"] = "degraded"
        
        return health


# Global instance for the enhanced chat processor
enhanced_chat_processor = EnhancedChatProcessor()


async def initialize_enhanced_chat():
    """Initialize the enhanced chat system"""
    try:
        await enhanced_chat_processor.initialize()
        logger.info("✅ Enhanced chat system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize enhanced chat system: {e}")
        return False


async def process_enhanced_chat_query(query: str, 
                                    context: Optional[Dict[str, Any]] = None,
                                    user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main API endpoint for enhanced chat processing
    
    Args:
        query: User's legal query
        context: Optional context information
        user_preferences: Optional user preferences
        
    Returns:
        Enhanced chat response with optional Quranic integration
    """
    
    return await enhanced_chat_processor.process_chat_query(
        query=query,
        context=context,
        user_preferences=user_preferences
    )


async def get_enhanced_chat_health() -> Dict[str, Any]:
    """Get health status of enhanced chat system"""
    return await enhanced_chat_processor.get_health_status()


def configure_enhanced_chat_features(feature_config: Dict[str, bool]):
    """Configure enhanced chat feature flags"""
    enhanced_chat_processor.configure_features(feature_config)


def set_integration_enabled(enabled: bool):
    """Enable or disable Quranic integration"""
    enhanced_chat_processor.enable_integration(enabled)