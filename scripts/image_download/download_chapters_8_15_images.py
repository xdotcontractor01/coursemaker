#!/usr/bin/env python3
"""
Download images for Chapters 8-15 from CDN URLs
Updates manifests with local image paths
"""

import json
import os
import re
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    HAS_REQUESTS = False

# Get project root
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MANIFESTS_DIR = PROJECT_ROOT / "manifests"
ASSETS_DIR = PROJECT_ROOT / "assets/images"
MARKDOWN_FILE = PROJECT_ROOT / "docs/MinerU_markdown_BasicHiwyPlanReading (1)_20260129005532_2016555753310150656.md"

def read_markdown():
    """Read the markdown file."""
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def extract_all_figure_urls(markdown: str) -> dict:
    """Extract all figure URLs from markdown with their figure numbers."""
    figure_urls = {}
    
    # Pattern: ![](url) followed by Figure X-Y
    # Look for any pattern of image URL followed by figure reference
    patterns = [
        r'!\[\]\(([^)]+)\)\s*\n*(?:Figure\s+)?(\d+)-(\d+)',
        r'!\[\]\(([^)]+)\)\s*\n*Figure\s+(\d+)-(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, markdown, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            url = match.group(1)
            chapter = int(match.group(2))
            figure_num = int(match.group(3))
            key = f"figure_{chapter}_{figure_num}"
            if key not in figure_urls and chapter >= 8 and chapter <= 15:
                figure_urls[key] = {
                    "url": url,
                    "chapter": chapter,
                    "figure_num": figure_num
                }
    
    return figure_urls

def download_image(url: str, save_path: Path) -> bool:
    """Download an image from URL to local path."""
    try:
        # Create directory if needed
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://cdn-mineru.openxlab.org.cn/'
        }
        
        if HAS_REQUESTS:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                f.write(response.content)
        else:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                with open(save_path, 'wb') as f:
                    f.write(response.read())
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("Downloading Images for Chapters 8-15")
    print("=" * 60)
    
    # Read markdown and extract all figure URLs
    print("\n[1] Scanning markdown for figure URLs...")
    markdown = read_markdown()
    figure_urls = extract_all_figure_urls(markdown)
    print(f"    Found {len(figure_urls)} figures for chapters 8-15")
    
    # Group by chapter
    chapters_to_process = {}
    for key, info in figure_urls.items():
        chapter = info['chapter']
        if chapter not in chapters_to_process:
            chapters_to_process[chapter] = []
        chapters_to_process[chapter].append(info)
    
    # Download images
    print("\n[2] Downloading images...")
    downloaded_count = 0
    failed_count = 0
    
    for chapter in sorted(chapters_to_process.keys()):
        figures = chapters_to_process[chapter]
        chapter_dir = ASSETS_DIR / f"chapter{chapter:02d}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n  Chapter {chapter}: {len(figures)} figures")
        
        for fig_info in figures:
            url = fig_info['url']
            fig_num = fig_info['figure_num']
            
            # Determine file extension from URL
            ext = ".jpg"
            if ".png" in url.lower():
                ext = ".png"
            
            filename = f"figure_{chapter}_{fig_num}{ext}"
            save_path = chapter_dir / filename
            
            if save_path.exists():
                print(f"    [SKIP] {filename} (already exists)")
                downloaded_count += 1
            else:
                print(f"    [DOWN] {filename}...", end=" ")
                if download_image(url, save_path):
                    print("OK")
                    downloaded_count += 1
                else:
                    print("FAILED")
                    failed_count += 1
    
    # Update manifests with local paths
    print("\n[3] Updating manifests with local paths...")
    
    for chapter in range(8, 16):
        manifest_path = MANIFESTS_DIR / f"chapter{chapter:02d}.json"
        if not manifest_path.exists():
            continue
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Update image paths in scenes
        updated = False
        for scene in manifest.get('scenes', []):
            new_image_paths = []
            for img_path in scene.get('image_paths', []):
                # Convert to local path format
                if img_path.startswith('assets/images/'):
                    # Extract figure reference
                    match = re.search(r'figure_(\d+)_(\d+)', img_path)
                    if match:
                        fig_chapter = int(match.group(1))
                        fig_num = int(match.group(2))
                        local_path = f"assets/images/chapter{fig_chapter:02d}/figure_{fig_chapter}_{fig_num}.jpg"
                        new_image_paths.append(local_path)
                        updated = True
                    else:
                        new_image_paths.append(img_path)
                else:
                    new_image_paths.append(img_path)
            scene['image_paths'] = new_image_paths
        
        # Update images dict with local paths
        if 'images' in manifest:
            new_images = {}
            for key, url in manifest['images'].items():
                match = re.search(r'figure_(\d+)_(\d+)', key)
                if match:
                    fig_chapter = int(match.group(1))
                    fig_num = int(match.group(2))
                    local_path = f"assets/images/chapter{fig_chapter:02d}/figure_{fig_chapter}_{fig_num}.jpg"
                    new_images[key] = {
                        "cdn_url": url,
                        "local_path": local_path
                    }
                else:
                    new_images[key] = url
            manifest['images'] = new_images
            updated = True
        
        if updated:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            print(f"    Updated: {manifest_path.name}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"DOWNLOAD COMPLETE")
    print(f"  Downloaded: {downloaded_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
