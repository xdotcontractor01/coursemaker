#!/usr/bin/env python3
"""
Extract content from markdown for Chapters 2, 3, and 4
Generate initial manifests with narration text and scene breakdowns
"""

import json
import re
from pathlib import Path

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MARKDOWN_FILE = str(PROJECT_ROOT / "test_workflow/MinerU_markdown_BasicHiwyPlanReading (1)_20251224155959_2003737404334637056.md")
MANIFESTS_DIR = PROJECT_ROOT / "manifests"

# Image URLs extracted from markdown
IMAGE_URLS = {
    # Chapter 3
    "figure_3_1": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/d2f5015ff5d016767e8142ab58273f4eb07a7e90241def8ec723c631d5000ff0.jpg",
    "figure_3_2": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/19c7a5d605babe0b6b5b50cc0cb246a03f4c04fcffc1921a77d3facbbe8e94ba.jpg",
    "figure_3_3": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/cd36c52ffd8f1f36b66985cd1c5962a6554d4cdb0e552d001e858ef16022559a.jpg",
    # Chapter 4
    "figure_4_1": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/4d6c1acad8f6624f1cbd8509f5105ae839a502fa17074fa388a39d3152885598.jpg",
    "figure_4_2": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/8319fed7bf31a55061ad5c5f3d5c760ac89f03d3ffa9cafdc00def8291d436b4.jpg",
    "figure_4_3": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/8319fed7bf31a55061ad5c5f3d5c760ac89f03d3ffa9cafdc00def8291d436b4.jpg",  # Note: Using same as 4-2 placeholder
}


