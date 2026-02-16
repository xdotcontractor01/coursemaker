#!/usr/bin/env python3
"""
Extract content from markdown for Chapters 5, 6, and 7
Generate manifests with sanitized narration and scene breakdowns
"""

import json
import re
from pathlib import Path

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MARKDOWN_FILE = str(PROJECT_ROOT / "docs/MinerU_markdown_BasicHiwyPlanReading (1)_20260129005532_2016555753310150656.md")
MANIFESTS_DIR = PROJECT_ROOT / "manifests"
ASSETS_DIR = PROJECT_ROOT / "assets/images"

# Ensure directories exist
MANIFESTS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

def read_markdown():
    """Read the markdown file."""
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def sanitize_narration(text: str) -> tuple[str, dict]:
    """
    Sanitize narration by replacing identifiers and long codes with readable descriptors.
    Returns (sanitized_text, sanitization_map)
    """
    sanitization_map = {}
    sanitized = text
    
    # Common words to never replace
    common_words = {
        'chapter', 'highway', 'plan', 'reading', 'construction', 'station', 'ahead', 'back',
        'figure', 'screen', 'project', 'roadway', 'centerline', 'survey', 'pavement',
        'elevation', 'section', 'profile', 'view', 'horizontal', 'vertical', 'alignment'
    }
    
    # Pattern 1: Mixed alphanumeric strings length >= 6, but exclude common words
    # Only match if it contains digits or is all uppercase (likely an identifier)
    pattern1 = r'\b([A-Z]{2,}\d+[A-Z0-9]*|\d+[A-Z]+\d*[A-Z]*|[A-Z]+\d{3,})\b'
    matches = list(re.finditer(pattern1, sanitized))
    for match in reversed(matches):  # Process in reverse to preserve positions
        original = match.group()
        original_lower = original.lower()
        
        # Skip common words
        if original_lower in common_words or len(original) < 4:
            continue
        
        # Check context for stationing
        context = sanitized[max(0, match.start()-30):match.end()+30].lower()
        if any(word in context for word in ['station', 'sta', 'stationing', 'sta.']):
            replacement = "this station number"
        elif any(word in context for word in ['curve', 'kc', 'p.i.', 'p.c.', 'p.t.']):
            replacement = "this curve identifier"
        elif any(word in context for word in ['bm', 'bench', 'mark']):
            replacement = "this bench mark"
        else:
            replacement = "this reference code"
        
        if original not in sanitization_map:
            sanitization_map[original] = {
                "sanitized": replacement,
                "reason": "alphanumeric identifier"
            }
        # Replace only this specific occurrence
        sanitized = sanitized[:match.start()] + replacement + sanitized[match.end():]
    
    # Pattern 2: Long numeric sequences length >= 5 (but not years or common numbers)
    pattern2 = r'\b(\d{5,})\b'
    matches = list(re.finditer(pattern2, sanitized))
    for match in reversed(matches):  # Process in reverse
        original = match.group()
        # Skip years (1900-2099)
        if 1900 <= int(original) <= 2099:
            continue
        
        context = sanitized[max(0, match.start()-30):match.end()+30].lower()
        if any(word in context for word in ['station', 'sta', 'stationing']):
            replacement = "the station number"
        else:
            replacement = "this number"
        
        if original not in sanitization_map:
            sanitization_map[original] = {
                "sanitized": replacement,
                "reason": "long numeric sequence"
            }
        sanitized = sanitized[:match.start()] + replacement + sanitized[match.end():]
    
    # Pattern 3: Station notation like "170+00", "138+49.42"
    pattern3 = r'\b(\d{2,}\s*\+\s*\d+(?:\.\d+)?)\b'
    matches = list(re.finditer(pattern3, sanitized))
    for match in reversed(matches):  # Process in reverse
        original = match.group()
        replacement = "this station number"
        if original not in sanitization_map:
            sanitization_map[original] = {
                "sanitized": replacement,
                "reason": "station notation format"
            }
        sanitized = sanitized[:match.start()] + replacement + sanitized[match.end():]
    
    return sanitized, sanitization_map

def extract_image_urls(text: str, chapter: int) -> dict:
    """Extract image URLs from markdown for a chapter."""
    images = {}
    # Pattern: ![](url) followed by Figure X-Y
    pattern = r'!\[\]\(([^)]+)\)\s*\n*Figure\s+(\d+)-(\d+)'
    matches = re.finditer(pattern, text)
    for match in matches:
        url = match.group(1)
        fig_chapter = int(match.group(2))
        fig_num = int(match.group(3))
        if fig_chapter == chapter:
            images[f"figure_{chapter}_{fig_num}"] = url
    return images

