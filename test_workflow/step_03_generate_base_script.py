"""
Step 3: Generate Base Manim Script
Generates creative, content-aware Manim animations with LLM freedom
Uses dynamic class name from CONFIG.py or INPUT.md title
"""

import re
import json
from shared import *

# Load animation preferences from CONFIG if available
try:
    from CONFIG import ANIMATION_STYLE, MANIM_FEATURES
except ImportError:
    ANIMATION_STYLE = "professional"
    MANIM_FEATURES = "all"

def main():
    """Generate base Manim script with creative freedom"""
    print_step(3, "Generate Base Manim Script (Creative Mode)")
    
    try:
        # Read summary
        summary_file = TEST_DIR / 'summary.txt'
        if not summary_file.exists():
            print_error("Summary file not found. Run step_02 first.")
            return 1
        
        summary = summary_file.read_text(encoding='utf-8')
        print_info(f"Loaded summary: {len(summary)} characters")
        
        # Read full input for deeper context
        input_file = TEST_DIR / 'input.md'
        if input_file.exists():
            full_content = input_file.read_text(encoding='utf-8')
            # Truncate if too long but keep substantial context
            if len(full_content) > 4000:
                full_content = full_content[:4000] + "\n[... content truncated ...]"
        else:
            full_content = summary
        
        # Get dynamic video/class name
        video_name = get_video_name()
        print_info(f"Video class name: {video_name}")
        
        # Save video name for other steps
        video_name_file = TEST_DIR / 'video_name.txt'
        video_name_file.write_text(video_name)
        
        # Generate Manim script with LLM - AGGRESSIVE CREATIVE MODE
        prompt = f"""{SYSTEM_GDOT}

═══════════════════════════════════════════════════════════════════════════════
🎬 MANIM ANIMATION SCRIPT GENERATION
═══════════════════════════════════════════════════════════════════════════════

You are a professional motion graphics designer creating an EDUCATIONAL VIDEO.
Your animations must VISUALLY TEACH concepts, not just display text on rectangles.

═══════════════════════════════════════════════════════════════════════════════
CONTENT TO ANIMATE
═══════════════════════════════════════════════════════════════════════════════

Summary: {summary}

Full Content:
{full_content}

═══════════════════════════════════════════════════════════════════════════════
🚨 CRITICAL: VISUAL DIVERSITY REQUIREMENTS 🚨
═══════════════════════════════════════════════════════════════════════════════

Your script MUST include ALL of these element types (minimum counts):
- 4+ Arrows (show flow, direction, connections)
- 3+ Circles (for icons, bullets, nodes)
- 3+ Different colored shapes (not just BLUE)
- 2+ Brace annotations (explain parts of diagrams)
- 2+ Transform or ReplacementTransform animations
- 1+ NumberLine or scale visualization
- Use of Indicate() or Circumscribe() for emphasis

❌ REJECTED PATTERNS (DO NOT DO THESE):
- Rectangle with text inside (BORING - this is PowerPoint!)
- Only using Rectangle() shapes
- Static text lists without visual diagrams
- Same animation pattern repeated for every slide
- Only blue colored shapes

✅ REQUIRED PATTERNS (DO THESE):
- Arrows connecting concepts → shows relationships
- Circles with icons → visual bullets
- Shapes that TRANSFORM into other shapes → shows change
- Elements that GROW from center or edges → reveals information
- Highlighted annotations using Brace() → explains parts
- Color coding: BLUE=main, ORANGE=highlight, GREEN=success, RED=warning

═══════════════════════════════════════════════════════════════════════════════
VISUAL DESIGN EXAMPLES (adapt these creatively!)
═══════════════════════════════════════════════════════════════════════════════

EXAMPLE A - Hierarchy Diagram (for document priority):
```
# Create pyramid/stack showing hierarchy
top = Triangle(color=GOLD, fill_opacity=0.8).scale(0.5).shift(UP*2)
mid = Rectangle(width=3, height=0.6, color=BLUE, fill_opacity=0.6).shift(UP*0.8)
bot = Rectangle(width=5, height=0.6, color=TEAL, fill_opacity=0.4).shift(DOWN*0.4)
# Arrows showing flow DOWN
arrow1 = Arrow(top.get_bottom(), mid.get_top(), color=ORANGE, stroke_width=3)
arrow2 = Arrow(mid.get_bottom(), bot.get_top(), color=ORANGE, stroke_width=3)
# Animate with staged reveal
self.play(GrowFromCenter(top), run_time=0.5)
self.play(GrowFromEdge(mid, UP), Create(arrow1), run_time=0.5)
self.play(GrowFromEdge(bot, UP), Create(arrow2), run_time=0.5)
```

EXAMPLE B - Process Flow (for steps/procedures):
```
# Create connected circles for steps
step1 = Circle(radius=0.5, color=BLUE, fill_opacity=0.7).shift(LEFT*4)
step2 = Circle(radius=0.5, color=BLUE, fill_opacity=0.7)
step3 = Circle(radius=0.5, color=GREEN, fill_opacity=0.7).shift(RIGHT*4)
# Curved arrows between them
arr1 = CurvedArrow(step1.get_right(), step2.get_left(), color=ORANGE)
arr2 = CurvedArrow(step2.get_right(), step3.get_left(), color=ORANGE)
# Labels with numbers inside
num1 = Text("1", color=WHITE, font_size=28).move_to(step1)
# Animate sequentially
self.play(GrowFromCenter(step1), Write(num1))
self.play(Create(arr1), GrowFromCenter(step2))
```

EXAMPLE C - Scale/Measurement Visualization:
```
# Number line showing scale
scale_line = NumberLine(x_range=[0, 100, 10], length=10, include_numbers=True)
pointer = Triangle(color=RED, fill_opacity=1).scale(0.3).rotate(PI).next_to(scale_line.n2p(50), UP)
brace = Brace(scale_line, DOWN, color=GRAY)
label = brace.get_text("Engineering Scale")
self.play(Create(scale_line), run_time=1)
self.play(GrowFromCenter(pointer), Write(label))
```

EXAMPLE D - Document/Form Visualization:
```
# Create a "document" with labeled sections
doc = RoundedRectangle(width=4, height=5, corner_radius=0.2, color=DARK_GRAY, fill_opacity=0.1)
header = Rectangle(width=3.5, height=0.8, color=BLUE, fill_opacity=0.3).move_to(doc.get_top()).shift(DOWN*0.6)
body = Rectangle(width=3.5, height=2, color=GRAY, fill_opacity=0.1).move_to(doc.get_center())
# Braces to annotate
brace_header = Brace(header, RIGHT, color=ORANGE)
brace_label = brace_header.get_text("Title Section", font_size=20)
# Show with indicator
self.play(Create(doc), Create(header), Create(body))
self.play(Create(brace_header), Write(brace_label))
self.play(Indicate(header, color=YELLOW))
```

EXAMPLE E - Transform Animation (for changes/relationships):
```
# Show concept A transforming to concept B
concept_a = Square(color=BLUE, fill_opacity=0.6).scale(0.8)
label_a = Text("Draft", font_size=24).next_to(concept_a, DOWN)
concept_b = Circle(color=GREEN, fill_opacity=0.6).scale(0.8)
label_b = Text("Final", font_size=24).next_to(concept_b, DOWN)
self.play(Create(concept_a), Write(label_a))
self.wait(1)
self.play(Transform(concept_a, concept_b), Transform(label_a, label_b))
self.play(Circumscribe(concept_a, color=GOLD))
```

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

1. Class: {video_name}(Scene)
2. First line of construct(): self.camera.background_color = WHITE
3. Create exactly {TARGET_SLIDES} slides
4. Each slide: 25-35 seconds with self.wait() calls
5. Mark each slide: # Slide N: Title
6. End each slide: self.play(FadeOut(...), run_time=1)
7. Use BLACK for text (readable on white background)

═══════════════════════════════════════════════════════════════════════════════
COLOR PALETTE (use variety!)
═══════════════════════════════════════════════════════════════════════════════

- Text: BLACK, DARK_GRAY
- Primary: BLUE, BLUE_D, DARK_BLUE
- Highlights: ORANGE, GOLD, YELLOW  
- Success/Go: GREEN, TEAL
- Warning/Stop: RED, MAROON
- Subtle: GRAY, LIGHT_GRAY

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Provide the Python code:
```python
from manim import *

class {video_name}(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Slide 1: [Title]
        # ... diverse visual elements ...
        
        # Slide 2: [Title]
        # ... continue with variety ...
```

Then provide timing JSON:
```json
{{"slides": [{{"slide_no": 1, "duration": 30, "title": "Title"}}, ...]}}
```

NOW CREATE A VISUALLY RICH, DIVERSE ANIMATION! NO RECTANGLE-ONLY SLIDES!"""
        
        print_info("Calling LLM for creative Manim script...")
        print_info("(This may take longer due to creative generation)")
        
        # Use higher token limit and slightly higher temperature for creativity
        content, tokens = call_llm(prompt, max_tokens=5000, temperature=0.6)
        
        print_info(f"Tokens used: {tokens}")
        
        # Extract Python script
        script_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
        if script_match:
            base_script = script_match.group(1)
        else:
            script_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
            if script_match:
                base_script = script_match.group(1)
            else:
                print_error("Could not extract Python script from LLM response")
                print("\n" + "-"*80)
                print("RAW LLM RESPONSE:")
                print(content[:2000])
                print("-"*80)
                return 1
        
        # Extract JSON timings
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            try:
            timings_data = json.loads(json_match.group(1))
            timings = timings_data.get('slides', [])
            except json.JSONDecodeError:
                timings = [{'slide_no': i+1, 'duration': 30, 'title': f'Slide {i+1}'} for i in range(TARGET_SLIDES)]
                print_info("JSON parsing failed, using default timings")
        else:
            timings = [{'slide_no': i+1, 'duration': 30, 'title': f'Slide {i+1}'} for i in range(TARGET_SLIDES)]
            print_info("No timings found, using default")
        
        # Validate script syntax
        try:
            compile(base_script, '<string>', 'exec')
            print_success("Script syntax is valid")
        except SyntaxError as e:
            print_error(f"Script has syntax error: {e}")
            print("\n" + "-"*80)
            print("SCRIPT WITH ERROR:")
            for i, line in enumerate(base_script.split('\n'), 1):
                print(f"{i:4}: {line}")
            print("-"*80)
            return 1
        
        # Check for white background
        if 'WHITE' in base_script and 'background_color' in base_script:
            print_success("White background found in script")
        else:
            print_error("White background NOT found in script!")
        
        # Analyze visual richness - STRICT CHECK
        print("\n" + "-"*80)
        print("VISUAL DIVERSITY ANALYSIS:")
        
        diversity_checks = {
            'Arrows': (base_script.count('Arrow(') + base_script.count('CurvedArrow('), 4),
            'Circles': (base_script.count('Circle('), 3),
            'Rectangles': (base_script.count('Rectangle(') + base_script.count('RoundedRectangle('), 0),
            'Triangles': (base_script.count('Triangle('), 1),
            'Transforms': (base_script.count('Transform(') + base_script.count('ReplacementTransform('), 2),
            'Emphasis': (base_script.count('Indicate(') + base_script.count('Circumscribe(') + base_script.count('Flash('), 1),
            'Braces': (base_script.count('Brace('), 1),
            'GrowFrom': (base_script.count('GrowFrom'), 2),
        }
        
        total_score = 0
        for element, (count, target) in diversity_checks.items():
            status = "✓" if count >= target else "✗"
            print(f"  {status} {element}: {count} (target: {target}+)")
            if count >= target:
                total_score += 1
        
        # Color diversity check
        colors_used = []
        for color in ['BLUE', 'ORANGE', 'GREEN', 'RED', 'GOLD', 'TEAL', 'YELLOW', 'PURPLE']:
            if color in base_script:
                colors_used.append(color)
        print(f"  Colors used: {', '.join(colors_used)} ({len(colors_used)} different)")
        
        print("-"*80)
        
        if total_score >= 5:
            print_success(f"Visual diversity: EXCELLENT ({total_score}/8 checks passed)")
        elif total_score >= 3:
            print_info(f"Visual diversity: GOOD ({total_score}/8 checks passed)")
        else:
            print_error(f"Visual diversity: NEEDS IMPROVEMENT ({total_score}/8 checks passed)")
        
        # Count slides
        slide_count = len(re.findall(r'# Slide \d+', base_script))
        if slide_count >= TARGET_SLIDES - 1:
            print_success(f"Script contains {slide_count} slides (target: {TARGET_SLIDES})")
        else:
            print_info(f"Script contains {slide_count} slides (target was {TARGET_SLIDES})")
        
        # Save script
        script_file = TEST_DIR / 'base_script.py'
        script_file.write_text(base_script, encoding='utf-8')
        print_info(f"Script saved to: {script_file}")
        
        # Save timings
        timings_file = TEST_DIR / 'timings.json'
        timings_file.write_text(json.dumps(timings, indent=2))
        print_info(f"Timings saved to: {timings_file}")
        
        # Save token count
        tokens_file = TEST_DIR / 'tokens_step_03.txt'
        tokens_file.write_text(str(tokens))
        
        print_info(f"Script length: {len(base_script)} characters")
        print_info(f"Number of slides in timing: {len(timings)}")
        
        print_success("Creative Manim script generated successfully!")
        return 0
        
    except Exception as e:
        print_error(f"Failed to generate base script: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
