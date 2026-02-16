#!/usr/bin/env python3
"""
Render script for Chapters 8-15

Renders all chapter videos using Manim at 1080p/30fps.
Outputs to outputs/ directory.
"""

import subprocess
import sys
from pathlib import Path

# Get project root
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MANIM_SCRIPTS_DIR = PROJECT_ROOT / "manim_scripts"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Ensure outputs directory exists
OUTPUTS_DIR.mkdir(exist_ok=True)

# Rendering configuration
# Format: (chapter_num, script_file, scene_class, output_name)
RENDER_CONFIG = [
    # Chapter 8: Drainage (3 lessons)
    (8, "chapter08.py", "Chapter08Lesson01", "chapter08_lesson01.mp4"),
    (8, "chapter08.py", "Chapter08Lesson02", "chapter08_lesson02.mp4"),
    (8, "chapter08.py", "Chapter08Lesson03", "chapter08_lesson03.mp4"),
    
    # Chapter 9: Utility Plans (1 full video)
    (9, "chapter09.py", "Chapter09Full", "chapter09_final.mp4"),
    
    # Chapter 10: Signs, Markings, Signals (1 full video)
    (10, "chapter10.py", "Chapter10Full", "chapter10_final.mp4"),
    
    # Chapter 11: Maintenance of Traffic (1 full video)
    (11, "chapter11.py", "Chapter11Full", "chapter11_final.mp4"),
    
    # Chapter 12: ESPCP (1 full video)
    (12, "chapter12.py", "Chapter12Full", "chapter12_final.mp4"),
    
    # Chapter 13: Cross Sections (2 lessons)
    (13, "chapter13.py", "Chapter13Lesson01", "chapter13_lesson01.mp4"),
    (13, "chapter13.py", "Chapter13Lesson02", "chapter13_lesson02.mp4"),
    
    # Chapter 14: Standards & Details (1 full video)
    (14, "chapter14.py", "Chapter14Full", "chapter14_final.mp4"),
    
    # Chapter 15: Right of Way (2 lessons)
    (15, "chapter15.py", "Chapter15Lesson01", "chapter15_lesson01.mp4"),
    (15, "chapter15.py", "Chapter15Lesson02", "chapter15_lesson02.mp4"),
]


def render_video(script_file: str, scene_class: str, output_name: str) -> bool:
    """Render a single video using Manim."""
    script_path = MANIM_SCRIPTS_DIR / script_file
    output_path = OUTPUTS_DIR / output_name
    
    if not script_path.exists():
        print(f"  ERROR: Script not found: {script_path}")
        return False
    
    # Build manim command
    # -qh = high quality (1080p)
    # --fps 30 = 30 frames per second
    # -o = output filename
    cmd = [
        "manim",
        "-qh",
        "--fps", "30",
        "-o", output_name,
        str(script_path),
        scene_class
    ]
    
    print(f"  Running: manim -qh --fps 30 {script_file} {scene_class}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per video
        )
        
        if result.returncode == 0:
            # Find rendered file and move to outputs
            # Manim outputs to media/videos/{script_name}/1080p30/{output_name}
            script_name = script_file.replace('.py', '')
            rendered_path = PROJECT_ROOT / "media" / "videos" / script_name / "1080p30" / output_name
            
            if rendered_path.exists():
                # Move to outputs directory
                import shutil
                shutil.copy2(str(rendered_path), str(output_path))
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"  SUCCESS: {output_name} ({size_mb:.1f} MB)")
                return True
            else:
                print(f"  WARNING: Rendered file not found at expected location")
                print(f"           Expected: {rendered_path}")
                # Check if it's in the outputs already
                if output_path.exists():
                    size_mb = output_path.stat().st_size / (1024 * 1024)
                    print(f"  Found at: {output_path} ({size_mb:.1f} MB)")
                    return True
                return False
        else:
            print(f"  ERROR: Manim failed")
            print(f"  STDERR: {result.stderr[:500]}" if result.stderr else "")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ERROR: Render timeout (>10 min)")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    print("=" * 70)
    print("RENDERING CHAPTERS 8-15")
    print("=" * 70)
    
    total = len(RENDER_CONFIG)
    success = 0
    failed = []
    
    for i, (chapter, script, scene_class, output) in enumerate(RENDER_CONFIG, 1):
        print(f"\n[{i}/{total}] Chapter {chapter}: {output}")
        print("-" * 60)
        
        if render_video(script, scene_class, output):
            success += 1
        else:
            failed.append(output)
    
    # Summary
    print("\n" + "=" * 70)
    print("RENDER SUMMARY")
    print("=" * 70)
    print(f"Total: {total}")
    print(f"Success: {success}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed videos:")
        for f in failed:
            print(f"  - {f}")
    
    # List outputs
    print("\nOutput files:")
    for output_file in sorted(OUTPUTS_DIR.glob("chapter*.mp4")):
        if any(c in output_file.name for c in ['08', '09', '10', '11', '12', '13', '14', '15']):
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"  {output_file.name}: {size_mb:.1f} MB")
    
    print("=" * 70)
    
    return len(failed) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
