# GDOT Video Generator - Architecture Documentation

## System Overview

The GDOT Educational Video Generator is a full-stack Python application that converts Markdown documents into professional educational videos using an 11-step AI-powered workflow with comprehensive error handling and resilience features.

## Tech Stack

### Core Technologies
- **Python 3.10+**: Main programming language
- **Streamlit**: Interactive web UI/dashboard
- **FastAPI**: RESTful API endpoints
- **SQLAlchemy**: ORM for SQLite database
- **SQLite**: Local job persistence

### AI & Media Processing
- **Groq API**: LLM for text generation (Mixtral-8x7b)
- **SerpAPI**: Web image search
- **Manim**: Animation and video rendering
- **edge-tts**: Text-to-speech synthesis
- **MoviePy**: Video/audio manipulation
- **Pillow**: Image processing

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Streamlit UI    │      │   FastAPI REST   │        │
│  │   (app.py)       │      │    (api.py)      │        │
│  └──────────────────┘      └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Business Logic Layer                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Workflow Engine (workflow.py)           │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Resilient Step Wrapper                    │  │  │
│  │  │  - Retry logic (exponential backoff)      │  │  │
│  │  │  - Checkpointing                          │  │  │
│  │  │  - Rollback on failure                    │  │  │
│  │  │  - Fallback mechanisms                    │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │                                                    │  │
│  │  11-Step Workflow:                                │  │
│  │  0. Load System Prompts                           │  │
│  │  1. Validate Input                                │  │
│  │  2. Generate Summary (LLM)                        │  │
│  │  3. Generate Base Script (LLM)                    │  │
│  │  4. Suggest Images & Layouts (LLM)               │  │
│  │  5. Fetch Images (SerpAPI)                        │  │
│  │  6. Inject Images                                 │  │
│  │  7. Render Silent Video (Manim)                  │  │
│  │  8. Generate Narration (LLM)                      │  │
│  │  9. Generate Audio (edge-tts)                     │  │
│  │  10. Merge & Finalize (MoviePy)                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Database    │  │   Logger     │  │   Prompts    │ │
│  │   (db.py)    │  │ (logger.py)  │  │(prompts.py)  │ │
│  │              │  │              │  │              │ │
│  │ - SQLite     │  │ - Error logs │  │ - GDOT style │ │
│  │ - Job model  │  │ - Checkpoints│  │ - Templates  │ │
│  │ - Queries    │  │ - Audit trail│  │ - Fallbacks  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Presentation Layer

#### Streamlit UI (`app.py`)
- **Purpose**: Interactive dashboard for video generation
- **Key Features**:
  - Markdown input with live preview
  - Real-time progress tracking
  - Live Mermaid flowchart (11 nodes)
  - Video preview and download
  - Job history browser
  - Error log viewer
- **Updates**: Uses `st.rerun()` for polling (2s intervals)
- **Styling**: Custom CSS for GDOT professional theme

#### FastAPI (`api.py`)
- **Purpose**: RESTful API for programmatic access
- **Endpoints**:
  - `POST /generate`: Start video generation
  - `GET /jobs/{job_id}`: Get job status
  - `GET /jobs`: List all jobs
  - `GET /download/{job_id}`: Download video
  - `GET /jobs/{job_id}/errors`: Get error logs
  - `DELETE /jobs/{job_id}`: Delete job
  - `GET /health`: Health check
- **Features**:
  - Async/sync modes
  - Background tasks
  - Pydantic validation
  - Auto-generated docs (/docs)

### 2. Business Logic Layer

#### Workflow Engine (`workflow.py`)

**WorkflowContext Class**:
```python
class WorkflowContext:
    - job_id: str
    - md_content: str
    - work_dir: Path
    - Step outputs (summary, script, images, etc.)
    - tokens_used: dict
    - error_count: int
    - degraded_mode: bool
```

**Resilient Step Wrapper**:
```python
def resilient_step(
    step_no, step_name, func, ctx,
    max_retries=3, allow_fallback=True
) -> (success: bool, result: Any)
```

