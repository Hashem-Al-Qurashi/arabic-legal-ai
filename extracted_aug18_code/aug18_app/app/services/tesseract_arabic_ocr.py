#!/usr/bin/env python3
"""
Professional Arabic OCR using Tesseract with optimal configuration
Much better than PaddleOCR for Arabic text
"""

import os
import logging
from typing import Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract

logger = logging.getLogger(__name__)

class ProfessionalArabicOCR:
    """
    High-quality Arabic OCR using Tesseract with advanced preprocessing
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._verify_tesseract()
    
    def _verify_tesseract(self):
        """Verify Tesseract and Arabic support"""
        try:
            version = pytesseract.get_tesseract_version()
            langs = pytesseract.get_languages()
            
            if 'ara' not in langs:
                logger.error("❌ Arabic language not installed for Tesseract")
                logger.error("Install with: sudo apt-get install tesseract-ocr-ara")
                raise RuntimeError("Arabic OCR support not available")
            
            logger.info(f"✅ Tesseract {version} with Arabic support ready")
            
        except Exception as e:
            logger.error(f"❌ Tesseract initialization failed: {e}")
            raise
    
    async def extract_arabic_text(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract Arabic text with high accuracy using Tesseract
        """
        try:
            # Convert bytes to image
            image_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Invalid image format")
            
            logger.info("🔍 Starting professional Arabic OCR with Tesseract")
            
            # Apply advanced preprocessing for Arabic
            preprocessed = self._preprocess_for_arabic(image)
            
            # Run OCR with optimal settings
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                self.executor,
                self._run_tesseract_ocr,
                preprocessed
            )
            
            # Clean and validate the text
            cleaned_text = self._clean_arabic_text(text)
            
            # Calculate quality metrics
            confidence = self._calculate_confidence(cleaned_text)
            
            return {
                "success": True,
                "text": cleaned_text,
                "confidence": confidence,
                "engine": "Tesseract-Arabic",
                "word_count": len(cleaned_text.split()),
                "metadata": {
                    "preprocessing": "Advanced Arabic optimization",
                    "language": "ara"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Arabic OCR failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def _preprocess_for_arabic(self, image: np.ndarray) -> np.ndarray:
        """
        Advanced preprocessing specifically optimized for Arabic text
        """
        # Convert to PIL for advanced processing
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # 1. Resize if too small (Arabic needs good resolution)
        width, height = pil_image.size
        if width < 1000:
            scale = 1500 / width
            new_size = (int(width * scale), int(height * scale))
            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # 2. Convert to grayscale
        pil_image = pil_image.convert('L')
        
        # 3. Enhance contrast (critical for Arabic)
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(2.0)
        
        # 4. Apply sharpening
        pil_image = pil_image.filter(ImageFilter.SHARPEN)
        
        # 5. Denoise while preserving edges
        img_array = np.array(pil_image)
        denoised = cv2.bilateralFilter(img_array, 9, 75, 75)
        
        # 6. Binarization with Otsu's method
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 7. Remove small noise
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # 8. Slight dilation to connect broken Arabic characters
        kernel_dilation = np.ones((1,1), np.uint8)
        final = cv2.dilate(cleaned, kernel_dilation, iterations=1)
        
        return final
    
    def _run_tesseract_ocr(self, image: np.ndarray) -> str:
        """
        Run Tesseract with optimal Arabic configuration
        """
        # Convert to PIL
        pil_image = Image.fromarray(image)
        
        # Optimal Tesseract configuration for Arabic
        custom_config = r"""
            --oem 3
            --psm 6
            -l ara
            -c preserve_interword_spaces=1
            -c textord_heavy_nr=1
            -c edges_max_children_per_outline=40
            -c tosp_old_sp_kn_th_factor=2
            -c tosp_threshold_bias2=1
            -c tessedit_write_images=0
        """
        
        # Run OCR
        text = pytesseract.image_to_string(
            pil_image,
            config=custom_config.strip()
        )
        
        return text
    
    def _clean_arabic_text(self, text: str) -> str:
        """
        Clean and normalize Arabic text
        """
        import re
        
        if not text:
            return ""
        
        # Remove non-Arabic/non-essential characters but keep numbers and punctuation
        # Arabic Unicode range: \u0600-\u06FF, \u0750-\u077F
        cleaned = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u0660-\u0669\u06F0-\u06F9\s\d\(\)\.,\-/:؛،]', '', text)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Fix common OCR mistakes in Arabic
        replacements = {
            'ىلع': 'على',
            'ىلإ': 'إلى',
            'نم': 'من',
            'ىف': 'في',
            'دق': 'قد',
            'امك': 'كما'
        }
        
        for wrong, correct in replacements.items():
            cleaned = cleaned.replace(wrong, correct)
        
        return cleaned.strip()
    
    def _calculate_confidence(self, text: str) -> float:
        """
        Calculate confidence score based on text quality
        """
        if not text:
            return 0.0
        
        import re
        
        # Check Arabic content ratio
        arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F]', text))
        total_chars = len(text.replace(' ', ''))
        
        if total_chars == 0:
            return 0.0
        
        arabic_ratio = arabic_chars / total_chars
        
        # Check for reasonable text length
        word_count = len(text.split())
        length_score = min(word_count / 50, 1.0)
        
        # Combined confidence
        confidence = (arabic_ratio * 0.7 + length_score * 0.3)
        
        return min(confidence, 0.95)

# Global instance
professional_arabic_ocr = ProfessionalArabicOCR()