"""
=============================================================================
GDOT VIDEO GENERATION - USER CONFIGURATION
=============================================================================

Edit this file to customize video generation settings and AI instructions.
These settings will be used by all workflow steps.
"""

# =============================================================================
# VIDEO NAMING
# =============================================================================
# Leave empty to auto-generate from INPUT.md title/first heading
# Or set a custom name (no spaces, use CamelCase)
# Example: "ErosionControl", "TrafficSafety", "PavementDesign"
VIDEO_NAME = ""

# =============================================================================
# CLEAR CACHE
# =============================================================================
# Set to True to delete old generated files before each new run
# Recommended: True (ensures fresh generation)
CLEAR_CACHE = True

# =============================================================================
# CUSTOM INSTRUCTIONS FOR AI
# =============================================================================
# These instructions are added to all AI prompts.
# Edit to match your specific content and requirements.

CUSTOM_INSTRUCTIONS = """
CONTENT SOURCE:
- Content is from Georgia Department of Transportation (GDOT) technical documents
- This includes manuals, guidelines, specifications, and training materials
- Topics may include: erosion control, bridge construction, traffic management, 
  pavement design, safety standards, environmental compliance, and more

STYLE REQUIREMENTS:
- Professional yet accessible language for DOT contractors and engineers
- Focus on practical applications and real-world scenarios
- Emphasize safety protocols and regulatory compliance
- Use technical terminology appropriately with clear explanations
- Break down complex procedures into digestible steps

VISUAL REQUIREMENTS:
- White or light backgrounds for professional appearance
- Clean, technical diagrams using shapes (Rectangle, Circle, Arrow, Line)
- High-contrast colors: BLACK for text, BLUE for shapes, ORANGE for highlights
- Process flows, checklists, and component diagrams
- Professional fonts and clear layouts
"""

# =============================================================================
# VISUAL STYLE SETTINGS
# =============================================================================
# Colors used in Manim animations
COLORS = {
    'background': 'WHITE',
    'text': 'BLACK',
    'shapes': 'BLUE',
    'highlights': 'ORANGE',
    'lines': 'GRAY',
}

# Image settings (reference images in top-right corner)
IMAGE_SETTINGS = {
    'width': 3.0,
    'height': 2.0,
    'x_position': 5.5,
    'y_position': 2.5,
    'opacity': 0.95,
    'label_text': 'Reference Image',
    'label_font_size': 14,
}

# =============================================================================
# AUDIO SETTINGS
# =============================================================================
# Text-to-speech voice (Microsoft Edge TTS)
# Options: en-US-GuyNeural, en-US-JennyNeural, en-US-AriaNeural
TTS_VOICE = "en-US-GuyNeural"

# =============================================================================
# SLIDE SETTINGS
# =============================================================================
# Default slide duration in seconds
DEFAULT_SLIDE_DURATION = 25

# Number of slides to generate
TARGET_SLIDES = 6

# =============================================================================
# ANIMATION STYLE (NEW - Creative Mode)
# =============================================================================
# Style preset for animations:
#   "professional" - Clean, corporate look with subtle animations
#   "educational" - Emphasis on clarity, step-by-step reveals
#   "dynamic" - More motion, transforms, and visual flair
#   "minimal" - Simple, focused animations with lots of white space
ANIMATION_STYLE = "educational"

# Manim features to allow:
#   "all" - Use any Manim capability (recommended for creative freedom)
#   "basic" - Stick to shapes, text, arrows (safer, less likely to error)
#   "advanced" - Include charts, graphs, math, transforms
MANIM_FEATURES = "all"

# Creative emphasis - what should the LLM prioritize:
#   "content_accuracy" - Focus on correctly representing the content
#   "visual_impact" - Focus on impressive, memorable animations
#   "balanced" - Balance between accuracy and visual appeal
CREATIVE_EMPHASIS = "balanced"

# Animation complexity:
#   "simple" - Basic Create, Write, FadeIn/Out animations
#   "moderate" - Add transforms, emphasis effects, staged reveals
#   "complex" - Full creative freedom with advanced animation sequences
ANIMATION_COMPLEXITY = "moderate"