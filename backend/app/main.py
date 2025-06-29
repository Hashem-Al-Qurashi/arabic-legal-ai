"""
Main FastAPI application with proper router separation
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime
import io

# Import routers
from app.api.simple_auth import router as auth_router
from app.api.simple_consultations import router as consultations_router

# Create FastAPI application
app = FastAPI(
    title="Arabic Legal Assistant",
    description="""
    🇸🇦 استشارة قانونية ومالية وإدارية ذكية مبنية على القانون السعودي
    
    Professional Arabic Legal Assistant with:
    - User authentication and management  
    - AI-powered legal consultations
    - Document export capabilities
    """,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(consultations_router, prefix="/api/consultations", tags=["Legal Consultations"])

# Document export endpoint (from your original working backend)
@app.get("/export/docx")
async def export_docx(question: str = Query(...), answer: str = Query(...)):
    """Export legal response as DOCX with perfect Arabic support"""
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        import re
        
        print(f"📝 Generating DOCX export...")
        
        # Create Word document
        doc = Document()
        
        # Clean HTML tags from content
        clean_question = re.sub('<[^<]+?>', '', question)
        clean_answer = re.sub('<[^<]+?>', '', answer)
        
        # Document title
        title = doc.add_heading('المساعد القانوني الذكي 🇸🇦', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Subtitle
        subtitle = doc.add_paragraph('استشارة قانونية ذكية مبنية على القانون السعودي')
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add separator line
        doc.add_paragraph('─' * 50).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add some space
        doc.add_paragraph()
        
        # Question section
        question_heading = doc.add_heading('📋 السؤال:', level=1)
        question_heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        question_para = doc.add_paragraph(clean_question)
        question_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Add space between sections
        doc.add_paragraph()
        
        # Answer section
        answer_heading = doc.add_heading('✅ الإجابة:', level=1)
        answer_heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        answer_para = doc.add_paragraph(clean_answer)
        answer_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Add footer with timestamp
        doc.add_paragraph()
        timestamp_text = f"تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d الساعة %H:%M')}"
        footer_para = doc.add_paragraph(timestamp_text)
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Save to buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"legal_response_{timestamp}.docx"
        
        print(f"✅ DOCX export generated successfully")
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        )
        
    except Exception as e:
        print(f"❌ DOCX export error: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في إنشاء ملف Word: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "مرحباً بك في المساعد القانوني الذكي",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "auth": "/api/auth",
            "consultations": "/api/consultations",
            "export": "/export/docx"
        }
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Arabic Legal Assistant"
    }

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        from app.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created!")
        print("🚀 Arabic Legal Assistant API started!")
        print("📋 Available endpoints:")
        print("   - POST /api/auth/register")
        print("   - POST /api/auth/login") 
        print("   - POST /api/consultations/ask")
        print("   - GET  /export/docx")
    except Exception as e:
        print(f"❌ Startup error: {e}")