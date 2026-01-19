#!/usr/bin/env python3
"""
Narration Script for Highway Plan Reading - Pages 5-7 Explainer Video

This module contains the scene-by-scene narration text that will be
converted to audio using OpenAI TTS.

Each narration is designed to:
- Explain the topic in detail
- Reference what is visible on screen
- Flow naturally like a human instructor
- Use calm, instructional pacing

Target: ~120-150 words per scene for natural pacing
"""

# ============================================================================
# SCENE NARRATIONS
# ============================================================================

NARRATIONS = {
    # ========================================================================
    # SCENE 1: Title/Introduction (0-5s visual, ~15s with audio)
    # ========================================================================
    "scene_1": """
Welcome to this instructional video on Basic Highway Plan Reading. 
In this segment, we'll be covering pages five through seven of the manual, 
which focus on understanding the key elements found on a highway construction 
cover sheet. By the end of this video, you'll be able to identify and interpret 
the project location sketch, the layout view, the sheet identification box, 
and engineering scales. These are fundamental skills for anyone working with 
highway construction plans. Let's get started.
""",

    # ========================================================================
    # SCENE 2: Project Location Sketch (~13s visual, ~25s with audio)
    # ========================================================================
    "scene_2": """
The first element we'll examine is the Project Location Sketch. 
As you can see on the screen, this is a small map typically found in the 
upper left corner of the cover sheet. Its purpose is to show the general 
geographical area where the construction project is located. 

The highlighted area in the image indicates the approximate limits of the project. 
This sketch gives you a quick reference to understand where the project sits 
within the county or region. It shows major roads, intersections, and landmarks 
that help orient you to the project location. Think of it as a bird's eye view 
that answers the question: where exactly is this project?
""",

    # ========================================================================
    # SCENE 3: Layout View (~12s visual, ~25s with audio)
    # ========================================================================
    "scene_3": """
Next, let's look at the Layout View, also known as the Plan View. 
This view shows the project as if you were looking down from above, 
similar to what you would see if you were flying over the construction site 
in an airplane.

The layout view is located in the center of the cover sheet, just below the title. 
As shown on screen, it displays the beginning station and the ending station 
of the project. Stations are measurement markers used to identify specific 
locations along the roadway. The green circle marks the beginning, 
and the red circle marks the end. This view helps you understand the full 
extent of the project from start to finish.
""",

    # ========================================================================
    # SCENE 4: Sheet Identification Box (~13s visual, ~30s with audio)
    # ========================================================================
    "scene_4": """
Now let's examine the Sheet Identification Box. 
Every sheet in a set of construction plans has this standardized box, 
which you'll find in the upper right corner.

As displayed in the table on screen, this box contains four key pieces 
of information. First, the state abbreviation, which in this example is 
Georgia, shown as G-A. Second, the project number, which is a unique 
identifier assigned to this specific project. Third, the sheet number, 
indicating which page you're currently viewing. And fourth, the total 
number of sheets in the complete plan set.

This identification system ensures that every sheet can be properly tracked 
and organized. In this example, we're looking at sheet one of seven hundred 
and seventy total sheets.
""",

    # ========================================================================
    # SCENE 5: Engineering Scale (~15s visual, ~30s with audio)
    # ========================================================================
    "scene_5": """
The final element we'll cover is the Engineering Scale. 
Highway plans are drawn to scale so that large projects can be represented 
on manageable sheet sizes.

As you can see in the images, engineers use specialized scales with divisions 
of ten, twenty, thirty, forty, fifty, and sixty per inch. These divisions 
allow for accurate measurements at different scales.

Common scales you'll encounter include one inch equals ten feet, 
one inch equals twenty feet, and for larger overview drawings, 
one inch equals one hundred feet or even one thousand feet. 
The scale being used is always noted on each plan sheet. 
Understanding how to read these scales is essential for accurately 
interpreting dimensions and distances shown on the plans.
""",

    # ========================================================================
    # SCENE 6: Summary/Outro (~7s visual, ~15s with audio)
    # ========================================================================
    "scene_6": """
Let's quickly recap what we've covered in this video. 
You've learned about the four key elements found on pages five through seven 
of a highway plan cover sheet: the Location Sketch, which shows the project's 
geographical area; the Layout View, which displays the project from above 
with station markers; the Sheet Identification Box, which organizes and tracks 
each page; and the Engineering Scale, which allows accurate measurements.

With this foundation, you're now ready to move on to more advanced topics 
in highway plan reading. Thank you for watching.
"""
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_narration(scene_name: str) -> str:
    """
    Get the narration text for a specific scene.
    
    Args:
        scene_name: The scene identifier (e.g., "scene_1")
    
    Returns:
        The narration text, stripped of leading/trailing whitespace
    """
    return NARRATIONS.get(scene_name, "").strip()


def get_all_narrations() -> dict:
    """
    Get all narration texts.
    
    Returns:
        Dictionary mapping scene names to narration texts
    """
    return {k: v.strip() for k, v in NARRATIONS.items()}


def get_scene_count() -> int:
    """Get the total number of scenes with narration."""
    return len(NARRATIONS)


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Narration Script - Highway Plan Reading Pages 5-7")
    print("=" * 70)
    
    total_words = 0
    for scene_name, narration in get_all_narrations().items():
        word_count = len(narration.split())
        total_words += word_count
        print(f"\n{scene_name.upper()} ({word_count} words)")
        print("-" * 40)
        print(narration[:200] + "..." if len(narration) > 200 else narration)
    
    print("\n" + "=" * 70)
    print(f"Total word count: {total_words}")
    print(f"Estimated audio duration: {total_words / 150 * 60:.0f}-{total_words / 120 * 60:.0f} seconds")
    print("=" * 70)











