#!/usr/bin/env python3
"""
Chapter 1, Video 4: Scales and Design Data
Pages 8-11 of Basic Highway Plan Reading

Topics:
- Engineer's vs architect's scale
- Bar scale
- Project length table
- Design data on the Cover Sheet

Compatible with Manim Community Edition v0.18.0+
"""

from manim import *
import requests
import wave
import os
from pathlib import Path

# ============================================================================
# MANIM CONFIGURATION
# ============================================================================

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30
config.background_color = WHITE

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================

AUDIO_DIR = PROJECT_ROOT / "audio"
VIDEO_NUM = 4
AUDIO_PREFIX = f"ch1_v{VIDEO_NUM}"
AUDIO_BUFFER = 0.12

# ============================================================================
# LAYOUT CONSTANTS
# ============================================================================

TITLE_BUFF = 0.6
CONTENT_LEFT_BUFF = 1.0
IMAGE_SCALE_FACTOR = 0.55
BULLET_FONT_SIZE = 28
TITLE_FONT_SIZE = 44
MAIN_TITLE_FONT_SIZE = 52
SUBTITLE_FONT_SIZE = 30
LINE_SPACING = 0.35

# Color scheme
TITLE_COLOR = "#1565C0"
HEADING_COLOR = "#2E7D32"
BODY_COLOR = "#212121"
ACCENT_COLOR = "#C62828"
MUTED_COLOR = "#616161"

# ============================================================================
# IMAGE URLS
# ============================================================================

IMAGE_URLS = {
    "figure_1_9": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/25aa20b11bc17322942fbc4764af7c95258df8b9344efb9fe6dabc401aa15195.jpg",
    "figure_1_10": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/a76db50d8c607aa0d9ea60c66f0dc3f1c971e837b6d2559b99083f4b3a0fc7c9.jpg",
    "figure_1_11": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/2135d6be8ed6c64c473b2d046c198d4a3bcd7ba83eec233eb614fa67706efa69.jpg",
}

ASSETS_DIR = PROJECT_ROOT / "assets/images/chapter1"

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


def get_audio_path(scene_num: int) -> str:
    """Get the path to the audio file for a scene."""
    padded = os.path.join(str(AUDIO_DIR), f"{AUDIO_PREFIX}_scene_{scene_num:02d}.wav")
    if os.path.exists(padded):
        return padded
    simple = os.path.join(str(AUDIO_DIR), f"{AUDIO_PREFIX}_scene_{scene_num}.wav")
    if os.path.exists(simple):
        return simple
    return padded


def audio_exists(scene_num: int) -> bool:
    """Check if the audio file exists."""
    return os.path.exists(get_audio_path(scene_num))


