#!/usr/bin/env python3
"""
Download images for Chapters 3 and 4 from CDN URLs
"""

import requests
from pathlib import Path

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

IMAGE_URLS = {
    # Chapter 3
    "chapter3/figure_3_1": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/d2f5015ff5d016767e8142ab58273f4eb07a7e90241def8ec723c631d5000ff0.jpg",
    "chapter3/figure_3_2": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/19c7a5d605babe0b6b5b50cc0cb246a03f4c04fcffc1921a77d3facbbe8e94ba.jpg",
    "chapter3/figure_3_3": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/cd36c52ffd8f1f36b66985cd1c5962a6554d4cdb0e552d001e858ef16022559a.jpg",
    # Chapter 4
    "chapter4/figure_4_1": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/4d6c1acad8f6624f1cbd8509f5105ae839a502fa17074fa388a39d3152885598.jpg",
    "chapter4/figure_4_2": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/8319fed7bf31a55061ad5c5f3d5c760ac89f03d3ffa9cafdc00def8291d436b4.jpg",
}

ASSETS_DIR = PROJECT_ROOT / "assets/images"


def download_images():
    """Download all images."""
    print("=" * 60)
    print("Downloading Images for Chapters 3 and 4")
    print("=" * 60)
    
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    for rel_path, url in IMAGE_URLS.items():
        output_path = ASSETS_DIR / f"{rel_path}.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.exists():
            print(f"[OK] {output_path.name} exists")
            continue
        
        try:
            print(f"Downloading {output_path.name}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                f.write(response.content)
            size_kb = len(response.content) / 1024
            print(f"[OK] Downloaded {output_path.name} ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"[ERROR] {output_path.name}: {e}")
    
    print("=" * 60)
    print("Image download complete!")
    print("=" * 60)


if __name__ == "__main__":
    download_images()







