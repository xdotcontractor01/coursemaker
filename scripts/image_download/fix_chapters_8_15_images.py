#!/usr/bin/env python3
"""
Fix missing images for Chapters 8-15.
Downloads images from working CDN URLs and updates manifests.
"""

import json
import os
import re
import requests
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
MANIFESTS_DIR = BASE_DIR / "manifests"
ASSETS_DIR = BASE_DIR / "assets" / "images"
NEW_MARKDOWN_PATH = BASE_DIR / "docs" / "MinerU_markdown_BasicHiwyPlanReading (1)_20260129005532_2016555753310150656.md"

# New working CDN base (2026-01-29 version)
NEW_CDN_BASE = "https://cdn-mineru.openxlab.org.cn/result/2026-01-29/ab7840c2-b7e0-464f-8396-e5c901b3b527/"

# Figure to hash mapping extracted from new markdown
FIGURE_HASHES = {
    # Chapter 8 figures
    "figure_8_1": None,  # This is a table, not an image
    "figure_8_2_a": "d083422ce8d40cfb92974e877e81b8e1176fa088da11eca50131c560b7a3681d.jpg",
    "figure_8_2_b": "a0fdb682afd55827921ad7be10eebdbf17d36f26c012b4d6c98da21bbe639c13.jpg",
    "figure_8_2_c": "e7fe9bea251c0d4497af47d043a95ebcd108466e24fab725e9bc288159b42279.jpg",
    "figure_8_2_d": "9b7968cc0086e32149c699fc5e453c5d622c913c57466573ab0c2376cfa2392f.jpg",
    "figure_8_3_a": "6a00f730f05ac6c3fa4dd2c6fe0f61b8e14768cdb81587b1398b8dd9089ea99e.jpg",
    "figure_8_3_b": "a078bf69ac0635393a7978410fc19ada2766cac2af83512cf40781a7260331e7.jpg",
    "figure_8_4": "35a2f854ce849325a7b0d6fa8772f0e172cbb4cc375db53bfa8be6320ab0c123.jpg",
    "figure_8_5": "6f05ee6bb5d5115855c1e01ce294f3ea1da9890f31a22ebb97f758febb8c1556.jpg",
    "figure_8_6": "88208580c2906a67eec5f46fc0d7630ed1e0cc5e0e0c21fa0411eb9e227eb4d3.jpg",
    "figure_8_7": "e1005b57f7c54b6d8661f50fe55ab9198faca26600d0072e4c894dfea73eedb1.jpg",
    "figure_8_8": "90c150059d516e1d0073b2069664873e1b99c5cd8936c2c661951dbcaf909884.jpg",
    "figure_8_9": "f5fd468448959b3bab4650b52c07e5f03aaa146afead73447a3160daf44018b5.jpg",
    "figure_8_11_a": "d20c6ca476e1919ec7075c616d4c3a22a097c91c57b01eea2698cab7fb43f2f7.jpg",
    "figure_8_11_b": "9301104cdc9401f9ccc48b137e8394dc128b8e4f82ea8a775ae646ab4e59d528.jpg",
    "figure_8_12": "f0c755ea48e057c8cd6ccc83f1dbf20eeaecdfb89c0de23a9dd89e126614e052.jpg",
    "figure_8_13": "5f0bc865a4c50d0a2bbe3b7d8c4f578e571f17709691a41a7ec5107c8418b46e.jpg",
    # Figure 8-14 not clearly available in the markdown
    
    # Chapter 12 figures
    "figure_12_1": "9ec25266da8ac3fbe34df8fef2f794392cc50ddb484d274e47539d5e8d9381a5.jpg",
    "figure_12_2": "a0fd1a3827f9255319af2d8a3f443dad97ed5f83eda2189c499642c20e2d28c8.jpg",
    
    # Chapter 13 figures
    "figure_13_1": "852e96733fdf325eb4b6943b315d92033028130c0500155133bfffa2af1add63.jpg",
    "figure_13_2": "312ac2236c505eee59b847d1b2c1a30e892cd0808bd82e1bc4a5035548952ce5.jpg",
    "figure_13_3": "a9052e717436eed508312b1b4c3befb328664fb948bb1b4ba9fcddca2e92bddc.jpg",
    "figure_13_4": "92e81ce0cbdbd77511780d2db10ba47ae565b32788568f3874ef01110fa9e2a4.jpg",
    "figure_13_5": "6469bba3d96229502ca95c420bb3e3f98ae644242a6d0f6b50ed8a64eb9cfdd3.jpg",
    "figure_13_6": "8572d4f6bb2099bdc70c90d6b4f822d5f073bb9838843a8730e179c344fc4d54.jpg",
    "figure_13_7": "cd00551920c41de5e77b0ce2f753e6718eda5a7bbe6b07502e95bb05f8b63f07.jpg",
    "figure_13_8": "0e404dee5ba2f2ac17c5720687f1dbc6b3289bc126d27d5425d16382f2416240.jpg",
    "figure_13_9_a": "5e85e589ab092a2e87b11120118ac0f6ed9be81ca28cc615cff80117e5972495.jpg",
    "figure_13_9_b": "96dedf4ea4d0d23ba41a9494e06a1380a404298b8f35e8a331c0113683cdfdef.jpg",
    "figure_13_10": "9a92cb5da86696f744127064bd530b6c5328f2199093940829810dcb1b27f7e2.jpg",
    "figure_13_11": "8cefae52eab9fde386c0c377504681b2d22b3ce5f85bab08fa0a83102d3d9e3c.jpg",
    
    # Chapter 14 figures
    "figure_14_1": "c2299c8a2fe8c8e90276d6cfa764b142f7a829c8ba60415336a0444b74fbd788.jpg",
    
    # Chapter 15 figures
    "figure_15_1": "e4eeec6f8f8d79edfc2a02f509a71720e22c2ec3a66b5dcd427e0f49b20840bb.jpg",
    "figure_15_2": "4ce0e9a934ed511d3fe674e72b1fb59827f3b7a0b0f3db20fdc7c2496f3286cf.jpg",
    "figure_15_3": "ba26335880d2f070f7a052c6228c4ae8473b8f93c330e09ea02966f8abd3981c.jpg",
    "figure_15_4": "1ec335c865b80f76863fbdb5d4098014779abebbd82954e3751b22184df2bf41.jpg",
}

