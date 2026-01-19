#!/usr/bin/env python3
"""
Chapter 1, Video 1: Requirements and Contract Documents
Pages 1-2 of Basic Highway Plan Reading

Topics:
- Requirements and Specifications
- Governing order of contract documents
- Errors and omissions
- Sheet order overview

Compatible with Manim Community Edition v0.18.0+
"""

from manim import *
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
VIDEO_NUM = 1
AUDIO_PREFIX = f"ch1_v{VIDEO_NUM}"
AUDIO_BUFFER = 0.12

# ============================================================================
# LAYOUT CONSTANTS (same as sample video)
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
# AUDIO HELPER FUNCTIONS
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


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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


def create_numbered_list(items: list, font_size: int = BULLET_FONT_SIZE) -> VGroup:
    """Create a numbered list."""
    numbered = VGroup()
    for i, item in enumerate(items, 1):
        item_text = Text(f"{i}. {item}", font_size=font_size, color=BODY_COLOR)
        numbered.add(item_text)
    numbered.arrange(DOWN, aligned_edge=LEFT, buff=LINE_SPACING)
    return numbered


# ============================================================================
# MAIN SCENE CLASS
# ============================================================================

class Chapter1Video1(Scene):
    """Video 1: Requirements and Contract Documents"""
    
    def construct(self):
        """Main construction method."""
        
        # Verify audio files
        print("\n" + "=" * 60)
        print(f"Chapter 1, Video {VIDEO_NUM}: Requirements and Contract Documents")
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
        self.scene_2_requirements()
        self.scene_3_governing_order()
        self.scene_4_errors_omissions()
        self.scene_5_sheet_order()
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
        title = Text("Beginning to Read Plans", font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        subtitle = Text("Requirements and Contract Documents", font_size=SUBTITLE_FONT_SIZE, color=BODY_COLOR)
        pages = Text("Pages 1-2", font_size=24, color=MUTED_COLOR)
        
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
    # SCENE 2: Requirements and Specifications
    # ========================================================================
    
    def scene_2_requirements(self):
        """Explain requirements and specifications."""
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
        heading = create_section_heading("Requirements & Specifications")
        
        contract_parts = [
            "Specifications",
            "Supplemental Specifications",
            "Plans",
            "Special Provisions",
            "Supplementary Documents"
        ]
        
        bullets = create_bullet_list(contract_parts)
        bullets.next_to(heading, DOWN, buff=0.8)
        bullets.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 0.5)
        
        key_point = Text(
            "A requirement in any part is binding as if in all parts",
            font_size=26,
            color=ACCENT_COLOR,
            weight=BOLD
        )
        key_point.next_to(bullets, DOWN, buff=0.6)
        key_point.align_to(bullets, LEFT)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        self.play(FadeIn(key_point), run_time=0.8)
        elapsed += 0.8
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 3: Governing Order
    # ========================================================================
    
    def scene_3_governing_order(self):
        """Explain the governing order of contract documents."""
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
        heading = create_section_heading("Governing Order of Documents")
        
        order_items = [
            "Special Provisions",
            "Project Plans (incl. Special Plan Details)",
            "Supplemental Specifications",
            "Standard Plans (incl. Construction Details)",
            "Standard Specifications"
        ]
        
        numbered_list = create_numbered_list(order_items, font_size=30)
        numbered_list.next_to(heading, DOWN, buff=0.8)
        numbered_list.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 0.5)
        
        # Priority indicator
        priority_high = Text("← Highest Priority", font_size=22, color=ACCENT_COLOR)
        priority_low = Text("← Lowest Priority", font_size=22, color=MUTED_COLOR)
        priority_high.next_to(numbered_list[0], RIGHT, buff=0.5)
        priority_low.next_to(numbered_list[-1], RIGHT, buff=0.5)
        
        note = Text(
            "Calculated dimensions govern over scaled dimensions",
            font_size=24,
            color=HEADING_COLOR,
            slant=ITALIC
        )
        note.next_to(numbered_list, DOWN, buff=0.6)
        note.align_to(numbered_list, LEFT)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for item in numbered_list:
            self.play(FadeIn(item, shift=RIGHT * 0.2), run_time=0.6)
            elapsed += 0.6
        
        self.play(FadeIn(priority_high), FadeIn(priority_low), run_time=0.5)
        elapsed += 0.5
        
        self.play(FadeIn(note), run_time=0.8)
        elapsed += 0.8
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 4: Errors and Omissions
    # ========================================================================
    
    def scene_4_errors_omissions(self):
        """Explain errors and omissions handling."""
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
        heading = create_section_heading("Errors and Omissions")
        
        warning = Text(
            "Do NOT take advantage of errors or omissions",
            font_size=32,
            color=ACCENT_COLOR,
            weight=BOLD
        )
        warning.next_to(heading, DOWN, buff=0.8)
        
        steps = [
            "Discover error or omission",
            "Immediately notify the Engineer",
            "Engineer makes corrections",
            "Construction proceeds as intended"
        ]
        
        step_list = VGroup()
        for i, step in enumerate(steps, 1):
            arrow = Text("→", font_size=28, color=HEADING_COLOR)
            text = Text(f"{step}", font_size=26, color=BODY_COLOR)
            row = VGroup(arrow, text).arrange(RIGHT, buff=0.3)
            step_list.add(row)
        
        step_list.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        step_list.next_to(warning, DOWN, buff=0.6)
        step_list.to_edge(LEFT, buff=CONTENT_LEFT_BUFF + 1.0)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(warning), run_time=0.8)
        elapsed += 0.8
        
        for step in step_list:
            self.play(FadeIn(step, shift=RIGHT * 0.2), run_time=0.6)
            elapsed += 0.6
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 5: Sheet Order
    # ========================================================================
    
    def scene_5_sheet_order(self):
        """Explain standard sheet order."""
        scene_num = 5
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 15.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Standard Sheet Order")
        
        # Two columns of sheets
        col1_items = [
            "01 - Cover Sheet",
            "02 - Index",
            "03 - Revision Summary",
            "04 - General Notes",
            "05 - Typical Sections",
            "06 - Summary of Quantities"
        ]
        
        col2_items = [
            "13 - Plan Drawings",
            "21 - Drainage Map",
            "22 - Drainage Profiles",
            "23 - Cross Sections",
            "24 - Utility Plans",
            "35 - Bridge Plans"
        ]
        
        col1 = VGroup()
        for item in col1_items:
            text = Text(item, font_size=24, color=BODY_COLOR)
            col1.add(text)
        col1.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        
        col2 = VGroup()
        for item in col2_items:
            text = Text(item, font_size=24, color=BODY_COLOR)
            col2.add(text)
        col2.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        
        columns = VGroup(col1, col2).arrange(RIGHT, buff=1.5, aligned_edge=UP)
        columns.next_to(heading, DOWN, buff=0.6)
        
        note = Text("(Sheet order may vary by project)", font_size=20, color=MUTED_COLOR)
        note.next_to(columns, DOWN, buff=0.4)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for item in col1:
            self.play(FadeIn(item, shift=RIGHT * 0.1), run_time=0.3)
            elapsed += 0.3
        
        for item in col2:
            self.play(FadeIn(item, shift=RIGHT * 0.1), run_time=0.3)
            elapsed += 0.3
        
        self.play(FadeIn(note), run_time=0.5)
        elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 6: Summary
    # ========================================================================
    
    def scene_6_summary(self):
        """Display summary checklist."""
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
            "All contract parts are equally binding",
            "Discrepancies resolved by governing order",
            "Report errors to Engineer immediately",
            "Sheets follow standardized sequence"
        ]
        
        checklist = VGroup()
        for item in items:
            checkmark = Text("[OK]", font_size=26, color=HEADING_COLOR)
            text = Text(item, font_size=BULLET_FONT_SIZE, color=BODY_COLOR)
            row = VGroup(checkmark, text).arrange(RIGHT, buff=0.4)
            checklist.add(row)
        
        checklist.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        checklist.next_to(title, DOWN, buff=0.8)
        
        next_text = Text("Next: The Cover Sheet", font_size=28, color=TITLE_COLOR)
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
    print(f"\nTo render: manim -qh chapter1/chapter1_video1.py Chapter1Video1")











