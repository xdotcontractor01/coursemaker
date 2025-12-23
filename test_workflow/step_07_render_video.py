"""
Step 7: Render Video
Renders the Manim script to create a silent video
Uses dynamic video name from step_03
"""

import subprocess
import time
from shared import *

def main():
    """Render video with Manim"""
    print_step(7, "Render Silent Video")
    
    try:
        # Check if render script exists
        render_file = TEST_DIR / 'render_script.py'
        if not render_file.exists():
            print_error("Render script file not found. Run step_06 first.")
            return 1
        
        print_info(f"Render script: {render_file}")
        
        # Get video name from file (saved by step_03)
        video_name_file = TEST_DIR / 'video_name.txt'
        if video_name_file.exists():
            video_name = video_name_file.read_text().strip()
        else:
            # Fallback to extracting from script
            video_name = get_video_name()
        
        print_info(f"Video class name: {video_name}")
        
        # Run Manim
        media_dir = TEST_DIR / 'media'
        cmd = [
            'manim',
            '-pqh',  # Preview, high quality (1080p)
            '--format', 'mp4',
            '--media_dir', str(media_dir),
            str(render_file),
            video_name
        ]
        
        print_info(f"Running: {' '.join(cmd)}")
        print_info("This may take 3-5 minutes...")
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        print_info(f"Render completed in {elapsed:.1f} seconds")
        
        if result.returncode == 0:
            print_success("Video rendered successfully!")
            
            # Find output video (search for the dynamic name)
            video_files = list(media_dir.glob(f'**/{video_name}.mp4'))
            if not video_files:
                # Try finding any mp4 file
                video_files = list(media_dir.glob('**/*.mp4'))
            
            if video_files:
                video_path = video_files[0]
                print_success(f"Video location: {video_path}")
                print_info(f"Video size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
                
                # Save video path for next steps
                video_path_file = TEST_DIR / 'video_path.txt'
                video_path_file.write_text(str(video_path))
                print_info(f"Video path saved to: {video_path_file}")
                
                return 0
            else:
                print_error("Video file not found after render")
                return 1
        else:
            print_error("Manim render failed!")
            print("\n" + "-"*80)
            print("MANIM ERROR OUTPUT:")
            print(result.stderr[-2000:])  # Last 2000 chars
            print("-"*80)
            return 1
        
    except Exception as e:
        print_error(f"Failed to render video: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
