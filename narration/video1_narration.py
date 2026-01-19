#!/usr/bin/env python3
"""
Narration Script for Chapter 1, Video 1: Requirements and Contract Documents
Pages 1-2 of Basic Highway Plan Reading

Topics covered:
- Requirements and Specifications
- Governing order of contract documents
- Errors and omissions
- Sheet order overview
"""

NARRATIONS = {
    # ========================================================================
    # SCENE 1: Title/Introduction
    # ========================================================================
    "scene_1": """
Welcome to Chapter One of Basic Highway Plan Reading. 
In this first video, we'll cover the foundational concepts you need 
to understand before reading highway construction plans. 
We'll discuss requirements and specifications, the governing order 
of contract documents, how to handle errors and omissions, 
and the standard sheet order used in plan sets. 
Let's begin.
""",

    # ========================================================================
    # SCENE 2: Requirements and Specifications
    # ========================================================================
    "scene_2": """
First, let's discuss requirements and specifications. 
A Georgia Department of Transportation contract consists of several 
interconnected parts. These include the Specifications, 
Supplemental Specifications, Plans, Special Provisions, 
and all supplementary documents.

Here's the key point: a requirement occurring in any one of these parts 
is just as binding as if it appeared in all of them. 
This means you must carefully review every component of the contract, 
not just the plans themselves.
""",

    # ========================================================================
    # SCENE 3: Governing Order
    # ========================================================================
    "scene_3": """
Now, what happens when there's a discrepancy between different parts 
of the contract? The Georgia DOT has established a clear hierarchy 
to resolve such conflicts.

As you can see on screen, the governing order is as follows: 
First, Special Provisions take precedence over everything else. 
Second come Project Plans, including Special Plan Details. 
Third are Supplemental Specifications. 
Fourth are Standard Plans and Standard Construction Details. 
And fifth, at the lowest priority, are Standard Specifications.

Additionally, calculated dimensions will always govern over scaled dimensions. 
This hierarchy ensures that the most project-specific information 
takes precedence.
""",

    # ========================================================================
    # SCENE 4: Errors and Omissions
    # ========================================================================
    "scene_4": """
Let's talk about errors and omissions. 
As a contractor, you are not permitted to take advantage 
of any apparent error or omission in the plans or specifications.

If you discover such an error or omission, you must immediately 
notify the Engineer. The Engineer will then make the necessary 
corrections and interpretations to fulfill the intent 
of the Plans or Specifications.

This rule protects the integrity of the project and ensures 
that construction proceeds according to the original design intent, 
even when documentation contains mistakes.
""",

    # ========================================================================
    # SCENE 5: Sheet Order
    # ========================================================================
    "scene_5": """
When a set of construction plans is completed, the sheets are placed 
in a specific, standardized order. While this order may vary slightly 
for individual projects, the general sequence is consistent.

As shown on screen, the typical order begins with the Cover Sheet, 
followed by the Index, Revision Summary Sheet, and General Notes. 
Next come Typical Sections, Summary of Quantities, and various 
plan drawings. The sequence continues through Drainage, Cross Sections, 
Utility Plans, and specialized drawings like Lighting, Signing, 
and Bridge Plans.

Understanding this standard arrangement helps you quickly locate 
the information you need within a plan set.
""",

    # ========================================================================
    # SCENE 6: Summary
    # ========================================================================
    "scene_6": """
Let's recap what we've covered in this video. 
You've learned that all parts of a contract are equally binding, 
that discrepancies are resolved by a specific governing order, 
that errors must be reported to the Engineer rather than exploited, 
and that plan sheets follow a standardized sequence.

These foundational concepts will help you navigate highway 
construction plans with confidence. In the next video, 
we'll examine the Cover Sheet in detail.
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
    print("Video 1 Narration - Requirements and Contract Documents")
    print("=" * 60)
    total_words = 0
    for scene_name, narration in get_all_narrations().items():
        word_count = len(narration.split())
        total_words += word_count
        print(f"\n{scene_name.upper()} ({word_count} words)")
    print(f"\nTotal: {total_words} words")
    print(f"Estimated duration: {total_words / 140 * 60:.0f}s")









