"""
Master Script: Run All Workflow Steps
Executes all 11 steps sequentially and displays summary report
"""

import sys
from datetime import datetime
from pathlib import Path

# Import shared utilities
from shared import TEST_DIR, print_step, print_success, print_error, print_info

# Import all step modules
import step_00_load_prompts
import step_01_validate_input
import step_02_generate_summary
import step_03_generate_base_script
import step_04_suggest_images
import step_05_download_images
import step_06_inject_images
import step_07_render_video
import step_08_generate_narration
import step_09_generate_audio
import step_10_merge_audio_video

def calculate_total_tokens():
    """Calculate total tokens used across all steps"""
    token_files = [
        'tokens_step_02.txt',
        'tokens_step_03.txt',
        'tokens_step_04.txt',
        'tokens_step_08.txt'
    ]
    total = 0
    for token_file in token_files:
        file_path = TEST_DIR / token_file
        if file_path.exists():
            try:
                total += int(file_path.read_text().strip())
            except:
                pass
    return total

def show_quality_report():
    """Display quality assessment report"""
    print("="*80)
    print("VIDEO QUALITY REPORT")
    print("="*80)
    
    # Check generated script for quality
    script_file = TEST_DIR / 'render_script.py'
    if not script_file.exists():
        script_file = TEST_DIR / 'base_script.py'
    
    if script_file.exists():
        script_content = script_file.read_text()
        
        # Count visual elements
        rectangles = script_content.count('Rectangle(')
        circles = script_content.count('Circle(')
        arrows = script_content.count('Arrow(')
        lines = script_content.count('Line(')
        polygons = script_content.count('Polygon(')
        total_shapes = rectangles + circles + arrows + lines + polygons
        
        # Count images
        image_count = script_content.count('ImageMobject(')
        injected_count = script_content.count('[AUTO-INJECTED]')
        
        # Count text elements
        text_count = script_content.count('Text(')
        vgroups = script_content.count('VGroup')
        
        print(f"Visual Elements:")
        print(f"  Shapes: {total_shapes} (Rectangles: {rectangles}, Circles: {circles}, Arrows: {arrows}, Lines: {lines}, Polygons: {polygons})")
        print(f"  Text objects: {text_count}")
        print(f"  VGroups: {vgroups}")
        print(f"  Images: {image_count} ({injected_count} auto-injected)")
        print(f"  White background: {'YES' if 'WHITE' in script_content else 'NO'}")
        
        # Quality assessment
        print(f"\nQuality Assessment:")
        if total_shapes >= 15:
            print(f"  Visual Richness: EXCELLENT ({total_shapes} shapes)")
        elif total_shapes >= 10:
            print(f"  Visual Richness: GOOD ({total_shapes} shapes)")
        elif total_shapes >= 5:
            print(f"  Visual Richness: FAIR (~{total_shapes} shapes, could be better)")
        else:
            print(f"  Visual Richness: POOR (only {total_shapes} shapes)")
        
        if text_count >= 10:
            print(f"  Text Content: GOOD ({text_count} text elements)")
        else:
            print(f"  Text Content: NEEDS MORE ({text_count} text elements)")
        
        if vgroups >= 3:
            print(f"  Organization: EXCELLENT ({vgroups} VGroups)")
        else:
            print(f"  Organization: BASIC ({vgroups} VGroups)")
        
        if image_count > 0:
            print(f"  Images: INTEGRATED ({image_count} images, {injected_count} auto-placed)")
        else:
            print(f"  Images: NONE")
    
    # Audio check
    audio_dir = TEST_DIR / 'audio_clips'
    if audio_dir.exists():
        audio_files = list(audio_dir.glob('*.mp3'))
        if audio_files:
            print(f"\nAudio:")
            print(f"  Clips generated: {len(audio_files)}")
            total_size = sum(f.stat().st_size for f in audio_files)
            print(f"  Total audio size: {total_size / 1024:.2f} KB")
    
    # Video check
    final_video_path_file = TEST_DIR / 'final_video_path.txt'
    video_path_file = TEST_DIR / 'video_path.txt'
    
    if final_video_path_file.exists():
        final_path = final_video_path_file.read_text().strip()
        if Path(final_path).exists():
            print(f"\nFinal Output:")
            print(f"  Video with audio: YES")
            print(f"  Location: {final_path}")
            print(f"  Size: {Path(final_path).stat().st_size / 1024 / 1024:.2f} MB")
    elif video_path_file.exists():
        video_path = video_path_file.read_text().strip()
        if Path(video_path).exists():
            print(f"\nFinal Output:")
            print(f"  Silent video: YES")
            print(f"  Location: {video_path}")
            print(f"  Size: {Path(video_path).stat().st_size / 1024 / 1024:.2f} MB")
    
    print("\n" + "="*80)

def main():
    """Run complete workflow"""
    print("\n")
    print("="*80)
    print("GDOT VIDEO GENERATION - COMPLETE WORKFLOW")
    print("="*80)
    print(f"Output directory: {TEST_DIR.absolute()}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")
    
    # Check for input file argument
    input_file = None
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print_info(f"Using input file: {input_file}")
    
    steps = [
        ("Step 0", step_00_load_prompts),
        ("Step 1", step_01_validate_input),
        ("Step 2", step_02_generate_summary),
        ("Step 3", step_03_generate_base_script),
        ("Step 4", step_04_suggest_images),
        ("Step 5", step_05_download_images),
        ("Step 6", step_06_inject_images),
        ("Step 7", step_07_render_video),
        ("Step 8", step_08_generate_narration),
        ("Step 9", step_09_generate_audio),
        ("Step 10", step_10_merge_audio_video),
    ]
    
    failed_steps = []
    
    for step_name, step_module in steps:
        try:
            print_info(f"Running {step_name}...")
            # Pass input file to step 1 if provided
            if step_name == "Step 1" and input_file:
                # Temporarily modify sys.argv to pass input file
                original_argv = sys.argv[:]
                sys.argv = [sys.argv[0], input_file]
                result = step_module.main()
                sys.argv = original_argv
            else:
                result = step_module.main()
            if result != 0:
                print_error(f"{step_name} failed with exit code {result}")
                failed_steps.append(step_name)
                # Continue with other steps even if one fails
        except Exception as e:
            print_error(f"{step_name} raised exception: {e}")
            failed_steps.append(step_name)
            import traceback
            traceback.print_exc()
            # Continue with other steps
    
    # Summary
    print("\n")
    print("="*80)
    print("WORKFLOW COMPLETE!")
    print("="*80)
    
    if failed_steps:
        print_error(f"Failed steps: {', '.join(failed_steps)}")
    else:
        print_success("All steps completed successfully!")
    
    total_tokens = calculate_total_tokens()
    print(f"[INFO] Total tokens used: {total_tokens}")
    print(f"[INFO] Output directory: {TEST_DIR.absolute()}")
    
    print("\nFiles generated:")
    for file in sorted(TEST_DIR.rglob('*')):
        if file.is_file():
            size = file.stat().st_size
            rel_path = file.relative_to(TEST_DIR)
            print(f"  - {rel_path} ({size:,} bytes)")
    print("\n")
    
    # Quality Report
    show_quality_report()
    
    print("\nNext Steps:")
    print("1. Watch the final video")
    print("2. Review the generated script in test_output/render_script.py")
    print("3. Run individual steps to debug or regenerate specific parts")
    print("4. If quality is good, integrate changes into main workflow")
    print("="*80 + "\n")
    
    return 0 if not failed_steps else 1

if __name__ == "__main__":
    exit(main())

