"""
Smart Content Injector
Analyzes Manim scripts and intelligently repositions content when adding images
"""

import re
from typing import List, Dict, Tuple
from layout_manager_v2 import LayoutManager, LayoutType, AlignmentGuide


class ContentAnalyzer:
    """Analyzes Manim script content and identifies elements to reposition"""
    
    @staticmethod
    def find_slide_boundaries(script_lines: List[str]) -> Dict[int, Tuple[int, int]]:
        """
        Find start and end line numbers for each slide
        
        Returns:
            Dict mapping slide_no -> (start_line, end_line)
        """
        slide_boundaries = {}
        current_slide = None
        slide_start = None
        
        for i, line in enumerate(script_lines):
            # Detect slide start
            slide_match = re.match(r'\s*# Slide (\d+)', line)
            if slide_match:
                # Save previous slide if exists
                if current_slide is not None and slide_start is not None:
                    slide_boundaries[current_slide] = (slide_start, i - 1)
                
                # Start new slide
                current_slide = int(slide_match.group(1))
                slide_start = i
        
        # Save last slide
        if current_slide is not None and slide_start is not None:
            slide_boundaries[current_slide] = (slide_start, len(script_lines) - 1)
        
        return slide_boundaries
    
    @staticmethod
    def find_variable_definitions(script_lines: List[str], start_line: int, end_line: int) -> List[Tuple[int, str]]:
        """
        Find all variable definitions in a slide (shapes, text, VGroups)
        
        Returns:
            List of (line_number, variable_name) tuples
        """
        variables = []
        
        for i in range(start_line, end_line + 1):
            line = script_lines[i].strip()
            
            # Match variable assignments for Manim objects
            # e.g., "beam = Rectangle(...)", "title = Text(...)", "diagram = VGroup(...)"
            match = re.match(r'(\w+)\s*=\s*(Rectangle|Circle|Arrow|Line|Polygon|Text|VGroup|Tex|MathTex|ImageMobject)\(', line)
            if match:
                var_name = match.group(1)
                variables.append((i, var_name))
        
        return variables
    
    @staticmethod
    def find_content_group_candidates(script_lines: List[str], start_line: int, end_line: int) -> List[str]:
        """
        Find VGroup variables that group content together
        
        Returns:
            List of VGroup variable names
        """
        vgroups = []
        
        for i in range(start_line, end_line + 1):
            line = script_lines[i].strip()
            
            # Match VGroup definitions
            match = re.match(r'(\w+)\s*=\s*VGroup\(', line)
            if match:
                var_name = match.group(1)
                # Skip title-only VGroups
                if 'title' not in var_name.lower():
                    vgroups.append(var_name)
        
        return vgroups
    
    @staticmethod
    def wrap_content_in_group(script_lines: List[str], start_line: int, end_line: int, 
                            slide_no: int, exclude_title: bool = True) -> Tuple[List[str], str]:
        """
        Wrap all content (except title) in a VGroup for easy repositioning
        
        Returns:
            (modified_script_lines, group_variable_name)
        """
        # Find all variable definitions except title
        variables = []
        
        for i in range(start_line, end_line + 1):
            line = script_lines[i].strip()
            
            # Match variable assignments
            match = re.match(r'(\w+)\s*=\s*', line)
            if match:
                var_name = match.group(1)
                # Skip title and image variables
                if exclude_title and 'title' in var_name.lower():
                    continue
                if 'img_' in var_name.lower():
                    continue
                variables.append(var_name)
        
        # If we found variables, create a content group
        if not variables:
            return script_lines, None
        
        # Find where to insert the content group (after all definitions, before first self.play)
        insert_line = None
        for i in range(start_line, end_line + 1):
            if 'self.play(' in script_lines[i]:
                insert_line = i
                break
        
        if insert_line is None:
            return script_lines, None
        
        # Create content group
        group_name = f"content_slide_{slide_no}"
        indent = len(script_lines[insert_line]) - len(script_lines[insert_line].lstrip())
        indent_str = ' ' * indent
        
        # Filter out duplicate variables (sometimes shapes are in VGroups)
        unique_vars = list(dict.fromkeys(variables))  # Preserve order, remove dupes
        
        content_group_line = f"{indent_str}{group_name} = VGroup({', '.join(unique_vars)})\n"
        
        # Insert the content group
        modified_lines = script_lines[:insert_line] + [content_group_line] + script_lines[insert_line:]
        
        return modified_lines, group_name


