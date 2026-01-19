#!/usr/bin/env python3
"""
Dry-run verification for Chapters 5, 6, and 7 Manim scripts
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
    """Perform dry-run for a chapter."""
    manifest_path = MANIFESTS_DIR / f"chapter{chapter_num:02d}.json"
    log_path = LOGS_DIR / f"ch{chapter_num:02d}_dryrun.log"
    
    print(f"\n{'='*60}")
    print(f"DRY-RUN: Chapter {chapter_num}")
    print(f"{'='*60}")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    log_lines = []
    log_lines.append(f"Chapter {chapter_num}: {manifest['title']}")
    log_lines.append(f"Pages: {manifest['pages']}")
    log_lines.append(f"Total scenes: {len(manifest['scenes'])}")
    log_lines.append("")
    
    total_duration = 0.0
    missing_audio = []
    
    for scene in manifest['scenes']:
        scene_index = scene['index']
        audio_file = scene['tts_file'].replace('audio/', '')
        audio_path = AUDIO_DIR / audio_file
        
        if audio_path.exists():
            duration = get_wav_duration(audio_path)
            total_duration += duration
            log_lines.append(f"[OK] Scene {scene_index:2d}: {audio_file} ({duration:.2f}s)")
            print(f"  [OK] Scene {scene_index:2d}: {audio_file} ({duration:.2f}s)")
        else:
            missing_audio.append(audio_file)
            log_lines.append(f"[MISSING] Scene {scene_index:2d}: {audio_file}")
            print(f"  [MISSING] Scene {scene_index:2d}: {audio_file}")
    
    log_lines.append("")
    log_lines.append(f"Total duration: {total_duration:.2f}s ({total_duration/60:.1f} min)")
    log_lines.append(f"Missing audio files: {len(missing_audio)}")
    
    if missing_audio:
        log_lines.append("")
        log_lines.append("MISSING AUDIO FILES:")
        for audio_file in missing_audio:
            log_lines.append(f"  MISSING_NARRATION_FOR: audio/{audio_file}")
            print(f"  MISSING_NARRATION_FOR: audio/{audio_file}")
    
    # Write log
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    
    print(f"\n  Log saved to: {log_path}")
    return len(missing_audio) == 0

def main():
    """Run dry-run for all chapters."""
    print("="*60)
    print("DRY-RUN VERIFICATION FOR CHAPTERS 5, 6, AND 7")
    print("="*60)
    
    all_ok = True
    for chapter_num in [5, 6, 7]:
        ok = dryrun_chapter(chapter_num)
        if not ok:
            all_ok = False
    
    print("\n" + "="*60)
    if all_ok:
        print("ALL CHECKS PASSED - Ready for rendering")
    else:
        print("SOME AUDIO FILES MISSING - Fix before rendering")
    print("="*60)

if __name__ == "__main__":
    main()




