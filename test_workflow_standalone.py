"""
Standalone Test Script for Video Generation Workflow
Runs all 11 steps with terminal output for debugging
"""

import os
import json
import re
import subprocess
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# ==================== CONFIGURATION ====================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not found in environment")
    print("Please set it: export OPENAI_API_KEY='your-key-here'")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# Test content
SAMPLE_MD = """# SECTION 3 SUPERSTRUCTURE

The superstructure of a bridge is that portion of the bridge above the caps. This includes the bearing devices, beams, decks, and railings.

# A. Check of Substructure

The location, both vertically and horizontally, of the substructure controls the location of the superstructure. The location of the substructure must be checked before superstructure construction is commenced. The Contractor must verify the elevations for all bearingseats before setting beams. Also, the centerline of each beam or girder shall be laid out and the location of the anchor bolt holes or dowel barschecked.

# B. Preparation of Bearing Areas

The areas of the cap where the bridge seats bear must be level and flat. These areas have been finished with a Type IV finish. A short (not over 6 inch) spirit level should be used to check these areas. If the areas are high in elevation or are not flat (either convex or concave) they must be ground down to a true surface. If the resulting area is low or started out low because of an error in elevation the lowness shall be compensated for by either shimming under the bearing plates or by adjusting the coping over the beams. If the error is greater than ½" it shall be corrected by shimming. This is for steel or prestressed concrete beams or girders.

C. Structural Steel Beams and Girders: (Section 501 SteelStructures)

# 1. Shear Connectors

Shear connectors extend out from the beams into the deck. Most of the time shear connectors will be welded to the beams in the shop. If the Engineer is in doubt about the acceptability of the shear connector welding or if the shear connectors are to be welded in the field contact the Inspection Services Branch of the OMAT for advice.

# 2. Erection of Beams

Beams shall be erected in accordance with the Specifications. All beams and girders must be preinspected at time of delivery as evidenced by GDT stamp on each member. No erection shall commence until approved erection drawings are on the job. Beams should be braced together as they are erected.

# 3. Bearings

If unbonded elastomeric pads are used on concrete, no preparation other than leveling of the bearing areas is required. A level but textured (floated) surface is best for these pads. If the pads are to be bonded to the cap concrete the bearing area must be ground smooth.

Self-lubricating plates, bushings or sliding plates fabricated from bronze material require special test reports. As the structural steel is shop inspected the Inspection Services Branch of the OMAT will inspect all these plates that pass through the fabricating shop. Inspected bronze plates will not be tagged or stamped accepted but will arrive on the project in shipments of GDT stamped primary steel members. If bronze plates do not arrive on the job in shipments which also include GDT stamped steel, they shall be considered as being uninspected. Notice by telephone should be given to the Inspection Service Branch of the OMAT when uninspected bronze plates are received on the project. All bronze plates must be physically inspected by the Engineer.

# 4. Inspection of Splices Connections

The Contractor is responsible for providing safe access to allow inspection of all splices and connections.

a. Bolted

All bolted splices and diaphragm connections shall be checked for torque. Calibration of torque wrenches must be done before bolted connections begin.

# b. Welded

All welding on Georgia DOT projects must be performed by GDOT certified welders. Welding for butt splices must be performed by specially certified welders and must be ultrasonically inspected. The Project Engineer is responsible for visual inspection of all fillet welds and should have a weld fillet gauge (available through OMAT) to check the size of fillet welds. The Inspection Services Branch of the OMAT will ultrasonically test all welding of butt splices. The Inspection Services Branch of OMAT should be notified at least three days in advance when welding of butt splices is required in order to schedule ultrasonic testing of the welds. They should also be contacted if there is any question on the acceptability of other welded connections of for other guidance. Prior to scheduling non-destructive testing of field butt welds the Project Engineer shall inspect each welded splice to ensure that the Contractor has done the following:

1) Completed welding on all splices.   

2) Removed all back-up strips and ground flush with parentmaterial.   

3) Removed all notch-effect in weld profile.   

4) Removed all torch marks, slag, weld splatter, etc.   

5) Dressed-up weld profile to acceptable workmanship and design.

The Inspection Services inspector will locate and mark all rejects and furnish a written report of the findings. The Engineer must be present when the rejects are located and marked. Record the results in the diary. After the rejected welds are repaired, they shall be inspected again."""

# Create test output directory
TEST_DIR = Path('./test_output')
TEST_DIR.mkdir(exist_ok=True)

