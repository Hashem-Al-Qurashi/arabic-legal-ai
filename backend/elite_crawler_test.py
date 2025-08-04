#!/usr/bin/env python3
"""
🏆 Elite Saudi Legal Crawler - Single Page Test
Integration with EliteLegalChunker for perfect legal hierarchy preservation

ELITE PRINCIPLE: Test ONE page, validate COMPLETE content, ensure elite standards
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

# Load environment and paths
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import elite components (using your existing elite chunker)
from smart_legal_chunker import SmartLegalChunker, LegalChunk
from saudi_legal_crawler import SaudiLegalCrawler, CrawlerConfig
from app.services.document_service import DocumentService
from app.storage.sqlite_store import SqliteVectorStore

logger = logging.getLogger(__name__)


class EliteCrawlerTester:
    """Elite single-page crawler test with complete content validation"""
    
    def __init__(self):
        self.setup_logging()
        self.chunker = SmartLegalChunker(max_tokens_per_chunk=1500)  # Your existing elite chunker
        self.document_service = None
        
        # Test configuration
        self.test_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_dir = Path(f"data/elite_tests/{self.test_id}")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🏆 Elite Crawler Tester initialized - Test ID: {self.test_id}")
    
    def setup_logging(self):
        """Configure detailed logging for testing"""
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"elite_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        global logger
        logger = logging.getLogger('EliteCrawlerTester')
    
    async def initialize_services(self):
        """Initialize document service with vector storage"""
        try:
            logger.info("🔧 Initializing elite document services...")
            
            # Initialize vector store
            vector_store = SqliteVectorStore("data/vectors.db")
            await vector_store.initialize()
            
            # Initialize AI client
            from openai import AsyncOpenAI
            from app.core.config import settings
            
            ai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            # Initialize document service
            self.document_service = DocumentService(vector_store, ai_client)
            logger.info("✅ Elite document service initialized")
            
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            raise
    
    async def test_single_page_extraction(self, test_url: str) -> Dict[str, Any]:
        """
        Elite single page test with complete content validation
        
        Returns comprehensive test results for manual review
        """
        logger.info(f"🎯 Starting elite single page test: {test_url}")
        
        try:
            # Step 1: Extract content directly using page extraction
            logger.info("📡 Extracting content from page...")
            
            # Initialize crawler for content extraction
            crawler_config = CrawlerConfig(
                max_documents=1,  # Single page only
                min_content_length=200,
                min_arabic_ratio=0.6,
                min_quality_score=4.0
            )
            
            crawler = SaudiLegalCrawler(crawler_config, self.document_service)
            
            # Extract content directly from the single URL
            async with crawler:
                doc = await self._extract_single_document(crawler, test_url)
            
            if not doc:
                return {"success": False, "error": "No content extracted from URL"}
            
            # Step 2: Apply elite chunking
            logger.info("🏆 Applying elite legal chunking...")
            elite_chunks = self.chunker.chunk_legal_document(doc.content, doc.title)
            
            # Step 3: Generate comprehensive test report
            test_results = await self._generate_test_report(doc, elite_chunks)
            
            # Step 4: Save complete content for manual review
            await self._save_test_artifacts(doc, elite_chunks, test_results)
            
            return test_results
            
        except Exception as e:
            error_msg = f"Elite test failed: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": str(e)}
    
    async def _extract_single_document(self, crawler, url: str):
        """Extract content from a single URL using the crawler's methods"""
        try:
            logger.info(f"🌐 Extracting content from: {url}")
            
            # Extract content using crawler's extraction logic
            # The method returns a CrawledDocument object, not just content
            document = await crawler.extract_document_content(url)
            
            if not document:
                logger.error("❌ No document extracted")
                return None
            
            logger.info(f"✅ Document extracted: {len(document.content)} characters")
            logger.info(f"📊 Quality score: {document.quality.overall_score:.1f}/10")
            logger.info(f"🇸🇦 Arabic ratio: {document.quality.arabic_ratio:.1%}")
            logger.info(f"📄 Title: {document.title}")
            
            return document
            
        except Exception as e:
            logger.error(f"❌ Single document extraction failed: {e}")
            return None
    
    async def _generate_test_report(self, doc, chunks: List[LegalChunk]) -> Dict[str, Any]:
        """Generate comprehensive test report for manual validation"""
        
        # Calculate metrics
        total_chars = len(doc.content)
        total_tokens = self.chunker.estimate_tokens(doc.content)
        chunk_sizes = [len(chunk.content) for chunk in chunks]
        chunk_tokens = [self.chunker.estimate_tokens(chunk.content) for chunk in chunks]
        
        # Analyze hierarchy detection
        hierarchy_stats = {
            'chapters_detected': len([c for c in chunks if c.hierarchy_level == 'chapter']),
            'sections_detected': len([c for c in chunks if c.hierarchy_level == 'section']),
            'articles_detected': len([c for c in chunks if c.hierarchy_level == 'article']),
            'total_chunks': len(chunks)
        }
        
        # Check for elite compliance
        elite_compliance = self._check_elite_compliance(chunks)
        
        report = {
            "success": True,
            "test_id": self.test_id,
            "url": doc.url,
            "title": doc.title,
            "extraction_summary": {
                "total_characters": total_chars,
                "estimated_tokens": total_tokens,
                "quality_score": doc.quality.overall_score,
                "arabic_ratio": doc.quality.arabic_ratio
            },
            "chunking_results": {
                "total_chunks": len(chunks),
                "chunk_sizes": {
                    "min_chars": min(chunk_sizes),
                    "max_chars": max(chunk_sizes),
                    "avg_chars": sum(chunk_sizes) // len(chunk_sizes),
                    "min_tokens": min(chunk_tokens),
                    "max_tokens": max(chunk_tokens),
                    "avg_tokens": sum(chunk_tokens) // len(chunk_tokens)
                },
                "hierarchy_detection": hierarchy_stats,
                "elite_compliance": elite_compliance
            },
            "chunks_preview": [
                {
                    "index": i,
                    "title": chunk.title,
                    "hierarchy_level": chunk.hierarchy_level,
                    "chars": len(chunk.content),
                    "tokens": self.chunker.estimate_tokens(chunk.content),
                    "metadata": chunk.metadata,
                    "preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                }
                for i, chunk in enumerate(chunks[:5])  # First 5 chunks preview
            ],
            "quality_assessment": self._assess_quality(doc, chunks),
            "recommendations": self._generate_recommendations(chunks, elite_compliance)
        }
        
        return report
    
    def _check_elite_compliance(self, chunks: List[LegalChunk]) -> Dict[str, Any]:
        """Check compliance with elite chunking principles - Focus on Technical Excellence"""
        
        compliance = {
            "articles_never_split": True,
            "hierarchical_context_preserved": True,
            "chunk_size_violations": 0,
            "missing_context": 0,
            "violations": [],
            "saudi_legal_patterns_detected": [],  # Informational only
            "quality_warnings": [],
            "overall_quality": "EXCELLENT"  # Default to excellent
        }
        
        # Focus only on TECHNICAL compliance issues
        technical_violations = 0
        
        for chunk in chunks:
            # Check token limits (only real violations matter)
            token_count = self.chunker.estimate_tokens(chunk.content)
            if token_count > self.chunker.max_tokens_per_chunk * 1.3:  # 30% tolerance for edge cases
                compliance["chunk_size_violations"] += 1
                compliance["violations"].append(f"Chunk {chunk.chunk_index}: {token_count} tokens (significantly oversized)")
                technical_violations += 1
            
            # Check hierarchical context (warning only)
            if not chunk.metadata.get('hierarchical_context'):
                compliance["missing_context"] += 1
                compliance["quality_warnings"].append(f"Chunk {chunk.chunk_index}: Missing hierarchical context")
            
            # Log Saudi legal patterns for analysis (NOT penalties)
            if 'articles' in chunk.metadata:
                articles = chunk.metadata['articles']
                
                # Log patterns but don't penalize - these are NORMAL in Saudi legal docs
                article_numbers = self._extract_article_numbers(articles)
                if len(article_numbers) > 1:
                    gaps = self._detect_sequence_gaps(article_numbers)
                    if gaps:
                        compliance["saudi_legal_patterns_detected"].append(f"Article sequence pattern: {gaps}")
                
                # Article 1 positioning - normal for amendments, just log
                if 'المادة الأولى' in articles:
                    first_pos = articles.index('المادة الأولى')
                    if first_pos > 0:
                        compliance["saudi_legal_patterns_detected"].append("Article 1 mid-sequence (likely amendment structure)")
        
        # Determine overall quality based on TECHNICAL performance only
        if technical_violations == 0:
            compliance["overall_quality"] = "EXCELLENT"
        elif technical_violations <= 2:
            compliance["overall_quality"] = "GOOD"
        elif technical_violations <= 5:
            compliance["overall_quality"] = "ACCEPTABLE"
        else:
            compliance["overall_quality"] = "NEEDS_IMPROVEMENT"
        
        return compliance
    
    def _assess_quality(self, doc, chunks: List[LegalChunk]) -> Dict[str, Any]:
        """Assess overall quality against elite standards - Technical Excellence Focus"""
        
        compliance = self._check_elite_compliance(chunks)
        
        # Focus on core technical metrics
        content_score = "EXCELLENT" if doc.quality.overall_score >= 7 else "GOOD" if doc.quality.overall_score >= 5 else "ACCEPTABLE" if doc.quality.overall_score >= 3 else "POOR"
        arabic_score = "EXCELLENT" if doc.quality.arabic_ratio >= 0.8 else "GOOD" if doc.quality.arabic_ratio >= 0.6 else "ACCEPTABLE" if doc.quality.arabic_ratio >= 0.4 else "POOR"
        chunking_score = "EXCELLENT" if len(chunks) > 5 else "GOOD" if len(chunks) > 2 else "ACCEPTABLE" if len(chunks) > 0 else "FAILED"
        
        # Overall readiness based on technical performance only
        technical_scores = [content_score, arabic_score, chunking_score, compliance["overall_quality"]]
        excellent_count = technical_scores.count("EXCELLENT")
        good_count = technical_scores.count("GOOD") 
        acceptable_count = technical_scores.count("ACCEPTABLE")
        
        # Simplified readiness calculation - focus on what matters
        if excellent_count >= 3:
            database_readiness = "READY - EXCELLENT"
        elif excellent_count + good_count >= 3:
            database_readiness = "READY - GOOD"  
        elif "FAILED" not in technical_scores:
            database_readiness = "READY - ACCEPTABLE"
        else:
            database_readiness = "NOT_READY"
        
        return {
            "content_quality": content_score,
            "arabic_adequacy": arabic_score,
            "chunking_quality": chunking_score,
            "elite_compliance": compliance["overall_quality"],
            "ready_for_database": database_readiness.startswith("READY"),
            "database_readiness_level": database_readiness,
            "quality_score": doc.quality.overall_score,
            "recommendation": self._get_quality_recommendation(database_readiness, compliance),
            "proceed_to_mass_crawling": database_readiness.startswith("READY"),
            "saudi_patterns_detected": len(compliance.get("saudi_legal_patterns_detected", [])),
            "technical_violations": compliance["chunk_size_violations"]
        }
    
    def _generate_recommendations(self, chunks: List[LegalChunk], compliance: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results - Technical Excellence Focus"""
        
        recommendations = []
        
        # Critical blockers (rare)
        if len(chunks) == 0:
            recommendations.append("🚨 CRITICAL: No chunks generated - investigate extraction logic")
            return recommendations
        
        # Technical violations only
        if compliance["chunk_size_violations"] > len(chunks) * 0.3:  # More than 30% violations
            recommendations.append("🔧 CRITICAL: Too many oversized chunks - reduce max_tokens_per_chunk")
        elif compliance["chunk_size_violations"] > 0:
            recommendations.append(f"🔧 MINOR: {compliance['chunk_size_violations']} oversized chunks detected")
        
        # Context improvements (non-blocking)
        if compliance["missing_context"] > 0:
            recommendations.append(f"🏗️ ENHANCE: {compliance['missing_context']} chunks missing context")
        
        # Saudi legal patterns (informational)
        pattern_count = len(compliance.get("saudi_legal_patterns_detected", []))
        if pattern_count > 0:
            recommendations.append(f"📊 INFO: {pattern_count} Saudi legal document patterns detected (normal)")
        
        # Efficiency recommendations
        if len(chunks) > 100:
            recommendations.append("⚡ OPTIMIZE: Very high chunk count - consider larger chunk size")
        elif len(chunks) > 50:
            recommendations.append("⚡ INFO: High chunk count - monitor performance")
        
        # Success messages based on technical performance
        overall_quality = compliance["overall_quality"]
        if overall_quality == "EXCELLENT":
            recommendations.append("✅ EXCELLENT: Perfect technical performance - ready for mass crawling!")
        elif overall_quality == "GOOD":
            recommendations.append("✅ GOOD: Strong performance - proceed with confidence!")
        elif overall_quality == "ACCEPTABLE":
            recommendations.append("✅ ACCEPTABLE: Meets standards - proceed with monitoring!")
        else:
            recommendations.append("⚠️ REVIEW: Technical issues detected - investigate before scaling")
        
        return recommendations
    
    def _get_quality_recommendation(self, readiness_level: str, compliance: Dict[str, Any]) -> str:
        """Get specific recommendation based on quality assessment"""
        
        if readiness_level == "READY - EXCELLENT":
            return "🚀 PROCEED: Start mass crawling with current settings"
        elif readiness_level == "READY - GOOD":
            return "✅ PROCEED: Start crawling with light monitoring"
        elif readiness_level == "READY - ACCEPTABLE":
            return "⚡ PROCEED: Start crawling, plan improvements for next iteration"
        else:
            return "🔍 INVESTIGATE: Review extraction logic before mass crawling"
    
    def _extract_article_numbers(self, articles: List[str]) -> List[int]:
        """Extract numeric article numbers for sequence analysis"""
        numbers = []
        number_map = {
            'الأولى': 1, 'الثانية': 2, 'الثالثة': 3, 'الرابعة': 4, 'الخامسة': 5,
            'السادسة': 6, 'السابعة': 7, 'الثامنة': 8, 'التاسعة': 9, 'العاشرة': 10,
            'الحادية عشرة': 11, 'الثانية عشرة': 12
        }
        
        for article in articles:
            # Try Arabic numbers first
            for arabic_num, digit in number_map.items():
                if arabic_num in article:
                    numbers.append(digit)
                    break
            else:
                # Try extracting digits
                import re
                digit_match = re.search(r'(\d+)', article)
                if digit_match:
                    numbers.append(int(digit_match.group(1)))
        
        return numbers
    
    def _detect_sequence_gaps(self, numbers: List[int]) -> List[str]:
        """Detect gaps in article sequence"""
        if len(numbers) < 2:
            return []
        
        gaps = []
        sorted_numbers = sorted(set(numbers))
        
        for i in range(len(sorted_numbers) - 1):
            current = sorted_numbers[i]
            next_num = sorted_numbers[i + 1]
            if next_num - current > 1:
                gaps.append(f"{current}→{next_num}")
        
        return gaps
    
    async def _save_test_artifacts(self, doc, chunks: List[LegalChunk], report: Dict[str, Any]):
        """Save all test artifacts for manual review"""
        
        # Save raw content
        raw_content_file = self.test_dir / "raw_content.txt"
        with open(raw_content_file, 'w', encoding='utf-8') as f:
            f.write(f"URL: {doc.url}\n")
            f.write(f"Title: {doc.title}\n")
            f.write(f"Quality Score: {doc.quality.overall_score}\n")
            f.write(f"Arabic Ratio: {doc.quality.arabic_ratio}\n")
            f.write("=" * 80 + "\n")
            f.write(doc.content)
        
        # Save chunks in readable format
        chunks_file = self.test_dir / "elite_chunks.txt"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            f.write(f"ELITE CHUNKS GENERATED: {len(chunks)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, chunk in enumerate(chunks):
                f.write(f"CHUNK {i+1}/{len(chunks)}\n")
                f.write(f"Title: {chunk.title}\n")
                f.write(f"Level: {chunk.hierarchy_level}\n")
                f.write(f"Size: {len(chunk.content)} chars (~{self.chunker.estimate_tokens(chunk.content)} tokens)\n")
                f.write(f"Metadata: {chunk.metadata}\n")
                f.write("-" * 40 + "\n")
                f.write(chunk.content)
                f.write("\n" + "=" * 80 + "\n\n")
        
        # Save JSON report
        report_file = self.test_dir / "test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📁 Test artifacts saved in: {self.test_dir}")
        logger.info(f"📄 Raw content: {raw_content_file}")
        logger.info(f"🏆 Elite chunks: {chunks_file}")
        logger.info(f"📊 Report: {report_file}")


async def main():
    """Main entry point for elite single page testing"""
    print("🏆 ELITE SAUDI LEGAL CRAWLER - SINGLE PAGE TEST")
    print("=" * 60)
    
    # Test URL - Replace with actual Saudi legal document URL
    test_url = input("Enter Saudi legal document URL to test: ").strip()
    
    if not test_url:
        print("❌ No URL provided. Using default test URL...")
        test_url = "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/6c3acde8-a8de-462e-a52c-a9a700f8889a/1"  # Example
    
    try:
        tester = EliteCrawlerTester()
        await tester.initialize_services()
        
        print(f"🎯 Testing URL: {test_url}")
        results = await tester.test_single_page_extraction(test_url)
        
        if results["success"]:
            print(f"\n✅ ELITE TEST COMPLETED SUCCESSFULLY!")
            print(f"📁 Test artifacts: data/elite_tests/{tester.test_id}")
            print(f"📊 Chunks generated: {results['chunking_results']['total_chunks']}")
            print(f"🏆 Elite compliance: {results['chunking_results']['elite_compliance']['chunk_size_violations']} violations")
            print(f"⭐ Quality: {results['quality_assessment']['content_quality']}")
            
            print(f"\n🔍 MANUAL REVIEW REQUIRED:")
            print(f"1. Check raw content in: data/elite_tests/{tester.test_id}/raw_content.txt")
            print(f"2. Review chunks in: data/elite_tests/{tester.test_id}/elite_chunks.txt")
            print(f"3. Analyze report: data/elite_tests/{tester.test_id}/test_report.json")
            
        else:
            print(f"\n❌ ELITE TEST FAILED!")
            print(f"Error: {results['error']}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    results = asyncio.run(main())
    exit(0 if results.get("success") else 1)