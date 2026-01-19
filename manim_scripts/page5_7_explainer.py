#!/usr/bin/env python3
"""
Highway Plan Reading - Pages 5-7 Explainer Video
Compatible with Manim Community Edition v0.18.0+

REFINED VERSION with:
- White background for clarity
- 1080p @ 30fps high-quality output
- Consistent layout grid (title zone, content zone, image zone)
- Proper text alignment using relative positioning
- AUDIO SYNCHRONIZATION with duration-locked scenes (FIXED)

Author: AI-Generated
Date: 2024-12-24
"""

from manim import *
import requests
import wave
import os
from pathlib import Path

# ============================================================================
# MANIM CONFIGURATION (Resolution, FPS, Background)
# ============================================================================

config.pixel_width = 1920           # Full HD width
config.pixel_height = 1080          # Full HD height
config.frame_rate = 30              # Smooth 30 FPS
config.background_color = WHITE     # Pure white background (#FFFFFF)

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

# Get the project root (one level up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================

AUDIO_DIR = PROJECT_ROOT / "audio"
AUDIO_BUFFER = 0.12                 # Small buffer after audio ends (seconds)
MAX_AUDIO_DURATION = 180.0          # Warning threshold for long audio

# ============================================================================
# LAYOUT GRID CONSTANTS
# ============================================================================

TITLE_BUFF = 0.6
CONTENT_LEFT_BUFF = 1.0
IMAGE_SCALE_FACTOR = 0.55
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
# ASSET CONFIGURATION
# ============================================================================

IMAGE_URLS = {
    "figure_1_3": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/884ac0596cdd7c2b789731a8a7bdb94f9a4a495c38fd39e66c7798451e388708.jpg",
    "figure_1_4": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/64f16d468bc94be67e798fa7fe9b0f7c8b0b3708ea2a20af8049fb936bd2d196.jpg",
    "figure_1_9": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/25aa20b11bc17322942fbc4764af7c95258df8b9344efb9fe6dabc401aa15195.jpg",
    "figure_1_10": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/a76db50d8c607aa0d9ea60c66f0dc3f1c971e837b6d2559b99083f4b3a0fc7c9.jpg",
}

ASSETS_DIR = PROJECT_ROOT / "assets/images"

# ============================================================================
# AUDIO HELPER FUNCTIONS (FIXED)
# ============================================================================

