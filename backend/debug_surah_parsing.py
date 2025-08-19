#!/usr/bin/env python3

import sys
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

from app.core.quran_verse_validator import get_verse_validator

validator = get_verse_validator()

test_input = "سُورَةُ البَقَرَةِ:الۤـمۤ"
print(f"Testing: '{test_input}'")

# Debug step by step
parsed = validator._parse_reference(test_input)
print(f"Parsed: {parsed}")

if parsed:
    surah_part, verse_part = parsed
    print(f"Surah part: '{surah_part}'")
    print(f"Verse part: '{verse_part}'")
    
    # Check if verse part is descriptive
    print(f"Is verse part descriptive? {verse_part in validator.descriptive_references}")
    print(f"Descriptive references: {validator.descriptive_references}")
    
    # Check surah normalization
    normalized = validator._normalize_surah_name(surah_part)
    print(f"Normalized surah: '{normalized}'")
    
    # Check available surahs
    print(f"Available surahs containing 'بقر': {[s for s in validator.verse_limits.keys() if 'بقر' in s]}")

# Test the full validation
result = validator.validate_verse_reference(test_input)
print(f"Final result: {result}")