# Video Generation Pipeline — Technical Documentation

> **Audience:** Senior engineers joining the project.
> **Last updated:** 2026-02-16
> **Branch:** `feature/unified-chapter-structure`

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Video Generation Rules](#3-video-generation-rules)
4. [Chapter & Lesson Strategy](#4-chapter--lesson-strategy)
5. [Constraints & Design Decisions](#5-constraints--design-decisions)
6. [Reproducibility Instructions](#6-reproducibility-instructions)
7. [What Is NOT in GitHub](#7-what-is-not-in-github)
8. [Safe Contribution Rules](#8-safe-contribution-rules)

---

## 1. Purpose

### What This System Is

This repository contains a **deterministic, code-driven pipeline** for producing educational videos about the Georgia Department of Transportation (GDOT) *Basic Highway Plan Reading* manual. The system converts a source PDF (extracted to Markdown) into a full course of narrated, animated videos — complete with quizzes, sanitized narration, and unified lesson metadata.

The pipeline spans 15 chapters and produces ~25 individual video lessons, each rendered as a 1080p/30fps MP4 with synchronized text-to-speech audio.

### Why Videos and Audio Are NOT Stored in GitHub

Generated media files (videos, audio, images) are **excluded from version control** for the following reasons:

| Reason | Detail |
|--------|--------|
| **Size** | A single chapter's video outputs can exceed 500 MB. The full set of rendered videos, WAV audio files, and downloaded images can easily reach 10+ GB. Git and GitHub are not designed for large binary assets. |
| **Reproducibility** | Every generated asset can be exactly reproduced by running the tracked scripts against the tracked manifests. The code *is* the source of truth — the media files are derived artifacts. |
| **Diff quality** | Binary files produce useless diffs. Tracking them in Git would bloat history, slow clones, and provide zero insight into what changed. |
| **Separation of concerns** | Developers modify code and manifests. Reviewers inspect code. CI can validate scripts. None of these workflows require committed media. |

### Core Philosophy

```
Source of truth  =  code  +  manifests  +  source markdown
Generated output =  videos  +  audio  +  images  +  quiz JSON  +  logs
```

Everything on the right side of this equation is `.gitignore`-d and reproduced locally.

---

## 2. High-Level Architecture

### End-to-End Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│                        SOURCE MATERIAL                               │
│  PDF (GDOT Basic Highway Plan Reading)                               │
│       ↓  (MinerU extraction — one-time, offline)                     │
│  Markdown file (docs/MinerU_markdown_*.md)                           │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 1 — CONTENT EXTRACTION   (scripts/extraction/)                 │
│  • Parse Markdown by chapter boundaries (page ranges)                │
│  • Extract scene-level narration text, source quotes, image URLs     │
│  • Sanitize narration (remove station numbers, project IDs, etc.)    │
│  • Generate per-chapter manifest JSON (manifests/chapterXX.json)     │
│  • Generate sanitization maps (sanitization/)                        │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 2 — IMAGE DOWNLOAD   (scripts/image_download/)                 │
│  • Read image URLs from manifest "images" field                      │
│  • Download JPEG files to assets/images/chapterXX/                   │
│  • Validate dimensions, repair broken downloads                      │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 3 — AUDIO GENERATION   (scripts/audio_generation/)             │
│  • Read narration_text (or narration_sanitized) from manifest        │
│  • Call OpenAI TTS API (model: tts-1, voice: nova, format: pcm)      │
│  • Convert raw PCM to WAV (24 kHz, 16-bit, mono)                    │
│  • Save to audio/chXX_sceneYY.wav                                    │
│  • Record actual duration back into manifest "duration" field        │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 4 — MANIM RENDERING   (manim_scripts/, scripts/rendering/)     │
│  • Each chapter has a Manim Python script (manim_scripts/chapterXX.py│
│  • Script loads its manifest at runtime                              │
│  • Scenes are built programmatically: headings, bullets, images,     │
│    tables, diagrams — all on a white background                      │
│  • Audio is synchronized per scene via WAV duration detection         │
│  • Render command: manim -qh --fps 30 chapterXX.py SceneClass       │
│  • Output: media/videos/.../SceneClass.mp4                           │
│  • Copy to outputs/chapterXX_lessonYY.mp4                            │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 5 — QUIZ & CONTENT GENERATION                                  │
│  (scripts/content_generation/generate_course_content_quizzes.py)     │
│  • Parse Markdown for question–answer pairs                          │
│  • Map questions to videos via manifest scene ranges                 │
│  • Convert to MCQ format with generated distractors                  │
│  • Assign confidence scores; flag low-confidence for review          │
│  • Sanitization pass (remove identifiers from quiz text)             │
│  • Output: quizzes/ChapterXX_videoYY/import_ready.json               │
│  •         manifests/course_content/ChapterXX_videoYY/content.json   │
│  •         review/review_chapterXX.csv (flagged questions)           │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 6 — UNIFIED LESSON ASSEMBLY                                    │
│  (scripts/utilities/build_unified_lessons.py)                        │
│  • Merge course content + quizzes into a single JSON per lesson      │
│  • Output: unified_lessons/ChapterXX_videoYY.json                    │
│  • Each file contains: title, summary, source pages, quiz array,     │
│    content source URL, generation timestamp                          │
└──────────────────────────────────────────────────────────────────────┘
```

### Parallel Workflow System (Streamlit / FastAPI)

In addition to the chapter-specific batch scripts above, the repository includes a **general-purpose MD-to-video workflow** (`workflow.py`) exposed through:

- **Streamlit UI** (`app.py`) — interactive dashboard with real-time progress, Mermaid flowchart, and job history.
- **FastAPI** (`api.py`) — RESTful endpoints for programmatic job management.

This workflow implements an **11-step resilient pipeline** with checkpointing, retry logic (exponential backoff), and per-step fallbacks. It is LLM-assisted (using OpenAI or Groq) and is designed for ad-hoc, single-document video generation — not for the batch chapter pipeline described above.

| Component | Role |
|-----------|------|
| `workflow.py` | 11-step MD-to-video engine (steps 0–10) |
| `app.py` | Streamlit frontend |
| `api.py` | FastAPI backend |
| `db.py` | SQLAlchemy job persistence (SQLite) |
| `logger.py` | Structured error logging, checkpoint management |
| `prompts.py` | System prompts and prompt templates for LLM calls |
| `smart_content_injector.py` | Analyzes Manim scripts to reposition content when adding images |
| `setup.py` | Environment setup helper (dependency install, directory creation) |
| `run.py` | Launcher (Streamlit or FastAPI mode) |

---

## 3. Video Generation Rules

These rules are enforced programmatically in the Manim scripts and must be preserved when adding new chapters.

### Visual Rules

| Rule | Implementation | Location |
|------|---------------|----------|
| **White background** | `config.background_color = WHITE` set at module level in every Manim script | `manim_scripts/chapterXX.py` line ~22 |
| **Resolution** | 1920 × 1080 (Full HD) | `config.pixel_width = 1920; config.pixel_height = 1080` |
| **Frame rate** | 30 fps for chapter renders; 60 fps available for preview scripts | `config.frame_rate = 30` |
| **Color scheme** | Dark-on-light for readability on white: titles in `#1565C0` (blue), headings in `#2E7D32` (green), body in `#212121` (dark gray), accents in `#C62828` (red), muted in `#616161` | Constants block in each script |
| **Font sizes** | Main title: 52pt, section title: 44pt, subtitle: 30pt, body/bullet: 28pt | `MAIN_TITLE_FONT_SIZE`, `TITLE_FONT_SIZE`, `SUBTITLE_FONT_SIZE`, `BULLET_FONT_SIZE` |
| **Line spacing** | 0.35 Manim units between bullet lines | `LINE_SPACING = 0.35` |
| **Logo watermark** | GDOT SVG logo placed statically on each scene | `LOGO_PATH = PROJECT_ROOT / "test_workflow/GDOT LOGO For Video watermark - 200x110.svg"` |
| **Image scaling** | Downloaded images scaled to 55% by default | `IMAGE_SCALE_FACTOR = 0.55` |

### Audio Synchronization Rules

| Rule | Detail |
|------|--------|
| **Per-scene audio** | Each manifest scene has a `tts_file` field pointing to its WAV file |
| **Duration detection** | `get_wav_duration_seconds()` reads the WAV header at render time to determine the exact duration |
| **Audio buffer** | A 0.12-second buffer (`AUDIO_BUFFER`) is added after each scene's audio duration to prevent clipping |
| **Wait timing** | Each scene calls `self.wait(audio_duration + AUDIO_BUFFER)` to hold the frame for exactly the narration length |
| **No hardcoded durations** | Durations are always read from WAV files or manifest `duration` fields — never hardcoded into Manim scripts |

### Narration & Sanitization Rules

| Rule | Detail |
|------|--------|
| **All narration from manifests** | The `narration_text` field in each scene of the manifest is the single source of truth for what is spoken |
| **No hardcoded text in scripts** | Manim scripts read bullet text and titles from the manifest JSON — they do not contain inline narration strings |
| **Sanitization** | Station numbers (e.g., `192+50`), project IDs, mixed alphanumeric identifiers, and other non-pronounceable codes are replaced with readable descriptors (e.g., "this station number") before TTS |
| **Sanitization maps** | Every replacement is recorded in a sanitization map JSON file for traceability |
| **narration_sanitized vs narration_raw** | Manifests store both the original (`narration_raw`) and sanitized (`narration_sanitized` or `narration_text`) versions |

---

## 4. Chapter & Lesson Strategy

### Chapter-to-Video Mapping

Not every chapter produces a single video. The number of videos per chapter depends on the density of the source material (page count, scene count, and total audio duration).

| Chapter | Pages | Scenes | Videos (Lessons) | Splitting Logic |
|---------|-------|--------|-------------------|-----------------|
| 1 | 1–11 | 24 | 4 | Split by topic groups; separate per-video manifests (`chapter01_video01.json` – `chapter01_video04.json`) |
| 2 | 11–12 | 4 | 1 | Short chapter; single video |
| 3 | 13–14 | 4 | 1 | Short chapter; single video |
| 4 | 15–17 | 5 | 1 | Short chapter; single video |
| 5 | 19–21 | 6 | 1 | Moderate; single video |
| 6 | 23–36 | 13 | 2 | Long chapter; split into 2 lessons via `FALLBACK_VIDEO_SPLITS` |
| 7 | 37–50 | 15 | 3 | Long chapter; split into 3 lessons via `FALLBACK_VIDEO_SPLITS` |
| 8 | 53–65 | 11 | 3 | Uses `lesson_boundaries` in manifest to define scene-to-lesson mapping |
| 9 | 66–68 | 3 | 1 | Short chapter; single video |
| 10 | 69–73 | 5 | 1 | Moderate; single video |
| 11 | 74–78 | 4 | 1 | Moderate; single video |
| 12 | 79–84 | 5 | 1 | Moderate; single video |
| 13 | 85–93 | 8 | 2 | Split into 2 lessons |
| 14 | 94–97 | 4 | 1 | Short chapter; single video |
| 15 | 98–105 | 7 | 2 | Split into 2 lessons |

### How Lessons Are Split

There are two mechanisms:

1. **`lesson_boundaries` in manifest** (preferred, chapters 8+): The manifest JSON contains a `lesson_boundaries` object mapping lesson IDs to scene index arrays and a title:

   ```json
   "lesson_boundaries": {
     "lesson_01": { "scenes": [1, 2, 3, 4], "title": "Introduction and Pipe Culverts" },
     "lesson_02": { "scenes": [5, 6, 7], "title": "Box Culverts and Wing Walls" },
     "lesson_03": { "scenes": [8, 9, 10, 11], "title": "Bridges and Utilities" }
   }
   ```

2. **`FALLBACK_VIDEO_SPLITS` in quiz generator** (chapters 5–7): A hardcoded mapping in `generate_course_content_quizzes.py` defines which scene indices belong to which lesson for chapters that predate the `lesson_boundaries` schema.

3. **Separate manifest files** (chapter 1): Chapter 1 uses four independent manifest files (`chapter01_video01.json` through `chapter01_video04.json`), each defining its own scene array.

### Why Some Chapters Have More Videos

- **Page count:** Chapters spanning 10+ pages contain too much material for a single video at a comfortable narration pace.
- **Audio duration target:** Each lesson should ideally be 3–8 minutes. If a chapter's total audio exceeds ~8 minutes, it is split.
- **Topic coherence:** Lessons are split along natural topic boundaries (e.g., "Pipe Culverts" vs. "Box Culverts") rather than at arbitrary scene counts.

### Manifest Naming Conventions

| Chapter Range | Manifest Pattern | Example |
|--------------|-----------------|---------|
| Chapter 1 | `chapter01_videoXX.json` | `chapter01_video01.json` |
| Chapters 2–4 | `chapter_0X.json` (underscore) | `chapter_02.json` |
| Chapters 5–15 | `chapter0X.json` (no underscore) | `chapter08.json` |

This inconsistency is historical. The quiz/content generator (`manifest_paths_for_chapter()`) handles all three patterns.

---

## 5. Constraints & Design Decisions

### Why LLMs Are NOT Used During Final Video Generation

The batch chapter pipeline (chapters 1–15) does **not** call any LLM at render time. This is deliberate:

| Constraint | Rationale |
|------------|-----------|
| **Determinism** | LLM outputs are non-deterministic. Re-running the pipeline must produce identical results. Manifests lock all narration text, bullet points, and scene structure at extraction time. |
| **Cost control** | Each render may be executed many times during development. LLM API calls at $0.01–$0.10 per call would accumulate unnecessarily. |
| **Auditability** | Every word spoken in a video traces back to a manifest field, which traces back to a source page. LLM-generated text would break this chain. |
| **Offline capability** | Rendering should work without internet access (given pre-downloaded images and pre-generated audio). Only the TTS step requires an API call. |

The general-purpose workflow (`workflow.py`) *does* use LLMs (OpenAI GPT-4o-mini or Groq Mixtral) for ad-hoc summarization and script generation — but this is a separate system, not the chapter production pipeline.

### Why Deterministic Scripts Are Preferred

Each Manim script is a hand-crafted Python file, not generated at runtime. This means:

- Visual layout is predictable and reviewable in code review.
- Scene timing is controlled by WAV duration, not by LLM-estimated pacing.
- Typography, colors, and positioning follow enforced constants (see Section 3).
- Bugs can be fixed by editing a specific line, not by re-prompting an LLM.

### Why Quizzes Are PDF-First

Quiz questions are extracted from the source Markdown (which was extracted from the source PDF). The extraction pipeline:

1. Searches for patterns like `Q:` / `A:`, numbered questions, or section review blocks in the Markdown.
2. Converts each question to multiple-choice format by generating plausible distractors.
3. Assigns a confidence score based on extraction quality heuristics.

This PDF-first approach ensures that quiz content is grounded in the official GDOT material, not hallucinated by an LLM.

### Why Confidence & Review Gates Exist

Each generated quiz question receives a confidence score (0.0–1.0). Questions below the threshold are:

- Written to `review/review_chapterXX.csv` for human review.
- Marked `"auto_ready": false` in the unified lesson JSON.

This prevents low-quality or ambiguous questions from reaching students without human verification.

---

## 6. Reproducibility Instructions

### Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| Python | 3.10+ | [python.org](https://www.python.org/) |
| FFmpeg | 4.4+ | `brew install ffmpeg` (macOS) or [ffmpeg.org](https://ffmpeg.org/download.html) |
| Manim | Community Edition 0.19.0+ | `pip install manim` |
| Node.js | 18+ (for frontend only) | [nodejs.org](https://nodejs.org/) |

### Environment Variables

Copy `env.example` to `.env` and fill in:

```bash
cp env.example .env
```

| Variable | Required | Source |
|----------|----------|--------|
| `OPENAI_API_KEY` | **Yes** (for TTS audio generation) | [platform.openai.com](https://platform.openai.com/) |
| `SERPAPI_KEY` | Optional (for ad-hoc image search in workflow mode) | [serpapi.com](https://serpapi.com/) |
| `LLM_PROVIDER` | Optional, defaults to `openai` | Set to `openai` or `groq` |
| `GROQ_API_KEY` | Optional (if using Groq as LLM provider) | [console.groq.com](https://console.groq.com/) |
| `EDGE_TTS_VOICE` | Optional, defaults to `en-US-GuyNeural` | Any [edge-tts voice](https://github.com/rany2/edge-tts) |
| `MANIM_PATH` | Optional, defaults to `manim` | Path to Manim binary if not on PATH |

### Step-by-Step: Clone and Regenerate

```bash
# 1. Clone the repository
git clone https://github.com/<org>/coursemaker.git
cd coursemaker

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install manim edge-tts

# 4. (Alternative) Run the setup helper
python setup.py

# 5. Set up environment variables
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

# 6. Verify FFmpeg
ffmpeg -version
```

### Regenerating Assets — Chapter-by-Chapter

The pipeline runs in stages. Each stage must complete before the next.

#### Stage 1: Extract Content (generates manifests)

```bash
# Chapters 2-4
python scripts/extraction/extract_chapters_234.py

# Chapters 5-7
python scripts/extraction/extract_chapters_567.py

# Chapters 8-15
python scripts/extraction/extract_chapters_8_15.py
```

**Note:** Chapter 1 manifests (`chapter01_video01.json` – `chapter01_video04.json`) are already tracked in Git and do not need extraction.

#### Stage 2: Download Images

```bash
python scripts/image_download/download_chapters_234_images.py
python scripts/image_download/download_chapters_567_images.py
python scripts/image_download/download_chapters_8_15_images.py
```

Output: `assets/images/chapterXX/figure_X_Y.jpg`

#### Stage 3: Generate Audio (requires OPENAI_API_KEY)

```bash
python scripts/audio_generation/generate_audio.py               # Chapter 1
python scripts/audio_generation/generate_chapters_234_audio.py
python scripts/audio_generation/generate_chapters_567_audio.py
python scripts/audio_generation/generate_chapters_8_15_audio.py
```

Output: `audio/chXX_sceneYY.wav`

#### Stage 4: Render Videos (requires Manim + FFmpeg)

```bash
python scripts/rendering/render_chapters_234.py
python scripts/rendering/render_chapters_567.py
python scripts/rendering/render_chapters_8_15.py
```

Output: `outputs/chapterXX_lessonYY.mp4`

To render a single scene for testing:

```bash
manim -pql manim_scripts/chapter08.py Chapter08Lesson01   # Low quality, fast
manim -qh --fps 30 manim_scripts/chapter08.py Chapter08Lesson01  # Production
```

#### Stage 5: Generate Quizzes & Course Content

```bash
python scripts/content_generation/generate_course_content_quizzes.py --chapters 1-15
```

Output:
- `quizzes/ChapterXX_videoYY/import_ready.json`
- `manifests/course_content/ChapterXX_videoYY/content.json`
- `review/review_chapterXX.csv`

#### Stage 6: Build Unified Lessons

```bash
python scripts/utilities/build_unified_lessons.py
```

Output: `unified_lessons/ChapterXX_videoYY.json`

### Dry Runs & Validation

Before committing to a full render, use the dry-run and validation scripts:

```bash
python scripts/utilities/dryrun_chapters_234.py
python scripts/utilities/dryrun_chapters_567.py
python scripts/utilities/dryrun_chapters_8_15.py
python scripts/utilities/feasibility_check_chapters_567.py
python scripts/utilities/feasibility_check_chapters_8_15.py
python scripts/utilities/validate_unified_lessons.py
python scripts/utilities/check_render_status.py
```

### Output Locations Summary

| Asset | Directory | Example File |
|-------|-----------|-------------|
| Manifest JSON | `manifests/` | `chapter08.json` |
| Audio | `audio/` | `ch08_scene01.wav` |
| Images | `assets/images/chapterXX/` | `figure_8_2.jpg` |
| Rendered videos | `outputs/` | `chapter08_lesson01.mp4` |
| Manim cache | `media/` | (intermediate render files) |
| Quiz JSON | `quizzes/ChapterXX_videoYY/` | `import_ready.json` |
| Course content | `manifests/course_content/` | `content.json` |
| Unified lessons | `unified_lessons/` | `Chapter08_video01.json` |
| Review flags | `review/` | `review_chapter08.csv` |
| Sanitization maps | `sanitization/` | `sanitization_map_chapter08.json` |

---

## 7. What Is NOT in GitHub

The following files and directories are **excluded from Git** via `.gitignore`. They are generated locally and must never be committed.

| Category | Paths | Why Excluded |
|----------|-------|-------------|
| **Rendered videos** | `outputs/*.mp4`, `media/` | Large binary files (100 MB–1 GB+); fully reproducible from Manim scripts + audio |
| **Audio files** | `audio/*.wav` | Generated by OpenAI TTS from manifest narration text; reproducible with API key |
| **Downloaded images** | `assets/images/chapterXX/*.jpg` | Downloaded from CDN URLs stored in manifests; reproducible with internet access |
| **Quiz JSON** | `quizzes/` | Generated by `generate_course_content_quizzes.py` from manifests + markdown |
| **Course content JSON** | `manifests/course_content/` | Generated by `generate_course_content_quizzes.py` |
| **Unified lesson JSON** | `unified_lessons/*.json` | Generated by `build_unified_lessons.py` from quiz + content JSON |
| **Sanitization maps** | `sanitization/` | Generated during content extraction |
| **Review CSVs** | `review/` | Generated during quiz pipeline; contain flagged questions |
| **Logs** | `logs/`, `app.log` | Runtime logs from the workflow engine |
| **Workflow data** | `data/` | Per-job working directories, checkpoints, SQLite database |
| **Archive bundles** | `*.zip` | Convenience snapshots of generated outputs; not source |
| **Virtual environments** | `venv/`, `coqui_test_env/` | Local Python environments; platform-specific |
| **Test outputs** | `test_output/`, `test_output_aligned/`, `test_coqui_output/` | Scratch directories from development experiments |
| **OS files** | `.DS_Store`, `Thumbs.db` | Operating system metadata |
| **IDE config** | `.vscode/`, `.idea/` | Per-developer editor settings |

### What IS Tracked in Git

| Category | Paths |
|----------|-------|
| **Manim scripts** | `manim_scripts/*.py`, `manim_scripts/chapter01/*.py` |
| **Pipeline scripts** | `scripts/audio_generation/`, `scripts/content_generation/`, `scripts/extraction/`, `scripts/image_download/`, `scripts/rendering/`, `scripts/utilities/` |
| **Core application** | `api.py`, `app.py`, `workflow.py`, `db.py`, `logger.py`, `prompts.py`, `smart_content_injector.py`, `setup.py`, `run.py` |
| **Manifest JSON** | `manifests/chapter*.json`, `manifests/sanitization_map_chapter*.json` |
| **Narration source** | `narration/*.py`, `narration/narration_script.txt` |
| **Frontend** | `src/`, `package.json`, `vite.config.js`, `tailwind.config.js`, `postcss.config.js` |
| **Tests** | `tests/` |
| **Documentation** | `docs/*.md`, `unified_lessons/README.md`, `unified_lessons/CONTENT_SOURCE_REFERENCE.md`, `README.md` |
| **Config** | `requirements.txt`, `env.example`, `LICENSE`, `.gitignore` |

---

## 8. Safe Contribution Rules

### Adding a New Chapter

1. **Create the manifest** in `manifests/` following the schema in `docs/CHAPTER_FILE_STRUCTURE.md`.
   - Use the naming convention: `chapter16.json` (for chapter 16).
   - Include `lesson_boundaries` if the chapter will produce multiple videos.
   - Populate all scene fields: `index`, `title`, `source_pages`, `source_text`, `image_paths`, `bullets`, `narration_text`, `tts_file`.

2. **Write the Manim script** in `manim_scripts/chapter16.py`.
   - Copy the structure from an existing chapter (e.g., `chapter08.py`).
   - Maintain all visual rules from Section 3 (white background, color scheme, font sizes, logo).
   - Load the manifest at runtime — do not hardcode narration or bullet text.

3. **Create extraction and rendering scripts** in the appropriate `scripts/` subdirectories if the existing batch scripts do not cover your chapter range.

4. **Run the full pipeline locally** (extraction → images → audio → render → quizzes → unified lessons) and verify outputs before pushing code.

### Updating an Existing Manifest

- Edit the manifest JSON directly in `manifests/`.
- After editing, regenerate downstream artifacts (audio, video, quizzes) locally to verify.
- Commit only the manifest change. Do not commit regenerated artifacts.

### What NOT to Commit

- **Never commit files in:** `audio/`, `assets/images/`, `media/`, `outputs/`, `quizzes/`, `manifests/course_content/`, `unified_lessons/*.json`, `sanitization/`, `review/`, `data/`, `logs/`
- **Never commit:** `.env`, `config.json`, `*.zip`, `*.mp4`, `*.wav`, `*.jpg`, `*.png`
- **Never commit virtual environments:** `venv/`, `coqui_test_env/`, `env/`

### How to Regenerate Assets Safely

```bash
# After pulling new code or manifests:

# 1. Re-extract content if extraction scripts changed
python scripts/extraction/extract_chapters_8_15.py

# 2. Re-download images if manifest image URLs changed
python scripts/image_download/download_chapters_8_15_images.py

# 3. Re-generate audio if narration text changed
python scripts/audio_generation/generate_chapters_8_15_audio.py

# 4. Re-render if Manim scripts or audio changed
python scripts/rendering/render_chapters_8_15.py

# 5. Re-generate quizzes if manifests changed
python scripts/content_generation/generate_course_content_quizzes.py --chapters 8-15

# 6. Rebuild unified lessons
python scripts/utilities/build_unified_lessons.py
```

### Code Review Checklist

When reviewing a pull request that touches the pipeline, verify:

- [ ] White background rule is preserved (`config.background_color = WHITE`)
- [ ] No hardcoded narration text in Manim scripts — all text from manifest
- [ ] No generated files included in the commit (check for `*.wav`, `*.mp4`, `*.jpg`, `*.json` in `quizzes/`, `manifests/course_content/`, `unified_lessons/`)
- [ ] Manifest schema is consistent with existing chapters
- [ ] Sanitization rules handle any new identifier patterns
- [ ] New scripts have proper `PROJECT_ROOT` resolution (`Path(__file__).parent.resolve()`)
- [ ] Font sizes and color constants match the project standards (Section 3)

---

## Appendix A: Workflow Engine Steps (workflow.py)

The general-purpose MD-to-video workflow (separate from the batch chapter pipeline) executes these 11 steps:

| Step | Name | Description |
|------|------|-------------|
| 0 | Load System Prompts | Load GDOT-DOT style prompts from `prompts.py` |
| 1 | Validate Input | Validate and chunk Markdown input (truncate if >10k chars) |
| 2 | Generate Summary | LLM-generated 100-word summary of the content |
| 3 | Generate Base Script | LLM-generated Manim script + timing JSON |
| 4 | Plan Images & Layouts | LLM suggests images and layout positions |
| 5 | Download Images | Fetch images via SerpAPI or URL |
| 6 | Enhance Script | Inject images into the Manim script using `smart_content_injector.py` |
| 7 | Render Silent Video | Execute Manim to produce a silent MP4 |
| 8 | Generate Narration | LLM-generated narration script with timestamps |
| 9 | Generate Audio | TTS audio from narration using edge-tts |
| 10 | Merge Audio + Video | FFmpeg combines silent video with audio track |

Each step has:
- **Checkpointing:** State saved to `data/checkpoints/` after success
- **Retry logic:** Up to 3 retries per step with exponential backoff
- **Fallback:** Degraded-quality fallback result if all retries fail
- **Error classification:** Errors categorized as TOKEN_ERROR, SYNTAX_ERROR, NETWORK_ERROR, FILE_ERROR, API_ERROR, RENDER_ERROR, FORMAT_ERROR, or UNKNOWN_ERROR

## Appendix B: Assumptions Made in This Document

This documentation was generated based on code inspection. The following engineering assumptions were made explicitly:

1. **Chapter 1 manifests are considered source** because they use a separate per-video file pattern and appear to have been manually curated, unlike the generated `course_content/` JSON.
2. **Sanitization maps in `manifests/`** (`sanitization_map_chapter05.json` through `sanitization_map_chapter07.json`) are treated as tracked source because they were created during the extraction phase for chapters 5–7 and stored alongside manifests — distinct from the `sanitization/` directory which holds generated maps for later chapters.
3. **The `test_workflow/` directory** contains source reference material (including the GDOT logo SVG and source Markdown) and is assumed to be tracked.
4. **The `narration/` directory** contains Python source files for Chapter 1 narration and is treated as tracked source code.
5. **Unified lesson JSON files** are treated as generated artifacts because they are the output of `build_unified_lessons.py`, but the accompanying Markdown files (`README.md`, `CONTENT_SOURCE_REFERENCE.md`) are tracked documentation.
