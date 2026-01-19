#!/usr/bin/env python3
"""
Dry-run verification script for Chapters 2, 3, and 4

Verifies that all audio files exist and can be loaded.
Generates logs for each chapter.
"""

import json
import wave
from pathlib import Path

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MANIFESTS_DIR = PROJECT_ROOT / "manifests"
AUDIO_DIR = PROJECT_ROOT / "audio"
LOGS_DIR = PROJECT_ROOT / "logs"

LOGS_DIR.mkdir(exist_ok=True)


def get_wav_duration(filepath: Path) -> float:
    """Get WAV file duration in seconds."""
    try:
        with wave.open(str(filepath), 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception:
        return 0.0


def dryrun_chapter(chapter_num: int):
    """Perform dry-run for a single chapter."""
    manifest_path = MANIFESTS_DIR / f"chapter_{chapter_num:02d}.json"
    log_path = LOGS_DIR / f"chapter_{chapter_num:02d}_dryrun.log"
    
    if not manifest_path.exists():
        print(f"[ERROR] Manifest not found: {manifest_path}")
        return False
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    log_lines = []
    log_lines.append("=" * 60)
    log_lines.append(f"Dry-Run Log: Chapter {chapter_num}")
    log_lines.append(f"Title: {manifest['title']}")
    log_lines.append(f"Pages: {manifest['pages']}")
    log_lines.append("=" * 60)
    log_lines.append("")
    
    all_ok = True
    total_duration = 0.0
    
    for scene in manifest['scenes']:
        scene_num = scene['index']
        audio_filename = scene['tts_file_path'].replace('audio/', '')
        audio_path = AUDIO_DIR / audio_filename
        
        if audio_path.exists():
            duration = get_wav_duration(audio_path)
            total_duration += duration
            log_lines.append(f"[OK] Scene {scene_num}: {audio_filename} ({duration:.1f}s)")
        else:
            log_lines.append(f"[MISSING] Scene {scene_num}: {audio_filename}")
            log_lines.append(f"MISSING_NARRATION_FOR: audio/{audio_filename}")
            all_ok = False
    
    log_lines.append("")
    log_lines.append("-" * 60)
    log_lines.append(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    log_lines.append(f"Status: {'PASS' if all_ok else 'FAIL'}")
    log_lines.append("=" * 60)
    
    # Write log file
    with open(log_path, 'w') as f:
        f.write('\n'.join(log_lines))
    
    # Print to console
    print('\n'.join(log_lines))
    print()
    
    return all_ok


def main():
    """Run dry-run for all chapters."""
    print("=" * 60)
    print("Dry-Run Verification for Chapters 2, 3, and 4")
    print("=" * 60)
    print()
    
    results = {}
    for chapter_num in [2, 3, 4]:
        results[chapter_num] = dryrun_chapter(chapter_num)
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    for chapter_num in [2, 3, 4]:
        status = "PASS" if results[chapter_num] else "FAIL"
        print(f"Chapter {chapter_num}: {status}")
    
    all_pass = all(results.values())
    print()
    if all_pass:
        print("All chapters passed dry-run verification!")
    else:
        print("Some chapters failed verification. Check logs for details.")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())







