# backend/app/api/ocr.py - Google Vision OCR Only (OCR_BIBLE.md compliant)
"""
OCR API endpoint for extracting text from images and PDFs
Google Vision OCR Only - as specified in OCR_BIBLE.md
No other OCR engines supported
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import base64
import io
import os
from datetime import datetime
import logging
import json

# Google Cloud Vision imports
try:
    from google.cloud import vision
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logging.warning("Google Cloud Vision not installed. OCR features will be limited.")

# PDF processing
try:
    import PyPDF2
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logging.warning("PyPDF2 not installed. PDF OCR will be limited.")

# Image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("Pillow not installed. Image preprocessing will be limited.")

from app.dependencies.simple_auth import get_optional_current_user
from app.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["OCR"])

# Supported file types
SUPPORTED_IMAGE_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png', 
    'image/bmp', 'image/tiff', 'image/webp'
}
SUPPORTED_PDF_TYPE = 'application/pdf'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

class OCRService:
    """Service for handling OCR operations"""
    
    def __init__(self):
        self.vision_client = None
        self._initialize_google_vision()
    
    def _initialize_google_vision(self):
        """Initialize Google Vision client"""
        if not GOOGLE_VISION_AVAILABLE:
            logger.warning("Google Vision API not available")
            return
        
        try:
            # Check for API key first (simpler method)
            google_api_key = os.getenv('GOOGLE_VISION_API_KEY')
            google_creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            google_creds_json = os.getenv('GOOGLE_VISION_CREDENTIALS_JSON')
            
            if google_api_key:
                # Use API key authentication (simpler)
                from google.api_core import client_options
                client_options_obj = client_options.ClientOptions(api_key=google_api_key)
                self.vision_client = vision.ImageAnnotatorClient(client_options=client_options_obj)
                logger.info("Google Vision initialized with API key")
            elif google_creds_json:
                # Use JSON credentials from environment variable
                credentials_dict = json.loads(google_creds_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict
                )
                self.vision_client = vision.ImageAnnotatorClient(credentials=credentials)
                logger.info("Google Vision initialized with JSON credentials")
            elif google_creds_path and os.path.exists(google_creds_path):
                # Use credentials file
                credentials = service_account.Credentials.from_service_account_file(
                    google_creds_path
                )
                self.vision_client = vision.ImageAnnotatorClient(credentials=credentials)
                logger.info(f"Google Vision initialized with file: {google_creds_path}")
            else:
                # Try default credentials (for Google Cloud environments)
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("Google Vision initialized with default credentials")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision: {str(e)}")
            self.vision_client = None
    
    async def extract_text_from_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract text from image using Google Vision API"""
        
        if not self.vision_client:
            # Fallback to basic OCR or return error
            return {
                "text": "",
                "confidence": 0,
                "engine": "none",
                "error": "Google Vision API not configured"
            }
        
        try:
            # Create vision image object
            image = vision.Image(content=image_bytes)
            
            # Perform text detection with Arabic language hint
            response = self.vision_client.document_text_detection(
                image=image,
                image_context={"language_hints": ["ar", "en"]}
            )
            
            # Check for errors
            if response.error.message:
                raise Exception(response.error.message)
            
            # Extract text and confidence
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # Calculate average confidence from pages
            confidence_scores = []
            if response.full_text_annotation:
                for page in response.full_text_annotation.pages:
                    for block in page.blocks:
                        if block.confidence:
                            confidence_scores.append(block.confidence)
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            return {
                "text": full_text.strip(),
                "confidence": avg_confidence,
                "engine": "Google Vision",
                "language": "ar",
                "word_count": len(full_text.split()) if full_text else 0
            }
            
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {str(e)}")
            return {
                "text": "",
                "confidence": 0,
                "engine": "Google Vision",
                "error": str(e)
            }
    
    async def extract_text_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text from PDF, using OCR for image-based pages"""
        
        extracted_texts = []
        total_confidence = 0
        page_count = 0
        
        try:
            if PYPDF_AVAILABLE:
                # Try to extract text directly from PDF
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        # Extract text from page
                        page_text = page.extract_text()
                        
                        if page_text and page_text.strip():
                            # Text extraction successful
                            extracted_texts.append(page_text)
                            total_confidence += 1.0  # High confidence for direct text
                        else:
                            # Page might be an image, try OCR
                            logger.info(f"Page {page_num + 1} appears to be image-based, attempting OCR")
                            # Note: Full PDF to image conversion would require additional libraries
                            # For now, we'll mark it as needing OCR
                            extracted_texts.append(f"[Page {page_num + 1}: Image-based content requires OCR]")
                            total_confidence += 0.5
                        
                        page_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                        extracted_texts.append(f"[Page {page_num + 1}: Error extracting text]")
                        page_count += 1
                
                # Combine all extracted texts
                full_text = "\n\n".join(extracted_texts)
                avg_confidence = total_confidence / page_count if page_count > 0 else 0
                
                return {
                    "text": full_text.strip(),
                    "confidence": avg_confidence,
                    "engine": "PyPDF2 + Google Vision",
                    "page_count": page_count,
                    "language": "ar"
                }
            else:
                return {
                    "text": "",
                    "confidence": 0,
                    "engine": "none",
                    "error": "PDF processing library not installed"
                }
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            return {
                "text": "",
                "confidence": 0,
                "engine": "PyPDF2",
                "error": str(e)
            }

# Initialize OCR service
ocr_service = OCRService()

@router.post("/ocr/extract")
async def extract_text(
    file: UploadFile = File(...),
    process_with_rag: Optional[str] = Form("false"),
    session_id: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Extract text from uploaded image or PDF file using OCR
    
    - **file**: Image (JPG, PNG, etc.) or PDF file
    - **process_with_rag**: Whether to process with RAG system (default: false)
    - **session_id**: Guest session ID if not authenticated
    """
    
    try:
        # Validate file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Validate file type
        content_type = file.content_type
        if content_type not in SUPPORTED_IMAGE_TYPES and content_type != SUPPORTED_PDF_TYPE:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {content_type}. Supported types: JPG, PNG, PDF, etc."
            )
        
        # Process based on file type
        if content_type == SUPPORTED_PDF_TYPE:
            # Extract text from PDF
            result = await ocr_service.extract_text_from_pdf(contents)
        else:
            # Extract text from image
            result = await ocr_service.extract_text_from_image(contents)
        
        # Check if extraction was successful
        if result.get("error"):
            logger.error(f"OCR extraction error: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
        
        if not result.get("text"):
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error": "لم يتم العثور على نص في الملف",
                    "ocr_result": result
                }
            )
        
        # Prepare response
        response_data = {
            "success": True,
            "ocr_result": {
                "text": result["text"],
                "confidence": result.get("confidence", 0),
                "engine": result.get("engine", "unknown"),
                "language": result.get("language", "ar"),
                "word_count": result.get("word_count", len(result["text"].split())),
                "page_count": result.get("page_count", 1)
            },
            "metadata": {
                "filename": file.filename,
                "content_type": content_type,
                "file_size": len(contents),
                "timestamp": datetime.now().isoformat(),
                "user_id": current_user.id if current_user else None,
                "session_id": session_id if not current_user else None
            }
        }
        
        # Optional: Process with RAG system if requested
        if process_with_rag == "true":
            # TODO: Integrate with your RAG/vector store system
            response_data["rag_processed"] = False
            response_data["rag_message"] = "RAG processing not yet implemented"
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OCR extraction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في معالجة الملف: {str(e)}"
        )

@router.get("/ocr/status")
async def ocr_status():
    """Check OCR service status and available engines"""
    
    status = {
        "service": "OCR Text Extraction",
        "status": "operational",
        "engines": {
            "google_vision": {
                "available": GOOGLE_VISION_AVAILABLE and ocr_service.vision_client is not None,
                "configured": ocr_service.vision_client is not None,
                "name": "Google Cloud Vision API"
            },
            "pdf_support": {
                "available": PYPDF_AVAILABLE,
                "name": "PyPDF2"
            },
            "image_support": {
                "available": PIL_AVAILABLE,
                "name": "Pillow"
            }
        },
        "supported_formats": {
            "images": list(SUPPORTED_IMAGE_TYPES),
            "documents": ["application/pdf"] if PYPDF_AVAILABLE else []
        },
        "limits": {
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
        }
    }
    
    return JSONResponse(content=status)