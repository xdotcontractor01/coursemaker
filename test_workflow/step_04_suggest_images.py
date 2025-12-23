"""
Step 4: Suggest Images for Slides
Uses LLM to suggest relevant reference images for slides.
Images will be displayed in top-right corner with "Reference Image" label.
"""

import re
import json
from shared import *

def main():
    """Suggest images for slides"""
    print_step(4, "Suggest Images for Slides")
    
    try:
        # Check if SERPAPI_KEY is configured
        if not SERPAPI_KEY:
            print_info("No SERPAPI_KEY found, skipping image suggestions")
            # Create empty images.json
            suggestions_file = TEST_DIR / 'images.json'
            suggestions_file.write_text('[]')
            print_info("Created empty images.json")
            return 0
        
        # Read summary
        summary_file = TEST_DIR / 'summary.txt'
        if not summary_file.exists():
            print_error("Summary file not found. Run step_02 first.")
            return 1
        summary = summary_file.read_text(encoding='utf-8')
        
        # Read timings
        timings_file = TEST_DIR / 'timings.json'
        if not timings_file.exists():
            print_error("Timings file not found. Run step_03 first.")
            return 1
        timings = json.loads(timings_file.read_text())
        
        print_info(f"Loaded summary and {len(timings)} slide timings")
        
        # Build slides info
        slides_info = "\n".join([
            f"Slide {s.get('slide_no', i+1)}: {s.get('title', 'Content')} ({s.get('duration', 25)}s)"
            for i, s in enumerate(timings)
        ])
        
        # Generate image suggestions with LLM
        # Note: Images will be placed in top-right corner as small reference images
        prompt = f"""{SYSTEM_GDOT}

Task: Suggest relevant reference images for each slide in an educational video about GDOT technical content.

IMPORTANT: Images will be displayed as small reference images in the TOP-RIGHT CORNER of the video
with a "Reference Image" label below. They should complement the content, not be the main focus.

REQUIREMENTS:
- Suggest 1 image per content slide (skip title/conclusion slides)
- Images should be clear, professional technical references
- Provide specific search queries for Google Images
- Focus on diagrams, technical illustrations, or real-world photos
- Images should be recognizable even at small size

GOOD IMAGE TYPES:
- Technical diagrams and cross-sections
- Real construction/field photos
- Safety equipment and procedures
- Engineering drawings and schematics
- Regulatory compliance visuals
- Process flowcharts

Slide Information:
{slides_info}

Content Summary:
{summary}

Provide JSON output ONLY (no other text):
[
  {{
    "slide_no": 2,
    "query": "specific technical diagram query here",
    "purpose": "Reference showing relevant concept"
  }},
  ...
]

Only suggest images for content slides (typically slides 2-5). Skip title and conclusion slides.
"""
        
        print_info("Calling LLM for image suggestions...")
        content, tokens = call_llm(prompt, max_tokens=800)
        
        print_info(f"Tokens used: {tokens}")
        
        # Extract JSON
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group(0))
            else:
                suggestions = json.loads(content)
        except json.JSONDecodeError as e:
            print_error(f"Could not parse image suggestions: {e}")
            print_info("Response: " + content[:200])
            suggestions = []
        
        # Save suggestions
        suggestions_file = TEST_DIR / 'images.json'
        suggestions_file.write_text(json.dumps(suggestions, indent=2))
        print_info(f"Suggestions saved to: {suggestions_file}")
        
        # Save token count
        tokens_file = TEST_DIR / 'tokens_step_04.txt'
        tokens_file.write_text(str(tokens))
        
        print_info(f"Suggested {len(suggestions)} reference images")
        for sugg in suggestions:
            slide = sugg.get('slide_no')
            query = sugg.get('query', '')
            purpose = sugg.get('purpose', '')
            print_info(f"  Slide {slide}: '{query}'")
            if purpose:
                print_info(f"    Purpose: {purpose}")
        
        print_success("Image suggestions generated successfully")
        return 0
        
    except Exception as e:
        print_error(f"Failed to suggest images: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

