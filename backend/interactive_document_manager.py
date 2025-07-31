#!/usr/bin/env python3
"""
🇸🇦 Interactive Document Management CLI
Professional tool for adding documents to your Saudi Legal AI system
Uses your existing DocumentService architecture - NO hardcoding!
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

# Import your existing services
from app.storage.sqlite_store import SqliteVectorStore
from app.services.document_service import DocumentService
from openai import AsyncOpenAI
from app.core.config import settings


class InteractiveDocumentManager:
    """Interactive CLI for managing documents in your legal AI system"""
    
    def __init__(self):
        self.storage = None
        self.document_service = None
        self.ai_client = None
        
    async def initialize(self):
        """Initialize services"""
        print("🔧 Initializing Saudi Legal AI Document Manager...")
        
        # Initialize vector store
        self.storage = SqliteVectorStore("data/vectors.db")
        await self.storage.initialize()
        
        # Initialize AI client
        self.ai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Initialize document service
        self.document_service = DocumentService(self.storage, self.ai_client)
        
        print("✅ Services initialized successfully")
        
    async def show_main_menu(self):
        """Display main menu and handle user selection"""
        while True:
            print("\n" + "="*60)
            print("🇸🇦 Saudi Legal AI - Document Management")
            print("="*60)
            
            # Show current status
            await self.show_database_status()
            
            print("\nAvailable Actions:")
            print("1. 📝 Add Single Document")
            print("2. 📚 Add Multiple Documents (Batch)")
            print("3. 📋 List All Documents")
            print("4. 🔍 Search Documents")
            print("5. ❌ Remove Document(s)")
            print("6. 📊 Database Statistics")
            print("7. 🧹 Clear All Documents")
            print("8. 🚪 Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            try:
                if choice == "1":
                    await self.add_single_document()
                elif choice == "2":
                    await self.add_multiple_documents()
                elif choice == "3":
                    await self.list_documents()
                elif choice == "4":
                    await self.search_documents()
                elif choice == "5":
                    await self.remove_documents()
                elif choice == "6":
                    await self.show_database_stats()
                elif choice == "7":
                    await self.clear_all_documents()
                elif choice == "8":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-8.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    async def show_database_status(self):
        """Show current database status"""
        try:
            health_info = await self.document_service.get_storage_health()
            total_docs = health_info.get("total_documents", 0)
            storage_size = health_info.get("storage_size_mb", 0)
            
            status = "🟢 Healthy" if health_info.get("healthy", False) else "🔴 Issues"
            
            print(f"Database Status: {status} | Documents: {total_docs} | Size: {storage_size:.2f} MB")
            
        except Exception as e:
            print(f"Database Status: 🔴 Error - {e}")
    
    async def add_single_document(self):
        """Add a single document through interactive input"""
        print("\n📝 Add Single Document")
        print("-" * 30)
        
        # Get document details
        title = input("Document Title: ").strip()
        if not title:
            print("❌ Title cannot be empty")
            return
            
        print("\nDocument Content Options:")
        print("1. Type content directly")
        print("2. Load from file")
        print("3. Paste content (multi-line)")
        
        content_choice = input("Choose option (1-3): ").strip()
        
        content = ""
        if content_choice == "1":
            content = input("Enter content: ").strip()
        elif content_choice == "2":
            file_path = input("Enter file path: ").strip()
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Loaded {len(content)} characters from file")
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                return
        elif content_choice == "3":
            print("Enter content (press Ctrl+D when finished):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                content = "\n".join(lines)
                
        if not content:
            print("❌ Content cannot be empty")
            return
            
        # Optional metadata
        metadata = {}
        add_metadata = input("Add metadata? (y/n): ").strip().lower()
        if add_metadata == 'y':
            source = input("Source (optional): ").strip()
            if source:
                metadata["source"] = source
                
            doc_type = input("Document type (optional): ").strip()
            if doc_type:
                metadata["type"] = doc_type
                
            authority = input("Issuing authority (optional): ").strip()
            if authority:
                metadata["authority"] = authority
        
        # Add timestamp
        metadata["added_at"] = datetime.now().isoformat()
        metadata["added_via"] = "interactive_cli"
        
        print(f"\n🔄 Adding document '{title}' ({len(content)} characters)...")
        
        try:
            success = await self.document_service.add_document(
                title=title,
                content=content,
                metadata=metadata
            )
            
            if success:
                print("✅ Document added successfully!")
                
                # Enhanced processing info
                estimated_tokens = self.document_service.estimate_tokens(content)
                
                if self.document_service.should_chunk_document(content):
                    print(f"📏 Large document ({estimated_tokens:,} tokens)")
                    print("✂️ Document was intelligently chunked using SmartLegalChunker")
                    print("🏛️ Arabic legal structure (الباب، الفصل، المادة) preserved")
                    print("📖 Each chunk maintains proper legal citations")
                else:
                    print(f"📄 Document stored as single chunk ({estimated_tokens:,} tokens)")
                    
                # Show character and token stats
                print(f"📊 Document stats: {len(content):,} characters, ~{estimated_tokens:,} tokens")
                
            else:
                print("❌ Failed to add document")
                print("💡 Tip: Very large documents are automatically chunked for optimal processing")
                
        except Exception as e:
            print(f"❌ Error adding document: {e}")
    
    async def add_multiple_documents(self):
        """Add multiple documents from various sources"""
        print("\n📚 Add Multiple Documents")
        print("-" * 35)
        
        print("Batch Import Options:")
        print("1. Load from JSON file")
        print("2. Load from directory (multiple text files)")
        print("3. Manual entry (guided)")
        
        choice = input("Choose option (1-3): ").strip()
        
        documents = []
        
        if choice == "1":
            await self.load_from_json_file(documents)
        elif choice == "2":
            await self.load_from_directory(documents)
        elif choice == "3":
            await self.manual_batch_entry(documents)
        else:
            print("❌ Invalid choice")
            return
            
        if not documents:
            print("❌ No documents to process")
            return
            
        # Confirm before processing
        print(f"\n📋 Ready to process {len(documents)} documents:")
        for i, doc in enumerate(documents[:5], 1):
            print(f"  {i}. {doc.get('title', 'Untitled')}")
        
        if len(documents) > 5:
            print(f"  ... and {len(documents) - 5} more")
            
        confirm = input("\nProceed with batch import? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Batch import cancelled")
            return
            
        print(f"\n🔄 Processing {len(documents)} documents...")
        
        try:
            result = await self.document_service.add_documents_batch(documents)
            
            if result["success"]:
                print(f"✅ Successfully processed {result['successful']} documents")
                if result.get("errors", 0) > 0:
                    print(f"⚠️ {result['errors']} documents had errors")
                    for error in result.get("error_details", [])[:3]:
                        print(f"   ❌ {error}")
            else:
                print(f"❌ Batch processing failed: {result['message']}")
                
        except Exception as e:
            print(f"❌ Error in batch processing: {e}")
    
    async def load_from_json_file(self, documents):
        """Load documents from JSON file"""
        file_path = input("Enter JSON file path: ").strip()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle different JSON structures
            if isinstance(data, list):
                documents.extend(data)
            elif isinstance(data, dict) and 'documents' in data:
                documents.extend(data['documents'])
            else:
                print("❌ JSON file should contain a list or have a 'documents' key")
                return
                
            print(f"✅ Loaded {len(documents)} documents from JSON file")
            
        except Exception as e:
            print(f"❌ Error reading JSON file: {e}")
    
    async def load_from_directory(self, documents):
        """Load documents from directory of text files"""
        dir_path = input("Enter directory path: ").strip()
        
        try:
            directory = Path(dir_path)
            if not directory.exists():
                print("❌ Directory does not exist")
                return
                
            text_files = list(directory.glob("*.txt"))
            if not text_files:
                print("❌ No .txt files found in directory")
                return
                
            for file_path in text_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    document = {
                        "title": file_path.stem,
                        "content": content,
                        "metadata": {
                            "source": str(file_path),
                            "loaded_from": "directory",
                            "added_at": datetime.now().isoformat()
                        }
                    }
                    documents.append(document)
                    
                except Exception as e:
                    print(f"⚠️ Error reading {file_path}: {e}")
                    
            print(f"✅ Loaded {len(documents)} documents from directory")
            
        except Exception as e:
            print(f"❌ Error processing directory: {e}")
    
    async def manual_batch_entry(self, documents):
        """Manual entry of multiple documents"""
        count = input("How many documents to add? ").strip()
        
        try:
            count = int(count)
            if count <= 0:
                print("❌ Invalid count")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
            
        for i in range(count):
            print(f"\n--- Document {i+1}/{count} ---")
            
            title = input("Title: ").strip()
            if not title:
                print("Skipping document (no title)")
                continue
                
            content = input("Content: ").strip()
            if not content:
                print("Skipping document (no content)")
                continue
                
            document = {
                "title": title,
                "content": content,
                "metadata": {
                    "added_via": "manual_batch",
                    "added_at": datetime.now().isoformat(),
                    "batch_position": i + 1
                }
            }
            documents.append(document)
            
        print(f"✅ Prepared {len(documents)} documents for batch processing")
    
    async def list_documents(self):
        """List all documents in the database"""
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
                
                print(f"{i:3d}. {title}")
                print(f"     ID: {doc_id}")
                print(f"     Length: {content_length:,} characters")
                
                metadata = doc.get('metadata', {})
                if metadata.get('source'):
                    print(f"     Source: {metadata['source']}")
                    
                print()
                
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
    
    async def search_documents(self):
        """Search documents by content or metadata"""
        print("\n🔍 Search Documents")
        print("-" * 25)
        
        query = input("Enter search query: ").strip()
        if not query:
            print("❌ Search query cannot be empty")
            return
            
        print(f"🔄 Searching for: '{query}'...")
        
        try:
            # This would use your existing vector search
            # For now, we'll do a simple text search
            documents = await self.document_service.list_documents()
            
            matches = []
            for doc in documents:
                title = doc.get('title', '').lower()
                content = doc.get('content', '').lower()
                query_lower = query.lower()
                
                if query_lower in title or query_lower in content:
                    matches.append(doc)
                    
            if matches:
                print(f"✅ Found {len(matches)} matches:")
                for i, doc in enumerate(matches, 1):
                    title = doc.get('title', 'Untitled')
                    doc_id = doc.get('id', 'unknown')
                    print(f"{i}. {title} (ID: {doc_id})")
            else:
                print("❌ No documents found matching your query")
                
        except Exception as e:
            print(f"❌ Error searching: {e}")
    
    async def remove_documents(self):
        """Remove documents from database"""
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
                
            confirm = input(f"Confirm removal of document '{doc_id}'? (y/n): ").strip().lower()
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
            
            print(f"Documents to remove: {doc_ids}")
            confirm = input(f"Confirm removal of {len(doc_ids)} documents? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Removal cancelled")
                return
                
            try:
                result = await self.document_service.remove_documents_batch(doc_ids)
                if result["success"]:
                    print(f"✅ Removed {result['deleted']} documents")
                    if result['not_found'] > 0:
                        print(f"⚠️ {result['not_found']} documents were not found")
                else:
                    print("❌ Batch removal failed")
            except Exception as e:
                print(f"❌ Error removing documents: {e}")
        
        elif choice == "3":
            print("✅ Operation cancelled")
    
    async def show_database_stats(self):
        """Show detailed database statistics"""
        print("\n📊 Database Statistics")
        print("-" * 30)
        
        try:
            health_info = await self.document_service.get_storage_health()
            
            print(f"Health Status: {'🟢 Healthy' if health_info.get('healthy') else '🔴 Issues'}")
            print(f"Total Documents: {health_info.get('total_documents', 0):,}")
            print(f"Storage Size: {health_info.get('storage_size_mb', 0):.2f} MB")
            print(f"Storage Type: {health_info.get('storage_type', 'Unknown')}")
            print(f"Last Updated: {health_info.get('last_updated', 'Unknown')}")
            
            # Additional stats if available
            documents = await self.document_service.list_documents()
            if documents:
                total_chars = sum(len(doc.get('content', '')) for doc in documents)
                avg_chars = total_chars / len(documents) if documents else 0
                
                print(f"Total Characters: {total_chars:,}")
                print(f"Average Document Size: {avg_chars:,.0f} characters")
                
                # Count by metadata types
                sources = {}
                for doc in documents:
                    source = doc.get('metadata', {}).get('source', 'Unknown')
                    sources[source] = sources.get(source, 0) + 1
                    
                if sources:
                    print("\nDocuments by Source:")
                    for source, count in sources.items():
                        print(f"  {source}: {count}")
                        
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    async def clear_all_documents(self):
        """Clear all documents from database"""
        print("\n🧹 Clear All Documents")
        print("-" * 30)
        
        print("⚠️  WARNING: This will delete ALL documents from the database!")
        print("This action cannot be undone.")
        
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
            else:
                print("❌ Failed to clear documents")
                
        except Exception as e:
            print(f"❌ Error clearing documents: {e}")


async def main():
    """Main entry point"""
    print("🇸🇦 Saudi Legal AI - Interactive Document Manager")
    print("=" * 60)
    
    manager = InteractiveDocumentManager()
    
    try:
        await manager.initialize()
        await manager.show_main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())