#!/usr/bin/env python3
"""
Render final MP4 videos for Chapters 5, 6, and 7
"""

import subprocess
import shutil
from pathlib import Path

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MANIM_SCRIPTS_DIR = PROJECT_ROOT / "manim_scripts"
OUTPUTS_DIR.mkdir(exist_ok=True)

def render_chapter(chapter_num: int):
    """Render a chapter video."""
    script_file = MANIM_SCRIPTS_DIR / f"chapter{chapter_num:02d}.py"
    scene_class = f"Chapter{chapter_num:02d}Video"
    
    print(f"\n{'='*60}")
    print(f"Rendering Chapter {chapter_num}")
    print(f"{'='*60}")
    print(f"Script: {script_file}")
    print(f"Scene: {scene_class}")
    
    # Render with Manim
    cmd = [
        "manim",
        "-qh",  # High quality, 1080p30
        str(script_file),
        scene_class
    ]
    
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Render failed:")
        print(result.stderr)
        return False
    
    # Find the generated video
    media_dir = PROJECT_ROOT / "media/videos"
    video_files = list(media_dir.rglob(f"{scene_class}*.mp4"))
    
    if not video_files:
        print(f"[ERROR] No video file found for {scene_class}")
        return False
    
    # Get the highest quality version (1080p30)
    video_file = None
    for vf in video_files:
        if "1080p30" in str(vf) or "1080p60" in str(vf):
            video_file = vf
            break
    
    if not video_file:
        video_file = video_files[0]  # Use any available
    
    # Copy to outputs directory
    output_file = OUTPUTS_DIR / f"chapter{chapter_num:02d}_final.mp4"
    shutil.copy2(video_file, output_file)
    
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Video rendered: {output_file}")
    print(f"     Size: {file_size_mb:.1f} MB")
    
    return True

def main():
    """Render all chapters."""
    print("="*60)
    print("RENDERING CHAPTERS 5, 6, AND 7")
    print("="*60)
    
    for chapter_num in [5, 6, 7]:
        success = render_chapter(chapter_num)
        if not success:
            print(f"\n[ERROR] Failed to render Chapter {chapter_num}")
            break
    
    print("\n" + "="*60)
    print("RENDERING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()




