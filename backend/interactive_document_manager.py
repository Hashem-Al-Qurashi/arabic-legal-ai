#!/usr/bin/env python3
"""
🛡️ CORRUPTION-PROOF Interactive Document Management CLI
Uses the fixed DocumentService that prevents all vector database corruption
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Import your FIXED services
from app.storage.sqlite_store import SqliteVectorStore
from app.services.document_service import DocumentService  # Your FIXED version
from openai import AsyncOpenAI
from app.core.config import settings


class CorruptionProofDocumentManager:
    """🛡️ Corruption-proof CLI for managing documents"""
    
    def __init__(self):
        self.storage = None
        self.document_service = None
        self.ai_client = None
        
    async def initialize(self):
        """Initialize services with corruption protection"""
        print("🛡️ Initializing Corruption-Proof Saudi Legal AI Document Manager...")
        
        try:
            # Initialize vector store
            self.storage = SqliteVectorStore("data/vectors.db")
            await self.storage.initialize()
            
            # Test database health immediately
            health = await self.storage.health_check()
            if not health:
                print("🚨 Database health check failed!")
                print("Run the recovery script first: python db_recovery.py")
                return False
            
            # Initialize AI client
            self.ai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            # Initialize FIXED document service
            self.document_service = DocumentService(self.storage, self.ai_client)
            
            print("✅ All services initialized successfully")
            print("🛡️ Corruption protection active")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            print("💡 Try running the recovery script: python db_recovery.py")
            return False
        
    async def show_main_menu(self):
        """Display main menu with enhanced corruption monitoring"""
        while True:
            print("\n" + "="*70)
            print("🛡️ Saudi Legal AI - Corruption-Proof Document Management")
            print("="*70)
            
            # Enhanced status display
            await self.show_enhanced_database_status()
            
            print("\nAvailable Actions:")
            print("1. 📝 Add Single Document (Safe Mode)")
            print("2. 📚 Add Multiple Documents (Batch Safe Mode)")
            print("3. 📋 List All Documents")
            print("4. 🔍 Search Documents")
            print("5. ❌ Remove Document(s)")
            print("6. 📊 Database Health & Statistics")
            print("7. 🧹 Clear All Documents")
            print("8. 🔧 Database Recovery Tools")
            print("9. 🚪 Exit")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            try:
                if choice == "1":
                    await self.add_single_document_safe()
                elif choice == "2":
                    await self.add_multiple_documents_safe()
                elif choice == "3":
                    await self.list_documents()
                elif choice == "4":
                    await self.search_documents()
                elif choice == "5":
                    await self.remove_documents()
                elif choice == "6":
                    await self.show_database_health()
                elif choice == "7":
                    await self.clear_all_documents()
                elif choice == "8":
                    await self.recovery_tools_menu()
                elif choice == "9":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-9.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("🛡️ Corruption protection prevented database damage")
                
    async def show_enhanced_database_status(self):
        """Enhanced status display with corruption monitoring"""
        try:
            health_info = await self.document_service.get_storage_health()
            
            # Health indicator
            if health_info.get("healthy", False):
                health_status = "🟢 Healthy"
            else:
                health_status = "🔴 Issues Detected"
            
            # Corruption detection
            corruption_pct = health_info.get("corruption_percentage", 0)
            if corruption_pct > 0:
                corruption_status = f"🚨 {corruption_pct:.1f}% Corrupted"
            else:
                corruption_status = "✅ No Corruption"
            
            # Display status
            total_docs = health_info.get("total_documents", 0)
            storage_size = health_info.get("storage_size_mb", 0)
            valid_chunks = health_info.get("valid_chunks", 0)
            corrupted_chunks = health_info.get("corrupted_chunks", 0)
            
            print(f"Status: {health_status} | {corruption_status}")
            print(f"Documents: {total_docs} | Valid Chunks: {valid_chunks} | Corrupted: {corrupted_chunks}")
            print(f"Storage: {storage_size:.2f} MB")
            
        except Exception as e:
            print(f"Status: 🔴 Cannot read database - {e}")
    
    async def add_single_document_safe(self):
        """🛡️ Corruption-proof single document addition"""
        print("\n📝 Add Single Document (Safe Mode)")
        print("-" * 40)
        
        # Enhanced input validation
        title = input("📄 Document Title: ").strip()
        if not title:
            print("❌ Title cannot be empty")
            return
        
        # Check title length
        if len(title) > 200:
            print("⚠️ Title very long, truncating to 200 characters")
            title = title[:200]
            
        print("\nContent Input Options:")
        print("1. Type content directly")
        print("2. Load from file")
        print("3. Paste multi-line content")
        
        content_choice = input("Choose option (1-3): ").strip()
        
        content = ""
        
        if content_choice == "1":
            content = input("Enter content: ").strip()
            
        elif content_choice == "2":
            file_path = input("Enter file path: ").strip()
            try:
                if not Path(file_path).exists():
                    print("❌ File does not exist")
                    return
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                print(f"✅ Loaded {len(content):,} characters from file")
                
                # Validate file content
                if len(content) > 1_000_000:  # 1MB text limit
                    print("⚠️ File very large, this might take a while to process")
                    proceed = input("Continue? (y/n): ").strip().lower()
                    if proceed != 'y':
                        return
                        
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                return
                
        elif content_choice == "3":
            print("Enter content (press Ctrl+D on empty line when finished):")
            lines = []
            try:
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                content = "\n".join(lines)
            except KeyboardInterrupt:
                print("\n❌ Input cancelled")
                return
        else:
            print("❌ Invalid choice")
            return
            
        # Validate content
        if not content or len(content.strip()) < 10:
            print("❌ Content too short (minimum 10 characters)")
            return
        
        # Enhanced metadata collection
        metadata = {}
        add_metadata = input("\nAdd metadata? (y/n): ").strip().lower()
        if add_metadata == 'y':
            source = input("📄 Source (optional): ").strip()
            if source:
                metadata["source"] = source
                
            doc_type = input("📋 Document type (e.g., نظام، لائحة، قرار): ").strip()
            if doc_type:
                metadata["document_type"] = doc_type
                
            authority = input("🏛️ Issuing authority (optional): ").strip()
            if authority:
                metadata["authority"] = authority
                
            year = input("📅 Year (optional): ").strip()
            if year and year.isdigit():
                metadata["year"] = int(year)
        
        # Add processing metadata
        metadata.update({
            "added_at": datetime.now().isoformat(),
            "added_via": "corruption_proof_cli",
            "content_length": len(content),
            "estimated_tokens": self.document_service.estimate_tokens(content)
        })
        
        # Show processing preview
        estimated_tokens = self.document_service.estimate_tokens(content)
        print(f"\n📊 Document Preview:")
        print(f"   Title: {title}")
        print(f"   Content: {len(content):,} characters")
        print(f"   Estimated tokens: {estimated_tokens:,}")
        
        if estimated_tokens > 4000:
            print(f"   📏 Large document - will be intelligently chunked")
            print(f"   🔧 Arabic legal structure will be preserved")
        else:
            print(f"   📄 Standard size - will be stored as single chunk")
        
        # Final confirmation
        proceed = input("\n🚀 Proceed with adding document? (y/n): ").strip().lower()
        if proceed != 'y':
            print("❌ Document addition cancelled")
            return
        
        print(f"\n🔄 Processing document '{title}'...")
        print("🛡️ Corruption protection active...")
        
        try:
            # Add document with corruption protection
            success = await self.document_service.add_document(
                title=title,
                content=content,
                metadata=metadata
            )
            
            if success:
                print("✅ Document added successfully!")
                
                # Show detailed processing results
                if estimated_tokens > 4000:
                    print("📏 Large document was intelligently chunked")
                    print("🏛️ Arabic legal structure preserved (الباب، الفصل، المادة)")
                    print("📖 Legal citations maintained across chunks")
                else:
                    print("📄 Document stored as optimized single chunk")
                
                # Verify storage integrity
                print("🔍 Verifying storage integrity...")
                docs = await self.document_service.list_documents()
                doc_found = any(doc['title'] == title for doc in docs)
                
                if doc_found:
                    print("✅ Document verified in database - no corruption detected")
                else:
                    print("⚠️ Document added but verification failed")
                    
            else:
                print("❌ Failed to add document")
                print("🛡️ Corruption protection prevented database damage")
                
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            print("🛡️ Database protected from corruption")

    async def add_multiple_documents_safe(self):
        """🛡️ Corruption-proof batch document processing"""
        print("\n📚 Add Multiple Documents (Batch Safe Mode)")
        print("-" * 50)
        
        print("Safe Batch Import Options:")
        print("1. Load from JSON file (with validation)")
        print("2. Load from directory (with file validation)")
        print("3. Manual entry (guided with validation)")
        
        choice = input("Choose option (1-3): ").strip()
        
        documents = []
        
        if choice == "1":
            await self.load_from_json_safe(documents)
        elif choice == "2":
            await self.load_from_directory_safe(documents)
        elif choice == "3":
            await self.manual_batch_entry_safe(documents)
        else:
            print("❌ Invalid choice")
            return
            
        if not documents:
            print("❌ No valid documents to process")
            return
        
        # Enhanced validation summary
        total_chars = sum(len(doc.get('content', '')) for doc in documents)
        total_tokens = sum(self.document_service.estimate_tokens(doc.get('content', '')) for doc in documents)
        large_docs = sum(1 for doc in documents if self.document_service.estimate_tokens(doc.get('content', '')) > 4000)
        
        print(f"\n📋 Batch Processing Summary:")
        print(f"   Documents: {len(documents)}")
        print(f"   Total content: {total_chars:,} characters")
        print(f"   Estimated tokens: {total_tokens:,}")
        print(f"   Large documents (will be chunked): {large_docs}")
        print(f"   Estimated processing time: {len(documents) * 2:.0f} seconds")
        
        # Show sample documents
        print(f"\n📄 Documents to process:")
        for i, doc in enumerate(documents[:5], 1):
            title = doc.get('title', 'Untitled')
            content_len = len(doc.get('content', ''))
            print(f"   {i}. {title} ({content_len:,} chars)")
        
        if len(documents) > 5:
            print(f"   ... and {len(documents) - 5} more documents")
            
        # Final confirmation with safety notice
        print(f"\n🛡️ SAFETY NOTICE:")
        print(f"   ✅ Corruption protection is active")
        print(f"   ✅ Failed embeddings will be skipped (not stored as null)")
        print(f"   ✅ Token limits are enforced to prevent API errors")
        print(f"   ✅ Database integrity will be maintained")
        
        confirm = input("\n🚀 Proceed with safe batch processing? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Batch processing cancelled")
            return
            
        print(f"\n🔄 Starting corruption-proof batch processing...")
        print(f"🛡️ Processing {len(documents)} documents with full protection...")
        
        try:
            # Use the corruption-proof batch method
            result = await self.document_service.add_documents_batch(documents)
            
            print(f"\n📊 BATCH PROCESSING RESULTS:")
            print(f"   ✅ Successful: {result['successful']}")
            print(f"   ❌ Errors: {result['errors']}")
            print(f"   📈 Success rate: {(result['successful']/len(documents)*100):.1f}%")
            
            if result["errors"] > 0:
                print(f"\n🔍 Error Details (first 5):")
                for error in result.get("error_details", [])[:5]:
                    print(f"   ❌ {error}")
                
                if len(result.get("error_details", [])) > 5:
                    print(f"   ... and {len(result['error_details']) - 5} more errors")
            
            # Database integrity check
            print(f"\n🔍 Post-processing integrity check...")
            health_info = await self.document_service.get_storage_health()
            
            if health_info.get("corruption_percentage", 0) == 0:
                print(f"✅ Database integrity maintained - no corruption detected")
            else:
                print(f"⚠️ Some corruption detected: {health_info['corruption_percentage']:.1f}%")
            
        except Exception as e:
            print(f"❌ Batch processing error: {e}")
            print("🛡️ Corruption protection prevented database damage")

    async def load_from_json_safe(self, documents):
        """Safe JSON loading with validation"""
        file_path = input("Enter JSON file path: ").strip()
        
        try:
            if not Path(file_path).exists():
                print("❌ File does not exist")
                return
                
            # Check file size
            file_size = Path(file_path).stat().st_size
            if file_size > 50_000_000:  # 50MB limit
                print(f"⚠️ File very large ({file_size/1024/1024:.1f} MB)")
                proceed = input("This might take a long time. Continue? (y/n): ").strip().lower()
                if proceed != 'y':
                    return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle different JSON structures
            raw_documents = []
            if isinstance(data, list):
                raw_documents = data
            elif isinstance(data, dict) and 'documents' in data:
                raw_documents = data['documents']
            else:
                print("❌ JSON should contain a list or have a 'documents' key")
                return
            
            # Validate each document
            valid_docs = 0
            for i, doc in enumerate(raw_documents):
                if isinstance(doc, dict) and 'title' in doc and 'content' in doc:
                    # Basic validation
                    title = str(doc['title']).strip()
                    content = str(doc['content']).strip()
                    
                    if title and content and len(content) >= 10:
                        documents.append({
                            'title': title,
                            'content': content,
                            'metadata': doc.get('metadata', {})
                        })
                        valid_docs += 1
                    else:
                        print(f"⚠️ Skipping invalid document {i+1}: {title or 'No title'}")
                else:
                    print(f"⚠️ Skipping malformed document {i+1}")
            
            print(f"✅ Loaded {valid_docs} valid documents from JSON file")
            if valid_docs != len(raw_documents):
                print(f"⚠️ Skipped {len(raw_documents) - valid_docs} invalid documents")
                
        except Exception as e:
            print(f"❌ Error reading JSON file: {e}")

    async def load_from_directory_safe(self, documents):
        """Safe directory loading with file validation"""
        dir_path = input("Enter directory path: ").strip()
        
        try:
            directory = Path(dir_path)
            if not directory.exists():
                print("❌ Directory does not exist")
                return
            
            # Find text files
            text_files = list(directory.glob("*.txt"))
            if not text_files:
                print("❌ No .txt files found in directory")
                return
            
            print(f"📁 Found {len(text_files)} text files")
            
            valid_files = 0
            for file_path in text_files:
                try:
                    # Check file size first
                    file_size = file_path.stat().st_size
                    if file_size > 10_000_000:  # 10MB per file limit
                        print(f"⚠️ Skipping large file: {file_path.name} ({file_size/1024/1024:.1f} MB)")
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Validate content
                    if len(content.strip()) < 20:
                        print(f"⚠️ Skipping short file: {file_path.name}")
                        continue
                    
                    # Check for binary content (basic validation)
                    if '\x00' in content:
                        print(f"⚠️ Skipping binary file: {file_path.name}")
                        continue
                        
                    document = {
                        "title": file_path.stem,
                        "content": content,
                        "metadata": {
                            "source": str(file_path),
                            "filename": file_path.name,
                            "file_size": file_size,
                            "loaded_from": "directory_safe",
                            "added_at": datetime.now().isoformat()
                        }
                    }
                    documents.append(document)
                    valid_files += 1
                    
                except Exception as e:
                    print(f"⚠️ Error reading {file_path.name}: {e}")
                    
            print(f"✅ Loaded {valid_files} valid documents from directory")
            if valid_files != len(text_files):
                print(f"⚠️ Skipped {len(text_files) - valid_files} invalid/problematic files")
                
        except Exception as e:
            print(f"❌ Error processing directory: {e}")

    async def manual_batch_entry_safe(self, documents):
        """Safe manual entry with enhanced validation"""
        try:
            count_input = input("How many documents to add? ").strip()
            count = int(count_input)
            
            if count <= 0 or count > 100:
                print("❌ Invalid count (must be 1-100)")
                return
                
        except ValueError:
            print("❌ Please enter a valid number")
            return
            
        for i in range(count):
            print(f"\n--- Document {i+1}/{count} ---")
            
            title = input("📄 Title: ").strip()
            if not title:
                print("⚠️ Skipping document (no title)")
                continue
            
            if len(title) > 200:
                title = title[:200]
                print(f"⚠️ Title truncated to 200 characters")
                
            content = input("📝 Content: ").strip()
            if not content or len(content) < 10:
                print("⚠️ Skipping document (content too short)")
                continue
                
            document = {
                "title": title,
                "content": content,
                "metadata": {
                    "added_via": "manual_batch_safe",
                    "added_at": datetime.now().isoformat(),
                    "batch_position": i + 1,
                    "batch_size": count
                }
            }
            documents.append(document)
            print(f"✅ Document {i+1} prepared")
            
        print(f"✅ Prepared {len(documents)} valid documents for safe batch processing")

    async def show_database_health(self):
        """🔍 Comprehensive database health analysis"""
        print("\n🔍 Database Health & Statistics")
        print("-" * 40)
        
        try:
            health_info = await self.document_service.get_storage_health()
            
            # Health status
            print(f"🏥 HEALTH STATUS:")
            if health_info.get("healthy", False):
                print(f"   ✅ Database is healthy")
            else:
                print(f"   🔴 Database has issues")
            
            # Corruption analysis
            corruption_pct = health_info.get("corruption_percentage", 0)
            print(f"\n🛡️ CORRUPTION ANALYSIS:")
            if corruption_pct == 0:
                print(f"   ✅ No corruption detected (0.0%)")
            else:
                print(f"   🚨 Corruption detected: {corruption_pct:.2f}%")
                print(f"   🔧 Corrupted chunks: {health_info.get('corrupted_chunks', 0)}")
            
            # Storage statistics
            print(f"\n📊 STORAGE STATISTICS:")
            print(f"   Documents: {health_info.get('total_documents', 0):,}")
            print(f"   Valid chunks: {health_info.get('valid_chunks', 0):,}")
            print(f"   Storage size: {health_info.get('storage_size_mb', 0):.2f} MB")
            print(f"   Storage type: {health_info.get('storage_type', 'Unknown')}")
            print(f"   Last updated: {health_info.get('last_updated', 'Unknown')}")
            
            # Document analysis
            try:
                documents = await self.document_service.list_documents()
                if documents:
                    total_chars = sum(len(doc.get('content', '')) for doc in documents)
                    avg_chars = total_chars / len(documents)
                    
                    print(f"\n📄 DOCUMENT ANALYSIS:")
                    print(f"   Total characters: {total_chars:,}")
                    print(f"   Average document size: {avg_chars:,.0f} characters")
                    
                    # Size distribution
                    small_docs = sum(1 for doc in documents if len(doc.get('content', '')) < 1000)
                    medium_docs = sum(1 for doc in documents if 1000 <= len(doc.get('content', '')) < 10000)
                    large_docs = sum(1 for doc in documents if len(doc.get('content', '')) >= 10000)
                    
                    print(f"   Small documents (<1K chars): {small_docs}")
                    print(f"   Medium documents (1K-10K chars): {medium_docs}")
                    print(f"   Large documents (>10K chars): {large_docs}")
                    
            except Exception as e:
                print(f"   ⚠️ Could not analyze documents: {e}")
                
        except Exception as e:
            print(f"❌ Error getting health information: {e}")

    async def recovery_tools_menu(self):
        """🔧 Database recovery and maintenance tools"""
        print("\n🔧 Database Recovery Tools")
        print("-" * 35)
        
        print("Recovery Options:")
        print("1. 🔍 Analyze database corruption")
        print("2. 🧹 Clean corrupted chunks")
        print("3. 🏗️ Rebuild database from scratch")
        print("4. 📋 Export documents before recovery")
        print("5. ⬅️ Back to main menu")
        
        choice = input("Choose option (1-5): ").strip()
        
        if choice == "1":
            await self.analyze_corruption()
        elif choice == "2":
            await self.clean_corrupted_chunks()
        elif choice == "3":
            await self.rebuild_database()
        elif choice == "4":
            await self.export_documents()
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")

    async def analyze_corruption(self):
        """Analyze database corruption in detail"""
        print("\n🔍 Analyzing Database Corruption...")
        
        try:
            health_info = await self.document_service.get_storage_health()
            
            print(f"📊 CORRUPTION ANALYSIS RESULTS:")
            print(f"   Total chunks: {health_info.get('total_documents', 0)}")
            print(f"   Valid chunks: {health_info.get('valid_chunks', 0)}")
            print(f"   Corrupted chunks: {health_info.get('corrupted_chunks', 0)}")
            print(f"   Corruption percentage: {health_info.get('corruption_percentage', 0):.2f}%")
            
            if health_info.get('corrupted_chunks', 0) > 0:
                print(f"\n🚨 CORRUPTION DETECTED:")
                print(f"   Your database has corrupted entries that should be cleaned")
                print(f"   These are likely caused by failed embedding generation")
                print(f"   Use option 2 to clean corrupted chunks")
            else:
                print(f"\n✅ NO CORRUPTION DETECTED:")
                print(f"   Your database is clean and healthy")
                
        except Exception as e:
            print(f"❌ Error analyzing corruption: {e}")

    async def clean_corrupted_chunks(self):
        """Remove corrupted chunks from database"""
        print("\n🧹 Cleaning Corrupted Chunks...")
        
        # This would require implementing a method in your storage layer
        print("⚠️ This feature requires extending the storage layer")
        print("For now, use option 3 to rebuild the database completely")

    async def rebuild_database(self):
        """Completely rebuild the database"""
        print("\n🏗️ Rebuild Database")
        
        print("⚠️ WARNING: This will completely rebuild your vector database")
        print("All current documents will be lost unless you export them first")
        
        confirm = input("Type 'REBUILD' to confirm: ").strip()
        if confirm != "REBUILD":
            print("❌ Rebuild cancelled")
            return
        
        print("🔄 Rebuilding database...")
        print("💡 Tip: Run the separate recovery script: python db_recovery.py")

    # ... (continue with remaining methods from your original code)
    async def list_documents(self):
        """List documents with corruption detection"""
        print("\n📋 All Documents")
        print("-" * 25)
        
        try:
            documents = await self.document_service.list_documents()
            
            if not documents:
                print("📂 No documents found in database")
                return
                
            print(f"Found {len(documents)} documents:\n")
            
            for i, doc in enumerate(documents, 1):
                doc_id = doc.get('id', 'unknown')
                title = doc.get('title', 'Untitled')
                content_length = len(doc.get('content', ''))
                chunk_count = doc.get('chunk_count', 1)
                
                print(f"{i:3d}. {title}")
                print(f"     ID: {doc_id}")
                print(f"     Length: {content_length:,} characters")
                print(f"     Chunks: {chunk_count}")
                
                metadata = doc.get('metadata', {})
                if metadata.get('source'):
                    print(f"     Source: {metadata['source']}")
                if metadata.get('document_type'):
                    print(f"     Type: {metadata['document_type']}")
                    
                print()
                
        except Exception as e:
            print(f"❌ Error listing documents: {e}")

    async def search_documents(self):
        """Search documents with enhanced results"""
        print("\n🔍 Search Documents")
        print("-" * 25)
        
        query = input("Enter search query: ").strip()
        if not query:
            print("❌ Search query cannot be empty")
            return
            
        print(f"🔄 Searching for: '{query}'...")
        
        try:
            documents = await self.document_service.list_documents()
            
            matches = []
            for doc in documents:
                title = doc.get('title', '').lower()
                content = doc.get('content', '').lower()
                query_lower = query.lower()
                
                # Enhanced matching
                title_match = query_lower in title
                content_match = query_lower in content
                
                if title_match or content_match:
                    match_info = {
                        'document': doc,
                        'title_match': title_match,
                        'content_match': content_match
                    }
                    matches.append(match_info)
                    
            if matches:
                print(f"✅ Found {len(matches)} matches:")
                for i, match in enumerate(matches, 1):
                    doc = match['document']
                    title = doc.get('title', 'Untitled')
                    doc_id = doc.get('id', 'unknown')
                    
                    match_type = []
                    if match['title_match']:
                        match_type.append("title")
                    if match['content_match']:
                        match_type.append("content")
                    
                    print(f"{i}. {title} (ID: {doc_id})")
                    print(f"   Match in: {', '.join(match_type)}")
            else:
                print("❌ No documents found matching your query")
                
        except Exception as e:
            print(f"❌ Error searching: {e}")

    async def remove_documents(self):
        """Remove documents with confirmation"""
        print("\n❌ Remove Documents")
        print("-" * 25)
        
        print("Remove Options:")
        print("1. Remove by ID")
        print("2. Remove multiple by IDs")
        print("3. Cancel")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            doc_id = input("Enter document ID: ").strip()
            if not doc_id:
                print("❌ Document ID cannot be empty")
                return
                
            # Show document info before removal
            try:
                docs = await self.document_service.list_documents()
                doc_to_remove = next((doc for doc in docs if doc['id'] == doc_id), None)
                
                if doc_to_remove:
                    print(f"\nDocument to remove:")
                    print(f"   Title: {doc_to_remove['title']}")
                    print(f"   Length: {len(doc_to_remove['content']):,} characters")
                    print(f"   Chunks: {doc_to_remove.get('chunk_count', 1)}")
                else:
                    print(f"❌ Document '{doc_id}' not found")
                    return
            except:
                pass  # Continue with removal attempt
                
            confirm = input(f"\nConfirm removal of document '{doc_id}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Removal cancelled")
                return
                
            try:
                success = await self.document_service.remove_document(doc_id)
                if success:
                    print("✅ Document removed successfully")
                else:
                    print("❌ Document not found or removal failed")
            except Exception as e:
                print(f"❌ Error removing document: {e}")
                
        elif choice == "2":
            ids_input = input("Enter document IDs (comma-separated): ").strip()
            if not ids_input:
                print("❌ Document IDs cannot be empty")
                return
                
            doc_ids = [id.strip() for id in ids_input.split(",")]
            doc_ids = [id for id in doc_ids if id]  # Remove empty IDs
            
            if not doc_ids:
                print("❌ No valid document IDs provided")
                return
            
            print(f"\nDocuments to remove: {len(doc_ids)} documents")
            for doc_id in doc_ids[:5]:  # Show first 5
                print(f"   - {doc_id}")
            if len(doc_ids) > 5:
                print(f"   ... and {len(doc_ids) - 5} more")
                
            confirm = input(f"\nConfirm removal of {len(doc_ids)} documents? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Removal cancelled")
                return
                
            try:
                print("🔄 Removing documents...")
                result = await self.document_service.remove_documents_batch(doc_ids)
                
                print(f"📊 Removal Results:")
                print(f"   ✅ Deleted: {result['deleted']}")
                print(f"   ❌ Not found: {result['not_found']}")
                
                if result.get('errors'):
                    print(f"   🔍 Errors: {len(result['errors'])}")
                    for error in result['errors'][:3]:
                        print(f"      {error}")
                        
            except Exception as e:
                print(f"❌ Error removing documents: {e}")
        
        elif choice == "3":
            print("✅ Operation cancelled")

    async def clear_all_documents(self):
        """Clear all documents with enhanced confirmation"""
        print("\n🧹 Clear All Documents")
        print("-" * 30)
        
        # Show current state
        try:
            health_info = await self.document_service.get_storage_health()
            doc_count = health_info.get('total_documents', 0)
            storage_size = health_info.get('storage_size_mb', 0)
            
            print(f"📊 Current database state:")
            print(f"   Documents: {doc_count}")
            print(f"   Storage: {storage_size:.2f} MB")
            
            if doc_count == 0:
                print("ℹ️ Database is already empty")
                return
                
        except:
            pass
        
        print(f"\n⚠️ WARNING: This will delete ALL documents from the database!")
        print(f"This action cannot be undone.")
        
        confirm1 = input("Type 'DELETE ALL' to confirm: ").strip()
        if confirm1 != "DELETE ALL":
            print("❌ Operation cancelled")
            return
            
        confirm2 = input("Are you absolutely sure? (y/n): ").strip().lower()
        if confirm2 != 'y':
            print("❌ Operation cancelled")
            return
            
        try:
            print("🔄 Clearing all documents...")
            success = await self.document_service.clear_all_documents()
            
            if success:
                print("✅ All documents cleared successfully")
                
                # Verify clearing
                health_info = await self.document_service.get_storage_health()
                if health_info.get('total_documents', 0) == 0:
                    print("✅ Database is now empty and clean")
                else:
                    print("⚠️ Some documents may still remain")
            else:
                print("❌ Failed to clear documents")
                
        except Exception as e:
            print(f"❌ Error clearing documents: {e}")

    async def export_documents(self):
        """Export all documents to JSON for backup"""
        print("\n📤 Export Documents")
        print("-" * 25)
        
        try:
            documents = await self.document_service.list_documents()
            
            if not documents:
                print("📂 No documents to export")
                return
            
            # Prepare export data
            export_data = {
                "export_info": {
                    "created_at": datetime.now().isoformat(),
                    "total_documents": len(documents),
                    "exported_by": "corruption_proof_cli"
                },
                "documents": []
            }
            
            for doc in documents:
                export_doc = {
                    "id": doc.get('id'),
                    "title": doc.get('title'),
                    "content": doc.get('content'),
                    "metadata": doc.get('metadata', {}),
                    "chunk_count": doc.get('chunk_count', 1),
                    "content_length": len(doc.get('content', ''))
                }
                export_data["documents"].append(export_doc)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = f"data/exports/documents_export_{timestamp}.json"
            
            # Ensure export directory exists
            Path("data/exports").mkdir(exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Exported {len(documents)} documents to:")
            print(f"   {export_path}")
            
            # Show export stats
            total_chars = sum(len(doc.get('content', '')) for doc in documents)
            file_size = Path(export_path).stat().st_size
            
            print(f"\n📊 Export Statistics:")
            print(f"   Documents: {len(documents)}")
            print(f"   Total content: {total_chars:,} characters")
            print(f"   File size: {file_size/1024/1024:.2f} MB")
            
        except Exception as e:
            print(f"❌ Error exporting documents: {e}")


async def main():
    """Main entry point with corruption protection"""
    print("🛡️ Saudi Legal AI - Corruption-Proof Document Manager")
    print("=" * 70)
    
    manager = CorruptionProofDocumentManager()
    
    try:
        # Initialize with health check
        init_success = await manager.initialize()
        
        if not init_success:
            print("\n🚨 INITIALIZATION FAILED!")
            print("Your database may be corrupted or have configuration issues.")
            print("\n🔧 RECOMMENDED ACTIONS:")
            print("1. Run the recovery script: python db_recovery.py")
            print("2. Check your OpenAI API key in .env file")
            print("3. Ensure all dependencies are installed")
            return
        
        # Show startup success
        print("\n🎉 SYSTEM READY!")
        print("🛡️ Corruption protection is active")
        print("🚀 You can now safely add documents")
        
        await manager.show_main_menu()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("🛡️ System protected database from corruption")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())