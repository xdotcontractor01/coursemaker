"""
FastAPI endpoints for GDOT Educational Video Generator.
Optional API interface for programmatic access.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import uuid
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import modules
from workflow import run_workflow
from db import (
    create_job, get_job, get_all_jobs, get_jobs_by_status,
    update_job_status, create_tables
)
from logger import get_job_errors, ensure_logs_dir

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="GDOT Video Generator API",
    description="Convert Markdown to educational videos with AI",
    version="1.0.0"
)

# Ensure database and logs initialized
create_tables()
ensure_logs_dir()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GenerateVideoRequest(BaseModel):
    """Request model for video generation."""
    markdown_content: str = Field(..., min_length=10, description="Markdown content to convert")
    job_id: Optional[str] = Field(None, description="Optional custom job ID (UUID)")
    async_mode: bool = Field(True, description="Run asynchronously in background")


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    current_step: str
    steps_completed: List[int]
    created_at: Optional[str]
    completed_at: Optional[str]
    output_path: Optional[str]
    video_duration: Optional[str]
    tokens_used: Dict[str, Any]
    total_retries: str
    degraded_mode: str
    errors: List[Dict[str, Any]]
    summary: Optional[str]


class JobListResponse(BaseModel):
    """Response model for job list."""
    total: int
    jobs: List[JobStatusResponse]


class GenerateVideoResponse(BaseModel):
    """Response model for generate endpoint."""
    job_id: str
    status: str
    message: str


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    details: Optional[str] = None


# ============================================================================
# BACKGROUND TASK
# ============================================================================

def run_workflow_background(job_id: str, md_content: str):
    """Background task to run workflow."""
    try:
        result = run_workflow(job_id, md_content)
        return result
    except Exception as e:
        update_job_status(job_id, 'error')
        from logger import log_error
        log_error(job_id, -1, 'WORKFLOW_ERROR', str(e), retry_count=0, fallback_used=False)
        return {
            'status': 'error',
            'message': str(e),
            'output_path': None
        }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "GDOT Video Generator API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/generate",
            "job_status": "/jobs/{job_id}",
            "list_jobs": "/jobs",
            "download": "/download/{job_id}",
            "errors": "/jobs/{job_id}/errors"
        }
    }


@app.post("/generate", response_model=GenerateVideoResponse)
async def generate_video(
    request: GenerateVideoRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate educational video from Markdown content.
    
    Args:
        request: GenerateVideoRequest with markdown content
        background_tasks: FastAPI background tasks
    
    Returns:
        GenerateVideoResponse with job_id and status
    """
    # Validate OpenAI API key (required)
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured. Check .env file. Get key from: https://platform.openai.com/api-keys"
        )
    
    # Generate or use provided job_id
    job_id = request.job_id or str(uuid.uuid4())
    
    try:
        # Validate UUID format if provided
        if request.job_id:
            uuid.UUID(request.job_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid job_id format. Must be valid UUID."
        )
    
    # Create job in database
    try:
        create_job(job_id, request.markdown_content, status='pending')
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create job: {str(e)}"
        )
    
    # Run workflow
    if request.async_mode:
        # Background processing
        background_tasks.add_task(run_workflow_background, job_id, request.markdown_content)
        
        return GenerateVideoResponse(
            job_id=job_id,
            status="pending",
            message="Video generation started. Check status at /jobs/{job_id}"
        )
    else:
        # Synchronous processing (blocking)
        update_job_status(job_id, 'processing')
        
        try:
            result = run_workflow(job_id, request.markdown_content)
            
            return GenerateVideoResponse(
                job_id=job_id,
                status=result['status'],
                message=result.get('message', 'Completed')
            )
        except Exception as e:
            update_job_status(job_id, 'error')
            raise HTTPException(
                status_code=500,
                detail=f"Workflow failed: {str(e)}"
            )


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status and details of a specific job.
    
    Args:
        job_id: Job UUID
    
    Returns:
        JobStatusResponse with job details
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    # Get errors
    errors = get_job_errors(job_id)
    
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        current_step=job.current_step or '0',
        steps_completed=job.steps_completed if isinstance(job.steps_completed, list) else [],
        created_at=job.created_at.isoformat() if job.created_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        output_path=job.output_path,
        video_duration=job.video_duration,
        tokens_used=job.tokens if isinstance(job.tokens, dict) else {},
        total_retries=job.total_retries or '0',
        degraded_mode=job.degraded_mode or 'false',
        errors=errors,
        summary=job.summary
    )


