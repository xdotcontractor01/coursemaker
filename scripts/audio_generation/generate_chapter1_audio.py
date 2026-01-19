#!/usr/bin/env python3
"""
Audio Generation Script for Chapter 1 Videos

Generates WAV audio files for all 4 videos in Chapter 1 using OpenAI TTS.
Each video has multiple scenes, and each scene gets its own audio file.

Usage:
    python chapter1/generate_chapter1_audio.py

Requirements:
    pip install openai
"""

import os
import sys
import wave
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

AUDIO_DIR = PROJECT_ROOT / "audio"

# OpenAI TTS settings
TTS_MODEL = "tts-1"
TTS_VOICE = "nova"  # Natural female voice
TTS_FORMAT = "pcm"

# Audio format
SAMPLE_RATE = 24000
SAMPLE_WIDTH = 2
CHANNELS = 1

# ============================================================================
# IMPORTS
# ============================================================================

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: OpenAI package not installed.")
    print("Please run: pip install openai")
    sys.exit(1)

# Import narration modules
try:
    from video1_narration import get_all_narrations as get_v1_narrations
    from video2_narration import get_all_narrations as get_v2_narrations
    from video3_narration import get_all_narrations as get_v3_narrations
    from video4_narration import get_all_narrations as get_v4_narrations
except ImportError as e:
    print(f"ERROR: Could not import narration modules: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)

# ============================================================================
# AUDIO FUNCTIONS
# ============================================================================

def pcm_to_wav(pcm_data: bytes, output_path: str) -> float:
    """Convert raw PCM to proper WAV file."""
    num_frames = len(pcm_data) // (SAMPLE_WIDTH * CHANNELS)
    
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm_data)
    
    duration = num_frames / SAMPLE_RATE
    return duration


def get_wav_duration(filepath: str) -> float:
    """Get WAV file duration in seconds."""
    try:
        with wave.open(filepath, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception:
        return 0.0


# ============================================================================
# API KEY LOADING
# ============================================================================

def load_api_key() -> str:
    """Load OpenAI API key from environment or config file."""
    
    # Check environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"\'')
                    if api_key:
                        return api_key
    
    # Check config.json
    config_file = Path("config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            api_key = config.get("openai_api_key", config.get("OPENAI_API_KEY", ""))
            if api_key and api_key.startswith("sk-"):
                return api_key
    
    return None


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_all_audio():
    """Generate audio for all 4 videos."""
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("=" * 60)
        print("ERROR: OpenAI API key not found!")
        print("=" * 60)
        print("\nPlease provide via one of these methods:")
        print("  1. Environment variable: set OPENAI_API_KEY=sk-...")
        print("  2. Edit config.json with your API key")
        print("  3. Create .env file with: OPENAI_API_KEY=sk-...")
        sys.exit(1)
    
    # Initialize client
    client = OpenAI(api_key=api_key)
    
    # Create output directory
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    
    # Collect all narrations
    all_videos = [
        ("ch1_v1", get_v1_narrations()),
        ("ch1_v2", get_v2_narrations()),
        ("ch1_v3", get_v3_narrations()),
        ("ch1_v4", get_v4_narrations()),
    ]
    
    total_files = sum(len(narrations) for _, narrations in all_videos)
    current = 0
    
    print("=" * 60)
    print("Chapter 1 Audio Generation")
    print("=" * 60)
    print(f"Total files to generate: {total_files}")
    print(f"TTS Model: {TTS_MODEL}")
    print(f"Voice: {TTS_VOICE}")
    print(f"Output: {AUDIO_DIR.absolute()}")
    print("=" * 60)
    
    results = []
    
    for video_prefix, narrations in all_videos:
        print(f"\n{video_prefix.upper()}")
        print("-" * 40)
        
        for scene_name, narration_text in narrations.items():
            current += 1
            
            # Extract scene number
            scene_num = int(scene_name.split("_")[1])
            
            # Output filename
            output_filename = f"{video_prefix}_scene_{scene_num:02d}.wav"
            output_path = AUDIO_DIR / output_filename
            
            word_count = len(narration_text.split())
            print(f"  [{current}/{total_files}] {output_filename} ({word_count} words)")
            
            try:
                # Call OpenAI TTS API
                response = client.audio.speech.create(
                    model=TTS_MODEL,
                    voice=TTS_VOICE,
                    input=narration_text,
                    response_format="pcm"
                )
                
                # Get PCM data and convert to WAV
                pcm_data = response.content
                duration = pcm_to_wav(pcm_data, str(output_path))
                
                file_size = output_path.stat().st_size / 1024
                print(f"       -> {file_size:.1f} KB, {duration:.1f}s")
                
                results.append((video_prefix, scene_num, duration))
                
            except Exception as e:
                print(f"       -> ERROR: {e}")
                results.append((video_prefix, scene_num, 0.0))
    
    # Summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    
    for video_prefix in ["ch1_v1", "ch1_v2", "ch1_v3", "ch1_v4"]:
        video_results = [(s, d) for v, s, d in results if v == video_prefix]
        total_duration = sum(d for _, d in video_results)
        print(f"{video_prefix}: {len(video_results)} scenes, {total_duration:.1f}s total")
    
    total_all = sum(d for _, _, d in results)
    print(f"\nTotal audio: {total_all:.1f}s ({total_all/60:.1f} min)")
    print("=" * 60)
    
    return results


def verify_audio_files():
    """Verify all audio files exist and have valid durations."""
    
    print("\n" + "=" * 60)
    print("AUDIO FILE VERIFICATION")
    print("=" * 60)
    
    videos = [
        ("ch1_v1", 6),   # Video 1 has 6 scenes
        ("ch1_v2", 6),   # Video 2 has 6 scenes
        ("ch1_v3", 8),   # Video 3 has 8 scenes
        ("ch1_v4", 8),   # Video 4 has 8 scenes
    ]
    
    all_ok = True
    total_duration = 0
    
    for video_prefix, num_scenes in videos:
        print(f"\n{video_prefix.upper()}:")
        
        for scene_num in range(1, num_scenes + 1):
            filename = f"{video_prefix}_scene_{scene_num:02d}.wav"
            filepath = AUDIO_DIR / filename
            
            if filepath.exists():
                duration = get_wav_duration(str(filepath))
                if duration > 0.5:
                    status = "OK"
                    total_duration += duration
                else:
                    status = "TOO SHORT"
                    all_ok = False
                print(f"  Scene {scene_num}: {duration:.1f}s [{status}]")
            else:
                print(f"  Scene {scene_num}: MISSING")
                all_ok = False
    
    print("\n" + "-" * 60)
    print(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"All files valid: {'YES' if all_ok else 'NO'}")
    print("=" * 60)
    
    return all_ok


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Chapter 1 audio files")
    parser.add_argument("--verify-only", "-v", action="store_true", help="Only verify existing files")
    parser.add_argument("--api-key", "-k", help="OpenAI API key")
    args = parser.parse_args()
    
    # Set API key from command line if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    if args.verify_only:
        verify_audio_files()
    else:
        generate_all_audio()
        verify_audio_files()
    
    print("\nNext steps:")
    print("  manim -qh chapter1/chapter1_video1.py Chapter1Video1")
    print("  manim -qh chapter1/chapter1_video2.py Chapter1Video2")
    print("  manim -qh chapter1/chapter1_video3.py Chapter1Video3")
    print("  manim -qh chapter1/chapter1_video4.py Chapter1Video4")









