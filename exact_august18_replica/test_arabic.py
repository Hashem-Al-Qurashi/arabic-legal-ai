#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Arabic display in terminal
"""

print("Testing Arabic Display")
print("=" * 30)

# Test basic Arabic
print("Basic Arabic: سورة البقرة")
print("With numbers: سورة البقرة:282")
print("Long text: هذا نص طويل باللغة العربية للاختبار")

# Test Quranic verses
verses = [
    "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
    "يَا أَيُّهَا الَّذِينَ آمَنُوا أَوْفُوا بِالْعُقُودِ"
]

print("\nQuranic Verses:")
for i, verse in enumerate(verses, 1):
    print(f"{i}. {verse}")

print("\nIf Arabic appears correctly, your terminal is fixed!")
print("If it appears backwards/broken, try the font fixes above.")