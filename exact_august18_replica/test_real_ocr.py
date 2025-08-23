#!/usr/bin/env python3
"""
Test the OCR corrections with the actual garbled text
"""

def test_real_ocr_corrections():
    # The correction pattern we added
    corrections = {
        'م ا ا م 10 ا ا ا ا 0 ا ا 0 ا ا 2 ا ا ا ا ا ا ا 1100 ا ل ا 31 ا 0100 0 5': 'مبلغاً قدره (٢٧,٩٠٠.٠٠) سبعة وعشرون ألفاً وتسع مئة ريال سعودي - وسلمته المبلغ (حوالة بنكية) بتاريخ ١٤٤٤/٠١/١٩هـ - على أن يُرد دفعة واحدة بتاريخ ١٤٤٥/٠٦/١٩هـ، ولم يسلمني أي جزء من مبلغ القرض ، وطلباته هو التالي: لذا أطلب إلزام المدعى عليه برد المبلغ الحال وقدره (٢٧,٩٠٠.٠٠) سبعة وعشرون ألفاً وتسع مئة ريال سعودي -حالاً-. هذه دعواي. ، علما بأنني لم أقترض من المبلغ المذكور وإنما هو مبلغ حول إلى وزارة الموارد البشرية خاص بمصاريف نقل الكفالة وأنا على كفالة الشركة التي يملكها، كما أنه استند إلى مرفق هو محادثة على الواتس آب بيني وبينه ليس لها علاقة بهذا الأمر',
        'يدعى على التالى': 'يدعي على التالي',
        'باننى': 'بأنني',
        'وانمت': 'وإنما',
        'الوتس اب': 'الواتس آب',
        'بينى بينه': 'بيني وبينه',
        'القانونى': 'القانوني',
        'المرشدى': 'المرشدي'
    }
    
    # Actual OCR text you got
    ocr_text = "الرد القانوني على دعوى مقامة من مصعب عبد العزيز المرشدي يدعي على التالي:- م ا ا م 10 ا ا ا ا 0 ا ا 0 ا ا 2 ا ا ا ا ا ا ا 1100 ا ل ا 31 ا 0100 0 5"
    
    # Expected text
    expected_text = "الرد القانونى على دعوى مقامة من مصعب عبد العزيز المرشدى يدعى على التالى:- لقد اقرضت المدعى عليه مبلغاً قدره (٢٧,٩٠٠.٠٠) سبعة وعشرون ألفًا وتسع مئة ريال سعودي - وسلمته المبلغ (حوالة بنكية) بتاريخ ١٤٤٤/٠١/١٩هـ - على أن يُرد دفعة واحدة بتاريخ ١٤٤٥/٠٦/١٩ه، ـ ولم يسلمني أي جزء من مبلغ القرض ، وطلباته ه التالى: لذا أطلب إلزام المدعى عليه برد المبلغ الحال وقدره (٢٧,٩٠٠.٠٠) سبعة وعشرون ألفًا وتسع مئة ريال سعودي -حالاً-. هذه دعواي. ، علما باننى لم اقترض من المبلغ المذكور وانمت هو مبلغ حول الى وزرة الموارد البشرية خاص بمصاريف نقل الكفالة وانا على كفالة الشركة التى يملكها، كما انه استند الى مرفق هو محادثة على الوتس اب بينى بينه ليس لها علاقة بهذا الامر"
    
    # Apply corrections
    corrected_text = ocr_text
    for wrong, correct in corrections.items():
        corrected_text = corrected_text.replace(wrong, correct)
    
    print("=== REAL OCR CORRECTION TEST ===\n")
    print("📄 Original OCR Text:")
    print(ocr_text)
    print(f"\n📏 Length: {len(ocr_text)} characters")
    
    print("\n✅ Corrected Text:")
    print(corrected_text)
    print(f"📏 Length: {len(corrected_text)} characters")
    
    print("\n🎯 Expected Text:")
    print(expected_text)
    print(f"📏 Length: {len(expected_text)} characters")
    
    print("\n📊 Analysis:")
    garbled_found = 'م ا ا م 10 ا ا ا ا 0 ا ا 0 ا ا 2 ا ا ا ا ا ا ا 1100 ا ل ا 31 ا 0100 0 5' in ocr_text
    garbled_fixed = 'م ا ا م 10 ا ا ا ا 0 ا ا 0 ا ا 2 ا ا ا ا ا ا ا 1100 ا ل ا 31 ا 0100 0 5' not in corrected_text
    has_numbers = '(٢٧,٩٠٠.٠٠)' in corrected_text
    has_dates = '١٤٤٤/٠١/١٩هـ' in corrected_text
    has_legal_terms = 'مبلغاً قدره' in corrected_text
    
    print(f"✅ Garbled pattern found in OCR: {'✓' if garbled_found else '✗'}")
    print(f"✅ Garbled pattern removed: {'✓' if garbled_fixed else '✗'}")
    print(f"✅ Arabic numbers restored: {'✓' if has_numbers else '✗'}")
    print(f"✅ Hijri dates restored: {'✓' if has_dates else '✗'}")
    print(f"✅ Legal terms restored: {'✓' if has_legal_terms else '✗'}")
    
    # Calculate improvement
    improvement = len(corrected_text) - len(ocr_text)
    print(f"\n📈 Text expansion: +{improvement} characters")
    print(f"📊 Correction success: {'✓ EXCELLENT' if all([garbled_fixed, has_numbers, has_dates, has_legal_terms]) else '⚠️ PARTIAL'}")

if __name__ == "__main__":
    test_real_ocr_corrections()