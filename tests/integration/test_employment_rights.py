"""
Integration tests for Employment Rights queries
Tests the complete pipeline from query to Islamic legal response
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json

from app.api.enhanced_chat import process_enhanced_chat_query, initialize_enhanced_chat
from app.core.enhancements.concept_mapping import create_concept_mapping_engine
from app.core.enhancements.multi_modal_search import create_multi_modal_search_engine


class TestEmploymentRightsIntegration:
    """Integration tests for employment rights scenarios"""
    
    @pytest.fixture
    def sample_employment_queries(self):
        return [
            {
                "query": "موظف سعودي يعمل في شركة خاصة منذ 5 سنوات، تم فصله فجأة بدون سبب واضح ولم تدفع له الشركة مستحقاته النهائية. ما هي حقوقه في نظام العمل السعودي؟",
                "expected_concepts": ["employment_dismissal", "unpaid_wages", "worker_rights"],
                "expected_islamic_concepts": ["العدالة", "الوفاء بالعهد", "أداء الحق"],
                "domain": "employment"
            },
            {
                "query": "شركة لم تدفع رواتب موظفيها لمدة ثلاثة أشهر، ما الحكم الشرعي؟",
                "expected_concepts": ["unpaid_wages", "employer_obligations"],
                "expected_islamic_concepts": ["أداء الحق", "تحريم أكل أموال الناس بالباطل"],
                "domain": "employment"
            },
            {
                "query": "هل يحق للموظف ترك العمل إذا لم يحصل على راتبه؟",
                "expected_concepts": ["worker_rights", "employment_termination"],
                "expected_islamic_concepts": ["العدالة", "عدم الظلم"],
                "domain": "employment"
            }
        ]
    
    @pytest.fixture
    def mock_quranic_database_results(self):
        return [
            {
                "foundation_id": "justice_verse_1",
                "verse_text": "إِنَّ اللَّهَ يَأْمُرُكُمْ أَن تُؤَدُّوا الْأَمَانَاتِ إِلَىٰ أَهْلِهَا",
                "legal_principle": "وجوب أداء الأمانات والحقوق لأصحابها",
                "principle_category": "العدالة",
                "verse_reference": "النساء: 58",
                "relevance_score": 0.95
            },
            {
                "foundation_id": "worker_rights_1",
                "verse_text": "وَلَا تَأْكُلُوا أَمْوَالَكُم بَيْنَكُم بِالْبَاطِلِ",
                "legal_principle": "تحريم أكل أموال الناس بالباطل",
                "principle_category": "المعاملات",
                "verse_reference": "البقرة: 188",
                "relevance_score": 0.90
            },
            {
                "foundation_id": "covenant_keeping_1",
                "verse_text": "وَأَوْفُوا بِالْعَهْدِ ۖ إِنَّ الْعَهْدَ كَانَ مَسْئُولًا",
                "legal_principle": "وجوب الوفاء بالعقود والالتزامات",
                "principle_category": "المعاملات",
                "verse_reference": "الإسراء: 34",
                "relevance_score": 0.85
            }
        ]
    
    @pytest.mark.asyncio
    async def test_employment_dismissal_query(self, sample_employment_queries, mock_quranic_database_results):
        """Test employment dismissal query end-to-end"""
        query_data = sample_employment_queries[0]
        
        # Mock the Islamic legal search to return relevant verses
        with patch('app.core.enhancements.multi_modal_search.VectorSearchStrategy.search') as mock_search:
            mock_search.return_value = [
                Mock(
                    foundation_id=result["foundation_id"],
                    content=result["verse_text"],
                    relevance_score=result["relevance_score"],
                    strategy_used="vector_search",
                    confidence_level=0.85
                )
                for result in mock_quranic_database_results
            ]
            
            # Initialize system
            await initialize_enhanced_chat()
            
            # Process query
            result = await process_enhanced_chat_query(query_data["query"])
            
            # Assertions
            assert result is not None
            assert result.get("response_type") == "enhanced"
            
            # Should find Islamic foundations
            quranic_sources_count = result.get("quranic_sources_count", 0)
            assert quranic_sources_count > 0, "Should find relevant Quranic sources"
            
            # Should use appropriate strategy
            strategy = result.get("strategy_used")
            assert strategy in ["civil_with_foundation", "foundation_first"], f"Unexpected strategy: {strategy}"
            
            # Response should include Islamic legal content
            answer = result.get("answer", "")
            assert any(concept in answer for concept in ["العدالة", "الوفاء", "الحق"]), "Should include Islamic legal concepts"
    
    @pytest.mark.asyncio
    async def test_unpaid_wages_query(self, sample_employment_queries, mock_quranic_database_results):
        """Test unpaid wages query"""
        query_data = sample_employment_queries[1]
        
        with patch('app.core.enhancements.multi_modal_search.VectorSearchStrategy.search') as mock_search:
            # Return specific verses about fulfilling rights
            mock_search.return_value = [
                Mock(
                    foundation_id="worker_rights_1",
                    content="وَلَا تَأْكُلُوا أَمْوَالَكُم بَيْنَكُم بِالْبَاطِلِ",
                    relevance_score=0.90,
                    strategy_used="vector_search",
                    confidence_level=0.85
                )
            ]
            
            await initialize_enhanced_chat()
            result = await process_enhanced_chat_query(query_data["query"])
            
            # Should detect this as employment + Islamic legal issue
            assert result.get("quranic_sources_count", 0) > 0
            
            # Should mention prohibition of unlawful consumption
            answer = result.get("answer", "")
            assert any(term in answer for term in ["الباطل", "الحق", "أموال"]), "Should reference unlawful consumption"
    
    @pytest.mark.asyncio
    async def test_worker_termination_rights(self, sample_employment_queries):
        """Test worker's right to terminate employment"""
        query_data = sample_employment_queries[2]
        
        with patch('app.core.enhancements.multi_modal_search.MultiModalSearchEngine.search') as mock_search:
            mock_search.return_value = [
                Mock(
                    foundation_id="justice_verse_1",
                    content="إِنَّ اللَّهَ يَأْمُرُ بِالْعَدْلِ وَالْإِحْسَانِ",
                    relevance_score=0.88,
                    strategy_used="keyword_search",
                    confidence_level=0.75
                )
            ]
            
            await initialize_enhanced_chat()
            result = await process_enhanced_chat_query(query_data["query"])
            
            # Should provide both civil law and Islamic guidance
            assert result.get("response_type") == "enhanced"
            assert result.get("strategy_used") in ["civil_with_foundation", "foundation_first"]
    
    def test_concept_mapping_for_employment(self):
        """Test concept mapping for employment scenarios"""
        mapping_engine = create_concept_mapping_engine()
        
        # Test employment dismissal concepts
        concepts = ["employment_dismissal", "unfair_termination"]
        query = "فصل موظف بدون سبب"
        
        result = asyncio.run(mapping_engine.enhance_query_with_islamic_concepts(concepts, query))
        
        # Should map to Islamic justice concepts
        assert result["confidence"] > 0.7
        assert len(result["quranic_search_terms"]) > 0
        
        # Should include justice and covenant concepts
        search_terms = [term[0] for term in result["quranic_search_terms"]]
        assert any("عدالة" in term or "justice" in term for term in search_terms)
    
    def test_multi_modal_search_fallback(self):
        """Test multi-modal search fallback mechanisms"""
        search_engine = create_multi_modal_search_engine()
        
        # Test that fallback strategies are available
        stats = search_engine.get_search_statistics()
        assert "available_strategies" in stats
        assert len(stats["available_strategies"]) >= 2  # Vector + Keyword minimum
    
    @pytest.mark.asyncio
    async def test_employment_query_without_islamic_results(self):
        """Test employment query when no Islamic results are found"""
        query = "موظف يطلب إجازة مرضية"
        
        # Mock empty Islamic search results
        with patch('app.core.enhancements.multi_modal_search.VectorSearchStrategy.search') as mock_search:
            mock_search.return_value = []
            
            # Should still provide civil law response
            await initialize_enhanced_chat()
            result = await process_enhanced_chat_query(query)
            
            # Should not crash and should provide some response
            assert result is not None
            assert isinstance(result.get("answer", ""), str)
            assert len(result.get("answer", "")) > 0
    
    @pytest.mark.asyncio 
    async def test_system_resilience_on_errors(self):
        """Test system behavior when components fail"""
        query = "حقوق العامل في الإسلام"
        
        # Mock various failures
        with patch('app.core.semantic_concepts.SemanticConceptEngine.extract_legal_concepts') as mock_concepts:
            mock_concepts.side_effect = Exception("Concept extraction failed")
            
            await initialize_enhanced_chat()
            result = await process_enhanced_chat_query(query)
            
            # System should not crash and should provide fallback response
            assert result is not None
            assert "error" not in result.get("answer", "").lower()


