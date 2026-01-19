#!/usr/bin/env python3
"""Check render status and print summary."""

from pathlib import Path
import subprocess

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

def get_video_duration(video_path: Path) -> float:
    """Get video duration using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return 0.0

# Expected files
expected_files = [
    "chapter06_lesson01.mp4",
    "chapter06_lesson02.mp4",
    "chapter07_lesson01.mp4",
    "chapter07_lesson02.mp4",
    "chapter07_lesson03.mp4",
]

print("="*60)
print("RENDER STATUS CHECK")
print("="*60)

for filename in expected_files:
    filepath = OUTPUTS_DIR / filename
    if filepath.exists():
        duration = get_video_duration(filepath)
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"\n[OK] {filename}")
        print(f"     Duration: {duration:.1f}s ({duration/60:.1f} min)")
        print(f"     Size: {size_mb:.1f} MB")
        if duration > 300:
            print(f"     [WARNING] Exceeds 5 minutes")
    else:
        print(f"\n[PENDING] {filename} - Not yet rendered")

print("\n" + "="*60)



