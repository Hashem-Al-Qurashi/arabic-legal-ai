# Create: simple_test_save.py
#!/usr/bin/env python3

print("🚀 Simple save test...")

# Import chunker
from smart_legal_chunker import EliteLegalChunker
chunker = EliteLegalChunker()

# Test content
content = """المادة (5):
تحدد رسوم القيد في سجل الوكالات كالآتي:
خمسمائة ريال للتاجر الفرد والشركة.
وتدفع الرسوم لمرة واحدة."""

# Generate chunks
chunks = chunker.chunk_legal_document(content, "نظام الوكالات التجارية")
print(f"✅ Generated {len(chunks)} chunks")

# Save directly to database
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('data/vectors.db')
cursor = conn.cursor()

for chunk in chunks:
    chunk_id = f"commercial_simple_{chunk.chunk_index}"
    
    cursor.execute("""
        INSERT OR REPLACE INTO chunks 
        (id, content, title, metadata, created_at, updated_at) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        chunk_id,
        chunk.content,
        chunk.title,
        json.dumps(chunk.metadata, ensure_ascii=False),
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

conn.commit()
conn.close()

print(f"🎉 SUCCESS! Saved {len(chunks)} chunks to database")

# Test the save
conn = sqlite3.connect('data/vectors.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM chunks WHERE content LIKE '%خمسمائة ريال%'")
count = cursor.fetchone()[0]
conn.close()

print(f"🔍 VERIFIED: {count} chunks with fee info in database")
print("✅ Now test your RAG with: 'ماهي رسوم القيد في سجل الوكالات؟'")