# ==================== SYSTEM PROMPTS ====================
SYSTEM_GDOT = """You are an expert technical writer and educator for the Georgia Department of Transportation (GDOT).
Your audience includes DOT contractors, engineers, and technical staff.
Your goal is to simplify Bridge Design Manuals and technical documentation while maintaining safety and compliance standards.

Style Guidelines:
- Professional, clear, and concise language
- Focus on practical applications and real-world scenarios
- Emphasize safety and regulatory compliance
- Use technical terminology appropriately
- Break down complex concepts into digestible steps

Visual Guidelines:
- White or light backgrounds for professional appearance
- Clean, technical diagrams and charts
- High-contrast colors for visibility
- Professional fonts and layouts
- Focus on clarity and information density"""

# ==================== HELPER FUNCTIONS ====================
def print_step(step_no, title):
    """Print step header"""
    print("\n" + "="*80)
    print(f"STEP {step_no}: {title}")
    print("="*80)

def print_success(message):
    """Print success message"""
    print(f"[SUCCESS] {message}")

def print_error(message):
    """Print error message"""
    print(f"[ERROR] {message}")

def print_info(message):
    """Print info message"""
    print(f"[INFO] {message}")

def call_llm(prompt, max_tokens=1500, temperature=0.3):
    """Call OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_GDOT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens
        return content, tokens
    except Exception as e:
        print_error(f"LLM call failed: {e}")
        raise

# ==================== WORKFLOW STEPS ====================

def step_0_load_prompts():
    """Step 0: Load system prompts"""
    print_step(0, "Load System Prompts")
    
    prompt_file = TEST_DIR / 'system_prompt.txt'
    prompt_file.write_text(SYSTEM_GDOT)
    print_info(f"System prompt saved to: {prompt_file}")
    print_success("System prompts loaded")
    return SYSTEM_GDOT

def step_1_validate_input(md_content):
    """Step 1: Validate markdown input"""
    print_step(1, "Validate Markdown Input")
    
    print_info(f"Content length: {len(md_content)} characters")
    print_info(f"Lines: {len(md_content.split(chr(10)))}")
    
    # Save input
    input_file = TEST_DIR / 'input.md'
    input_file.write_text(md_content)
    print_info(f"Input saved to: {input_file}")
    
    if len(md_content) < 50:
        print_error("Content too short")
        return False
    
    print_success("Input validation passed")
    return True

def step_2_generate_summary(md_content):
    """Step 2: Generate summary"""
    print_step(2, "Generate Summary")
    
    prompt = f"""{SYSTEM_GDOT}

Task: Generate a concise 100-word summary of the following Markdown document.
Focus on:
- Main technical concepts
- Key safety or compliance points
- Practical applications for DOT contractors
- Critical takeaways

Markdown Document:
{md_content}

