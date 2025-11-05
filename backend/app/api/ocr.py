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
        
        # Try direct REST API approach first if we have an API key
        google_api_key = os.getenv('GOOGLE_VISION_API_KEY')
        if google_api_key:
            try:
                import requests
                import base64
                
                # Use REST API directly - more reliable for API key auth
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                url = f"https://vision.googleapis.com/v1/images:annotate?key={google_api_key}"
                payload = {
                    "requests": [{
                        "image": {"content": image_b64},
                        "features": [{"type": "DOCUMENT_TEXT_DETECTION", "maxResults": 1}],
                        "imageContext": {"languageHints": ["ar", "en"], "textDetectionParams": {"enableTextDetectionConfidenceScore": True}}
                    }]
                }
                
                logger.info(f"Making direct REST API call to Google Vision...")
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                
                result = response.json()
                
                if 'responses' not in result or not result['responses']:
                    raise Exception("Invalid response format from Google Vision API")
                
                vision_response = result['responses'][0]
                
                if 'error' in vision_response:
                    error = vision_response['error']
                    raise Exception(f"Google Vision API error {error['code']}: {error['message']}")
                
                # Extract text from response
                full_text = ""
                confidence_scores = []
                
                if 'fullTextAnnotation' in vision_response:
                    full_text = vision_response['fullTextAnnotation'].get('text', '').strip()
                    
                    # Extract confidence scores
                    for page in vision_response['fullTextAnnotation'].get('pages', []):
                        for block in page.get('blocks', []):
                            if 'confidence' in block:
                                confidence_scores.append(block['confidence'])
                
                avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
                
                logger.info(f"Google Vision REST API success. Text length: {len(full_text)}")
                
                return {
                    "text": full_text,
                    "confidence": avg_confidence,
                    "engine": "Google Vision REST API",
                    "language": "ar",
                    "word_count": len(full_text.split()) if full_text else 0
                }
                
            except Exception as e:
                logger.error(f"Google Vision REST API failed: {str(e)}")
                # Fall back to client library or demo mode
        
        if not self.vision_client:
            # Return demo mode response when Google Vision is not configured
            demo_text = """[نموذج تجريبي - Demo Mode]
            
هذا نص تجريبي لخدمة استخراج النص من الصور.
This is a demo text for the OCR service.

الخدمة الفعلية تتطلب تكوين Google Vision API.
The actual service requires Google Vision API configuration.

يمكنك رفع الصور ولكن سيتم عرض هذا النص التجريبي.
You can upload images but this demo text will be shown.

للحصول على استخراج نص حقيقي، يرجى تكوين:
For real text extraction, please configure:
- GOOGLE_VISION_API_KEY or
- GOOGLE_APPLICATION_CREDENTIALS"""
            
            return {
                "text": demo_text,
                "confidence": 0.95,
                "engine": "Demo Mode",
                "error": None,
                "warning": "OCR في وضع تجريبي - Google Vision API غير مكون",
                "demo_mode": True
            }
        
        try:
            # Create vision image object
            image = vision.Image(content=image_bytes)
            
            # Perform text detection with Arabic language hint and enhanced parameters
            image_context = vision.ImageContext(
                language_hints=["ar", "en"],
                text_detection_params=vision.TextDetectionParams(
                    enable_text_detection_confidence_score=True
                )
            )
            response = self.vision_client.document_text_detection(
                image=image,
                image_context=image_context
            )
            
            # Check for errors
            if response.error.message:
                raise Exception(response.error.message)
            
            # Extract text and confidence
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # Debug logging
            logger.info(f"Google Vision response received. Text length: {len(full_text)}")
            if not full_text:
                logger.warning("Google Vision returned empty text - image may not contain readable text")
            
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
            error_msg = str(e)
            logger.error(f"Google Vision OCR failed: {error_msg}")
            
            # Provide more helpful error messages
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                user_error = "تم تجاوز الحد اليومي لخدمة Google Vision API"
            elif "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
                user_error = "مفتاح Google Vision API غير صالح أو غير مخول"
            elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
                user_error = "لا توجد صلاحية للوصول إلى Google Vision API"
            else:
                user_error = f"خطأ في Google Vision API: {error_msg}"
            
            return {
                "text": "",
                "confidence": 0,
                "engine": "Google Vision", 
                "error": user_error,
                "technical_error": error_msg
            }
    
    async def extract_text_from_pdf_via_ocr(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text from PDF using Google Vision OCR (for Arabic PDFs with encoding issues)"""
        
        try:
            # Import PyMuPDF for PDF to image conversion
            import fitz  # PyMuPDF
            import io
            from PIL import Image
            
            logger.info("Converting PDF pages to images for OCR processing")
            
            # Open PDF document
            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            all_text = []
            total_confidence = 0
            page_count = 0
            
            # Process each page
            for page_num in range(len(pdf_doc)):
                try:
                    # Get page
                    page = pdf_doc[page_num]
                    
                    # Convert page to image with high DPI for better OCR
                    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Convert to PIL Image
                    img_data = pix.tobytes("png")
                    
                    # Perform OCR on the page image
                    ocr_result = await self.extract_text_from_image(img_data)
                    
                    if ocr_result.get("text"):
                        page_text = ocr_result["text"].strip()
                        if page_text:
                            all_text.append(f"=== صفحة {page_num + 1} ===\n{page_text}")
                            total_confidence += ocr_result.get("confidence", 0)
                            logger.info(f"Page {page_num + 1}: Extracted {len(page_text)} characters")
                        else:
                            logger.info(f"Page {page_num + 1}: No text found")
                    else:
                        logger.warning(f"Page {page_num + 1}: OCR failed")
                    
                    page_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                    all_text.append(f"=== صفحة {page_num + 1} ===\n[خطأ في معالجة هذه الصفحة: {str(e)}]")
                    page_count += 1
            
            # Close PDF document
            pdf_doc.close()
            
            # Combine all page texts
            full_text = "\n\n".join(all_text)
            avg_confidence = total_confidence / page_count if page_count > 0 else 0
            
            logger.info(f"PDF OCR completed: {page_count} pages, {len(full_text)} total characters")
            
            return {
                "text": full_text,
                "confidence": avg_confidence,
                "engine": "PyMuPDF + Google Vision OCR",
                "language": "ar",
                "word_count": len(full_text.split()) if full_text else 0,
                "page_count": page_count
            }
            
        except ImportError as e:
            logger.error(f"Required libraries not available: {str(e)}")
            return {
                "text": "[خطأ: المكتبات المطلوبة لمعالجة PDF غير متوفرة. يرجى تثبيت PyMuPDF و Pillow.]",
                "confidence": 0,
                "engine": "Missing dependencies",
                "language": "ar",
                "word_count": 0,
                "page_count": 0,
                "error": f"Missing dependencies: {str(e)}"
            }
        except Exception as e:
            logger.error(f"PDF OCR failed: {str(e)}")
            return {
                "text": "",
                "confidence": 0,
                "engine": "PDF OCR failed",
                "language": "ar",
                "word_count": 0,
                "page_count": 0,
                "error": str(e)
            }

    async def extract_text_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text from PDF, using Google Vision OCR for Arabic PDFs"""
        
        # For Arabic legal documents, skip PyPDF2 and use Google Vision directly
        # This avoids character encoding issues common with Arabic fonts
        google_api_key = os.getenv('GOOGLE_VISION_API_KEY')
        if google_api_key:
            logger.info("Using Google Vision OCR for PDF (better Arabic support)")
            try:
                import requests
                import base64
                
                # Convert PDF to base64 for Google Vision
                pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
                
                url = f"https://vision.googleapis.com/v1/files:annotate?key={google_api_key}"
                payload = {
                    "requests": [{
                        "inputConfig": {
                            "content": pdf_b64,
                            "mimeType": "application/pdf"
                        },
                        "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                        "imageContext": {"languageHints": ["ar", "en"], "textDetectionParams": {"enableTextDetectionConfidenceScore": True}}
                    }]
                }
                
                response = requests.post(url, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'responses' in result and result['responses']:
                        vision_response = result['responses'][0]
                        
                        if 'error' not in vision_response and 'fullTextAnnotation' in vision_response:
                            full_text = vision_response['fullTextAnnotation'].get('text', '').strip()
                            logger.info(f"Google Vision PDF success. Text length: {len(full_text)}")
                            
                            return {
                                "text": full_text,
                                "confidence": 0.9,
                                "engine": "Google Vision PDF OCR",
                                "language": "ar",
                                "word_count": len(full_text.split()) if full_text else 0,
                                "page_count": 1
                            }
                
                # Fall back to PyPDF2 if Google Vision fails
                logger.warning("Google Vision PDF OCR failed, falling back to PyPDF2")
                
            except Exception as e:
                logger.error(f"Google Vision PDF OCR failed: {str(e)}")
                # Fall back to PyPDF2
        
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
                            # Check if text contains garbled characters (common with Arabic PDFs)
                            garbled_chars = ['Ú', 'Ý', 'Þ', 'ß', 'à', 'Û', 'Ü', '§', '¢', '¦', '°', '²', '³', 'Ñ', 'Ô', 'Õ', 'Ø', 'É', 'Æ', 'á', 'é', 'è', 'â', 'ç', 'î', 'ê', 'ì', 'ð', 'ô', 'ù', 'û', 'ü', 'ÿ']
                            garbled_count = sum(1 for char in garbled_chars if char in page_text)
                            
                            # If more than 2% of text is garbled characters, force OCR (lowered threshold)
                            if garbled_count > len(page_text) * 0.02:
                                logger.info(f"Page {page_num + 1}: Detected garbled Arabic text ({garbled_count} garbled chars), forcing OCR for entire PDF")
                                # Skip PyPDF2 extraction completely and force Google Vision OCR
                                return await self.extract_text_from_pdf_via_ocr(pdf_bytes)
                            else:
                                # Text extraction successful with good encoding
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
        
        # Check if extraction was successful or in demo mode
        if result.get("demo_mode"):
            # Demo mode - return success with demo text
            logger.info(f"OCR in demo mode for file: {file.filename}")
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "demo_mode": True,
                    "warning": result.get("warning"),
                    "ocr_result": result,
                    "metadata": {
                        "filename": file.filename,
                        "content_type": content_type,
                        "file_size": len(contents),
                        "timestamp": datetime.now().isoformat(),
                        "user_id": current_user.id if current_user else None,
                        "session_id": session_id if not current_user else None
                    }
                }
            )
        elif result.get("error"):
            logger.error(f"OCR extraction error: {result['error']}")
            # Real error - return error response
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error": f"تعذر استخراج النص من الملف: {result['error']}",
                    "ocr_result": result,
                    "metadata": {
                        "filename": file.filename,
                        "content_type": content_type,
                        "file_size": len(contents),
                        "timestamp": datetime.now().isoformat(),
                        "user_id": current_user.id if current_user else None,
                        "session_id": session_id if not current_user else None
                    }
                }
            )
        
        if not result.get("text"):
            # Distinguish between processing errors and no text found
            error_message = "لم يتم العثور على نص في الملف"
            
            # If there was a technical error, use that instead
            if result.get("error"):
                error_message = f"خطأ في معالجة الملف: {result['error']}"
            # If it's a PDF, provide more specific guidance
            elif content_type == SUPPORTED_PDF_TYPE:
                error_message = "لم يتم العثور على نص في ملف PDF. قد يكون الملف يحتوي على صور فقط أو محمي بكلمة مرور"
            # If it's an image, provide image-specific guidance
            else:
                error_message = "لم يتم العثور على نص واضح في الصورة. يرجى التأكد من وضوح النص وجودة الصورة"
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error": error_message,
                    "ocr_result": result,
                    "suggestions": [
                        "تأكد من وضوح النص في الملف",
                        "تحقق من أن الملف غير محمي أو مشفر",
                        "جرب رفع ملف بجودة أفضل"
                    ],
                    "metadata": {
                        "filename": file.filename,
                        "content_type": content_type,
                        "file_size": len(contents),
                        "timestamp": datetime.now().isoformat(),
                        "user_id": current_user.id if current_user else None,
                        "session_id": session_id if not current_user else None
                    }
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