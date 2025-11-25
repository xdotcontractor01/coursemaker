"""
Step 6: Inject Images into Manim Script
Injects downloaded images into the Manim script with smart layouts
"""

import re
import json
from shared import *

# Layout type constants
class LayoutType:
    BACKGROUND_ONLY = "background_only"
    SPLIT_LEFT = "split_left"
    SPLIT_RIGHT = "split_right"
    SIDEBAR_RIGHT = "sidebar_right"

# Layout region configurations
def get_layout_regions(layout_type, has_title=True):
    """Get layout regions for different layout types"""
    if layout_type == LayoutType.BACKGROUND_ONLY:
        return {
            'image': {'width': 14.2, 'height': 8.0, 'center': [0, 0]}
        }
    elif layout_type == LayoutType.SPLIT_RIGHT:
        return {
            'content': {'width': 7.0, 'height': 6.0, 'center': [-3.5, -0.5]},
            'image': {'width': 5.5, 'height': 6.0, 'center': [3.2, -0.5]}
        }
    elif layout_type == LayoutType.SPLIT_LEFT:
        return {
            'image': {'width': 5.5, 'height': 6.0, 'center': [-3.2, -0.5]},
            'content': {'width': 7.0, 'height': 6.0, 'center': [3.5, -0.5]}
        }
    elif layout_type == LayoutType.SIDEBAR_RIGHT:
        return {
            'content': {'width': 9.0, 'height': 6.0, 'center': [-2.0, -0.5]},
            'image': {'width': 4.0, 'height': 4.0, 'center': [4.5, -0.5]}
        }
    else:
        # Default to split_right
        return {
            'content': {'width': 7.0, 'height': 6.0, 'center': [-3.5, -0.5]},
            'image': {'width': 5.5, 'height': 6.0, 'center': [3.2, -0.5]}
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
        
        # Strategy: Inject images AND their display animations
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
                layout_str = img_data['layout']
                # Convert layout string to constant
                if layout_str == "background_only":
                    layout = LayoutType.BACKGROUND_ONLY
                elif layout_str == "split_left":
                    layout = LayoutType.SPLIT_LEFT
                elif layout_str == "split_right":
                    layout = LayoutType.SPLIT_RIGHT
                elif layout_str == "sidebar_right":
                    layout = LayoutType.SIDEBAR_RIGHT
                else:
                    layout = LayoutType.SPLIT_RIGHT  # default
                
                print_info(f"Injecting image for slide {current_slide} with layout: {layout_str}")
                
                # Get the indentation from the current line
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Build image code
                img_code_lines = [
                    f"{indent_str}# [AUTO-INJECTED] Image for slide {current_slide}",
                    f"{indent_str}img_{current_slide} = ImageMobject(r\"{img_path}\")",
                ]
                
                if layout == LayoutType.BACKGROUND_ONLY:
                    img_code_lines.extend([
                        f"{indent_str}img_{current_slide}.scale_to_fit_width(config.frame_width)",
                        f"{indent_str}img_{current_slide}.scale_to_fit_height(config.frame_height)",
                        f"{indent_str}img_{current_slide}.set_opacity(0.25)",
                        f"{indent_str}self.add(img_{current_slide})  # Background layer",
                        ""
                    ])
                else:
                    # Non-background: position and animate
                    regions = get_layout_regions(layout, has_title=True)
                    img_region = regions['image']
                    img_code_lines.extend([
                        f"{indent_str}img_{current_slide}.scale_to_fit_width({img_region['width']:.2f})",
                        f"{indent_str}img_{current_slide}.scale_to_fit_height({img_region['height']:.2f})",
                        f"{indent_str}img_{current_slide}.move_to(RIGHT * {img_region['center'][0]:.2f} + UP * {img_region['center'][1]:.2f})",
                        f"{indent_str}self.play(FadeIn(img_{current_slide}), run_time=0.5)  # Show image",
                        ""
                    ])
                
                # Add image code
                modified_lines.extend(img_code_lines)
                
                # Now add back the original self.play() line
                modified_lines.append(line)
                
                # Mark as injected
                slide_image_injected[current_slide] = True
            
            # Handle fadeout - add image to the fadeout group
            elif (line.strip().startswith('self.play(FadeOut(') and 
                  current_slide in downloaded_images and 
                  slide_image_injected.get(current_slide, False)):
                
                # Modify the fadeout to include the image
                if 'VGroup' in line:
                    # Change VGroup to Group for ImageMobject compatibility
                    modified_line = line.replace('VGroup(', 'Group(')
                    # Add image to the fadeout
                    modified_line = modified_line.replace('), run_time', f', img_{current_slide}), run_time')
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

