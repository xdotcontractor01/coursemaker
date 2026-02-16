# Course Video Generation Workflow Documentation

## Overview

This workflow converts educational markdown content into animated Manim videos with narration. It runs through 11 sequential steps, each building on the previous step's output.

```
INPUT.md → [11 Steps] → final_video_with_audio.mp4
```

---

## Architecture Diagram

```
┌─────────────────┐
│    INPUT.md     │  ← Your educational content (markdown)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Step 0: Load   │  → system_prompt.txt
│  System Prompts │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 1: Validate│  → test_output/input.md (validated copy)
│     Input       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 2: Generate│  → summary.txt (100-word summary)
│    Summary      │     Uses: OpenAI GPT-4o-mini
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 3: Generate│  → base_script.py (Manim Python code)
│  Manim Script   │  → timings.json (slide durations)
│                 │     Uses: OpenAI GPT-4o-mini
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 4: Suggest │  → images.json (image search queries)
│     Images      │     Uses: OpenAI GPT-4o-mini
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 5: Download│  → images/*.jpg|png (downloaded images)
│     Images      │  → downloaded_images.json
│                 │     Uses: SerpAPI Google Images
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 6: Inject  │  → render_script.py (script with images)
│     Images      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 7: Render  │  → media/videos/.../Chapter1.mp4 (silent)
│   Silent Video  │  → video_path.txt
│                 │     Uses: Manim (manim CLI)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 8: Generate│  → narration.json (text for each slide)
│   Narration     │     Uses: OpenAI GPT-4o-mini
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 9: Generate│  → audio_clips/*.mp3 (audio files)
│   Audio Clips   │  → audio_clips.json
│                 │     Uses: edge-tts (online) OR pyttsx3 (offline)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 10: Merge  │  → final_video_with_audio.mp4
│  Audio + Video  │     Uses: moviepy
└─────────────────┘
```

---

## Detailed Step-by-Step Breakdown

### Step 0: Load System Prompts
**File:** `step_00_load_prompts.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `CONFIG.py` settings | `test_output/system_prompt.txt` | shared.py |

**What it does:**
- Loads the `SYSTEM_GDOT` prompt from `shared.py` (which includes `CUSTOM_INSTRUCTIONS` from `CONFIG.py`)
- Saves the combined system prompt to disk for reference

**Failure Points:** None (simple file write)

---

### Step 1: Validate Markdown Input
**File:** `step_01_validate_input.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `INPUT.md` (or CLI arg, or built-in sample) | `test_output/input.md` | shared.py |

**What it does:**
- Reads markdown content from `INPUT.md` (priority 1), CLI argument (priority 2), or built-in sample (fallback)
- Validates content is at least 50 characters
- Copies validated content to `test_output/input.md`

**Failure Points:**
- ❌ File not found (if using CLI argument)
- ❌ Content too short (<50 chars)

---

### Step 2: Generate Summary
**File:** `step_02_generate_summary.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/input.md` | `test_output/summary.txt` | OpenAI API, shared.py |

**What it does:**
- Reads the validated markdown
- Calls GPT-4o-mini to generate a ~100-word summary
- Focuses on: main concepts, safety points, practical applications, takeaways

**Failure Points:**
- ❌ OpenAI API key missing
- ❌ API rate limits or errors
- ❌ Input.md not found (step 1 not run)

---

### Step 3: Generate Base Manim Script (CRITICAL)
**File:** `step_03_generate_base_script.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/summary.txt`, `test_output/input.md` | `test_output/base_script.py`, `test_output/timings.json` | OpenAI API, shared.py |

**What it does:**
- Reads summary and full content
- Calls GPT-4o-mini with a detailed prompt to generate Python Manim code
- Prompt includes:
  - Manim capabilities guide (shapes, animations, colors)
  - Visual diversity requirements (arrows, circles, transforms)
  - Structural requirements (slide markers, fadeouts)
- Validates syntax with `compile()`
- Analyzes visual diversity (checks for variety of shapes/animations)

**Output Format:**
```python
from manim import *

class VideoName(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Slide 1: Title
        ...
        self.play(FadeOut(...))
        
        # Slide 2: Content
        ...
```

**Failure Points:**
- ❌ **LLM generates syntactically invalid Python** (caught by compile())
- ❌ **LLM generates runtime errors** (list index out of range, undefined variables) — NOT caught until Step 7
- ❌ LLM ignores visual diversity requirements (just uses rectangles)
- ❌ LLM doesn't follow slide marker format (`# Slide N:`)