def get_chapter_5_manifest():
    """Generate manifest for Chapter 5 (4 pages, 1-2 videos expected)."""
    markdown = read_markdown()
    
    # Extract Chapter 5 content (from "# Chapter 5:Views" to "# Chapter 6")
    ch5_start = markdown.find("# Chapter 5:Views")
    ch6_start = markdown.find("# Chapter 6: Stationing")
    ch5_content = markdown[ch5_start:ch6_start] if ch5_start != -1 and ch6_start != -1 else ""
    
    # Extract images
    images = extract_image_urls(ch5_content, 5)
    
    # Smart split: Chapter 5 is 4 pages, relatively short, 1 video should suffice
    # But it has 6 figures, so we'll create scenes for each major concept
    
    scenes = [
        {
            "index": 1,
            "title": "Title",
            "source_pages": "19",
            "source_text": "Chapter 5: Views",
            "image_paths": [],
            "bullets": [
                "Understanding plan views",
                "Different drawing perspectives",
                "Reading construction plans"
            ],
            "narration_text": """Welcome to Chapter Five of Basic Highway Plan Reading. 
In this chapter, we'll explore the different types of views used in construction plans. 
Understanding these views is essential for reading and interpreting highway plans correctly. 
We'll cover plan views, elevations, cross sections, and profile views. 
Let's begin by understanding what these different perspectives show us.""",
            "tts_file": "audio/ch05_scene01.wav",
            "duration": None
        },
        {
            "index": 2,
            "title": "Plan View",
            "source_pages": "19",
            "source_text": "A Plan View is a view from directly above the object.",
            "image_paths": ["assets/images/chapter5/figure_5_1.jpg"] if "figure_5_1" in images else [],
            "bullets": [
                "View from directly above",
                "Shows top-down perspective",
                "Like looking from airplane"
            ],
            "narration_text": """Let's start with the Plan View. A Plan View is a view from directly above the object. 
Think of it as a top view looking down. As you can see in Figure 5-1 on screen, 
this shows what you would see if you were flying in an airplane over the project and looked down. 
The plan view shows the entire project from above, with dotted lines indicating parts that would be hidden 
from this perspective. On construction plans, the cover sheet typically shows a Plan View of the entire project, 
giving you an overview of the project's layout and location.""",
            "tts_file": "audio/ch05_scene02.wav",
            "duration": None
        },
        {
            "index": 3,
            "title": "Elevations",
            "source_pages": "19",
            "source_text": "The next set of views shows the elevation or height of the chair from the side and rear.",
            "image_paths": ["assets/images/chapter5/figure_5_2.jpg"] if "figure_5_2" in images else [],
            "bullets": [
                "Side and rear views",
                "Shows height and elevation",
                "Outside perspective"
            ],
            "narration_text": """Now let's examine Elevations. Elevations show the height or elevation of an object 
from the side, rear, front, or other angles. As shown in Figure 5-2, elevations display items from the outside, 
providing clear drawings that are almost like pictures. These views show the external appearance and dimensions 
of structures, helping you understand how they look from different angles. Elevations are essential for understanding 
the vertical aspects of construction elements.""",
            "tts_file": "audio/ch05_scene03.wav",
            "duration": None
        },
        {
            "index": 4,
            "title": "Cross Sections",
            "source_pages": "19-20",
            "source_text": "As you face the front of the chair, a section has been 'sliced' away.",
            "image_paths": ["assets/images/chapter5/figure_5_3.jpg"] if "figure_5_3" in images else [],
            "bullets": [
                "Inside view after slicing",
                "Shows internal structure",
                "Like cutting with knife"
            ],
            "narration_text": """Cross Sections are different from elevations. While elevations show the outside, 
cross sections always show an inside view - something has been sliced away to reveal how the inside part should be. 
As you can see in Figure 5-3, these slices can be made at any point, similar to cutting an apple into two parts with a knife. 
Cross sections reveal the internal structure, materials, and construction details that aren't visible from the outside. 
This is crucial for understanding how components are assembled and what materials are used internally.""",
            "tts_file": "audio/ch05_scene04.wav",
            "duration": None
        },
        {
            "index": 5,
            "title": "Profile View",
            "source_pages": "20-21",
            "source_text": "A Profile View is a lot like a longitudinal cross section of the roadway.",
            "image_paths": [
                "assets/images/chapter5/figure_5_5.jpg" if "figure_5_5" in images else None,
                "assets/images/chapter5/figure_5_6.jpg" if "figure_5_6" in images else None
            ],
            "bullets": [
                "Longitudinal cross section",
                "Shows hills and valleys",
                "Roadway centerline view"
            ],
            "narration_text": """A Profile View is similar to a longitudinal cross section of the roadway. 
Rather than showing left to right width, the profile view shows the hills and valleys of the roadway 
running along the centerline of the road. It's how the road would look if you were actually riding 
on the surface of the road. As shown in Figures 5-5 and 5-6, profile views use section lines labeled 
with letters like A-A, B-B, and C-C to indicate where the section is taken. The arrows on the ends 
of these lines show which direction you're looking when viewing the section. Profile views are essential 
for understanding vertical alignment, which we'll discuss in more detail in Chapter Seven.""",
            "tts_file": "audio/ch05_scene05.wav",
            "duration": None
        },
        {
            "index": 6,
            "title": "Summary",
            "source_pages": "21",
            "source_text": "Summary of Chapter 5 key points",
            "image_paths": [],
            "bullets": [
                "Plan view shows top-down",
                "Elevations show outside",
                "Cross sections show inside"
            ],
            "narration_text": """Let's review what we've covered in this chapter.
            
You've learned that a Plan View shows the project from directly above, like looking down from an airplane. 
Elevations show items from the outside, providing clear external views. Cross sections show inside views 
after something has been sliced away, revealing internal structure and materials. Profile views show 
the longitudinal cross section along the roadway centerline, displaying hills and valleys.
            
Understanding these different views is essential for reading construction plans effectively. 
Each view provides different information that, when combined, gives you a complete understanding 
of the project. In the next chapter, we'll explore stationing, symbols, and abbreviations.""",
            "tts_file": "audio/ch05_scene06.wav",
            "duration": None
        }
    ]
    
    # Sanitize narration for all scenes
    sanitization_map_all = {}
    for scene in scenes:
        sanitized, map_part = sanitize_narration(scene["narration_text"])
        scene["narration_sanitized"] = sanitized
        scene["narration_raw"] = scene["narration_text"]  # Keep original
        sanitization_map_all.update(map_part)
    
    return {
        "chapter": 5,
        "pages": "19-21",
        "title": "Views",
        "videos": 1,  # Single video for 4 pages
        "scenes": scenes,
        "images": images,
        "sanitization_map": sanitization_map_all
    }