def download_images():
    """Download all required images."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    for name, url in IMAGE_URLS.items():
        output_path = ASSETS_DIR / f"{name}.jpg"
        if output_path.exists():
            print(f"[OK] {name}.jpg exists")
            continue
        try:
            print(f"Downloading {name}.jpg...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"[OK] Downloaded {name}.jpg")
        except Exception as e:
            print(f"[ERROR] {name}: {e}")


def create_section_heading(text: str) -> Text:
    """Create a section heading."""
    heading = Text(text, font_size=TITLE_FONT_SIZE, weight=BOLD, color=HEADING_COLOR)
    heading.to_edge(UP, buff=TITLE_BUFF)
    return heading


def create_bullet_list(items: list, font_size: int = BULLET_FONT_SIZE) -> VGroup:
    """Create a bullet list."""
    bullets = VGroup()
    for item in items:
        bullet_text = Text(f"• {item}", font_size=font_size, color=BODY_COLOR)
        bullets.add(bullet_text)
    bullets.arrange(DOWN, aligned_edge=LEFT, buff=LINE_SPACING)
    return bullets


def load_image_safe(image_name: str, scale: float = IMAGE_SCALE_FACTOR) -> Mobject:
    """Safely load an image with fallback."""
    try:
        img_path = str(ASSETS_DIR / f"{image_name}.jpg")
        img = ImageMobject(img_path)
        img.scale(scale)
        border = SurroundingRectangle(img, color=MUTED_COLOR, buff=0.05, stroke_width=1)
        return Group(img, border)
    except Exception:
        placeholder = Rectangle(width=4, height=3, color=MUTED_COLOR, stroke_width=2)
        label = Text("Image", font_size=20, color=MUTED_COLOR)
        return VGroup(placeholder, label)


# ============================================================================
# MAIN SCENE CLASS
# ============================================================================

class Chapter1Video4(Scene):
    """Video 4: Scales and Design Data"""
    
    def construct(self):
        """Main construction method."""
        
        # Download images
        download_images()
        
        # Verify audio files
        print("\n" + "=" * 60)
        print(f"Chapter 1, Video {VIDEO_NUM}: Scales and Design Data")
        print("=" * 60)
        
        for i in range(1, 9):
            audio_path = get_audio_path(i)
            if os.path.exists(audio_path):
                duration = get_wav_duration_seconds(audio_path)
                print(f"[OK] Scene {i}: {audio_path} ({duration:.1f}s)")
            else:
                print(f"[MISSING] Scene {i}: {audio_path}")
        
        print("=" * 60 + "\n")
        
        # Execute scenes
        self.scene_1_title()
        self.scene_2_scale_intro()
        self.scene_3_engineer_vs_architect()
        self.scene_4_engineer_scale_detail()
        self.scene_5_bar_scale()
        self.scene_6_project_length()
        self.scene_7_design_data()
        self.scene_8_summary()
    
    # ========================================================================
    # SCENE 1: Title
    # ========================================================================
    
    def scene_1_title(self):
        """Display title screen."""
        scene_num = 1
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 5.0
        
        elapsed = 0.0
        
        # Visual elements
        chapter = Text("Chapter 1", font_size=SUBTITLE_FONT_SIZE, color=MUTED_COLOR)
        title = Text("Scales and Design Data", font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        subtitle = Text("Reading and Interpreting Plan Dimensions", font_size=SUBTITLE_FONT_SIZE, color=BODY_COLOR)
        pages = Text("Pages 8-11", font_size=24, color=MUTED_COLOR)
        
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
    
    # ========================================================================
    # SCENE 2: Scale Introduction
    # ========================================================================
    
    def scene_2_scale_intro(self):
        """Introduce why scales are used."""
        scene_num = 2
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 10.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Why Use Scales?")
        
        main_point = Text(
            "Large projects on manageable sheets",
            font_size=32,
            color=TITLE_COLOR,
            weight=BOLD
        )
        main_point.next_to(heading, DOWN, buff=0.8)
        
        types = VGroup(
            Text("Engineer's Scale", font_size=28, color=HEADING_COLOR, weight=BOLD),
            Text("• Used for roadway plans", font_size=24, color=BODY_COLOR),
            Text("Architect's Scale", font_size=28, color=HEADING_COLOR, weight=BOLD),
            Text("• Used for structure plans", font_size=24, color=BODY_COLOR),
        )
        types.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        types.next_to(main_point, DOWN, buff=0.6)
        types.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 1.0)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(main_point), run_time=0.8)
        elapsed += 0.8
        
        for item in types:
            self.play(FadeIn(item, shift=RIGHT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 3: Engineer vs Architect Scale
    # ========================================================================
    
    def scene_3_engineer_vs_architect(self):
        """Compare engineer's and architect's scales."""
        scene_num = 3
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 15.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Engineer's vs Architect's Scale")
        
        scale_img = load_image_safe("figure_1_9", scale=0.45)
        scale_img.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        scale_img.shift(DOWN * 0.3)
        
        caption = Text("Figure 1-9: Engineer's (top) and Architect's (bottom)", font_size=18, color=MUTED_COLOR)
        caption.next_to(scale_img, DOWN, buff=0.2)
        
        comparison = VGroup(
            Text("Engineer's Scale:", font_size=26, color=HEADING_COLOR, weight=BOLD),
            Text('1" = 10 ft, 1" = 20 ft, etc.', font_size=24, color=BODY_COLOR),
            Text("Architect's Scale:", font_size=26, color=HEADING_COLOR, weight=BOLD),
            Text('1/4" = 1 ft, 1/8" = 1 ft, etc.', font_size=24, color=BODY_COLOR),
        )
        comparison.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        comparison.next_to(scale_img, RIGHT, buff=0.8)
        comparison.align_to(scale_img, UP)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(scale_img), run_time=1.0)
        elapsed += 1.0
        
        self.play(FadeIn(caption), run_time=0.5)
        elapsed += 0.5
        
        for item in comparison:
            self.play(FadeIn(item, shift=RIGHT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 4: Engineer's Scale Detail
    # ========================================================================
    
    def scene_4_engineer_scale_detail(self):
        """Show engineer's scale detail."""
        scene_num = 4
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 15.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Engineer's Scale Divisions")
        
        scale_detail = load_image_safe("figure_1_10", scale=0.5)
        scale_detail.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        scale_detail.shift(DOWN * 0.3)
        
        caption = Text("Figure 1-10: Detail of Engineer's Scale", font_size=18, color=MUTED_COLOR)
        caption.next_to(scale_detail, DOWN, buff=0.2)
        
        divisions = Text("Divisions: 10, 20, 30, 40, 50, 60 per inch", font_size=26, color=BODY_COLOR, weight=BOLD)
        
        examples = create_bullet_list([
            '1" = 10 feet (10 divisions)',
            '1" = 100 feet (multiples)',
            '1" = 1000 feet (multiples)'
        ], font_size=24)
        
        content = VGroup(divisions, examples)
        content.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        content.next_to(scale_detail, RIGHT, buff=0.8)
        content.align_to(scale_detail, UP)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(scale_detail), run_time=1.0)
        elapsed += 1.0
        
        self.play(FadeIn(caption), run_time=0.5)
        elapsed += 0.5
        
        self.play(FadeIn(divisions), run_time=0.6)
        elapsed += 0.6
        
        for bullet in examples:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 5: Bar Scale
    # ========================================================================
    
    def scene_5_bar_scale(self):
        """Explain bar scale."""
        scene_num = 5
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 12.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Bar Scale")
        
        bar_img = load_image_safe("figure_1_11", scale=0.5)
        bar_img.next_to(heading, DOWN, buff=0.6)
        bar_img.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        
        caption = Text("Figure 1-11: Bar Scale from Plan Sheet 60", font_size=18, color=MUTED_COLOR)
        caption.next_to(bar_img, DOWN, buff=0.2)
        
        explanation = create_bullet_list([
            "Graphical scale representation",
            "Shows scale in feet",
            "Measure directly on drawing",
            "Each sheet notes its scale"
        ], font_size=24)
        explanation.next_to(bar_img, RIGHT, buff=0.8)
        explanation.align_to(bar_img, UP)
        
        warning = Text(
            "Half-size plans: DOUBLE measurements!",
            font_size=24,
            color=ACCENT_COLOR,
            weight=BOLD
        )
        warning.next_to(explanation, DOWN, buff=0.6)
        warning.align_to(explanation, LEFT)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(bar_img), run_time=1.0)
        elapsed += 1.0
        
        self.play(FadeIn(caption), run_time=0.5)
        elapsed += 0.5
        
        for bullet in explanation:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.4)
            elapsed += 0.4
        
        self.play(FadeIn(warning), run_time=0.6)
        elapsed += 0.6
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 6: Project Length Table
    # ========================================================================
    
    def scene_6_project_length(self):
        """Explain project length table."""
        scene_num = 6
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 12.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Length of Project Table")
        
        # Simplified table
        table_data = VGroup(
            Text("Project: STP-IM-022-1(26)", font_size=24, color=TITLE_COLOR, weight=BOLD),
            VGroup(
                Text("Spalding Co:", font_size=22, color=MUTED_COLOR),
                Text("6.76 mi", font_size=22, color=BODY_COLOR, weight=BOLD)
            ).arrange(RIGHT, buff=0.3),
            VGroup(
                Text("Butts Co:", font_size=22, color=MUTED_COLOR),
                Text("0.88 mi", font_size=22, color=BODY_COLOR, weight=BOLD)
            ).arrange(RIGHT, buff=0.3),
            VGroup(
                Text("Total:", font_size=22, color=HEADING_COLOR),
                Text("7.64 miles", font_size=22, color=HEADING_COLOR, weight=BOLD)
            ).arrange(RIGHT, buff=0.3),
        )
        table_data.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        table_data.next_to(heading, DOWN, buff=0.6)
        table_data.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 1.0)
        
        components = create_bullet_list([
            "Net Length of Roadway",
            "Net Length of Bridges",
            "Net Length of Exceptions",
            "Gross Length of Project"
        ], font_size=24)
        components.next_to(table_data, RIGHT, buff=1.5)
        components.align_to(table_data, UP)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for item in table_data:
            self.play(FadeIn(item), run_time=0.5)
            elapsed += 0.5
        
        for bullet in components:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.4)
            elapsed += 0.4
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 7: Design Data
    # ========================================================================
    
    def scene_7_design_data(self):
        """Explain design data section."""
        scene_num = 7
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 15.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Design Data")
        
        intro = Text(
            "Traffic data determines lanes and pavement depth",
            font_size=26,
            color=TITLE_COLOR
        )
        intro.next_to(heading, DOWN, buff=0.6)
        
        data_items = VGroup(
            VGroup(Text("A.D.T. (2027):", font_size=24, color=MUTED_COLOR), Text("31,900", font_size=24, color=BODY_COLOR)).arrange(RIGHT, buff=0.3),
            VGroup(Text("A.D.T. (2007):", font_size=24, color=MUTED_COLOR), Text("19,100", font_size=24, color=BODY_COLOR)).arrange(RIGHT, buff=0.3),
            VGroup(Text("D.H.V.:", font_size=24, color=MUTED_COLOR), Text("2,880", font_size=24, color=BODY_COLOR)).arrange(RIGHT, buff=0.3),
            VGroup(Text("Trucks:", font_size=24, color=MUTED_COLOR), Text("13%", font_size=24, color=BODY_COLOR)).arrange(RIGHT, buff=0.3),
            VGroup(Text("Design Speed:", font_size=24, color=MUTED_COLOR), Text("55/45 mph", font_size=24, color=BODY_COLOR)).arrange(RIGHT, buff=0.3),
            VGroup(Text("Classification:", font_size=24, color=MUTED_COLOR), Text("Rural Arterial", font_size=24, color=BODY_COLOR)).arrange(RIGHT, buff=0.3),
        )
        data_items.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        data_items.next_to(intro, DOWN, buff=0.5)
        data_items.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 1.5)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(intro), run_time=0.6)
        elapsed += 0.6
        
        for item in data_items:
            self.play(FadeIn(item), run_time=0.4)
            elapsed += 0.4
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 8: Summary
    # ========================================================================
    
    def scene_8_summary(self):
        """Display final summary."""
        scene_num = 8
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 15.0
        
        elapsed = 0.0
        
        # Visual elements
        title = Text("Chapter 1 Complete!", font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        title.to_edge(UP, buff=TITLE_BUFF)
        
        items = [
            "Engineer's and architect's scales",
            "Bar scales on plan sheets",
            "Project length calculations",
            "Design data interpretation"
        ]
        
        checklist = VGroup()
        for item in items:
            checkmark = Text("[OK]", font_size=26, color=HEADING_COLOR)
            text = Text(item, font_size=BULLET_FONT_SIZE, color=BODY_COLOR)
            row = VGroup(checkmark, text).arrange(RIGHT, buff=0.4)
            checklist.add(row)
        
        checklist.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        checklist.next_to(title, DOWN, buff=0.8)
        
        thanks = Text("Thank You!", font_size=40, weight=BOLD, color=TITLE_COLOR)
        thanks.move_to(ORIGIN)
        
        next_chapter = Text("Next: Chapter 2 - Index and Revision Summary", font_size=26, color=MUTED_COLOR)
        next_chapter.to_edge(DOWN, buff=0.8)
        
        # Animations
        self.play(FadeIn(title), run_time=0.8)
        elapsed += 0.8
        
        for item in checklist:
            self.play(FadeIn(item), run_time=0.4)
            elapsed += 0.4
        
        mid_wait = max(0, (duration - elapsed - 3.0) / 2)
        self.wait(mid_wait)
        elapsed += mid_wait
        
        self.play(FadeOut(title), FadeOut(checklist), run_time=0.6)
        elapsed += 0.6
        
        self.play(FadeIn(thanks), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(next_chapter), run_time=0.5)
        elapsed += 0.5
        
        remaining = max(0.5, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(FadeOut(thanks), FadeOut(next_chapter), run_time=0.8)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"\nTo render: manim -qh chapter1/chapter1_video4.py Chapter1Video4")









