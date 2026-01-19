#!/usr/bin/env python3
"""
Chapter 1, Video 3: Cover Sheet Details
Pages 5-8 of Basic Highway Plan Reading

Topics:
- Project location sketch
- Layout view
- Sheet identification box
- Plans revised vs plans completed
- Legal notes and signature boxes

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
VIDEO_NUM = 3
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
    "figure_1_3": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/884ac0596cdd7c2b789731a8a7bdb94f9a4a495c38fd39e66c7798451e388708.jpg",
    "figure_1_4": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/64f16d468bc94be67e798fa7fe9b0f7c8b0b3708ea2a20af8049fb936bd2d196.jpg",
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

class Chapter1Video3(Scene):
    """Video 3: Cover Sheet Details"""
    
    def construct(self):
        """Main construction method."""
        
        # Download images
        download_images()
        
        # Verify audio files
        print("\n" + "=" * 60)
        print(f"Chapter 1, Video {VIDEO_NUM}: Cover Sheet Details")
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
        self.scene_2_location_sketch()
        self.scene_3_layout_view()
        self.scene_4_sheet_id_box()
        self.scene_5_legal_notes()
        self.scene_6_signature_boxes()
        self.scene_7_plans_revised()
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
        title = Text("Cover Sheet Details", font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        subtitle = Text("Location, Layout, and Identification", font_size=SUBTITLE_FONT_SIZE, color=BODY_COLOR)
        pages = Text("Pages 5-8", font_size=24, color=MUTED_COLOR)
        
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
    # SCENE 2: Project Location Sketch
    # ========================================================================
    
    def scene_2_location_sketch(self):
        """Explain project location sketch."""
        scene_num = 2
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 15.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Project Location Sketch")
        
        location_img = load_image_safe("figure_1_3", scale=0.5)
        location_img.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        location_img.shift(DOWN * 0.3)
        
        caption = Text("Figure 1-3: Location Sketch", font_size=18, color=MUTED_COLOR)
        caption.next_to(location_img, DOWN, buff=0.2)
        
        bullets = create_bullet_list([
            "Upper left corner of Cover Sheet",
            "Shows general geographical area",
            "Displays approximate project limits",
            "Major roads and landmarks"
        ], font_size=26)
        bullets.next_to(location_img, RIGHT, buff=0.8)
        bullets.align_to(location_img, UP)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(location_img), run_time=1.0)
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
    # SCENE 3: Layout View
    # ========================================================================
    
    def scene_3_layout_view(self):
        """Explain layout/plan view."""
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
        heading = create_section_heading("Layout View (Plan View)")
        
        layout_img = load_image_safe("figure_1_4", scale=0.5)
        layout_img.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        layout_img.shift(DOWN * 0.3)
        
        caption = Text("Figure 1-4: Plan View of Project", font_size=18, color=MUTED_COLOR)
        caption.next_to(layout_img, DOWN, buff=0.2)
        
        # Add station markers
        img_center = layout_img.get_center()
        begin_circle = Circle(radius=0.2, color=HEADING_COLOR, stroke_width=3)
        begin_circle.move_to(img_center + LEFT * 1.2)
        begin_label = Text("Begin", font_size=16, color=HEADING_COLOR)
        begin_label.next_to(begin_circle, DOWN, buff=0.1)
        
        end_circle = Circle(radius=0.2, color=ACCENT_COLOR, stroke_width=3)
        end_circle.move_to(img_center + RIGHT * 1.2)
        end_label = Text("End", font_size=16, color=ACCENT_COLOR)
        end_label.next_to(end_circle, DOWN, buff=0.1)
        
        desc = VGroup(
            Text("View from above", font_size=26, color=BODY_COLOR, weight=BOLD),
            Text("(like flying over project)", font_size=22, color=MUTED_COLOR),
            Text("Shows beginning & ending stations", font_size=24, color=BODY_COLOR),
        )
        desc.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        desc.next_to(layout_img, RIGHT, buff=0.8)
        desc.align_to(layout_img, UP)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(layout_img), FadeIn(caption), run_time=1.0)
        elapsed += 1.0
        
        self.play(Create(begin_circle), Create(end_circle), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(begin_label), FadeIn(end_label), run_time=0.5)
        elapsed += 0.5
        
        for item in desc:
            self.play(FadeIn(item), run_time=0.5)
            elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 4: Sheet Identification Box
    # ========================================================================
    
    def scene_4_sheet_id_box(self):
        """Explain sheet identification box."""
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
        heading = create_section_heading("Sheet Identification Box")
        
        # Create table
        table = Table(
            [["GA.", "STP-IM-022-1(26)", "1", "770"]],
            col_labels=[
                Text("STATE", font_size=22, color=BODY_COLOR),
                Text("PROJECT NUMBER", font_size=22, color=BODY_COLOR),
                Text("SHEET NO.", font_size=22, color=BODY_COLOR),
                Text("TOTAL SHEETS", font_size=22, color=BODY_COLOR)
            ],
            include_outer_lines=True,
            line_config={"color": BODY_COLOR, "stroke_width": 1.5},
            element_to_mobject_config={"color": BODY_COLOR}
        ).scale(0.55)
        table.next_to(heading, DOWN, buff=0.8)
        
        location_note = Text("Located in upper right corner of every sheet", font_size=24, color=MUTED_COLOR)
        location_note.next_to(table, DOWN, buff=0.5)
        
        # Annotations
        annotations = VGroup(
            Text("State abbreviation", font_size=20, color=TITLE_COLOR),
            Text("Unique project ID", font_size=20, color=TITLE_COLOR),
            Text("Current page", font_size=20, color=TITLE_COLOR),
            Text("Total in set", font_size=20, color=TITLE_COLOR),
        )
        annotations.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        annotations.next_to(table, RIGHT, buff=0.6)
        annotations.align_to(table, UP)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(Create(table), run_time=1.5)
        elapsed += 1.5
        
        self.play(FadeIn(location_note), run_time=0.5)
        elapsed += 0.5
        
        for ann in annotations:
            self.play(FadeIn(ann, shift=LEFT * 0.2), run_time=0.5)
            elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 5: Legal Notes
    # ========================================================================
    
    def scene_5_legal_notes(self):
        """Explain legal notes."""
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
        heading = create_section_heading("Legal Notes & Disclaimers")
        
        disclaimer_box = Rectangle(
            width=10, height=2.5,
            color=MUTED_COLOR,
            stroke_width=1.5
        )
        disclaimer_box.next_to(heading, DOWN, buff=0.6)
        
        disclaimer_text = Text(
            "Data shown is based on field investigations\nand believed accurate, but shown as\nINFORMATION ONLY - NOT GUARANTEED",
            font_size=22,
            color=BODY_COLOR,
            line_spacing=1.3
        )
        disclaimer_text.move_to(disclaimer_box)
        
        key_points = create_bullet_list([
            "Based on field investigations",
            "Information only, not guaranteed",
            "Does not bind DOT",
            "References spec subsections"
        ], font_size=24)
        key_points.next_to(disclaimer_box, DOWN, buff=0.5)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(Create(disclaimer_box), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(disclaimer_text), run_time=1.0)
        elapsed += 1.0
        
        for point in key_points:
            self.play(FadeIn(point, shift=RIGHT * 0.2), run_time=0.4)
            elapsed += 0.4
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 6: Signature Boxes
    # ========================================================================
    
    def scene_6_signature_boxes(self):
        """Explain signature/approval chain."""
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
        heading = create_section_heading("Signature & Approval Chain")
        
        approval_chain = [
            "Prepared By",
            "Transportation Engineer",
            "Submitted By",
            "District Engineer",
            "Chief Engineer"
        ]
        
        chain = VGroup()
        for i, item in enumerate(approval_chain):
            box = Rectangle(width=4, height=0.6, color=TITLE_COLOR, stroke_width=1.5)
            text = Text(item, font_size=22, color=BODY_COLOR)
            text.move_to(box)
            group = VGroup(box, text)
            chain.add(group)
        
        chain.arrange(DOWN, buff=0.3)
        chain.next_to(heading, DOWN, buff=0.6)
        
        # Add arrows between boxes
        arrows = VGroup()
        for i in range(len(chain) - 1):
            arrow = Arrow(
                chain[i].get_bottom(),
                chain[i+1].get_top(),
                color=HEADING_COLOR,
                stroke_width=2,
                buff=0.1
            )
            arrows.add(arrow)
        
        note = Text("Each signature includes a date", font_size=22, color=MUTED_COLOR)
        note.next_to(chain, RIGHT, buff=0.8)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        for i, item in enumerate(chain):
            self.play(FadeIn(item), run_time=0.4)
            elapsed += 0.4
            if i < len(arrows):
                self.play(GrowArrow(arrows[i]), run_time=0.3)
                elapsed += 0.3
        
        self.play(FadeIn(note), run_time=0.5)
        elapsed += 0.5
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 7: Plans Revised Box
    # ========================================================================
    
    def scene_7_plans_revised(self):
        """Explain plans revised box."""
        scene_num = 7
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 12.0
        
        elapsed = 0.0
        
        # Visual elements
        heading = create_section_heading("Plans Revised Box")
        
        # Create revision box display
        box = Rectangle(width=8, height=3, color=BODY_COLOR, stroke_width=1.5)
        box.next_to(heading, DOWN, buff=0.6)
        
        entries = VGroup(
            Text("FINAL: 9-10-2004", font_size=24, color=HEADING_COLOR, weight=BOLD),
            Text("PLANS COMPLETED: 03-01-2004", font_size=24, color=BODY_COLOR),
            Text("REVISIONS: 12-29-04", font_size=24, color=ACCENT_COLOR),
            Text("  Sheets 4, 422, & 450", font_size=22, color=MUTED_COLOR),
        )
        entries.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        entries.move_to(box)
        
        purpose = Text(
            "Tracks revision history for version control",
            font_size=24,
            color=TITLE_COLOR
        )
        purpose.next_to(box, DOWN, buff=0.5)
        
        # Animations
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(Create(box), run_time=0.8)
        elapsed += 0.8
        
        for entry in entries:
            self.play(FadeIn(entry), run_time=0.5)
            elapsed += 0.5
        
        self.play(FadeIn(purpose), run_time=0.6)
        elapsed += 0.6
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    
    # ========================================================================
    # SCENE 8: Summary
    # ========================================================================
    
    def scene_8_summary(self):
        """Display summary."""
        scene_num = 8
        audio_path = get_audio_path(scene_num)
        
        if os.path.exists(audio_path):
            duration = get_wav_duration_seconds(audio_path)
            self.add_sound(audio_path)
            print(f"[AUDIO] Scene {scene_num}: {duration:.1f}s")
        else:
            duration = 12.0
        
        elapsed = 0.0
        
        # Visual elements
        title = Text("Key Takeaways", font_size=TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        title.to_edge(UP, buff=TITLE_BUFF + 0.3)
        
        items = [
            "Location Sketch shows project area",
            "Layout View shows start/end stations",
            "Sheet ID Box on every page",
            "Legal notes define liability",
            "Signature chain documents approval",
            "Revisions box tracks changes"
        ]
        
        checklist = VGroup()
        for item in items:
            checkmark = Text("[OK]", font_size=24, color=HEADING_COLOR)
            text = Text(item, font_size=24, color=BODY_COLOR)
            row = VGroup(checkmark, text).arrange(RIGHT, buff=0.4)
            checklist.add(row)
        
        checklist.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        checklist.next_to(title, DOWN, buff=0.6)
        
        next_text = Text("Next: Scales and Design Data", font_size=28, color=TITLE_COLOR)
        next_text.to_edge(DOWN, buff=0.8)
        
        # Animations
        self.play(FadeIn(title), run_time=0.8)
        elapsed += 0.8
        
        for item in checklist:
            self.play(FadeIn(item), run_time=0.4)
            elapsed += 0.4
        
        self.play(FadeIn(next_text), run_time=0.6)
        elapsed += 0.6
        
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"\nTo render: manim -qh chapter1/chapter1_video3.py Chapter1Video3")











