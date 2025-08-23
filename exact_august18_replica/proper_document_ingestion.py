#!/usr/bin/env python3
"""
🔧 PROPER DOCUMENT INGESTION PIPELINE
=====================================
This is the RIGHT WAY to add documents - ensures embeddings are always generated
Uses your existing DocumentService architecture - NO direct database manipulation
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Import your existing services
from app.storage.sqlite_store import SqliteVectorStore
from app.services.document_service import DocumentService
from openai import AsyncOpenAI
from app.core.config import settings


class ProperDocumentIngestion:
    """
    The RIGHT way to add documents to your system
    Always generates embeddings - no more missing embeddings!
    """
    
    def __init__(self):
        self.storage = None
        self.document_service = None
        self.ai_client = None
        
    async def initialize(self):
        """Initialize all services properly"""
        print("🔧 Initializing Saudi Legal AI Document Pipeline...")
        
        # Initialize vector store
        self.storage = SqliteVectorStore("data/vectors.db")
        await self.storage.initialize()
        
        # Initialize AI client with proper error handling
        if not settings.openai_api_key:
            raise ValueError("❌ OPENAI_API_KEY not set in environment/settings")
            
        self.ai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Initialize document service (this ensures embeddings)
        self.document_service = DocumentService(self.storage, self.ai_client)
        
        print("✅ All services initialized with embedding support")
        
    async def add_commercial_agencies_law_properly(self):
        """
        Add commercial agencies law the RIGHT way
        This will automatically generate embeddings
        """
        print("\n🏛️ Adding Commercial Agencies Law (PROPER METHOD)")
        print("=" * 55)
        
        # Your commercial agencies content
        commercial_content = """المادة (1):
لا يجوز لغير السعوديين سواء بصفة أشخاص طبيعيين أو معنويين أن يكونوا وكلاء تجاريين في المملكة العربية السعودية.

المادة (5):
تحدد رسوم القيد في سجل الوكالات كالآتي:
خمسمائة ريال للتاجر الفرد والشركة.
وتدفع الرسوم لمرة واحدة.

المادة (6):
يجب على الوكيل التجاري أن يقدم طلب القيد في سجل الوكالات خلال ستين يوماً من تاريخ إبرام عقد الوكالة.

