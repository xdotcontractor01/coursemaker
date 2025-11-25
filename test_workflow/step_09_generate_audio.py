"""
Step 9: Generate Audio Clips
Generates audio clips from narration using edge-tts
"""

import json
from shared import *

def main():
    """Generate audio clips with edge-tts"""
    print_step(9, "Generate Audio Clips")
    
    try:
        import edge_tts
        import asyncio
    except ImportError:
        print_error("edge-tts not installed. Run: pip install edge-tts")
        print_info("Skipping audio generation...")
        # Create empty audio_clips.json
        audio_info_file = TEST_DIR / 'audio_clips.json'
        audio_info_file.write_text('[]')
        return 0
    
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
        
        voice = "en-US-GuyNeural"
        print_info(f"Using voice: {voice}")
        
        async def generate_clip(idx, narration):
            try:
                text = narration.get('narration_text', '')
                output_file = audio_dir / f'clip_{idx}.mp3'
                
                print_info(f"  Generating clip {idx}: {len(text)} characters...")
                
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(str(output_file))
                
                # Verify file was created
                if not output_file.exists():
                    raise Exception(f"Audio file not created: {output_file}")
                
                size = output_file.stat().st_size
                if size == 0:
                    raise Exception(f"Audio file is empty: {output_file}")
                
                print_success(f"  Clip {idx} saved: {size} bytes")
                return str(output_file)
                
            except Exception as e:
                print_error(f"  Failed to generate clip {idx}: {e}")
                raise
        
        async def generate_all():
            results = []
            for i, n in enumerate(narrations):
                try:
                    result = await generate_clip(i, n)
                    results.append(result)
                except Exception as e:
                    print_error(f"Clip {i} generation failed: {e}")
                    # Continue with other clips
            return results
        
        print_info(f"Generating {len(narrations)} audio clips...")
        
        audio_files = asyncio.run(generate_all())
        
        # Verify we got audio files
        if not audio_files or len(audio_files) == 0:
            print_error("No audio files were generated!")
            audio_info_file = TEST_DIR / 'audio_clips.json'
            audio_info_file.write_text('[]')
            return 1
        
        # Check files exist
        valid_files = []
        for audio_file in audio_files:
            audio_path = Path(audio_file)
            if audio_path.exists() and audio_path.stat().st_size > 0:
                valid_files.append(audio_file)
            else:
                print_error(f"Invalid audio file: {audio_file}")
        
        if not valid_files:
            print_error("No valid audio files were generated!")
            audio_info_file = TEST_DIR / 'audio_clips.json'
            audio_info_file.write_text('[]')
            return 1
        
        print_success(f"Successfully generated {len(valid_files)} audio clips")
        
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

