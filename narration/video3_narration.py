#!/usr/bin/env python3
"""
Narration Script for Chapter 1, Video 3: Cover Sheet Details
Pages 5-8 of Basic Highway Plan Reading

Topics covered:
- Project location sketch
- Layout view
- Sheet identification box
- Plans revised vs plans completed
- Legal notes and signature boxes
"""

NARRATIONS = {
    # ========================================================================
    # SCENE 1: Title/Introduction
    # ========================================================================
    "scene_1": """
Welcome to Video 3 of Chapter One. 
In this segment, we'll continue our exploration of the Cover Sheet 
by examining several important elements in detail: the Project Location 
Sketch, the Layout View, the Sheet Identification Box, legal notes, 
signature boxes, and the Plans Revised box. 
These elements provide critical context for understanding 
the construction project.
""",

    # ========================================================================
    # SCENE 2: Project Location Sketch
    # ========================================================================
    "scene_2": """
Let's begin with the Project Location Sketch. 
As you can see in the upper left corner of the image on screen, 
this is a small map showing the general geographical area of the project.

The Location Sketch shows the approximate limits of the project 
within the county or region. It helps you quickly orient yourself 
to where the construction will take place. You'll see major roads, 
county boundaries, and other landmarks that provide geographic context.

Think of it as answering the question: Where exactly is this project located?
""",

    # ========================================================================
    # SCENE 3: Layout View
    # ========================================================================
    "scene_3": """
Now let's look at the Layout View, which appears in the center 
of the Cover Sheet, just below the project title.

The Layout View is a Plan View of the project, meaning it shows 
the project as if you were looking down from above. Imagine you're 
flying over the construction site in an airplane, looking straight down. 
That's what the Layout View represents.

This view displays the beginning station and ending station of the project. 
As highlighted on screen, these stations mark the start and end points 
of the roadway construction. Understanding stations is essential 
for locating specific points along the project.
""",

    # ========================================================================
    # SCENE 4: Sheet Identification Box
    # ========================================================================
    "scene_4": """
Now look at the upper right corner of any plan sheet 
and you'll find the Sheet Identification Box.

As shown in the table on screen, this standardized box contains 
four key pieces of information. First is the State abbreviation, 
in this case G-A for Georgia. Second is the Project Number, 
which uniquely identifies this specific project.

Third is the Sheet Number, telling you which page you're currently viewing. 
And fourth is the Total Sheets count, showing how many sheets 
are in the complete plan set. In this example, we're looking at sheet 1 
of 770 total sheets.

This identification system ensures every sheet can be properly 
tracked and organized.
""",

    # ========================================================================
    # SCENE 5: Legal Notes
    # ========================================================================
    "scene_5": """
The Cover Sheet also contains important legal notes 
regarding the Department's responsibility.

The standard disclaimer states that while the data and information 
shown on the plans are based upon field investigations 
and believed to be accurate, they are shown as information only, 
are not guaranteed, and do not bind the Department of Transportation.

This note directs bidders to specific subsections of the Specifications 
for further details. Understanding these legal notes is important 
because they define the limits of liability and the basis 
for the information presented.
""",

    # ========================================================================
    # SCENE 6: Signature Boxes
    # ========================================================================
    "scene_6": """
Cover Sheets typically include signature boxes for those responsible 
for the preparation and approval of the plans.

The approval chain usually includes spaces for the person who prepared 
the plans, the Transportation Engineer who recommended submission, 
the official who submitted the plans, the District Engineer's recommendation 
for approval, and finally, the Chief Engineer's approval.

Each signature includes a date, creating a documented record 
of the approval process. This chain of signatures establishes 
accountability and ensures proper review at each level.
""",

    # ========================================================================
    # SCENE 7: Plans Revised Box
    # ========================================================================
    "scene_7": """
The Plans Revised box is another important element on the Cover Sheet. 
This box tracks the history of revisions made to the plans.

As shown on screen, the box includes the date when plans were completed, 
and entries for each subsequent revision. Each revision entry shows 
the date and which sheets were affected.

In our example, the plans were completed on March 1st, 2004, 
marked as final on September 10th, 2004, with one revision 
on December 29th, 2004 affecting sheets 4, 422, and 450.

This revision tracking is essential for ensuring everyone 
is working with the most current version of the plans.
""",

    # ========================================================================
    # SCENE 8: Summary
    # ========================================================================
    "scene_8": """
Let's review what we've covered in this video.

You've learned about the Location Sketch, which shows the project's 
geographic area. You understand the Layout View, which displays 
the project from above with beginning and ending stations.

You know how to read the Sheet Identification Box with its state, 
project number, sheet number, and total sheets. You're aware 
of the legal disclaimers and the signature approval chain.

And finally, you understand how the Plans Revised box tracks 
changes to the construction plans. In the next video, 
we'll explore engineering scales and design data.
"""
}


def get_narration(scene_name: str) -> str:
    """Get the narration text for a specific scene."""
    return NARRATIONS.get(scene_name, "").strip()


def get_all_narrations() -> dict:
    """Get all narration texts."""
    return {k: v.strip() for k, v in NARRATIONS.items()}


def get_scene_count() -> int:
    """Get the total number of scenes with narration."""
    return len(NARRATIONS)


if __name__ == "__main__":
    print("Video 3 Narration - Cover Sheet Details")
    print("=" * 60)
    total_words = 0
    for scene_name, narration in get_all_narrations().items():
        word_count = len(narration.split())
        total_words += word_count
        print(f"\n{scene_name.upper()} ({word_count} words)")
    print(f"\nTotal: {total_words} words")
    print(f"Estimated duration: {total_words / 140 * 60:.0f}s")









