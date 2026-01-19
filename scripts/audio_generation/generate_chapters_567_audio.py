#!/usr/bin/env python3
"""
Audio Generation Script for Chapters 5, 6, and 7

Generates WAV audio files for all scenes using OpenAI TTS.
Uses sanitized narration text.
Normalizes audio to -16 LUFS using ffmpeg.
Updates manifests with durations.
"""

import json
import os
import sys
import wave
import subprocess
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: OpenAI package not installed.")
    print("Please run: pip install openai")
    sys.exit(1)

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Configuration
MANIFESTS_DIR = PROJECT_ROOT / "manifests"
AUDIO_DIR = PROJECT_ROOT / "audio"
TTS_MODEL = "tts-1"
TTS_VOICE = "nova"
SAMPLE_RATE = 24000
SAMPLE_WIDTH = 2
CHANNELS = 1

# Audio normalization settings
LUFS_TARGET = -16.0


def load_api_key():
    """Load OpenAI API key from config.json."""
    try:
        with open(PROJECT_ROOT / "config.json", 'r') as f:
            config = json.load(f)
            api_key = config.get("openai_api_key", config.get("OPENAI_API_KEY", ""))
            if api_key and api_key.startswith("sk-"):
                return api_key
    except Exception as e:
        print(f"Error loading config: {e}")
    return None


def pcm_to_wav(pcm_data: bytes, output_path: Path, sample_rate: int = SAMPLE_RATE, 
                channels: int = CHANNELS, sampwidth: int = SAMPLE_WIDTH) -> float:
    """Convert raw PCM bytes to a WAV file."""
    num_frames = len(pcm_data) // (sampwidth * channels)
    
    with wave.open(str(output_path), 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    
    duration = num_frames / sample_rate
    return duration


def normalize_audio(input_path: Path, output_path: Path) -> bool:
    """Normalize audio to -16 LUFS using ffmpeg loudnorm."""
    try:
        cmd = [
            "ffmpeg", "-i", str(input_path),
            "-af", f"loudnorm=I={LUFS_TARGET}:TP=-1.5:LRA=11",
            "-y",  # Overwrite output file
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True
        else:
            print(f"[WARNING] FFmpeg normalization failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[WARNING] FFmpeg timeout for {input_path.name}")
        return False
    except FileNotFoundError:
        print("[WARNING] FFmpeg not found - skipping normalization")
        return False
    except Exception as e:
        print(f"[WARNING] Normalization error: {e}")
        return False


def get_wav_duration(filepath: Path) -> float:
    """Get WAV file duration in seconds."""
    try:
        with wave.open(str(filepath), 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception:
        return 0.0


def generate_audio_for_chapter(chapter_num: int, client: OpenAI):
    """Generate audio for a single chapter."""
    manifest_path = MANIFESTS_DIR / f"chapter{chapter_num:02d}.json"
    
    if not manifest_path.exists():
        print(f"[ERROR] Manifest not found: {manifest_path}")
        return False
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\nChapter {chapter_num}: {manifest['title']}")
    print("-" * 60)
    
    total_duration = 0.0
    
    for scene in manifest['scenes']:
        scene_num = scene['index']
        # Use sanitized narration for TTS
        narration_text = scene.get('narration_sanitized', scene.get('narration_text', '')).strip()
        if not narration_text:
            narration_text = scene.get('narration_text', '').strip()
        
        audio_filename = scene['tts_file'].replace('audio/', '')
        audio_path = AUDIO_DIR / audio_filename
        temp_path = AUDIO_DIR / f"temp_{audio_filename}"
        
        word_count = len(narration_text.split())
        print(f"  Scene {scene_num}: {audio_filename} ({word_count} words)")
        
        # Skip if already exists
        if audio_path.exists():
            duration = get_wav_duration(audio_path)
            total_duration += duration
            file_size = audio_path.stat().st_size / 1024
            print(f"       -> [EXISTS] {file_size:.1f} KB, {duration:.1f}s")
            scene['duration'] = duration
            continue
        
        try:
            # Generate TTS
            response = client.audio.speech.create(
                model=TTS_MODEL,
                voice=TTS_VOICE,
                input=narration_text,
                response_format="pcm"
            )
            
            # Convert PCM to WAV
            pcm_data = response.content
            duration = pcm_to_wav(pcm_data, temp_path)
            file_size = temp_path.stat().st_size / 1024
            print(f"       -> {file_size:.1f} KB, {duration:.1f}s (raw)")
            
            # Normalize audio
            normalized = normalize_audio(temp_path, audio_path)
            if normalized:
                duration = get_wav_duration(audio_path)
                file_size = audio_path.stat().st_size / 1024
                print(f"       -> {file_size:.1f} KB, {duration:.1f}s (normalized)")
            else:
                # Use non-normalized file
                temp_path.rename(audio_path)
                print(f"       -> {file_size:.1f} KB, {duration:.1f}s (not normalized)")
            
            total_duration += duration
            scene['duration'] = duration
            
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
                
        except Exception as e:
            print(f"       -> [ERROR] {e}")
            scene['duration'] = None
    
    # Save updated manifest
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n  Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    return True


def main():
    """Generate audio for all chapters."""
    api_key = load_api_key()
    if not api_key:
        print("ERROR: OpenAI API key not found in config.json")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    print("=" * 60)
    print("Generating Audio for Chapters 5, 6, and 7")
    print("=" * 60)
    
    for chapter_num in [5, 6, 7]:
        generate_audio_for_chapter(chapter_num, client)
    
    print("\n" + "=" * 60)
    print("Audio generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()




