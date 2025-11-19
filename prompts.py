"""
System prompts for GDOT-DOT educational video generation.
Professional tone for contractors and engineers.
"""

# Core system prompt for GDOT-DOT style
SYSTEM_GDOT_DOT = """You are an expert technical writer and educator for the Georgia Department of Transportation (GDOT).
Your audience includes DOT contractors, engineers, and technical staff.
Your goal is to simplify Bridge Design Manuals and technical documentation while maintaining safety and compliance standards.

Style Guidelines:
- Professional, clear, and concise language
- Focus on practical applications and real-world scenarios
- Emphasize safety and regulatory compliance
- Use technical terminology appropriately
- Break down complex concepts into digestible steps
- Include specific examples relevant to DOT work

Visual Guidelines:
- White or light backgrounds for professional appearance
- Clean, technical diagrams and charts
- High-contrast colors for visibility
- Professional fonts and layouts
- Minimize decorative elements
- Focus on clarity and information density
"""

# Step 2: Summary generation
SUMMARY_PROMPT_TEMPLATE = """{system_prompt}

Task: Generate a concise 100-word summary of the following Markdown document.
Focus on:
- Main technical concepts
- Key safety or compliance points
- Practical applications for DOT contractors
- Critical takeaways

Markdown Document:
{markdown_content}

Provide only the summary text, no additional formatting or commentary.
"""

# Step 3: Base script generation
BASE_SCRIPT_PROMPT_TEMPLATE = """{system_prompt}

Task: Generate a Python Manim script for an educational video based on this content.

Requirements:
- FIRST LINE in construct() MUST be: config.background_color = WHITE
- Use BLACK, BLUE, or GRAY for all Text, shapes, and diagrams (for contrast)
- Professional DOT color scheme for visibility
- 4-6 slides/scenes with clear transitions
- Use Text, VGroup, shapes (Rectangle, Circle, Arrow) for diagrams
- Each scene should wait 20-30 seconds for narration
- Professional DOT-style visuals (charts, diagrams, bullet points)
- Include self.wait() calls with appropriate durations
- Clean, readable code with comments

Also generate a timings JSON object with format:
{{"slides": [{{"slide_no": 1, "duration": 25, "title": "Introduction"}}, ...]}}

Content Summary:
{summary}

Provide two outputs:
1. Complete Manim Python script
2. JSON timings object

Format as:
```python
# Manim script here
```

```json
// Timings here
```
"""

# Step 4: Image suggestions
IMAGE_LAYOUT_PROMPT_TEMPLATE = """{system_prompt}

Task: Suggest images and layouts for the video based on this script summary.

Requirements for Images:
- Technical, professional images relevant to GDOT/DOT work
- Search prompts should be specific (e.g., "bridge construction diagram", "traffic engineering chart")
- Target resolution: 800x600 pixels
- Prefer diagrams, technical illustrations, and real-world photos
- Maximum 3-4 images total

Requirements for Layouts:
- Text typically LEFT side (60% width), images RIGHT side (40% width)
- Use VGroup to prevent overlaps
- Specify positions as [x, y, z] coordinates for Manim
- Text should be readable and not obscured by images

Script Summary:
{script_summary}

Provide two JSON outputs:

1. images.json format:
[
  {{"slide_no": 1, "search_query": "bridge support structure diagram", "alt_text": "Bridge support"}},
  ...
]

2. layouts.json format:
[
  {{"slide_no": 1, "text_pos": [-3, 0, 0], "text_width": 0.6, "img_pos": [3, 0, 0], "img_scale": 0.8}},
  ...
]

Provide only the two JSON objects, clearly labeled.
"""

# Step 8: Narration generation
NARRATION_PROMPT_TEMPLATE = """{system_prompt}

Task: Generate natural, professional narration script for each slide of the video.

Requirements:
- Professional but conversational tone
- Explain technical concepts clearly
- Include practical tips and DOT-specific guidance
- Reference visuals when appropriate (e.g., "As shown in the diagram...")
- Natural pacing for text-to-speech
- Duration should match slide timings

Slide Information:
{slides_info}

Image Descriptions:
{image_info}

Provide JSON output:
[
  {{"slide_no": 1, "duration": 25, "narration_text": "Welcome to this overview of..."}},
  ...
]

Provide only the JSON array, no additional text.
"""

# Fallback templates
FALLBACK_SUMMARY = "Overview of GDOT technical documentation covering bridge design, safety protocols, and construction standards for DOT contractors and engineers."

FALLBACK_NARRATION_TEMPLATE = "This slide covers {title}. Please refer to the visual content for detailed information."

# Manim base template for fallback
MANIM_BASE_TEMPLATE = """from manim import *

class GDOTScene(Scene):
    def construct(self):
        config.background_color = WHITE
        
        # Title slide
        title = Text("GDOT Educational Video", color=BLACK, font_size=48)
        subtitle = Text("Generated from Markdown", color=GRAY, font_size=24)
        subtitle.next_to(title, DOWN)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(3)
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Content slide
        content = Text("Content Overview", color=BLACK, font_size=36)
        self.play(Write(content))
        self.wait(2)
        self.play(FadeOut(content))
        
        # End slide
        end = Text("Thank You", color=BLACK, font_size=48)
        self.play(Write(end))
        self.wait(2)
"""

def get_summary_prompt(markdown_content: str) -> str:
    """Generate summary prompt with system context."""
    return SUMMARY_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_GDOT_DOT,
        markdown_content=markdown_content
    )

def get_base_script_prompt(summary: str) -> str:
    """Generate base script prompt with system context."""
    return BASE_SCRIPT_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_GDOT_DOT,
        summary=summary
    )

def get_image_layout_prompt(script_summary: str) -> str:
    """Generate image/layout suggestions prompt."""
    return IMAGE_LAYOUT_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_GDOT_DOT,
        script_summary=script_summary
    )

def get_narration_prompt(slides_info: str, image_info: str = "") -> str:
    """Generate narration script prompt."""
    return NARRATION_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_GDOT_DOT,
        slides_info=slides_info,
        image_info=image_info or "No images available"
    )

