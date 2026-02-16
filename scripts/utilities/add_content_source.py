#!/usr/bin/env python3
"""
Add Content Source URL to Unified Lessons
Updates all unified lesson JSON files with the content source URL.
"""

import json
from pathlib import Path


def update_content_source():
    """Update all unified lesson files with content source URL."""
    
    # The Google Drive URL for the source PDF
    content_source_url = "https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view"
    
    unified_dir = Path("unified_lessons")
    
    if not unified_dir.exists():
        print(f"ERROR: unified_lessons directory not found")
        return
    
    json_files = sorted([f for f in unified_dir.iterdir() if f.suffix == ".json"])
    
    print(f"Updating {len(json_files)} unified lesson files with content source URL...\n")
    
    updated_count = 0
    
    for json_file in json_files:
        try:
            # Read the file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update content_source
            data['content_source'] = content_source_url
            
            # Write back to file
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            source_pages = data.get('source_pages', 'N/A')
            print(f"[OK] {json_file.name} - Pages: {source_pages}")
            updated_count += 1
            
        except Exception as e:
            print(f"[ERROR] {json_file.name}: {e}")
    
    print(f"\n{'='*80}")
    print(f"Updated {updated_count}/{len(json_files)} files")
    print(f"Content Source URL: {content_source_url}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    update_content_source()