# Map scene image paths to correct figure names (based on manifest content analysis)
SCENE_TO_FIGURES = {
    # Chapter 8
    ("chapter08", 2): ["figure_8_2_c"],  # Box culvert parts - use combined image
    ("chapter08", 4): ["figure_8_2_c", "figure_8_3_b"],  # Box culvert parts
    ("chapter08", 5): ["figure_8_4"],  # Longitudinal section
    ("chapter08", 6): ["figure_8_5", "figure_8_6"],  # Plan view and skew
    ("chapter08", 7): ["figure_8_7", "figure_8_8", "figure_8_9"],  # Wing walls
    ("chapter08", 8): ["figure_8_11_b"],  # Bridge structure (elevation)
    ("chapter08", 9): ["figure_8_12"],  # Bridge bents
    ("chapter08", 10): ["figure_8_13"],  # Utility accommodations
    
    # Chapter 12
    ("chapter12", 2): ["figure_12_1"],  # ESPCP
    ("chapter12", 3): ["figure_12_2"],  # BMP plan
    
    # Chapter 13
    ("chapter13", 3): ["figure_13_1", "figure_13_2"],  # Earthwork
    ("chapter13", 4): ["figure_13_3", "figure_13_4", "figure_13_6"],  # Typical sections
    ("chapter13", 6): ["figure_13_7", "figure_13_8"],  # Slopes
    ("chapter13", 7): ["figure_13_10", "figure_13_11"],  # Slope stakes - use 13-10 and 13-11
    
    # Chapter 14
    ("chapter14", 3): ["figure_14_1"],  # Intersection details
    
    # Chapter 15
    ("chapter15", 4): ["figure_15_1"],  # ROW plan sheets
    ("chapter15", 5): ["figure_15_2", "figure_15_3"],  # Conventional symbols
    ("chapter15", 6): ["figure_15_4"],  # Property information
}


def download_image(figure_key: str, chapter_dir: Path) -> str | None:
    """Download an image from CDN and save locally."""
    hash_name = FIGURE_HASHES.get(figure_key)
    if not hash_name:
        print(f"  [SKIP] No hash for {figure_key}")
        return None
    
    url = NEW_CDN_BASE + hash_name
    # Normalize figure key to standard format
    local_name = figure_key.replace("_a", "").replace("_b", "").replace("_c", "").replace("_d", "") + ".jpg"
    if "_a" in figure_key or "_b" in figure_key:
        local_name = figure_key + ".jpg"
    
    local_path = chapter_dir / local_name
    
    if local_path.exists():
        print(f"  [EXISTS] {local_path.name}")
        return str(local_path)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        chapter_dir.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(response.content)
        
        print(f"  [OK] Downloaded {local_path.name} ({len(response.content)} bytes)")
        return str(local_path)
    except Exception as e:
        print(f"  [FAIL] {figure_key}: {e}")
        return None


