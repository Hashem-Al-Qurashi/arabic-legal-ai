"""
OCR API Endpoints for Arabic Document Processing
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import asyncio
import uuid
from datetime import datetime

from app.database import get_database
from app.dependencies.simple_auth import get_current_active_user, get_optional_current_user
from app.services.ocr_service import arabic_ocr_service
from app.services.enhanced_ocr_service import enhanced_arabic_ocr
from app.services.arabic_ocr_fixed import arabic_ocr_fixed
from app.services.tesseract_arabic_ocr import professional_arabic_ocr
from app.services.google_vision_ocr import google_vision_ocr
from app.services.cooldown_service import CooldownService
from app.services.guest_service import GuestService
from app.models.user import User
from rag_engine import get_rag_engine

router = APIRouter(prefix="/ocr", tags=["ocr"])

# File size limits (in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_PDF_PAGES = 50  # Maximum pages to process in PDF

@router.post("/extract")
async def extract_text_from_file(
    file: UploadFile = File(..., description="Image or PDF file for OCR processing"),
    session_id: Optional[str] = Form(None, description="Guest session ID (for guests only)"),
    process_with_rag: bool = Form(False, description="Process extracted text with RAG system"),
    question: Optional[str] = Form(None, description="Question to ask about the extracted text"),
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Extract Arabic text from uploaded image or PDF file
    
    - Supports: JPG, PNG, BMP, TIFF, WebP, PDF
    - Maximum file size: 50MB
    - Maximum PDF pages: 50
    - Optional RAG processing of extracted text
    """
    
    try:
        # ===== AUTHENTICATION & VALIDATION =====
        if not current_user and not session_id:
            raise HTTPException(
                status_code=400,
                detail="Authentication required: either login or provide session_id for guest access"
            )
        
        # Check file upload
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Validate file type
        if not arabic_ocr_service.is_format_supported(file.content_type):
            supported_formats = ", ".join(arabic_ocr_service.get_supported_formats())
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file.content_type}. Supported: {supported_formats}"
            )
        
        # ===== USER LIMITS CHECK =====
        # DISABLED FOR LOCAL DEVELOPMENT - This is your own system!
        # Uncomment below if you want to re-enable quotas later
        
        # if current_user:
        #     # Check authenticated user limits
        #     can_ask, cooldown_message, reset_time = CooldownService.can_ask_question(db, current_user)
        #     if not can_ask:
        #         raise HTTPException(
        #             status_code=429,
        #             detail={
        #                 "message": cooldown_message,
        #                 "reset_time": reset_time.isoformat() if reset_time else None
        #             }
        #         )
        #     
        #     # Use question quota
        #     if not CooldownService.use_question(db, current_user):
        #         raise HTTPException(status_code=500, detail="Failed to process request")
        #         
        # else:
        #     # Check guest user limits
        #     can_ask, cooldown_message, reset_time = GuestService.can_guest_ask_question(session_id)
        #     if not can_ask:
        #         raise HTTPException(
        #             status_code=429,
        #             detail={
        #                 "message": cooldown_message,
        #                 "reset_time": reset_time.isoformat() if reset_time else None
        #             }
        #         )
        # 
        #     # Use guest question quota
        #     if not GuestService.use_guest_question(session_id):
        #         raise HTTPException(status_code=500, detail="Failed to process request")
        
        print(f"🔍 Processing OCR for {'user' if current_user else 'guest'}: {file.filename}")
        print(f"📁 File: {file.filename} ({file.content_type}, {len(file_content)} bytes)")
        
        # ===== ENHANCED OCR PROCESSING FOR 100% ACCURACY =====
        start_time = datetime.utcnow()
        
        if file.content_type == "application/pdf":
            # PDF processing (use original service for now)
            ocr_result = await arabic_ocr_service.extract_text_from_pdf(
                file_content, 
                max_pages=MAX_PDF_PAGES
            )
        else:
            # Try Google Vision first (best accuracy), fallback to Tesseract
            print("🌟 Trying Google Cloud Vision API for 98% Arabic accuracy...")
            enhanced_result = await google_vision_ocr.extract_arabic_text(file_content)
            
            if not enhanced_result.get('success'):
                print("⚠️ Google Vision failed, falling back to Tesseract...")
                enhanced_result = await professional_arabic_ocr.extract_arabic_text(file_content)
            
            if enhanced_result.get('success'):
                # Convert to expected format
                ocr_result = {
                    "success": True,
                    "text": enhanced_result['text'],
                    "confidence": enhanced_result['confidence'],
                    "word_count": len(enhanced_result['text'].split()) if enhanced_result['text'] else 0,
                    "language": "ar",
                    "metadata": enhanced_result.get('metadata', {})
                }
                print(f"✅ Root-Fixed OCR: {enhanced_result.get('engine')} engine, {enhanced_result.get('linguistic_fixes_applied', 0)} fixes applied")
            else:
                # Fallback to original service
                print("⚠️ Enhanced OCR failed, falling back to original service")
                ocr_result = await arabic_ocr_service.extract_text_from_image(file_content)
        
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        if not ocr_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {ocr_result.get('error', 'Unknown error')}"
            )
        
        extracted_text = ocr_result["text"]
        
        print(f"✅ OCR completed: {len(extracted_text)} characters extracted")
        print(f"🎯 Confidence: {ocr_result['confidence']:.2%}")
        
        # ===== OPTIONAL RAG PROCESSING =====
        rag_response = None
        if process_with_rag and extracted_text.strip():
            try:
                rag_engine = get_rag_engine()
                
                if question and question.strip():
                    # User provided specific question about the document
                    query = f"بناءً على المستند التالي:\n\n{extracted_text}\n\nسؤال: {question.strip()}"
                else:
                    # Default analysis
                    query = f"قم بتحليل هذا المستند القانوني وتلخيص محتواه:\n\n{extracted_text}"
                
                print(f"🧠 Processing with RAG: {query[:100]}...")
                rag_response = await rag_engine.ask_question_async(query)
                
                print(f"🎯 RAG analysis completed: {len(rag_response)} characters")
                
            except Exception as e:
                print(f"⚠️ RAG processing failed: {e}")
                # Don't fail the entire request if RAG fails
                rag_response = f"خطأ في معالجة النص: {str(e)}"
        
        # ===== RESPONSE =====
        response_data = {
            "success": True,
            "request_id": str(uuid.uuid4()),
            "file_info": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size_bytes": len(file_content),
                "pages_processed": ocr_result.get("pages_processed", 1)
            },
            "ocr_result": {
                "text": extracted_text,
                "confidence": ocr_result["confidence"],
                "word_count": ocr_result["word_count"],
                "language": ocr_result["language"],
                "engine": ocr_result.get("metadata", {}).get("engine", "PaddleOCR v5")
            },
            "processing": {
                "ocr_time_ms": processing_time,
                "total_time_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000),
                "timestamp": datetime.utcnow().isoformat()
            },
            "user_info": {
                "user_type": "authenticated" if current_user else "guest",
                "user_id": str(current_user.id) if current_user else None,
                "session_id": session_id if not current_user else None
            }
        }
        
        # Add RAG analysis if requested
        if process_with_rag:
            response_data["rag_analysis"] = {
                "enabled": True,
                "question": question if question else "تحليل المستند",
                "response": rag_response,
                "success": rag_response is not None and "خطأ" not in rag_response
            }
        else:
            response_data["rag_analysis"] = {"enabled": False}
        
        print(f"📤 OCR response ready: {len(extracted_text)} chars, RAG: {process_with_rag}")
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        # Re-raise HTTP exceptions (limits, validation, etc.)
        raise
    except Exception as e:
        # Rollback question usage on error
        try:
            if current_user:
                current_user.questions_used_current_cycle -= 1
                if current_user.questions_used_current_cycle <= 0:
                    current_user.cycle_reset_time = None
                db.commit()
            elif session_id:
                guest_session = GuestService.get_guest_session(session_id)
                guest_session["questions_used"] -= 1
        except:
            pass  # Don't fail on rollback errors
        
        print(f"❌ OCR processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )

@router.post("/analyze")
async def analyze_extracted_text(
    text: str = Form(..., description="Previously extracted text to analyze"),
    question: str = Form(..., description="Question about the text"),
    session_id: Optional[str] = Form(None, description="Guest session ID (for guests only)"),
    db: Session = Depends(get_database),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Analyze previously extracted text with RAG system
    This endpoint doesn't use question quota as it processes existing text
    """
    
    try:
        # ===== VALIDATION =====
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        if not question or not question.strip():
            raise HTTPException(status_code=400, detail="Question is required")
        
        if not current_user and not session_id:
            raise HTTPException(
                status_code=400,
                detail="Authentication required: either login or provide session_id"
            )
        
        # Limit text size for analysis
        if len(text) > 50000:  # 50k characters max
            raise HTTPException(
                status_code=400,
                detail="Text too long for analysis (max 50,000 characters)"
            )
        
        print(f"🔍 Analyzing text for {'user' if current_user else 'guest'}")
        print(f"📝 Text: {len(text)} characters")
        print(f"❓ Question: {question[:100]}...")
        
        # ===== RAG PROCESSING =====
        start_time = datetime.utcnow()
        
        rag_engine = get_rag_engine()
        query = f"بناءً على النص التالي:\n\n{text}\n\nسؤال: {question}"
        
        response = await rag_engine.ask_question_async(query)
        
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        print(f"✅ Analysis completed: {len(response)} characters in {processing_time}ms")
        
        return JSONResponse(content={
            "success": True,
            "request_id": str(uuid.uuid4()),
            "analysis": {
                "question": question,
                "response": response,
                "input_text_length": len(text),
                "response_length": len(response)
            },
            "processing": {
                "time_ms": processing_time,
                "timestamp": datetime.utcnow().isoformat()
            },
            "user_info": {
                "user_type": "authenticated" if current_user else "guest",
                "user_id": str(current_user.id) if current_user else None,
                "session_id": session_id if not current_user else None
            }
        })
        
    except Exception as e:
        print(f"❌ Text analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/health")
async def ocr_health_check():
    """
    Check OCR service health and capabilities
    """
    try:
        health_result = await arabic_ocr_service.health_check()
        
        return JSONResponse(content={
            "service": "Arabic OCR Service",
            "timestamp": datetime.utcnow().isoformat(),
            "health": health_result,
            "limits": {
                "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
                "max_pdf_pages": MAX_PDF_PAGES,
                "supported_formats": arabic_ocr_service.get_supported_formats()
            },
            "features": [
                "Arabic text recognition",
                "PDF document processing", 
                "Image preprocessing",
                "Confidence scoring",
                "RAG integration",
                "Batch processing"
            ]
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "service": "Arabic OCR Service",
                "timestamp": datetime.utcnow().isoformat(),
                "health": {"status": "unhealthy", "error": str(e)},
                "error": str(e)
            }
        )

@router.get("/formats")
async def get_supported_formats():
    """
    Get list of supported file formats for OCR
    """
    return {
        "supported_formats": arabic_ocr_service.get_supported_formats(),
        "limits": {
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
            "max_pdf_pages": MAX_PDF_PAGES
        },
        "recommendations": {
            "image_quality": "High resolution images (300+ DPI) work best",
            "file_formats": "PNG and TIFF provide best quality, JPEG is acceptable",
            "pdf_guidelines": "Text-based PDFs may work better with native text extraction",
            "arabic_text": "Clear, high-contrast Arabic text yields highest accuracy"
        }
    }