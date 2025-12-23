"""
Shared utilities and configuration for workflow test scripts
Loads settings from CONFIG.py for user customization
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# ==================== PATHS ====================
_SCRIPT_DIR = Path(__file__).parent.resolve()
TEST_DIR = _SCRIPT_DIR / 'test_output'
TEST_DIR.mkdir(exist_ok=True)
INPUT_FILE = _SCRIPT_DIR / 'INPUT.md'
CONFIG_FILE = _SCRIPT_DIR / 'CONFIG.py'

# ==================== LOAD USER CONFIG ====================
# Default values (overridden by CONFIG.py if it exists)
VIDEO_NAME = ""
CLEAR_CACHE = True
CUSTOM_INSTRUCTIONS = ""
TTS_VOICE = "en-US-GuyNeural"
DEFAULT_SLIDE_DURATION = 25
TARGET_SLIDES = 6
IMAGE_SETTINGS = {
    'width': 3.0,
    'height': 2.0,
    'x_position': 5.5,
    'y_position': 2.5,
    'opacity': 0.95,
    'label_text': 'Reference Image',
    'label_font_size': 14,
}

# Load CONFIG.py if it exists
if CONFIG_FILE.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("config", CONFIG_FILE)
    config_module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(config_module)
        # Import settings from config
        VIDEO_NAME = getattr(config_module, 'VIDEO_NAME', VIDEO_NAME)
        CLEAR_CACHE = getattr(config_module, 'CLEAR_CACHE', CLEAR_CACHE)
        CUSTOM_INSTRUCTIONS = getattr(config_module, 'CUSTOM_INSTRUCTIONS', CUSTOM_INSTRUCTIONS)
        TTS_VOICE = getattr(config_module, 'TTS_VOICE', TTS_VOICE)
        DEFAULT_SLIDE_DURATION = getattr(config_module, 'DEFAULT_SLIDE_DURATION', DEFAULT_SLIDE_DURATION)
        TARGET_SLIDES = getattr(config_module, 'TARGET_SLIDES', TARGET_SLIDES)
        IMAGE_SETTINGS = getattr(config_module, 'IMAGE_SETTINGS', IMAGE_SETTINGS)
    except Exception as e:
        print(f"Warning: Could not load CONFIG.py: {e}")

# ==================== API KEYS ====================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not found in environment")
    print("Please set it: export OPENAI_API_KEY='your-key-here'")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# ==================== SYSTEM PROMPT (GENERALIZED) ====================
SYSTEM_GDOT = f"""You are an expert technical writer and educator for the Georgia Department of Transportation (GDOT).
Your audience includes DOT contractors, engineers, and technical staff.
Your goal is to create clear, educational content from GDOT technical documentation while maintaining safety and compliance standards.

{CUSTOM_INSTRUCTIONS}
"""

# ==================== VIDEO NAMING ====================
def extract_title_from_content(content: str) -> str:
    """Extract title from markdown content (first heading or first line)"""
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Remove markdown heading markers
        if line.startswith('#'):
            title = line.lstrip('#').strip()
            if title:
                return title
        # Use first non-empty line if no heading
        return line[:50]  # Limit to 50 chars
    return "GDOTContent"

def generate_class_name(title: str) -> str:
    """Convert a title to a valid Python class name (CamelCase)"""
    # Remove special characters, keep alphanumeric and spaces
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    # Split into words and capitalize each
    words = clean.split()
    # Take first few words to keep it short
    words = words[:4]
    # Convert to CamelCase
    class_name = ''.join(word.capitalize() for word in words)
    # Ensure it starts with a letter
    if class_name and not class_name[0].isalpha():
        class_name = 'GDOT' + class_name
    return class_name or 'GDOTContent'

def get_video_name() -> str:
    """Get the video/class name from config or input file"""
    # Priority 1: User-defined in CONFIG.py
    if VIDEO_NAME:
        return VIDEO_NAME
    
    # Priority 2: Extract from INPUT.md
    if INPUT_FILE.exists():
        content = INPUT_FILE.read_text(encoding='utf-8')
        title = extract_title_from_content(content)
        return generate_class_name(title)
    
    # Priority 3: Check test_output/input.md
    input_md = TEST_DIR / 'input.md'
    if input_md.exists():
        content = input_md.read_text(encoding='utf-8')
        title = extract_title_from_content(content)
        return generate_class_name(title)
    
    # Fallback
    return 'GDOTContent'

# ==================== SAMPLE TEST CONTENT ====================
SAMPLE_MD = """# Sample GDOT Technical Content

This is sample content for testing the video generation workflow.

# Section 1: Overview

The Georgia Department of Transportation (GDOT) provides technical documentation for contractors, engineers, and staff working on transportation infrastructure projects.

# Section 2: Key Requirements

1. All work must comply with GDOT specifications
2. Safety protocols must be followed at all times
3. Proper documentation is required for all activities

# Section 3: Procedures

Follow the established procedures for your specific project type. Contact the appropriate GDOT division for guidance on complex situations.
"""

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
    """Call OpenAI API with system prompt"""
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

def clear_output_cache():
    """Clear previous generated files from test_output"""
    import shutil
    
    # Files/folders to clear
    items_to_clear = [
        'summary.txt',
        'base_script.py',
        'render_script.py',
        'timings.json',
        'images.json',
        'downloaded_images.json',
        'narration.json',
        'audio_clips.json',
        'video_path.txt',
        'final_video_path.txt',
        'audio_clips',
        'images',
        'media',
    ]
    
    cleared = 0
    for item in items_to_clear:
        path = TEST_DIR / item
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                cleared += 1
            except Exception as e:
                print_error(f"Could not clear {item}: {e}")
    
    return cleared
