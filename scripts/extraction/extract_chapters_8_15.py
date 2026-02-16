#!/usr/bin/env python3
"""
Extract content from markdown for Chapters 8-15
Generate manifests with sanitized narration and scene breakdowns
"""

import json
import re
from pathlib import Path

# Get the project root
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MARKDOWN_FILE = PROJECT_ROOT / "test_workflow/MinerU_markdown_BasicHiwyPlanReading (1)_20251224155959_2003737404334637056.md"
MANIFESTS_DIR = PROJECT_ROOT / "manifests"
ASSETS_DIR = PROJECT_ROOT / "assets/images"

# Ensure directories exist
MANIFESTS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

def read_markdown():
    """Read the markdown file."""
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def sanitize_narration(text: str) -> tuple:
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
        'elevation', 'section', 'profile', 'view', 'horizontal', 'vertical', 'alignment',
        'drainage', 'culvert', 'bridge', 'utility', 'erosion', 'traffic', 'control'
    }
    
    # Pattern 1: Station notation like "170+00", "138+49.42"
    pattern1 = r'\b(\d{2,}\s*\+\s*\d+(?:\.\d+)?)\b'
    matches = list(re.finditer(pattern1, sanitized))
    for match in reversed(matches):
        original = match.group()
        replacement = "this station number"
        if original not in sanitization_map:
            sanitization_map[original] = {
                "sanitized": replacement,
                "reason": "station notation format"
            }
        sanitized = sanitized[:match.start()] + replacement + sanitized[match.end():]
    
    # Pattern 2: Mixed alphanumeric strings (identifiers)
    pattern2 = r'\b([A-Z]{2,}\d+[A-Z0-9]*|\d+[A-Z]+\d*[A-Z]*|[A-Z]+\d{3,})\b'
    matches = list(re.finditer(pattern2, sanitized))
    for match in reversed(matches):
        original = match.group()
        original_lower = original.lower()
        
        if original_lower in common_words or len(original) < 4:
            continue
        
        context = sanitized[max(0, match.start()-30):match.end()+30].lower()
        if any(word in context for word in ['station', 'sta', 'stationing']):
            replacement = "this station number"
        elif any(word in context for word in ['culvert', 'structure', 'pipe']):
            replacement = "this structure number"
        elif any(word in context for word in ['sheet', 'plan']):
            replacement = "this sheet number"
        else:
            replacement = "this reference code"
        
        if original not in sanitization_map:
            sanitization_map[original] = {
                "sanitized": replacement,
                "reason": "alphanumeric identifier"
            }
        sanitized = sanitized[:match.start()] + replacement + sanitized[match.end():]
    
    # Pattern 3: Long numeric sequences (5+ digits, but not years)
    pattern3 = r'\b(\d{5,})\b'
    matches = list(re.finditer(pattern3, sanitized))
    for match in reversed(matches):
        original = match.group()
        if 1900 <= int(original) <= 2099:
            continue
        
        replacement = "this number"
        if original not in sanitization_map:
            sanitization_map[original] = {
                "sanitized": replacement,
                "reason": "long numeric sequence"
            }
        sanitized = sanitized[:match.start()] + replacement + sanitized[match.end():]
    
    return sanitized, sanitization_map

def extract_image_urls(text: str, chapter: int) -> dict:
    """Extract image URLs from markdown for a chapter."""
    images = {}
    # Pattern: ![](url) followed by Figure X-Y
    pattern = r'!\[\]\(([^)]+)\)\s*\n*(?:Figure\s+)?(\d+)-(\d+)'
    matches = re.finditer(pattern, text, re.IGNORECASE)
    for match in matches:
        url = match.group(1)
        fig_chapter = int(match.group(2))
        fig_num = int(match.group(3))
        if fig_chapter == chapter:
            images[f"figure_{chapter}_{fig_num}"] = url
    return images

# ============================================================================
# CHAPTER 8: DRAINAGE (Pages 53-65, 14 figures, 3 lessons)
# ============================================================================

def get_chapter_8_manifest():
    """Generate manifest for Chapter 8: Drainage"""
    markdown = read_markdown()
    
    # Extract Chapter 8 content
    ch8_start = markdown.find("# Chapter 8: Drainage")
    ch9_start = markdown.find("# Chapter 9: Utility Plans")
    ch8_content = markdown[ch8_start:ch9_start] if ch8_start != -1 and ch9_start != -1 else ""
    
    images = extract_image_urls(ch8_content, 8)
    all_sanitization = {}
    
    # Lesson 1: Introduction and Pipe Culverts (Scenes 1-4)
    # Lesson 2: Box Culverts and Wing Walls (Scenes 5-8)
    # Lesson 3: Bridges and Utility Accommodations (Scenes 9-12)
    
    scenes = []
    scene_idx = 1
    
    # Scene 1: Title/Introduction
    narration = """Welcome to Chapter Eight of Basic Highway Plan Reading. 
This chapter covers Drainage, one of the most important aspects of highway construction. 
Project drainage is accomplished through ditches, pipe culverts, box culverts, bridges, 
and minor drainage structures such as drop inlets, junction boxes, manholes, and endwalls. 
The amount of water to be drained determines the type of drainage structure to be built. 
Let's begin by understanding the difference between culverts and bridges."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Introduction to Drainage",
        "source_pages": "53",
        "source_text": "Project drainage is accomplished by means of ditches, pipe culverts, box culverts, bridges and minor drainage structures.",
        "image_paths": [],
        "bullets": [
            "Drainage structures overview",
            "Culverts vs bridges distinction",
            "Types of drainage structures"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 2: Culverts vs Bridges
    narration = """Let's clarify the difference between culverts and bridges. 