**Features**:
- **Retry Logic**: Exponential backoff (2^n seconds, max 30s)
- **Checkpointing**: JSON snapshots after each step
- **Rollback**: Restore previous checkpoint on failure
- **Fallback**: Degraded functionality when retries exhausted
- **Error Classification**: TOKEN_ERROR, SYNTAX_ERROR, NETWORK_ERROR, etc.

**Step Functions**:
Each step is a pure function: `def step_N_name(ctx: WorkflowContext) -> Any`

### 3. Data Layer

#### Database (`db.py`)

**Job Model**:
```python
class Job(Base):
    id: str (UUID primary key)
    md_content: TEXT
    status: str (pending, processing, done, error, degraded)
    output_path: str
    tokens: JSON
    errors: JSON (list)
    created_at: DateTime
    updated_at: DateTime
    completed_at: DateTime
    current_step: str
    steps_completed: JSON (list)
    summary: TEXT
    video_duration: str
    total_retries: str
    degraded_mode: str
```

**Key Functions**:
- `create_job()`, `get_job()`, `update_job()`
- `update_job_status()`, `add_job_error()`
- `increment_retry_count()`, `mark_step_complete()`
- `get_all_jobs()`, `get_jobs_by_status()`
- `delete_job()`

#### Logger (`logger.py`)

**Error Logging**:
```python
def log_error(
    job_id, step_no, error_type, details,
    retry_count=0, fallback_used=False,
    checkpoint_restored=None
)
```

Logs to: `data/errors.json`

**Checkpoint Management**:
```python
def save_checkpoint(job_id, step_no, data) -> path
def load_checkpoint(job_id, step_no) -> data
def cleanup_checkpoints(job_id)
```

Checkpoints: `data/checkpoints/{job_id}_step_{N}.json`

**Logging Levels**:
- `log_info()`: General progress
- `log_success()`: Step completion
- `log_warning()`: Non-fatal issues
- `log_error()`: Failures and retries

#### Prompts (`prompts.py`)

**System Prompt**:
- GDOT-DOT professional tone
- Target audience: DOT contractors/engineers
- Focus: Technical clarity, safety, compliance

**Prompt Templates**:
- Summary generation
- Base script generation
- Image/layout suggestions
- Narration generation

**Fallbacks**:
- Default summary
- Base Manim template
- Default narration template

## Data Flow

### Typical Workflow Execution

```
1. User Input
   └─> Markdown content entered in UI

2. Job Creation
   └─> UUID generated, saved to DB (status: pending)

3. Workflow Execution (11 steps)
   ├─> Each step wrapped in resilient_step()
   ├─> Try execution
   │   ├─> Success? Save checkpoint, continue
   │   └─> Failure?
   │       ├─> Log error to errors.json
   │       ├─> Increment retry counter
   │       ├─> Exponential backoff sleep
   │       ├─> Load previous checkpoint
   │       ├─> Retry (up to 3 times)
   │       └─> Still failing?
   │           ├─> Try fallback
   │           └─> Mark degraded if >5 errors
   └─> Update DB after each step

4. Video Generation
   ├─> Manim renders animation
   ├─> edge-tts generates audio
   └─> MoviePy merges to final.mp4

5. Completion
   ├─> Status: done or degraded
   ├─> output_path: ./data/outputs/{job_id}.mp4
   ├─> Cleanup checkpoints
   └─> Update DB with metadata
```

### Error Handling Flow

```
Exception Raised
    ↓
Classify Error Type
    ↓
Log to errors.json
    ↓
Retry < max_retries?
    ├─> Yes: Exponential backoff → Retry
    └─> No: Fallback available?
        ├─> Yes: Use fallback → Continue (degraded)
        └─> No: Mark step failed → Abort workflow
```

## File System Structure