**⚠️ MAJOR LOOPHOLE:** The script is validated for syntax but NOT for runtime correctness. Errors like mismatched list indices only surface in Step 7.

---

### Step 4: Suggest Images
**File:** `step_04_suggest_images.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/summary.txt`, `test_output/timings.json` | `test_output/images.json` | OpenAI API, shared.py |

**What it does:**
- Reads summary and slide timings
- Calls GPT-4o-mini to suggest image search queries for each slide
- Outputs JSON with search terms and purposes

**Failure Points:**
- ❌ API errors
- ❌ JSON parsing failures

---

### Step 5: Download Images
**File:** `step_05_download_images.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/images.json` | `test_output/images/*.jpg\|png`, `test_output/downloaded_images.json` | SerpAPI, PIL |

**What it does:**
- Reads image suggestions
- Uses SerpAPI to search Google Images
- Downloads and validates images (checks for corruption with PIL)
- Saves to `images/` folder

**Failure Points:**
- ❌ SerpAPI key missing
- ❌ No search results found
- ❌ Downloaded images corrupted
- ❌ Network errors

---

### Step 6: Inject Images into Script
**File:** `step_06_inject_images.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/base_script.py`, `test_output/downloaded_images.json` | `test_output/render_script.py` | PIL, shared.py |

**What it does:**
- Reads base Manim script and downloaded image metadata
- Validates each image file
- Injects `ImageMobject` code into the script at each slide
- Places images in top-right corner with "Reference Image" label
- Modifies `FadeOut()` calls to include image groups

**Injection Pattern:**
```python
# Slide 1: Title
# [AUTO-INJECTED] Reference image for slide 1 (top-right corner)
img_1 = ImageMobject(r"path/to/image.jpg")
img_1.set_height(2.0)
...
self.play(FadeIn(img_group_1))
```

**Failure Points:**
- ❌ Image files missing or corrupted
- ❌ Script doesn't have expected `# Slide N:` markers
- ❌ Script doesn't have expected `self.play(` patterns

---

### Step 7: Render Silent Video (CRITICAL)
**File:** `step_07_render_video.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/render_script.py` | `test_output/media/videos/.../VideoName.mp4`, `test_output/video_path.txt` | Manim CLI, LaTeX |

**What it does:**
- Runs `manim -pqh --format mp4` on the render script
- Creates high-quality (1080p60) silent video
- Saves video path for next steps

**Failure Points:**
- ❌ **Python runtime errors in generated script** (IndexError, NameError, etc.)
- ❌ Manim not installed or misconfigured
- ❌ LaTeX not installed (for MathTex)
- ❌ FFmpeg not available
- ❌ Image files referenced in script don't exist

**⚠️ MAJOR LOOPHOLE:** This is where LLM-generated code errors manifest. If the LLM wrote buggy code in Step 3, it crashes here with cryptic Manim stack traces.

---

### Step 8: Generate Narration
**File:** `step_08_generate_narration.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/summary.txt`, `test_output/timings.json` | `test_output/narration.json` | OpenAI API, shared.py |

**What it does:**
- Reads summary and slide timings
- Calls GPT-4o-mini to generate educational narration for each slide
- Requirements: 50-80 words per slide, references visuals, professional tone
- Outputs JSON array with narration text per slide

**Failure Points:**
- ❌ API errors
- ❌ JSON parsing failures

---

### Step 9: Generate Audio Clips (PROBLEMATIC)
**File:** `step_09_generate_audio.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/narration.json` | `test_output/audio_clips/*.mp3`, `test_output/audio_clips.json` | edge-tts OR pyttsx3 |

**What it does:**
1. Tries edge-tts (Microsoft Azure TTS, requires internet)
2. Falls back to pyttsx3 (Windows SAPI, offline)
3. Generates MP3 audio for each narration clip

**Failure Points:**
- ❌ **edge-tts: "No audio was received"** — network/firewall/service issue
- ❌ **pyttsx3: File rename errors** — existing files not cleaned up
- ❌ pyttsx3 not installed
- ❌ Empty narration text

**⚠️ MAJOR LOOPHOLE:** edge-tts requires internet access to Microsoft's TTS service. If blocked by firewall or service is down, it fails silently with "No audio was received" for ALL clips. The pyttsx3 fallback needs a clean directory.

---

### Step 10: Merge Audio & Video
**File:** `step_10_merge_audio_video.py`

| Input | Output | Dependencies |
|-------|--------|--------------|
| `test_output/video_path.txt`, `test_output/audio_clips.json` | `test_output/final_video_with_audio.mp4` | moviepy, ffmpeg |

