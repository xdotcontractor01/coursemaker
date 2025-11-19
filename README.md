# GDOT Educational Video Generator

A full-stack Python application that converts Markdown documents into professional educational videos with narration, visuals, and animations using an 11-step AI-powered workflow.

## Features

- **Streamlit Dashboard**: Clean UI with real-time progress tracking
- **11-Step Workflow**: From MD parsing to final video with checkpoints
- **Resilience**: Automatic retries, rollbacks, and degraded mode
- **Live Updates**: Mermaid flowchart showing step progress
- **Error Tracking**: Detailed error logging to JSON per job
- **Job History**: SQLite database with downloadable results

## Prerequisites

Before running the application, install:

1. **Python 3.10+** with pip

2. **FFmpeg** (required by Manim and MoviePy):
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

3. **OpenAI API Key** (Required):
   - Get API key: https://platform.openai.com/api-keys
   - Costs: ~$0.02-0.05 per video (GPT-4o-mini)
   - Add billing info to your OpenAI account

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd coursemaker
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
   
   Optional: Add SerpAPI key for images
   ```env
   SERPAPI_KEY=your-serpapi-key
   ```
   Get SerpAPI key from https://serpapi.com

## Usage

### Run Streamlit App

```bash
streamlit run app.py
```

Navigate to http://localhost:8501 in your browser.

### Run with FastAPI Backend (Optional)

In a separate terminal:

```bash
uvicorn api:app --reload
```

Then access API at http://localhost:8000/docs

## Workflow Steps

0. **Load System Prompts**: GDOT-DOT professional style
1. **Input MD & Pre-Validate**: Chunk large documents
2. **LLM: Generate Summary**: 100-word overview
3. **LLM: Generate Base Script**: Manim animation code
4. **LLM: Suggest Images & Layouts**: Visual content planning
5. **Fetch Images**: Download via SerpAPI, resize to 16:9
6. **Inject Images & Layouts**: Merge visuals into script
7. **Validate & Render**: Generate silent video (MP4)
8. **LLM: Generate Narration**: Per-slide voice script
9. **TTS & Audio Padding**: edge-tts synthesis
10. **Merge, Report & Cleanup**: Final video with audio

## Resilience Features

- **Per-step retries**: Up to 3 attempts with exponential backoff
- **Checkpoints**: JSON snapshots after each step
- **Rollback**: Restore previous checkpoint on failure
- **Fallbacks**: Degraded functionality (e.g., shapes instead of images)
- **Error logging**: Detailed JSON logs per job
- **Degraded mode**: Continue with >5 errors, mark status

## Project Structure

```
coursemaker/
├── app.py              # Streamlit UI entry point
├── api.py              # FastAPI endpoints (optional)
├── workflow.py         # 11-step resilient workflow
├── prompts.py          # GDOT-DOT system prompts
├── db.py               # SQLAlchemy models
├── logger.py           # Error logging utilities
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── .env                # Your config (create this)
└── data/               # Created at runtime
    ├── md_videos.db    # SQLite database
    ├── checkpoints/    # Step checkpoints
    ├── errors.json     # Error logs
    └── outputs/        # Generated videos
```

## Troubleshooting

### Manim not found
Ensure Manim is installed and in PATH:
```bash
manim --version
```

### FFmpeg errors
Install FFmpeg and verify:
```bash
ffmpeg -version
```

### API key errors
Check `.env` file has valid keys without quotes:
```
GROQ_API_KEY=gsk_...
SERPAPI_KEY=...
```

## License

MIT License

