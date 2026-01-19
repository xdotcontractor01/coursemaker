#!/usr/bin/env python3
"""
Audio Generation Script for Highway Plan Reading Explainer Video

This script generates WAV audio files for each scene using OpenAI's TTS API.
Fixed version that properly handles WAV format conversion.

Requirements:
    pip install openai

Usage:
    python generate_audio.py

Environment:
    OPENAI_API_KEY must be set (env var, .env file, or config.json)
"""

import os
import sys
import io
import wave
import struct
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Output directory for audio files (zero-padded filenames)
AUDIO_DIR = PROJECT_ROOT / "audio"

# OpenAI TTS settings
TTS_MODEL = "tts-1"           # Standard quality model
TTS_VOICE = "nova"            # Natural female voice
TTS_FORMAT = "pcm"            # Raw PCM for proper WAV conversion

# Audio format settings
SAMPLE_RATE = 24000           # OpenAI TTS sample rate
SAMPLE_WIDTH = 2              # 16-bit audio (2 bytes)
CHANNELS = 1                  # Mono

# ============================================================================
# IMPORTS
# ============================================================================

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: OpenAI package not installed.")
    print("Please run: pip install openai")
    sys.exit(1)

# Import narration text
try:
    from narration_scenes import get_all_narrations, get_scene_count
except ImportError:
    print("ERROR: narration_scenes.py not found.")
    print("Please ensure narration_scenes.py is in the same directory.")
    sys.exit(1)

# ============================================================================
# AUDIO CONVERSION FUNCTIONS
# ============================================================================

def pcm_to_wav(pcm_data: bytes, output_path: str) -> float:
    """
    Convert raw PCM audio data to a proper WAV file.
    
    Args:
        pcm_data: Raw PCM audio bytes
        output_path: Path to save the WAV file
        
    Returns:
        Duration of the audio in seconds
    """
    # Calculate number of frames
    num_frames = len(pcm_data) // (SAMPLE_WIDTH * CHANNELS)
    
    # Write WAV file with proper headers
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm_data)
    
    # Calculate and return duration
    duration = num_frames / SAMPLE_RATE
    return duration


def get_wav_duration(filepath: str) -> float:
    """
    Get the duration of a WAV file in seconds.
    
    Args:
        filepath: Path to the WAV file
        
    Returns:
        Duration in seconds
    """
    try:
        with wave.open(filepath, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}")
        return 0.0


# ============================================================================
# API KEY LOADING
# ============================================================================

def load_api_key() -> str:
    """Load OpenAI API key from environment, .env file, or config.json."""
    
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
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
            api_key = config.get("openai_api_key", "")
            if api_key and api_key.startswith("sk-"):
                return api_key
    
    return None


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_audio_files():
    """
    Generate WAV audio files for all scenes using OpenAI TTS.
    Uses PCM format and converts to proper WAV.
    
    Returns:
        List of (scene_num, filepath, duration) tuples
    """
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("=" * 60)
        print("ERROR: OpenAI API key not found!")
        print("=" * 60)
        print("\nProvide via one of these methods:")
        print("  1. Environment variable: set OPENAI_API_KEY=sk-...")
        print("  2. Edit config.json with your API key")
        print("  3. Command line: python generate_audio.py --api-key sk-...")
        sys.exit(1)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Create output directory
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Audio output directory: {AUDIO_DIR.absolute()}")
    
    # Get all narrations
    narrations = get_all_narrations()
    total_scenes = len(narrations)
    
    print(f"\nGenerating audio for {total_scenes} scenes...")
    print("Using PCM format with proper WAV conversion")
    print("=" * 60)
    
    results = []
    
    for i, (scene_name, narration_text) in enumerate(narrations.items(), 1):
        # Zero-padded filename: scene_01.wav, scene_02.wav, etc.
        output_filename = f"scene_{i:02d}.wav"
        output_path = AUDIO_DIR / output_filename
        
        # Also create non-padded version for backward compatibility
        compat_filename = f"scene_{i}.wav"
        compat_path = AUDIO_DIR / compat_filename
        
        print(f"\n[{i}/{total_scenes}] Generating {output_filename}...")
        print(f"  Text: {len(narration_text)} chars, {len(narration_text.split())} words")
        
        try:
            # Call OpenAI TTS API with PCM format
            response = client.audio.speech.create(
                model=TTS_MODEL,
                voice=TTS_VOICE,
                input=narration_text,
                response_format="pcm"  # Raw PCM for proper conversion
            )
            
            # Get PCM data
            pcm_data = response.content
            
            # Convert to proper WAV
            duration = pcm_to_wav(pcm_data, str(output_path))
            
            # Also save with non-padded name for compatibility
            pcm_to_wav(pcm_data, str(compat_path))
            
            file_size = output_path.stat().st_size / 1024
            print(f"  Saved: {output_path} ({file_size:.1f} KB, {duration:.1f}s)")
            
            results.append((i, str(output_path), duration))
            
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((i, str(output_path), 0.0))
            continue
    
    print("\n" + "=" * 60)
    print(f"Generation complete: {len([r for r in results if r[2] > 0])}/{total_scenes} files created")
    
    return results


