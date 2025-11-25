"""
Step 4: Suggest Images for Slides
Uses LLM to suggest relevant images with layout types
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
        prompt = f"""{SYSTEM_GDOT}

Task: Suggest relevant images for each slide in an educational video about bridge construction.

REQUIREMENTS:
- Suggest 1-2 images per slide (skip title/conclusion slides)
- Images should support the content, not distract
- Provide specific search queries for SerpAPI
- Choose appropriate layout type for each image

AVAILABLE LAYOUT TYPES:
- background_only: Subtle background image at 25% opacity (best for text-heavy slides)
- split_left: Image on left, content on right (good for comparisons)
- split_right: Content on left, image on right (best for showing examples)
- sidebar_right: Small image on right side (minimal distraction)

Slide Information:
{slides_info}

Content Summary:
{summary}

Provide JSON output ONLY (no other text):
[
  {{
    "slide_no": 2,
    "query": "bridge steel beam construction site",
    "layout": "split_right",
    "purpose": "Show actual bridge beams during explanation"
  }},
  ...
]

Only suggest images for slides 2-5 (skip title and conclusion). Be selective - not every slide needs an image.
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
        
        print_info(f"Suggested {len(suggestions)} images")
        for sugg in suggestions:
            slide = sugg.get('slide_no')
            query = sugg.get('query', '')
            layout = sugg.get('layout', 'background_only')
            print_info(f"  Slide {slide}: '{query}' [layout: {layout}]")
        
        print_success("Image suggestions generated successfully")
        return 0
        
    except Exception as e:
        print_error(f"Failed to suggest images: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

