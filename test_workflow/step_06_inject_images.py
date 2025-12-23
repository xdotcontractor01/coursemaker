"""
Step 6: Inject Images into Manim Script
Injects downloaded images into the Manim script - positioned in top-right corner
with "Reference Image" label below to avoid disturbing main content layout.
"""

import re
import json
from shared import *

# Image positioning configuration
# Top-right corner placement - non-intrusive to main content
IMAGE_CONFIG = {
    'width': 3.0,          # Small width to not interfere
    'height': 2.0,         # Small height
    'x_pos': 5.5,          # Right side (positive X)
    'y_pos': 2.5,          # Top area (positive Y, below title)
    'label_offset': -0.3,  # Label position below image
    'label_font_size': 14, # Small font for label
    'opacity': 0.95,       # Slightly transparent
}

def main():
    """Inject images into Manim script"""
    print_step(6, "Inject Images into Script")
    
    try:
        # Read base script
        base_script_file = TEST_DIR / 'base_script.py'
        if not base_script_file.exists():
            print_error("Base script file not found. Run step_03 first.")
            return 1
        base_script = base_script_file.read_text(encoding='utf-8')
        
        # Read downloaded images metadata
        downloaded_file = TEST_DIR / 'downloaded_images.json'
        if not downloaded_file.exists():
            print_error("Downloaded images file not found. Run step_05 first.")
            return 1
        downloaded_images_data = json.loads(downloaded_file.read_text())
        
        # Convert string keys to int
        downloaded_images = {}
        for key, value in downloaded_images_data.items():
            downloaded_images[int(key)] = value
        
        if not downloaded_images:
            print_info("No images to inject, using original script")
            # Copy base script to render script
            render_file = TEST_DIR / 'render_script.py'
            render_file.write_text(base_script, encoding='utf-8')
            print_info(f"Render script (no images): {render_file}")
            return 0
        
        print_info(f"Injecting {len(downloaded_images)} images into script")
        print_info(f"Image placement: Top-right corner ({IMAGE_CONFIG['x_pos']}, {IMAGE_CONFIG['y_pos']})")
        print_info(f"Image size: {IMAGE_CONFIG['width']}x{IMAGE_CONFIG['height']}")
        
        # Strategy: Inject images in top-right corner with "Reference Image" label
        lines = base_script.split('\n')
        modified_lines = []
        current_slide = 0
        slide_image_injected = {}  # Track if we've injected for this slide
        
        for i, line in enumerate(lines):
            # Detect slide start
            if line.strip().startswith('# Slide'):
                slide_match = re.search(r'# Slide (\d+)', line)
                if slide_match:
                    current_slide = int(slide_match.group(1))
                    slide_image_injected[current_slide] = False
            
            # Add the original line
            modified_lines.append(line)
            
            # Check if this is the first self.play() in a slide with an image
            if (line.strip().startswith('self.play(') and 
                current_slide in downloaded_images and 
                not slide_image_injected.get(current_slide, False)):
                
                # Inject image code BEFORE this line
                modified_lines.pop()  # Remove the self.play line we just added
                
                img_data = downloaded_images[current_slide]
                img_path = img_data['path']
                
                print_info(f"Injecting image for slide {current_slide} -> top-right corner")
                
                # Get the indentation from the current line
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Build image code - TOP RIGHT CORNER placement
                # Image positioned at top-right, with "Reference Image" label below
                img_code_lines = [
                    f"{indent_str}# [AUTO-INJECTED] Reference image for slide {current_slide} (top-right corner)",
                    f"{indent_str}img_{current_slide} = ImageMobject(r\"{img_path}\")",
                    f"{indent_str}img_{current_slide}.set_height({IMAGE_CONFIG['height']})",
                    f"{indent_str}img_{current_slide}.set_width({IMAGE_CONFIG['width']})",
                    f"{indent_str}img_{current_slide}.move_to(RIGHT * {IMAGE_CONFIG['x_pos']} + UP * {IMAGE_CONFIG['y_pos']})",
                    f"{indent_str}img_{current_slide}.set_opacity({IMAGE_CONFIG['opacity']})",
                    f"{indent_str}# Label below the image",
                    f"{indent_str}img_label_{current_slide} = Text(\"Reference Image\", color=GRAY, font_size={IMAGE_CONFIG['label_font_size']})",
                    f"{indent_str}img_label_{current_slide}.next_to(img_{current_slide}, DOWN, buff=0.1)",
                    f"{indent_str}# Group image and label together (use Group instead of VGroup for ImageMobject)",
                    f"{indent_str}img_group_{current_slide} = Group(img_{current_slide}, img_label_{current_slide})",
                    f"{indent_str}self.play(FadeIn(img_group_{current_slide}), run_time=0.5)",
                    ""
                ]
                
                # Add image code
                modified_lines.extend(img_code_lines)
                
                # Now add back the original self.play() line
                modified_lines.append(line)
                
                # Mark as injected
                slide_image_injected[current_slide] = True
            
            # Handle fadeout - add image group to the fadeout
            elif (line.strip().startswith('self.play(FadeOut(') and 
                  current_slide in downloaded_images and 
                  slide_image_injected.get(current_slide, False)):
                
                # Modify the fadeout to include the image group
                if 'VGroup' in line or 'Group(' in line:
                    # Add image group to the fadeout
                    modified_line = line.replace('), run_time', f', img_group_{current_slide}), run_time')
                    modified_lines[-1] = modified_line
        
        final_script = '\n'.join(modified_lines)
        
        # Save modified script
        render_file = TEST_DIR / 'render_script.py'
        render_file.write_text(final_script, encoding='utf-8')
        print_info(f"Modified script saved to: {render_file}")
        
        # Count injected images
        injected_count = final_script.count('[AUTO-INJECTED]')
        print_success(f"Injected {injected_count} images with display animations")
        
        return 0
        
    except Exception as e:
        print_error(f"Failed to inject images: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

