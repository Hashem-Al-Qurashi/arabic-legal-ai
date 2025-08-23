#!/usr/bin/env python3
"""
Test how our preprocessing affects Arabic OCR quality
"""

import cv2
import numpy as np
from paddleocr import PaddleOCR
from app.services.ocr_service import ArabicOCRService

def create_test_arabic_image():
    """Create a test image with Arabic text"""
    # Create white background
    img = np.ones((200, 600, 3), dtype=np.uint8) * 255
    
    # Add some clear black Arabic-style text (using English for testing)
    cv2.putText(img, "Arabic Text Test", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Legal Document", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    return img

def test_preprocessing_steps():
    """Test OCR with and without our preprocessing"""
    
    print("🧪 Testing preprocessing impact on Arabic OCR")
    print("="*60)
    
    # Create test image
    original_img = create_test_arabic_image()
    
    # Initialize OCR
    ocr = PaddleOCR(lang='ar')
    
    # Test 1: Raw image (no preprocessing)
    print("\n🔍 Test 1: Raw image (no preprocessing)")
    try:
        results_raw = ocr.ocr(original_img)
        print(f"✅ Raw OCR successful")
        
        if results_raw and len(results_raw) > 0:
            result = results_raw[0]
            if hasattr(result, 'rec_texts'):
                print(f"📝 Raw texts: {result.rec_texts}")
                print(f"🎯 Raw scores: {result.rec_scores}")
            else:
                print(f"📝 Raw result: {result}")
    except Exception as e:
        print(f"❌ Raw OCR failed: {e}")
    
    # Test 2: Our current preprocessing
    print("\n🔍 Test 2: With our current preprocessing")
    try:
        # Apply our preprocessing (from ocr_service.py)
        service = ArabicOCRService()
        processed_img = service._preprocess_image(original_img)
        
        results_processed = ocr.ocr(processed_img)
        print(f"✅ Processed OCR successful")
        
        if results_processed and len(results_processed) > 0:
            result = results_processed[0]
            if hasattr(result, 'rec_texts'):
                print(f"📝 Processed texts: {result.rec_texts}")
                print(f"🎯 Processed scores: {result.rec_scores}")
            else:
                print(f"📝 Processed result: {result}")
    except Exception as e:
        print(f"❌ Processed OCR failed: {e}")
    
    # Test 3: Minimal preprocessing
    print("\n🔍 Test 3: Minimal preprocessing (just BGR check)")
    try:
        # Minimal preprocessing - just ensure 3 channels
        minimal_img = original_img.copy()
        if len(minimal_img.shape) == 2:
            minimal_img = cv2.cvtColor(minimal_img, cv2.COLOR_GRAY2BGR)
        
        results_minimal = ocr.ocr(minimal_img)
        print(f"✅ Minimal OCR successful")
        
        if results_minimal and len(results_minimal) > 0:
            result = results_minimal[0]
            if hasattr(result, 'rec_texts'):
                print(f"📝 Minimal texts: {result.rec_texts}")
                print(f"🎯 Minimal scores: {result.rec_scores}")
            else:
                print(f"📝 Minimal result: {result}")
    except Exception as e:
        print(f"❌ Minimal OCR failed: {e}")
    
    print("\n" + "="*60)
    print("🔍 Preprocessing test complete!")

if __name__ == "__main__":
    test_preprocessing_steps()