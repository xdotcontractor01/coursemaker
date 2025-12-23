"""
Step 9: Generate Audio Clips
Generates audio clips using Coqui TTS (primary) with pyttsx3 as fallback
"""

import json
import time
from shared import *

# Coqui TTS settings
COQUI_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"


def generate_with_coqui_tts(narrations, audio_dir):
    """Primary TTS using Coqui TTS (offline, high quality)"""
    try:
        import torch
        from TTS.api import TTS
        
        print_info("Using Coqui TTS (offline, local processing)...")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print_info(f"Using device: {device}")
        
        print_info(f"Loading model: {COQUI_MODEL}")
        start_load = time.time()
        tts = TTS(COQUI_MODEL).to(device)
        print_info(f"Model loaded in {time.time() - start_load:.1f}s")
        
        audio_files = []
        for i, narration in enumerate(narrations):
            text = narration.get('narration_text', '')
            if not text.strip():
                print_error(f"  Clip {i}: Empty narration text!")
                continue
            
            # Coqui TTS outputs WAV
            output_file = audio_dir / f'clip_{i}.wav'
            
            print_info(f"  Generating clip {i}: {len(text)} chars...")
            
            try:
                start_time = time.time()
                tts.tts_to_file(text=text, file_path=str(output_file))
                gen_time = time.time() - start_time
                
                if output_file.exists() and output_file.stat().st_size > 0:
                    size = output_file.stat().st_size / 1024
                    print_success(f"  Clip {i} saved: {size:.1f} KB ({gen_time:.1f}s)")
                    audio_files.append(str(output_file))
                else:
                    print_error(f"  Clip {i} generation failed - empty file")
                    
            except Exception as e:
                print_error(f"  Clip {i} failed: {e}")
        
        return audio_files
        
    except ImportError as e:
        print_error(f"Coqui TTS not available: {e}")
        print_info("Install with: pip install TTS (requires Python 3.9-3.11)")
        print_info("Or use the coqui_test_env virtual environment")
        return []
    except Exception as e:
        print_error(f"Coqui TTS failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def generate_with_pyttsx3(narrations, audio_dir):
    """Fallback TTS using pyttsx3 (offline, works without internet)"""
    try:
        import pyttsx3
        
        print_info("Using pyttsx3 (offline TTS) as fallback...")
        engine = pyttsx3.init()
        
        # Configure voice
        voices = engine.getProperty('voices')
        # Try to find an English voice
        for voice in voices:
            if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                print_info(f"Using voice: {voice.name}")
                break
        
        # Set properties
        engine.setProperty('rate', 150)  # Words per minute
        engine.setProperty('volume', 0.9)
        
        audio_files = []
        for i, narration in enumerate(narrations):
            text = narration.get('narration_text', '')
            if not text.strip():
                continue
            
            # pyttsx3 saves to wav
            output_file = audio_dir / f'clip_{i}.wav'
            
            print_info(f"  Generating clip {i}: {len(text)} chars...")
            
            try:
                # Clean up any existing files
                if output_file.exists():
                    output_file.unlink()
                
                engine.save_to_file(text, str(output_file))
                engine.runAndWait()
                
                if output_file.exists() and output_file.stat().st_size > 0:
                    print_success(f"  Clip {i} saved: {output_file.stat().st_size / 1024:.1f} KB")
                    audio_files.append(str(output_file))
                else:
                    print_error(f"  Clip {i} generation failed - empty file")
            except Exception as e:
                print_error(f"  Clip {i} failed: {e}")
        
        return audio_files
        
    except ImportError:
        print_error("pyttsx3 not installed. Run: pip install pyttsx3")
        return []
    except Exception as e:
        print_error(f"pyttsx3 fallback failed: {e}")
        return []


def main():
    """Generate audio clips with Coqui TTS as primary"""
    print_step(9, "Generate Audio Clips")
    
    try:
        # Read narration
        narration_file = TEST_DIR / 'narration.json'
        if not narration_file.exists():
            print_error("Narration file not found. Run step_08 first.")
            return 1
        narrations = json.loads(narration_file.read_text())
        
        print_info(f"Loaded {len(narrations)} narration clips")
        
        # Create audio directory
        audio_dir = TEST_DIR / 'audio_clips'
        audio_dir.mkdir(exist_ok=True)
        
        # Clear any existing audio files
        for f in audio_dir.glob('*.mp3'):
            f.unlink()
        for f in audio_dir.glob('*.wav'):
            f.unlink()
        
        audio_files = []
        
        # Try Coqui TTS first (primary - offline, good quality)
        print_info("\n=== Trying Coqui TTS (primary) ===")
        audio_files = generate_with_coqui_tts(narrations, audio_dir)
        
        # If Coqui TTS failed, try pyttsx3
        if not audio_files:
            print_info("\n=== Falling back to pyttsx3 ===")
            audio_files = generate_with_pyttsx3(narrations, audio_dir)
        
        # Verify we got audio files
        if not audio_files or len(audio_files) == 0:
            print_error("No audio files were generated!")
            print_info("\nTo enable Coqui TTS:")
            print_info("  1. Use Python 3.11: coqui_test_env\\Scripts\\python.exe")
            print_info("  2. Or install TTS: pip install TTS (Python 3.9-3.11)")
            print_info("\nAlternatively, install pyttsx3:")
            print_info("  pip install pyttsx3")
            audio_info_file = TEST_DIR / 'audio_clips.json'
            audio_info_file.write_text('[]')
            return 1
        
        # Check files exist
        valid_files = []
        for audio_file in audio_files:
            audio_path = Path(audio_file)
            if audio_path.exists() and audio_path.stat().st_size > 0:
                valid_files.append(audio_file)
        
        if not valid_files:
            print_error("No valid audio files were generated!")
            audio_info_file = TEST_DIR / 'audio_clips.json'
            audio_info_file.write_text('[]')
            return 1
        
        print_success(f"\nSuccessfully generated {len(valid_files)} audio clips")
        
        # Show summary
        total_size = sum(Path(f).stat().st_size for f in valid_files)
        print_info(f"Total audio size: {total_size / 1024:.2f} KB")
        
        # Save audio files list
        audio_info_file = TEST_DIR / 'audio_clips.json'
        audio_info_file.write_text(json.dumps(valid_files, indent=2))
        print_info(f"Audio clips info saved to: {audio_info_file}")
        
        return 0
        
    except Exception as e:
        print_error(f"Failed to generate audio: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
