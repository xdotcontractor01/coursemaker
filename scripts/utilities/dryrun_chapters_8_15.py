#!/usr/bin/env python3
"""
Dry-run verification for Chapters 8-15

Verifies all audio files exist and reports durations.
Does NOT run Manim render.
"""

import json
import wave
from pathlib import Path

# Get project root
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MANIFESTS_DIR = PROJECT_ROOT / "manifests"
AUDIO_DIR = PROJECT_ROOT / "audio"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)


def get_wav_duration(filepath: Path) -> float:
    """Get WAV duration in seconds."""
    try:
        with wave.open(str(filepath), 'rb') as wf:
            return wf.getnframes() / float(wf.getframerate())
    except Exception:
        return 0.0


def verify_chapter(chapter_num: int) -> dict:
    """Verify a chapter's assets and return status."""
    manifest_path = MANIFESTS_DIR / f"chapter{chapter_num:02d}.json"
    
    if not manifest_path.exists():
        return {"error": f"Manifest not found: {manifest_path}"}
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    results = {
        "chapter": chapter_num,
        "title": manifest['title'],
        "pages": manifest['pages'],
        "scenes": [],
        "total_duration": 0.0,
        "missing_audio": [],
        "all_ok": True
    }
    
    for scene in manifest['scenes']:
        scene_num = scene['index']
        audio_file = scene['tts_file'].replace('audio/', '')
        audio_path = AUDIO_DIR / audio_file
        
        scene_info = {
            "index": scene_num,
            "title": scene['title'],
            "audio_file": audio_file,
            "audio_exists": audio_path.exists()
        }
        
        if audio_path.exists():
            duration = get_wav_duration(audio_path)
            scene_info["duration"] = duration
            results["total_duration"] += duration
        else:
            scene_info["duration"] = 0.0
            results["missing_audio"].append(audio_file)
            results["all_ok"] = False
        
        results["scenes"].append(scene_info)
    
    return results


def main():
    print("=" * 70)
    print("DRY-RUN VERIFICATION - Chapters 8-15")
    print("=" * 70)
    
    all_results = []
    grand_total = 0.0
    all_chapters_ok = True
    
    for chapter_num in range(8, 16):
        results = verify_chapter(chapter_num)
        all_results.append(results)
        
        if "error" in results:
            print(f"\n[Chapter {chapter_num}] ERROR: {results['error']}")
            all_chapters_ok = False
            continue
        
        print(f"\n[Chapter {chapter_num}] {results['title']}")
        print(f"  Pages: {results['pages']}")
        print(f"  Scenes: {len(results['scenes'])}")
        print("-" * 60)
        
        for scene in results['scenes']:
            status = "OK" if scene['audio_exists'] else "MISSING"
            duration_str = f"{scene['duration']:.1f}s" if scene['audio_exists'] else "N/A"
            print(f"  Scene {scene['index']:2d}: {scene['audio_file']:25s} [{status}] {duration_str}")
        
        print(f"  {'-' * 50}")
        print(f"  Total duration: {results['total_duration']:.1f}s ({results['total_duration']/60:.1f} min)")
        
        if results['missing_audio']:
            print(f"  MISSING AUDIO:")
            for f in results['missing_audio']:
                print(f"    - audio/{f}")
            all_chapters_ok = False
        
        grand_total += results['total_duration']
        
        # Save log file
        log_path = LOGS_DIR / f"chapter{chapter_num:02d}_dryrun.log"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Chapter {chapter_num}: {results['title']}\n")
            f.write(f"Pages: {results['pages']}\n")
            f.write(f"Scenes: {len(results['scenes'])}\n")
            f.write(f"Total Duration: {results['total_duration']:.1f}s\n")
            f.write(f"All OK: {results['all_ok']}\n\n")
            for scene in results['scenes']:
                status = "OK" if scene['audio_exists'] else "MISSING"
                f.write(f"Scene {scene['index']}: {scene['audio_file']} [{status}] {scene['duration']:.1f}s\n")
        print(f"  Log saved: {log_path.name}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total chapters: 8")
    print(f"Total runtime: {grand_total:.1f}s ({grand_total/60:.1f} min)")
    
    if all_chapters_ok:
        print("\nSTATUS: ALL ASSETS VERIFIED - Ready to render")
    else:
        print("\nSTATUS: SOME ASSETS MISSING - Check logs for details")
    
    print("=" * 70)
    
    return all_chapters_ok


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
