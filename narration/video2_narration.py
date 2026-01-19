#!/usr/bin/env python3
"""
Narration Script for Chapter 1, Video 2: The Cover Sheet
Pages 2-4 of Basic Highway Plan Reading

Topics covered:
- What the Cover Sheet is
- Information contained on the Cover Sheet
- Project description and P.I. Numbers
"""

NARRATIONS = {
    # ========================================================================
    # SCENE 1: Title/Introduction
    # ========================================================================
    "scene_1": """
Welcome back to Basic Highway Plan Reading. 
In this video, we'll take a detailed look at the Cover Sheet, 
which is the front page of any set of construction plans. 
The Cover Sheet contains essential project information 
that you'll reference throughout your work. 
Let's explore what you'll find there.
""",

    # ========================================================================
    # SCENE 2: What is a Cover Sheet
    # ========================================================================
    "scene_2": """
The Cover Sheet is the first sheet in any set of highway construction plans. 
As you can see in the image on screen, it provides a comprehensive overview 
of the entire project at a glance.

Think of the Cover Sheet as the title page and summary combined. 
It contains identification information, location details, 
and key project parameters that set the context for everything 
that follows in the plan set.
""",

    # ========================================================================
    # SCENE 3: Cover Sheet Elements
    # ========================================================================
    "scene_3": """
The Cover Sheet contains numerous important elements. 
Let's walk through them as shown on screen.

You'll find the Project name, Project number, and Project Identification 
Number, also known as the P.I. Number. The County and Congressional 
district are listed, along with a standard note directing attention 
to the Georgia DOT Standard Specification Book.

Additional elements include the Project location sketch, 
a box containing revisions, and the project limits shown in large scale. 
You'll also see the Length of Project box, Federal and State Route Numbers 
when applicable, and signature boxes for those responsible for the design.

If space permits, the Cover Sheet may also include a Legend, 
a Sheet Layout Diagram, and an Index for smaller projects.
""",

    # ========================================================================
    # SCENE 4: Project Description
    # ========================================================================
    "scene_4": """
Now let's look at the Project Description in detail. 
As displayed on screen, this section tells you exactly what the project 
involves and where it's located.

In our example, the project is for construction of State Route 16 
in Spalding and Butts Counties. The description provides the geographic 
context you need to understand the project's scope and location.

The Project Identification Number, or P.I. Number, is a unique identifier 
assigned to each project. In this example, the Program Identification 
Number is 332520.
""",

    # ========================================================================
    # SCENE 5: P.I. Numbers and Project Numbers
    # ========================================================================
    "scene_5": """
Let's discuss Project Numbers in more detail. 
Some projects, like this example, may have multiple P.I. Numbers 
if they involve different funding sources or project components.

The project number for P.I. Number 332520 is STP-IM-022-1(26). 
There's also a second P.I. Number for an interstate bridge widening 
component. However, not all projects will have multiple P.I. Numbers.

Also note whether the project has a Federal Route Number, 
a State Route Number, or both. This project has only a State Route 
Number of 16. These identifiers help track and organize the project 
within the state's transportation system.
""",

    # ========================================================================
    # SCENE 6: Summary
    # ========================================================================
    "scene_6": """
To summarize, the Cover Sheet is your starting point 
for understanding any highway construction project.

You've learned that it contains project identification information, 
location details, route numbers, and references to specifications. 
You now know how to find the project description and interpret 
P.I. Numbers and Project Numbers.

In the next video, we'll explore additional Cover Sheet elements 
including the location sketch, layout view, and identification boxes.
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
    print("Video 2 Narration - The Cover Sheet")
    print("=" * 60)
    total_words = 0
    for scene_name, narration in get_all_narrations().items():
        word_count = len(narration.split())
        total_words += word_count
        print(f"\n{scene_name.upper()} ({word_count} words)")
    print(f"\nTotal: {total_words} words")
    print(f"Estimated duration: {total_words / 140 * 60:.0f}s")









