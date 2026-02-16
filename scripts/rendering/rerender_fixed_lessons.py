#!/usr/bin/env python3
"""
Re-render only the lessons that had missing images.
Does NOT regenerate audio or change narration.
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

# Lessons that need re-rendering (from image fix script)
AFFECTED_LESSONS = [
    (8, 1),
    (8, 2),
    (8, 3),
    (12, 1),
    (13, 1),
    (13, 2),
    (14, 1),
    (15, 2),
]

def get_scene_class_name(chapter: int, lesson: int) -> str:
    """Get the Manim scene class name for a chapter/lesson."""
    if chapter in [8, 13, 15]:  # Multi-lesson chapters
        return f"Chapter{chapter:02d}Lesson{lesson:02d}"
    else:  # Single-lesson chapters
        return f"Chapter{chapter:02d}Scene"

def get_output_filename(chapter: int, lesson: int) -> str:
    """Get the expected output filename."""
    if chapter in [8, 13, 15]:  # Multi-lesson chapters
        return f"chapter{chapter:02d}_lesson{lesson:02d}.mp4"
    else:
        return f"chapter{chapter:02d}_final.mp4"

def render_lesson(chapter: int, lesson: int):
    """Render a single lesson."""
    script_path = BASE_DIR / "manim_scripts" / f"chapter{chapter:02d}.py"
    scene_name = get_scene_class_name(chapter, lesson)
    output_name = get_output_filename(chapter, lesson)
    
    print(f"\n{'='*60}")
    print(f"Rendering Chapter {chapter:02d}, Lesson {lesson:02d}")
    print(f"  Script: {script_path.name}")
    print(f"  Scene: {scene_name}")
    print(f"  Output: {output_name}")
    print(f"{'='*60}")
    
    if not script_path.exists():
        print(f"  [ERROR] Script not found: {script_path}")
        return False
    
    # Build manim command
    cmd = [
        sys.executable, "-m", "manim", "render",
        "-qh",  # High quality
        "--fps", "30",
        str(script_path),
        scene_name,
        "-o", output_name
    ]
    
    print(f"  Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            print(f"  [OK] Rendered successfully")
            # Move output to outputs folder
            media_path = BASE_DIR / "media" / "videos" / f"chapter{chapter:02d}" / "1080p60"
            if not media_path.exists():
                media_path = BASE_DIR / "media" / "videos" / f"chapter{chapter:02d}" / "1080p30"
            
            src_file = media_path / output_name
            if src_file.exists():
                dst_file = BASE_DIR / "outputs" / output_name
                import shutil
                shutil.copy2(str(src_file), str(dst_file))
                print(f"  [OK] Copied to outputs/{output_name}")
            return True
        else:
            print(f"  [FAIL] Render error:")
            print(result.stderr[-500:] if result.stderr else "No error output")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  [FAIL] Timeout after 600 seconds")
        return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


def main():
    print("=" * 60)
    print("RE-RENDERING LESSONS WITH FIXED IMAGES")
    print("=" * 60)
    print(f"Total lessons to re-render: {len(AFFECTED_LESSONS)}")
    
    results = []
    for chapter, lesson in AFFECTED_LESSONS:
        success = render_lesson(chapter, lesson)
        results.append((chapter, lesson, success))
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for _, _, s in results if s)
    fail_count = len(results) - success_count
    
    for chapter, lesson, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} Chapter {chapter:02d}, Lesson {lesson:02d}")
    
    print(f"\nTotal: {success_count} succeeded, {fail_count} failed")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
