#!/usr/bin/env python3
"""
Chapter 1, Video 2: The Cover Sheet
Pages 2-4 of Basic Highway Plan Reading

Topics:
- What the Cover Sheet is
- Information contained on the Cover Sheet
- Project description and P.I. Numbers

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
VIDEO_NUM = 2
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
    "figure_1_1": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/ddb56e09976ec69fdd20ab21dc84e58d5b4028f35fb851299a574d24508fc150.jpg",
    "figure_1_2": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/58966cfcfe9fd560a7a2c4cfc8772c8239f36114ab22e616e7797f8de01c9cf4.jpg",
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
    """Check if the audio file for a scene exists."""
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

class Chapter1Video2(Scene):
    """Video 2: The Cover Sheet"""
    
    def construct(self):
        """Main construction method."""
        
        # Download images
        download_images()
        
        # Verify audio files
        print("\n" + "=" * 60)
        print(f"Chapter 1, Video {VIDEO_NUM}: The Cover Sheet")
        print("=" * 60)
        
        for i in range(1, 7):
            audio_path = get_audio_path(i)
            if os.path.exists(audio_path):
                duration = get_wav_duration_seconds(audio_path)
                print(f"[OK] Scene {i}: {audio_path} ({duration:.1f}s)")
            else:
                print(f"[MISSING] Scene {i}: {audio_path}")
        
        print("=" * 60 + "\n")
        
        # Execute scenes
        self.scene_1_title()
        self.scene_2_what_is_coversheet()
        self.scene_3_coversheet_elements()
        self.scene_4_project_description()
        self.scene_5_pi_numbers()
        self.scene_6_summary()
    
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
        title = Text("The Cover Sheet", font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        subtitle = Text("Project Identification and Description", font_size=SUBTITLE_FONT_SIZE, color=BODY_COLOR)
        pages = Text("Pages 2-4", font_size=24, color=MUTED_COLOR)
        
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
    # SCENE 2: What is a Cover Sheet
    # ========================================================================
    
    def scene_2_what_is_coversheet(self):
        """Explain what a cover sheet is."""
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
        heading = create_section_heading("What is the Cover Sheet?")
        
        # Load figure 1-1
        cover_img = load_image_safe("figure_1_1", scale=0.45)
        cover_img.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        cover_img.shift(DOWN * 0.3)
        
        caption = Text("Figure 1-1: Plan View of Project", font_size=18, color=MUTED_COLOR)
        caption.next_to(cover_img, DOWN, buff=0.2)
        
        bullets = create_bullet_list([
            "First sheet in plan set",
            "Title page and summary",
            "Project overview at a glance"
        ], font_size=26)
        bullets.next_to(cover_img, RIGHT, buff=0.8)
        bullets.align_to(cover_img, UP)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(cover_img), run_time=1.0)
        elapsed += 1.0
        
        self.play(FadeIn(caption), run_time=0.5)
        elapsed += 0.5
        
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 3: Cover Sheet Elements
    # ========================================================================
    
    def scene_3_coversheet_elements(self):
        """List cover sheet elements."""
        scene_num = 3
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 20.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Cover Sheet Elements")
        
        col1_items = [
            "Project name",
            "Project number",
            "P.I. Number",
            "County",
            "Congressional district",
            "Standard spec note"
        ]
        
        col2_items = [
            "Location sketch",
            "Revisions box",
            "Project limits",
            "Length of project",
            "Route numbers",
            "Signature boxes"
        ]
        
        col1 = VGroup()
        for item in col1_items:
            text = Text(f"• {item}", font_size=24, color=BODY_COLOR)
            col1.add(text)
        col1.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        
        col2 = VGroup()
        for item in col2_items:
            text = Text(f"• {item}", font_size=24, color=BODY_COLOR)
            col2.add(text)
        col2.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        
        columns = VGroup(col1, col2).arrange(RIGHT, buff=2.0, aligned_edge=UP)
        columns.next_to(heading, DOWN, buff=0.6)
        
        optional = Text("Optional: Legend, Sheet Layout, Index", font_size=22, color=MUTED_COLOR)
        optional.next_to(columns, DOWN, buff=0.5)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for i in range(max(len(col1), len(col2))):
            anims = []
            if i < len(col1):
                anims.append(FadeIn(col1[i], shift=RIGHT * 0.1))
            if i < len(col2):
                anims.append(FadeIn(col2[i], shift=RIGHT * 0.1))
            self.play(*anims, run_time=0.4)
            elapsed += 0.4
        
        self.play(FadeIn(optional), run_time=0.5)
        elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 4: Project Description
    # ========================================================================
    
    def scene_4_project_description(self):
        """Explain project description."""
        scene_num = 4
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 12.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Project Description")
        
        # Load figure 1-2
        desc_img = load_image_safe("figure_1_2", scale=0.5)
        desc_img.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        desc_img.shift(DOWN * 0.3)
        
        caption = Text("Figure 1-2: Description of Project", font_size=18, color=MUTED_COLOR)
        caption.next_to(desc_img, DOWN, buff=0.2)
        
        details = VGroup(
            Text("Project: SR 16 Construction", font_size=26, color=BODY_COLOR),
            Text("Location: Spalding & Butts Counties", font_size=26, color=BODY_COLOR),
            Text("P.I. Number: 332520", font_size=26, color=HEADING_COLOR, weight=BOLD),
        )
        details.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        details.next_to(desc_img, RIGHT, buff=0.8)
        details.align_to(desc_img, UP)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(desc_img), run_time=1.0)
        elapsed += 1.0
        
        self.play(FadeIn(caption), run_time=0.5)
        elapsed += 0.5
        
        for detail in details:
            self.play(FadeIn(detail, shift=RIGHT * 0.2), run_time=0.6)
            elapsed += 0.6
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 5: P.I. Numbers
    # ========================================================================
    
    def scene_5_pi_numbers(self):
        """Explain P.I. and project numbers."""
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
        heading = create_section_heading("Project Identification Numbers")
        
        # Table-like display
        table_data = VGroup(
            VGroup(
                Text("P.I. Number:", font_size=26, color=MUTED_COLOR),
                Text("332520", font_size=26, color=BODY_COLOR, weight=BOLD)
            ).arrange(RIGHT, buff=0.5),
            VGroup(
                Text("Project Number:", font_size=26, color=MUTED_COLOR),
                Text("STP-IM-022-1(26)", font_size=26, color=BODY_COLOR, weight=BOLD)
            ).arrange(RIGHT, buff=0.5),
            VGroup(
                Text("State Route:", font_size=26, color=MUTED_COLOR),
                Text("SR 16", font_size=26, color=BODY_COLOR, weight=BOLD)
            ).arrange(RIGHT, buff=0.5),
        )
        table_data.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        table_data.next_to(heading, DOWN, buff=0.8)
        table_data.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 1.0)
        
        note = Text(
            "Projects may have multiple P.I. Numbers",
            font_size=24,
            color=ACCENT_COLOR
        )
        note.next_to(table_data, DOWN, buff=0.6)
        note.align_to(table_data, LEFT)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for row in table_data:
            self.play(FadeIn(row), run_time=0.6)
            elapsed += 0.6
        
        self.play(FadeIn(note), run_time=0.6)
        elapsed += 0.6
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 6: Summary
    # ========================================================================
    
    def scene_6_summary(self):
        """Display summary."""
        scene_num = 6
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 10.0
        
        elapsed = 0.0
        
        # Visual elements
        title = Text("Key Takeaways", font_size=TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        title.to_edge(UP, buff=TITLE_BUFF + 0.3)
        
        items = [
            "Cover Sheet is the first page",
            "Contains project identification",
            "Shows location and route info",
            "P.I. Numbers track projects"
        ]
        
        checklist = VGroup()
        for item in items:
            checkmark = Text("[OK]", font_size=26, color=HEADING_COLOR)
            text = Text(item, font_size=BULLET_FONT_SIZE, color=BODY_COLOR)
            row = VGroup(checkmark, text).arrange(RIGHT, buff=0.4)
            checklist.add(row)
        
        checklist.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        checklist.next_to(title, DOWN, buff=0.8)
        
        next_text = Text("Next: Cover Sheet Details", font_size=28, color=TITLE_COLOR)
        next_text.to_edge(DOWN, buff=1.0)
        
        # Animations
        self.play(FadeIn(title), run_time=0.8)
        elapsed += 0.8
        
        for item in checklist:
            self.play(FadeIn(item), run_time=0.5)
            elapsed += 0.5
        
        self.play(FadeIn(next_text), run_time=0.6)
        elapsed += 0.6
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"\nTo render: manim -qh chapter1/chapter1_video2.py Chapter1Video2")