Provide only the summary text, no additional formatting or commentary."""
    
    print_info("Calling LLM for summary...")
    summary, tokens = call_llm(prompt, max_tokens=300)
    
    print_info(f"Tokens used: {tokens}")
    print_info(f"Summary length: {len(summary)} characters")
    print("\n" + "-"*80)
    print("SUMMARY:")
    print(summary)
    print("-"*80)
    
    # Save summary
    summary_file = TEST_DIR / 'summary.txt'
    summary_file.write_text(summary, encoding='utf-8')
    print_info(f"Summary saved to: {summary_file}")
    
    print_success("Summary generated")
    return summary, tokens

def step_3_generate_base_script(summary):
    """Step 3: Generate base Manim script"""
    print_step(3, "Generate Base Manim Script")
    
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
            raise ValueError("Script extraction failed")
    
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
        raise
    
    # Check for white background
    if 'WHITE' in base_script and 'background_color' in base_script:
        print_success("White background found in script")
    else:
        print_error("White background NOT found in script!")
    
    # Check for visual shapes
    shape_count = 0
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
        print_error("Consider regenerating with more emphasis on visual elements")
    
    # Save script (with UTF-8 encoding for special characters)
    script_file = TEST_DIR / 'base_script.py'
    script_file.write_text(base_script, encoding='utf-8')
    print_info(f"Script saved to: {script_file}")
    
    # Save timings
    timings_file = TEST_DIR / 'timings.json'
    timings_file.write_text(json.dumps(timings, indent=2))
    print_info(f"Timings saved to: {timings_file}")
    
    print_info(f"Script length: {len(base_script)} characters")
    print_info(f"Number of slides: {len(timings)}")
    
    print_success("Base script generated")
    return base_script, timings, tokens

def step_7_render_video(script_content):
    """Step 7: Render video with Manim"""
    print_step(7, "Render Silent Video")
    
    # Save as render script
    render_file = TEST_DIR / 'render_script.py'
    render_file.write_text(script_content, encoding='utf-8')
    print_info(f"Render script: {render_file}")
    
    # Run Manim
    media_dir = TEST_DIR / 'media'
    cmd = [
        'manim',
        '-pqh',  # Preview, high quality (1080p)
        '--format', 'mp4',
        '--media_dir', str(media_dir),
        str(render_file),
        'BridgeDesignManual'
    ]
    
    print_info(f"Running: {' '.join(cmd)}")
    print_info("This may take 3-5 minutes...")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    print_info(f"Render completed in {elapsed:.1f} seconds")
    
    if result.returncode == 0:
        print_success("Video rendered successfully!")
        
        # Find output video
        video_files = list(media_dir.glob('**/BridgeDesignManual.mp4'))
        if video_files:
            video_path = video_files[0]
            print_success(f"Video location: {video_path}")
            print_info(f"Video size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
            return str(video_path)
        else:
            print_error("Video file not found after render")
            return None
    else:
        print_error("Manim render failed!")
        print("\n" + "-"*80)
        print("MANIM ERROR OUTPUT:")
        print(result.stderr[-2000:])  # Last 2000 chars
        print("-"*80)
        raise Exception("Render failed")

def step_8_generate_narration(summary, timings):
    """Step 8: Generate narration script"""
    print_step(8, "Generate Narration")
    
    slides_info = "\n".join([
        f"Slide {s.get('slide_no', i+1)}: {s.get('title', 'Content')} (Duration: {s.get('duration', 25)}s)"
        for i, s in enumerate(timings)
    ])
    
    prompt = f"""{SYSTEM_GDOT}

Task: Generate detailed, educational narration for each slide with explanations.

NARRATION REQUIREMENTS:
- Professional yet conversational tone
- EXPLAIN what the audience is seeing on screen
- Reference visual elements ("As shown in the diagram...", "Notice the blue circles...")
- Provide practical DOT-specific tips and examples
- Include safety reminders where relevant
- Natural pacing for text-to-speech (approximately 3-4 words per second)
- Fill the entire duration with valuable content

NARRATION STRUCTURE PER SLIDE:
1. Opening (2-3 seconds): Introduce the topic
2. Main Content (15-20 seconds): Explain key concepts, reference visuals
3. Practical Tip (3-5 seconds): Real-world application
4. Transition (2-3 seconds): Lead into next topic

EXAMPLE GOOD NARRATION:
"Let's examine the bridge superstructure components. As you can see in the diagram, the main beam shown in black distributes the load across the structure. Notice the blue circular bearings at each end - these critical connection points allow for thermal expansion while maintaining structural integrity. For GDOT contractors, it's essential to verify that bearing surfaces are level and properly prepared before beam installation. Any irregularities could compromise load distribution and require costly corrections later."

Slide Information:
{slides_info}

Content Summary:
{summary}

CRITICAL: Write 50-80 words per slide to fill the duration. Be educational and descriptive.

Provide JSON output:
[
  {{"slide_no": 1, "duration": 25, "narration_text": "Detailed narration here..."}},
  ...
]

