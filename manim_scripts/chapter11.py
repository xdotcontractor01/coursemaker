#!/usr/bin/env python3
"""
Chapter 11: Maintenance of Traffic, Sequence of Operations, and Staging
Pages 71-72 of Basic Highway Plan Reading

Compatible with Manim Community Edition v0.19.0+
"""

from manim import *
import wave
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

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = PROJECT_ROOT / "manifests/chapter11.json"
AUDIO_DIR = PROJECT_ROOT / "audio"
LOGO_PATH = PROJECT_ROOT / "test_workflow/GDOT LOGO For Video watermark - 200x110.svg"
AUDIO_BUFFER = 0.12

# Layout constants
TITLE_BUFF = 0.6
CONTENT_LEFT_BUFF = 1.0
BULLET_FONT_SIZE = 28
TITLE_FONT_SIZE = 44
MAIN_TITLE_FONT_SIZE = 44
SUBTITLE_FONT_SIZE = 30
LINE_SPACING = 0.35

# Colors
TITLE_COLOR = "#1565C0"
HEADING_COLOR = "#2E7D32"
BODY_COLOR = "#212121"
MUTED_COLOR = "#616161"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_wav_duration_seconds(filepath: str) -> float:
    try:
        with wave.open(filepath, 'rb') as wf:
            return wf.getnframes() / float(wf.getframerate())
    except Exception:
        return 0.0


def load_manifest():
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_section_heading(text: str) -> Text:
    heading = Text(text, font_size=TITLE_FONT_SIZE, weight=BOLD, color=HEADING_COLOR)
    heading.to_edge(UP, buff=TITLE_BUFF)
    return heading


def create_bullet_list(items: list) -> VGroup:
    bullets = VGroup()
    for item in items:
        bullet_text = Text(f"• {item}", font_size=BULLET_FONT_SIZE, color=BODY_COLOR)
        bullets.add(bullet_text)
    bullets.arrange(DOWN, aligned_edge=LEFT, buff=LINE_SPACING)
    return bullets


def load_logo() -> Mobject:
    try:
        if LOGO_PATH.exists():
            logo = ImageMobject(str(LOGO_PATH))
            logo.scale(0.15)
            logo.set_opacity(0.6)
            logo.to_edge(RIGHT + DOWN, buff=0.4)
            return logo
    except Exception:
        pass
    return None


# ============================================================================
# SCENE CLASSES
# ============================================================================

class Chapter11BaseScene(Scene):
    def render_scene(self, scene_data, manifest):
        scene_index = scene_data['index']
        title = scene_data['title']
        bullets = scene_data['bullets']
        audio_file = scene_data['tts_file'].replace('audio/', '')
        audio_path = AUDIO_DIR / audio_file
        
        if audio_path.exists():
            duration = get_wav_duration_seconds(str(audio_path))
            self.add_sound(str(audio_path))
            print(f"[AUDIO] Attached {audio_path} duration={duration:.2f}s")
        else:
            duration = scene_data.get('duration', 10.0)
        
        self.clear()
        logo = load_logo()
        if logo:
            self.add(logo)
        
        if scene_index == 1:
            chapter_text = Text("Chapter 11", font_size=SUBTITLE_FONT_SIZE, color=MUTED_COLOR)
            title_text = Text("Maintenance of Traffic", font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
            subtitle_text = Text("Sequence of Operations and Staging", font_size=30, color=MUTED_COLOR)
            pages_text = Text(f"Pages {manifest['pages']}", font_size=24, color=MUTED_COLOR)
            
            title_group = VGroup(chapter_text, title_text, subtitle_text, pages_text)
            title_group.arrange(DOWN, buff=0.4)
            title_group.move_to(ORIGIN)
            
            self.play(FadeIn(title_group), run_time=1.0)
            self.wait(duration + AUDIO_BUFFER - 1.0)
            self.play(FadeOut(title_group), run_time=0.5)
        else:
            heading = create_section_heading(title)
            self.play(FadeIn(heading), run_time=0.8)
            
            bullet_list = create_bullet_list(bullets)
            bullet_list.next_to(heading, DOWN, buff=0.8)
            bullet_list.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
            self.play(FadeIn(bullet_list), run_time=0.8)
            
            remaining = max(0, duration + AUDIO_BUFFER - 1.6)
            self.wait(remaining)
            self.play(*[FadeOut(mob) for mob in self.mobjects if mob != logo], run_time=0.5)


class Chapter11Full(Chapter11BaseScene):
    """Full Chapter 11 - all scenes"""
    
    def construct(self):
        manifest = load_manifest()
        print("\n" + "=" * 60)
        print(f"Chapter 11: {manifest['title']}")
        print("=" * 60)
        
        for scene_data in manifest['scenes']:
            self.render_scene(scene_data, manifest)
