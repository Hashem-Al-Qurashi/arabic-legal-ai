#!/usr/bin/env python3
"""
Quick script to inspect the HuggingFace dataset and understand its structure
"""

import sys
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

from datasets import load_dataset
import json

def inspect_dataset():
    print("🔍 Loading HuggingFace Quran-Tafseer dataset...")
    
    try:
        dataset = load_dataset("MohamedRashad/Quran-Tafseer")
        print(f"✅ Dataset loaded successfully")
        print(f"📊 Total entries: {len(dataset['train'])}")
        
        # Check the first few entries
        print("\n📋 Sample entries:")
        for i, row in enumerate(dataset['train']):
            if i >= 5:
                break
            print(f"\nEntry {i+1}:")
            print(f"  Tafsir book: {row.get('tafsir_book', 'N/A')}")
            print(f"  Surah: {row.get('surah_name', 'N/A')}")
            print(f"  Ayah: {row.get('ayah', 'N/A')}")
            if 'tafsir_content' in row:
                content = row['tafsir_content'][:200] + "..." if len(row['tafsir_content']) > 200 else row['tafsir_content']
                print(f"  Content preview: {content}")
            print(f"  All keys: {list(row.keys())}")
        
        # Check available tafsir books
        print("\n📚 Available Tafsir Books:")
        tafsir_books = set()
        qurtubi_count = 0
        for row in dataset['train']:
            book = row.get('tafsir_book', '')
            tafsir_books.add(book)
            if 'قرطبي' in book or 'القرطبي' in book:
                qurtubi_count += 1
        
        for book in sorted(tafsir_books):
            print(f"  - {book}")
        
        print(f"\n🕌 Al-Qurtubi entries found: {qurtubi_count}")
        
        # Find the exact Al-Qurtubi book name
        target_name = "* تفسير الجامع لاحكام القرآن/ القرطبي (ت 671 هـ)"
        exact_match_count = sum(1 for row in dataset['train'] if row.get('tafsir_book') == target_name)
        print(f"📖 Exact target match count: {exact_match_count}")
        
        # Show some Al-Qurtubi samples
        print(f"\n🔍 Al-Qurtubi samples:")
        qurtubi_samples = 0
        for row in dataset['train']:
            if row.get('tafsir_book') == target_name and qurtubi_samples < 3:
                qurtubi_samples += 1
                print(f"\nSample {qurtubi_samples}:")
                print(f"  Surah: {row.get('surah_name', 'N/A')}")
                print(f"  Ayah: {row.get('ayah', 'N/A')}")
                content = row.get('tafsir_content', '')[:300] + "..." if len(row.get('tafsir_content', '')) > 300 else row.get('tafsir_content', '')
                print(f"  Content: {content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_dataset()