A culvert is a structure not classified as a bridge that provides an opening under a roadway, 
usually for water drainage. According to Standard Specifications, a culvert has a clear opening 
of 20 feet or less. A bridge, on the other hand, is a structure having a length of over 20 feet 
that is erected over a roadway, stream, railroad, depression, or combination of these. 
Each drainage structure is pictured in the Plan Sheets, as shown in Figure 8-1, 
which displays a drainage table showing culvert locations, stations, sizes, and receiving streams."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Culverts vs Bridges",
        "source_pages": "53",
        "source_text": "A culvert is a structure not classified as a bridge. A bridge is a structure having a length of over 20 feet.",
        "image_paths": [f"assets/images/chapter08/figure_8_1.jpg"],
        "bullets": [
            "Culvert: 20 feet or less",
            "Bridge: over 20 feet span",
            "Drainage table on Plan Sheets"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 3: Pipe Culverts
    narration = """Now let's examine pipe culverts. Several examples of pipe culverts can be found 
on construction plan sheets. A slope drain pipe culvert may be used to drain a portion of the median 
and incorporate a median drop inlet. The pipe flows to a flared end section at the outfall. 
The drainage profiles show pipe details including elevation and flow direction. 
On the drainage map plan sheets, you'll find culvert details including station location, 
skew angle, size, drainage area, water flow rate, and the receiving stream. 
This information is critical for understanding drainage design."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Pipe Culverts",
        "source_pages": "53-54",
        "source_text": "Several examples of pipe culverts are found on Sheet 62. Look near station 192+50.",
        "image_paths": [],
        "bullets": [
            "Slope drain pipe culverts",
            "Median drop inlet integration",
            "Drainage profiles show details"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 4: Box Culvert Parts
    narration = """Box culverts have several major parts you need to know. 
As shown in Figure 8-2, a box culvert consists of three main components: 
the barrel, the wing walls, and the parapet. The barrel has a top slab, bottom slab, and barrel walls. 
A cutoff wall hangs down below the bottom slab at each end. 
The barrel walls become wing walls at each end of the barrel. 
Culverts can be built with more than one barrel, creating double or triple culverts. 
The dimensions are expressed as span by height, where span is the horizontal distance 
and height is the vertical distance."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Box Culvert Parts",
        "source_pages": "54-55",
        "source_text": "You need to know the names of the different box culvert parts.",
        "image_paths": [f"assets/images/chapter08/figure_8_2.jpg", f"assets/images/chapter08/figure_8_3.jpg"],
        "bullets": [
            "Barrel, wing walls, parapet",
            "Top slab, bottom slab, walls",
            "Span x height dimensions"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 5: Longitudinal Section
    narration = """Figure 8-4 shows a longitudinal section of a box culvert. 
Notice these important features: The inlet end where water enters is always higher than the outlet end. 
The centerline flowline, also known as the invert, is the elevation of the top of the bottom slab 
at the roadway centerline. The percent of slope for the culvert barrel is established from the inlet 
and outlet elevations. Construction joints show where one concrete pour may end and another begins. 
Understanding these elements helps you interpret drainage cross section sheets accurately."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Longitudinal Section",
        "source_pages": "56",
        "source_text": "Shown above is a longitudinal section of a box culvert.",
        "image_paths": [f"assets/images/chapter08/figure_8_4.jpg"],
        "bullets": [
            "Inlet higher than outlet",
            "Centerline flowline (invert)",
            "Construction joints shown"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 6: Plan View and Skew
    narration = """The plan view shows the culvert from the top, as seen in Figures 8-5 and 8-6. 
Notice the centerline of the roadway. The skew angle is the angle that the centerline of the culvert 
makes with the centerline of the roadway. A culvert perpendicular to the roadway is on a 90 degree skew. 
As shown in Figure 8-6, a 45 degree skew means the culvert crosses at an angle. 
The skew angle affects how the culvert is designed and constructed, 
particularly the wing wall lengths on each end."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Plan View and Skew Angles",
        "source_pages": "57",
        "source_text": "This plan view shows the culvert from the top. The SKEW ANGLE is the angle that the centerline of the culvert makes with the roadway.",
        "image_paths": [f"assets/images/chapter08/figure_8_5.jpg", f"assets/images/chapter08/figure_8_6.jpg"],
        "bullets": [
            "Plan view shows top-down",
            "Skew angle measurement",
            "90 degrees is perpendicular"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 7: Wing Walls
    narration = """Wing walls are extensions of the barrel walls that flare out away from the stream. 
As shown in Figures 8-7 and 8-8, the purpose of wing walls is to keep the earth fill above the culvert 
from spilling into the stream bed. When a culvert is built on a skew, one wing is shorter than the other. 
The wing lengths vary depending on the height of the culvert, the slope of the fill, 
and the skew angle. The wings are parallel to lines that bisect the interior corner angles 
of the culvert, which is the standard method for establishing wing direction."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Wing Walls",
        "source_pages": "58-59",
        "source_text": "Wing walls are extensions of the barrel walls that flare out away from the stream.",
        "image_paths": [f"assets/images/chapter08/figure_8_7.jpg", f"assets/images/chapter08/figure_8_8.jpg", f"assets/images/chapter08/figure_8_9.jpg"],
        "bullets": [
            "Keep fill from stream",
            "Vary with skew angle",
            "Bisect interior corners"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 8: Bridge Overview
    narration = """A bridge is constructed over a roadway, stream, or railroad, or a combination of these. 
Figure 8-11 shows plan and elevation views of a three-span bridge. The spans consist of a reinforced 
concrete deck supported on steel or concrete beams or girders. These beams are placed lengthwise 
along the bridge, parallel to the centerline, with each end resting on a bent cap. 
The superstructure is everything above the bent caps, while the substructure includes the bent caps, 
columns, footings, and piles below."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Bridge Structure Overview",
        "source_pages": "60",
        "source_text": "A bridge is constructed over a roadway, stream, or railroad. Refer to Figure 8-11 for two views of a three span bridge.",
        "image_paths": [f"assets/images/chapter08/figure_8_11.jpg"],
        "bullets": [
            "Spans, beams, and deck",
            "Superstructure above bent caps",
            "Substructure below bent caps"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 9: Bridge Bents
    narration = """Bents are the supporting structures for bridges. As shown in Figure 8-12, 
a bent is composed of the bent cap, columns, footings, and piles beneath. 
End bents normally use piles for support. The bent cap is constructed of reinforced concrete 
and supports the beams. Footings support the columns and may rest on piles or firm soil. 
Piles are used when firm material is not available. Steel piles are used in rocky areas, 
while concrete piles are used in coastal areas where steel would corrode."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Bridge Bents",
        "source_pages": "62",
        "source_text": "The following are views of the most common types of Interior and End Bents.",
        "image_paths": [f"assets/images/chapter08/figure_8_12.jpg"],
        "bullets": [
            "Bent cap, columns, footings",
            "Steel or concrete piles",
            "Support for beams"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 10: Utility Accommodations
    narration = """Often utilities such as water lines, gas lines, telephone lines, and power lines 
must cross roadways spanned by bridges. Figure 8-13 shows how utilities are supported below a bridge slab. 
Concrete inserts are placed in the slab when concrete is poured. Hangers are then screwed into 
the bottom of the insert when utilities are installed. Utilities are normally placed inside 
the exterior beams and above the bottom of the beam so they cannot be seen from below. 
Figure 8-14 shows how utilities pass through the end wall at the end of a bridge."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Utility Accommodations",
        "source_pages": "64-65",
        "source_text": "Often it is necessary for UTILITIES to cross the roadway spanned by a bridge.",
        "image_paths": [f"assets/images/chapter08/figure_8_13.jpg", f"assets/images/chapter08/figure_8_14.jpg"],
        "bullets": [
            "Utilities below bridge slab",
            "Concrete inserts and hangers",
            "Pass through end walls"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 11: Summary
    narration = """Let's review what we've covered in this chapter on Drainage. 
You've learned the difference between culverts and bridges based on their span length. 
You understand the parts of box culverts including barrels, wing walls, and the significance of skew angles. 
You know how to read longitudinal sections and plan views of culverts. 
You've learned about bridge components including the superstructure and substructure, 
bents, and how utilities are accommodated. 
This knowledge is essential for reading drainage plans on highway construction projects."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Summary",
        "source_pages": "65",
        "source_text": "Summary of Chapter 8: Drainage",
        "image_paths": [],
        "bullets": [
            "Culverts vs bridges",
            "Box culvert components",
            "Bridge structure elements"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch08_scene{scene_idx:02d}.wav",
        "duration": None
    })
    
    manifest = {
        "chapter": 8,
        "pages": "53-65",
        "title": "Drainage",
        "lessons": 3,
        "lesson_boundaries": {
            "lesson_01": {"scenes": [1, 2, 3, 4], "title": "Introduction and Pipe Culverts"},
            "lesson_02": {"scenes": [5, 6, 7], "title": "Box Culverts and Wing Walls"},
            "lesson_03": {"scenes": [8, 9, 10, 11], "title": "Bridges and Utilities"}
        },
        "scenes": scenes,
        "images": images,
        "total_duration": None
    }
    
    return manifest, all_sanitization

# ============================================================================
# CHAPTER 9: UTILITIES (Pages 67-68, 0 figures, 1 lesson)
# ============================================================================

def get_chapter_9_manifest():
    """Generate manifest for Chapter 9: Utility Plans"""
    markdown = read_markdown()
    all_sanitization = {}
    
    scenes = []
    scene_idx = 1
    
    # Scene 1: Title/Introduction
    narration = """Welcome to Chapter Nine of Basic Highway Plan Reading. 
This chapter covers Utility Plans, which are used primarily to facilitate coordination 
between the construction contractor and utility companies having facilities in the roadway corridor. 
The Department of Transportation is not involved in the relocation of utilities 
unless done under a Force Account. Utility plans show the contractor the approximate locations 
of existing, relocated, and proposed new utilities, helping identify and avoid conflicts or damage."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Introduction to Utility Plans",
        "source_pages": "67",
        "source_text": "Utility plans are used primarily to facilitate coordination between the construction contractor and utility companies.",
        "image_paths": [],
        "bullets": [
            "Coordination with utilities",
            "Existing and proposed locations",
            "Avoid conflicts and damage"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch09_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 2: Utility Plan Content
    narration = """Utility plans show the contractor the approximate locations of existing utilities, 
relocated utilities, and proposed new utilities. This helps designers and contractors identify 
potential conflicts and avoid damage to facilities. Information is typically obtained from 
field survey data or from the affected utility owner. 
An example utility plan might show gas lines where one is being relocated 
while another remains in its original location. 
Pipeline dig notification requirements are also noted on these plans."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Utility Plan Content",
        "source_pages": "67",
        "source_text": "These plans show the contractor the approximate locations of existing, relocated, and proposed new utilities.",
        "image_paths": [],
        "bullets": [
            "Existing utility locations",
            "Relocated and new utilities",
            "Dig notification requirements"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch09_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 3: Summary
    narration = """To summarize Chapter Nine, utility plans are essential for coordinating construction 
with utility companies. These plans show approximate, not exact, locations of utilities. 
The information comes from field surveys and utility owners. 
As a contractor, you must use these plans to identify potential conflicts 
and protect existing utility infrastructure during construction. 
In the next chapter, we'll cover signing, pavement markings, signals, lighting, and landscaping."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Summary",
        "source_pages": "67-68",
        "source_text": "Summary of Chapter 9: Utility Plans",
        "image_paths": [],
        "bullets": [
            "Approximate utility locations",
            "Coordination is key",
            "Protect existing utilities"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch09_scene{scene_idx:02d}.wav",
        "duration": None
    })
    
    manifest = {
        "chapter": 9,
        "pages": "67-68",
        "title": "Utility Plans",
        "lessons": 1,
        "scenes": scenes,
        "images": {},
        "total_duration": None
    }
    
    return manifest, all_sanitization

# ============================================================================
# CHAPTER 10: SIGNING, MARKINGS, SIGNALS, LIGHTING, LANDSCAPING (Pages 69-70)
# ============================================================================

def get_chapter_10_manifest():
    """Generate manifest for Chapter 10"""
    all_sanitization = {}
    scenes = []
    scene_idx = 1
    
    # Scene 1: Title/Introduction
    narration = """Welcome to Chapter Ten of Basic Highway Plan Reading. 
This chapter covers Signing and Pavement Markings, Traffic Signals, Highway Lighting, and Landscaping. 
These elements are critical for driver safety and guidance. 
Sign and pavement marking plans are normally in the same general format as roadway plans. 
All permanent roadway signs and pavement markings are placed on the plans 
as they should appear upon completion of the project."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Introduction",
        "source_pages": "69",
        "source_text": "Plans are also prepared consisting of signs and pavement markings.",
        "image_paths": [],
        "bullets": [
            "Signs and pavement markings",
            "Traffic signals and lighting",
            "Landscaping plans"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch10_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 2: Pavement Markings
    narration = """All required pavement markings are depicted on the plans including color, width, and spacing. 
Call-outs may identify the type of each line on plan sheets. 
All required arrows and hatching in accordance with Department Standards are included. 
While each arrow may not be labeled, at least one note referencing the applicable standard 
is included on each sheet. A summary of quantities for overhead signs typically follows 
the sign and pavement marking plans."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Pavement Markings",
        "source_pages": "69",
        "source_text": "All required pavement markings are depicted on the plans including the color, width, and spacing.",
        "image_paths": [],
        "bullets": [
            "Color, width, and spacing",
            "Arrows and hatching",
            "Reference standards noted"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch10_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 3: Traffic Signals
    narration = """Traffic signal plans show the complete site layout, equipment details, 
electrical circuitry, signal phasing, and other relevant data. 
A separate plan sheet is provided for each intersection requiring signalization. 
A summary table shows the items needed for each intersection, including the name of the item, 
method of payment, and quantity to be used for each installation."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Traffic Signals",
        "source_pages": "69",
        "source_text": "The signalization plans will show the complete site layout, equipment details, electrical circuitry, signal phasing.",
        "image_paths": [],
        "bullets": [
            "Complete site layout",
            "Electrical circuitry",
            "Signal phasing details"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch10_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 4: Lighting and Landscaping
    narration = """Highway lighting plans are required when a project involves lighting improvements. 
These plans provide construction details, electrical circuit tabulations, pole data summaries, 
luminaire type and intensity, foundations, and other lighting-related data. 
For high mast lighting, soil survey and foundation design are required. 
Landscaping plans, when required, include an overall site plan, planting plans, 
planting details, and irrigation plans."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Lighting and Landscaping",
        "source_pages": "69-70",
        "source_text": "Highway lighting plans are required when a project involves lighting improvements.",
        "image_paths": [],
        "bullets": [
            "Lighting construction details",
            "High mast requirements",
            "Landscape planting plans"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch10_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 5: Summary
    narration = """Let's review Chapter Ten. Sign and pavement marking plans follow the same format as roadway plans. 
Pavement markings show color, width, and spacing. Traffic signal plans include complete layouts 
and electrical details for each intersection. Lighting plans cover all electrical and foundation requirements. 
Landscaping plans include site plans, planting plans, and irrigation details. 
In the next chapter, we'll cover maintenance of traffic and staging."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Summary",
        "source_pages": "70",
        "source_text": "Summary of Chapter 10",
        "image_paths": [],
        "bullets": [
            "Markings show details",
            "Signal plans per intersection",
            "Lighting and landscaping"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch10_scene{scene_idx:02d}.wav",
        "duration": None
    })
    
    manifest = {
        "chapter": 10,
        "pages": "69-70",
        "title": "Signing, Pavement Markings, Signals, Lighting, Landscaping",
        "lessons": 1,
        "scenes": scenes,
        "images": {},
        "total_duration": None
    }
    
    return manifest, all_sanitization

# ============================================================================
# CHAPTER 11: MAINTENANCE OF TRAFFIC (Pages 71-72)
# ============================================================================

def get_chapter_11_manifest():
    """Generate manifest for Chapter 11"""
    all_sanitization = {}
    scenes = []
    scene_idx = 1
    
    # Scene 1: Title/Introduction
    narration = """Welcome to Chapter Eleven of Basic Highway Plan Reading. 
This chapter covers Maintenance of Traffic, Sequence of Operations, and Staging. 
Special attention is given to constructability, traffic handling, detours, 
restrictions to traffic, hours of closure or lane loss, and contractor responsibility. 
The Traffic Control Plan complements the Traffic Control Specifications 
and the Manual of Uniform Traffic Control Devices."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Introduction",
        "source_pages": "71",
        "source_text": "Special attention is given to constructability, traffic handling, detours, restrictions to traffic.",
        "image_paths": [],
        "bullets": [
            "Traffic handling and detours",
            "Hours of closure",
            "Contractor responsibility"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch11_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 2: Traffic Control Plans
    narration = """Traffic Control Plan sheets are prepared for each stage of construction 
using information from plan sheets and intersection layouts. 
For each construction stage, plans show roadway areas and major drainage structures to be constructed, 
along with traffic flow patterns including lane widths. 
Plans indicate areas of temporary pavement, locations of temporary barriers, 
and any temporary drainage structures. 
A narrative of the sequence of construction and traffic handling for each stage is also included."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Traffic Control Plans",
        "source_pages": "71",
        "source_text": "Traffic Control Plan sheets for each stage of construction are prepared.",
        "image_paths": [],
        "bullets": [
            "Stage-by-stage planning",
            "Traffic flow patterns",
            "Temporary barriers and pavements"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch11_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 3: Detours
    narration = """If an on-site detour is required, detour plans with cross sections and signing are included. 
These show the detour centerline with curve and alignment data, detour profile, pavement edges and width, 
construction limits, required right-of-way and easements, temporary drainage, and temporary barriers. 
If a road closing and off-site detour is required, a plan shows the layout of local roads 
with road closure points and the detour route."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Detour Plans",
        "source_pages": "71-72",
        "source_text": "If an on-site detour is required, detour plans with cross sections and signing are included.",
        "image_paths": [],
        "bullets": [
            "On-site detour details",
            "Off-site detour routes",
            "Road closure points"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch11_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 4: Summary
    narration = """To summarize Chapter Eleven, Traffic Control Plans are developed specifically for each project, 
not used generically from project to project. Detours receive significant attention in traffic control planning. 
Cross sections of construction stages may be included where necessary. 
Understanding these plans ensures safe and efficient traffic flow during construction. 
In the next chapter, we'll cover Erosion, Sedimentation, and Pollution Control Plans."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Summary",
        "source_pages": "72",
        "source_text": "Summary of Chapter 11",
        "image_paths": [],
        "bullets": [
            "Project-specific plans",
            "Detour attention required",
            "Stage cross sections"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch11_scene{scene_idx:02d}.wav",
        "duration": None
    })
    
    manifest = {
        "chapter": 11,
        "pages": "71-72",
        "title": "Maintenance of Traffic, Sequence of Operations, and Staging",
        "lessons": 1,
        "scenes": scenes,
        "images": {},
        "total_duration": None
    }
    
    return manifest, all_sanitization

# ============================================================================
# CHAPTER 12: ESPCP (Pages 73-76, 2 figures, 1 lesson)
# ============================================================================

def get_chapter_12_manifest():
    """Generate manifest for Chapter 12"""
    markdown = read_markdown()
    
    ch12_start = markdown.find("# Chapter 12: Erosion")
    ch13_start = markdown.find("# Chapter 13: Cross Sections")
    ch12_content = markdown[ch12_start:ch13_start] if ch12_start != -1 else ""
    
    images = extract_image_urls(ch12_content, 12)
    all_sanitization = {}
    scenes = []
    scene_idx = 1
    
    # Scene 1: Title/Introduction
    narration = """Welcome to Chapter Twelve of Basic Highway Plan Reading. 
This chapter covers Erosion, Sedimentation, and Pollution Control Plans, often abbreviated ESPCP. 
Steep embankments, ditches, or other exposed surfaces adjacent to a roadway require erosion control 
to prevent soil from eroding due to wind, water, and freeze-thaw action. 
Measures such as grassing, silt fence, paved ditches, straw mulch, silt gates, 
and soil reinforcing mats may be used depending on the need."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Introduction to ESPCP",
        "source_pages": "73",
        "source_text": "Steep embankments, ditches, or other exposed surfaces require erosion control.",
        "image_paths": [],
        "bullets": [
            "Prevent soil erosion",
            "Wind, water, freeze-thaw",
            "Various control measures"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch12_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 2: When ESPCP Required
    narration = """ESPCP requirements depend on project size. 
If the total project disturbs less than one acre, only a set of Best Management Practices, 
or BMP Location Details, are prepared and included in construction plans. 
BMPs are either structural, like rip-rap or paved ditches, or vegetative, like grassing or sod. 
If the project disturbs one acre or more, a standalone erosion control package is required, 
placed at the back of the final construction plans."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "When ESPCP is Required",
        "source_pages": "73",
        "source_text": "If the total project disturbs less than one (1) acres only a set of BMP Location Details are prepared.",
        "image_paths": [f"assets/images/chapter12/figure_12_1.jpg"],
        "bullets": [
            "Less than 1 acre: BMP only",
            "1 acre or more: full ESPCP",
            "Structural or vegetative BMPs"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch12_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 3: ESPCP Contents
    narration = """The ESPCP standalone package includes several sheets: a Cover Sheet, General Note Sheet, 
Drainage Area Map, and BMP Plan Sheets. As shown in Figure 12-2, these sheets use the same scale 
and matchlines as the construction plans. Erosion control measures are identified by standard symbols. 
Examples include CO for construction exit, SD for temporary sediment basin, 
and CH for channel stabilization. All required measures are found in construction details."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "ESPCP Contents",
        "source_pages": "74",
        "source_text": "Included in ESPCP standalone package you should find: Cover Sheet, General Note Sheet, Drainage Area Map, BMP Plan Sheets.",
        "image_paths": [f"assets/images/chapter12/figure_12_2.jpg"],
        "bullets": [
            "Cover and note sheets",
            "Drainage area map",
            "BMP plan sheets"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch12_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 4: Contractor Responsibilities
    narration = """While the Department of Transportation provides the erosion control plans, 
contractors have specific responsibilities. If there are any changes to staging, 
the contractor is responsible for revising the plans. 
Additionally, contractors are responsible for ESPCP for borrow pits, haul roads, and waste pits. 
Berm ditches may require concrete ditch paving as erosion control measures, 
with limits and quantities noted in the Summary of Quantities."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Contractor Responsibilities",
        "source_pages": "74-75",
        "source_text": "The contractor is responsible for revising the plans if there are changes to staging.",
        "image_paths": [],
        "bullets": [
            "Revise plans for changes",
            "Responsible for borrow pits",
            "Haul roads and waste pits"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch12_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 5: Summary
    narration = """To summarize Chapter Twelve, ESPCP are required when a project disturbs one acre or more. 
These plans follow Department Specification Section 161. Erosion control measures include grassing, 
silt fence, paved ditches, straw mulch, and many others. 
Contractors must revise plans when staging changes and are responsible for erosion control 
at borrow pits, haul roads, and waste pits. 
In the next chapter, we'll cover Cross Sections."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Summary",
        "source_pages": "75-76",
        "source_text": "Summary of Chapter 12: ESPCP",
        "image_paths": [],
        "bullets": [
            "Required for 1+ acres",
            "Specification Section 161",
            "Contractor responsibilities"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch12_scene{scene_idx:02d}.wav",
        "duration": None
    })
    
    manifest = {
        "chapter": 12,
        "pages": "73-76",
        "title": "Erosion, Sedimentation, and Pollution Control Plans (ESPCP)",
        "lessons": 1,
        "scenes": scenes,
        "images": images,
        "total_duration": None
    }
    
    return manifest, all_sanitization

# ============================================================================
# CHAPTER 13: CROSS SECTIONS (Pages 77-84, 11 figures, 2 lessons)
# ============================================================================

def get_chapter_13_manifest():
    """Generate manifest for Chapter 13"""
    markdown = read_markdown()
    
    ch13_start = markdown.find("# Chapter 13: Cross Sections")
    ch14_start = markdown.find("# Chapter 14: Standards")
    ch13_content = markdown[ch13_start:ch14_start] if ch13_start != -1 else ""
    
    images = extract_image_urls(ch13_content, 13)
    all_sanitization = {}
    scenes = []
    scene_idx = 1
    
    # Scene 1: Title/Introduction
    narration = """Welcome to Chapter Thirteen of Basic Highway Plan Reading. 
This chapter covers Cross Sections, which depict existing ground conditions 
as sections perpendicular to the construction centerline. 
The proposed cross-sectional outline of the new roadway with all its elements is also shown. 
Standard Cross Section Plan Sheets use a recommended scale of 1 inch equals 100 feet 
or 1 inch equals 200 feet. Understanding cross sections is essential for earthwork calculations."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Introduction to Cross Sections",
        "source_pages": "77",
        "source_text": "Cross Sections depict the existing ground conditions as sections perpendicular to the construction centerline.",
        "image_paths": [],
        "bullets": [
            "Perpendicular to centerline",
            "Existing and proposed shown",
            "Scale 1 inch = 100 feet"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch13_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 2: Cross Section Elements
    narration = """Existing ground lines are shown with a dashed line, while proposed roadway templates 
use solid lines. The existing ground elevation at the profile grade line is noted below the ground line. 
Existing construction such as pavements, curbs, and sidewalks are shown with dashed lines. 
The station number is normally shown in heavy numbers to the right of or below the cross section. 
Profile grade elevations are shown vertically above the profile grade line."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Cross Section Elements",
        "source_pages": "77",
        "source_text": "Existing ground lines are shown with a dashed line. The proposed roadway template is shown with a solid line.",
        "image_paths": [],
        "bullets": [
            "Dashed for existing",
            "Solid for proposed",
            "Station numbers in heavy type"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch13_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 3: Earthwork
    narration = """Figure 13-1 illustrates typical terrain for a two-lane roadway, conveying depth 
that a plan view cannot show. Earthwork, measured in cubic yards, changes from station to station. 
Because earthwork is costly, it must be carefully estimated using cross section plan sheets. 
Figure 13-2 shows examples of cut and fill cross sections. A cross section may be all cut, all fill, 
or part cut and part fill. The designer combines the typical section with the existing ground 
to determine cut and fill areas."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Earthwork",
        "source_pages": "77-78",
        "source_text": "Earthwork is usually a costly item in highway construction.",
        "image_paths": [f"assets/images/chapter13/figure_13_1.jpg", f"assets/images/chapter13/figure_13_2.jpg"],
        "bullets": [
            "Cubic yards of dirt",
            "Cut and fill sections",
            "Costly item in construction"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch13_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 4: Typical Sections
    narration = """As shown in Figures 13-3 and 13-4, the typical section represents an end view 
of the pavement necessary for the designed traffic volume. The cross section of the original ground 
is distinctive for every location along the centerline. By combining the typical section 
with the original ground cross section, you can determine cut and fill areas. 
Figure 13-6 shows how volume is calculated by multiplying depth by the average of end areas."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Typical Sections and Volume",
        "source_pages": "78-79",
        "source_text": "The typical section represents an end view of the pavement necessary to carry the type and volume of traffic.",
        "image_paths": [f"assets/images/chapter13/figure_13_3.jpg", f"assets/images/chapter13/figure_13_4.jpg", f"assets/images/chapter13/figure_13_6.jpg"],
        "bullets": [
            "Typical section for traffic",
            "Combine with ground section",
            "Volume by end area method"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch13_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 5: Grade
    narration = """The profile grade elevation is the top elevation listed on cross sections. 
The lower elevation shows the finished grade for the ditch. The smaller elevation shown 
just below the profile grade is the existing grade. You can verify elevations by comparing 
the cross section sheet with the plan and profile sheets. 
The profile grade is typically at the center of the median for divided highways."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Grade",
        "source_pages": "80",
        "source_text": "The profile grade elevation listed for a station is the top elevation.",
        "image_paths": [],
        "bullets": [
            "Profile grade is top elevation",
            "Ditch grade shown below",
            "Verify with plan sheets"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch13_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 6: Slopes
    narration = """Slopes are referred to as cut slopes or back slopes, fill slopes, and side slopes 
or front slopes. A cut slope runs from the drainage ditch to the top of the cut. 
A fill slope runs from the shoulder point to the toe of the fill. 
Slopes are measured as a ratio of horizontal distance versus vertical distance. 
A 2:1 slope means for every 2 feet horizontal, the elevation changes 1 foot vertical. 
Figure 13-7 shows various slope configurations used on cross sections."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Slopes",
        "source_pages": "80-81",
        "source_text": "Slopes are usually referred to as cut slopes, fill slopes, and side slopes.",
        "image_paths": [f"assets/images/chapter13/figure_13_7.jpg", f"assets/images/chapter13/figure_13_8.jpg"],
        "bullets": [
            "Cut, fill, and side slopes",
            "Ratio horizontal to vertical",
            "2:1 slope common"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch13_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 7: Slope Stakes
    narration = """Slope stakes contain information telling the contractor how much cut or fill is required 
from the stake to the ditch line or shoulder point. They are placed at the intersection 
of the cut or fill slope with the natural ground line. As shown in Figures 13-9 through 13-11, 
the front of the stake shows cut or fill indicator, amount of cut or fill, 
distance to centerline, rate of slope, and superelevation rate if in a curve. 
The station number appears on the back of the stake."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Slope Stakes",
        "source_pages": "81-83",
        "source_text": "Slope stakes contain information that tells the Contractor how much cut or fill is required.",
        "image_paths": [f"assets/images/chapter13/figure_13_9.jpg", f"assets/images/chapter13/figure_13_10.jpg", f"assets/images/chapter13/figure_13_11.jpg"],
        "bullets": [
            "Cut or fill amount",
            "Distance to centerline",
            "Station on back of stake"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch13_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 8: Summary
    narration = """Let's review Chapter Thirteen on Cross Sections. 
Cross sections depict both existing ground and proposed roadway perpendicular to the centerline. 
Existing features use dashed lines while proposed uses solid lines. 
Earthwork volumes are calculated using the end area method from cross sections. 
Slopes are expressed as ratios of horizontal to vertical distance. 
Slope stakes provide cut and fill information at specific locations. 
In the next chapter, we'll cover Standards and Details."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Summary",
        "source_pages": "83-84",
        "source_text": "Summary of Chapter 13: Cross Sections",
        "image_paths": [],
        "bullets": [
            "Existing vs proposed lines",
            "End area volume method",
            "Slope stake information"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch13_scene{scene_idx:02d}.wav",
        "duration": None
    })
    
    manifest = {
        "chapter": 13,
        "pages": "77-84",
        "title": "Cross Sections",
        "lessons": 2,
        "lesson_boundaries": {
            "lesson_01": {"scenes": [1, 2, 3, 4], "title": "Cross Sections and Earthwork"},
            "lesson_02": {"scenes": [5, 6, 7, 8], "title": "Grade, Slopes, and Slope Stakes"}
        },
        "scenes": scenes,
        "images": images,
        "total_duration": None
    }
    
    return manifest, all_sanitization

# ============================================================================
# CHAPTER 14: STANDARDS & DETAILS (Pages 85-86, 1 figure, 1 lesson)
# ============================================================================

def get_chapter_14_manifest():
    """Generate manifest for Chapter 14"""
    markdown = read_markdown()
    
    ch14_start = markdown.find("# Chapter 14: Standards")
    ch15_start = markdown.find("# Chapter 15: Right of Way")
    ch14_content = markdown[ch14_start:ch15_start] if ch14_start != -1 else ""
    
    images = extract_image_urls(ch14_content, 14)
    all_sanitization = {}
    scenes = []
    scene_idx = 1
    
    # Scene 1: Title/Introduction
    narration = """Welcome to Chapter Fourteen of Basic Highway Plan Reading. 
This chapter covers Standards and Details. Georgia Construction Standard Drawings, or Standards, 
are generalized construction drawings applicable to most projects. 
Think of Standards as drawings showing the normal way the Department of Transportation 
wants something built. Georgia Construction Detail Drawings, or Details, 
are more specific and specialized, showing methods not common to all projects."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Introduction",
        "source_pages": "85",
        "source_text": "Georgia Construction Standard Drawings or Standards are generalized construction drawings.",
        "image_paths": [],
        "bullets": [
            "Standards: generalized drawings",
            "Details: specialized methods",
            "Special Details: project-specific"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch14_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 2: Types of Drawings
    narration = """There are three types of drawings you'll encounter. Georgia Construction Standard Drawings 
are general drawings used on most projects. Georgia Construction Detail Drawings show specialized methods 
not commonly used on all projects. Georgia Special Construction Details are specific to one project only. 
On the Index Sheet, you'll find which sheets are Construction Details and which are Construction Standards, 
all to be used on the job."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Types of Drawings",
        "source_pages": "85",
        "source_text": "Georgia Special Construction Details are drawings that are specific to that project only.",
        "image_paths": [],
        "bullets": [
            "Standard Drawings: general",
            "Detail Drawings: specialized",
            "Special Details: one project"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch14_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 3: Intersection Details and Ramps
    narration = """Intersection details are larger scale views showing information that couldn't be clearly shown 
on smaller scale plan sheets. As shown in Figure 14-1, each ramp in an interchange is identified 
by a letter designation, usually assigned starting from the upper left moving clockwise. 
Interior ramps or loops are designated with subscripts like A1, A2, or as Loop A, Loop B. 
Ramps constructed under a previous contract are shown with dashed lines indicating existing conditions."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Intersection Details",
        "source_pages": "85-86",
        "source_text": "Intersection details are larger scale views showing detailed information.",
        "image_paths": [f"assets/images/chapter14/figure_14_1.jpg"],
        "bullets": [
            "Larger scale views",
            "Ramps identified by letters",
            "Loops use subscripts"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch14_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 4: Summary
    narration = """To summarize Chapter Fourteen, remember that Georgia Construction Standard Drawings 
are generally used drawings showing the normal construction method. 
Georgia Construction Detail Drawings show methods not common to all projects. 
Georgia Special Construction Details are project-specific. 
Intersection details provide enlarged views of complex areas. 
Ramp identification uses letter designations with loops using subscripts. 
In the final chapter, we'll cover Right of Way."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Summary",
        "source_pages": "86",
        "source_text": "Summary of Chapter 14: Standards & Details",
        "image_paths": [],
        "bullets": [
            "Three types of drawings",
            "Intersection detail views",
            "Ramp letter designations"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch14_scene{scene_idx:02d}.wav",
        "duration": None
    })
    
    manifest = {
        "chapter": 14,
        "pages": "85-86",
        "title": "Standards & Details",
        "lessons": 1,
        "scenes": scenes,
        "images": images,
        "total_duration": None
    }
    
    return manifest, all_sanitization

# ============================================================================
# CHAPTER 15: RIGHT OF WAY (Pages 87-94, 4 figures, 2 lessons)
# ============================================================================

def get_chapter_15_manifest():
    """Generate manifest for Chapter 15"""
    markdown = read_markdown()
    
    ch15_start = markdown.find("# Chapter 15: Right of Way")
    appendix_start = markdown.find("# Questions for Appendices")
    ch15_content = markdown[ch15_start:appendix_start] if ch15_start != -1 else ""
    
    images = extract_image_urls(ch15_content, 15)
    all_sanitization = {}
    scenes = []
    scene_idx = 1
    
    # Scene 1: Title/Introduction
    narration = """Welcome to Chapter Fifteen, the final chapter of Basic Highway Plan Reading. 
This chapter covers Right of Way. To construct any highway, the Right of Way Office must secure 
the needed land. Right of Way personnel are often the first official contact property owners have 
with the Department. It's essential that they be competent in plan reading 
so they can properly interpret highway plans for property owners."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Introduction to Right of Way",
        "source_pages": "87",
        "source_text": "In order to construct any highway, the Right of Way Office must be successful in securing the needed land.",
        "image_paths": [],
        "bullets": [
            "Secure land for highway",
            "First contact with owners",
            "Interpret plans for owners"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch15_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 2: Property Owner Concerns
    narration = """Property owners have many concerns about highway projects. 
They ask about ingress and egress, how cuts and fills affect their property, 
and how their residence or business will be impacted. Farmers are particularly interested 
in how fields and pastures will be divided, access to water, fencing relocation, 
livestock movement, and construction timing relative to planting and harvest seasons. 
The Right of Way Specialist must be able to answer these questions confidently."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Property Owner Concerns",
        "source_pages": "87-88",
        "source_text": "Property owners will ask questions regarding ingress and egress of a proposed highway.",
        "image_paths": [],
        "bullets": [
            "Ingress and egress questions",
            "Cuts and fills impact",
            "Farm operation concerns"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch15_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 3: Key Terms
    narration = """Right of Way has many specialized terms. Right of Way itself denotes land or interest 
acquired for highway purposes. A partial take means acquiring only a portion of a property, 
while a total take acquires the entire property. Easements grant the Department rights 
to use property for specific purposes and durations. Construction easements extend 
to the farthest limits of construction beyond right of way limits. 
Limited access means ingress and egress only at designated points."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Right of Way Terms",
        "source_pages": "88-91",
        "source_text": "RIGHT OF WAY - this is a term denoting land, interest therein, or property which is acquired for highway purposes.",
        "image_paths": [],
        "bullets": [
            "Partial vs total take",
            "Types of easements",
            "Limited access defined"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch15_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 4: Right of Way Plan Sheets
    narration = """Right of Way Plans are separate from Construction Plans. As shown in Figure 15-1, 
they include two cover sheets with sheet number differences from construction plans. 
Similar to construction plans, a revision summary sheet is included. 
The cover sheets show property owners instead of an index, with parcels identified 
by rectangular boxes with numbers. The plan view shows the project in relationship 
to property lines rather than topographical landmarks."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Right of Way Plan Sheets",
        "source_pages": "91",
        "source_text": "Right of Way Plans are a separate set of plans from the construction Plans.",
        "image_paths": [f"assets/images/chapter15/figure_15_1.jpg"],
        "bullets": [
            "Separate from construction",
            "Two cover sheets",
            "Shows property owners"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch15_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 5: Conventional Symbols
    narration = """Right of Way plans use conventional symbols that differ from construction plans. 
As shown in Figure 15-2, pay close attention to variations among line types. 
Land lot lines are thin dashed lines marked with LLL. Required Right of Way and Limit of Access lines 
are thicker than land lot lines. Property lines are thin solid lines broken by a single dash, 
marked with PL. Existing right of way uses the same symbol as property lines but without the PL marking."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Conventional Symbols",
        "source_pages": "91-93",
        "source_text": "Conventional Symbols - notice the slight variations among the various types of lines.",
        "image_paths": [f"assets/images/chapter15/figure_15_2.jpg", f"assets/images/chapter15/figure_15_3.jpg"],
        "bullets": [
            "Line type variations",
            "Land lot lines: LLL",
            "Property lines: PL"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch15_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 6: Property Information
    narration = """Property information details are shown either on the same plan sheet as the property 
or on a separate sheet. As shown in Figure 15-4, the taking is described by point, offset and distance, 
station and bearing, and alignment. The offset is from centerline, and distance is to the next 
right of way point. The alignment indicates which construction centerline is being used. 
Construction and drive easements are marked with diagonal shadings on the plan sheets."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Property Information",
        "source_pages": "93-94",
        "source_text": "Property information that details the right of way taking is shown on the plan sheet.",
        "image_paths": [f"assets/images/chapter15/figure_15_4.jpg"],
        "bullets": [
            "Point, offset, distance",
            "Station and bearing",
            "Easements with diagonal shading"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch15_scene{scene_idx:02d}.wav",
        "duration": None
    })
    scene_idx += 1
    
    # Scene 7: Course Summary
    narration = """Congratulations! You've completed Basic Highway Plan Reading. 
Throughout this course, you've learned to read cover sheets, understand indexes and revisions, 
interpret typical sections, read views and profiles, understand stationing and symbols, 
work with drainage and cross sections, and understand right of way plans. 
These skills are essential for anyone working in highway construction. 
Thank you for completing this course, and best of luck in your career."""
    
    sanitized, smap = sanitize_narration(narration)
    all_sanitization.update(smap)
    
    scenes.append({
        "index": scene_idx,
        "title": "Course Summary",
        "source_pages": "94",
        "source_text": "Summary of Chapter 15 and complete course",
        "image_paths": [],
        "bullets": [
            "Course completion",
            "Essential plan reading skills",
            "Ready for highway work"
        ],
        "narration_text": narration.strip(),
        "narration_sanitized": sanitized.strip(),
        "narration_raw": narration.strip(),
        "tts_file": f"audio/ch15_scene{scene_idx:02d}.wav",
        "duration": None
    })
    
    manifest = {
        "chapter": 15,
        "pages": "87-94",
        "title": "Right of Way",
        "lessons": 2,
        "lesson_boundaries": {
            "lesson_01": {"scenes": [1, 2, 3], "title": "Introduction and Terms"},
            "lesson_02": {"scenes": [4, 5, 6, 7], "title": "Plan Sheets and Symbols"}
        },
        "scenes": scenes,
        "images": images,
        "total_duration": None
    }
    
    return manifest, all_sanitization

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("Extracting content for Chapters 8-15")
    print("=" * 60)
    
    chapters = [
        (8, get_chapter_8_manifest),
        (9, get_chapter_9_manifest),
        (10, get_chapter_10_manifest),
        (11, get_chapter_11_manifest),
        (12, get_chapter_12_manifest),
        (13, get_chapter_13_manifest),
        (14, get_chapter_14_manifest),
        (15, get_chapter_15_manifest),
    ]
    
    total_scenes = 0
    total_images = 0
    
    for chapter_num, manifest_func in chapters:
        print(f"\n[Chapter {chapter_num}] Generating manifest...")
        
        manifest, sanitization_map = manifest_func()
        
        # Save manifest
        manifest_path = MANIFESTS_DIR / f"chapter{chapter_num:02d}.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"    Saved: {manifest_path.name}")
        
        # Save sanitization map
        if sanitization_map:
            sanitization_path = MANIFESTS_DIR / f"sanitization_map_chapter{chapter_num:02d}.json"
            with open(sanitization_path, 'w', encoding='utf-8') as f:
                json.dump(sanitization_map, f, indent=2, ensure_ascii=False)
            print(f"    Saved: {sanitization_path.name}")
        
        scenes_count = len(manifest['scenes'])
        images_count = len(manifest.get('images', {}))
        lessons = manifest.get('lessons', 1)
        
        print(f"    Lessons: {lessons}, Scenes: {scenes_count}, Images: {images_count}")
        total_scenes += scenes_count
        total_images += images_count
    
    print("\n" + "=" * 60)
    print(f"TOTAL: {total_scenes} scenes, {total_images} images to download")
    print("=" * 60)

if __name__ == "__main__":
    main()