def get_chapter_6_manifest():
    """Generate manifest for Chapter 6 (14 pages, 4-6 videos expected)."""
    markdown = read_markdown()
    
    # Extract Chapter 6 content
    ch6_start = markdown.find("# Chapter 6: Stationing, Symbols and Abbreviations")
    ch7_start = markdown.find("# Chapter 7: Plan and Profile Sheets")
    ch6_content = markdown[ch6_start:ch7_start] if ch6_start != -1 and ch7_start != -1 else ""
    
    # Extract images
    images = extract_image_urls(ch6_content, 6)
    
    # Smart split: Chapter 6 is 14 pages with many subheadings
    # Split into 2 videos: Video 1 (Stationing), Video 2 (Symbols and Abbreviations)
    
    scenes = [
        # Video 1: Stationing
        {
            "index": 1,
            "title": "Title - Stationing",
            "source_pages": "23",
            "source_text": "Chapter 6: Stationing, Symbols and Abbreviations - Stationing",
            "image_paths": [],
            "bullets": [
                "Understanding stationing",
                "Measuring along survey line",
                "Fundamental to highway plans"
            ],
            "narration_text": """Welcome to Chapter Six of Basic Highway Plan Reading. 
This chapter covers two essential topics: Stationing, and Symbols and Abbreviations. 
We'll start with Stationing, which is fundamental to highway plans. 
Stationing is the system used to measure distances and identify points along a project. 
Let's begin by understanding what stations are and how they work.""",
            "tts_file": "audio/ch06_scene01.wav",
            "duration": None
        },
        {
            "index": 2,
            "title": "What is Stationing?",
            "source_pages": "23",
            "source_text": "A station is the horizontal measurement along the Construction Survey Line of a project.",
            "image_paths": ["assets/images/chapter6/figure_6_1.jpg"] if "figure_6_1" in images else [],
            "bullets": [
                "One station equals 100 feet",
                "Horizontal measurement",
                "Along construction survey line"
            ],
            "narration_text": """Stationing is the horizontal measurement along the Construction Survey Line of a project. 
Distances are measured and points are identified on plans with reference to station numbers. 
One hundred feet is equivalent to one station. Think of highway stationing like a rope with knots at 100-foot intervals. 
The beginning would be Station 0, the first knot at 100 feet would be Station Number 1, written as one plus zero zero. 
The second station would be Station 2, which is 200 feet from the beginning, written as two plus zero zero, and so on. 
As you can see in Figure 6-1, this system provides a consistent way to locate any point along the project.""",
            "tts_file": "audio/ch06_scene02.wav",
            "duration": None
        },
        {
            "index": 3,
            "title": "Half Stations",
            "source_pages": "23-24",
            "source_text": "A half station is 50 feet and is located halfway between stations.",
            "image_paths": ["assets/images/chapter6/figure_6_2.jpg"] if "figure_6_2" in images else [],
            "bullets": [
                "Half station equals 50 feet",
                "Written as plus 50",
                "Located between stations"
            ],
            "narration_text": """A half station is 50 feet and is located halfway between stations. 
It is written as plus 50 after the station number. For example, halfway between Station 1 and Station 2 
would be Station 1 plus 50. As shown in Figure 6-2, any point between two stations is shown in this same manner. 
For instance, two feet forward of Station 500 would be written as Station 500 plus 02. 
Numbers less than 10 are indicated as 01, 02, 03, and so on. Ninety-nine feet ahead of Station 500 
would be written as Station 500 plus 99. Of course, 100 feet ahead of Station 500 is Station 501 plus 00.""",
            "tts_file": "audio/ch06_scene03.wav",
            "duration": None
        },
        {
            "index": 4,
            "title": "Station Notation on Plans",
            "source_pages": "24-25",
            "source_text": "On the Plan Sheets, the Station Numbers are usually written along the Construction Centerline.",
            "image_paths": ["assets/images/chapter6/figure_6_3.jpg"] if "figure_6_3" in images else [],
            "bullets": [
                "Written along centerline",
                "AHEAD means increasing",
                "BACK means decreasing"
            ],
            "narration_text": """On plan sheets, station numbers are usually written along the Construction Centerline. 
Stationing is sometimes along a baseline, or along one lane of a multiple lane highway. 
On a project, AHEAD means in the direction in which station numbers increase, usually toward the end of a project. 
BACK means in the direction in which station numbers decrease, usually towards the beginning of the project. 
Ahead is sometimes abbreviated FWD for forward, and back is abbreviated BK. 
As you can see in Figure 6-3, stationing on a plan sheet shows these relationships clearly, 
helping you understand the direction and location of points along the project.""",
            "tts_file": "audio/ch06_scene04.wav",
            "duration": None
        },
        {
            "index": 5,
            "title": "Station Equations",
            "source_pages": "25-26",
            "source_text": "Sometimes it is necessary to relate a system of stationing to another system.",
            "image_paths": ["assets/images/chapter6/figure_6_4.jpg"] if "figure_6_4" in images else [],
            "bullets": [
                "Relate two station systems",
                "Account for alignment changes",
                "Written as equality"
            ],
            "narration_text": """Sometimes it is necessary to relate a system of stationing to another system, 
such as when connecting two projects or accounting for an increase or decrease in the project's length 
due to a change in horizontal alignment. Station equations, also called station equalities, are written 
to describe a point on the Construction Centerline where the station numbers of one system change 
to the station numbers of another system. As shown in Figure 6-4, an equality might read: 
Station 138 plus 49.42 BACK equals Station 114 plus 11.00 AHEAD. 
The first number is the stationing that is ending, and the next number is the beginning station number 
of the new system. This ensures continuity when projects are connected or when alignment changes occur.""",
            "tts_file": "audio/ch06_scene05.wav",
            "duration": None
        },
        {
            "index": 6,
            "title": "Determining Project Length",
            "source_pages": "26-27",
            "source_text": "If there are NO STATION EQUALITIES on the project, you can subtract the beginning station from the ending station.",
            "image_paths": [],
            "bullets": [
                "Subtract beginning from ending",
                "Multiply by 100 for feet",
                "Divide by 5280 for miles"
            ],
            "narration_text": """If there are no station equalities on the project, you can determine the project length 
by subtracting the beginning station from the ending station and multiplying by 100, since each station equals 100 feet. 
For example, if a project begins at Station 409 plus 69 and ends at Station 701 plus 50, 
the length would be 291 plus 81, or 29,181 feet. To convert to miles, divide by 5,280 feet per mile. 
In this case, 29,181 divided by 5,280 equals approximately 5.5 miles. 
Remember that this calculation only works if no station equalities occur between the beginning and end of the project.""",
            "tts_file": "audio/ch06_scene06.wav",
            "duration": None
        },
        # Video 2: Symbols and Abbreviations
        {
            "index": 7,
            "title": "Introduction to Symbols",
            "source_pages": "28",
            "source_text": "A legend of symbols and abbreviations is not included in the plans.",
            "image_paths": ["assets/images/chapter6/figure_6_6.jpg"] if "figure_6_6" in images else [],
            "bullets": [
                "No legend in plans",
                "Common symbols used",
                "Standard abbreviations"
            ],
            "narration_text": """Now let's move on to Symbols and Abbreviations. 
A legend of symbols and abbreviations is not included in the plans. However, certain symbols 
and abbreviations are common to a set of highway plans. As you can see in Figure 6-6, 
these symbols represent various features like right-of-way markers, property lines, and other elements. 
You should become familiar with the standard symbols used by the Georgia Department of Transportation, 
which are defined in the Department's Manual of Guidance.""",
            "tts_file": "audio/ch06_scene07.wav",
            "duration": None
        },
        {
            "index": 8,
            "title": "Conventional and ROW Symbols",
            "source_pages": "28-29",
            "source_text": "State or County Line, City Limit Line, Property Line, Survey or Base Line, Right of Way Line",
            "image_paths": ["assets/images/chapter6/figure_6_7.jpg"] if "figure_6_7" in images else [],
            "bullets": [
                "Property and survey lines",
                "Right of way markers",
                "Construction limits"
            ],
            "narration_text": """Conventional symbols include state or county lines, city limit lines, property lines, 
survey or base lines, and right of way lines. As shown in Figure 6-7, right of way symbols include 
begin limit of access, end limit of access, limit of access, and various combinations. 
Construction limits are shown with C for cut and F for fill. Easements for construction and maintenance 
of slopes, both permanent and temporary, are also shown with specific symbols. 
These symbols help you quickly identify the type and purpose of various lines and markers on the plans.""",
            "tts_file": "audio/ch06_scene08.wav",
            "duration": None
        },
        {
            "index": 9,
            "title": "Utility Symbols - Water and Gas",
            "source_pages": "30-31",
            "source_text": "Water mains, non-potable water mains, gas mains, and petroleum product pipelines",
            "image_paths": [
                "assets/images/chapter6/figure_6_8.jpg" if "figure_6_8" in images else None,
                "assets/images/chapter6/figure_6_9.jpg" if "figure_6_9" in images else None
            ],
            "bullets": [
                "Water main symbols",
                "Gas main symbols",
                "Existing and proposed"
            ],
            "narration_text": """Utility symbols represent various infrastructure elements. Water mains are shown 
with specific line styles for existing, proposed, temporary, and to-be-removed conditions. 
Fire hydrants are marked W-FH, and valves are marked with W-V. Non-potable water mains use similar 
but distinct symbols. Gas mains and petroleum product pipelines are shown with G symbols, 
with variations for existing, proposed, casings, and valves. As you can see in Figures 6-8 and 6-9, 
these symbols clearly distinguish between different utility types and their conditions on the plans.""",
            "tts_file": "audio/ch06_scene09.wav",
            "duration": None
        },
        {
            "index": 10,
            "title": "Utility Symbols - Sewer and Steam",
            "source_pages": "32",
            "source_text": "Sanitary sewer and steam lines",
            "image_paths": ["assets/images/chapter6/figure_6_10.jpg"] if "figure_6_10" in images else [],
            "bullets": [
                "Sanitary sewer symbols",
                "Steam line symbols",
                "Different line styles"
            ],
            "narration_text": """Sanitary sewer lines and steam lines each have their own distinct symbols. 
As shown in Figure 6-10, these utilities use specific line patterns to indicate existing, proposed, 
temporary, and to-be-removed conditions. Understanding these symbols is essential for identifying 
all utility infrastructure that may affect or be affected by the highway construction project.""",
            "tts_file": "audio/ch06_scene10.wav",
            "duration": None
        },
        {
            "index": 11,
            "title": "Utility Symbols - Electrical and Communications",
            "source_pages": "33-35",
            "source_text": "Electrical power, telephone, telegraph, television, and microwave cables",
            "image_paths": [
                "assets/images/chapter6/figure_6_11.jpg" if "figure_6_11" in images else None,
                "assets/images/chapter6/figure_6_12.jpg" if "figure_6_12" in images else None,
                "assets/images/chapter6/figure_6_13.jpg" if "figure_6_13" in images else None
            ],
            "bullets": [
                "Electrical power symbols",
                "Telephone and telegraph",
                "TV and microwave cables"
            ],
            "narration_text": """Electrical power, telephone, telegraph, television, and microwave cables 
all have specific symbols on the plans. As shown in Figures 6-11, 6-12, and 6-13, these symbols 
distinguish between overhead and underground installations, and between existing, proposed, temporary, 
and to-be-removed conditions. For overhead wire crossings, the elevation of overhead clearances 
must be given and plotted in the profile as well. These symbols help you identify all communication 
and power infrastructure that needs to be considered during construction.""",
            "tts_file": "audio/ch06_scene11.wav",
            "duration": None
        },
        {
            "index": 12,
            "title": "Utility Abbreviations and Railroad Symbols",
            "source_pages": "35-36",
            "source_text": "Utility symbol abbreviations and railroad symbols",
            "image_paths": ["assets/images/chapter6/figure_6_14.jpg"] if "figure_6_14" in images else [],
            "bullets": [
                "Common abbreviations",
                "Railroad symbols",
                "Crossing signs and signals"
            ],
            "narration_text": """Utility symbol abbreviations include codes like PPL for Plantation Pipe Line, 
SNG for Southern Natural Gas, OC for Overhead Cable, and various codes for telephone and telegraph companies. 
Railroad symbols include railroad tracks, mileposts, crossing signs, automatic flashing signals, 
automatic gates, and draw bridges. As shown in Figure 6-14, these abbreviations and symbols provide 
a compact way to represent complex infrastructure elements on the plans. Understanding these symbols 
is essential for identifying all features that may impact the highway construction project.""",
            "tts_file": "audio/ch06_scene12.wav",
            "duration": None
        },
        {
            "index": 13,
            "title": "Summary",
            "source_pages": "36",
            "source_text": "Summary of Chapter 6 key points",
            "image_paths": [],
            "bullets": [
                "Stationing measures distance",
                "Symbols represent features",
                "Abbreviations save space"
            ],
            "narration_text": """Let's review what we've covered in this chapter.
            
You've learned that stationing is the horizontal measurement system used along the Construction Survey Line, 
with one station equaling 100 feet. You understand half stations, station notation, station equations, 
and how to determine project length.
            
You've also learned about the various symbols and abbreviations used on highway plans, including conventional symbols, 
right-of-way symbols, and utility symbols for water, gas, sewer, electrical, and communications infrastructure. 
Understanding these symbols and abbreviations is essential for reading and interpreting construction plans effectively. 
In the next chapter, we'll explore Plan and Profile Sheets.""",
            "tts_file": "audio/ch06_scene13.wav",
            "duration": None
        }
    ]
    
    # Sanitize narration for all scenes
    sanitization_map_all = {}
    for scene in scenes:
        sanitized, map_part = sanitize_narration(scene["narration_text"])
        scene["narration_sanitized"] = sanitized
        scene["narration_raw"] = scene["narration_text"]
        sanitization_map_all.update(map_part)
    
    return {
        "chapter": 6,
        "pages": "23-36",
        "title": "Stationing, Symbols and Abbreviations",
        "videos": 2,  # Split into 2 videos: Stationing (scenes 1-6) and Symbols (scenes 7-13)
        "scenes": scenes,
        "images": images,
        "sanitization_map": sanitization_map_all
    }

