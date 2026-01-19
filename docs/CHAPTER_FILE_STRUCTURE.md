# Unified Chapter File Structure Guide

This document defines the standard file structure for creating videos for any chapter. Follow this pattern when starting a new chapter (e.g., Chapter 8).

## Required Files Per Chapter

### 1. Manifest JSON (REQUIRED)
**Location:** `manifests/`
**Naming:** 
- Single video chapters: `chapter08.json`
- Multi-video chapters: `chapter08_video01.json`, `chapter08_video02.json`, etc.

**Format:**
```json
{
  "chapter": 8,
  "video": 1,
  "pages": "XX-YY",
  "title": "Chapter Title Here",
  "topics": [
    "Topic 1",
    "Topic 2"
  ],
  "scenes": [
    {
      "index": 1,
      "title": "Scene Title",
      "source_pages": "XX",
      "source_text": "Quote from source material",
      "image_paths": ["assets/images/chapter8/figure_8_1.jpg"],
      "bullets": [
        "Bullet point 1 (max 10 words)",
        "Bullet point 2",
        "Bullet point 3"
      ],
      "narration_text": "Full narration script for this scene...",
      "tts_file": "audio/ch08_scene01.wav",
      "duration": null
    }
  ],
  "images": {
    "figure_8_1": "https://cdn-url.../image.jpg"
  },
  "total_duration": null
}
```

### 2. Audio Files (GENERATED)
**Location:** `audio/`
**Naming:** `ch08_scene01.wav`, `ch08_scene02.wav`, etc.
**For multi-video:** `ch08_v01_scene01.wav`, `ch08_v01_scene02.wav`, etc.

### 3. Manim Script (REQUIRED)
**Location:** `manim_scripts/`
**Naming:** `chapter08.py` or `chapter08/video01.py`

### 4. Image Assets (IF NEEDED)
**Location:** `assets/images/chapter8/`
**Naming:** `figure_8_1.jpg`, `figure_8_2.jpg`, etc.

### 5. Sanitization Map (OPTIONAL - for chapters 5+)
**Location:** `manifests/`
**Naming:** `sanitization_map_chapter08.json`

---

## Current Chapter Overview

| Chapter | Pages | Videos | Manifest Files |
|---------|-------|--------|----------------|
| 1 | 1-11 | 4 | `chapter01_video01.json` through `chapter01_video04.json` |
| 2 | 11-12 | 1 | `chapter_02.json` |
| 3 | 13-14 | 1 | `chapter_03.json` |
| 4 | 15-17 | 1 | `chapter_04.json` |
| 5 | 19-21 | 1 | `chapter05.json` |
| 6 | 23-36 | 2 | `chapter06.json` (contains 2 lessons) |
| 7 | 37-50 | 3 | `chapter07.json` (contains 3 lessons) |

---

## Scripts Workflow

When creating a new chapter, run these scripts in order:

### Step 1: Content Extraction
```bash
python scripts/extraction/extract_chapters_XXX.py
```
Creates: `manifests/chapterXX.json`

### Step 2: Download Images (if needed)
```bash
python scripts/image_download/download_chapters_XXX_images.py
```
Creates: `assets/images/chapterXX/*.jpg`

### Step 3: Generate Audio
```bash
python scripts/audio_generation/generate_chapters_XXX_audio.py
```
Creates: `audio/chXX_sceneYY.wav`

### Step 4: Verify Setup (Dry Run)
```bash
python scripts/utilities/dryrun_chapters_XXX.py
```
Creates: `logs/chapterXX_dryrun.log`

### Step 5: Render Video
```bash
python scripts/rendering/render_chapters_XXX.py
```
Creates: `outputs/chapterXX_final.mp4`

---

## Directory Structure Summary

```
coursemaker/
├── manifests/           # JSON manifest files (scene definitions, narration)
├── audio/               # Generated WAV files
├── assets/images/       # Downloaded/prepared images
├── outputs/             # Final rendered MP4 videos
├── manim_scripts/       # Manim Python scripts
├── scripts/
│   ├── extraction/      # Content extraction from markdown/PDF
│   ├── audio_generation/# TTS audio generation
│   ├── image_download/  # Image downloading
│   ├── rendering/       # Video render orchestration
│   └── utilities/       # Verification and utility scripts
├── logs/                # Dry-run and debug logs
└── narration/           # Legacy narration Python files (reference only)
```

---

## Key Rules

1. **Manifest is the source of truth** - All narration, scene info, and audio paths live here
2. **Audio files per scene** - Never merge audio; one WAV per scene
3. **Audio-driven timing** - Manim scenes wait for `duration + 0.12s` buffer
4. **Consistent naming** - Use zero-padded numbers: `scene01`, not `scene1`
5. **Relative paths** - All paths in manifests relative to project root
