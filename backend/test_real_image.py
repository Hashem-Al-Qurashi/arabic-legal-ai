#!/usr/bin/env python3
"""
Test with actual image processing like the server does
"""

from paddleocr import PaddleOCR
import cv2
import numpy as np

# Initialize OCR exactly like the server
ocr = PaddleOCR(use_textline_orientation=True, lang='ar')

# Create test image with some text (like a real screenshot)
test_img = np.ones((300, 800, 3), dtype=np.uint8) * 255
cv2.putText(test_img, "Arabic Test", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

# Preprocess like our service does
gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
denoised = cv2.fastNlMeansDenoising(gray)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
enhanced = clahe.apply(denoised)
processed_image = cv2.GaussianBlur(enhanced, (1, 1), 0)

print("🔍 Running OCR on processed image...")

try:
    results = ocr.ocr(processed_image)
    print(f"✅ OCR completed successfully")
    print(f"Results type: {type(results)}")
    print(f"Results length: {len(results) if results else 0}")
    
    if results and len(results) > 0:
        first_result = results[0]
        print(f"First result type: {type(first_result)}")
        
        if hasattr(first_result, 'rec_texts'):
            print(f"✅ Has rec_texts: {len(first_result.rec_texts)} items")
            if first_result.rec_texts:
                print(f"Text found: {first_result.rec_texts}")
        else:
            print(f"❌ No rec_texts attribute!")
            print(f"Available attributes: {dir(first_result)}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()