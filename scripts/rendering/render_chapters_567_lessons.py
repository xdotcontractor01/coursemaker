#!/usr/bin/env python3
"""
Render lesson-based MP4 videos for Chapters 6 and 7
"""

import subprocess
import shutil
import wave
from pathlib import Path

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MANIM_SCRIPTS_DIR = PROJECT_ROOT / "manim_scripts"
OUTPUTS_DIR.mkdir(exist_ok=True)

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

def render_lesson(chapter_num: int, lesson_num: int, scene_class: str):
    """Render a lesson video."""
    script_file = MANIM_SCRIPTS_DIR / f"chapter{chapter_num:02d}.py"
    output_name = f"chapter{chapter_num:02d}_lesson{lesson_num:02d}.mp4"
    
    print(f"\n{'='*60}")
    print(f"Rendering Chapter {chapter_num}, Lesson {lesson_num}")
    print(f"{'='*60}")
    print(f"Script: {script_file}")
    print(f"Scene: {scene_class}")
    print(f"Output: {output_name}")
    
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
    output_file = OUTPUTS_DIR / output_name
    shutil.copy2(video_file, output_file)
    
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    duration = get_video_duration(output_file)
    duration_min = duration / 60
    
    print(f"\n[OK] Video rendered: {output_file}")
    print(f"     Size: {file_size_mb:.1f} MB")
    print(f"     Duration: {duration:.1f}s ({duration_min:.1f} min)")
    
    if duration > 300:  # 5 minutes
        print(f"     [WARNING] Video exceeds 5 minutes")
    
    return True

def main():
    """Render all lessons."""
    print("="*60)
    print("RENDERING LESSON-BASED VIDEOS FOR CHAPTERS 6 AND 7")
    print("="*60)
    
    # Chapter 6: 2 lessons
    lessons = [
        (6, 1, "Chapter06Lesson01"),
        (6, 2, "Chapter06Lesson02"),
    ]
    
    # Chapter 7: 3 lessons
    lessons.extend([
        (7, 1, "Chapter07Lesson01"),
        (7, 2, "Chapter07Lesson02"),
        (7, 3, "Chapter07Lesson03"),
    ])
    
    all_success = True
    for chapter_num, lesson_num, scene_class in lessons:
        success = render_lesson(chapter_num, lesson_num, scene_class)
        if not success:
            print(f"\n[ERROR] Failed to render Chapter {chapter_num}, Lesson {lesson_num}")
            all_success = False
            break
    
    print("\n" + "="*60)
    if all_success:
        print("ALL LESSONS RENDERED SUCCESSFULLY")
    else:
        print("SOME LESSONS FAILED TO RENDER")
    print("="*60)
    
    # Print summary
    if all_success:
        print("\nOutput files:")
        for chapter_num, lesson_num, _ in lessons:
            output_file = OUTPUTS_DIR / f"chapter{chapter_num:02d}_lesson{lesson_num:02d}.mp4"
            if output_file.exists():
                duration = get_video_duration(output_file)
                print(f"  {output_file.name}: {duration/60:.1f} min")

if __name__ == "__main__":
    main()



