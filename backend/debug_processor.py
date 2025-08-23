#!/usr/bin/env python3
"""
Debug the Al-Qurtubi processor to see why no legal content is being found
"""

import sys
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

import asyncio
from datasets import load_dataset
from app.processors.qurtubi_processor import SemanticLegalAnalyzer

async def debug_analyzer():
    print("🔍 Loading Al-Qurtubi dataset...")
    
    try:
        dataset = load_dataset("MohamedRashad/Quran-Tafseer")
        target_tafsir = "* تفسير الجامع لاحكام القرآن/ القرطبي (ت 671 هـ)"
        
        # Get Al-Qurtubi entries
        qurtubi_entries = [row for row in dataset['train'] if row.get('tafsir_book') == target_tafsir]
        print(f"✅ Found {len(qurtubi_entries)} Al-Qurtubi entries")
        
        # Initialize analyzer
        analyzer = SemanticLegalAnalyzer()
        
        # Test first 10 entries
        print("\n🔍 Testing legal content analysis on sample entries:")
        
        for i, entry in enumerate(qurtubi_entries[:10]):
            surah = entry.get('surah_name', '')
            ayah = entry.get('ayah', '')
            content = entry.get('tafsir_content', '')
            
            print(f"\n--- Entry {i+1} ---")
            print(f"Surah: {surah}")
            print(f"Ayah: {ayah}")
            print(f"Content length: {len(content)} characters")
            print(f"Content preview: {content[:200]}...")
            
            # Analyze content
            context = {"surah": surah, "ayah": ayah}
            analysis = await analyzer.analyze_content(content, context)
            
            print(f"Is legal: {analysis['is_legal_content']}")
            print(f"Legal relevance: {analysis['legal_relevance_score']:.3f}")
            print(f"Scholarship confidence: {analysis['scholarship_confidence']:.3f}")
            print(f"Applicable domains: {analysis['applicable_domains']}")
            print(f"Semantic concepts: {analysis['semantic_concepts']}")
            
            if analysis['is_legal_content']:
                print(f"✅ LEGAL CONTENT FOUND!")
                print(f"Legal principle: {analysis['legal_principle']}")
                print(f"Principle category: {analysis['principle_category']}")
                break
        
        # Look for specifically legal-related content
        print("\n🔍 Searching for entries with explicit legal terms...")
        
        legal_terms = ["أحكام", "حكم", "فقه", "شريعة", "قضاء", "حلال", "حرام", "عقد", "ميراث", "زواج"]
        legal_entries_found = 0
        
        for i, entry in enumerate(qurtubi_entries):
            content = entry.get('tafsir_content', '').lower()
            if any(term in content for term in legal_terms):
                legal_entries_found += 1
                if legal_entries_found <= 3:  # Show first 3
                    print(f"\nFound legal entry {legal_entries_found}:")
                    print(f"Surah: {entry.get('surah_name', '')}")
                    print(f"Content preview: {entry.get('tafsir_content', '')[:300]}...")
                    
                    # Test this entry
                    context = {"surah": entry.get('surah_name', ''), "ayah": entry.get('ayah', '')}
                    analysis = await analyzer.analyze_content(entry.get('tafsir_content', ''), context)
                    print(f"Analysis result - Legal: {analysis['is_legal_content']}, Score: {analysis['legal_relevance_score']:.3f}")
        
        print(f"\n📊 Total entries with legal terms: {legal_entries_found} out of {len(qurtubi_entries)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_analyzer())