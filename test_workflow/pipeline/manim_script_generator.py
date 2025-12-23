"""
Manim Script Generator Module - ENHANCED
Generates rich, properly-structured Manim animations with actual educational visuals.
Supports embedding PDF figures with callout annotations.
"""

import re
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import call_llm, print_info, print_success, print_error


@dataclass
class ScriptGenerationResult:
    """Result of script generation"""
    video_id: str
    script_path: Path
    timings_path: Path
    script_content: str
    timings: List[Dict]
    syntax_valid: bool
    diversity_score: int
    diversity_report: Dict[str, Any]
    source_comments: List[str]
    figures_used: List[str] = None  # List of figure paths used


class ManimScriptGenerator:
    """Generates properly structured Manim scripts with educational visuals"""
    
    def _build_prompt(self, video_id: str, title: str, description: str, 
                      slide_plans: str, class_name: str,
                      figure_info: str = "") -> str:
        """Build the prompt with proper escaping"""
        
        # Code examples with escaped braces
        examples = '''
MANDATORY STRUCTURE FOR EVERY SLIDE:

# Slide N: [Title]
self.clear()  # ALWAYS clear before new slide

# Title at TOP - ALWAYS positioned at top
title = Text("[Title]", color=BLUE_D, font_size=40, weight=BOLD)
title.to_edge(UP, buff=0.5)
self.play(Write(title))

# Main content - use VGroup for multiple elements, PROPERLY POSITIONED
content_group = VGroup()

element1 = Rectangle(width=4, height=2.5, color=BLUE, fill_opacity=0.1)
label1 = Text("Label", color=BLACK, font_size=24)
label1.move_to(element1)
labeled_box = VGroup(element1, label1)
content_group.add(labeled_box)

# CRITICAL: Arrange and position content!
content_group.arrange(DOWN, buff=0.5)
content_group.next_to(title, DOWN, buff=0.8)

# Animate with VARIETY
self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
self.play(Indicate(element1, color=ORANGE))
self.wait(2)

═══════════════════════════════════════════════════════════════════════════════
VISUAL ELEMENT PATTERNS (COPY AND ADAPT THESE)
═══════════════════════════════════════════════════════════════════════════════

DOCUMENT/SHEET:
sheet = Rectangle(width=5, height=6, color=DARK_GRAY, stroke_width=2, fill_opacity=0.05)
header = Rectangle(width=5, height=1, color=BLUE_D, fill_opacity=0.3)
header.align_to(sheet, UP)
header_text = Text("COVER SHEET", color=BLACK, font_size=20, weight=BOLD)
header_text.move_to(header)
document = VGroup(sheet, header, header_text)
document.move_to(ORIGIN)

FLOWCHART WITH ARROWS:
box1 = VGroup(
    RoundedRectangle(width=3.5, height=1, corner_radius=0.2, color=BLUE_D, fill_opacity=0.2),
    Text("Standard Specs", color=BLACK, font_size=18)
)
box1[1].move_to(box1[0])

box2 = VGroup(
    RoundedRectangle(width=3.5, height=1, corner_radius=0.2, color=ORANGE, fill_opacity=0.2),
    Text("Special Provisions", color=BLACK, font_size=18)
)
box2[1].move_to(box2[0])

boxes = VGroup(box1, box2).arrange(DOWN, buff=1.5)
arrow = Arrow(box1.get_bottom(), box2.get_top(), color=GRAY, buff=0.1)

SCALE BAR WITH MEASUREMENTS:
scale_bar = Line(LEFT * 3, RIGHT * 3, color=BLACK, stroke_width=4)
scale_ticks = VGroup()
for i in range(7):
    tick = Line(UP * 0.2, DOWN * 0.2, color=BLACK, stroke_width=2)
    tick.move_to(scale_bar.get_start() + RIGHT * i)
    scale_ticks.add(tick)
scale_label = Text("Scale: 1 inch = 20 feet", color=BLUE_D, font_size=20)
scale_group = VGroup(scale_bar, scale_ticks, scale_label).arrange(DOWN, buff=0.4)
scale_group.move_to(ORIGIN)

CENTERLINE WITH TRACER (IMPORTANT - USE THIS!):
centerline = Line(LEFT * 5, RIGHT * 5, color=BLUE, stroke_width=3)
tracer = Dot(color=RED, radius=0.15)
tracer.move_to(centerline.get_start())
# Animation:
self.play(Create(centerline))
self.play(MoveAlongPath(tracer, centerline), run_time=3)

═══════════════════════════════════════════════════════════════════════════════
PDF FIGURE DISPLAY WITH CALLOUTS (USE WHEN FIGURES ARE PROVIDED!):
═══════════════════════════════════════════════════════════════════════════════

# Load and display a PDF figure
figure = ImageMobject("figures/chapter_01/fig_1-1.png")
figure.scale_to_fit_width(9)  # Scale to fit screen
figure.move_to(ORIGIN)

# Add a frame around the figure
frame = SurroundingRectangle(figure, color=BLUE_D, buff=0.1, stroke_width=2)

# Create callout annotation pointing to a specific area
callout_arrow = Arrow(
    start=RIGHT * 4 + DOWN * 2,  # Where the label is
    end=RIGHT * 1.5 + UP * 0.5,   # Where you're pointing
    color=ORANGE, 
    stroke_width=3
)
callout_label = Text("Project Number", color=ORANGE, font_size=24, weight=BOLD)
callout_label.next_to(callout_arrow.get_start(), RIGHT)

# Animate figure appearance with callouts
self.play(FadeIn(figure), Create(frame))
self.wait(1)
self.play(Create(callout_arrow), Write(callout_label))
self.play(Indicate(callout_label, color=RED))
self.wait(2)

# Multiple callouts on same figure:
callout_group = VGroup()
points_to_highlight = [
    ("Sheet Number", RIGHT * 3 + UP * 2, RIGHT * 1 + UP * 1.5),
    ("Project ID", LEFT * 3 + DOWN * 1, LEFT * 1 + DOWN * 0.5),
]
for label_text, label_pos, arrow_end in points_to_highlight:
    arrow = Arrow(label_pos, arrow_end, color=ORANGE, stroke_width=2)
    label = Text(label_text, color=ORANGE, font_size=20)
    label.next_to(arrow.get_start(), DOWN if label_pos[1] > 0 else UP)
    callout_group.add(VGroup(arrow, label))

self.play(LaggedStart(*[Create(c) for c in callout_group], lag_ratio=0.3))

# Figure with side-by-side explanation
figure = ImageMobject("figures/chapter_01/fig_1-9.png")
figure.scale_to_fit_height(5)
figure.to_edge(LEFT, buff=0.5)

explanation = VGroup(
    Text("Engineer's Scale", color=BLUE_D, font_size=28, weight=BOLD),
    Text("• 10 divisions = 1 inch", color=BLACK, font_size=20),
    Text("• Use for plan measurements", color=BLACK, font_size=20),
    Text("• Read right to left", color=BLACK, font_size=20),
).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
explanation.to_edge(RIGHT, buff=0.8)

self.play(FadeIn(figure))
self.play(LaggedStart(*[Write(item) for item in explanation], lag_ratio=0.2))

TABLE/GRID LAYOUT:
table_items = VGroup()
for row in range(3):
    row_items = VGroup()
    for col in range(2):
        cell = Rectangle(width=2.5, height=0.8, color=GRAY, stroke_width=1, fill_opacity=0.05)
        text = Text("Cell", color=BLACK, font_size=14)
        text.move_to(cell)
        row_items.add(VGroup(cell, text))
    row_items.arrange(RIGHT, buff=0.1)
    table_items.add(row_items)
table_items.arrange(DOWN, buff=0.1)

═══════════════════════════════════════════════════════════════════════════════
ANIMATION REQUIREMENTS (MANDATORY!)
═══════════════════════════════════════════════════════════════════════════════

1. ALWAYS call self.clear() between slides
2. Use GrowFromCenter, DrawBorderThenFill, Write - NOT just FadeIn
3. Use LaggedStart for revealing multiple items sequentially
4. Include AT LEAST ONE MoveAlongPath with a tracer dot
5. Use Indicate() or Circumscribe() for emphasis
6. ALWAYS position elements with .to_edge(), .next_to(), .move_to(), .arrange()

COLOR SCHEME:
- Background: WHITE (self.camera.background_color = WHITE)
- Text: BLACK, DARK_GRAY  
- Primary: BLUE_D, BLUE
- Emphasis: ORANGE, GOLD
- Success: GREEN_D, TEAL
- Warning: RED
'''
        
        # Add figure section if figures are provided
        figure_section = ""
        if figure_info:
            figure_section = f"""
═══════════════════════════════════════════════════════════════════════════════
AVAILABLE FIGURES TO DISPLAY
═══════════════════════════════════════════════════════════════════════════════
{figure_info}

IMPORTANT: When a figure is available for a slide, you MUST:
1. Load it using: figure = ImageMobject("path/to/figure.png")
2. Scale appropriately: figure.scale_to_fit_width(9) or figure.scale_to_fit_height(5)
3. Add callout arrows and labels pointing to key elements
4. The figure should be the MAIN VISUAL for that slide

"""
        
        prompt = f'''You are creating a Manim animation for highway plan reading education.

═══════════════════════════════════════════════════════════════════════════════
VIDEO INFO
═══════════════════════════════════════════════════════════════════════════════
Video ID: {video_id}
Title: {title}
Description: {description}
{figure_section}
═══════════════════════════════════════════════════════════════════════════════
SLIDES TO CREATE
═══════════════════════════════════════════════════════════════════════════════
{slide_plans}

═══════════════════════════════════════════════════════════════════════════════
{examples}
═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

OUTPUT ONLY VALID PYTHON CODE. NO MARKDOWN BLOCKS.

from manim import *

class {class_name}(MovingCameraScene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Slide 1: [Title]
        self.clear()
        title = Text("...", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        # ... rich visual content with shapes, diagrams, arrows ...
        # ... proper positioning with .next_to(), .move_to(), .arrange() ...
        self.wait(2)
        
        # Slide 2: ...
        self.clear()
        # ... continue ...

After the code, on a new line write:
TIMINGS_JSON:
{{"slides": [{{"slide_no": 1, "duration": 30, "title": "..."}}]}}
'''
        return prompt

    def __init__(self, output_dir: Path, figures_dir: Optional[Path] = None):
        self.output_dir = output_dir
        self.figures_dir = figures_dir
        self._image_metadata_cache = {}
    
    def _load_image_metadata(self, chapter_id: str) -> Dict[str, Any]:
        """Load image metadata from image_metadata.json"""
        if chapter_id in self._image_metadata_cache:
            return self._image_metadata_cache[chapter_id]
        
        if not self.figures_dir:
            return {}
        
        metadata_path = self.figures_dir / chapter_id / "image_metadata.json"
        if metadata_path.exists():
            try:
                import json
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self._image_metadata_cache[chapter_id] = json.load(f)
                    return self._image_metadata_cache[chapter_id]
            except Exception as e:
                print_error(f"Failed to load image metadata: {e}")
        
        return {}
    
    def generate_script(
        self,
        video_id: str,
        chapter_id: str,
        title: str,
        description: str,
        slides: List[Dict],
        figure_paths: List[str],
        source_file: str = "",
        figure_metadata: Optional[Dict] = None
    ) -> ScriptGenerationResult:
        """Generate a Manim script from a video plan"""
        
        # Load image metadata if not provided
        if not figure_metadata:
            figure_metadata = self._load_image_metadata(chapter_id)
        
        # If figure_paths is empty, try to get them from metadata
        if not figure_paths and figure_metadata and 'images' in figure_metadata:
            for img in figure_metadata['images']:
                if img.get('path'):
                    full_path = self.figures_dir.parent / img['path'] if self.figures_dir else Path(img['path'])
                    if full_path.exists():
                        figure_paths.append(str(full_path))
        
        # Format slide plans with more detail
        slide_plans_text = self._format_slide_plans(slides)
        
        # Generate class name from video_id
        class_name = self._generate_class_name(video_id, title)
        
        # Build figure information for prompt
        figure_info = self._build_figure_info(figure_paths, figure_metadata)
        
        # Build prompt
        prompt = self._build_prompt(
            video_id=video_id,
            title=title,
            description=description,
            slide_plans=slide_plans_text,
            class_name=class_name,
            figure_info=figure_info
        )
        
        print_info(f"Generating Manim script for: {video_id}")
        
        # Call LLM with higher temperature for creativity
        response, tokens = call_llm(prompt, max_tokens=6000, temperature=0.7)
        print_info(f"LLM tokens used: {tokens}")
        
        # Parse response
        script_content, timings = self._parse_response(response, video_id, len(slides))
        
        # Post-process to fix common issues
        script_content = self._post_process_script(script_content)
        
        # Validate syntax
        syntax_valid = self._validate_syntax(script_content)
        
        # If syntax is invalid, try to fix it
        if not syntax_valid:
            script_content = self._attempt_syntax_fix(script_content)
            syntax_valid = self._validate_syntax(script_content)
        
        # Check diversity
        diversity_score, diversity_report = self._analyze_diversity(script_content)
        
        # Extract source comments
        source_comments = re.findall(r'# Slide \d+:.*', script_content)
        
        # Save files
        video_dir = self.output_dir / chapter_id / video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = video_dir / "base_script.py"
        script_path.write_text(script_content, encoding='utf-8')
        
        timings_path = video_dir / "timings.json"
        timings_path.write_text(json.dumps(timings, indent=2))
        
        print_success(f"Script saved: {script_path}")
        
        return ScriptGenerationResult(
            video_id=video_id,
            script_path=script_path,
            timings_path=timings_path,
            script_content=script_content,
            timings=timings,
            syntax_valid=syntax_valid,
            diversity_score=diversity_score,
            diversity_report=diversity_report,
            source_comments=source_comments,
            figures_used=figure_paths if figure_paths else []
        )
    
    def _build_figure_info(self, figure_paths: List[str], metadata: Optional[Dict] = None) -> str:
        """Build figure information section for the prompt"""
        if not figure_paths:
            return ""
        
        lines = ["YOU MUST USE AT LEAST 2 OF THESE FIGURES IN YOUR SCRIPT!"]
        lines.append("For each figure you use, create a dedicated slide showing the image with callout annotations.\n")
        
        for i, fig_path in enumerate(figure_paths, 1):
            path = Path(fig_path)
            
            # Try to get metadata for this figure
            fig_meta = {}
            if metadata and 'images' in metadata:
                for img in metadata['images']:
                    if img.get('path', '').endswith(path.name) or img.get('id') in path.name:
                        fig_meta = img
                        break
            
            lines.append(f"═══ FIGURE {i}: {path.name} ═══")
            lines.append(f"  Path (USE THIS EXACT PATH): \"{fig_path}\"")
            lines.append(f"  Manim code: figure = ImageMobject(\"{fig_path}\")")
            
            if fig_meta:
                if fig_meta.get('label'):
                    lines.append(f"  Label: {fig_meta['label']}")
                if fig_meta.get('description'):
                    lines.append(f"  What it shows: {fig_meta['description']}")
                if fig_meta.get('key_elements'):
                    elements = fig_meta['key_elements'][:5]
                    lines.append(f"  Key elements to point out with arrows: {', '.join(elements)}")
                if fig_meta.get('educational_points'):
                    points = fig_meta['educational_points'][:3]
                    lines.append(f"  Teaching points: {', '.join(points)}")
                if fig_meta.get('highlight_suggestions'):
                    highlights = fig_meta['highlight_suggestions'][:3]
                    lines.append(f"  Suggested callouts: {', '.join(highlights)}")
            
            lines.append("")
        
        lines.append("REMINDER: Create slides that DISPLAY these figures using ImageMobject!")
        lines.append("Add Arrow callouts pointing to important elements in each figure.")
        
        return "\n".join(lines)
    
    def _format_slide_plans(self, slides: List[Dict]) -> str:
        """Format slide plans with rich detail"""
        lines = []
        for i, slide in enumerate(slides, 1):
            lines.append(f"═══ SLIDE {i} ═══")
            lines.append(f"Title: {slide.get('title', f'Slide {i}')}")
            lines.append(f"Duration: {slide.get('timing_seconds', 30)} seconds")
            lines.append(f"Visual Goal: {slide.get('visual_goal', 'Explain key concepts')}")
            
            # Add specific visual requirements
            recipe = slide.get('visual_recipe', {})
            if recipe:
                lines.append("Visual Elements to Create:")
                if 'main_elements' in recipe:
                    for elem in recipe['main_elements']:
                        elem_type = elem.get('type', 'Unknown')
                        content = elem.get('content', elem.get('description', ''))
                        
                        # IMPORTANT: Include full path for ImageMobject elements
                        if elem_type == "ImageMobject" and 'path' in elem:
                            img_path = elem['path']
                            lines.append(f"  • {elem_type}: DISPLAY THIS IMAGE")
                            lines.append(f"    EXACT CODE: figure = ImageMobject(r\"{img_path}\")")
                            lines.append(f"    figure.scale_to_fit_width(9)")
                            lines.append(f"    figure.move_to(ORIGIN)")
                            lines.append(f"    self.play(FadeIn(figure))")
                        else:
                            lines.append(f"  • {elem_type}: {content}")
                            
                if 'animations' in recipe:
                    anim_types = [a.get('type', '?') for a in recipe['animations']]
                    lines.append(f"Recommended animations: {', '.join(anim_types)}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_class_name(self, video_id: str, title: str) -> str:
        """Generate a valid Python class name"""
        # Clean title for class name
        name = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        name = ''.join(word.capitalize() for word in name.split())
        
        if not name or name[0].isdigit():
            name = "Video" + name
        
        if not name.isidentifier():
            name = "VideoScene"
        
        return name[:50]  # Limit length
    
    def _parse_response(self, response: str, video_id: str, expected_slides: int) -> tuple[str, List[Dict]]:
        """Parse LLM response into script and timings"""
        
        # Split at TIMINGS_JSON marker
        if "TIMINGS_JSON:" in response:
            parts = response.split("TIMINGS_JSON:")
            script_part = parts[0].strip()
            timings_part = parts[1].strip() if len(parts) > 1 else ""
        else:
            script_part = response
            timings_part = ""
        
        # Clean script
        script_content = script_part.strip()
        
        # Remove markdown code fences if present
        if script_content.startswith("```"):
            script_content = re.sub(r'^```\w*\n?', '', script_content)
        script_content = re.sub(r'\n?```$', '', script_content)
        script_content = script_content.strip()
        
        # Ensure proper imports
        if not script_content.startswith("from manim"):
            script_content = "from manim import *\n\n" + script_content
        
        # Parse timings
        timings = []
        if timings_part:
            try:
                json_match = re.search(r'\{.*\}', timings_part, re.DOTALL)
                if json_match:
                    timings_data = json.loads(json_match.group())
                    timings = timings_data.get('slides', [])
            except json.JSONDecodeError:
                pass
        
        # Generate default timings if needed
        if not timings:
            timings = [
                {"slide_no": i + 1, "duration": 30, "title": f"Slide {i + 1}"}
                for i in range(expected_slides)
            ]
        
        return script_content, timings
    
    def _post_process_script(self, script: str) -> str:
        """Fix common issues in generated scripts"""
        
        # Check for multiple slides and ensure self.clear() between them
        slides = re.findall(r'# Slide \d+:', script)
        if len(slides) > 1:
            lines = script.split('\n')
            new_lines = []
            slide_count = 0
            for i, line in enumerate(lines):
                if re.match(r'\s*# Slide \d+:', line):
                    slide_count += 1
                    if slide_count > 1:
                        # Check if previous lines have self.clear()
                        prev_idx = i - 1
                        while prev_idx >= 0 and lines[prev_idx].strip() == '':
                            prev_idx -= 1
                        if prev_idx >= 0 and 'self.clear()' not in lines[prev_idx]:
                            indent = len(line) - len(line.lstrip())
                            new_lines.append(' ' * indent + 'self.clear()')
                            new_lines.append('')
                new_lines.append(line)
            script = '\n'.join(new_lines)
        
        return script
    
    def _attempt_syntax_fix(self, script: str) -> str:
        """Attempt to fix common syntax errors"""
        # Fix common issues
        # 1. Remove duplicate imports
        lines = script.split('\n')
        import_lines = []
        other_lines = []
        for line in lines:
            if line.strip().startswith('from manim') or line.strip().startswith('import manim'):
                if line not in import_lines:
                    import_lines.append(line)
            else:
                other_lines.append(line)
        
        # Ensure only one import
        if import_lines:
            script = import_lines[0] + '\n\n' + '\n'.join(other_lines)
        
        return script
    
    def _validate_syntax(self, script: str) -> bool:
        """Validate Python syntax"""
        try:
            compile(script, '<string>', 'exec')
            print_success("Script syntax is valid")
            return True
        except SyntaxError as e:
            print_error(f"Script has syntax error at line {e.lineno}: {e.msg}")
            return False
    
    def _analyze_diversity(self, script: str) -> tuple[int, Dict[str, Any]]:
        """Analyze visual diversity of the script"""
        checks = {
            'rectangles_shapes': {
                'count': script.count('Rectangle(') + script.count('RoundedRectangle(') + script.count('Square('),
                'target': 2,
                'weight': 2
            },
            'arrows': {
                'count': script.count('Arrow(') + script.count('CurvedArrow('),
                'target': 1,
                'weight': 1
            },
            'vgroups': {
                'count': script.count('VGroup('),
                'target': 3,
                'weight': 2
            },
            'positioning': {
                'count': script.count('.to_edge(') + script.count('.next_to(') + script.count('.move_to(') + script.count('.arrange('),
                'target': 5,
                'weight': 3
            },
            'grow_animations': {
                'count': script.count('GrowFrom') + script.count('DrawBorderThenFill'),
                'target': 2,
                'weight': 2
            },
            'lagged_start': {
                'count': script.count('LaggedStart('),
                'target': 1,
                'weight': 2
            },
            'emphasis': {
                'count': script.count('Indicate(') + script.count('Circumscribe(') + script.count('Flash('),
                'target': 1,
                'weight': 1
            },
            'dynamic_elements': {
                'count': script.count('MoveAlongPath(') + script.count('add_updater('),
                'target': 1,
                'weight': 3
            },
            'clear_calls': {
                'count': script.count('self.clear()'),
                'target': 2,
                'weight': 2
            }
        }
        
        score = 0
        report = {}
        
        for name, data in checks.items():
            passed = data['count'] >= data['target']
            score += data['weight'] if passed else 0
            report[name] = {
                'count': data['count'],
                'target': data['target'],
                'passed': passed
            }
        
        # Check colors used
        colors = ['BLUE', 'ORANGE', 'GREEN', 'RED', 'GOLD', 'TEAL', 'YELLOW', 'PURPLE', 'GRAY']
        colors_used = [c for c in colors if c in script]
        report['colors'] = {
            'used': colors_used,
            'count': len(colors_used),
            'target': 3,
            'passed': len(colors_used) >= 3
        }
        if report['colors']['passed']:
            score += 2
        
        max_score = sum(c['weight'] for c in checks.values()) + 2
        report['total_score'] = score
        report['max_score'] = max_score
        report['percentage'] = round(score / max_score * 100, 1)
        
        return score, report
    
    def print_diversity_report(self, report: Dict[str, Any]):
        """Print a formatted diversity report"""
        print("\n" + "="*60)
        print("VISUAL DIVERSITY REPORT")
        print("="*60)
        
        for name, data in report.items():
            if name in ['total_score', 'max_score', 'percentage']:
                continue
            
            if isinstance(data, dict) and 'passed' in data:
                status = "[OK]" if data['passed'] else "[X]"
                if 'count' in data:
                    print(f"  {status} {name}: {data['count']} (target: {data['target']}+)")
                elif 'used' in data:
                    print(f"  {status} {name}: {', '.join(data['used'][:5])} ({data['count']} colors)")
        
        print("-"*60)
        print(f"Score: {report['total_score']}/{report['max_score']} ({report['percentage']}%)")
        print("="*60)


def generate_script_from_plan(plan_path: Path, output_dir: Path, figures_dir: Optional[Path] = None) -> ScriptGenerationResult:
    """Convenience function to generate a script from a plan file"""
    
    plan_data = json.loads(plan_path.read_text())
    
    generator = ManimScriptGenerator(output_dir, figures_dir)
    
    result = generator.generate_script(
        video_id=plan_data['video_id'],
        chapter_id=plan_data['chapter_id'],
        title=plan_data['title'],
        description=plan_data['description'],
        slides=plan_data['slides'],
        figure_paths=plan_data.get('figure_paths', []),
        source_file=plan_data.get('source_file', '')
    )
    
    generator.print_diversity_report(result.diversity_report)
    
    return result


if __name__ == "__main__":
    print("Manim Script Generator - Run via orchestrator scripts")
