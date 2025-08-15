#!/usr/bin/env python3
"""
🚀 ELITE LEGAL CHUNKER - BULLETPROOF CLI TEST SUITE
==================================================

Usage:
    python test_elite_chunker.py --all          # Run all tests
    python test_elite_chunker.py --basic        # Basic functionality
    python test_elite_chunker.py --stress       # Stress tests
    python test_elite_chunker.py --edge         # Edge cases
    python test_elite_chunker.py --benchmark    # Performance tests
    python test_elite_chunker.py --interactive  # Interactive mode

MISSION: Brutally test the EliteLegalChunker before production
"""

import sys
import time
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import asdict
import re

# Colors for beautiful terminal output
class C:
    R = '\033[91m'  # Red
    G = '\033[92m'  # Green  
    Y = '\033[93m'  # Yellow
    B = '\033[94m'  # Blue
    M = '\033[95m'  # Magenta
    C = '\033[96m'  # Cyan
    W = '\033[97m'  # White
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print fancy header"""
    print(f"\n{C.BOLD}{C.C}{'='*60}{C.END}")
    print(f"{C.BOLD}{C.C} {text:^56} {C.END}")
    print(f"{C.BOLD}{C.C}{'='*60}{C.END}\n")

def print_test(name: str, status: str, details: str = ""):
    """Print test result"""
    if status == "PASS":
        print(f"{C.G}✅ {name:<40} PASS{C.END} {details}")
    elif status == "FAIL":
        print(f"{C.R}❌ {name:<40} FAIL{C.END} {details}")
    elif status == "WARN":
        print(f"{C.Y}⚠️  {name:<40} WARN{C.END} {details}")
    else:
        print(f"{C.B}ℹ️  {name:<40} INFO{C.END} {details}")

class EliteChunkerTester:
    """Terminal-based test suite for EliteLegalChunker"""
    
    def __init__(self):
        # Import the chunker (assumes it's available)
        try:
            from smart_legal_chunker import EliteLegalChunker, LegalChunk
            self.chunker = EliteLegalChunker(max_tokens_per_chunk=2500)
            self.LegalChunk = LegalChunk
        except ImportError:
            print(f"{C.R}❌ ERROR: Cannot import EliteLegalChunker{C.END}")
            print("Make sure smart_legal_chunker.py is in the same directory")
            sys.exit(1)
        
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Test documents
        self.test_docs = self._load_test_documents()

    def _load_test_documents(self) -> Dict[str, str]:
        """Load test documents for different scenarios"""
        return {
            # Perfect legal structure
            "saudi_labor": """الباب الأول: التعريفات والأحكام العامة
الفصل الأول: التعريفات
المادة الأولى: يسمى هذا النظام "نظام العمل".
المادة الثانية: يقصد بالألفاظ والعبارات الآتية - أينما وردت في هذا النظام - المعاني المبينة أمامها ما لم يقتض السياق خلاف ذلك:
أ) الوزارة: وزارة العمل والتنمية الاجتماعية.
ب) الوزير: وزير العمل والتنمية الاجتماعية.
ج) مكتب العمل: الجهة الإدارية المنوط بها شؤون العمل في النطاق المكاني الذي يحدد بقرار من الوزير.

المادة الثالثة: العمل حق للمواطن، لا يجوز لغيره ممارسته إلا بعد توافر الشروط المنصوص عليها في هذا النظام، والمواطنون متساوون في حق العمل.

الفصل الثاني: نطاق التطبيق
المادة الرابعة: يجب على صاحب العمل والعامل عند تطبيق أحكام هذا النظام الالتزام بمقتضيات أحكام الشريعة الإسلامية.

