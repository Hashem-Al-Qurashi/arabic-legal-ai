#!/usr/bin/env python3
"""
Debug PaddleOCR v5 output format
"""

from paddleocr import PaddleOCR
import numpy as np
import cv2
import json

# Create a test image with Arabic text
test_img = np.ones((200, 600, 3), dtype=np.uint8) * 255
cv2.putText(test_img, "Test Arabic", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# Initialize OCR with new parameter
ocr = PaddleOCR(use_textline_orientation=True, lang='ar')

# Run OCR
print("🔍 Running OCR...")
results = ocr.ocr(test_img)

print(f"\n📊 Results type: {type(results)}")
print(f"📊 Results length: {len(results) if results else 0}")

if results:
    print(f"\n🔍 Full results structure:")
    print(f"Type of results: {type(results)}")
    print(f"Number of items: {len(results)}")
    
    if len(results) > 0:
        first_result = results[0]
        print(f"\n🔍 First result:")
        print(f"Type: {type(first_result)}")
        
        if isinstance(first_result, dict):
            print(f"Keys: {first_result.keys()}")
            print(f"\n📝 Dict contents:")
            for key, value in first_result.items():
                if key in ['rec_texts', 'rec_scores', 'rec_polys']:
                    print(f"  {key}: {type(value)} with {len(value) if hasattr(value, '__len__') else 'N/A'} items")
                    if hasattr(value, '__len__') and len(value) > 0:
                        print(f"    First item: {value[0] if len(value) > 0 else 'empty'}")
                elif key not in ['input_img', 'rot_img', 'output_img']:  # Skip large image arrays
                    print(f"  {key}: {value}")
        elif isinstance(first_result, list):
            print(f"List length: {len(first_result)}")
            if len(first_result) > 0:
                print(f"First item type: {type(first_result[0])}")
                print(f"First item: {first_result[0]}")
                
print("\n✅ Debug complete!")