```
coursemaker/
├── app.py                  # Streamlit entry point
├── api.py                  # FastAPI server
├── workflow.py             # 11-step engine
├── prompts.py              # GDOT prompts
├── db.py                   # SQLAlchemy models
├── logger.py               # Error logging
├── requirements.txt        # Dependencies
├── setup.py               # Installation helper
├── run.py                 # Launcher script
├── test_installation.py   # Verification tests
├── .env                   # Config (not in git)
├── env.example            # Config template
└── data/                  # Runtime data (not in git)
    ├── md_videos.db       # SQLite database
    ├── errors.json        # Error logs
    ├── checkpoints/       # Step checkpoints
    │   └── {job_id}_step_{N}.json
    ├── work/              # Temporary files
    │   └── {job_id}/
    │       ├── input.md
    │       ├── summary.txt
    │       ├── base_script.py
    │       ├── enhanced_script.py
    │       ├── timings.json
    │       ├── images.json
    │       ├── layouts.json
    │       ├── narration.json
    │       ├── silent_video.mp4
    │       ├── full_audio.mp3
    │       ├── temp_images/
    │       ├── audio_clips/
    │       └── media/       # Manim output
    └── outputs/            # Final videos
        └── {job_id}.mp4
```

## Configuration

### Environment Variables (`.env`)

```env
# Required
GROQ_API_KEY=gsk_...        # Groq LLM API key

# Optional
SERPAPI_KEY=...             # Image search (fallback: shapes)

# Paths
MANIM_PATH=manim            # Manim executable
EDGE_TTS_VOICE=en-US-GuyNeural  # TTS voice
DB_PATH=./data/md_videos.db
CHECKPOINT_DIR=./data/checkpoints
LOGS_PATH=./data/errors.json

# Resilience Settings
MAX_RETRIES_PER_STEP=3      # Per-step retry limit
MAX_TOTAL_RETRIES=10        # Total retry limit per job
ERROR_THRESHOLD_DEGRADED=5  # Errors before degraded mode
```

## Resilience Features

### 1. Per-Step Retries
- Max 3 attempts per step
- Exponential backoff: 2^n seconds (max 30s)
- Different retry limits per step based on criticality

### 2. Checkpointing
- JSON snapshot after each successful step
- Includes step output and context state
- Enables rollback and recovery

### 3. Rollback
- On failure, load previous checkpoint
- Restore context state
- Retry from known-good state

### 4. Fallbacks
- **Step 2 (Summary)**: Generic GDOT summary
- **Step 3 (Script)**: Base template with placeholder
- **Step 4 (Images)**: Empty list, skip images
- **Step 5 (Fetch)**: Empty list, use shapes
- **Step 7 (Render)**: Low-quality mode
- **Step 8 (Narration)**: Template-based text
- **Step 9 (Audio)**: Silence clips
- **Step 10 (Merge)**: Silent video only

### 5. Degraded Mode
- Triggered when error_count > 5
- Continues workflow with fallbacks
- Final status: "degraded" (not "done")
- Video still generated but may lack features

### 6. Error Logging
- All errors logged to `errors.json`
- Schema: `{job_id, step_no, error_type, details, timestamp, retry_count, fallback_used}`
- Viewable in UI sidebar or via API

### 7. Total Retry Limit
- Maximum 10 retries across entire workflow
- Prevents infinite retry loops
- Aborts workflow if exceeded

## API Integration

### Groq API (Required)
- **Model**: mixtral-8x7b-32768
- **Usage**: Steps 2, 3, 4, 8 (text generation)
- **Rate Limits**: Handled by retry logic
- **Token Tracking**: Logged to database

### SerpAPI (Optional)
- **Usage**: Step 5 (image search)
- **Fallback**: Skip images, use geometric shapes
- **Rate Limiting**: 1s delay between requests

### Manim (Local)
- **Usage**: Step 7 (video rendering)
- **Fallback**: Low-quality mode (-ql)
- **Output**: 1080p MP4 (or 480p fallback)

### edge-tts (Local/Cloud)
- **Usage**: Step 9 (text-to-speech)
- **Voice**: Configurable (default: en-US-GuyNeural)
- **Fallback**: Silence clips

## Performance Considerations

### Typical Execution Time
- Simple MD (500 words): 2-3 minutes
- Medium MD (1000 words): 3-5 minutes
- Complex MD (2000 words): 5-10 minutes

### Bottlenecks
1. **LLM API calls** (Steps 2,3,4,8): ~10-30s each
2. **Manim rendering** (Step 7): ~30-120s
3. **TTS generation** (Step 9): ~10-20s