class SmartContentInjector:
    """
    Intelligently injects images and repositions content with proper alignment
    """
    
    @staticmethod
    def inject_images_with_alignment(base_script: str, downloaded_images: Dict[int, Dict],
                                     verbose: bool = True) -> str:
        """
        Inject images and reposition content to prevent overlaps
        
        Args:
            base_script: Original Manim script as string
            downloaded_images: Dict mapping slide_no -> {'path': ..., 'layout': ...}
            verbose: Print debug information
            
        Returns:
            Modified script with properly aligned images and content
        """
        if not downloaded_images:
            return base_script
        
        script_lines = base_script.split('\n')
        analyzer = ContentAnalyzer()
        
        # Find slide boundaries
        slide_boundaries = analyzer.find_slide_boundaries(script_lines)
        
        if verbose:
            print(f"[INJECTOR] Found {len(slide_boundaries)} slides")
            print(f"[INJECTOR] Injecting images for slides: {list(downloaded_images.keys())}")
        
        # Process each slide that has an image
        for slide_no in sorted(downloaded_images.keys()):
            if slide_no not in slide_boundaries:
                if verbose:
                    print(f"[INJECTOR] Warning: Slide {slide_no} not found in script")
                continue
            
            start_line, end_line = slide_boundaries[slide_no]
            img_data = downloaded_images[slide_no]
            img_path = img_data['path']
            layout_str = img_data['layout']
            layout_type = LayoutType(layout_str)
            
            if verbose:
                print(f"[INJECTOR] Processing slide {slide_no}: {layout_str} layout")
            
            # Step 1: Find first self.play() in slide
            first_play_line = None
            for i in range(start_line, end_line + 1):
                if 'self.play(' in script_lines[i] and not '[AUTO-INJECTED]' in script_lines[i]:
                    first_play_line = i
                    break
            
            if first_play_line is None:
                if verbose:
                    print(f"[INJECTOR] Warning: No self.play() found in slide {slide_no}")
                continue
            
            # Step 2: Inject image code BEFORE first play
            indent = len(script_lines[first_play_line]) - len(script_lines[first_play_line].lstrip())
            indent_str = ' ' * indent
            
            image_code = LayoutManager.generate_image_injection_code(
                slide_no, img_path, layout_type, indent_str
            )
            
            # Insert image code
            script_lines = (script_lines[:first_play_line] + 
                          image_code + 
                          script_lines[first_play_line:])
            
            # Update boundaries and indices (we added lines)
            lines_added = len(image_code)
            end_line += lines_added
            first_play_line += lines_added
            
            # Update all subsequent slide boundaries
            for other_slide_no in slide_boundaries:
                other_start, other_end = slide_boundaries[other_slide_no]
                if other_start > start_line:
                    slide_boundaries[other_slide_no] = (other_start + lines_added, other_end + lines_added)
            
            # Step 3: Reposition content if not background layout
            if layout_type != LayoutType.BACKGROUND_ONLY:
                script_lines = SmartContentInjector._reposition_slide_content(
                    script_lines, start_line, end_line, slide_no, layout_type, indent_str, verbose
                )
            
            # Step 4: Update fadeout to include image
            script_lines = SmartContentInjector._add_image_to_fadeout(
                script_lines, start_line, end_line, slide_no, verbose
            )
        
        return '\n'.join(script_lines)
    
    @staticmethod
    def _reposition_slide_content(script_lines: List[str], start_line: int, end_line: int,
                                 slide_no: int, layout_type: LayoutType, indent_str: str,
                                 verbose: bool) -> List[str]:
        """
        Reposition content elements to fit within content region
        """
        regions = LayoutManager.get_layout_regions(layout_type, has_title=True)
        content_region = regions['content']
        guide = AlignmentGuide(content_region)
        
        if verbose:
            print(f"[INJECTOR]   Content region: x=[{content_region.left:.2f}, {content_region.right:.2f}], "
                  f"y=[{content_region.bottom:.2f}, {content_region.top:.2f}]")
        
        modified_lines = script_lines.copy()
        
        # Track which lines have been modified
        repositioned_count = 0
        
        for i in range(start_line, min(end_line + 1, len(modified_lines))):
            line = modified_lines[i]
            
            # Skip title positioning and already injected code
            if 'title' in line.lower() and '.to_edge(UP)' in line:
                continue
            if '[AUTO-INJECTED]' in line:
                continue
            if 'img_' in line:
                continue
            
            # Reposition elements that use absolute positioning
            # Replace .to_edge(LEFT) with content-aware positioning
            if '.to_edge(LEFT)' in line and 'title' not in line.lower():
                var_match = re.match(r'(\s*)(\w+)\.to_edge\(LEFT\)', line.strip())
                if var_match:
                    var_name = var_match.group(2)
                    x_pos = guide.get_left_aligned(offset=0.3)
                    indent = len(line) - len(line.lstrip())
                    modified_lines[i] = ' ' * indent + f"{var_name}.move_to(RIGHT * {x_pos:.2f}).align_on_border(LEFT, buff=0.3)"
                    repositioned_count += 1
                    if verbose:
                        print(f"[INJECTOR]   Repositioned {var_name} to x={x_pos:.2f}")
            
            # Replace .to_edge(RIGHT)
            elif '.to_edge(RIGHT)' in line and 'title' not in line.lower():
                var_match = re.match(r'(\s*)(\w+)\.to_edge\(RIGHT\)', line.strip())
                if var_match:
                    var_name = var_match.group(2)
                    x_pos = guide.get_right_aligned(offset=0.3)
                    indent = len(line) - len(line.lstrip())
                    modified_lines[i] = ' ' * indent + f"{var_name}.move_to(RIGHT * {x_pos:.2f}).align_on_border(RIGHT, buff=0.3)"
                    repositioned_count += 1
            
            # Adjust .shift() positions to scale within content region
            elif '.shift(LEFT*' in line or '.shift(RIGHT*' in line:
                shift_match = re.search(r'\.shift\((LEFT|RIGHT)\s*\*\s*([0-9.]+)', line)
                if shift_match and 'img_' not in line:
                    direction = shift_match.group(1)
                    amount = float(shift_match.group(2))
                    
                    # Calculate new position relative to content region
                    if direction == 'LEFT':
                        new_x = content_region.center_x - (amount * 0.7)  # Scale down slightly
                    else:
                        new_x = content_region.center_x + (amount * 0.7)
                    
                    # Replace the shift
                    old_pattern = f'.shift({direction}*{amount}'
                    new_pattern = f'.move_to(RIGHT * {new_x:.2f}'
                    modified_lines[i] = line.replace(old_pattern, new_pattern)
                    repositioned_count += 1
        
        if verbose and repositioned_count > 0:
            print(f"[INJECTOR]   Repositioned {repositioned_count} elements")
        
        return modified_lines
    
    @staticmethod
    def _add_image_to_fadeout(script_lines: List[str], start_line: int, end_line: int,
                             slide_no: int, verbose: bool) -> List[str]:
        """
        Add image to the slide's fadeout animation
        """
        modified_lines = script_lines.copy()
        
        for i in range(start_line, min(end_line + 1, len(modified_lines))):
            line = modified_lines[i]
            
            # Find fadeout line
            if 'self.play(FadeOut(' in line and 'img_' not in line:
                # Check if it's a VGroup or Group
                if 'VGroup(' in line:
                    # Replace VGroup with Group (supports ImageMobject)
                    modified_lines[i] = line.replace('VGroup(', 'Group(')
                    # Add image to the group - need to find the closing paren of VGroup/Group
                    # Pattern: FadeOut(Group(...)) -> FadeOut(Group(..., img_X))
                    modified_lines[i] = re.sub(r'(\))\),\s*run_time', f', img_{slide_no})), run_time', modified_lines[i])
                    if verbose:
                        print(f"[INJECTOR]   Added img_{slide_no} to fadeout")
                    break
                elif 'Group(' in line:
                    # Already using Group, just add image
                    modified_lines[i] = re.sub(r'(\))\),\s*run_time', f', img_{slide_no})), run_time', line)
                    if verbose:
                        print(f"[INJECTOR]   Added img_{slide_no} to fadeout")
                    break
        
        return modified_lines


