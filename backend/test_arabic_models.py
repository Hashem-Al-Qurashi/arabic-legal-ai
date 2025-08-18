#!/usr/bin/env python3
"""
Test different Arabic models in PaddleOCR
"""

from paddleocr import PaddleOCR
import cv2
import numpy as np

def test_arabic_models():
    """Test different model configurations for Arabic"""
    
    # Create test image
    img = np.ones((200, 600, 3), dtype=np.uint8) * 255
    cv2.putText(img, "Arabic Test Sample", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Different model configurations to test
    configs = [
        {
            "name": "Arabic Default",
            "params": {"lang": "ar"}
        },
        {
            "name": "Arabic with Orientation",
            "params": {"lang": "ar", "use_textline_orientation": True}
        },
        {
            "name": "Arabic Server Model (if available)",
            "params": {"lang": "ar", "use_textline_orientation": True, "rec_model_dir": None}
        }
    ]
    
    print("🧪 Testing Arabic model configurations...")
    
    for config in configs:
        print(f"\n{'='*50}")
        print(f"🔍 Testing: {config['name']}")
        
        try:
            ocr = PaddleOCR(**config['params'])
            results = ocr.ocr(img)
            
            print("✅ Model loaded successfully")
            
            if results and len(results) > 0:
                result = results[0]
                if hasattr(result, 'rec_texts'):
                    print(f"📝 Texts: {result.rec_texts}")
                    print(f"🎯 Scores: {result.rec_scores}")
                else:
                    print(f"📝 Result type: {type(result)}")
                    
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # Check what models are actually available
    print(f"\n{'='*50}")
    print("🔍 Checking available language models...")
    
    try:
        # Try to get model info
        ocr = PaddleOCR(lang='ar')
        print("✅ Arabic language model successfully loaded")
        
        # Check what happens with a more complex Arabic-like pattern
        arabic_pattern = np.ones((150, 400, 3), dtype=np.uint8) * 255
        # Draw some lines that mimic Arabic text direction
        cv2.line(arabic_pattern, (50, 75), (350, 75), (0, 0, 0), 2)
        cv2.line(arabic_pattern, (50, 100), (300, 100), (0, 0, 0), 2)
        
        results = ocr.ocr(arabic_pattern)
        print(f"📊 Test with Arabic-style pattern: {len(results)} results")
        
    except Exception as e:
        print(f"❌ Arabic model test failed: {e}")

if __name__ == "__main__":
    test_arabic_models()