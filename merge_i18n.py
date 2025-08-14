#!/usr/bin/env python3
"""
Script to merge i18n translations from one JSON file into another.
Specifically designed to merge English translations from the-book-which-tells-the-truth.json
into target_all_fr_clean_nosubheads.json while preserving the target structure.
"""

import json
import sys
from pathlib import Path

def load_json(file_path):
    """Load JSON file and return parsed data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)

def save_json(data, file_path):
    """Save data to JSON file with proper formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def merge_i18n_translations(target_data, source_data):
    """
    Merge i18n translations from source into target.

    Args:
        target_data: The target JSON data (with empty i18n fields)
        source_data: The source JSON data (with filled i18n translations)

    Returns:
        Modified target_data with merged translations
    """
    # Create lookup dictionaries for faster access
    source_chapters = {}
    for chapter in source_data.get('chapters', []):
        chapter_n = chapter.get('n')
        if chapter_n:
            source_chapters[chapter_n] = chapter

    # Process each chapter in target
    for target_chapter in target_data.get('chapters', []):
        chapter_n = target_chapter.get('n')

        if chapter_n in source_chapters:
            source_chapter = source_chapters[chapter_n]

            # Create lookup for source paragraphs
            source_paragraphs = {}
            for para in source_chapter.get('paragraphs', []):
                para_n = para.get('n')
                if para_n:
                    source_paragraphs[para_n] = para

            # Merge paragraph i18n translations
            for target_para in target_chapter.get('paragraphs', []):
                para_n = target_para.get('n')

                if para_n in source_paragraphs:
                    source_para = source_paragraphs[para_n]
                    source_i18n = source_para.get('i18n', {})

                    # Merge i18n translations (prioritize English from source)
                    if 'i18n' in target_para:
                        # Only merge English translation if it exists in source
                        if 'en' in source_i18n and source_i18n['en']:
                            target_para['i18n']['en'] = source_i18n['en']

                        # Optionally merge other languages too
                        for lang in ['de', 'es', 'ru', 'ja', 'zh']:
                            if lang in source_i18n and source_i18n[lang]:
                                target_para['i18n'][lang] = source_i18n[lang]

            # Handle chapter title i18n if it exists in target
            if 'i18n' in target_chapter and 'title' in source_chapter:
                # For chapter titles, we might need to manually map or use the title
                # Since source doesn't have i18n for chapter titles, we can't merge them
                pass

    return target_data

def main():
    """Main function to orchestrate the merge process."""
    if len(sys.argv) != 4:
        print("Usage: python merge_i18n.py <target_file> <source_file> <output_file>")
        print("Example: python merge_i18n.py target_all_fr_clean_nosubheads.json the-book-which-tells-the-truth.json merged_output.json")
        sys.exit(1)

    target_file = sys.argv[1]
    source_file = sys.argv[2]
    output_file = sys.argv[3]

    print(f"Loading target file: {target_file}")
    target_data = load_json(target_file)

    print(f"Loading source file: {source_file}")
    source_data = load_json(source_file)

    print("Merging i18n translations...")
    merged_data = merge_i18n_translations(target_data, source_data)

    print(f"Saving merged data to: {output_file}")
    save_json(merged_data, output_file)

    # Print some statistics
    total_chapters = len(merged_data.get('chapters', []))
    total_paragraphs = sum(len(ch.get('paragraphs', [])) for ch in merged_data.get('chapters', []))

    # Count filled English translations
    filled_en_translations = 0
    for chapter in merged_data.get('chapters', []):
        for para in chapter.get('paragraphs', []):
            if para.get('i18n', {}).get('en'):
                filled_en_translations += 1

    print(f"\nMerge completed successfully!")
    print(f"Total chapters: {total_chapters}")
    print(f"Total paragraphs: {total_paragraphs}")
    print(f"Paragraphs with English translations: {filled_en_translations}")
    print(f"Translation coverage: {filled_en_translations/total_paragraphs*100:.1f}%" if total_paragraphs > 0 else "No paragraphs found")

if __name__ == "__main__":
    main()