def read_markdown():
    """Read the markdown file."""
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def get_chapter_2_manifest():
    """Generate manifest for Chapter 2."""
    return {
        "chapter": 2,
        "pages": "11-12",
        "title": "Index and Revision Summary Sheet",
        "scenes": [
            {
                "index": 1,
                "title": "Title",
                "source_pages": "11",
                "source_text": "Chapter 2: Index and Revision Summary Sheet",
                "image_paths": [],
                "bullets": [
                    "Index and Revision Summary",
                    "Understanding plan organization",
                    "Tracking plan changes"
                ],
                "narration_text": """Welcome to Chapter Two of Basic Highway Plan Reading. 
In this chapter, we'll explore two essential organizational elements found in construction plan sets: 
the Index and the Revision Summary Sheet. These sheets help you navigate the plan set 
and understand any changes that have been made to the plans after they were originally completed. 
Let's begin.""",
                "tts_file_path": "audio/ch02_scene01.wav",
                "expected_duration": None
            },
            {
                "index": 2,
                "title": "Index",
                "source_pages": "11",
                "source_text": "An index is required for each set of construction plans to help the user in identifying what sheets are in the set of plans.",
                "image_paths": [],
                "bullets": [
                    "Required for all plan sets",
                    "Lists all sheets with descriptions",
                    "Includes standards and drawing numbers"
                ],
                "narration_text": """Let's start with the Index. An index is required for each set of construction plans 
to help you identify what sheets are included in the plan set. 

On smaller projects with few sheets, the index may be included on the cover sheet. 
However, on most projects, the index is included as a separate sheet directly following the cover sheet.

The index sheet includes a description of each plan sheet along with its corresponding sheet number. 
As you can see on screen, this provides a clear reference of what information is contained on each sheet.

Additionally, the index includes a listing of all Georgia DOT standards and construction drawings 
that relate to the particular project. Each standard is shown with its corresponding standard number, 
the most recent revision date of that standard, and the sheet number where it appears.

An area is usually available on the sheet for later additions or deletions of sheets, 
and the total number of all sheets in the plan set is clearly shown. 
This helps you ensure you have a complete set of plans.""",
                "tts_file_path": "audio/ch02_scene02.wav",
                "expected_duration": None
            },
            {
                "index": 3,
                "title": "Revision Summary Sheet",
                "source_pages": "11-12",
                "source_text": "A Revision Summary Sheet is used for the purpose of keeping a record of those revisions.",
                "image_paths": [],
                "bullets": [
                    "Tracks all plan revisions",
                    "Shows date and sheet numbers",
                    "Required element of plan sets"
                ],
                "narration_text": """Now let's examine the Revision Summary Sheet. 

At times after the final set of plans has been drawn up, it becomes necessary to revise, 
or change, the design for a portion of the plans. A Revision Summary Sheet is used 
to keep a record of all such revisions. For this reason, a revision summary sheet 
is a required element of a set of construction plans.

The Revision Summary Sheet consists of three columns in addition to the normal project 
information found in the title blocks. The first column is for the date on which 
the revision was made. The second column lists the plan sheet number or numbers 
that were affected by the revision. And the third column contains a description 
of the revision, written in enough detail to quickly understand the nature of the change.

As shown in the example on screen, a revision entry might indicate that on December 29th, 2004, 
sheets 422 and 450 were revised, and the revision involved relocating a utility line.

The Revision Summary Sheet will typically follow directly behind the Index Sheet or the Cover Sheet, 
making it easy to locate and review any changes that have been made to the original plans. 
This tracking system is essential for ensuring everyone is working with the most current version 
of the construction plans.""",
                "tts_file_path": "audio/ch02_scene03.wav",
                "expected_duration": None
            },
            {
                "index": 4,
                "title": "Summary",
                "source_pages": "12",
                "source_text": "Summary of Chapter 2 key points",
                "image_paths": [],
                "bullets": [
                    "Index lists all plan sheets",
                    "Revision Summary tracks changes",
                    "Both are required elements"
                ],
                "narration_text": """Let's review what we've covered in this chapter.

You've learned that an index is required for each set of construction plans 
and helps you identify what sheets are included in the plan set. The index lists 
each sheet with its description and includes standards and construction drawings.

You understand that the Revision Summary Sheet is a required element that tracks 
all changes made to plans after they were originally completed. Each revision entry 
shows the date, the affected sheet numbers, and a description of the change.

These organizational tools are essential for navigating construction plans effectively 
and ensuring you're working with the most current information. 
In the next chapter, we'll explore Typical Sections.""",
                "tts_file_path": "audio/ch02_scene04.wav",
                "expected_duration": None
            }
        ],
        "total_expected_duration": 0.0
    }


