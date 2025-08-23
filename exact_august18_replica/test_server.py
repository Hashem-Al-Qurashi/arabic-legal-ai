#!/usr/bin/env python3
"""
Simple test server for Quranic integration system
Run on localhost to test the system via web interface
"""

import sys
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from app.storage.quranic_foundation_store import QuranicFoundationStore
from app.core.semantic_concepts import SemanticConceptEngine

# Initialize FastAPI app
app = FastAPI(title="Quranic Integration Test Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
quranic_store = None
concept_engine = None
system_ready = False

class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class QueryResponse(BaseModel):
    query: str
    concepts_extracted: int
    quranic_foundations: int
    results: list
    processing_time_ms: float

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global quranic_store, concept_engine, system_ready
    
    try:
        print("🔄 Initializing Quranic integration system...")
        
        # Initialize Quranic store
        quranic_store = QuranicFoundationStore()
        await quranic_store.initialize()
        
        # Initialize concept engine
        concept_engine = SemanticConceptEngine()
        
        # Check system health
        health = await quranic_store.health_check()
        if not health:
            raise Exception("Quranic store is not healthy")
        
        stats = await quranic_store.get_stats()
        print(f"✅ System ready! Quranic database has {stats.total_chunks} foundations")
        
        system_ready = True
        
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        system_ready = False

@app.get("/")
async def root():
    """Serve a simple test interface"""
    html_content = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🕌 اختبار نظام التكامل القرآني</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .content {
                padding: 30px;
            }
            .input-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #444;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                box-sizing: border-box;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.2s;
                width: 100%;
                margin-top: 10px;
            }
            button:hover {
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .result-item {
                background: white;
                margin: 15px 0;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .verse-ref {
                color: #1e3c72;
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 8px;
            }
            .principle {
                color: #2c5282;
                font-weight: 600;
                margin-bottom: 10px;
            }
            .commentary {
                color: #4a5568;
                line-height: 1.6;
                font-size: 14px;
            }
            .confidence {
                background: #e2e8f0;
                color: #2d3748;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                display: inline-block;
                margin-top: 8px;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            .error {
                background: #fed7d7;
                color: #c53030;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
            }
            .status {
                text-align: center;
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 8px;
            }
            .status.ready {
                background: #c6f6d5;
                color: #22543d;
            }
            .status.error {
                background: #fed7d7;
                color: #c53030;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🕌 نظام التكامل القرآني للذكاء الاصطناعي القانوني</h1>
                <p>اختبار نظام البحث في الأسس القرآنية للمسائل القانونية</p>
            </div>
            
            <div class="content">
                <div id="status" class="status">
                    🔄 جاري التحقق من حالة النظام...
                </div>
                
                <div class="input-group">
                    <label for="query">أدخل استفسارك القانوني:</label>
                    <input type="text" id="query" placeholder="مثال: أحكام العقود، العدالة في القضاء، الميراث والتركات">
                </div>
                
                <button onclick="searchQuranic()" id="searchBtn">
                    🔍 البحث في الأسس القرآنية
                </button>
                
                <div id="results"></div>
            </div>
        </div>

        <script>
            // Check system status on load
            window.onload = checkStatus;
            
            async function checkStatus() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    
                    const statusDiv = document.getElementById('status');
                    if (data.ready) {
                        statusDiv.className = 'status ready';
                        statusDiv.innerHTML = `✅ النظام جاهز - ${data.foundations_count} أساس قرآني متاح`;
                    } else {
                        statusDiv.className = 'status error';
                        statusDiv.innerHTML = '❌ النظام غير جاهز';
                    }
                } catch (error) {
                    const statusDiv = document.getElementById('status');
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = '❌ خطأ في الاتصال بالنظام';
                }
            }
            
            async function searchQuranic() {
                const query = document.getElementById('query').value.trim();
                if (!query) {
                    alert('يرجى إدخال استفسار قانوني');
                    return;
                }
                
                const resultsDiv = document.getElementById('results');
                const searchBtn = document.getElementById('searchBtn');
                
                // Show loading
                resultsDiv.innerHTML = '<div class="loading">🔄 جاري البحث في الأسس القرآنية...</div>';
                searchBtn.disabled = true;
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ query: query, limit: 5 })
                    });
                    
                    const data = await response.json();
                    displayResults(data);
                    
                } catch (error) {
                    resultsDiv.innerHTML = '<div class="error">❌ حدث خطأ أثناء البحث: ' + error.message + '</div>';
                } finally {
                    searchBtn.disabled = false;
                }
            }
            
            function displayResults(data) {
                const resultsDiv = document.getElementById('results');
                
                if (data.quranic_foundations === 0) {
                    resultsDiv.innerHTML = `
                        <div class="results">
                            <h3>📊 نتائج البحث</h3>
                            <p><strong>الاستفسار:</strong> ${data.query}</p>
                            <p><strong>المفاهيم المستخرجة:</strong> ${data.concepts_extracted}</p>
                            <p><strong>الأسس القرآنية:</strong> لم يتم العثور على أسس قرآنية مناسبة</p>
                            <p><strong>وقت المعالجة:</strong> ${data.processing_time_ms.toFixed(1)} مللي ثانية</p>
                        </div>
                    `;
                    return;
                }
                
                let html = `
                    <div class="results">
                        <h3>📊 نتائج البحث</h3>
                        <p><strong>الاستفسار:</strong> ${data.query}</p>
                        <p><strong>المفاهيم المستخرجة:</strong> ${data.concepts_extracted}</p>
                        <p><strong>الأسس القرآنية:</strong> ${data.quranic_foundations}</p>
                        <p><strong>وقت المعالجة:</strong> ${data.processing_time_ms.toFixed(1)} مللي ثانية</p>
                        
                        <h4>🕌 الأسس القرآنية ذات الصلة:</h4>
                `;
                
                data.results.forEach((result, index) => {
                    html += `
                        <div class="result-item">
                            <div class="verse-ref">${index + 1}. ${result.verse_reference}</div>
                            <div class="principle">${result.legal_principle}</div>
                            <div class="commentary">${result.commentary}</div>
                            <span class="confidence">درجة الصلة: ${(result.confidence * 100).toFixed(1)}%</span>
                        </div>
                    `;
                });
                
                html += '</div>';
                resultsDiv.innerHTML = html;
            }
            
            // Allow Enter key to search
            document.getElementById('query').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchQuranic();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Check system health"""
    if not system_ready:
        return {"ready": False, "error": "System not initialized"}
    
    try:
        health = await quranic_store.health_check()
        stats = await quranic_store.get_stats()
        
        return {
            "ready": health,
            "foundations_count": stats.total_chunks,
            "storage_size_mb": stats.storage_size_mb
        }
    except Exception as e:
        return {"ready": False, "error": str(e)}

@app.post("/search", response_model=QueryResponse)
async def search_quranic_foundations(request: QueryRequest):
    """Search for Quranic foundations based on query"""
    
    if not system_ready:
        raise HTTPException(status_code=503, detail="System not ready")
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Extract concepts
        concepts = await concept_engine.extract_legal_concepts(request.query)
        
        # Search Quranic foundations
        context = {"domain": "legal", "api_request": True}
        results = await quranic_store.semantic_search_foundations(
            concepts, context, limit=request.limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            metadata = result.chunk.metadata
            formatted_results.append({
                "verse_reference": metadata.get('verse_reference', 'غير محدد'),
                "legal_principle": metadata.get('legal_principle', 'غير محدد')[:200],
                "commentary": result.chunk.content[:300] + "..." if len(result.chunk.content) > 300 else result.chunk.content,
                "confidence": result.similarity_score,
                "surah": metadata.get('surah', 'غير محدد'),
                "modern_applications": metadata.get('modern_applications', [])
            })
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return QueryResponse(
            query=request.query,
            concepts_extracted=len(concepts),
            quranic_foundations=len(results),
            results=formatted_results,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get detailed system statistics"""
    if not system_ready:
        raise HTTPException(status_code=503, detail="System not ready")
    
    try:
        # Quranic store stats
        quranic_stats = await quranic_store.get_stats()
        
        # Concept engine stats
        concept_stats = concept_engine.get_extraction_stats()
        
        return {
            "quranic_store": {
                "total_foundations": quranic_stats.total_chunks,
                "storage_size_mb": quranic_stats.storage_size_mb,
                "last_updated": quranic_stats.last_updated.isoformat()
            },
            "concept_engine": concept_stats,
            "system_ready": system_ready
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")

if __name__ == "__main__":
    print("🕌 Starting Quranic Integration Test Server...")
    print("📱 Open http://localhost:8001 in your browser to test")
    print("🔗 API endpoints:")
    print("   - GET  /health - Check system health")
    print("   - POST /search - Search Quranic foundations")
    print("   - GET  /stats  - Get system statistics")
    print("\n🚀 Starting server...")
    
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )