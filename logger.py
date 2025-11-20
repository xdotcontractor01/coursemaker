"""
Error logging utilities for resilient workflow.
Logs errors to JSON file per job with detailed context.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

# Configure Python logging with rotation
log_handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=3  # Keep 3 backup files
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        log_handler,
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

LOGS_PATH = os.getenv('LOGS_PATH', './data/errors.json')

def ensure_logs_dir():
    """Ensure logs directory exists."""
    Path(LOGS_PATH).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(LOGS_PATH):
        with open(LOGS_PATH, 'w') as f:
            json.dump([], f)

def log_error(
    job_id: str,
    step_no: int,
    error_type: str,
    details: str,
    retry_count: int = 0,
    fallback_used: bool = False,
    checkpoint_restored: Optional[str] = None
) -> None:
    """
    Log error to errors.json file with detailed context.
    
    Args:
        job_id: Unique job identifier
        step_no: Workflow step number (0-10)
        error_type: Type of error (e.g., 'TOKEN_ERROR', 'SYNTAX_ERROR')
        details: Detailed error message
        retry_count: Current retry attempt number
        fallback_used: Whether fallback mechanism was used
        checkpoint_restored: Path to checkpoint that was restored
    """
    ensure_logs_dir()
    
    error_entry = {
        'job_id': job_id,
        'step_no': step_no,
        'error_type': error_type,
        'details': details,
        'timestamp': datetime.utcnow().isoformat(),
        'retry_count': retry_count,
        'fallback_used': fallback_used,
        'checkpoint_restored': checkpoint_restored
    }
    
    try:
        # Read existing logs
        with open(LOGS_PATH, 'r') as f:
            logs = json.load(f)
        
        # Append new error
        logs.append(error_entry)
        
        # Write back
        with open(LOGS_PATH, 'w') as f:
            json.dump(logs, f, indent=2)
        
        # Also log to Python logger
        logger.error(
            f"Job {job_id} Step {step_no}: {error_type} - {details} "
            f"(retry={retry_count}, fallback={fallback_used})"
        )
        
    except Exception as e:
        logger.error(f"Failed to write error log: {e}")

def get_job_errors(job_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all errors for a specific job.
    
    Args:
        job_id: Unique job identifier
    
    Returns:
        List of error dictionaries
    """
    ensure_logs_dir()
    
    try:
        with open(LOGS_PATH, 'r') as f:
            logs = json.load(f)
        return [log for log in logs if log.get('job_id') == job_id]
    except Exception as e:
        logger.error(f"Failed to read error logs: {e}")
        return []

def get_job_error_count(job_id: str) -> int:
    """Get total error count for a job."""
    return len(get_job_errors(job_id))

def clear_old_logs(days: int = 30) -> None:
    """
    Clear error logs older than specified days.
    
    Args:
        days: Number of days to keep logs
    """
    ensure_logs_dir()
    
    try:
        with open(LOGS_PATH, 'r') as f:
            logs = json.load(f)
        
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        filtered_logs = [
            log for log in logs
            if datetime.fromisoformat(log['timestamp']).timestamp() > cutoff
        ]
        
        with open(LOGS_PATH, 'w') as f:
            json.dump(filtered_logs, f, indent=2)
        
        logger.info(f"Cleared {len(logs) - len(filtered_logs)} old log entries")
        
    except Exception as e:
        logger.error(f"Failed to clear old logs: {e}")

def log_info(job_id: str, step_no: int, message: str) -> None:
    """Log informational message."""
    logger.info(f"Job {job_id} Step {step_no}: {message}")

def log_warning(job_id: str, step_no: int, message: str) -> None:
    """Log warning message."""
    logger.warning(f"Job {job_id} Step {step_no}: {message}")

def log_success(job_id: str, step_no: int, message: str) -> None:
    """Log success message."""
    logger.info(f"✓ Job {job_id} Step {step_no}: {message}")

# Checkpoint management
def save_checkpoint(job_id: str, step_no: int, data: Dict[str, Any]) -> str:
    """
    Save checkpoint data for a workflow step.
    
    Args:
        job_id: Unique job identifier
        step_no: Workflow step number
        data: Data to checkpoint
    
    Returns:
        Path to checkpoint file
    """
    checkpoint_dir = os.getenv('CHECKPOINT_DIR', './data/checkpoints')
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
    
    checkpoint_path = os.path.join(checkpoint_dir, f"{job_id}_step_{step_no}.json")
    
    checkpoint_data = {
        'job_id': job_id,
        'step_no': step_no,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    
    try:
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        logger.info(f"Checkpoint saved: {checkpoint_path}")
        return checkpoint_path
    except Exception as e:
        logger.error(f"Failed to save checkpoint: {e}")
        return ""

def load_checkpoint(job_id: str, step_no: int) -> Optional[Dict[str, Any]]:
    """
    Load checkpoint data for a workflow step.
    
    Args:
        job_id: Unique job identifier
        step_no: Workflow step number
    
    Returns:
        Checkpoint data or None if not found
    """
    checkpoint_dir = os.getenv('CHECKPOINT_DIR', './data/checkpoints')
    checkpoint_path = os.path.join(checkpoint_dir, f"{job_id}_step_{step_no}.json")
    
    if not os.path.exists(checkpoint_path):
        logger.warning(f"Checkpoint not found: {checkpoint_path}")
        return None
    
    try:
        with open(checkpoint_path, 'r') as f:
            checkpoint_data = json.load(f)
        logger.info(f"Checkpoint loaded: {checkpoint_path}")
        return checkpoint_data.get('data')
    except Exception as e:
        logger.error(f"Failed to load checkpoint: {e}")
        return None

def cleanup_checkpoints(job_id: str) -> None:
    """Clean up all checkpoints for a job."""
    checkpoint_dir = os.getenv('CHECKPOINT_DIR', './data/checkpoints')
    
    if not os.path.exists(checkpoint_dir):
        return
    
    try:
        for filename in os.listdir(checkpoint_dir):
            if filename.startswith(f"{job_id}_"):
                file_path = os.path.join(checkpoint_dir, filename)
                os.remove(file_path)
        logger.info(f"Cleaned up checkpoints for job {job_id}")
    except Exception as e:
        logger.error(f"Failed to cleanup checkpoints: {e}")


