# Coursemaker — GDOT Educational Video Generator

A deterministic, code-driven pipeline for producing narrated educational videos from the Georgia Department of Transportation (GDOT) *Basic Highway Plan Reading* manual. The system converts a source PDF (extracted to Markdown) into a full course of animated, narrated video lessons with quizzes.

## Overview

| Stat | Value |
|------|-------|
| Chapters | 1–15 |
| Video lessons | ~25 |
| Resolution | 1920 x 1080, 30 fps |
| Audio | OpenAI TTS (model `tts-1`, voice `nova`) |
| Animation | Manim Community Edition |
| Narration source | Manifest JSON (no hardcoded text in scripts) |

All videos, audio, and images are **fully reproducible** from the tracked code and manifests. Generated assets are `.gitignore`-d and never committed.

## Repository Structure

```
coursemaker/
├── manifests/              # Chapter manifest JSON files (source of truth)
├── manim_scripts/          # Manim animation scripts per chapter
├── scripts/
│   ├── audio_generation/   # TTS audio generation (OpenAI)
│   ├── content_generation/ # Quiz & course content pipeline
│   ├── extraction/         # Markdown → manifest extraction
│   ├── image_download/     # CDN image fetcher
│   ├── rendering/          # Manim batch render scripts
│   └── utilities/          # Dry-runs, validation, unified lesson builder
├── narration/              # Chapter 1 narration source files
├── docs/                   # Pipeline documentation & source markdown
├── assets/logo/            # GDOT watermark logo (SVG)
├── workflow.py             # 11-step resilient MD-to-video engine
├── app.py                  # Streamlit UI
├── api.py                  # FastAPI endpoints
├── requirements.txt        # Python dependencies
└── env.example             # Environment variable template
```

## Quick Start

```bash
# Clone
git clone https://github.com/xdotcontractor01/coursemaker.git
cd coursemaker

# Python environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
pip install manim edge-tts

# Environment variables
cp env.example .env
# Edit .env → add OPENAI_API_KEY (required for TTS)

# Verify
python --version   # 3.10+
ffmpeg -version    # 4.4+
manim --version    # 0.19.0+
```

## Regenerate All Assets

Run these stages in order:

```bash
# 1. Extract content → manifests
python scripts/extraction/extract_chapters_234.py
python scripts/extraction/extract_chapters_567.py
python scripts/extraction/extract_chapters_8_15.py

# 2. Download images
python scripts/image_download/download_chapters_234_images.py
python scripts/image_download/download_chapters_567_images.py
python scripts/image_download/download_chapters_8_15_images.py

# 3. Generate audio (requires OPENAI_API_KEY)
python scripts/audio_generation/generate_audio.py
python scripts/audio_generation/generate_chapters_234_audio.py
python scripts/audio_generation/generate_chapters_567_audio.py
python scripts/audio_generation/generate_chapters_8_15_audio.py

# 4. Render videos (requires Manim + FFmpeg)
python scripts/rendering/render_chapters_234.py
python scripts/rendering/render_chapters_567.py
python scripts/rendering/render_chapters_8_15.py

# 5. Generate quizzes & course content
python scripts/content_generation/generate_course_content_quizzes.py --chapters 1-15

# 6. Build unified lesson JSON
python scripts/utilities/build_unified_lessons.py
```

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | TTS audio generation |
| `SERPAPI_KEY` | No | Ad-hoc image search (workflow mode) |
| `LLM_PROVIDER` | No | `openai` (default) or `groq` |
| `GROQ_API_KEY` | No | Groq LLM fallback |
| `EDGE_TTS_VOICE` | No | Default: `en-US-GuyNeural` |

## Key Design Decisions

- **No LLMs at render time** — All narration text is locked in manifests at extraction time. Rendering is deterministic.
- **White background, dark text** — Professional GDOT visual identity enforced in every Manim script.
- **Audio-synced scenes** — Each scene duration is derived from the WAV file header, not hardcoded.
- **Sanitized narration** — Station numbers, project IDs, and alphanumeric codes are replaced with readable descriptors before TTS.
- **Confidence-gated quizzes** — Low-confidence questions are flagged in `review/` CSVs for human verification.

## Documentation

See [`docs/VIDEO_GENERATION_PIPELINE.md`](docs/VIDEO_GENERATION_PIPELINE.md) for the full technical reference covering architecture, rules, constraints, and contribution guidelines.

## License

See [LICENSE](LICENSE).
