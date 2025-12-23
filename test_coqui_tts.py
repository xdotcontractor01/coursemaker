"""
Test script for Coqui TTS evaluation
Tests various models and measures quality/performance
"""

import time
import os
from pathlib import Path

# Create output directory
OUTPUT_DIR = Path("test_coqui_output")
OUTPUT_DIR.mkdir(exist_ok=True)

def test_basic_tts():
    """Test basic TTS functionality with default model"""
    print("\n" + "="*60)
    print("TEST 1: Basic TTS with default model")
    print("="*60)
    
    try:
        import torch
        from TTS.api import TTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Use a fast, lightweight model for initial test
        print("\nInitializing TTS (this may download a model on first run)...")
        start_time = time.time()
        
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
        
        init_time = time.time() - start_time
        print(f"Model initialization time: {init_time:.2f}s")
        
        # Test text
        test_text = "Hello! This is a test of the Coqui text-to-speech system. It provides high-quality neural voice synthesis."
        
        output_file = OUTPUT_DIR / "test_basic.wav"
        
        print(f"\nGenerating speech for: '{test_text[:50]}...'")
        start_time = time.time()
        
        tts.tts_to_file(text=test_text, file_path=str(output_file))
        
        gen_time = time.time() - start_time
        file_size = output_file.stat().st_size / 1024
        
        print(f"✓ Generation time: {gen_time:.2f}s")
        print(f"✓ Output file: {output_file}")
        print(f"✓ File size: {file_size:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_speedy_speech():
    """Test with speedy-speech model (faster but lower quality)"""
    print("\n" + "="*60)
    print("TEST 2: Speedy Speech model (fast synthesis)")
    print("="*60)
    
    try:
        import torch
        from TTS.api import TTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("Loading speedy-speech model...")
        start_time = time.time()
        
        tts = TTS("tts_models/en/ljspeech/speedy-speech").to(device)
        
        init_time = time.time() - start_time
        print(f"Model initialization time: {init_time:.2f}s")
        
        test_text = "This is a faster model that may be suitable for real-time applications. The quality is lower but generation is quicker."
        
        output_file = OUTPUT_DIR / "test_speedy.wav"
        
        print(f"\nGenerating speech...")
        start_time = time.time()
        
        tts.tts_to_file(text=test_text, file_path=str(output_file))
        
        gen_time = time.time() - start_time
        file_size = output_file.stat().st_size / 1024
        
        print(f"✓ Generation time: {gen_time:.2f}s")
        print(f"✓ Output file: {output_file}")
        print(f"✓ File size: {file_size:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vits_model():
    """Test VITS model (good balance of quality and speed)"""
    print("\n" + "="*60)
    print("TEST 3: VITS model (balanced quality/speed)")
    print("="*60)
    
    try:
        import torch
        from TTS.api import TTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("Loading VITS model...")
        start_time = time.time()
        
        # VITS is generally the best balance
        tts = TTS("tts_models/en/ljspeech/vits").to(device)
        
        init_time = time.time() - start_time
        print(f"Model initialization time: {init_time:.2f}s")
        
        test_text = "The VITS model provides excellent quality speech synthesis with reasonable generation speed. It's often the best choice for offline applications."
        
        output_file = OUTPUT_DIR / "test_vits.wav"
        
        print(f"\nGenerating speech...")
        start_time = time.time()
        
        tts.tts_to_file(text=test_text, file_path=str(output_file))
        
        gen_time = time.time() - start_time
        file_size = output_file.stat().st_size / 1024
        
        print(f"✓ Generation time: {gen_time:.2f}s")
        print(f"✓ Output file: {output_file}")
        print(f"✓ File size: {file_size:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_speaker():
    """Test multi-speaker model with voice cloning capability"""
    print("\n" + "="*60)
    print("TEST 4: Multi-speaker VCTK model (multiple voices)")
    print("="*60)
    
    try:
        import torch
        from TTS.api import TTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("Loading multi-speaker model...")
        start_time = time.time()
        
        tts = TTS("tts_models/en/vctk/vits").to(device)
        
        init_time = time.time() - start_time
        print(f"Model initialization time: {init_time:.2f}s")
        
        # Get available speakers
        speakers = tts.speakers
        if speakers:
            print(f"Available speakers: {len(speakers)}")
            print(f"Sample speakers: {speakers[:5]}...")
        
        test_text = "This model supports multiple different voices. Each speaker has a unique voice characteristic."
        
        # Test with a few different speakers
        for i, speaker in enumerate(speakers[:3] if speakers else [None]):
            output_file = OUTPUT_DIR / f"test_multispeaker_{i}.wav"
            
            print(f"\nGenerating with speaker: {speaker}")
            start_time = time.time()
            
            if speaker:
                tts.tts_to_file(text=test_text, speaker=speaker, file_path=str(output_file))
            else:
                tts.tts_to_file(text=test_text, file_path=str(output_file))
            
            gen_time = time.time() - start_time
            print(f"✓ Generation time: {gen_time:.2f}s - {output_file.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_available_models():
    """List all available TTS models"""
    print("\n" + "="*60)
    print("AVAILABLE MODELS")
    print("="*60)
    
    try:
        from TTS.api import TTS
        
        # Get list of models
        print("\nEnglish TTS models:")
        models = TTS().list_models()
        
        # Filter English models
        english_models = [m for m in models if '/en/' in m or 'multilingual' in m]
        for model in english_models[:15]:  # Show first 15
            print(f"  - {model}")
        
        if len(english_models) > 15:
            print(f"  ... and {len(english_models) - 15} more")
            
        return True
        
    except Exception as e:
        print(f"✗ Error listing models: {e}")
        return False


def test_longer_text():
    """Test with longer narration-style text (similar to your use case)"""
    print("\n" + "="*60)
    print("TEST 5: Longer narration text (course-style content)")
    print("="*60)
    
    try:
        import torch
        from TTS.api import TTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Use Tacotron2-DDC for this test (doesn't require espeak)
        print("Loading Tacotron2-DDC model for narration test...")
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
        
        # Longer educational text
        narration_text = """
        Welcome to this course on machine learning fundamentals. 
        In this section, we'll explore the basic concepts that underpin modern artificial intelligence.
        Machine learning is a subset of AI that enables computers to learn from data without being explicitly programmed.
        There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.
        Let's start by understanding supervised learning, which is the most common approach.
        """
        
        output_file = OUTPUT_DIR / "test_narration.wav"
        
        print(f"Text length: {len(narration_text)} characters")
        print("Generating narration...")
        start_time = time.time()
        
        tts.tts_to_file(text=narration_text, file_path=str(output_file))
        
        gen_time = time.time() - start_time
        file_size = output_file.stat().st_size / 1024
        
        # Calculate approximate audio duration (rough estimate: 22050 sample rate, 16-bit)
        estimated_duration = (file_size * 1024) / (22050 * 2)  # Very rough
        
        print(f"✓ Generation time: {gen_time:.2f}s")
        print(f"✓ Output file: {output_file}")
        print(f"✓ File size: {file_size:.1f} KB")
        print(f"✓ Characters per second: {len(narration_text) / gen_time:.1f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("COQUI TTS EVALUATION TEST")
    print("="*60)
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    
    results = {}
    
    # List models first
    list_available_models()
    
    # Run tests
    results["Basic TTS"] = test_basic_tts()
    results["Speedy Speech"] = test_speedy_speech()
    results["VITS"] = test_vits_model()
    results["Multi-speaker"] = test_multi_speaker()
    results["Long Narration"] = test_longer_text()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nGenerated audio files are in: {OUTPUT_DIR.absolute()}")
    print("\nTo play the files, open them with any audio player.")
    
    # Comparison with current solution
    print("\n" + "="*60)
    print("COMPARISON WITH CURRENT SOLUTION (edge-tts)")
    print("="*60)
    print("""
    Coqui TTS (local):
      + Works offline (no internet required)
      + No rate limits or API costs
      + Can fine-tune models for custom voices
      + Better privacy (data stays local)
      - Requires more CPU/GPU resources
      - Initial model download is large
      - May be slower than edge-tts on CPU
    
    Edge-TTS (current):
      + Very fast (runs on Microsoft servers)
      + High quality neural voices
      + No local compute needed
      + Easy to use
      - Requires internet connection
      - Potential rate limits
      - Less control over voice characteristics
    """)


if __name__ == "__main__":
    main()