Provide only the JSON array, no additional text."""
    
    print_info("Calling LLM for narration...")
    content, tokens = call_llm(prompt, max_tokens=1500)
    
    print_info(f"Tokens used: {tokens}")
    
    # Extract JSON
    try:
        # Try to find JSON in response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            narrations = json.loads(json_match.group(0))
        else:
            narrations = json.loads(content)
    except json.JSONDecodeError as e:
        print_error(f"Could not parse narration JSON: {e}")
        print("\n" + "-"*80)
        print("RAW RESPONSE:")
        print(content)
        print("-"*80)
        raise
    
    # Save narrations
    narration_file = TEST_DIR / 'narration.json'
    narration_file.write_text(json.dumps(narrations, indent=2))
    print_info(f"Narration saved to: {narration_file}")
    
    print_info(f"Generated {len(narrations)} narration clips")
    for i, narr in enumerate(narrations):
        text = narr.get('narration_text', '')
        duration = narr.get('duration', 0)
        print_info(f"  Clip {i}: {duration}s, {len(text)} chars")
    
    print_success("Narration generated")
    return narrations, tokens

def step_9_generate_audio(narrations):
    """Step 9: Generate audio with edge-tts"""
    print_step(9, "Generate Audio Clips")
    
    try:
        import edge_tts
        import asyncio
    except ImportError:
        print_error("edge-tts not installed. Run: pip install edge-tts")
        print_info("Skipping audio generation...")
        return None
    
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
            return output_file
            
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
    
    try:
        audio_files = asyncio.run(generate_all())
        
        # Verify we got audio files
        if not audio_files or len(audio_files) == 0:
            print_error("No audio files were generated!")
            return None
        
        # Check files exist
        valid_files = []
        for audio_file in audio_files:
            if audio_file and audio_file.exists() and audio_file.stat().st_size > 0:
                valid_files.append(audio_file)
            else:
                print_error(f"Invalid audio file: {audio_file}")
        
        if not valid_files:
            print_error("No valid audio files were generated!")
            return None
        
        print_success(f"Successfully generated {len(valid_files)} audio clips")
        
        # Show summary
        total_size = sum(f.stat().st_size for f in valid_files)
        print_info(f"Total audio size: {total_size / 1024:.2f} KB")
        
        return valid_files
        
    except Exception as e:
        print_error(f"Audio generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def step_10_merge_audio_video(video_path, audio_files, narrations):
    """Step 10: Merge audio clips and sync with video"""
    print_step(10, "Merge Audio & Video")
    
    if not audio_files or len(audio_files) == 0:
        print_error("No audio files to merge - returning silent video")
        print_info(f"Silent video location: {video_path}")
        return video_path
    
    print_info(f"Found {len(audio_files)} audio files to merge")
    
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip
        from pydub import AudioSegment
    except ImportError:
        print_error("moviepy or pydub not installed. Run: pip install moviepy pydub")
        print_info("Skipping audio merge...")
        return video_path
    
    print_info("Loading video file...")
    video = VideoFileClip(video_path)
    video_duration = video.duration
    print_info(f"Video duration: {video_duration:.2f}s")
    
    # Concatenate all audio clips
    print_info("Concatenating audio clips...")
    audio_clips = []
    total_audio_duration = 0
    
    for i, audio_file in enumerate(audio_files):
        audio_clip = AudioFileClip(str(audio_file))
        audio_clips.append(audio_clip)
        duration = audio_clip.duration
        total_audio_duration += duration
        print_info(f"  Clip {i}: {duration:.2f}s")
    
    full_audio = concatenate_audioclips(audio_clips)
    print_info(f"Total audio duration: {total_audio_duration:.2f}s")
    
    # Check alignment
    duration_diff = abs(video_duration - total_audio_duration)
    if duration_diff > 2.0:
        print_error(f"WARNING: Duration mismatch of {duration_diff:.2f}s")
        print_info(f"Video: {video_duration:.2f}s, Audio: {total_audio_duration:.2f}s")
        
        # Pad audio if shorter
        if total_audio_duration < video_duration:
            from moviepy.editor import AudioClip
            silence_duration = video_duration - total_audio_duration
            silence = AudioClip(lambda t: 0, duration=silence_duration)
            full_audio = concatenate_audioclips([full_audio, silence])
            print_info(f"Padded audio with {silence_duration:.2f}s silence")
    else:
        print_success(f"Good alignment! Difference: {duration_diff:.2f}s")
    
    # Attach audio to video
    print_info("Attaching audio to video...")
    final_video = video.set_audio(full_audio)
    
    # Save final video
    output_path = TEST_DIR / 'final_video_with_audio.mp4'
    print_info(f"Saving final video to: {output_path}")
    print_info("This may take 1-2 minutes...")
    
    final_video.write_videofile(
        str(output_path),
        codec='libx264',
        audio_codec='aac',
        logger=None,
        fps=60
    )
    
    # Cleanup
    video.close()
    full_audio.close()
    for clip in audio_clips:
        clip.close()
    
    print_success(f"Final video created: {output_path}")
    print_info(f"Final size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return str(output_path)

# ==================== MAIN EXECUTION ====================

def main():
    """Run complete workflow"""
    print("\n")
    print("="*80)
    print("GDOT VIDEO GENERATION - STANDALONE TEST WORKFLOW")
    print("="*80)
    print(f"Output directory: {TEST_DIR.absolute()}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")
    
    total_tokens = 0
    
    try:
        # Step 0
        system_prompt = step_0_load_prompts()
        
        # Step 1
        if not step_1_validate_input(SAMPLE_MD):
            return
        
        # Step 2
        summary, tokens = step_2_generate_summary(SAMPLE_MD)
        total_tokens += tokens
        
        # Step 3
        base_script, timings, tokens = step_3_generate_base_script(summary)
        total_tokens += tokens
        
        # Skip steps 4-6 (image related) for now
        print_step(4, "Suggest Images (SKIPPED)")
        print_info("Skipping image suggestions for this test")
        
        print_step(5, "Fetch Images (SKIPPED)")
        print_info("Skipping image fetching for this test")
        
        print_step(6, "Inject Images (SKIPPED)")
        print_info("Skipping image injection for this test")
        
        # Step 7
        video_path = step_7_render_video(base_script)
        
        # Step 8
        narrations, tokens = step_8_generate_narration(summary, timings)
        total_tokens += tokens
        
        # Step 9
        audio_files = step_9_generate_audio(narrations)
        
        # Step 10
        if audio_files and video_path:
            final_video = step_10_merge_audio_video(video_path, audio_files, narrations)
        else:
            final_video = video_path
            print_info("Skipping audio merge (no audio files)")
        
        # Summary
        print("\n")
        print("="*80)
        print("WORKFLOW COMPLETE!")
        print("="*80)
        print(f"[SUCCESS] Total tokens used: {total_tokens}")
        print(f"[SUCCESS] Output directory: {TEST_DIR.absolute()}")
        if video_path:
            print(f"[SUCCESS] Silent video: {video_path}")
        if final_video and final_video != video_path:
            print(f"[SUCCESS] Final video with audio: {final_video}")
        print("\n")
        print("Files generated:")
        for file in sorted(TEST_DIR.rglob('*')):
            if file.is_file():
                size = file.stat().st_size
                print(f"  - {file.relative_to(TEST_DIR)} ({size:,} bytes)")
        print("\n")
        
        # Quality Report
        print("="*80)
        print("VIDEO QUALITY REPORT")
        print("="*80)
        
        # Check generated script for quality
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
            
            # Count text elements
            text_count = script_content.count('Text(')
            vgroups = script_content.count('VGroup')
            
            print(f"Visual Elements:")
            print(f"  Shapes: {total_shapes} (Rectangles: {rectangles}, Circles: {circles}, Arrows: {arrows}, Lines: {lines}, Polygons: {polygons})")
            print(f"  Text objects: {text_count}")
            print(f"  VGroups: {vgroups}")
            print(f"  White background: {'YES' if 'WHITE' in script_content else 'NO'}")
            
            # Quality assessment
            print(f"\nQuality Assessment:")
            if total_shapes >= 15:
                print(f"  Visual Richness: EXCELLENT ✓ ({total_shapes} shapes)")
            elif total_shapes >= 10:
                print(f"  Visual Richness: GOOD ✓ ({total_shapes} shapes)")
            elif total_shapes >= 5:
                print(f"  Visual Richness: FAIR (~{total_shapes} shapes, could be better)")
            else:
                print(f"  Visual Richness: POOR ✗ (only {total_shapes} shapes)")
            
            if text_count >= 10:
                print(f"  Text Content: GOOD ✓ ({text_count} text elements)")
            else:
                print(f"  Text Content: NEEDS MORE ✗ ({text_count} text elements)")
            
            if vgroups >= 3:
                print(f"  Organization: EXCELLENT ✓ ({vgroups} VGroups)")
            else:
                print(f"  Organization: BASIC ({vgroups} VGroups)")
        
        # Audio check
        if audio_files:
            print(f"\nAudio:")
            print(f"  Clips generated: {len(audio_files)} ✓")
            total_size = sum(f.stat().st_size for f in audio_files)
            print(f"  Total audio size: {total_size / 1024:.2f} KB")
        else:
            print(f"\nAudio: NOT GENERATED ✗")
        
        # Video check
        if final_video and final_video != video_path:
            print(f"\nFinal Output:")
            print(f"  Video with audio: YES ✓")
            print(f"  Location: {final_video}")
        elif video_path:
            print(f"\nFinal Output:")
            print(f"  Silent video: YES")
            print(f"  Location: {video_path}")
        
        print("\n" + "="*80)
        print("\nNext Steps:")
        print("1. Watch the final video")
        print("2. Review the generated script in test_output/base_script.py")
        print("3. If quality is good, integrate changes into main workflow")
        print("="*80 + "\n")
        
    except Exception as e:
        print("\n")
        print_error(f"Workflow failed: {e}")
        import traceback
        print("\n" + "-"*80)
        print("FULL ERROR TRACEBACK:")
        traceback.print_exc()
        print("-"*80)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

