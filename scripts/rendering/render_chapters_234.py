#!/usr/bin/env python3
"""
Render script for Chapters 2, 3, and 4

Renders all three chapters using Manim and moves output to outputs/ directory.
"""

import subprocess
import shutil
from pathlib import Path
import sys

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MANIM_SCRIPTS_DIR = PROJECT_ROOT / "manim_scripts"
OUTPUTS_DIR.mkdir(exist_ok=True)


def find_rendered_video(script_name: str, scene_name: str) -> Path:
    """Find the rendered video file in media/videos directory."""
    # Manim typically creates: media/videos/{script_name}/{quality}/{scene_name}.mp4
    # We're using -qh which creates 1080p30 quality
    media_path = PROJECT_ROOT / "media/videos" / script_name.replace(".py", "") / "1080p30" / f"{scene_name}.mp4"
    
    if media_path.exists():
        return media_path
    
    # Try alternative path structure
    alt_path = PROJECT_ROOT / "media/videos" / script_name / "1080p30" / f"{scene_name}.mp4"
    if alt_path.exists():
        return alt_path
    
    # Search recursively
    videos_dir = PROJECT_ROOT / "media/videos"
    if videos_dir.exists():
        for path in videos_dir.rglob(f"{scene_name}.mp4"):
            return path
    
    return None


def render_chapter(chapter_num: int):
    """Render a single chapter."""
    script_name = f"chapter{chapter_num:02d}.py"
    script_path = MANIM_SCRIPTS_DIR / script_name
    scene_name = f"Chapter{chapter_num:02d}Video"
    output_name = f"chapter{chapter_num:02d}_final.mp4"
    output_path = OUTPUTS_DIR / output_name
    
    print("=" * 60)
    print(f"Rendering Chapter {chapter_num}")
    print("=" * 60)
    print(f"Script: {script_name}")
    print(f"Scene: {scene_name}")
    print(f"Output: {output_path}")
    print()
    
    # Build manim command
    cmd = ["manim", "-qh", str(script_path), scene_name]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        # Run manim
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        # Find the rendered video
        rendered_path = find_rendered_video(script_name, scene_name)
        
        if rendered_path and rendered_path.exists():
            # Copy to outputs directory
            shutil.copy2(rendered_path, output_path)
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"[OK] Video rendered: {output_path.name} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"[ERROR] Rendered video not found for {scene_name}")
            print(f"Expected location: media/videos/.../{scene_name}.mp4")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Render timeout for Chapter {chapter_num}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Render failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def main():
    """Render all chapters."""
    print("=" * 60)
    print("Rendering Chapters 2, 3, and 4")
    print("=" * 60)
    print()
    
    results = {}
    for chapter_num in [2, 3, 4]:
        results[chapter_num] = render_chapter(chapter_num)
        print()
    
    print("=" * 60)
    print("Rendering Summary")
    print("=" * 60)
    for chapter_num in [2, 3, 4]:
        status = "SUCCESS" if results[chapter_num] else "FAILED"
        output_name = f"chapter{chapter_num:02d}_final.mp4"
        print(f"Chapter {chapter_num}: {status} -> {OUTPUTS_DIR / output_name}")
    
    all_success = all(results.values())
    print()
    if all_success:
        print("All chapters rendered successfully!")
    else:
        print("Some chapters failed to render. Check errors above.")
    
    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())







