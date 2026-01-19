#!/usr/bin/env python3
"""
Chapter 4: Summary & Detailed Estimate Quantities
Pages 15-17 of Basic Highway Plan Reading

Compatible with Manim Community Edition v0.18.0+
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
MANIFEST_PATH = PROJECT_ROOT / "manifests/chapter_04.json"
AUDIO_DIR = PROJECT_ROOT / "audio"
ASSETS_DIR = PROJECT_ROOT / "assets/images/chapter4"
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
    with open(MANIFEST_PATH, 'r') as f:
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
        # Extract filename from path like "assets/images/chapter4/figure_4_1.jpg"
        img_name = Path(image_path).name
        img_path = ASSETS_DIR / img_name
        img = ImageMobject(str(img_path))
        img.scale(scale)
        border = SurroundingRectangle(img, color=MUTED_COLOR, buff=0.05, stroke_width=1)
        return Group(img, border)
    except Exception as e:
        print(f"[WARNING] Could not load image {image_path}: {e}")
        placeholder = Rectangle(width=4, height=3, color=MUTED_COLOR, stroke_width=2)
        label = Text("Image", font_size=20, color=MUTED_COLOR)
        return VGroup(placeholder, label)


# ============================================================================
# MAIN SCENE CLASS
# ============================================================================

class Chapter04Video(Scene):
    """Chapter 4: Summary & Detailed Estimate Quantities"""
    
    def construct(self):
        """Main construction method."""
        manifest = load_manifest()
        
        print("\n" + "=" * 60)
        print(f"Chapter 4: {manifest['title']}")
        print("=" * 60)
        
        # Verify audio files
        for scene in manifest['scenes']:
            audio_path = AUDIO_DIR / scene['tts_file_path'].replace('audio/', '')
            if audio_path.exists():
                duration = get_wav_duration_seconds(str(audio_path))
                print(f"[OK] Scene {scene['index']}: {audio_path.name} ({duration:.1f}s)")
            else:
                print(f"[MISSING] Scene {scene['index']}: {audio_path.name}")
        
        print("=" * 60 + "\n")
        
        # Execute scenes
        self.scene_1_title(manifest['scenes'][0])
        self.scene_2_summary_quantities(manifest['scenes'][1])
        self.scene_3_drainage_summary(manifest['scenes'][2])
        self.scene_4_detailed_estimate(manifest['scenes'][3])
        self.scene_5_summary(manifest['scenes'][4])
    
    def scene_1_title(self, scene_data):
        """Display title screen."""
        audio_path = AUDIO_DIR / scene_data['tts_file_path'].replace('audio/', '')
        duration = scene_data.get('expected_duration', 5.0)
        
        if audio_path.exists():
            self.add_sound(str(audio_path))
            duration = get_wav_duration_seconds(str(audio_path))
        else:
            print(f"[MISSING] {audio_path}")
        
        elapsed = 0.0
        
        # Visual elements
        chapter = Text("Chapter 4", font_size=SUBTITLE_FONT_SIZE, color=MUTED_COLOR)
        title = Text("Summary & Detailed Estimate", font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        subtitle = Text("Construction Quantities", font_size=SUBTITLE_FONT_SIZE, color=BODY_COLOR)
        pages = Text("Pages 15-17", font_size=24, color=MUTED_COLOR)
        
        title_group = VGroup(chapter, title, subtitle, pages)
        title_group.arrange(DOWN, buff=0.4, center=True)
        title_group.move_to(ORIGIN)
        
        # Animations
        self.play(FadeIn(chapter), run_time=0.8)
        elapsed += 0.8
        self.play(FadeIn(title), run_time=1.0)
        elapsed += 1.0
        self.play(FadeIn(subtitle), FadeIn(pages), run_time=0.8)
        elapsed += 0.8
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        self.play(FadeOut(title_group), run_time=0.5)
    
    def scene_2_summary_quantities(self, scene_data):
        """Explain Summary of Quantities."""
        audio_path = AUDIO_DIR / scene_data['tts_file_path'].replace('audio/', '')
        duration = scene_data.get('expected_duration', 10.0)
        
        if audio_path.exists():
            self.add_sound(str(audio_path))
            duration = get_wav_duration_seconds(str(audio_path))
        else:
            print(f"[MISSING] {audio_path}")
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Summary of Quantities")
        bullets = create_bullet_list(scene_data['bullets'])
        bullets.next_to(heading, DOWN, buff=0.8)
        bullets.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 0.5)
        
        # Load image if available
        image_group = None
        if scene_data.get('image_paths') and len(scene_data['image_paths']) > 0:
            image_group = load_image_safe(scene_data['image_paths'][0])
            image_group.next_to(bullets, DOWN, buff=0.8)
            image_group.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        if image_group:
            self.play(FadeIn(image_group), run_time=1.0)
            elapsed += 1.0
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    def scene_3_drainage_summary(self, scene_data):
        """Explain Drainage Summary."""
        audio_path = AUDIO_DIR / scene_data['tts_file_path'].replace('audio/', '')
        duration = scene_data.get('expected_duration', 10.0)
        
        if audio_path.exists():
            self.add_sound(str(audio_path))
            duration = get_wav_duration_seconds(str(audio_path))
        else:
            print(f"[MISSING] {audio_path}")
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Drainage Summary")
        bullets = create_bullet_list(scene_data['bullets'])
        bullets.next_to(heading, DOWN, buff=0.8)
        bullets.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 0.5)
        
        # Load image if available
        image_group = None
        if scene_data.get('image_paths') and len(scene_data['image_paths']) > 0:
            image_group = load_image_safe(scene_data['image_paths'][0])
            image_group.next_to(bullets, DOWN, buff=0.8)
            image_group.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        if image_group:
            self.play(FadeIn(image_group), run_time=1.0)
            elapsed += 1.0
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    def scene_4_detailed_estimate(self, scene_data):
        """Explain Detailed Estimate."""
        audio_path = AUDIO_DIR / scene_data['tts_file_path'].replace('audio/', '')
        duration = scene_data.get('expected_duration', 10.0)
        
        if audio_path.exists():
            self.add_sound(str(audio_path))
            duration = get_wav_duration_seconds(str(audio_path))
        else:
            print(f"[MISSING] {audio_path}")
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Detailed Estimate")
        bullets = create_bullet_list(scene_data['bullets'])
        bullets.next_to(heading, DOWN, buff=0.8)
        bullets.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 0.5)
        
        # Note: Figure 4-3 is a table, not an image, so no image_paths
        # We'll just show the bullets
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    def scene_5_summary(self, scene_data):
        """Display summary."""
        audio_path = AUDIO_DIR / scene_data['tts_file_path'].replace('audio/', '')
        duration = scene_data.get('expected_duration', 10.0)
        
        if audio_path.exists():
            self.add_sound(str(audio_path))
            duration = get_wav_duration_seconds(str(audio_path))
        else:
            print(f"[MISSING] {audio_path}")
        
        elapsed = 0.0
        
        # Visual elements
        title = Text("Key Takeaways", font_size=TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        title.to_edge(UP, buff=TITLE_BUFF + 0.3)
        
        bullets = create_bullet_list(scene_data['bullets'])
        bullets.next_to(title, DOWN, buff=0.8)
        
        next_text = Text("Next: Views", font_size=28, color=TITLE_COLOR)
        next_text.to_edge(DOWN, buff=1.0)
        
        # Animations
        self.play(FadeIn(title), run_time=0.8)
        elapsed += 0.8
        
        for bullet in bullets:
            self.play(FadeIn(bullet), run_time=0.5)
            elapsed += 0.5
        
        self.play(FadeIn(next_text), run_time=0.6)
        elapsed += 0.6
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


if __name__ == "__main__":
    print(f"\nTo render: manim -qh manim_chapter04.py Chapter04Video")







