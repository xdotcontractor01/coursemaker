#!/usr/bin/env python3
"""
Download images for Chapters 5, 6, and 7 from CDN URLs
"""

import json
import requests
from pathlib import Path

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MANIFESTS_DIR = PROJECT_ROOT / "manifests"
ASSETS_DIR = PROJECT_ROOT / "assets/images"

def download_images():
    """Download all images from manifests."""
    print("=" * 60)
    print("Downloading Images for Chapters 5, 6, and 7")
    print("=" * 60)
    
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    for chapter_num in [5, 6, 7]:
        manifest_path = MANIFESTS_DIR / f"chapter{chapter_num:02d}.json"
        if not manifest_path.exists():
            print(f"[WARNING] Manifest not found: {manifest_path}")
            continue
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        images = manifest.get('images', {})
        print(f"\nChapter {chapter_num}: {len(images)} images")
        
        for fig_name, url in images.items():
            # Extract figure number from name (e.g., "figure_5_1" -> "chapter5/figure_5_1")
            parts = fig_name.split('_')
            if len(parts) >= 3:
                chapter_part = f"chapter{parts[1]}"
                fig_part = f"{parts[1]}_{parts[2]}"
                output_path = ASSETS_DIR / chapter_part / f"figure_{fig_part}.jpg"
            else:
                output_path = ASSETS_DIR / f"chapter{chapter_num}" / f"{fig_name}.jpg"
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output_path.exists():
                print(f"  [OK] {output_path.name} exists")
                continue
            
            try:
                print(f"  Downloading {output_path.name}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                size_kb = len(response.content) / 1024
                print(f"  [OK] Downloaded {output_path.name} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"  [ERROR] {output_path.name}: {e}")
    
    print("\n" + "=" * 60)
    print("Image download complete!")
    print("=" * 60)

if __name__ == "__main__":
    download_images()