def get_wav_duration_seconds(filepath: str) -> float:
    """
    Get the duration of a WAV audio file in seconds.
    Uses the wave module to read proper WAV headers.
    
    Args:
        filepath: Path to the WAV file
        
    Returns:
        Duration in seconds, or 0.0 if file doesn't exist or is invalid
    """
    try:
        with wave.open(filepath, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        print(f"[ERROR] Could not read audio file {filepath}: {e}")
        return 0.0


def get_audio_path(scene_num: int) -> str:
    """
    Get the path to the audio file for a scene.
    Checks for zero-padded filename first, then non-padded.
    
    Args:
        scene_num: Scene number (1-6)
        
    Returns:
        Path to the audio file
    """
    # Try zero-padded filename first (scene_01.wav)
    padded_path = os.path.join(str(AUDIO_DIR), f"scene_{scene_num:02d}.wav")
    if os.path.exists(padded_path):
        return padded_path
    
    # Fall back to non-padded (scene_1.wav)
    simple_path = os.path.join(str(AUDIO_DIR), f"scene_{scene_num}.wav")
    if os.path.exists(simple_path):
        return simple_path
    
    # Return padded path as default (will fail assertion if missing)
    return padded_path


def audio_exists(scene_num: int) -> bool:
    """Check if the audio file for a scene exists."""
    path = get_audio_path(scene_num)
    return os.path.exists(path)


# ============================================================================
# IMAGE HELPER FUNCTIONS
# ============================================================================

def download_images():
    """Download all required images from URLs if not already cached."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    for name, url in IMAGE_URLS.items():
        output_path = ASSETS_DIR / f"{name}.jpg"
        
        if output_path.exists():
            print(f"[OK] {name}.jpg already exists")
            continue
        
        try:
            print(f"Downloading {name}.jpg...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"[OK] Downloaded {name}.jpg")
        except Exception as e:
            print(f"[ERROR] Error downloading {name}: {e}")
            raise


def create_section_heading(text: str) -> Text:
    """Create a consistently styled section heading."""
    heading = Text(text, font_size=TITLE_FONT_SIZE, weight=BOLD, color=HEADING_COLOR)
    heading.to_edge(UP, buff=TITLE_BUFF)
    return heading


def create_bullet_list(items: list, font_size: int = BULLET_FONT_SIZE) -> VGroup:
    """Create a consistently formatted bullet list."""
    bullets = VGroup()
    for item in items:
        bullet_text = Text(f"  {item}", font_size=font_size, color=BODY_COLOR)
        bullets.add(bullet_text)
    bullets.arrange(DOWN, aligned_edge=LEFT, buff=LINE_SPACING)
    return bullets


def load_image_safe(image_name: str, scale: float = IMAGE_SCALE_FACTOR) -> Mobject:
    """Safely load an image with fallback to placeholder."""
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

class ExplainerScene(Scene):
    """
    Main scene containing all 6 subscenes for the explainer video.
    Each scene has its own audio file attached via self.add_sound().
    """
    
    def construct(self):
        """Main construction method that orchestrates all scenes."""
        
        # Download images
        download_images()
        
        # Verify audio files
        print("\n" + "=" * 60)
        print("AUDIO VERIFICATION")
        print("=" * 60)
        
        all_audio_ok = True
        for i in range(1, 7):
            audio_path = get_audio_path(i)
            exists = os.path.exists(audio_path)
            if exists:
                duration = get_wav_duration_seconds(audio_path)
                if duration > MAX_AUDIO_DURATION:
                    print(f"[WARNING] Scene {i}: {audio_path} duration {duration:.1f}s exceeds {MAX_AUDIO_DURATION}s")
                else:
                    print(f"[OK] Scene {i}: {audio_path} ({duration:.1f}s)")
            else:
                print(f"[MISSING] Scene {i}: {audio_path}")
                all_audio_ok = False
        
        if not all_audio_ok:
            print("\n[WARNING] Some audio files are missing. Run generate_audio.py first.")
        
        print("=" * 60 + "\n")
        
        # Execute scenes in sequence
        self.scene_1_title()
        self.scene_2_location_sketch()
        self.scene_3_layout_view()
        self.scene_4_sheet_identification()
        self.scene_5_scale()
        self.scene_6_summary()
    
    # ========================================================================
    # SCENE 1: Title/Intro
    # ========================================================================
    
    def scene_1_title(self):
        """Display title screen with main heading and subtitle."""
        
        # --- AUDIO SETUP ---
        scene_num = 1
        audio_path = get_audio_path(scene_num)
        assert os.path.exists(audio_path), f"Missing audio file: {audio_path}"
        
        duration = get_wav_duration_seconds(audio_path)
        self.add_sound(audio_path)
        print(f"[AUDIO] Scene {scene_num}: Attached {audio_path} ({duration:.1f}s)")
        
        # --- VISUAL ELEMENTS ---
        title = Text("Highway Plan Reading", font_size=MAIN_TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        subtitle = Text("Understanding Cover Sheet Elements", font_size=SUBTITLE_FONT_SIZE, color=BODY_COLOR)
        page_ref = Text("Pages 5-7", font_size=SUBTITLE_FONT_SIZE - 4, color=MUTED_COLOR)
        
        title_group = VGroup(title, subtitle, page_ref)
        title_group.arrange(DOWN, buff=0.4, center=True)
        title_group.move_to(ORIGIN)
        
        # --- ANIMATIONS ---
        elapsed = 0.0
        
        self.play(FadeIn(title), run_time=1.2)
        elapsed += 1.2
        
        self.play(FadeIn(subtitle), run_time=1.0)
        elapsed += 1.0
        
        self.play(FadeIn(page_ref), run_time=0.8)
        elapsed += 0.8
        
        # Wait for remaining audio duration
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(FadeOut(title_group), run_time=0.5)
    
    # ========================================================================
    # SCENE 2: Project Location Sketch
    # ========================================================================
    
    def scene_2_location_sketch(self):
        """Explain project location sketch with Figure 1-3."""
        
        # --- AUDIO SETUP ---
        scene_num = 2
        audio_path = get_audio_path(scene_num)
        assert os.path.exists(audio_path), f"Missing audio file: {audio_path}"
        
        duration = get_wav_duration_seconds(audio_path)
        self.add_sound(audio_path)
        print(f"[AUDIO] Scene {scene_num}: Attached {audio_path} ({duration:.1f}s)")
        
        elapsed = 0.0
        
        # --- VISUAL ELEMENTS ---
        heading = create_section_heading("Project Location Sketch")
        
        location_img = load_image_safe("figure_1_3", scale=0.5)
        location_img.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        location_img.shift(DOWN * 0.3)
        
        arrow = Arrow(
            start=location_img.get_top() + UP * 0.2,
            end=location_img.get_top() + UP * 1.0,
            color=ACCENT_COLOR,
            stroke_width=3
        )
        arrow_label = Text("Project Area", font_size=20, color=ACCENT_COLOR)
        arrow_label.next_to(arrow, UP, buff=0.1)
        
        bullet_items = [
            "Shows general geographical area",
            "Indicates approximate project limits",
            "Located in upper left corner of cover sheet"
        ]
        bullets = create_bullet_list(bullet_items)
        bullets.next_to(location_img, RIGHT, buff=0.8)
        bullets.align_to(location_img, UP)
        
        caption = Text("Figure 1-3: Location Sketch", font_size=18, color=MUTED_COLOR)
        caption.next_to(location_img, DOWN, buff=0.2)
        
        # --- ANIMATIONS ---
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(location_img), run_time=1.2)
        elapsed += 1.2
        
        self.play(FadeIn(caption), run_time=0.5)
        elapsed += 0.5
        
        self.play(GrowArrow(arrow), FadeIn(arrow_label), run_time=1.0)
        elapsed += 1.0
        
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT * 0.2), run_time=0.7)
            elapsed += 0.7
        
        # Wait for remaining audio duration
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)
    
    # ========================================================================
    # SCENE 3: Layout View
    # ========================================================================
    
    def scene_3_layout_view(self):
        """Explain layout view with Figure 1-4."""
        
        # --- AUDIO SETUP ---
        scene_num = 3
        audio_path = get_audio_path(scene_num)
        assert os.path.exists(audio_path), f"Missing audio file: {audio_path}"
        
        duration = get_wav_duration_seconds(audio_path)
        self.add_sound(audio_path)
        print(f"[AUDIO] Scene {scene_num}: Attached {audio_path} ({duration:.1f}s)")
        
        elapsed = 0.0
        
        # --- VISUAL ELEMENTS ---
        heading = create_section_heading("Layout View")
        
        layout_img = load_image_safe("figure_1_4", scale=0.55)
        layout_img.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        layout_img.shift(DOWN * 0.3)
        
        caption = Text("Figure 1-4: Plan View of Project", font_size=18, color=MUTED_COLOR)
        caption.next_to(layout_img, DOWN, buff=0.2)
        
        desc_title = Text("Plan view from above", font_size=BULLET_FONT_SIZE, weight=BOLD, color=BODY_COLOR)
        desc_sub = Text("(as if flying over the project)", font_size=22, color=MUTED_COLOR)
        
        bullet_items = ["Shows beginning station", "Shows ending station", "Displays project extent"]
        bullets = create_bullet_list(bullet_items)
        
        content_group = VGroup(desc_title, desc_sub, bullets)
        content_group.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        content_group.next_to(layout_img, RIGHT, buff=0.8)
        content_group.align_to(layout_img, UP)
        
        img_center = layout_img.get_center()
        circle1 = Circle(radius=0.25, color="#4CAF50", stroke_width=3)
        circle1.move_to(img_center + LEFT * 1.5)
        circle2 = Circle(radius=0.25, color=ACCENT_COLOR, stroke_width=3)
        circle2.move_to(img_center + RIGHT * 1.5)
        
        label1 = Text("Begin", font_size=16, color="#4CAF50")
        label1.next_to(circle1, DOWN, buff=0.1)
        label2 = Text("End", font_size=16, color=ACCENT_COLOR)
        label2.next_to(circle2, DOWN, buff=0.1)
        
        # --- ANIMATIONS ---
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(layout_img), FadeIn(caption), run_time=1.2)
        elapsed += 1.2
        
        self.play(Create(circle1), Create(circle2), run_time=1.0)
        elapsed += 1.0
        
        self.play(FadeIn(label1), FadeIn(label2), run_time=0.5)
        elapsed += 0.5
        
        self.play(FadeIn(content_group), run_time=1.5)
        elapsed += 1.5
        
        # Wait for remaining audio duration
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)
    
    # ========================================================================
    # SCENE 4: Sheet Identification
    # ========================================================================
    
    def scene_4_sheet_identification(self):
        """Display sheet identification box with table."""
        
        # --- AUDIO SETUP ---
        scene_num = 4
        audio_path = get_audio_path(scene_num)
        assert os.path.exists(audio_path), f"Missing audio file: {audio_path}"
        
        duration = get_wav_duration_seconds(audio_path)
        self.add_sound(audio_path)
        print(f"[AUDIO] Scene {scene_num}: Attached {audio_path} ({duration:.1f}s)")
        
        elapsed = 0.0
        
        # --- VISUAL ELEMENTS ---
        heading = create_section_heading("Sheet Identification Box")
        
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
        
        desc = Text("Located in upper right corner of every sheet", font_size=24, color=MUTED_COLOR)
        desc.next_to(table, DOWN, buff=0.5)
        
        annotations = VGroup(
            Text("State abbreviation", font_size=20, color=TITLE_COLOR),
            Text("Unique project identifier", font_size=20, color=TITLE_COLOR),
            Text("Current sheet number", font_size=20, color=TITLE_COLOR),
            Text("Total sheets in plan set", font_size=20, color=TITLE_COLOR),
        )
        annotations.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        annotations.next_to(table, RIGHT, buff=0.6)
        annotations.align_to(table, UP)
        
        # --- ANIMATIONS ---
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(Create(table), run_time=1.8)
        elapsed += 1.8
        
        self.play(FadeIn(desc), run_time=0.8)
        elapsed += 0.8
        
        for annotation in annotations:
            self.play(FadeIn(annotation, shift=LEFT * 0.2), run_time=0.6)
            elapsed += 0.6
        
        # Wait for remaining audio duration
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)
    
    # ========================================================================
    # SCENE 5: Scale
    # ========================================================================
    
    def scene_5_scale(self):
        """Explain engineering scale with Figures 1-9 and 1-10."""
        
        # --- AUDIO SETUP ---
        scene_num = 5
        audio_path = get_audio_path(scene_num)
        assert os.path.exists(audio_path), f"Missing audio file: {audio_path}"
        
        duration = get_wav_duration_seconds(audio_path)
        self.add_sound(audio_path)
        print(f"[AUDIO] Scene {scene_num}: Attached {audio_path} ({duration:.1f}s)")
        
        elapsed = 0.0
        
        # --- VISUAL ELEMENTS ---
        heading = create_section_heading("Engineering Scale")
        
        scale_img1 = load_image_safe("figure_1_9", scale=0.35)
        scale_img2 = load_image_safe("figure_1_10", scale=0.35)
        
        images = Group(scale_img1, scale_img2)
        images.arrange(DOWN, buff=0.3)
        images.to_edge(LEFT, buff=CONTENT_LEFT_BUFF)
        images.shift(DOWN * 0.3)
        
        caption1 = Text("Figure 1-9: Engineer's & Architect's Scales", font_size=16, color=MUTED_COLOR)
        caption1.next_to(scale_img1, DOWN, buff=0.1)
        caption2 = Text("Figure 1-10: Scale Detail", font_size=16, color=MUTED_COLOR)
        caption2.next_to(scale_img2, DOWN, buff=0.1)
        
        section1_title = Text("Engineer's scale divisions:", font_size=BULLET_FONT_SIZE, weight=BOLD, color=BODY_COLOR)
        section1_detail = Text("10, 20, 30, 40, 50, 60 per inch", font_size=24, color=BODY_COLOR)
        
        section2_title = Text("Common scales:", font_size=BULLET_FONT_SIZE, weight=BOLD, color=BODY_COLOR)
        scale_items = VGroup(
            Text('1" = 10 feet', font_size=24, color=BODY_COLOR),
            Text('1" = 20 feet', font_size=24, color=BODY_COLOR),
            Text('1" = 100 feet (multiples)', font_size=24, color=BODY_COLOR),
        )
        scale_items.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        
        content = VGroup(section1_title, section1_detail, section2_title, scale_items)
        content.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        content.next_to(images, RIGHT, buff=0.8)
        content.align_to(images, UP)
        
        ruler_line = Line(LEFT * 1.5, RIGHT * 1.5, color=BODY_COLOR, stroke_width=2)
        ruler_label = Text('1 inch = 10 feet on ground', font_size=20, color=HEADING_COLOR)
        ruler_group = VGroup(ruler_line, ruler_label)
        ruler_group.arrange(DOWN, buff=0.15)
        ruler_group.next_to(content, DOWN, buff=0.5)
        ruler_group.align_to(content, LEFT)
        
        # --- ANIMATIONS ---
        self.play(FadeIn(heading), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(images), run_time=1.2)
        elapsed += 1.2
        
        self.play(FadeIn(caption1), FadeIn(caption2), run_time=0.5)
        elapsed += 0.5
        
        self.play(FadeIn(section1_title), run_time=0.5)
        elapsed += 0.5
        
        self.play(FadeIn(section1_detail), run_time=0.5)
        elapsed += 0.5
        
        self.play(FadeIn(section2_title), run_time=0.5)
        elapsed += 0.5
        
        for item in scale_items:
            self.play(FadeIn(item, shift=RIGHT * 0.2), run_time=0.4)
            elapsed += 0.4
        
        self.play(FadeIn(ruler_group), run_time=0.8)
        elapsed += 0.8
        
        # Wait for remaining audio duration
        remaining = max(0, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)
    
    # ========================================================================
    # SCENE 6: Summary/Outro
    # ========================================================================
    
    def scene_6_summary(self):
        """Display recap with checkmarks."""
        
        # --- AUDIO SETUP ---
        scene_num = 6
        audio_path = get_audio_path(scene_num)
        assert os.path.exists(audio_path), f"Missing audio file: {audio_path}"
        
        duration = get_wav_duration_seconds(audio_path)
        self.add_sound(audio_path)
        print(f"[AUDIO] Scene {scene_num}: Attached {audio_path} ({duration:.1f}s)")
        
        elapsed = 0.0
        
        # --- VISUAL ELEMENTS ---
        title = Text("Key Elements Covered", font_size=TITLE_FONT_SIZE, weight=BOLD, color=TITLE_COLOR)
        title.to_edge(UP, buff=TITLE_BUFF + 0.3)
        
        items = ["Location Sketch", "Layout View", "Sheet Identification Box", "Engineering Scale"]
        
        checklist = VGroup()
        for item in items:
            checkmark = Text("[OK]", font_size=28, color=HEADING_COLOR)
            text = Text(item, font_size=BULLET_FONT_SIZE, color=BODY_COLOR)
            row = VGroup(checkmark, text).arrange(RIGHT, buff=0.4)
            checklist.add(row)
        
        checklist.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        checklist.next_to(title, DOWN, buff=0.8)
        
        thanks = Text("Thank You!", font_size=40, weight=BOLD, color=TITLE_COLOR)
        thanks.move_to(ORIGIN)
        
        # --- ANIMATIONS ---
        self.play(FadeIn(title), run_time=0.8)
        elapsed += 0.8
        
        for item in checklist:
            self.play(FadeIn(item), run_time=0.6)
            elapsed += 0.6
        
        # Wait before transitioning
        mid_wait = max(0, (duration - elapsed - 4.0) / 2)
        self.wait(mid_wait)
        elapsed += mid_wait
        
        self.play(FadeOut(title), FadeOut(checklist), run_time=0.8)
        elapsed += 0.8
        
        self.play(FadeIn(thanks), run_time=1.0)
        elapsed += 1.0
        
        # Wait for remaining audio
        remaining = max(0.5, duration - elapsed + AUDIO_BUFFER)
        self.wait(remaining)
        
        self.play(FadeOut(thanks), run_time=1.0)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Highway Plan Reading - Pages 5-7 Explainer Video")
    print("WITH AUDIO SYNCHRONIZATION (FIXED)")
    print("=" * 70)
    print(f"\nResolution: {config.pixel_width}x{config.pixel_height}")
    print(f"Frame Rate: {config.frame_rate} fps")
    print(f"Background: WHITE")
    print(f"Audio Directory: {AUDIO_DIR}")
    
    # Check audio files
    print("\nAudio Files:")
    for i in range(1, 7):
        path = get_audio_path(i)
        if os.path.exists(path):
            dur = get_wav_duration_seconds(path)
            print(f"  Scene {i}: {path} ({dur:.1f}s)")
        else:
            print(f"  Scene {i}: MISSING - {path}")
    
    print("\nTo generate audio, run:")
    print("  python generate_audio.py")
    
    print("\nTo render high-quality video with audio:")
    print("  manim -qh page5_7_explainer.py ExplainerScene")
    
    print("\nOutput will be at:")
    print("  media/videos/page5_7_explainer/1080p30/ExplainerScene.mp4")
    print("\n" + "=" * 70 + "\n")