def test_smart_injector():
    """Test the smart content injector"""
    
    # Sample script
    sample_script = """from manim import *

class BridgeDesignManual(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Slide 1: Title
        title = Text("Bridge Components", color=BLACK, font_size=40).to_edge(UP)
        
        beam = Rectangle(width=6, height=0.5, color=BLACK, fill_opacity=0.2, stroke_width=3)
        bearing_left = Circle(radius=0.4, color=BLUE, fill_opacity=0.6, stroke_width=2).next_to(beam, DOWN+LEFT, buff=0.3)
        bearing_right = Circle(radius=0.4, color=BLUE, fill_opacity=0.6, stroke_width=2).next_to(beam, DOWN+RIGHT, buff=0.3)
        
        bullets = VGroup(
            Text("• Load distribution", color=BLACK, font_size=20),
            Text("• Structural support", color=BLACK, font_size=20),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(LEFT).shift(DOWN*0.5)
        
        diagram = VGroup(beam, bearing_left, bearing_right)
        
        self.play(Write(title), run_time=1)
        self.play(Create(diagram), run_time=2)
        self.play(Write(bullets), run_time=1.5)
        self.wait(25)
        self.play(FadeOut(VGroup(title, diagram, bullets)), run_time=1)
"""
    
    # Simulated downloaded images
    downloaded_images = {
        1: {
            'path': 'test_output/images/slide_1.jpg',
            'layout': 'split_right'
        }
    }
    
    print("="*80)
    print("TESTING SMART CONTENT INJECTOR")
    print("="*80)
    
    print("\nOriginal Script:")
    print("-"*80)
    print(sample_script)
    
    print("\n\nInjecting Images...")
    print("-"*80)
    
    injector = SmartContentInjector()
    modified_script = injector.inject_images_with_alignment(sample_script, downloaded_images, verbose=True)
    
    print("\n\nModified Script:")
    print("-"*80)
    print(modified_script)
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_smart_injector()