**What it does:**
- Loads silent video from Step 7
- Concatenates all audio clips
- Handles duration mismatches (pads with silence if needed)
- Writes final video with audio

**Failure Points:**
- ❌ No audio files generated (Step 9 failed)
- ❌ Video file not found (Step 7 failed)
- ❌ moviepy/ffmpeg not installed
- ❌ Duration mismatch too large

---

## Configuration Files

### CONFIG.py
User-editable settings:
- `VIDEO_NAME`: Custom video class name (or auto-generate from INPUT.md)
- `CLEAR_CACHE`: Delete old files before each run
- `CUSTOM_INSTRUCTIONS`: Added to all LLM prompts
- `COLORS`: Color palette for Manim
- `IMAGE_SETTINGS`: Position/size of reference images
- `TTS_VOICE`: Voice for edge-tts
- `TARGET_SLIDES`: Number of slides to generate
- `ANIMATION_STYLE/COMPLEXITY`: Creative mode settings

### shared.py
Shared utilities and configuration loader:
- `SYSTEM_GDOT`: Combined system prompt
- `call_llm()`: OpenAI API wrapper
- `get_video_name()`: Extracts class name from content
- Path constants: `TEST_DIR`, `INPUT_FILE`

---

## Common Failure Patterns & Solutions

| Issue | Step | Cause | Solution |
|-------|------|-------|----------|
| "IndexError: list index out of range" | 7 | LLM generated buggy list comprehension | Improve Step 3 prompt OR manually fix base_script.py |
| "No audio was received" | 9 | edge-tts blocked by network/firewall | Use pyttsx3 fallback, ensure clean audio_clips folder |
| "Manim render failed" | 7 | Syntax error in generated script | Check Step 3 syntax validation |
| "Video file not found" | 10 | Step 7 failed | Fix Step 7 first |
| "Image validation failed" | 6 | Corrupted download | Re-run Step 5 |

---

## Execution Flow

### Full Run
```bash
python run_all.py
```

### Individual Steps
```bash
python step_01_validate_input.py
python step_02_generate_summary.py
# ... etc
```

### Skip to Specific Step (after fixing issues)
```bash
# After fixing base_script.py, re-run from step 6:
python step_06_inject_images.py
python step_07_render_video.py
python step_08_generate_narration.py
python step_09_generate_audio.py
python step_10_merge_audio_video.py
```

---

## Key Loopholes to Address

1. **Step 3 → Step 7 Gap**: LLM-generated code is validated for syntax but not runtime correctness. Need to either:
   - Add a "dry run" execution test after Step 3
   - Improve the prompt with more explicit code patterns
   - Add automated code review/correction step

2. **Audio Generation Reliability**: edge-tts requires internet and can fail silently. Need to:
   - Make pyttsx3 the primary method (works offline)
   - Ensure clean directory before audio generation
   - Add proper error recovery

3. **Visual Diversity**: Despite prompting, LLM often falls back to simple rectangles. Need to:
   - Provide more concrete code examples in prompt
   - Add a regeneration loop if diversity check fails
   - Consider pre-built animation templates

---

## File Structure

```
test_workflow/
├── INPUT.md                    # YOUR CONTENT GOES HERE
├── CONFIG.py                   # Settings
├── shared.py                   # Shared utilities
├── run_all.py                  # Runs all steps
├── step_00_load_prompts.py
├── step_01_validate_input.py
├── step_02_generate_summary.py
├── step_03_generate_base_script.py   # ⚠️ Critical
├── step_04_suggest_images.py
├── step_05_download_images.py
├── step_06_inject_images.py
├── step_07_render_video.py           # ⚠️ Critical
├── step_08_generate_narration.py
├── step_09_generate_audio.py         # ⚠️ Problematic
├── step_10_merge_audio_video.py
└── test_output/
    ├── input.md
    ├── summary.txt
    ├── base_script.py
    ├── render_script.py
    ├── timings.json
    ├── images.json
    ├── downloaded_images.json
    ├── narration.json
    ├── audio_clips.json
    ├── video_path.txt
    ├── images/
    │   └── slide_*.jpg|png
    ├── audio_clips/
    │   └── clip_*.mp3
    └── media/
        └── videos/render_script/1080p60/
            └── VideoName.mp4
```

---

## Recommended Prompt Improvements

To give better prompts for fixing issues, provide:

1. **The exact error message** from the step that failed
2. **The relevant generated file** (e.g., `base_script.py` for Step 7 errors)
3. **The input content** (`INPUT.md`)
4. **Which step number** failed

Example: "Step 7 failed with IndexError. Here's base_script.py lines 75-85 where the error occurred."

