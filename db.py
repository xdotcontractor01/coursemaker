"""
SQLAlchemy database models and utilities for job management.
Uses SQLite for local storage of job history and status.
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DB_PATH = os.getenv('DB_PATH', './data/md_videos.db')

# Ensure database directory exists
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# SQLAlchemy setup
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Job(Base):
    """Job model for tracking video generation tasks."""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    md_content = Column(Text, nullable=False)
    status = Column(String, default='pending')  # pending, processing, done, error, degraded
    output_path = Column(String, nullable=True)
    tokens = Column(JSON, default=dict)  # Token usage tracking
    errors = Column(JSON, default=list)  # List of error summaries
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Workflow progress
    current_step = Column(String, default='0')
    steps_completed = Column(JSON, default=list)
    
    # Additional metadata
    summary = Column(Text, nullable=True)
    video_duration = Column(String, nullable=True)
    total_retries = Column(String, default='0')
    degraded_mode = Column(String, default='false')  # 'true' or 'false' as string

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return {
            'id': self.id,
            'status': self.status,
            'output_path': self.output_path,
            'tokens': self.tokens if isinstance(self.tokens, dict) else {},
            'errors': self.errors if isinstance(self.errors, list) else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'current_step': self.current_step,
            'steps_completed': self.steps_completed if isinstance(self.steps_completed, list) else [],
            'summary': self.summary,
            'video_duration': self.video_duration,
            'total_retries': self.total_retries,
            'degraded_mode': self.degraded_mode
        }


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let caller handle it


def create_job(
    job_id: str,
    md_content: str,
    status: str = 'pending'
) -> Job:
    """
    Create a new job in the database.
    
    Args:
        job_id: Unique job identifier (UUID)
        md_content: Markdown input content
        status: Initial status
    
    Returns:
        Created Job object
    """
    db = get_db()
    try:
        job = Job(
            id=job_id,
            md_content=md_content,
            status=status,
            tokens={},
            errors=[],
            steps_completed=[],
            current_step='0',
            total_retries='0',
            degraded_mode='false'
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


def get_job(job_id: str) -> Optional[Job]:
    """
    Retrieve job by ID.
    
    Args:
        job_id: Unique job identifier
    
    Returns:
        Job object or None if not found
    """
    db = get_db()
    try:
        return db.query(Job).filter(Job.id == job_id).first()
    finally:
        db.close()


def update_job(
    job_id: str,
    **kwargs
) -> Optional[Job]:
    """
    Update job fields.
    
    Args:
        job_id: Unique job identifier
        **kwargs: Fields to update
    
    Returns:
        Updated Job object or None if not found
    """
    db = get_db()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


def update_job_status(
    job_id: str,
    status: str,
    current_step: Optional[str] = None
) -> Optional[Job]:
    """
    Update job status and optionally current step.
    
    Args:
        job_id: Unique job identifier
        status: New status
        current_step: Current workflow step
    
    Returns:
        Updated Job object or None if not found
    """
    update_data = {'status': status}
    if current_step is not None:
        update_data['current_step'] = current_step
    
    if status in ['done', 'error', 'degraded']:
        update_data['completed_at'] = datetime.utcnow()
    
    return update_job(job_id, **update_data)


def add_job_error(job_id: str, error_summary: str) -> None:
    """
    Add error summary to job errors list.
    
    Args:
        job_id: Unique job identifier
        error_summary: Brief error description
    """
    db = get_db()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            errors = job.errors if isinstance(job.errors, list) else []
            errors.append({
                'message': error_summary,
                'timestamp': datetime.utcnow().isoformat()
            })
            job.errors = errors
            db.commit()
    finally:
        db.close()


def increment_retry_count(job_id: str) -> None:
    """Increment total retry count for job."""
    db = get_db()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            current = int(job.total_retries or '0')
            job.total_retries = str(current + 1)
            db.commit()
    finally:
        db.close()


def mark_step_complete(job_id: str, step_no: int) -> None:
    """
    Mark a workflow step as completed.
    
    Args:
        job_id: Unique job identifier
        step_no: Step number (0-10)
    """
    db = get_db()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            steps = job.steps_completed if isinstance(job.steps_completed, list) else []
            if step_no not in steps:
                steps.append(step_no)
            job.steps_completed = steps
            job.current_step = str(step_no)
            db.commit()
    finally:
        db.close()


def get_all_jobs(limit: int = 50) -> List[Job]:
    """
    Get all jobs ordered by creation date (newest first).
    
    Args:
        limit: Maximum number of jobs to return
    
    Returns:
        List of Job objects
    """
    db = get_db()
    try:
        return db.query(Job).order_by(Job.created_at.desc()).limit(limit).all()
    finally:
        db.close()


def get_jobs_by_status(status: str, limit: int = 50) -> List[Job]:
    """
    Get jobs filtered by status.
    
    Args:
        status: Status to filter by
        limit: Maximum number of jobs to return
    
    Returns:
        List of Job objects
    """
    db = get_db()
    try:
        return db.query(Job).filter(Job.status == status).order_by(
            Job.created_at.desc()
        ).limit(limit).all()
    finally:
        db.close()


def delete_job(job_id: str) -> bool:
    """
    Delete a job from database.
    
    Args:
        job_id: Unique job identifier
    
    Returns:
        True if deleted, False if not found
    """
    db = get_db()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            db.delete(job)
            db.commit()
            return True
        return False
    finally:
        db.close()


# Initialize database on import
create_tables()