def scan_manifests():
    """Scan all manifests for chapters 8-15 and identify missing images."""
    report = []
    
    for ch_num in range(8, 16):
        manifest_path = MANIFESTS_DIR / f"chapter{ch_num:02d}.json"
        if not manifest_path.exists():
            print(f"[WARN] Manifest not found: {manifest_path}")
            continue
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        chapter_key = f"chapter{ch_num:02d}"
        chapter_img_dir = ASSETS_DIR / chapter_key
        
        for scene in manifest.get("scenes", []):
            scene_idx = scene.get("index", 0)
            image_paths = scene.get("image_paths", [])
            narration = scene.get("narration_text", "")[:80]
            source_pages = scene.get("source_pages", "")
            
            # Check if this scene should have images
            expected_figures = SCENE_TO_FIGURES.get((chapter_key, scene_idx), [])
            
            missing_images = []
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    missing_images.append(img_path)
            
            # Also check if scene has empty image_paths but should have images
            if not image_paths and expected_figures:
                missing_images.append("(no images defined)")
            
            if missing_images or expected_figures:
                report.append({
                    "chapter": ch_num,
                    "lesson": get_lesson_for_scene(manifest, scene_idx),
                    "scene_index": scene_idx,
                    "current_image_paths": image_paths,
                    "missing_images": missing_images,
                    "expected_figures": expected_figures,
                    "narration_excerpt": narration,
                    "source_pages": source_pages
                })
    
    return report


def get_lesson_for_scene(manifest, scene_idx):
    """Get lesson number for a scene index."""
    boundaries = manifest.get("lesson_boundaries", {})
    for lesson_key, lesson_data in boundaries.items():
        if scene_idx in lesson_data.get("scenes", []):
            return int(lesson_key.replace("lesson_", ""))
    return 1


def fix_images_for_chapters():
    """Download missing images and update manifests."""
    print("=" * 60)
    print("STEP 1: Scanning manifests for unresolved figures")
    print("=" * 60)
    
    report = scan_manifests()
    
    print("\n--- UNRESOLVED FIGURES REPORT ---\n")
    affected_lessons = set()
    
    for item in report:
        ch = item["chapter"]
        lesson = item["lesson"]
        scene_idx = item["scene_index"]
        expected = item["expected_figures"]
        
        if expected:
            print(f"Chapter {ch}, Lesson {lesson}, Scene {scene_idx}:")
            print(f"  Current paths: {item['current_image_paths']}")
            print(f"  Expected figures: {expected}")
            print(f"  Source pages: {item['source_pages']}")
            print(f"  Narration: {item['narration_excerpt']}...")
            affected_lessons.add((ch, lesson))
            print()
    
    print("=" * 60)
    print("STEP 2: Downloading images from new CDN URLs")
    print("=" * 60)
    
    downloaded_files = {}
    
    for ch_num in range(8, 16):
        chapter_key = f"chapter{ch_num:02d}"
        chapter_dir = ASSETS_DIR / chapter_key
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all figures needed for this chapter
        chapter_figures = set()
        for (ch_key, scene_idx), figures in SCENE_TO_FIGURES.items():
            if ch_key == chapter_key:
                chapter_figures.update(figures)
        
        if chapter_figures:
            print(f"\n[Chapter {ch_num}] Downloading {len(chapter_figures)} figures...")
            for fig_key in chapter_figures:
                result = download_image(fig_key, chapter_dir)
                if result:
                    downloaded_files[(chapter_key, fig_key)] = result
    
    print("\n" + "=" * 60)
    print("STEP 3: Updating manifests with correct image paths")
    print("=" * 60)
    
    for ch_num in range(8, 16):
        manifest_path = MANIFESTS_DIR / f"chapter{ch_num:02d}.json"
        if not manifest_path.exists():
            continue
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        chapter_key = f"chapter{ch_num:02d}"
        modified = False
        
        for scene in manifest.get("scenes", []):
            scene_idx = scene.get("index", 0)
            expected_figures = SCENE_TO_FIGURES.get((chapter_key, scene_idx), [])
            
            if expected_figures:
                new_paths = []
                for fig_key in expected_figures:
                    # Build correct path
                    local_name = fig_key + ".jpg"
                    local_path = f"assets/images/{chapter_key}/{local_name}"
                    new_paths.append(local_path)
                
                if new_paths != scene.get("image_paths", []):
                    print(f"  [UPDATE] Ch{ch_num} Scene {scene_idx}: {new_paths}")
                    scene["image_paths"] = new_paths
                    modified = True
        
        if modified:
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            print(f"  [SAVED] {manifest_path.name}")
    
    print("\n" + "=" * 60)
    print("STEP 4: Summary of affected lessons requiring re-render")
    print("=" * 60)
    
    for ch, lesson in sorted(affected_lessons):
        print(f"  - Chapter {ch:02d}, Lesson {lesson:02d}")
    
    return sorted(affected_lessons)


if __name__ == "__main__":
    affected = fix_images_for_chapters()
    
    # Save affected lessons for re-render script
    with open(BASE_DIR / "data" / "affected_lessons.json", "w") as f:
        json.dump([{"chapter": ch, "lesson": lesson} for ch, lesson in affected], f, indent=2)
    
    print(f"\n[DONE] Affected lessons saved to data/affected_lessons.json")
    print(f"       Total: {len(affected)} lessons need re-rendering")
