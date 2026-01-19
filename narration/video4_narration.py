#!/usr/bin/env python3
"""
Narration Script for Chapter 1, Video 4: Scales and Design Data
Pages 8-11 of Basic Highway Plan Reading

Topics covered:
- Engineer's vs architect's scale
- Bar scale
- Project length table
- Design data on the Cover Sheet
"""

NARRATIONS = {
    # ========================================================================
    # SCENE 1: Title/Introduction
    # ========================================================================
    "scene_1": """
Welcome to the final video of Chapter One. 
In this segment, we'll cover two important topics: engineering scales 
and design data. Understanding how to read scales is essential 
for accurately interpreting dimensions on highway plans. 
We'll also look at the design data that informs 
how a highway is planned and built.
""",

    # ========================================================================
    # SCENE 2: Scale Introduction
    # ========================================================================
    "scene_2": """
Roadway and structure plans are drawn to scale so that large projects 
can be represented on easy-to-use sheet sizes. Without scaling, 
a highway project spanning several miles would require 
an impossibly large piece of paper.

Highway plans primarily use two types of scales: the engineer's scale 
and the architect's scale. Roadway plans typically use the engineer's 
scale, while structure plans may use either type depending on the detail 
required. Let's look at each one.
""",

    # ========================================================================
    # SCENE 3: Engineer vs Architect Scale
    # ========================================================================
    "scene_3": """
As you can see in the image on screen, the civil engineer's scale 
is shown at the top, and the architect's scale is shown below it.

The engineer's scale expresses scale as inches to feet. 
Common scales include 1 inch equals 10 feet, 1 inch equals 20 feet, 
and so on. The scale is usually one foot long and may be triangular 
or flat in shape.

The architect's scale, also called a mechanical engineer's scale, 
expresses scale as a fraction of an inch to one foot. 
Examples include one-quarter inch equals one foot, 
or one-eighth inch equals one foot.
""",

    # ========================================================================
    # SCENE 4: Engineer's Scale Detail
    # ========================================================================
    "scene_4": """
Let's examine the civil engineer's scale more closely. 
As shown in the detail on screen, this scale has divisions 
of 10, 20, 30, 40, 50, and 60 to the inch.

In the 1 inch equals 10 feet scale, there are 10 divisions per inch, 
with each division representing one foot. These same divisions 
can be used for multiples of 10, such as 1 inch equals 100 feet 
or 1 inch equals 1000 feet.

The scales are divided into decimal parts of an inch, such as 
one-tenth inch, one-twentieth inch, and so on. This decimal system 
makes calculations straightforward when measuring plan dimensions.
""",

    # ========================================================================
    # SCENE 5: Bar Scale
    # ========================================================================
    "scene_5": """
Many plan sheets include a bar scale, which is a graphical representation 
of the scale being used. As shown on screen, this bar scale 
is from Plan Sheet 60 of our example project.

The bar scale shows the scale stated in feet, allowing you 
to measure distances directly on the drawing without needing 
a physical engineer's scale. The scale used on each sheet 
is always noted on that sheet.

An important reminder: if you're working with half-size plan sheets, 
which are common reproductions, you must double any measurements 
taken from the plans.
""",

    # ========================================================================
    # SCENE 6: Project Length Table
    # ========================================================================
    "scene_6": """
The Cover Sheet includes a Length of Project table 
that breaks down the project's extent by county.

As shown on screen, this table displays the Net Length of Roadway, 
Net Length of Bridges, Net Length of Project, Net Length of Exceptions, 
and Gross Length of Project. Each value is shown in miles, 
broken down by county.

In our example, the STP-IM project has a total gross length 
of 7.64 miles, spanning 6.76 miles in Spalding County 
and 0.88 miles in Butts County. This information helps you understand 
the overall scope and geographic distribution of the project.
""",

    # ========================================================================
    # SCENE 7: Design Data
    # ========================================================================
    "scene_7": """
Finally, let's look at the Design Data section of the Cover Sheet. 
This data is used in the design process to determine 
the number of lanes and the depth of pavement.

As displayed on screen, the design data includes several key metrics. 
The Traffic A.D.T., or Average Daily Traffic, shows both current 
and projected traffic volumes. The D.H.V., or Design Hourly Volume, 
and directional distribution are listed.

You'll also find the percentage of trucks, the design speed, 
the functional classification such as Rural Arterial, 
and the project designation. This data directly influences 
the design decisions shown throughout the plan set.
""",

    # ========================================================================
    # SCENE 8: Summary
    # ========================================================================
    "scene_8": """
Congratulations! You've completed Chapter One of Basic Highway 
Plan Reading.

In this video, you learned about engineer's and architect's scales, 
including how they differ and how to read them. You understand 
how bar scales work and the importance of adjusting for half-size plans.

You can now interpret the Project Length table to understand 
a project's scope, and you know where to find design data 
that influences highway construction.

With this foundation in place, you're ready to move on to Chapter Two, 
which covers the Index and Revision Summary Sheet. Thank you for watching.
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
    print("Video 4 Narration - Scales and Design Data")
    print("=" * 60)
    total_words = 0
    for scene_name, narration in get_all_narrations().items():
        word_count = len(narration.split())
        total_words += word_count
        print(f"\n{scene_name.upper()} ({word_count} words)")
    print(f"\nTotal: {total_words} words")
    print(f"Estimated duration: {total_words / 140 * 60:.0f}s")