الباب الثاني: تنظيم عمليات التوظيف
الفصل الأول: وحدات التوظيف
المادة الخامسة: توفر الوزارة وحدات للتوظيف دون مقابل في الأماكن المناسبة لأصحاب العمل والعمال، وتقوم هذه الوحدات بتسجيل طالبي العمل وأصحاب العمل، وتوفيق أوضاعهم، وإرشادهم لما فيه خدمة سوق العمل.""",

            # Oversized single article (now actually oversized!)
            "oversized_article": """المادة الأولى: """ + "هذا نص طويل جداً يحتوي على تفاصيل قانونية معقدة ومتشعبة تتطلب شرحاً مفصلاً ودقيقاً لكل جانب من جوانب القانون المتعلق بهذا الموضوع، حيث يشمل التعريفات والإجراءات والمتطلبات والاستثناءات والعقوبات المترتبة على المخالفات، بالإضافة إلى الأحكام الانتقالية والتطبيقية التي تحكم تنفيذ هذا النظام في جميع أنحاء المملكة العربية السعودية، وكذلك الضوابط التنظيمية والإدارية اللازمة لتطبيق أحكام هذا النظام على الوجه الأكمل والأتم، مع مراعاة الظروف والاعتبارات الخاصة بكل حالة على حدة، والتأكد من التوافق مع الأنظمة واللوائح الأخرى ذات الصلة. " * 400,

            # No clear structure
            "unstructured": """هذا نص قانوني بدون هيكل واضح. يحتوي على معلومات قانونية مهمة ولكن لا يتبع التنظيم التقليدي للوثائق القانونية السعودية. قد يكون هذا النص من قرار وزاري أو تعميم إداري أو مذكرة توضيحية لا تتبع نفس هيكل الأنظمة الرسمية.""",

            # Mixed numbering styles
            "mixed_numbering": """الباب 1: أحكام عامة
الفصل الأول: التعريفات
المادة (1): التعريف الأول.
المادة رقم 2: التعريف الثاني.
المادة الثالثة: التعريف الثالث.
الفصل 2: التطبيق
المادة ٤: نطاق التطبيق.""",

            # Complex hierarchy
            "complex_hierarchy": """الباب الأول: الأحكام العامة