def get_chapter_7_manifest():
    """Generate manifest for Chapter 7 (15 pages, 5-7 videos expected)."""
    markdown = read_markdown()
    
    # Extract Chapter 7 content
    ch7_start = markdown.find("# Chapter 7: Plan and Profile Sheets")
    ch8_start = markdown.find("# Chapter 8: Drainage")
    ch7_content = markdown[ch7_start:ch8_start] if ch7_start != -1 and ch8_start != -1 else ""
    
    # Extract images
    images = extract_image_urls(ch7_content, 7)
    
    # Smart split: Chapter 7 is 15 pages with many major sections
    # Split into 3 videos: Video 1 (Plan View & Horizontal Alignment), 
    # Video 2 (Profile View & Vertical Alignment), Video 3 (Construction Elements)
    
    scenes = [
        # Video 1: Plan View & Horizontal Alignment
        {
            "index": 1,
            "title": "Title - Plan and Profile Sheets",
            "source_pages": "37",
            "source_text": "Chapter 7: Plan and Profile Sheets",
            "image_paths": [],
            "bullets": [
                "Plan and profile sheets",
                "Horizontal and vertical alignment",
                "Complete project view"
            ],
            "narration_text": """Welcome to Chapter Seven of Basic Highway Plan Reading. 
This chapter covers Plan and Profile Sheets, which are among the most important sheets in a construction plan set. 
Roadway Plan Sheets depict details of the project's horizontal alignment. They may be presented in conjunction 
with the corresponding profile on the lower half of the sheet, called a Plan/Profile Sheet, or the Profile Plan Sheets 
may be separate from the Plan Sheet. Both types give a view of the entire project, beginning with the lowest station number 
and showing the entire roadway ahead to the end of the project. Let's begin by exploring the Plan View.""",
            "tts_file": "audio/ch07_scene01.wav",
            "duration": None
        },
        {
            "index": 2,
            "title": "Plan View",
            "source_pages": "37-38",
            "source_text": "Remember that a PLAN VIEW shows the roadway as if you were flying over the project and were looking down.",
            "image_paths": ["assets/images/chapter7/figure_7_1.jpg"] if "figure_7_1" in images else [],
            "bullets": [
                "View from above",
                "Shows pavement lines",
                "Survey line orientation"
            ],
            "narration_text": """Remember that a Plan View shows the roadway as if you were flying over the project 
and looking down. As you can see in Figure 7-1, on the Plan Sheet, the pavement lines, which are the edges of the pavement, 
are shown. You can also see the Survey Line running from the left of the sheet ahead to the right of the sheet. 
Above the Construction Centerline on the Plan Sheet is considered left of the Survey Line. Below the Survey Centerline 
is considered right of the Survey Line. Either case will be as though you were standing on the Survey Line facing ahead. 
Remember throughout this course that LEFT refers to LEFT of the Construction Centerline and RIGHT refers to RIGHT 
of the Construction Centerline, relative to increasing stationing, not the left and right side of the Plan Sheet.""",
            "tts_file": "audio/ch07_scene02.wav",
            "duration": None
        },
        {
            "index": 3,
            "title": "North Arrow",
            "source_pages": "38",
            "source_text": "On all construction plans and right of way plans, there is an arrow-like symbol with the point indicating North.",
            "image_paths": ["assets/images/chapter7/figure_7_2.jpg"] if "figure_7_2" in images else [],
            "bullets": [
                "Arrow indicates north",
                "Oriented to true north",
                "Basis for directions"
            ],
            "narration_text": """On all construction plans and right of way plans, there is an arrow-like symbol 
with the point indicating North. The north arrow will be oriented on the plans to north, not necessarily to the top of the page, 
and will indicate the basis of north. As shown in Figure 7-2, a north arrow may be referenced to magnetic north 
or to the Georgia State Plane Coordinate System West Zone. The direction of all control and boundary lines 
is in reference to this North arrow. The direction of a Construction Line as you are advancing in stationing, 
as expressed by a bearing, defines the relationship between the direction of the survey line and a North line. 
It is customary to orient drawings so that the North direction is to the TOP of the plan. However, since plans 
for a complete highway project can seldom be confined to a single sheet, and must be a series of sheets, 
it is an accepted practice to make the plans so as to extend from left to right without regard to the North direction.""",
            "tts_file": "audio/ch07_scene03.wav",
            "duration": None
        },
        {
            "index": 4,
            "title": "Horizontal Alignment",
            "source_pages": "39-40",
            "source_text": "Horizontal Alignment consists of tangents and curves and is shown on the Plan View.",
            "image_paths": ["assets/images/chapter7/figure_7_3.jpg"] if "figure_7_3" in images else [],
            "bullets": [
                "Tangents and curves",
                "Point of curve and tangent",
                "Degree of curve"
            ],
            "narration_text": """Horizontal Alignment consists of tangents, which are straight sections of road, 
and curves, which are shown on the Plan View. As you can see in Figure 7-3, key terms include: 
Point on Curve, which is a point on a curved segment of roadway; Superelevation, which is elevating 
the outside edge of pavement to compensate for centrifugal force in a curved segment; Delta Angle, 
the angle that intersects between the forward and back angle; Tangent Distance, the distance measured 
from the Point of Curve or Point of Tangent to the Point of Intersection; Length of Curve, the distance 
measured along the curve from Point of Curve to Point of Tangent; and Degree of Curve, the angle to express 
how quickly a curve turns. Understanding these terms is essential for reading horizontal alignment information on plan sheets.""",
            "tts_file": "audio/ch07_scene04.wav",
            "duration": None
        },
        {
            "index": 5,
            "title": "Spiral Curves",
            "source_pages": "40-41",
            "source_text": "SPIRAL CURVES are introduced for the purpose of connecting a tangent with a circular curve.",
            "image_paths": ["assets/images/chapter7/figure_7_4.jpg"] if "figure_7_4" in images else [],
            "bullets": [
                "Transition curves",
                "Connect tangent to curve",
                "Gradual change"
            ],
            "narration_text": """Spiral Curves, also called Transition Curves, are introduced for the purpose of connecting 
a tangent with a circular curve in such a manner that the change of direction and elevation from one to the other 
takes place gradually. A spiral is a curve in which the degree of curve increases directly with the length of curve 
measured from the point where the curve leaves the tangent. The degree of curve is zero at the tangent and at the point 
at which the spiral meets the circular, it is equal to the degree of circular curve. As shown in Figure 7-4, 
significant spiral curve stations include TS, Tangent to Spiral station; SC, Spiral to Curve station; 
CS, Curve to Spiral station; and ST, Spiral to Tangent station. Spiral curves are always used in railroad work, 
but are seldom used in new construction highway work.""",
            "tts_file": "audio/ch07_scene05.wav",
            "duration": None
        },
        {
            "index": 6,
            "title": "Superelevation",
            "source_pages": "41-42",
            "source_text": "Superelevation of Curves - 'superelevate' may be defined as the rotating of the roadway CROSS SECTION.",
            "image_paths": [],
            "bullets": [
                "Rotating cross section",
                "Overcome centrifugal force",
                "Transitional runoff"
            ],
            "narration_text": """Superelevation of Curves may be defined as the rotating of the roadway cross section 
in such a manner as to overcome the centrifugal force that acts on the motor vehicle while it is traversing curved sections. 
In other words, when you are in a curve, your car tends to be thrown to the outside of the curve. 
So, in order to overcome centrifugal force, the normal roadway cross section will have to be tilted to the superelevated cross section. 
This tilting is accomplished by means of rotating the cross section about the inner edge of the pavement for divided highways 
so that the inner edge retains its normal grade but the centerline grade is varied. On two-lane pavements, 
the tilting is accomplished by means of rotating the section about the centerline axis. The distance required for accomplishing 
the transition from a normal to superelevated section is called a transitional runoff and is a function of the design speed, 
degree of curvature, and the rate of superelevation.""",
            "tts_file": "audio/ch07_scene06.wav",
            "duration": None
        },
        {
            "index": 7,
            "title": "Bearings",
            "source_pages": "42-43",
            "source_text": "A bearing is a method used to express direction.",
            "image_paths": [
                "assets/images/chapter7/figure_7_5.jpg" if "figure_7_5" in images else None,
                "assets/images/chapter7/figure_7_6.jpg" if "figure_7_6" in images else None
            ],
            "bullets": [
                "Method to express direction",
                "Referenced to north",
                "Degrees, minutes, seconds"
            ],
            "narration_text": """A bearing is a method used to express direction. Bearings are used on a set of plans 
to indicate the magnetic direction of the Construction Centerline and the magnetic direction of survey lines and property lines. 
Bearings may be referenced to true north, magnetic north, or grid north, which is the state plane grid. 
Angular measurement is referenced to a circle, and the circle can be broken into more precise measurements of minutes and seconds. 
There are 360 degrees in a full circle, 60 minutes for each degree, and 60 seconds in each minute. 
As shown in Figure 7-5, when shown as a compass circle, the circle is divided at North, East, West, and South points 
into four sections of 90 degrees each. These four 90-degree sections are called quadrants and designated Northeast, 
Northwest, Southeast, and Southwest. All bearings on the plans must be definitely described as to direction, degrees, minutes, and seconds. 
A bearing might be written as N 65 degrees 15 minutes 30 seconds E.""",
            "tts_file": "audio/ch07_scene07.wav",
            "duration": None
        },
        # Video 2: Profile View & Vertical Alignment
        {
            "index": 8,
            "title": "Profile View Introduction",
            "source_pages": "45",
            "source_text": "A profile is like a longitudinal cross section of the roadway.",
            "image_paths": ["assets/images/chapter7/figure_7_7.jpg"] if "figure_7_7" in images else [],
            "bullets": [
                "Longitudinal cross section",
                "Shows vertical alignment",
                "Profile grade line"
            ],
            "narration_text": """Now let's move on to the Profile View, also called Vertical Alignment. 
A profile is like a longitudinal cross section of the roadway; rather than the left to right width of the roadway, 
the profile shows vertical alignment along the roadway at the centerline, survey line, construction centerline, or another point. 
The cut or fill on the point shown on the profile does not necessarily mean that the cut or fill will be the same 
at this or at any other point on the cross section. For instance, the left side of the roadway might be in a cut section 
while the right side might be in a fill section. On the Profile View, a heavy dark solid line usually shows 
the proposed Profile Grade Line. It is a regular and smooth line, just as the top of the roadway will be when finished being built. 
The Original Ground Line is usually shown by a dashed line and is very irregular since the original ground is irregular before construction begins. 
As you can see in Figure 7-7, the primary purpose of the profile is to show the relationship between the proposed Profile Grade 
and the Original Ground Line.""",
            "tts_file": "audio/ch07_scene08.wav",
            "duration": None
        },
        {
            "index": 9,
            "title": "Elevations",
            "source_pages": "45-46",
            "source_text": "Elevations are given in feet above a datum.",
            "image_paths": [],
            "bullets": [
                "Feet above datum",
                "Sea level reference",
                "Bench marks shown"
            ],
            "narration_text": """Elevations are given in feet above a datum. A datum is a reference surface such as sea level. 
These numbers are shown on the right and left edge of the Profile Sheet. Looking at a Profile Sheet, 
look at the station numbers at the bottom of the page. On each side of the gridline that is drawn from the station number 
are two elevation numbers. On the left side of each line is the existing grade elevation at that station number, 
and on the right side of the line is the proposed grade elevation at that station. Note that these numbers are elevations 
in feet above sea level. The surveyors set reference points of known elevations so that they measure differences in elevations, 
which are vertical distances. Sometimes, markers will be set in trees or in structures and their elevations determined and recorded. 
These markers are called Bench Marks, shown by numbers like BM number 1, BM number 2, and so on. These Bench Marks may be listed 
on the Plan's Profile Sheets.""",
            "tts_file": "audio/ch07_scene09.wav",
            "duration": None
        },
        {
            "index": 10,
            "title": "Grade",
            "source_pages": "46-47",
            "source_text": "Grade is the slope of the roadway.",
            "image_paths": ["assets/images/chapter7/figure_7_8.jpg"] if "figure_7_8" in images else [],
            "bullets": [
                "Slope of roadway",
                "Expressed as percentage",
                "Positive or negative"
            ],
            "narration_text": """Grade is the slope of the roadway. It is expressed as a percentage of the horizontal distance. 
That is, a plus 3 percent grade means a rise of 3 feet per 100 feet of horizontal distance. 
The grade is considered to be positive or negative depending upon whether it rises or falls as you proceed along 
the Grade Line in the direction of increasing stations. As shown in Figure 7-8, a positive grade goes uphill, 
and a negative grade goes downhill. Understanding grade is essential for understanding how the roadway changes elevation 
along its length.""",
            "tts_file": "audio/ch07_scene10.wav",
            "duration": None
        },
        {
            "index": 11,
            "title": "Vertical Curves",
            "source_pages": "47-48",
            "source_text": "When a road goes over a hill or mountain, it must curve over the top, or down in a valley.",
            "image_paths": [
                "assets/images/chapter7/figure_7_9.jpg" if "figure_7_9" in images else None,
                "assets/images/chapter7/figure_7_10.jpg" if "figure_7_10" in images else None
            ],
            "bullets": [
                "Crest and sag curves",
                "Parabolic curves",
                "PVI, PVC, PVT"
            ],
            "narration_text": """When a road goes over a hill or mountain, it must curve over the top, called a crest, 
or down in a valley, called a sag. These are Vertical Curves and are shown on the Profile Sheets. 
They differ from horizontal curves in two ways: they are parabolic and not circular curves, 
and they define vertical alignment, not horizontal alignment. A small triangle at the intersection of the tangents 
shows the PVI, or Point of Vertical Intersection. These PVIs are similar to the PIs, Point of Intersection, 
for horizontal curves. As shown in Figure 7-9, the PVIs are never on the actual grade. They will be either above or below grade. 
The beginning point of the curve is the PVC, Point of Vertical Curve, and the end of the curve is the PVT, 
Point of Vertical Tangent. The length between the PVC and PVT is the length of vertical curve, or LVC. 
Almost always, the PVC to PVI and PVI to PVT is one-half of the LVC. The grade into the PVI is g1, 
and the grade out of the PVI is g2. A negative grade is downhill. As shown in Figure 7-10, the Grade Point is a point 
where the profile grade line, the proposed roadway surface, crosses the original ground line.""",
            "tts_file": "audio/ch07_scene11.wav",
            "duration": None
        },
        # Video 3: Construction Elements
        {
            "index": 12,
            "title": "Paving Limits",
            "source_pages": "49",
            "source_text": "Paving limits are the LENGTH AND WIDTH of the roadway to be paved.",
            "image_paths": [],
            "bullets": [
                "Length and width",
                "Different for tangent sections",
                "Different for superelevated"
            ],
            "narration_text": """Paving limits are the length and width of the roadway to be paved. 
On construction plan sheets, typical sections for crossroads are shown. Note that a different cross section 
is used for tangent and superelevated sections. The paving limits specify exactly where pavement will be placed, 
ensuring consistent construction across the project.""",
            "tts_file": "audio/ch07_scene12.wav",
            "duration": None
        },
        {
            "index": 13,
            "title": "Construction Limits",
            "source_pages": "50",
            "source_text": "The Construction Limits of grading represent either the toe of the fill or limits of the cut slopes.",
            "image_paths": [],
            "bullets": [
                "Toe of fill",
                "Limits of cut slopes",
                "Shown as dashed lines"
            ],
            "narration_text": """The Construction Limits of grading represent either the toe of the fill or limits of the cut slopes 
or lateral ditches, berm ditches, or surface ditches showing where the limits of the construction should be. 
These limits of grading are usually shown as dashed lines on the plans. Looking at a construction plan sheet, 
left of the survey line at a station, you will notice that the letters F are part of that dashed line. 
This indicates that in this area, the limits will be in a fill section of the terrain. At another station, 
left and right of the centerline, a dashed line is shown with the letter C. This indicates that in this area, 
the limits will be in a cut section of the terrain. It is possible to have cut on one side of the centerline 
and fill on the other.""",
            "tts_file": "audio/ch07_scene13.wav",
            "duration": None
        },
        {
            "index": 14,
            "title": "Fencing, Guard Rail, and ROW Markers",
            "source_pages": "50",
            "source_text": "Fencing, Guard Rail, and Right of Way Markers",
            "image_paths": ["assets/images/chapter7/figure_7_11.jpg"] if "figure_7_11" in images else [],
            "bullets": [
                "Fencing delineates ROW",
                "Guard rail locations",
                "ROW markers on ground"
            ],
            "narration_text": """Fencing is used to physically delineate the right of way of a controlled or limited access roadway 
or to replace fence that is along the right of way and personal property. A separate Fencing Plan may be included 
in a set of plans if the amount of fence warrants it. In most plans, fencing is pictured on the construction plans, 
as any other construction item would be, however, the quantities and locations are listed on the Quantity and Summary Sheets. 
Guard Rail locations are shown on construction plan sheets, with details for Guard Rail location under various conditions. 
The beginning, end, and type of guard rail locations are shown. Right of Way Markers are used to physically mark the limits 
of the land, property, and so on that was acquired for highway purposes on the ground. Normally right of way markers are placed 
where there is a break in the right of way such as a PC or PT. As shown in Figure 7-11, the symbols for proposed and existing 
Right of Way Markers are clearly defined. In addition to the symbol used, the locations are flagged with a station number 
and the distance from the construction centerline.""",
            "tts_file": "audio/ch07_scene14.wav",
            "duration": None
        },
        {
            "index": 15,
            "title": "Summary",
            "source_pages": "50",
            "source_text": "Summary of Chapter 7 key points",
            "image_paths": [],
            "bullets": [
                "Plan view shows horizontal",
                "Profile view shows vertical",
                "Construction elements defined"
            ],
            "narration_text": """Let's review what we've covered in this chapter.
            
You've learned that Plan and Profile Sheets are among the most important sheets in a construction plan set. 
Plan Views show the roadway from above, displaying horizontal alignment including tangents, curves, superelevation, and bearings. 
Profile Views show vertical alignment along the roadway centerline, displaying elevations, grades, and vertical curves.
            
You understand paving limits, construction limits, fencing, guard rail, and right of way markers, 
all of which are essential elements shown on plan and profile sheets. These sheets provide a complete view of the project, 
showing both horizontal and vertical alignment along with all construction elements. 
Understanding how to read these sheets is fundamental to working with highway construction plans.""",
            "tts_file": "audio/ch07_scene15.wav",
            "duration": None
        }
    ]
    
    # Sanitize narration for all scenes
    sanitization_map_all = {}
    for scene in scenes:
        sanitized, map_part = sanitize_narration(scene["narration_text"])
        scene["narration_sanitized"] = sanitized
        scene["narration_raw"] = scene["narration_text"]
        sanitization_map_all.update(map_part)
    
    return {
        "chapter": 7,
        "pages": "37-50",
        "title": "Plan and Profile Sheets",
        "videos": 3,  # Split into 3 videos: Plan View (scenes 1-7), Profile View (scenes 8-11), Construction Elements (scenes 12-15)
        "scenes": scenes,
        "images": images,
        "sanitization_map": sanitization_map_all
    }

