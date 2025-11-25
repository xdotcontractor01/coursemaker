"""
Step 3: Generate Base Manim Script
Generates a visually rich Manim script with shapes and diagrams
"""

import re
import json
from shared import *

def main():
    """Generate base Manim script"""
    print_step(3, "Generate Base Manim Script")
    
    try:
        # Read summary
        summary_file = TEST_DIR / 'summary.txt'
        if not summary_file.exists():
            print_error("Summary file not found. Run step_02 first.")
            return 1
        
        summary = summary_file.read_text(encoding='utf-8')
        print_info(f"Loaded summary: {len(summary)} characters")
        
        # Generate Manim script with LLM
        prompt = f"""{SYSTEM_GDOT}

Task: Generate a visually rich Python Manim script with shapes, diagrams, and icons.

CRITICAL VISUAL REQUIREMENTS:
🚨 DO NOT CREATE TEXT-ONLY SLIDES! EVERY SLIDE MUST HAVE SHAPES/DIAGRAMS!
🚨 You MUST include at least 15-20 shape objects (Rectangle, Circle, Arrow, Line)
🚨 Create visual diagrams, not just bullet points

SETUP REQUIREMENTS:
- Class name: BridgeDesignManual
- First line in construct(): self.camera.background_color = WHITE
- Import: from manim import *
- Colors for contrast: BLACK (text), BLUE (shapes), ORANGE (highlights), GRAY (lines)

STRUCTURE (5-6 slides, each 25-30s):
1. Title slide with decorative shapes/border
2-5. Content slides with diagrams and visual elements
6. Conclusion with summary visual

MANDATORY VISUAL PATTERNS - Use these examples:

Example 1 - Component Diagram:
```python
# Slide 2: Bridge Components
title = Text("Bridge Components", color=BLACK, font_size=40).to_edge(UP)

# Visual diagram of bridge structure
beam = Rectangle(width=6, height=0.5, color=BLACK, fill_opacity=0.2, stroke_width=3)
bearing_left = Circle(radius=0.4, color=BLUE, fill_opacity=0.6, stroke_width=2).next_to(beam, DOWN+LEFT, buff=0.3)
bearing_right = Circle(radius=0.4, color=BLUE, fill_opacity=0.6, stroke_width=2).next_to(beam, DOWN+RIGHT, buff=0.3)

# Labels with arrows pointing to parts
beam_label = Text("Beam", color=BLACK, font_size=24).next_to(beam, UP, buff=0.3)
bearing_label = Text("Bearings", color=BLUE, font_size=24).next_to(bearing_left, DOWN, buff=0.3)

# Bullet points on the side
bullets = VGroup(
    Text("• Load distribution", color=BLACK, font_size=20),
    Text("• Structural support", color=BLACK, font_size=20),
    Text("• Connection points", color=BLACK, font_size=20)
).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(LEFT).shift(DOWN*0.5)

diagram = VGroup(beam, bearing_left, bearing_right, beam_label, bearing_label)

self.play(Write(title), run_time=1)
self.play(Create(diagram), run_time=2)
self.play(Write(bullets), run_time=1.5)
self.wait(25)
self.play(FadeOut(VGroup(title, diagram, bullets)), run_time=1)
```

Example 2 - Process Flow:
```python
# Slide 3: Inspection Process
title = Text("Inspection Process", color=BLACK, font_size=40).to_edge(UP)

# Flow diagram with steps
step1_box = Rectangle(width=2.5, height=1.2, color=BLUE, fill_opacity=0.3, stroke_width=2).shift(LEFT*4)
step2_box = Rectangle(width=2.5, height=1.2, color=BLUE, fill_opacity=0.3, stroke_width=2)
step3_box = Rectangle(width=2.5, height=1.2, color=BLUE, fill_opacity=0.3, stroke_width=2).shift(RIGHT*4)

# Arrows connecting steps
arrow1 = Arrow(step1_box.get_right(), step2_box.get_left(), color=GRAY, stroke_width=3)
arrow2 = Arrow(step2_box.get_right(), step3_box.get_left(), color=GRAY, stroke_width=3)

# Step labels inside boxes
step1_text = VGroup(
    Text("STEP 1", color=BLACK, font_size=16, weight=BOLD),
    Text("Verify", color=BLACK, font_size=20)
).arrange(DOWN, buff=0.1).move_to(step1_box)

step2_text = VGroup(
    Text("STEP 2", color=BLACK, font_size=16, weight=BOLD),
    Text("Inspect", color=BLACK, font_size=20)
).arrange(DOWN, buff=0.1).move_to(step2_box)

step3_text = VGroup(
    Text("STEP 3", color=BLACK, font_size=16, weight=BOLD),
    Text("Report", color=BLACK, font_size=20)
).arrange(DOWN, buff=0.1).move_to(step3_box)

flow = VGroup(step1_box, step2_box, step3_box, arrow1, arrow2, step1_text, step2_text, step3_text)

self.play(Write(title), run_time=1)
self.play(Create(flow), run_time=2.5)
self.wait(25)
self.play(FadeOut(VGroup(title, flow)), run_time=1)
```

Example 3 - Icon with Details:
```python
# Slide 4: Safety Requirements
title = Text("Safety Requirements", color=BLACK, font_size=40).to_edge(UP)

# Warning icon (triangle with exclamation)
warning_triangle = Polygon(
    [0, 0.8, 0], [-0.7, -0.4, 0], [0.7, -0.4, 0],
    color=ORANGE, fill_opacity=0.3, stroke_width=3
).shift(LEFT*4 + UP*0.5)
exclamation = Text("!", color=ORANGE, font_size=60, weight=BOLD).move_to(warning_triangle)

# Safety checklist with checkmarks
check1 = VGroup(
    Circle(radius=0.15, color=BLUE, fill_opacity=0.5),
    Text("✓", color=BLUE, font_size=20)
).arrange(RIGHT, buff=0).shift(RIGHT*0.5 + UP*1)
text1 = Text("PPE Required", color=BLACK, font_size=24).next_to(check1, RIGHT, buff=0.3)

check2 = VGroup(
    Circle(radius=0.15, color=BLUE, fill_opacity=0.5),
    Text("✓", color=BLUE, font_size=20)
).arrange(RIGHT, buff=0).shift(RIGHT*0.5)
text2 = Text("Torque Calibration", color=BLACK, font_size=24).next_to(check2, RIGHT, buff=0.3)

check3 = VGroup(
    Circle(radius=0.15, color=BLUE, fill_opacity=0.5),
    Text("✓", color=BLUE, font_size=20)
).arrange(RIGHT, buff=0).shift(RIGHT*0.5 + DOWN*1)
text3 = Text("Documentation", color=BLACK, font_size=24).next_to(check3, RIGHT, buff=0.3)

checklist = VGroup(check1, text1, check2, text2, check3, text3)
safety_icon = VGroup(warning_triangle, exclamation)

self.play(Write(title), run_time=1)
self.play(Create(safety_icon), run_time=1)
self.play(Create(checklist), run_time=2)
self.wait(25)
self.play(FadeOut(VGroup(title, safety_icon, checklist)), run_time=1)
```

YOUR OUTPUT REQUIREMENTS:
✓ 5-6 slides total
✓ Each slide has title + visual diagram (shapes) + text labels
✓ Use Rectangle, Circle, Arrow, Line, Polygon for diagrams
✓ Use VGroup to organize complex elements
✓ Clear animations: Create() for shapes, Write() for text, FadeOut() for transitions
✓ Each slide waits 25-30 seconds
✓ Position elements clearly: .to_edge(), .shift(), .next_to()

CODE QUALITY:
- Define ALL variables before using them
- Use consistent names (check spelling!)
- Test .next_to() references

Content Summary:
{summary}

Generate TWO outputs:
```python
from manim import *

class BridgeDesignManual(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # YOUR SLIDES HERE WITH SHAPES
```

```json
{{"slides": [{{"slide_no": 1, "duration": 25, "title": "Title"}}, ...]}}
```

🚨 REMEMBER: Include shapes (Rectangle, Circle, Arrow) in EVERY slide!"""
        
        print_info("Calling LLM for Manim script...")
        content, tokens = call_llm(prompt, max_tokens=2500, temperature=0.3)
        
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
                print(content[:1000])
                print("-"*80)
                return 1
        
        # Extract JSON timings
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            timings_data = json.loads(json_match.group(1))
            timings = timings_data.get('slides', [])
        else:
            timings = [{'slide_no': 1, 'duration': 30, 'title': 'Overview'}]
            print_info("No timings found, using default")
        
        # Validate script syntax
        try:
            compile(base_script, '<string>', 'exec')
            print_success("Script syntax is valid")
        except SyntaxError as e:
            print_error(f"Script has syntax error: {e}")
            print("\n" + "-"*80)
            print("SCRIPT WITH ERROR:")
            print(base_script)
            print("-"*80)
            return 1
        
        # Check for white background
        if 'WHITE' in base_script and 'background_color' in base_script:
            print_success("White background found in script")
        else:
            print_error("White background NOT found in script!")
        
        # Check for visual shapes
        shape_types = {
            'Rectangle': base_script.count('Rectangle('),
            'Circle': base_script.count('Circle('),
            'Arrow': base_script.count('Arrow('),
            'Line': base_script.count('Line('),
            'Polygon': base_script.count('Polygon(')
        }
        shape_count = sum(shape_types.values())
        
        print("\n" + "-"*80)
        print("VISUAL ELEMENTS ANALYSIS:")
        print(f"Total shape objects: {shape_count}")
        for shape, count in shape_types.items():
            if count > 0:
                print(f"  - {shape}: {count}")
        print("-"*80 + "\n")
        
        if shape_count >= 10:
            print_success(f"Excellent! Script contains {shape_count} visual shapes")
        elif shape_count >= 5:
            print_info(f"Good! Script contains {shape_count} shapes (could use more)")
        else:
            print_error(f"WARNING: Only {shape_count} shapes found! Script may be text-heavy")
        
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
        print_info(f"Number of slides: {len(timings)}")
        
        print_success("Base script generated successfully")
        return 0
        
    except Exception as e:
        print_error(f"Failed to generate base script: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

