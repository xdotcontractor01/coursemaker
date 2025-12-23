"""
Regenerate Chapter 1 videos with:
1. Fixed images (properly extracted)
2. Continuity between videos (intro/outro transitions)
3. Chapter-level flow
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from shared import call_llm, print_step, print_info, print_success, print_error
from pipeline.manim_script_generator import ManimScriptGenerator

# Configuration
CHAPTER_ID = "chapter_01"
FIGURES_DIR = Path("figures")
OUTPUT_DIR = Path("output/gdot_plan_videos")

# Video titles for continuity
VIDEO_TITLES = [
    "General Information & Plans Revised",
    "Requirements and Specifications & Scale",  
    "Sheet Order & Project Length",
    "Errors or Omissions",
    "Cover Sheet"
]

# Figure assignments per video (distribute figures across videos)
VIDEO_FIGURE_ASSIGNMENTS = {
    1: ["fig_1-1.png", "fig_1-2.png", "fig_1-3.png"],  # Cover sheet, project ID
    2: ["fig_1-4.png", "fig_1-5.png", "fig_1-6.png"],  # Scale figures
    3: ["fig_1-7.png", "fig_1-8.png"],  # Index, sheet order
    4: ["fig_1-9.png", "fig_1-12.png"],  # Roadway section, quantities
    5: ["fig_1-13.png", "fig_1-14.png", "fig_1-15.png", "fig_1-16.png"]  # Cover sheet details
}


def get_continuity_intro(video_num: int, total_videos: int) -> str:
    """Generate intro text for continuity"""
    if video_num == 1:
        return f"""
        # Chapter Intro
        chapter_title = Text("Chapter 1: Beginning to Read Plans", color=BLUE_D, font_size=48, weight=BOLD)
        chapter_title.move_to(ORIGIN)
        subtitle = Text("Part {video_num} of {total_videos}", color=GRAY, font_size=28)
        subtitle.next_to(chapter_title, DOWN, buff=0.5)
        
        self.play(Write(chapter_title))
        self.play(FadeIn(subtitle))
        self.wait(1)
        self.play(FadeOut(chapter_title), FadeOut(subtitle))
        """
    else:
        return f"""
        # Continuation from previous video
        continue_text = Text("Chapter 1: Beginning to Read Plans", color=BLUE_D, font_size=36, weight=BOLD)
        part_text = Text("Part {video_num} of {total_videos} - Continuing...", color=GRAY, font_size=24)
        continue_text.to_edge(UP, buff=0.3)
        part_text.next_to(continue_text, DOWN, buff=0.2)
        
        self.play(FadeIn(continue_text), FadeIn(part_text))
        self.wait(0.5)
        self.play(FadeOut(continue_text), FadeOut(part_text))
        """


def get_continuity_outro(video_num: int, total_videos: int, next_topic: str = None) -> str:
    """Generate outro text for continuity"""
    if video_num < total_videos:
        return f"""
        # Transition to next video
        self.clear()
        next_text = Text("Coming up next...", color=GRAY, font_size=28)
        next_topic_text = Text("{next_topic}", color=BLUE_D, font_size=32, weight=BOLD)
        next_group = VGroup(next_text, next_topic_text).arrange(DOWN, buff=0.4)
        next_group.move_to(ORIGIN)
        
        self.play(FadeIn(next_group))
        self.wait(1.5)
        self.play(FadeOut(next_group))
        """
    else:
        return f"""
        # Chapter conclusion
        self.clear()
        complete_text = Text("Chapter 1 Complete!", color=GREEN_D, font_size=40, weight=BOLD)
        summary_text = Text("You've learned the basics of reading highway plans", color=BLACK, font_size=24)
        complete_group = VGroup(complete_text, summary_text).arrange(DOWN, buff=0.5)
        complete_group.move_to(ORIGIN)
        
        self.play(GrowFromCenter(complete_text))
        self.play(FadeIn(summary_text))
        self.wait(2)
        """


def generate_video_script_with_continuity(video_num: int, total_videos: int = 5):
    """Generate a single video script with continuity elements"""
    
    figures_chapter_dir = FIGURES_DIR / CHAPTER_ID
    plan_path = OUTPUT_DIR / CHAPTER_ID / f"chapter_01_video_0{video_num}.plan.json"
    
    if not plan_path.exists():
        print_error(f"Plan not found: {plan_path}")
        return None
    
    plan_data = json.loads(plan_path.read_text())
    
    # Get figure paths for this video
    figure_files = VIDEO_FIGURE_ASSIGNMENTS.get(video_num, [])
    figure_paths = [str(figures_chapter_dir / f) for f in figure_files if (figures_chapter_dir / f).exists()]
    
    # Load image metadata for better LLM context
    metadata_path = figures_chapter_dir / "image_metadata.json"
    figure_metadata = {}
    if metadata_path.exists():
        figure_metadata = json.loads(metadata_path.read_text())
    
    # Generate the script
    generator = ManimScriptGenerator(OUTPUT_DIR, FIGURES_DIR)
    
    # Create enhanced slides with continuity
    next_topic = VIDEO_TITLES[video_num] if video_num < total_videos else None
    
    result = generator.generate_script(
        video_id=plan_data['video_id'],
        chapter_id=plan_data['chapter_id'],
        title=plan_data['title'],
        description=plan_data['description'] + f"\n\nThis is Part {video_num} of {total_videos} for Chapter 1.",
        slides=plan_data['slides'],
        figure_paths=figure_paths,
        source_file='chapter_01.md',
        figure_metadata=figure_metadata
    )
    
    # Inject continuity elements
    script_content = result.script_content
    
    # Find the construct method and inject intro after the first self.camera.background_color line
    intro_code = get_continuity_intro(video_num, total_videos)
    script_content = script_content.replace(
        "self.camera.background_color = WHITE",
        "self.camera.background_color = WHITE\n" + intro_code,
        1
    )
    
    # Add outro before the final wait or at the end
    outro_code = get_continuity_outro(video_num, total_videos, next_topic)
    if "self.wait(2)" in script_content:
        # Replace the last self.wait(2) with outro
        lines = script_content.rsplit("self.wait(2)", 1)
        if len(lines) == 2:
            script_content = lines[0] + outro_code + lines[1]
    else:
        # Append outro at the end
        script_content = script_content.rstrip() + "\n\n" + outro_code
    
    # Save the updated script
    script_path = OUTPUT_DIR / CHAPTER_ID / f"chapter_01_video_0{video_num}" / "base_script.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script_content)
    
    print_success(f"Video {video_num}: Generated with continuity (figures: {len(figure_paths)})")
    
    return result


def main():
    print("=" * 60)
    print("REGENERATING CHAPTER 1 VIDEOS WITH CONTINUITY")
    print("=" * 60)
    
    total_videos = 5
    
    for video_num in range(1, total_videos + 1):
        print_step(video_num, f"Generating Video {video_num}: {VIDEO_TITLES[video_num-1]}")
        result = generate_video_script_with_continuity(video_num, total_videos)
        if result:
            print_info(f"  Diversity score: {result.diversity_score}")
            print_info(f"  Uses images: {'ImageMobject' in result.script_content}")
    
    print()
    print("=" * 60)
    print("REGENERATION COMPLETE")
    print("=" * 60)
    print("Run the following to render all videos:")
    print("  manim render -ql output\\gdot_plan_videos\\chapter_01\\chapter_01_video_0X\\base_script.py")


if __name__ == "__main__":
    main()