def get_chapter_3_manifest():
    """Generate manifest for Chapter 3."""
    return {
        "chapter": 3,
        "pages": "13-14",
        "title": "Typical Sections",
        "scenes": [
            {
                "index": 1,
                "title": "Title",
                "source_pages": "13",
                "source_text": "Chapter 3: Typical Sections",
                "image_paths": [],
                "bullets": [
                    "Typical Sections overview",
                    "Cross-sectional roadway view",
                    "Construction dimensions guide"
                ],
                "narration_text": """Welcome to Chapter Three of Basic Highway Plan Reading. 
In this chapter, we'll learn about Typical Sections, which are essential drawings 
that show how a roadway will be constructed. These sections provide the cross-sectional view 
of the roadway with all necessary dimensions. Let's explore what typical sections show us.""",
                "tts_file_path": "audio/ch03_scene01.wav",
                "expected_duration": None
            },
            {
                "index": 2,
                "title": "Introduction to Typical Sections",
                "source_pages": "13",
                "source_text": "The typical section is a picture, with dimensions, of how the cross-sectional view of the roadway would appear after the construction is completed.",
                "image_paths": ["assets/images/chapter3/figure_3_1.jpg"],
                "bullets": [
                    "Shows cross-sectional view",
                    "Illustrates fill and cut areas",
                    "Identifies roadway elements"
                ],
                "narration_text": """Let's begin by understanding what a typical section is.

A typical section is a picture, with dimensions, showing how the cross-sectional view 
of the roadway would appear after construction is completed. A cross section shows 
what the road would look like if you cut it from side to side.

As you can see in Figure 3-1 on screen, this shows an idealized roadway typical section 
with the various elements identified. The left side of the typical section illustrates 
how the roadway is to be constructed in a fill area, where earth has been added 
to raise the road above the existing ground level.

The right side of this typical section illustrates how the roadway is to be constructed 
in a cut area, where the road will be below the existing grade, meaning earth 
has been removed to lower the road surface.

It's important to note that the right and left sides of the typical section 
are interchangeable—they simply show different construction conditions that 
may occur along the length of the project.

Looking at the typical section, you can identify key features such as travel lanes, 
shoulders, medians, ditches, and slopes. All of these elements are shown with 
their exact dimensions, allowing contractors to construct the roadway precisely 
as designed.""",
                "tts_file_path": "audio/ch03_scene02.wav",
                "expected_duration": None
            },
            {
                "index": 3,
                "title": "Required Pavement",
                "source_pages": "13",
                "source_text": "Paving requirements are also spelled out under the Normal Tangent Section.",
                "image_paths": ["assets/images/chapter3/figure_3_2.jpg"],
                "bullets": [
                    "Pavement layer details",
                    "Material specifications",
                    "Thickness requirements"
                ],
                "narration_text": """Now let's look at the paving requirements shown on typical sections.

As displayed in Figure 3-2 on screen, the paving requirements are spelled out 
under the Normal Tangent Section. This detail shows the exact composition 
and thickness of each pavement layer.

The typical section will specify the types of materials to be used, such as 
asphaltic concrete, aggregate base course, and subgrade preparation. 
Each layer is shown with its required thickness, ensuring the roadway 
is built to the proper specifications.

These pavement details are critical because they determine the structural integrity 
and longevity of the roadway. Contractors must follow these specifications exactly 
as shown on the typical section to ensure the finished road meets the design requirements 
and will perform as intended under traffic loads.

The paving schedule may vary for different sections of the roadway, such as 
tangent sections versus curved sections, so it's important to check the typical section 
that applies to the specific location you're working on.""",
                "tts_file_path": "audio/ch03_scene03.wav",
                "expected_duration": None
            },
            {
                "index": 4,
                "title": "Horizontal Distance",
                "source_pages": "14",
                "source_text": "The dimensions given for Typical Sections are Horizontal dimensions.",
                "image_paths": ["assets/images/chapter3/figure_3_3.jpg"],
                "bullets": [
                    "Dimensions are horizontal",
                    "Not measured along slopes",
                    "Level lines show true width"
                ],
                "narration_text": """An important concept to understand about typical sections 
is that the dimensions given are horizontal dimensions.

This means that the distances are not measured along the slopes of the roadway. 
For example, if the typical section shows that the distance from the profile grade 
of the left lane to the edge of the pavement is written as 24 feet, that is a horizontal distance.

However, if you were to measure along the one-quarter inch per foot slope of the pavement, 
that distance would actually be slightly longer than 24 feet. Figure 3-3 on screen 
exaggerates this difference to help you understand the distinction.

All dimensions shown by level lines on typical sections are horizontal distances. 
This is an important distinction because when contractors are staking out the roadway 
or placing materials, they need to understand that these dimensions are measured horizontally, 
not along any sloped surfaces.

This horizontal measurement system is used consistently throughout highway construction plans 
because it provides a standardized way to show dimensions that can be accurately measured 
in the field using standard surveying equipment. Explanations of slopes and their relationship 
to horizontal distances will be discussed in more detail later in this manual.""",
                "tts_file_path": "audio/ch03_scene04.wav",
                "expected_duration": None
            }
        ],
        "total_expected_duration": 0.0
    }