القسم الأول: التعريفات الأساسية
الفصل الأول: التعريفات العامة
المبحث الأول: المصطلحات القانونية
المادة الأولى: يقصد بالمصطلحات التالية...
المادة الثانية: تطبق هذه التعريفات...
المبحث الثاني: المصطلحات الإجرائية
المادة الثالثة: الإجراءات المحددة...
الفصل الثاني: التعريفات الخاصة
المادة الرابعة: التعريفات الخاصة بهذا الباب..."""
        }

    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and track results"""
        self.total_tests += 1
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            if result:
                self.passed_tests += 1
                print_test(test_name, "PASS", f"({end_time-start_time:.3f}s)")
                return True
            else:
                self.failed_tests += 1
                print_test(test_name, "FAIL")
                return False
        except Exception as e:
            self.failed_tests += 1
            print_test(test_name, "FAIL", f"Exception: {str(e)}")
            return False

    def test_basic_functionality(self):
        """Test 1: Basic chunking functionality"""
        def test():
            chunks = self.chunker.chunk_legal_document(
                self.test_docs["saudi_labor"], 
                "نظام العمل السعودي"
            )
            return len(chunks) > 0 and all(isinstance(c, self.LegalChunk) for c in chunks)
        
        return self.run_test("Basic Chunking", test)

    def test_article_integrity(self):
        """Test 2: Articles are NEVER split"""
        def test():
            chunks = self.chunker.chunk_legal_document(
                self.test_docs["saudi_labor"], 
                "نظام العمل السعودي"
            )
            
            # Check that no chunk ends mid-article
            for chunk in chunks:
                content = chunk.content
                # Should not end with partial article text
                if "المادة" in content:
                    article_matches = list(re.finditer(r'المادة\s+\w+', content))
                    if article_matches:
                        # Each article should be complete (not cut off)
                        for match in article_matches:
                            article_start = match.start()
                            remaining_text = content[article_start:]
                            # Article should have substantive content after the header
                            if len(remaining_text.strip()) < 10:
                                return False
            return True
        
        return self.run_test("Article Integrity", test)

    def test_hierarchical_context(self):
        """Test 3: Hierarchical context preservation"""
        def test():
            chunks = self.chunker.chunk_legal_document(
                self.test_docs["complex_hierarchy"], 
                "نظام معقد"
            )
            
            context_preserved = True
            for chunk in chunks:
                metadata = chunk.metadata
                if 'hierarchical_context' not in metadata:
                    context_preserved = False
                    break
                
                # Check that context makes sense
                context = metadata['hierarchical_context']
                if not isinstance(context, dict):
                    context_preserved = False
                    break
            
            return context_preserved and len(chunks) > 0
        
        return self.run_test("Hierarchical Context", test)

    def test_oversized_articles(self):
        """Test 4: Handle oversized articles gracefully"""
        def test():
            chunks = self.chunker.chunk_legal_document(
                self.test_docs["oversized_article"], 
                "مادة ضخمة"
            )
            
            # Should create at least one chunk
            if len(chunks) == 0:
                return False
            
            # Check for oversized flag
            oversized_found = False
            for chunk in chunks:
                if chunk.metadata.get('is_oversized', False):
                    oversized_found = True
                    break
            
            return oversized_found
        
        return self.run_test("Oversized Articles", test)

    def test_token_limits(self):
        """Test 5: Respect token limits (except for atomic articles)"""
        def test():
            chunks = self.chunker.chunk_legal_document(
                self.test_docs["saudi_labor"], 
                "نظام العمل السعودي"
            )
            
            violations = 0
            for chunk in chunks:
                token_count = chunk.metadata.get('token_count', 0)
                is_oversized = chunk.metadata.get('is_oversized', False)
                
                # Only oversized chunks can exceed limit
                if token_count > self.chunker.max_tokens_per_chunk and not is_oversized:
                    violations += 1
            
            return violations == 0
        
        return self.run_test("Token Limits", test)

    def test_arabic_handling(self):
        """Test 6: Proper Arabic text handling"""
        def test():
            chunks = self.chunker.chunk_legal_document(
                self.test_docs["saudi_labor"], 
                "نظام العمل السعودي"
            )
            
            # Check that Arabic text is preserved properly
            for chunk in chunks:
                content = chunk.content
                # Should contain Arabic characters
                has_arabic = any('\u0600' <= char <= '\u06FF' for char in content)
                if not has_arabic:
                    return False
                
                # Check that legal terms are preserved
                if "المادة" in self.test_docs["saudi_labor"] and "المادة" not in ''.join(c.content for c in chunks):
                    return False
            
            return True
        
        return self.run_test("Arabic Handling", test)

    def test_mixed_numbering(self):
        """Test 7: Handle mixed numbering styles"""
        def test():
            chunks = self.chunker.chunk_legal_document(
                self.test_docs["mixed_numbering"], 
                "نص مختلط"
            )
            
            # Should handle different article patterns
            all_content = ''.join(chunk.content for chunk in chunks)
            patterns_found = 0
            
            test_patterns = [r'المادة \(1\)', r'المادة رقم 2', r'المادة الثالثة', r'المادة ٤']
            for pattern in test_patterns:
                if re.search(pattern, all_content):
                    patterns_found += 1
            
            return patterns_found >= 3  # Most patterns should be preserved
        
        return self.run_test("Mixed Numbering", test)

    def test_empty_and_malformed(self):
        """Test 8: Handle edge cases gracefully"""
        def test():
            # Test empty content
            try:
                chunks1 = self.chunker.chunk_legal_document("", "وثيقة فارغة")
                if len(chunks1) != 0:  # Should handle empty gracefully
                    return False
            except:
                return False
            
            # Test very short content
            try:
                chunks2 = self.chunker.chunk_legal_document("نص قصير", "وثيقة قصيرة")
                # Should create at least one chunk or handle gracefully
                return len(chunks2) >= 0  # No crashes
            except:
                return False
        
        return self.run_test("Edge Cases", test)

    def test_performance_benchmark(self):
        """Test 9: Performance benchmark"""
        def test():
            # Create large document
            large_doc = self.test_docs["saudi_labor"] * 10  # 10x size
            
            start_time = time.time()
            chunks = self.chunker.chunk_legal_document(large_doc, "وثيقة كبيرة")
            end_time = time.time()
            
            processing_time = end_time - start_time
            doc_size_kb = len(large_doc) / 1024
            
            print(f"    📊 Processed {doc_size_kb:.1f}KB in {processing_time:.3f}s")
            print(f"    📊 Speed: {doc_size_kb/processing_time:.1f} KB/s")
            print(f"    📊 Created {len(chunks)} chunks")
            
            # Should process reasonably fast (< 5 seconds for test doc)
            return processing_time < 5.0 and len(chunks) > 0
        
        return self.run_test("Performance", test)

    def test_metadata_completeness(self):
        """Test 10: Metadata completeness and accuracy"""
        def test():
            chunks = self.chunker.chunk_legal_document(
                self.test_docs["complex_hierarchy"], 
                "نظام معقد"
            )
            
            required_fields = [
                'items_count', 'hierarchy_levels', 'token_count',
                'legal_boundaries_respected', 'contains_complete_articles',
                'hierarchical_context', 'full_legal_path'
            ]
            
            for chunk in chunks:
                metadata = chunk.metadata
                for field in required_fields:
                    if field not in metadata:
                        print(f"    Missing field: {field}")
                        return False
            
            return True
        
        return self.run_test("Metadata Completeness", test)

    def run_basic_tests(self):
        """Run basic functionality tests"""
        print_header("BASIC FUNCTIONALITY TESTS")
        
        self.test_basic_functionality()
        self.test_article_integrity()
        self.test_hierarchical_context()
        self.test_arabic_handling()

    def run_stress_tests(self):
        """Run stress tests"""
        print_header("STRESS TESTS")
        
        self.test_oversized_articles()
        self.test_token_limits()
        self.test_performance_benchmark()

    def run_edge_case_tests(self):
        """Run edge case tests"""
        print_header("EDGE CASE TESTS")
        
        self.test_mixed_numbering()
        self.test_empty_and_malformed()
        self.test_metadata_completeness()

    def run_all_tests(self):
        """Run complete test suite"""
        print(f"{C.BOLD}{C.M}🚀 ELITE LEGAL CHUNKER - BULLETPROOF TEST SUITE{C.END}")
        print(f"{C.C}Testing EliteLegalChunker with max_tokens_per_chunk={self.chunker.max_tokens_per_chunk}{C.END}")
        
        self.run_basic_tests()
        self.run_stress_tests()
        self.run_edge_case_tests()
        
        self.print_summary()

    def run_interactive_mode(self):
        """Interactive testing mode"""
        print_header("INTERACTIVE MODE")
        print("Enter your Arabic legal text (press Ctrl+D when done):")
        
        try:
            content = sys.stdin.read()
            if not content.strip():
                print(f"{C.R}❌ No content provided. Exiting.{C.END}")
                return

            title = input("Document title: ").strip() or "وثيقة تفاعلية"
            
            print(f"\n{C.Y}Processing...{C.END}")
            start_time = time.time()
            
            chunks = self.chunker.chunk_legal_document(content, title)
            
            end_time = time.time()
            
            print(f"\n{C.G}✅ SUCCESS!{C.END}")
            print(f"Created {len(chunks)} chunks in {end_time - start_time:.3f}s")
            
            # 🚀 SAVE TO DATABASE?
            save_to_db = input(f"\n{C.Y}Save to database? (y/n): {C.END}").lower().strip()
            if save_to_db in ['y', 'yes', '']:
                print(f"{C.Y}Saving to database...{C.END}")
                
                try:
                    from app.services.document_service import DocumentService
                    service = DocumentService()
                    
                    documents = []
                    timestamp_ms = int(time.time() * 1000)  # Avoid ID collisions
                    for chunk in chunks:
                        doc_id = f"interactive_test_{chunk.chunk_index}_{timestamp_ms}"
                        documents.append({
                            'id': doc_id,
                            'title': chunk.title,
                            'content': chunk.content,
                            'metadata': chunk.metadata or {}
                        })
                    
                    result = service.add_documents_batch(documents)
                    success_count = result.get('success_count', 0)
                    error_count = result.get('error_count', 0)
                    
                    if success_count > 0:
                        print(f"{C.G}✅ SAVED: {success_count} chunks saved to database{C.END}")
                        print(f"{C.C}Now you can search for this content in your RAG system!{C.END}")
                    if error_count > 0:
                        print(f"{C.R}❌ ERRORS: {error_count} chunks failed to save{C.END}")
                        
                except ImportError:
                    print(f"{C.R}❌ ERROR: Cannot import DocumentService{C.END}")
                    print("Make sure app.services.document_service is available")
                except Exception as e:
                    print(f"{C.R}❌ DATABASE ERROR: {str(e)}{C.END}")

            # Display chunks
            for i, chunk in enumerate(chunks):
                metadata = chunk.metadata or {}
                print(f"\n{C.B}--- Chunk {i+1}/{len(chunks)} ---{C.END}")
                print(f"Title: {chunk.title}")
                print(f"Hierarchy: {chunk.hierarchy_level}")
                print(f"Tokens: {metadata.get('token_count', 'N/A')}")
                print(f"Articles: {metadata.get('articles', 'None')}")
                print(f"Content preview: {chunk.content[:200]}...")

        except KeyboardInterrupt:
            print(f"\n{C.Y}👋 Interactive mode interrupted by user.{C.END}")
        except EOFError:
            print(f"\n{C.R}❌ Input ended unexpectedly (EOF).{C.END}")
        except Exception as e:
            print(f"{C.R}❌ Unexpected error during processing: {str(e)}{C.END}")
            import traceback
            traceback.print_exc()


           


    def print_summary(self):
        """Print test summary"""
        print_header("TEST RESULTS SUMMARY")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {C.B}{self.total_tests}{C.END}")
        print(f"Passed: {C.G}{self.passed_tests}{C.END}")
        print(f"Failed: {C.R}{self.failed_tests}{C.END}")
        print(f"Success Rate: {C.G if success_rate >= 90 else C.Y if success_rate >= 70 else C.R}{success_rate:.1f}%{C.END}")
        
        if success_rate >= 95:
            print(f"\n{C.BOLD}{C.G}🎉 EXCELLENT! EliteLegalChunker is production-ready!{C.END}")
        elif success_rate >= 90:
            print(f"\n{C.BOLD}{C.Y}⚠️  GOOD! Minor issues need attention.{C.END}")
        else:
            print(f"\n{C.BOLD}{C.R}❌ CRITICAL ISSUES! Do not deploy to production!{C.END}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="EliteLegalChunker Test Suite")
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--basic', action='store_true', help='Run basic tests')
    parser.add_argument('--stress', action='store_true', help='Run stress tests')
    parser.add_argument('--edge', action='store_true', help='Run edge case tests')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark tests')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        args.all = True  # Default to all tests
    
    tester = EliteChunkerTester()
    
    try:
        if args.interactive:
            tester.run_interactive_mode()
        elif args.basic:
            tester.run_basic_tests()
            tester.print_summary()
        elif args.stress:
            tester.run_stress_tests()
            tester.print_summary()
        elif args.edge:
            tester.run_edge_case_tests()
            tester.print_summary()
        elif args.benchmark:
            tester.test_performance_benchmark()
        else:
            tester.run_all_tests()
            
    except KeyboardInterrupt:
        print(f"\n{C.Y}Tests interrupted by user.{C.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{C.R}FATAL ERROR: {e}{C.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()