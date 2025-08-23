#!/usr/bin/env python3
"""
Test multiple OCR engines for Arabic text comparison
"""

import cv2
import numpy as np
from paddleocr import PaddleOCR
import io
from PIL import Image

def load_test_image():
    """Load a test Arabic image - you'll need to provide the actual screenshot"""
    # For now, create a simple test image
    img = np.ones((300, 800, 3), dtype=np.uint8) * 255
    
    # Add some text that mimics Arabic (using readable text for testing)
    cv2.putText(img, "Legal Document Test", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Arabic Text Sample", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Court Filing Example", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    return img

def test_different_preprocessing(image):
    """Test different preprocessing approaches"""
    
    preprocessed_images = {}
    
    # 1. Original (minimal processing)
    preprocessed_images["original"] = image
    
    # 2. Grayscale conversion
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    preprocessed_images["grayscale"] = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    # 3. Gaussian blur to smooth text
    blurred = cv2.GaussianBlur(gray, (1, 1), 0)
    preprocessed_images["blurred"] = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
    
    # 4. Morphological operations for text cleaning
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    preprocessed_images["morphology"] = cv2.cvtColor(morph, cv2.COLOR_GRAY2BGR)
    
    # 5. Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast = clahe.apply(gray)
    preprocessed_images["contrast"] = cv2.cvtColor(contrast, cv2.COLOR_GRAY2BGR)
    
    # 6. Threshold to pure black/white
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    preprocessed_images["threshold"] = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    
    return preprocessed_images

def test_paddle_ocr_configs(image):
    """Test different PaddleOCR configurations"""
    
    configs = [
        {"name": "Standard Arabic", "params": {"lang": "ar"}},
        {"name": "Arabic + Orientation", "params": {"lang": "ar", "use_textline_orientation": True}},
        {"name": "Arabic + No Orientation", "params": {"lang": "ar", "use_textline_orientation": False}},
    ]
    
    results = {}
    
    for config in configs:
        try:
            print(f"\n🧪 Testing: {config['name']}")
            ocr = PaddleOCR(**config['params'])
            
            # Test with original image
            paddle_results = ocr.ocr(image)
            
            extracted_text = ""
            if paddle_results and len(paddle_results) > 0:
                result = paddle_results[0]
                if hasattr(result, 'rec_texts'):
                    extracted_text = " ".join(result.rec_texts)
                    print(f"📝 Extracted: {extracted_text}")
                    print(f"🎯 Confidence: {result.rec_scores}")
            
            results[config['name']] = extracted_text
            
        except Exception as e:
            print(f"❌ Failed {config['name']}: {e}")
            results[config['name']] = f"Error: {e}"
    
    return results

def main():
    """Run comprehensive OCR testing"""
    
    print("🧪 Multi-Engine Arabic OCR Testing")
    print("="*60)
    
    # Load test image
    test_image = load_test_image()
    print(f"📷 Test image loaded: {test_image.shape}")
    
    # Test different preprocessing
    print(f"\n🔧 Testing preprocessing approaches...")
    preprocessed_images = test_different_preprocessing(test_image)
    
    # Test PaddleOCR with different configs and preprocessing
    for prep_name, prep_image in preprocessed_images.items():
        print(f"\n{'='*40}")
        print(f"🖼️ Testing with: {prep_name} preprocessing")
        
        # Test with standard Arabic config
        try:
            ocr = PaddleOCR(lang='ar')
            results = ocr.ocr(prep_image)
            
            if results and len(results) > 0:
                result = results[0]
                if hasattr(result, 'rec_texts') and result.rec_texts:
                    text = " ".join(result.rec_texts)
                    avg_conf = np.mean(result.rec_scores) if result.rec_scores else 0
                    print(f"📝 {prep_name}: {text}")
                    print(f"🎯 Confidence: {avg_conf:.3f}")
                else:
                    print(f"📝 {prep_name}: No text extracted")
            else:
                print(f"📝 {prep_name}: No results")
                
        except Exception as e:
            print(f"❌ {prep_name} failed: {e}")
    
    print(f"\n{'='*60}")
    print("🏁 OCR testing complete!")
    print("\n💡 Recommendations:")
    print("1. Try uploading your screenshot again with the current system")
    print("2. If still poor quality, we'll need to implement Tesseract or EasyOCR")
    print("3. Consider using higher resolution images")

if __name__ == "__main__":
    main()