def get_chapter_4_manifest():
    """Generate manifest for Chapter 4."""
    return {
        "chapter": 4,
        "pages": "15-17",
        "title": "Summary & Detailed Estimate Quantities",
        "scenes": [
            {
                "index": 1,
                "title": "Title",
                "source_pages": "15",
                "source_text": "Chapter 4: Summary & Detailed Estimate Quantities",
                "image_paths": [],
                "bullets": [
                    "Summary of Quantities",
                    "Detailed Estimate overview",
                    "Construction item tracking"
                ],
                "narration_text": """Welcome to Chapter Four of Basic Highway Plan Reading. 
In this chapter, we'll explore how construction quantities are organized and presented 
in plan sets. We'll look at the Summary of Quantities, the Drainage Summary, 
and the Detailed Estimate. These sheets are essential for understanding what materials 
and work items are required for the project. Let's begin.""",
                "tts_file_path": "audio/ch04_scene01.wav",
                "expected_duration": None
            },
            {
                "index": 2,
                "title": "Summary of Quantities",
                "source_pages": "15",
                "source_text": "The Summary of Quantities Construction Plan Sheets show all the items of construction that are indicated on the Plan and Profile Sheets.",
                "image_paths": ["assets/images/chapter4/figure_4_1.jpg"],
                "bullets": [
                    "Lists all construction items",
                    "Organized by categories",
                    "Shows locations and quantities"
                ],
                "narration_text": """Let's start with the Summary of Quantities.

The Summary of Quantities Construction Plan Sheets show all the items of construction 
that are indicated on the Plan and Profile Sheets. As you can see in Figure 4-1 on screen, 
the items are normally grouped together into like categories, and then these categories 
are placed in boxes on the sheet with their representative quantities.

For example, all paving items might be grouped together, all drainage items in another group, 
and all structures in yet another group. This organization makes it easy to see at a glance 
how much of each type of work is required for the project.

The Summary of Quantities also notes the location, size, and other relevant details 
where each item is required. This allows project personnel to quickly reference 
where specific work items are needed without having to search through all the plan sheets.

There are exceptions to this format. If an item is stated to be included in the cost 
of another item, it may not be listed separately. Also, on small bridge replacement projects 
where quantities are small and pay items are very limited, the quantities may be placed 
on the Detailed Estimate only, without a separate Summary of Quantities sheet.""",
                "tts_file_path": "audio/ch04_scene02.wav",
                "expected_duration": None
            },
            {
                "index": 3,
                "title": "Drainage Summary",
                "source_pages": "15-16",
                "source_text": "A numerical drainage summary is used in most project plans.",
                "image_paths": ["assets/images/chapter4/figure_4_2.jpg"],
                "bullets": [
                    "Lists drainage structures",
                    "Consecutively numbered items",
                    "Cross-references plan sheets"
                ],
                "narration_text": """Now let's examine the Drainage Summary.

A numerical drainage summary is used in most project plans. This part of the summary 
is usually on its own sheet in a set of plans and follows after the Summary of Quantities 
Plan Sheet. As shown in Figure 4-2 on screen, storm drain pipe, drainage structures, 
culverts, and other drainage elements that are to be placed on the project are listed 
in a chart format with the quantities needed and then consecutively numbered.

Each drainage item is given a unique number that corresponds to the numbers shown 
on the Plan View Plan Sheets and the Drainage Cross Section sheets. This numbering system 
allows project personnel to easily cross-reference drainage items from one view to another.

For example, if you see Culvert Number 10 on a plan sheet, you can find detailed information 
about that culvert in the Drainage Summary, including its size, location, station number, 
and other relevant design details. This cross-referencing is essential for understanding 
the complete scope of drainage work required on the project.

The drainage summary helps contractors and inspectors ensure that all required drainage 
structures are properly installed and that the quantities match what was specified 
in the original plans.""",
                "tts_file_path": "audio/ch04_scene03.wav",
                "expected_duration": None
            },
            {
                "index": 4,
                "title": "Detailed Estimate",
                "source_pages": "16-17",
                "source_text": "The Detailed Estimate lists the required pay item numbers and the quantity for each item.",
                "image_paths": ["assets/images/chapter4/figure_4_3.jpg"],
                "bullets": [
                    "Pay item numbers listed",
                    "Quantities for each item",
                    "Used for bid proposals"
                ],
                "narration_text": """Finally, let's look at the Detailed Estimate.

If included in your plan set, the Detailed Estimate lists the required pay item numbers 
and the quantity for each item. The Office of Contracts Administration uses this sheet 
in preparing the bid proposal, making it a critical document for the contracting process.

As displayed in Figure 4-3 on screen, the Detailed Estimate plan sheet is listed 
in numerical order by the item number. The pay item number, description, and units 
are shown exactly as they appear in the Department's Pay Item Index, ensuring consistency 
across all projects.

Quantities are usually shown in whole units and rounded up, unless the item is measured 
per each, in which case the exact count is shown.

It's important to remember that these quantities are estimates. The contractor will be paid 
for the actual quantities used in the project construction, not necessarily the estimated 
quantities shown on the plans. This is why careful measurement and documentation 
during construction is so important.

If there are any items in the contract that are not to be paid for by the Department, 
they are usually listed in a separate column labeled Non-Participatory Items. 
This distinction helps contractors understand which items are included in their bid 
and which are considered part of the overall project but not separately compensated.""",
                "tts_file_path": "audio/ch04_scene04.wav",
                "expected_duration": None
            },
            {
                "index": 5,
                "title": "Summary",
                "source_pages": "17",
                "source_text": "Summary of Chapter 4 key points",
                "image_paths": [],
                "bullets": [
                    "Summary organizes by category",
                    "Drainage Summary cross-references",
                    "Detailed Estimate used for bidding"
                ],
                "narration_text": """Let's review what we've covered in this chapter.

You've learned that the Summary of Quantities shows all construction items 
from the Plan and Profile Sheets, organized into categories with representative quantities 
and locations.

You understand that the Drainage Summary is a numerical listing of all drainage structures, 
consecutively numbered for easy cross-referencing with plan sheets.

And you know that the Detailed Estimate lists pay item numbers and quantities 
in numerical order, and is used by the Office of Contracts Administration 
in preparing bid proposals.

These quantity sheets are essential for understanding the scope of work, 
preparing accurate bids, and tracking construction progress. 
In the next chapter, we'll explore different types of views used in construction plans.""",
                "tts_file_path": "audio/ch04_scene05.wav",
                "expected_duration": None
            }
        ],
        "total_expected_duration": 0.0
    }


def main():
    """Generate all manifests."""
    MANIFESTS_DIR.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Generating Manifests for Chapters 2, 3, and 4")
    print("=" * 60)
    
    # Chapter 2
    ch2 = get_chapter_2_manifest()
    with open(MANIFESTS_DIR / "chapter_02.json", 'w') as f:
        json.dump(ch2, f, indent=2)
    print(f"\n[OK] Chapter 2: {len(ch2['scenes'])} scenes")
    
    # Chapter 3
    ch3 = get_chapter_3_manifest()
    with open(MANIFESTS_DIR / "chapter_03.json", 'w') as f:
        json.dump(ch3, f, indent=2)
    print(f"[OK] Chapter 3: {len(ch3['scenes'])} scenes")
    
    # Chapter 4
    ch4 = get_chapter_4_manifest()
    with open(MANIFESTS_DIR / "chapter_04.json", 'w') as f:
        json.dump(ch4, f, indent=2)
    print(f"[OK] Chapter 4: {len(ch4['scenes'])} scenes")
    
    total_scenes = len(ch2['scenes']) + len(ch3['scenes']) + len(ch4['scenes'])
    print(f"\nTotal scenes: {total_scenes}")
    print("=" * 60)
    print("Manifests generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()







