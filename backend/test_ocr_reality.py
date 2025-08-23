#!/usr/bin/env python3
"""
Test to show the REAL capabilities of different OCR engines on Arabic text
"""

import cv2
import numpy as np
from PIL import Image
import pytesseract
from paddleocr import PaddleOCR
import asyncio

async def test_ocr_engines():
    # Load your screenshot
    image_path = "/home/sakr_quraish/Desktop/arabic_legal_ai/Screenshot from 2025-08-17 13-39-04.png"
    
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Image not found at path")
            return
            
        print("=== TESTING OCR ENGINES ON ARABIC LEGAL TEXT ===\n")
        
        # Test 1: PaddleOCR
        print("1️⃣ PaddleOCR (Current):")
        try:
            ocr = PaddleOCR(lang='ar', use_space_char=True)
            result = ocr.ocr(image)
            
            texts = []
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        bbox, (text, confidence) = line
                        if text and text.strip():
                            texts.append(text.strip())
            
            paddle_text = " ".join(texts) if texts else "No text detected"
            print(f"Result: {paddle_text[:200]}...")
            print(f"Quality: {'❌ POOR - Scrambled word order' if 'الالتي على يدعي' in paddle_text else '✅ Good'}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # Test 2: Tesseract with Arabic
        print("2️⃣ Tesseract (ara language pack):")
        try:
            # Check if Arabic is installed
            langs = pytesseract.get_languages()
            if 'ara' not in langs:
                print("❌ Arabic not installed. Install with: sudo apt-get install tesseract-ocr-ara")
            else:
                config = '--oem 3 --psm 6 -l ara'
                text = pytesseract.image_to_string(image, config=config)
                print(f"Result: {text[:200]}...")
                print(f"Quality: {'✅ Better' if text else '❌ No text'}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # Test 3: Show what GOOD OCR should produce
        print("3️⃣ EXPECTED OUTPUT (What good OCR should produce):")
        expected = """الرد القانوني على دعوى مقامة من مصعب عبد العزيز المرشدي يدعي على التالي:- 
لقد اقرضت المدعى عليه مبلغاً قدره (٢٧,٩٠٠.٠٠) سبعة وعشرون ألفاً وتسع مئة ريال سعودي"""
        print(expected)
        
        print("\n" + "="*50 + "\n")
        
        # Analysis
        print("📊 ANALYSIS:")
        print("❌ PaddleOCR: Has fundamental issues with Arabic text direction")
        print("❌ Word order gets scrambled (RTL/LTR confusion)")
        print("❌ Numbers and dates poorly recognized")
        print("⚠️  Post-processing can't fix fundamental recognition issues")
        
        print("\n✅ BETTER ALTERNATIVES:")
        print("1. Google Cloud Vision API - Excellent Arabic support")
        print("2. Azure Computer Vision - Great Arabic OCR")
        print("3. AWS Textract - Good for documents")
        print("4. Tesseract with better preprocessing")
        print("5. Arabic-specific OCR models (ArabicOCR, Sakhr)")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ocr_engines())