def main():
    """Generate manifests for Chapters 5, 6, and 7."""
    print("Generating manifests for Chapters 5, 6, and 7...")
    
    # Generate manifests
    ch5_manifest = get_chapter_5_manifest()
    ch6_manifest = get_chapter_6_manifest()
    ch7_manifest = get_chapter_7_manifest()
    
    # Save manifests
    for chapter_num, manifest in [(5, ch5_manifest), (6, ch6_manifest), (7, ch7_manifest)]:
        manifest_file = MANIFESTS_DIR / f"chapter{chapter_num:02d}.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"Saved manifest: {manifest_file}")
        
        # Save sanitization map separately
        sanitization_file = MANIFESTS_DIR / f"sanitization_map_chapter{chapter_num:02d}.json"
        with open(sanitization_file, 'w', encoding='utf-8') as f:
            json.dump(manifest["sanitization_map"], f, indent=2, ensure_ascii=False)
        print(f"Saved sanitization map: {sanitization_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("SMART SPLIT SUMMARY")
    print("="*60)
    print(f"Chapter 5: Pages {ch5_manifest['pages']} -> {ch5_manifest['videos']} video(s), {len(ch5_manifest['scenes'])} scenes")
    print(f"  Reason: 4 pages, 6 figures, single cohesive topic")
    print(f"Chapter 6: Pages {ch6_manifest['pages']} -> {ch6_manifest['videos']} video(s), {len(ch6_manifest['scenes'])} scenes")
    print(f"  Reason: 14 pages, split into Stationing (scenes 1-6) and Symbols (scenes 7-13)")
    print(f"Chapter 7: Pages {ch7_manifest['pages']} -> {ch7_manifest['videos']} video(s), {len(ch7_manifest['scenes'])} scenes")
    print(f"  Reason: 15 pages, split into Plan View (scenes 1-7), Profile View (scenes 8-11), Construction Elements (scenes 12-15)")
    print("="*60)

if __name__ == "__main__":
    main()

