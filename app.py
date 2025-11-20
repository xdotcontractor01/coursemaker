"""
Streamlit UI for GDOT Educational Video Generator.
Real-time updates with Mermaid flowchart and job history.
"""

import streamlit as st
import os
import json
import uuid
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import threading

# Import modules
from workflow import run_workflow
from db import (
    create_job, get_job, get_all_jobs, update_job_status,
    create_tables
)
from logger import get_job_errors, ensure_logs_dir

load_dotenv()

# Page config
st.set_page_config(
    page_title="GDOT Video Generator",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for DOT professional theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #003366;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-complete {
        color: #28a745;
        font-weight: bold;
    }
    .step-error {
        color: #dc3545;
        font-weight: bold;
    }
    .step-pending {
        color: #6c757d;
    }
    .mermaid-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.875rem;
    }
    .status-done {
        background: #d4edda;
        color: #155724;
    }
    .status-processing {
        background: #d1ecf1;
        color: #0c5460;
    }
    .status-error {
        background: #f8d7da;
        color: #721c24;
    }
    .status-degraded {
        background: #fff3cd;
        color: #856404;
    }
    .flowchart-wrapper {
        overflow-x: auto;
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
create_tables()
ensure_logs_dir()

# Cleanup orphaned MoviePy temp files on startup
def cleanup_temp_files():
    """Remove any orphaned MoviePy temporary files"""
    import glob
    try:
        for temp_file in glob.glob("*TEMP_MPY*.mp4"):
            try:
                os.remove(temp_file)
                print(f"Cleaned up orphaned temp file: {temp_file}")
            except Exception as e:
                print(f"Could not remove temp file {temp_file}: {e}")
    except Exception as e:
        print(f"Cleanup error: {e}")

cleanup_temp_files()

# Session state initialization
if 'workflow_running' not in st.session_state:
    st.session_state.workflow_running = False
if 'current_job_id' not in st.session_state:
    st.session_state.current_job_id = None
if 'md_input' not in st.session_state:
    st.session_state.md_input = ''
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# Sample GDOT markdown
SAMPLE_MD = """# Bridge Inspection Guidelines

## Introduction
This guide covers essential bridge inspection procedures for GDOT contractors and engineers.

## Safety Requirements
- Always wear proper PPE (hard hat, safety vest, steel-toed boots)
- Establish traffic control zones per MUTCD standards
- Use fall protection equipment when working at heights >6 feet

## Inspection Process

### Visual Assessment
Inspect all structural components for:
- Cracks and spalling in concrete
- Corrosion on steel members
- Deterioration of bearings and expansion joints

### Documentation
- Take photos of all defects
- Record measurements accurately
- Complete inspection forms per GDOT standards

### Reporting
Submit reports within 48 hours including:
- Executive summary
- Detailed findings
- Recommended repairs
- Cost estimates

## Conclusion
Regular bridge inspections ensure public safety and extend structure lifespan. Follow all GDOT protocols and maintain thorough documentation.
"""


def generate_mermaid_flowchart(current_step: int, status: str, error_steps: list = None) -> str:
    """
    Generate Mermaid flowchart showing workflow progress.
    
    Args:
        current_step: Current step number (0-10)
        status: Job status
        error_steps: List of steps with errors
    
    Returns:
        Mermaid diagram string
    """
    error_steps = error_steps or []
    
    steps = [
        "Load Prompts",
        "Validate Input",
        "Generate Summary",
        "Base Script",
        "Image Suggestions",
        "Fetch Images",
        "Inject Images",
        "Render Video",
        "Narration",
        "Generate Audio",
        "Merge & Finalize"
    ]
    
    mermaid = "```mermaid\ngraph TD\n"
    
    for i, step_name in enumerate(steps):
        node_id = f"S{i}"
        
        # Determine node style
        if i < current_step or (status in ['done', 'degraded'] and i <= 10):
            if i in error_steps:
                style = "fill:#ffcccc,stroke:#cc0000,stroke-width:2px"
                icon = "❌"
            else:
                style = "fill:#ccffcc,stroke:#00cc00,stroke-width:2px"
                icon = "✓"
        elif i == current_step and status == 'processing':
            style = "fill:#ffffcc,stroke:#ffcc00,stroke-width:3px"
            icon = "⏳"
        else:
            style = "fill:#f0f0f0,stroke:#cccccc,stroke-width:1px"
            icon = "○"
        
        mermaid += f'    {node_id}["{icon} {i}: {step_name}"]:::{f"step{i}"}\n'
        mermaid += f'    style {node_id} {style}\n'
        
        # Add connections
        if i < len(steps) - 1:
            mermaid += f'    {node_id} --> S{i+1}\n'
    
    mermaid += "```"
    return mermaid


def run_workflow_thread(job_id: str, md_content: str):
    """Run workflow in background thread."""
    try:
        result = run_workflow(job_id, md_content)
        st.session_state.workflow_result = result
    except Exception as e:
        st.session_state.workflow_result = {
            'status': 'error',
            'message': str(e),
            'output_path': None
        }
    finally:
        st.session_state.workflow_running = False


def format_status_badge(status: str) -> str:
    """Format status as HTML badge."""
    status_classes = {
        'done': 'status-done',
        'processing': 'status-processing',
        'error': 'status-error',
        'degraded': 'status-degraded',
        'pending': 'status-processing'
    }
    
    status_display = status.upper()
    css_class = status_classes.get(status, 'status-processing')
    
    return f'<span class="status-badge {css_class}">{status_display}</span>'


# ============================================================================
# MAIN UI
# ============================================================================

# Header
st.markdown('<div class="main-header">🎥 xDOT Video Generator</div>', unsafe_allow_html=True)

st.markdown("""
Convert Markdown documentation into professional educational videos with AI-powered narration and visuals.
Designed for GDOT contractors and engineers.
""")

# Sidebar - Configuration & History
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check environment
    llm_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
    openai_key = os.getenv('OPENAI_API_KEY', '')
    serpapi_key = os.getenv('SERPAPI_KEY', '')
    
    st.info(f"🤖 LLM Provider: **{llm_provider.upper()}**")
    
    # Check OpenAI (primary/required)
    if openai_key:
        st.success("✓ OpenAI API Key configured")
    else:
        st.error("✗ OpenAI API Key missing")
        st.caption("Add OPENAI_API_KEY to .env file")
        st.caption("Get key from: https://platform.openai.com/api-keys")
    
    # SerpAPI (optional)
    if serpapi_key:
        st.success("✓ SerpAPI Key configured")
    else:
        st.warning("⚠ SerpAPI Key missing (images disabled)")
    
    st.divider()
    
    # Job History
    st.header("📋 Job History")
    
    jobs = get_all_jobs(limit=10)
    
    if jobs:
        for job in jobs:
            with st.expander(f"Job {job.id[:8]}... - {job.status}"):
                st.markdown(f"**Status:** {format_status_badge(job.status)}", unsafe_allow_html=True)
                st.caption(f"Created: {job.created_at.strftime('%Y-%m-%d %H:%M:%S') if job.created_at else 'Unknown'}")
                
                if job.output_path and os.path.exists(job.output_path):
                    with open(job.output_path, 'rb') as f:
                        st.download_button(
                            "⬇️ Download Video",
                            f,
                            file_name=f"{job.id}.mp4",
                            mime="video/mp4",
                            key=f"download_{job.id}"
                        )
                
                if job.summary:
                    st.caption(f"Summary: {job.summary[:100]}...")
                
                # Show errors
                errors = get_job_errors(job.id)
                if errors:
                    st.warning(f"Errors: {len(errors)}")
                    if st.button("View Errors", key=f"errors_{job.id}"):
                        st.json(errors)
    else:
        st.info("No jobs yet. Create your first video!")
    
    st.divider()
    
    # Error Log Viewer
    if st.button("🔍 View All Error Logs"):
        st.session_state.show_all_errors = True

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📝 Markdown Input")
    
    # Sample and Clear buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📄 Load Sample GDOT Markdown"):
            st.session_state.md_input = SAMPLE_MD
            st.rerun()
    
    with col_btn2:
        if st.button("🗑️ Clear Input"):
            st.session_state.md_input = ""
            st.session_state.current_job_id = None
            st.rerun()
    
    # Markdown input
    md_input = st.text_area(
        "Paste your Markdown content:",
        value=st.session_state.get('md_input', ''),
        height=300,
        placeholder="Enter or paste Markdown documentation here...",
        key="md_textarea"
    )
    
    # Preview
    if md_input:
        with st.expander("👁️ Markdown Preview"):
            st.markdown(md_input)
    
    # Summary Preview Section
    if st.session_state.get('current_job_id'):
        job = get_job(st.session_state.current_job_id)
        if job:
            summary_file = Path(f'./data/work/{job.id}/summary.txt')
            if summary_file.exists():
                with st.expander("📋 Video Summary Preview", expanded=True):
                    summary_text = summary_file.read_text(encoding='utf-8')
                    # Parse into bullets
                    st.markdown("**Topics Covered:**")
                    for line in summary_text.split('.'):
                        line = line.strip()
                        if line and len(line) > 5:  # Skip very short fragments
                            st.markdown(f"• {line}")

with col2:
    st.header("🎬 Generate Video")
    
    # Validation
    has_openai_key = bool(os.getenv('OPENAI_API_KEY', ''))
    
    can_generate = (
        md_input and 
        len(md_input) > 10 and 
        has_openai_key and 
        not st.session_state.workflow_running
    )
    
    if not has_openai_key:
        st.error("⚠️ Cannot generate: OpenAI API key not configured")
        st.caption("Add OPENAI_API_KEY to .env file")
        st.caption("Get key from: https://platform.openai.com/api-keys")
    
    # Generate button
    if st.button(
        "🚀 Generate Video",
        type="primary",
        disabled=not can_generate,
        use_container_width=True
    ):
        # Create new job
        job_id = str(uuid.uuid4())
        create_job(job_id, md_input, status='pending')
        
        st.session_state.current_job_id = job_id
        st.session_state.workflow_running = True
        st.session_state.workflow_result = None
        
        # Start workflow in thread
        thread = threading.Thread(
            target=run_workflow_thread,
            args=(job_id, md_input),
            daemon=True
        )
        thread.start()
        
        st.rerun()

# ============================================================================
# WORKFLOW PROGRESS DISPLAY
# ============================================================================

if st.session_state.current_job_id:
    st.divider()
    st.header("⚡ Workflow Progress")
    
    job_id = st.session_state.current_job_id
    job = get_job(job_id)
    
    if job:
        # Status and progress
        col_status, col_progress = st.columns([1, 3])
        
        with col_status:
            st.markdown(f"**Job ID:** `{job_id[:8]}...`")
            st.markdown(f"**Status:** {format_status_badge(job.status)}", unsafe_allow_html=True)
            
            if job.total_retries and int(job.total_retries) > 0:
                st.warning(f"⚠️ Retries: {job.total_retries}")
        
        with col_progress:
            # Progress bar
            current_step = int(job.current_step or 0)
            progress = min((current_step + 1) / 11, 1.0)
            
            st.progress(progress, text=f"Step {current_step + 1} of 11")
            
            # Time estimate
            if job.created_at and job.status == 'processing':
                elapsed = (datetime.utcnow() - job.created_at).total_seconds()
                st.caption(f"⏱️ Elapsed: {int(elapsed)}s")
        
        # Flowchart
        st.subheader("📊 Workflow Flowchart")
        
        # Get error steps
        job_errors = get_job_errors(job_id)
        error_steps = list(set([err.get('step_no', -1) for err in job_errors if err.get('step_no', -1) >= 0]))
        
        mermaid_chart = generate_mermaid_flowchart(current_step, job.status, error_steps)
        
        st.markdown('<div class="flowchart-wrapper">', unsafe_allow_html=True)
        st.markdown(mermaid_chart)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Script viewer (if available)
        work_dir = Path('./data/work') / job_id
        script_file = work_dir / 'base_script.py'
        
        if script_file.exists():
            with st.expander("🐍 View Generated Script"):
                with open(script_file, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                st.code(script_content, language='python')
        
        # Live media preview
        with st.expander("🎬 Live Media Preview", expanded=True):
            # Images section
            images_dir = Path(f'./data/work/{job_id}/temp_images')
            if images_dir.exists():
                st.subheader("Images Fetched:")
                image_files = list(images_dir.glob('*.png'))
                if image_files:
                    cols = st.columns(min(len(image_files), 3))
                    for idx, img_file in enumerate(image_files):
                        with cols[idx % 3]:
                            st.image(str(img_file), caption=img_file.name, width=200)
                else:
                    st.caption("No images yet...")
            else:
                st.caption("Waiting for image fetch step...")
            
            # Audio section
            audio_clips_dir = Path(f'./data/work/{job_id}/audio_clips')
            if audio_clips_dir.exists():
                st.subheader("Audio Status:")
                clips = list(audio_clips_dir.glob('clip_*.mp3'))
                narration_file = Path(f'./data/work/{job_id}/narration.json')
                if narration_file.exists():
                    with open(narration_file, 'r', encoding='utf-8') as f:
                        narrations = json.load(f)
                        total_clips = len(narrations)
                        generated_clips = len(clips)
                        if total_clips > 0:
                            st.progress(generated_clips / total_clips)
                            st.caption(f"Generating clip {generated_clips}/{total_clips}...")
                            
                            # Show total duration when done
                            if generated_clips == total_clips:
                                total_dur = sum(n.get('duration', 0) for n in narrations)
                                mins = int(total_dur // 60)
                                secs = int(total_dur % 60)
                                st.success(f"✅ All clips ready, total duration: {mins}m {secs}s")
                else:
                    st.caption("Waiting for narration generation...")
            else:
                st.caption("Waiting for audio generation step...")
        
        # Error display
        if job_errors:
            with st.expander(f"⚠️ Errors ({len(job_errors)})", expanded=True):
                st.json(job_errors)
        
        # Video preview (if done)
        if job.status in ['done', 'degraded'] and job.output_path:
            if os.path.exists(job.output_path):
                st.divider()
                st.header("🎉 Video Ready!")
                
                if job.status == 'degraded':
                    st.warning("⚠️ Video completed in degraded mode (some features may be missing)")
                else:
                    st.success("✅ Video generated successfully!")
                
                # Show validation checklist
                st.subheader("✅ Validation Checklist")
                
                # Load checklist from job context if available
                checklist_file = Path(f'./data/work/{job_id}/checklist.json')
                if checklist_file.exists():
                    with open(checklist_file, 'r', encoding='utf-8') as f:
                        checks = json.load(f)
                else:
                    # Default checks
                    checks = {
                        'summarised': True, 'script_generated': True,
                        'images_identified': True, 'images_added': False,
                        'video_rendered': True, 'audio_generated': True,
                        'audio_integrated': True, 'aligned': True,
                        'video_ready': job.status == 'done'
                    }
                
                cols = st.columns(4)
                check_items = [
                    ('Summarised', 'summarised'),
                    ('Script Generated', 'script_generated'),
                    ('Images Added', 'images_added'),
                    ('Video Rendered', 'video_rendered'),
                    ('Audio Generated', 'audio_generated'),
                    ('Audio Integrated', 'audio_integrated'),
                    ('Duration Aligned', 'aligned'),
                    ('Video Ready', 'video_ready'),
                ]
                
                for idx, (label, key) in enumerate(check_items):
                    with cols[idx % 4]:
                        if checks.get(key, False):
                            st.success(f"✅ {label}")
                        else:
                            st.error(f"❌ {label}")
                
                if not checks.get('video_ready', False):
                    st.warning("⚠️ Degraded video - some features skipped")
                
                st.divider()
                
                # Video player
                st.video(job.output_path, format='video/mp4', start_time=0)
                
                # Download button below player
                with open(job.output_path, 'rb') as f:
                    st.download_button(
                        "⬇️ Download GDOT Video",
                        data=f,
                        file_name=f"gdot_training_{job_id[:8]}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                
                # Metadata
                col_meta1, col_meta2, col_meta3 = st.columns(3)
                
                with col_meta1:
                    if job.video_duration:
                        st.metric("Duration", f"{float(job.video_duration):.1f}s")
                
                with col_meta2:
                    tokens = job.tokens if isinstance(job.tokens, dict) else {}
                    st.metric("Tokens Used", tokens.get('total', 0))
                
                with col_meta3:
                    st.metric("Total Errors", len(job_errors))
                
                # Reset button
                if st.button("🔄 Generate Another Video"):
                    st.session_state.current_job_id = None
                    st.session_state.workflow_running = False
                    st.rerun()
            else:
                st.error("Video file not found")
        
        # Auto-refresh while processing (only during active job)
        if st.session_state.workflow_running and job.status == 'processing':
            time.sleep(2)
            st.rerun()

# ============================================================================
# ERROR LOG VIEWER
# ============================================================================

if st.session_state.get('show_all_errors', False):
    st.divider()
    st.header("🔍 All Error Logs")
    
    logs_path = os.getenv('LOGS_PATH', './data/errors.json')
    
    if os.path.exists(logs_path):
        with open(logs_path, 'r') as f:
            all_errors = json.load(f)
        
        if all_errors:
            st.json(all_errors)
        else:
            st.info("No errors logged yet")
    else:
        st.info("Error log file not found")
    
    if st.button("Close Error Logs"):
        st.session_state.show_all_errors = False
        st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.caption("🏗️ Built for GDOT Contractors")

with col_footer2:
    st.caption("🤖 Powered by OpenAI + Manim")

with col_footer3:
    st.caption("📊 SQLite Database")

# Help section
with st.expander("ℹ️ Help & Documentation"):
    st.markdown("""
    ### How to Use
    
    1. **Paste Markdown**: Enter your technical documentation in the text area
    2. **Generate**: Click "Generate Video" to start the workflow
    3. **Monitor**: Watch the live flowchart as each step completes
    4. **Download**: Once complete, preview and download your video
    
    ### Requirements
    
    - **Groq API Key**: For AI text generation (required)
    - **SerpAPI Key**: For image search (optional, falls back to shapes)
    - **Manim**: For video rendering (must be installed)
    - **FFmpeg**: Required by Manim and MoviePy
    
    ### Workflow Steps
    
    0. Load GDOT-DOT system prompts
    1. Validate and chunk markdown input
    2. Generate summary (Groq LLM)
    3. Generate Manim script (Groq LLM)
    4. Suggest images and layouts (Groq LLM)
    5. Fetch images from web (SerpAPI)
    6. Inject images into script
    7. Render silent video (Manim)
    8. Generate narration script (Groq LLM)
    9. Generate audio (edge-tts)
    10. Merge video and audio (MoviePy)
    
    ### Resilience Features
    
    - **Retries**: Each step retries up to 3 times with exponential backoff
    - **Checkpoints**: State saved after each successful step
    - **Rollback**: Restore previous checkpoint on failure
    - **Fallbacks**: Degraded functionality when steps fail (e.g., shapes instead of images)
    - **Error Logging**: Detailed error tracking to `errors.json`
    
    ### Status Indicators
    
    - **DONE**: ✅ Completed successfully
    - **DEGRADED**: ⚠️ Completed with fallbacks
    - **PROCESSING**: ⏳ Currently running
    - **ERROR**: ❌ Failed completely
    
    ### Troubleshooting
    
    - **"Groq API Key missing"**: Add `GROQ_API_KEY=your_key` to `.env` file
    - **"Manim not found"**: Install with `pip install manim`
    - **"FFmpeg error"**: Install FFmpeg for your system
    - **Long processing time**: Complex documents may take 5-10 minutes
    """)

# Auto-refresh indicator
if st.session_state.workflow_running:
    st.caption("🔄 Auto-refreshing...")