المادة (10):
تسري أحكام هذا النظام على جميع عقود الوكالة التجارية المبرمة بعد نفاذه."""
        
        # Prepare document in the format DocumentService expects
        documents = [{
            'id': 'commercial_agencies_law_2024',
            'title': 'نظام الوكالات التجارية السعودي',
            'content': commercial_content,
            'metadata': {
                'source': 'official_saudi_legal_system',
                'authority': 'وزارة التجارة',
                'type': 'regulation',
                'categories': ['تجاري', 'وكالات', 'استثمار'],
                'language': 'arabic',
                'jurisdiction': 'saudi_arabia'
            }
        }]
        
        print(f"📄 Document prepared:")
        print(f"   📋 Title: {documents[0]['title']}")
        print(f"   🔢 Content length: {len(commercial_content):,} characters")
        print(f"   🏷️ Metadata: {len(documents[0]['metadata'])} fields")
        
        # Add using proper DocumentService (guarantees embeddings)
        print("\n🚀 Processing through DocumentService...")
        result = await self.document_service.add_documents_batch(documents)
        
        if result['success']:
            print(f"✅ SUCCESS! Document processed properly")
            print(f"   📊 Processed: {result.get('successful', 0)} documents")
            print(f"   🧠 Embeddings: Generated automatically")
            print(f"   📦 Chunks: Created using SmartLegalChunker")
            print(f"   🔍 RAG Ready: Can now be found by semantic search")
            
            if result.get('errors', 0) > 0:
                print(f"   ⚠️ Errors: {result['errors']}")
                for error in result.get('error_details', []):
                    print(f"      ❌ {error}")
                    
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
            return False
            
        return True
    
    async def verify_proper_ingestion(self):
        """Verify the document was added with embeddings"""
        print("\n🔍 VERIFICATION: Checking if document has embeddings")
        print("=" * 55)
        
        import sqlite3
        
        # Check database directly
        conn = sqlite3.connect('data/vectors.db')
        cursor = conn.cursor()
        
        # Check for our document
        cursor.execute("""
            SELECT id, title, 
                   CASE WHEN embedding IS NOT NULL THEN 'YES' ELSE 'NO' END as has_embedding,
                   substr(content, 1, 100) as content_preview
            FROM chunks 
            WHERE content LIKE '%خمسمائة ريال%'
            ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        
        if results:
            print(f"✅ Found {len(results)} chunks with fee information:")
            for chunk_id, title, has_embedding, content_preview in results:
                print(f"\n   📄 Chunk ID: {chunk_id}")
                print(f"   📋 Title: {title}")
                print(f"   🧠 Has Embedding: {has_embedding}")
                print(f"   📝 Content: {content_preview}...")
                
                if has_embedding == 'YES':
                    print(f"   🎯 RAG STATUS: Ready for semantic search ✅")
                else:
                    print(f"   🎯 RAG STATUS: Missing embedding ❌")
        else:
            print("❌ No chunks found with fee information")
            
        # Check total chunks with embeddings
        cursor.execute("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
        embedded_chunks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cursor.fetchone()[0]
        
        print(f"\n📊 OVERALL STATUS:")
        print(f"   📦 Total chunks: {total_chunks}")
        print(f"   🧠 With embeddings: {embedded_chunks}")
        print(f"   📈 Embedding rate: {embedded_chunks/total_chunks*100:.1f}%")
        
        conn.close()
        
        return embedded_chunks == total_chunks
    
    async def test_rag_search(self):
        """Test if RAG can now find the answer"""
        print("\n🧪 RAG SEARCH TEST")
        print("=" * 25)
        
        test_query = "ماهي رسوم القيد في سجل الوكالات؟"
        print(f"🔍 Query: {test_query}")
        
        try:
            # Import your RAG engine
            from rag_engine import rag_engine
            
            print("🤖 Sending query to RAG engine...")
            
            # Test the search (collect response)
            response_parts = []
            async for chunk in rag_engine.ask_question_streaming(test_query):
                response_parts.append(chunk)
            
            full_response = ''.join(response_parts)
            
            print(f"\n📝 RAG Response:")
            print(f"{full_response}")
            
            # Check if response contains the answer
            has_fee_info = 'خمسمائة ريال' in full_response
            has_specific_answer = 'رسوم القيد' in full_response
            
            print(f"\n🎯 ANALYSIS:")
            print(f"   💰 Contains fee amount: {'✅' if has_fee_info else '❌'}")
            print(f"   📋 Answers question: {'✅' if has_specific_answer else '❌'}")
            
            if has_fee_info and has_specific_answer:
                print(f"   🏆 RAG SYSTEM: Working perfectly!")
                return True
            else:
                print(f"   ⚠️ RAG SYSTEM: Still needs configuration")
                return False
                
        except Exception as e:
            print(f"❌ RAG test failed: {e}")
            return False


async def main():
    """Main execution flow"""
    print("🇸🇦 SAUDI LEGAL AI - PROPER DOCUMENT INGESTION")
    print("=" * 60)
    
    ingestion = ProperDocumentIngestion()
    
    try:
        # Step 1: Initialize services
        await ingestion.initialize()
        
        # Step 2: Add document properly (with embeddings)
        success = await ingestion.add_commercial_agencies_law_properly()
        
        if not success:
            print("❌ Document ingestion failed - stopping")
            return
        
        # Step 3: Verify embeddings were created
        embeddings_ok = await ingestion.verify_proper_ingestion()
        
        if not embeddings_ok:
            print("⚠️ Some chunks missing embeddings - check logs")
        
        # Step 4: Test RAG search
        rag_ok = await ingestion.test_rag_search()
        
        # Final summary
        print(f"\n🏁 FINAL RESULTS:")
        print(f"   📄 Document Added: {'✅' if success else '❌'}")
        print(f"   🧠 Embeddings: {'✅' if embeddings_ok else '❌'}")
        print(f"   🔍 RAG Search: {'✅' if rag_ok else '❌'}")
        
        if success and embeddings_ok and rag_ok:
            print(f"\n🎉 SUCCESS! Your RAG system is now working perfectly!")
            print(f"   ✅ No more missing embeddings")
            print(f"   ✅ Questions about fees will get proper answers")
            print(f"   ✅ Use this method for all future documents")
        else:
            print(f"\n⚠️ Some issues remain - check the output above")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())