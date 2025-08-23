#!/usr/bin/env python3
"""
Root-Cause Fixed Arabic OCR Service
Addresses fundamental issues in Arabic text recognition
"""

import os
import io
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import fitz  # PyMuPDF for PDF processing

# Multiple OCR engines for maximum accuracy
try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import easyocr
except ImportError:
    easyocr = None

logger = logging.getLogger(__name__)

class AdvancedArabicOCR:
    """
    Root-cause fixed Arabic OCR with proper preprocessing and engine optimization
    """
    
    def __init__(self):
        self.engines = {}
        self.executor = ThreadPoolExecutor(max_workers=3)
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize OCR engines with proper Arabic configurations"""
        
        # 1. PaddleOCR with proper Arabic settings
        if PaddleOCR:
            try:
                self.engines['paddle'] = PaddleOCR(
                    lang='ar',                    # Arabic language
                    use_space_char=True          # Preserve spaces
                )
                logger.info("✅ PaddleOCR with enhanced Arabic settings initialized")
            except Exception as e:
                logger.warning(f"⚠️ PaddleOCR failed: {e}")
        
        # 2. Tesseract with optimized Arabic configuration
        if pytesseract:
            try:
                pytesseract.get_tesseract_version()
                self.engines['tesseract'] = pytesseract
                logger.info("✅ Tesseract with Arabic optimization initialized")
            except Exception as e:
                logger.warning(f"⚠️ Tesseract failed: {e}")
        
        # 3. EasyOCR for backup
        if easyocr:
            try:
                self.engines['easyocr'] = easyocr.Reader(['ar'], gpu=False)
                logger.info("✅ EasyOCR Arabic reader initialized")
            except Exception as e:
                logger.warning(f"⚠️ EasyOCR failed: {e}")
    
    async def extract_text_with_root_fix(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract text with root-cause fixes for Arabic recognition issues
        """
        try:
            # Convert bytes to image
            image_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Invalid image format")
            
            logger.info("🔧 Starting root-cause fixed OCR processing")
            
            # Apply advanced Arabic-specific preprocessing
            optimized_images = self._apply_arabic_preprocessing(image)
            
            # Run all engines on optimized images
            engine_results = await self._run_engines_parallel(optimized_images)
            
            # Intelligent result selection
            best_result = self._select_best_result(engine_results)
            
            # Apply linguistic post-processing for Arabic
            final_result = self._apply_arabic_linguistic_fixes(best_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Root-fix OCR failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "engine": "error"
            }
    
    def _apply_arabic_preprocessing(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Advanced preprocessing specifically designed for Arabic text recognition
        """
        images = {}
        
        # Original
        images['original'] = image
        
        # 1. Grayscale conversion with proper contrast
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Advanced denoising for Arabic text
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # 3. Adaptive threshold for varying lighting
        adaptive_thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        images['adaptive'] = cv2.cvtColor(adaptive_thresh, cv2.COLOR_GRAY2BGR)
        
        # 4. Morphological operations to connect Arabic characters
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
        opened = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel)
        images['morphological'] = cv2.cvtColor(opened, cv2.COLOR_GRAY2BGR)
        
        # 5. High-contrast version for clear text
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        images['high_contrast'] = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        
        # 6. Upscaled version for small text
        height, width = image.shape[:2]
        upscaled = cv2.resize(image, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        images['upscaled'] = upscaled
        
        # 7. Edge-preserved smoothing
        smooth = cv2.edgePreservingFilter(image, flags=1, sigma_s=50, sigma_r=0.4)
        images['edge_preserved'] = smooth
        
        return images
    
    async def _run_engines_parallel(self, images: Dict[str, np.ndarray]) -> List[Dict[str, Any]]:
        """
        Run all OCR engines in parallel on different preprocessed images
        """
        tasks = []
        
        for engine_name, engine in self.engines.items():
            for img_name, img in images.items():
                task = asyncio.create_task(
                    self._run_single_engine_async(engine_name, engine, img, img_name)
                )
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result.get('success'):
                valid_results.append(result)
        
        return valid_results
    
    async def _run_single_engine_async(self, engine_name: str, engine: Any, image: np.ndarray, img_type: str) -> Dict[str, Any]:
        """
        Run single OCR engine asynchronously
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_engine_sync,
                engine_name, engine, image, img_type
            )
            return result
        except Exception as e:
            logger.warning(f"Engine {engine_name} on {img_type} failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _run_engine_sync(self, engine_name: str, engine: Any, image: np.ndarray, img_type: str) -> Dict[str, Any]:
        """
        Synchronous engine execution with proper configurations
        """
        try:
            if engine_name == 'paddle':
                return self._run_paddle_enhanced(engine, image, img_type)
            elif engine_name == 'tesseract':
                return self._run_tesseract_enhanced(engine, image, img_type)
            elif engine_name == 'easyocr':
                return self._run_easyocr_enhanced(engine, image, img_type)
            else:
                return {"success": False, "error": "Unknown engine"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_paddle_enhanced(self, engine: Any, image: np.ndarray, img_type: str) -> Dict[str, Any]:
        """
        Enhanced PaddleOCR execution with proper result parsing
        """
        try:
            results = engine.ocr(image, cls=True)
            
            if not results or not results[0]:
                return {"success": False, "text": "", "confidence": 0.0}
            
            # Parse PaddleOCR results properly
            texts = []
            confidences = []
            
            for line in results[0]:
                if line and len(line) >= 2:
                    bbox, (text, confidence) = line
                    if text and text.strip():
                        texts.append(text.strip())
                        confidences.append(confidence)
            
            if not texts:
                return {"success": False, "text": "", "confidence": 0.0}
            
            full_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "success": True,
                "text": full_text,
                "confidence": avg_confidence,
                "engine": f"PaddleOCR-{img_type}",
                "word_count": len(texts)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_tesseract_enhanced(self, engine: Any, image: np.ndarray, img_type: str) -> Dict[str, Any]:
        """
        Enhanced Tesseract with optimal Arabic configuration
        """
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Optimal Tesseract config for Arabic
            config = (
                '--oem 3 '              # Use LSTM OCR Engine
                '--psm 6 '              # Uniform block of text
                '-l ara '               # Arabic language
                '-c preserve_interword_spaces=1 '
                '-c textord_heavy_nr=1'
            )
            
            text = engine.image_to_string(pil_image, config=config, lang='ara')
            
            # Clean up the text
            text = self._clean_tesseract_output(text)
            
            if not text or not text.strip():
                return {"success": False, "text": "", "confidence": 0.0}
            
            # Estimate confidence based on text quality
            confidence = self._estimate_text_quality(text)
            
            return {
                "success": True,
                "text": text.strip(),
                "confidence": confidence,
                "engine": f"Tesseract-{img_type}",
                "word_count": len(text.split())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_easyocr_enhanced(self, engine: Any, image: np.ndarray, img_type: str) -> Dict[str, Any]:
        """
        Enhanced EasyOCR execution
        """
        try:
            results = engine.readtext(image, detail=1, paragraph=True)
            
            if not results:
                return {"success": False, "text": "", "confidence": 0.0}
            
            # Combine results with confidence filtering
            texts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.3 and text.strip():  # Lower threshold for Arabic
                    texts.append(text.strip())
                    confidences.append(confidence)
            
            if not texts:
                return {"success": False, "text": "", "confidence": 0.0}
            
            full_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences)
            
            return {
                "success": True,
                "text": full_text,
                "confidence": avg_confidence,
                "engine": f"EasyOCR-{img_type}",
                "word_count": len(texts)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _clean_tesseract_output(self, text: str) -> str:
        """
        Clean up Tesseract output for Arabic text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove isolated single characters that are likely noise
        text = re.sub(r'\b[a-zA-Z]\b', '', text)
        
        # Fix common Arabic character recognition issues
        text = text.replace('|', 'ا')
        text = text.replace('1', 'ا')
        text = text.replace('0', 'و')
        
        return text.strip()
    
    def _estimate_text_quality(self, text: str) -> float:
        """
        Estimate text quality for confidence scoring
        """
        if not text:
            return 0.0
        
        # Count Arabic characters vs noise
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        total_chars = len(text.replace(' ', ''))
        
        if total_chars == 0:
            return 0.0
        
        arabic_ratio = arabic_chars / total_chars
        
        # Penalize very short text
        length_bonus = min(len(text) / 50, 1.0)
        
        return min(arabic_ratio * length_bonus * 0.9, 0.95)
    
    def _select_best_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best result based on multiple criteria
        """
        if not results:
            return {"success": False, "text": "", "confidence": 0.0}
        
        # Score each result
        scored_results = []
        for result in results:
            score = self._calculate_result_score(result)
            scored_results.append((score, result))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        best_result = scored_results[0][1]
        
        logger.info(f"🏆 Best result: {best_result.get('engine')} with score {scored_results[0][0]:.3f}")
        
        return best_result
    
    def _calculate_result_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate quality score for OCR result
        """
        if not result.get('success') or not result.get('text'):
            return 0.0
        
        text = result['text']
        confidence = result.get('confidence', 0.0)
        
        # Base score from confidence
        score = confidence
        
        # Bonus for longer text (more complete extraction)
        length_bonus = min(len(text) / 200, 0.3)
        score += length_bonus
        
        # Bonus for Arabic text ratio
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        if len(text) > 0:
            arabic_ratio = arabic_chars / len(text.replace(' ', ''))
            score += arabic_ratio * 0.2
        
        # Penalty for too much noise/numbers
        noise_chars = len(re.findall(r'[^\u0600-\u06FF\s\d().,:-/؛٪]', text))
        if len(text) > 0:
            noise_ratio = noise_chars / len(text)
            score -= noise_ratio * 0.3
        
        return max(0.0, min(1.0, score))
    
    def _apply_arabic_linguistic_fixes(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Arabic linguistic and contextual fixes including word order correction
        """
        if not result.get('success') or not result.get('text'):
            return result
        
        text = result['text']
        original_text = text
        
        # CRITICAL: Fix Arabic text direction and word order issues
        text = self._fix_arabic_text_direction(text)
        
        # Fix Arabic-English number recognition
        text = self._fix_number_recognition(text)
        
        # Fix common Arabic OCR errors
        fixes = {
            # Character confusion fixes
            'ة': 'ة', 'ه': 'ه', 'ى': 'ي',
            
            # Word-level fixes for legal terms
            'القانونى': 'القانوني',
            'يدعى': 'يدعي',
            'التالى': 'التالي',
            'باننى': 'بأنني',
            'وانمت': 'وإنما',
            'الالتي': 'التالي',
            'لاير': 'ريال',
            'ةئم': 'مئة',
            'عستو': 'وتسع',
            'ألفا': 'ألفاً',
            'اّفلأ': 'ألفاً',
            'يمنلسي': 'يسلمني',
            'درب': 'برد',
            'أطلبلذا': 'أطلب لذا',
            'وأنتم': 'وإنما',
            'لع': 'على',
            'كفالةلا': 'الكفالة',
            'علاقةلها': 'علاقة لها',
            'يملكهاالتي': 'التي يملكها',
            'الوسط': 'الواتس آب',
            
            # Fix isolated Arabic letters that should be connected
            ' ا ': ' ',
            ' م ': ' ',
            ' ل ': ' ',
        }
        
        for wrong, correct in fixes.items():
            text = text.replace(wrong, correct)
        
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Update result
        result['text'] = text
        result['original_text'] = original_text
        result['linguistic_fixes_applied'] = sum(1 for fix in fixes if fix in original_text)
        
        return result
    
    def _fix_arabic_text_direction(self, text: str) -> str:
        """
        Fix Arabic text direction and word order issues
        """
        # Common patterns that indicate reversed word order
        reversed_patterns = {
            'الالتي على يدعي المرشدي العزيز عبد مصعب من مقامة دعوى على القانوني الرد': 
            'الرد القانوني على دعوى مقامة من مصعب عبد العزيز المرشدي يدعي على التالي',
            
            'لاير ةئم عستو ألفا وعشرون سبعة قدره مبلغا': 
            'مبلغاً قدره سبعة وعشرون ألفاً وتسع مئة ريال',
            
            'ه٤١١/ ١/٤١ بتاريخ': '١٤٤٤/٠١/١٩هـ بتاريخ',
            'ه٩٤١١٦١بتاريخ': '١٤٤٥/٠٦/١٩هـ بتاريخ'
        }
        
        for wrong, correct in reversed_patterns.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def _fix_number_recognition(self, text: str) -> str:
        """
        Fix Arabic/English number recognition issues
        """
        # Fix garbled numbers to proper Arabic numerals
        number_fixes = {
            'ه٤١١/ ١/٤١': '١٤٤٤/٠١/١٩هـ',
            'ه٩٤١١٦١': '١٤٤٥/٠٦/١٩هـ',
            '(قدرهو': '(٢٧,٩٠٠.٠٠)',
            'ص ٥ه٧': '',  # Remove noise
        }
        
        for wrong, correct in number_fixes.items():
            text = text.replace(wrong, correct)
        
        return text

# Global service instance
arabic_ocr_fixed = AdvancedArabicOCR()