class TestEmploymentRightsAccuracy:
    """Test accuracy of employment rights responses"""
    
    @pytest.fixture
    def expected_islamic_principles(self):
        return {
            "justice": ["العدالة", "الإنصاف", "عدم الظلم"],
            "covenant_keeping": ["الوفاء بالعهد", "الوفاء بالعقود"],
            "rights_fulfillment": ["أداء الحق", "إعطاء كل ذي حق حقه"],
            "prohibition_unlawful": ["تحريم أكل أموال الناس بالباطل", "عدم الأكل بالباطل"]
        }
    
    @pytest.mark.asyncio
    async def test_response_contains_relevant_principles(self, expected_islamic_principles):
        """Test that employment responses contain relevant Islamic principles"""
        query = "شركة تؤخر رواتب موظفيها، ما حكم الشريعة؟"
        
        # Mock Islamic search to return rights-related verses
        with patch('app.core.enhancements.multi_modal_search.MultiModalSearchEngine.search') as mock_search:
            mock_search.return_value = [
                Mock(
                    foundation_id="rights_verse",
                    content="إِنَّ اللَّهَ يَأْمُرُكُمْ أَن تُؤَدُّوا الْأَمَانَاتِ إِلَىٰ أَهْلِهَا",
                    relevance_score=0.95,
                    strategy_used="vector_search",
                    confidence_level=0.90
                )
            ]
            
            await initialize_enhanced_chat()
            result = await process_enhanced_chat_query(query)
            
            answer = result.get("answer", "")
            
            # Should contain at least one principle from each category
            found_principles = []
            for category, principles in expected_islamic_principles.items():
                for principle in principles:
                    if any(word in answer for word in principle.split()):
                        found_principles.append(category)
                        break
            
            assert len(found_principles) >= 2, f"Should contain multiple Islamic principles, found: {found_principles}"
    
    @pytest.mark.asyncio
    async def test_response_quality_metrics(self):
        """Test quality metrics of employment rights responses"""
        query = "موظف لم يحصل على مكافأة نهاية الخدمة"
        
        await initialize_enhanced_chat()
        result = await process_enhanced_chat_query(query)
        
        # Quality checks
        assert result.get("cultural_appropriateness", 0) >= 0.7, "Should be culturally appropriate"
        assert result.get("response_type") == "enhanced", "Should be enhanced response"
        
        answer = result.get("answer", "")
        assert len(answer) > 100, "Response should be comprehensive"
        assert "الله" in answer or "القرآن" in answer or "الشريعة" in answer, "Should reference Islamic sources"


if __name__ == "__main__":
    pytest.main([__file__])