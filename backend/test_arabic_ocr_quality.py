#!/usr/bin/env python3
"""
Test Arabic OCR quality with different configurations
"""

from paddleocr import PaddleOCR
import cv2
import numpy as np

def test_arabic_ocr_configs():
    """Test different PaddleOCR configurations for Arabic"""
    
    # Create test image with clear Arabic text
    test_img = np.ones((400, 800, 3), dtype=np.uint8) * 255
    
    # Add some Arabic text (you can replace this with actual Arabic)
    arabic_text = "النص العربي واضح"
    
    # Test configurations
    configs = [
        {
            "name": "Basic Arabic",
            "params": {"lang": "ar"}
        },
        {
            "name": "Arabic with text orientation", 
            "params": {"lang": "ar", "use_textline_orientation": True}
        },
        {
            "name": "Arabic with all features",
            "params": {
                "lang": "ar", 
                "use_textline_orientation": True,
                "use_gpu": False,
                "enable_mkldnn": False
            }
        }
    ]
    
    print("🔍 Testing Arabic OCR configurations...")
    
    for config in configs:
        print(f"\n{'='*50}")
        print(f"🧪 Testing: {config['name']}")
        print(f"📋 Parameters: {config['params']}")
        
        try:
            # Initialize OCR
            ocr = PaddleOCR(**config['params'])
            
            # Test with white image (should return empty or minimal results)
            results = ocr.ocr(test_img)
            
            print(f"✅ Initialization: SUCCESS")
            print(f"📊 Results type: {type(results)}")
            print(f"📊 Results length: {len(results) if results else 0}")
            
            if results and len(results) > 0:
                first_result = results[0]
                print(f"🔍 First result type: {type(first_result)}")
                
                # Check for OCRResult format
                if hasattr(first_result, 'rec_texts'):
                    texts = first_result.rec_texts
                    scores = first_result.rec_scores
                    print(f"📝 Extracted texts: {texts}")
                    print(f"🎯 Confidence scores: {scores}")
                elif isinstance(first_result, list):
                    print(f"📝 Legacy format with {len(first_result)} items")
                    for i, item in enumerate(first_result[:3]):  # Show first 3
                        print(f"   Item {i}: {item}")
                        
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print(f"\n{'='*50}")
    print("🔍 Testing complete!")

if __name__ == "__main__":
    test_arabic_ocr_configs()