def verify_audio_files():
    """Verify all audio files and print a diagnostic table."""
    
    print("\n" + "=" * 70)
    print("AUDIO FILE VERIFICATION")
    print("=" * 70)
    print(f"{'Scene':<10} {'Filename':<25} {'Exists':<10} {'Duration':<12} {'Status'}")
    print("-" * 70)
    
    total_duration = 0
    all_valid = True
    
    for i in range(1, get_scene_count() + 1):
        # Check zero-padded filename
        filename_padded = f"scene_{i:02d}.wav"
        filepath_padded = AUDIO_DIR / filename_padded
        
        # Check non-padded filename
        filename = f"scene_{i}.wav"
        filepath = AUDIO_DIR / filename
        
        # Prefer zero-padded, fall back to non-padded
        if filepath_padded.exists():
            use_path = filepath_padded
            use_name = filename_padded
        elif filepath.exists():
            use_path = filepath
            use_name = filename
        else:
            print(f"Scene {i:<4} {filename_padded:<25} {'NO':<10} {'N/A':<12} MISSING")
            all_valid = False
            continue
        
        duration = get_wav_duration(str(use_path))
        
        if duration > 0.5:
            status = "OK"
            total_duration += duration
        elif duration > 0:
            status = "TOO SHORT"
            all_valid = False
        else:
            status = "INVALID"
            all_valid = False
        
        print(f"Scene {i:<4} {use_name:<25} {'YES':<10} {duration:<12.1f}s {status}")
    
    print("-" * 70)
    print(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"All files valid: {'YES' if all_valid else 'NO'}")
    print("=" * 70)
    
    return all_valid


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate audio for Highway Plan Reading video")
    parser.add_argument("--api-key", "-k", help="OpenAI API key")
    parser.add_argument("--verify-only", "-v", action="store_true", help="Only verify existing files")
    args = parser.parse_args()
    
    # Set API key from command line if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    print("=" * 60)
    print("Highway Plan Reading - Audio Generation Script")
    print("=" * 60)
    print(f"\nTTS Model: {TTS_MODEL}")
    print(f"Voice: {TTS_VOICE}")
    print(f"Format: PCM -> WAV ({SAMPLE_RATE}Hz, {SAMPLE_WIDTH*8}-bit, {'mono' if CHANNELS==1 else 'stereo'})")
    
    if args.verify_only:
        verify_audio_files()
    else:
        # Generate audio files
        results = generate_audio_files()
        
        # Verify results
        if results:
            verify_audio_files()
    
    print("\nDone!")
    print("\nNext step: Run the Manim script to render the video with audio:")
    print("  manim -qh page5_7_explainer.py ExplainerScene")