### Optimization Strategies
- **Caching**: Checkpoint system avoids re-running steps
- **Parallel processing**: Could parallelize LLM calls (future)
- **Quality settings**: Low-res fallback for faster iteration
- **Content limits**: Truncate >10k chars to prevent timeouts

## Security Considerations

### API Keys
- Stored in `.env` (not in git)
- Validated on startup
- Never exposed in logs or UI

### File Safety
- All paths use `pathlib` for safety
- Work directories isolated per job
- Subprocess calls with timeout limits
- No user-provided code execution (Manim scripts are LLM-generated, not user-provided)

### Database
- Local SQLite (no network exposure)
- SQL injection prevented by SQLAlchemy ORM
- No sensitive data stored

### Input Validation
- Markdown content length limits
- UUID format validation
- Pydantic models for API requests

## Monitoring & Observability

### Logs
- **Python logging**: `app.log` (INFO level)
- **Error JSON**: `data/errors.json` (structured)
- **Checkpoints**: `data/checkpoints/*.json` (state)

### Metrics Tracked
- Tokens used (per step, total)
- Error count (per job)
- Retry count (per job)
- Video duration
- Processing time (timestamps)

### UI Indicators
- Live flowchart (11 nodes, color-coded)
- Progress bar (0-100%)
- Status badges (done, processing, error, degraded)
- Error count warnings

## Testing & Debugging

### Test Installation
```bash
python test_installation.py
```

Checks:
- Python version (3.10+)
- All Python packages
- FFmpeg availability
- Manim CLI
- .env configuration
- Directory structure
- Basic functionality

### Manual Testing
1. Load sample Markdown
2. Generate video
3. Watch flowchart
4. Check error logs
5. Download video

### Debug Mode
- Check `app.log` for detailed logs
- Inspect `data/work/{job_id}/` for intermediate files
- View `data/errors.json` for error details
- Query database for job status

## Deployment Considerations

### Local Development
```bash
streamlit run app.py
```

### Production (Server)
```bash
# Streamlit (single user)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# FastAPI (multi-user API)
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Future)
- Dockerfile with Python 3.10, FFmpeg, Manim
- Volume mounts for `data/` directory
- Environment variables from `.env`

### Scaling Considerations
- **Concurrent jobs**: Currently sequential (one at a time per user)
- **Queue system**: Could add Celery/RQ for job queue
- **Distributed**: Could split LLM/rendering to separate workers
- **Database**: Could upgrade to PostgreSQL for multi-user

## Future Enhancements

### Planned Features
- [ ] Multiple output formats (WebM, GIF)
- [ ] Custom voice selection
- [ ] Parallel step execution (where possible)
- [ ] Video template customization
- [ ] Real-time collaboration
- [ ] Cloud deployment guide
- [ ] Docker containerization
- [ ] Job queue system (Celery)
- [ ] WebSocket for true real-time updates
- [ ] Advanced Manim scene generation
- [ ] Multi-language support
- [ ] Video preview before final render

### Known Limitations
- Single job execution per user session
- Manim script generation quality varies
- Image search requires SerpAPI (paid)
- No video editing after generation
- Limited customization options

## Troubleshooting

### Common Issues

1. **"Groq API Key missing"**
   - Add `GROQ_API_KEY` to `.env`

2. **"Manim not found"**
   - `pip install manim`
   - Verify: `manim --version`

3. **"FFmpeg error"**
   - Install FFmpeg for your OS
   - Add to PATH

4. **"Render timeout"**
   - Reduce content length
   - Use low-quality mode

5. **"Too many retries"**
   - Check API key validity
   - Check network connection
   - Simplify markdown content

## Support & Contribution

### Getting Help
- Check QUICKSTART.md for setup
- Review ARCHITECTURE.md (this file)
- Inspect logs: `app.log`, `errors.json`
- Test installation: `python test_installation.py`

### Contributing
- Follow existing code style
- Add tests for new features
- Update documentation
- Check linting: No errors reported

## License

MIT License - See LICENSE file for details.