@app.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List all jobs or filter by status.
    
    Args:
        status: Optional status filter (pending, processing, done, error, degraded)
        limit: Maximum number of jobs to return (default 50)
    
    Returns:
        JobListResponse with list of jobs
    """
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )
    
    if status:
        jobs = get_jobs_by_status(status, limit=limit)
    else:
        jobs = get_all_jobs(limit=limit)
    
    job_responses = []
    
    for job in jobs:
        errors = get_job_errors(job.id)
        
        job_responses.append(JobStatusResponse(
            job_id=job.id,
            status=job.status,
            current_step=job.current_step or '0',
            steps_completed=job.steps_completed if isinstance(job.steps_completed, list) else [],
            created_at=job.created_at.isoformat() if job.created_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            output_path=job.output_path,
            video_duration=job.video_duration,
            tokens_used=job.tokens if isinstance(job.tokens, dict) else {},
            total_retries=job.total_retries or '0',
            degraded_mode=job.degraded_mode or 'false',
            errors=errors,
            summary=job.summary
        ))
    
    return JobListResponse(
        total=len(job_responses),
        jobs=job_responses
    )


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """
    Download generated video file.
    
    Args:
        job_id: Job UUID
    
    Returns:
        FileResponse with MP4 video
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    if job.status not in ['done', 'degraded']:
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} not completed yet. Current status: {job.status}"
        )
    
    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found for job {job_id}"
        )
    
    return FileResponse(
        job.output_path,
        media_type="video/mp4",
        filename=f"gdot_video_{job_id[:8]}.mp4"
    )


@app.get("/jobs/{job_id}/errors")
async def get_job_error_log(job_id: str):
    """
    Get detailed error log for a specific job.
    
    Args:
        job_id: Job UUID
    
    Returns:
        JSON array of error entries
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    errors = get_job_errors(job_id)
    
    return {
        "job_id": job_id,
        "total_errors": len(errors),
        "errors": errors
    }


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its associated files.
    
    Args:
        job_id: Job UUID
    
    Returns:
        Success message
    """
    from db import delete_job as db_delete_job
    import shutil
    
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    # Delete work directory
    work_dir = Path('./data/work') / job_id
    if work_dir.exists():
        shutil.rmtree(work_dir)
    
    # Delete output file
    if job.output_path and os.path.exists(job.output_path):
        os.remove(job.output_path)
    
    # Delete from database
    db_delete_job(job_id)
    
    return {
        "message": f"Job {job_id} deleted successfully"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "llm_provider": "openai",
        "openai_api_configured": bool(os.getenv('OPENAI_API_KEY')),
        "serpapi_configured": bool(os.getenv('SERPAPI_KEY'))
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "details": str(exc.detail if hasattr(exc, 'detail') else '')}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("🚀 GDOT Video Generator API started")
    print(f"📊 Database: {os.getenv('DB_PATH', './data/md_videos.db')}")
    print(f"🤖 LLM Provider: OpenAI (GPT-4o-mini)")
    print(f"🔑 OpenAI API: {'✓ Configured' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}")
    print(f"🔑 SerpAPI: {'✓ Configured' if os.getenv('SERPAPI_KEY') else '✗ Missing (optional)'}")
    
    # Ensure directories exist
    Path('./data/work').mkdir(parents=True, exist_ok=True)
    Path('./data/outputs').mkdir(parents=True, exist_ok=True)
    Path('./data/checkpoints').mkdir(parents=True, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 GDOT Video Generator API shutting down")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

