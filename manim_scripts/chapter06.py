#!/usr/bin/env python3
"""
Chapter 6: Stationing, Symbols and Abbreviations
Pages 23-36 of Basic Highway Plan Reading

Compatible with Manim Community Edition v0.19.0+
"""

from manim import *
import wave
import os
import json
from pathlib import Path

# ============================================================================
# MANIM CONFIGURATION
# ============================================================================

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30
config.background_color = WHITE

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get the project root (one level up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = PROJECT_ROOT / "manifests/chapter06.json"
AUDIO_DIR = PROJECT_ROOT / "audio"
ASSETS_DIR = PROJECT_ROOT / "assets/images"
LOGO_PATH = PROJECT_ROOT / "assets/logo/gdot_watermark.svg"
AUDIO_BUFFER = 0.12
IMAGE_SCALE_FACTOR = 0.55

# ============================================================================
# LAYOUT CONSTANTS
# ============================================================================

TITLE_BUFF = 0.6
CONTENT_LEFT_BUFF = 1.0
BULLET_FONT_SIZE = 28
TITLE_FONT_SIZE = 44
MAIN_TITLE_FONT_SIZE = 52
SUBTITLE_FONT_SIZE = 30
LINE_SPACING = 0.35

# Color scheme for white background
TITLE_COLOR = "#1565C0"
HEADING_COLOR = "#2E7D32"
BODY_COLOR = "#212121"
ACCENT_COLOR = "#C62828"
MUTED_COLOR = "#616161"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_wav_duration_seconds(filepath: str) -> float:
    """Get WAV duration in seconds."""
    try:
        with wave.open(filepath, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception as e:
        print(f"[ERROR] Could not read audio file {filepath}: {e}")
        return 0.0


def load_manifest():
    """Load chapter manifest."""
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_section_heading(text: str) -> Text:
    """Create a consistently styled section heading."""
    heading = Text(text, font_size=TITLE_FONT_SIZE, weight=BOLD, color=HEADING_COLOR)
    heading.to_edge(UP, buff=TITLE_BUFF)
    return heading


def create_bullet_list(items: list, font_size: int = BULLET_FONT_SIZE) -> VGroup:
    """Create a consistently formatted bullet list."""
    bullets = VGroup()
    for item in items:
        bullet_text = Text(f"• {item}", font_size=font_size, color=BODY_COLOR)
        bullets.add(bullet_text)
    bullets.arrange(DOWN, aligned_edge=LEFT, buff=LINE_SPACING)
    return bullets


def load_image_safe(image_path: str, scale: float = IMAGE_SCALE_FACTOR) -> Mobject:
    """Safely load an image with fallback."""
    try:
        # Handle paths like "assets/images/chapter6/figure_6_1.jpg"
        full_path = Path(image_path)
        if not full_path.exists():
            # Try relative to ASSETS_DIR
            full_path = ASSETS_DIR / full_path.name
            if not full_path.exists():
                # Try with chapter subdirectory
                parts = image_path.split('/')
                if len(parts) >= 3:
                    chapter_dir = parts[-2]  # e.g., "chapter6"
                    filename = parts[-1]  # e.g., "figure_6_1.jpg"
                    full_path = ASSETS_DIR / chapter_dir / filename
        
        img = ImageMobject(str(full_path))
        img.scale(scale)
        border = SurroundingRectangle(img, color=MUTED_COLOR, buff=0.05, stroke_width=1)
        return Group(img, border)
    except Exception as e:
        print(f"[WARNING] Could not load image {image_path}: {e}")
        placeholder = Rectangle(width=4, height=3, color=MUTED_COLOR, stroke_width=2)
        label = Text("Image", font_size=20, color=MUTED_COLOR)
        return VGroup(placeholder, label)


def load_logo() -> Mobject:
    """Load the GDOT logo with opacity."""
    try:
        if LOGO_PATH.exists():
            logo = ImageMobject(str(LOGO_PATH))
            logo.scale(0.15)  # Adjust scale as needed
            logo.set_opacity(0.6)
            logo.to_edge(RIGHT + DOWN, buff=0.4)
            return logo
        else:
            print(f"[WARNING] Logo not found: {LOGO_PATH}")
            return None
    except Exception as e:
        print(f"[WARNING] Could not load logo: {e}")
        return None


# ============================================================================
# BASE SCENE CLASS
# ============================================================================

class Chapter06BaseScene(Scene):
    """Base scene class with common functionality."""
    
    def render_scene(self, scene_data, manifest):
        """Render a single scene from manifest data."""
        scene_index = scene_data['index']
        title = scene_data['title']
        bullets = scene_data['bullets']
        image_paths = scene_data.get('image_paths', [])
        audio_file = scene_data['tts_file'].replace('audio/', '')
        audio_path = AUDIO_DIR / audio_file
        
        # Get duration
        if audio_path.exists():
            duration = get_wav_duration_seconds(str(audio_path))
            self.add_sound(str(audio_path))
            print(f"[AUDIO] Attached {audio_path} duration={duration:.2f}s")
        else:
            duration = scene_data.get('duration', 10.0)
            print(f"[MISSING_NARRATION_FOR] audio/{audio_file}")
        
        # Clear previous scene
        self.clear()
        
        # Add logo (static, always visible)
        logo = load_logo()
        if logo:
            self.add(logo)
        
        # Title/Heading
        if "Title" in title or scene_index == 1:
            # Title scene
            chapter_text = Text("Chapter 6", font_size=SUBTITLE_FONT_SIZE, color=MUTED_COLOR)
            title_text = Text(manifest['title'], font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
            pages_text = Text(f"Pages {manifest['pages']}", font_size=24, color=MUTED_COLOR)
            
            title_group = VGroup(chapter_text, title_text, pages_text)
            title_group.arrange(DOWN, buff=0.4, center=True)
            title_group.move_to(ORIGIN)
            
            self.play(FadeIn(title_group), run_time=1.0)
            self.wait(duration + AUDIO_BUFFER - 1.0)
            self.play(FadeOut(title_group), run_time=0.5)
        else:
            # Regular scene with heading
            heading = create_section_heading(title)
            self.play(FadeIn(heading), run_time=0.8)
            
            # Bullets
            if bullets:
                bullet_list = create_bullet_list(bullets)
                bullet_list.next_to(heading, DOWN, buff=0.8)
                bullet_list.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
                
                # Images (if any)
                if image_paths:
                    image_group = Group()
                    for img_path in image_paths:
                        if img_path:  # Skip None values
                            img = load_image_safe(img_path)
                            image_group.add(img)
                    
                    if len(image_group) > 0:
                        if len(image_group) == 1:
                            image_group[0].next_to(bullet_list, RIGHT, buff=1.0)
                            image_group[0].align_to(bullet_list, UP)
                        else:
                            image_group.arrange(RIGHT, buff=0.5)
                            image_group.next_to(bullet_list, RIGHT, buff=1.0)
                            image_group.align_to(bullet_list, UP)
                        
                        # Animate bullets and images
                        self.play(FadeIn(bullet_list), run_time=0.8)
                        self.play(*[FadeIn(img) for img in image_group], run_time=0.8)
                    else:
                        self.play(FadeIn(bullet_list), run_time=0.8)
                else:
                    # No images, just bullets
                    self.play(FadeIn(bullet_list), run_time=0.8)
            
            # Wait for audio duration
            elapsed = 0.8 + (0.8 if bullets else 0) + (0.8 if image_paths else 0)
            remaining = max(0, duration + AUDIO_BUFFER - elapsed)
            self.wait(remaining)
            
            # Fade out
            self.play(*[FadeOut(mob) for mob in self.mobjects if mob != logo], run_time=0.5)


# ============================================================================
# LESSON SCENE CLASSES
# ============================================================================

class Chapter06Lesson01(Chapter06BaseScene):
    """Chapter 6, Lesson 1: Stationing (scenes 1-6)"""
    
    def construct(self):
        """Main construction method."""
        manifest = load_manifest()
        
        print("\n" + "=" * 60)
        print(f"Chapter 6, Lesson 1: Stationing")
        print("=" * 60)
        
        # Scenes 1-6
        scenes_to_render = [s for s in manifest['scenes'] if 1 <= s['index'] <= 6]
        
        for scene_data in scenes_to_render:
            self.render_scene(scene_data, manifest)


class Chapter06Lesson02(Chapter06BaseScene):
    """Chapter 6, Lesson 2: Symbols and Abbreviations (scenes 7-13)"""
    
    def construct(self):
        """Main construction method."""
        manifest = load_manifest()
        
        print("\n" + "=" * 60)
        print(f"Chapter 6, Lesson 2: Symbols and Abbreviations")
        print("=" * 60)
        
        # Scenes 7-13
        scenes_to_render = [s for s in manifest['scenes'] if 7 <= s['index'] <= 13]
        
        for scene_data in scenes_to_render:
            self.render_scene(scene_data, manifest)
