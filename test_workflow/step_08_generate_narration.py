"""
Step 8: Generate Narration
Generates detailed narration script for each slide
"""

import re
import json
from shared import *

def main():
    """Generate narration script"""
    print_step(8, "Generate Narration")
    
    try:
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
            f"Slide {s.get('slide_no', i+1)}: {s.get('title', 'Content')} (Duration: {s.get('duration', 25)}s)"
            for i, s in enumerate(timings)
        ])
        
        # Generate narration with LLM
        prompt = f"""{SYSTEM_GDOT}

Task: Generate detailed, educational narration for each slide with explanations.

NARRATION REQUIREMENTS:
- Professional yet conversational tone
- EXPLAIN what the audience is seeing on screen
- Reference visual elements ("As shown in the diagram...", "Notice the blue circles...")
- Provide practical DOT-specific tips and examples
- Include safety reminders where relevant
- Natural pacing for text-to-speech (approximately 3-4 words per second)
- Fill the entire duration with valuable content

NARRATION STRUCTURE PER SLIDE:
1. Opening (2-3 seconds): Introduce the topic
2. Main Content (15-20 seconds): Explain key concepts, reference visuals
3. Practical Tip (3-5 seconds): Real-world application
4. Transition (2-3 seconds): Lead into next topic

EXAMPLE GOOD NARRATION:
"Let's examine the key components shown in this diagram. As you can see, the main elements are highlighted in blue, representing the critical areas that require attention. Notice how each component connects to form the complete system. For GDOT contractors and engineers, it's essential to follow the proper procedures and verify compliance at each step. The reference image in the corner shows a real-world example of what we're discussing. Any deviations from the specified requirements could impact safety and require costly corrections later."

Slide Information:
{slides_info}

Content Summary:
{summary}

CRITICAL: Write 50-80 words per slide to fill the duration. Be educational and descriptive.

Provide JSON output:
[
  {{"slide_no": 1, "duration": 25, "narration_text": "Detailed narration here..."}},
  ...
]

Provide only the JSON array, no additional text."""
        
        print_info("Calling LLM for narration...")
        content, tokens = call_llm(prompt, max_tokens=1500)
        
        print_info(f"Tokens used: {tokens}")
        
        # Extract JSON
        try:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                narrations = json.loads(json_match.group(0))
            else:
                narrations = json.loads(content)
        except json.JSONDecodeError as e:
            print_error(f"Could not parse narration JSON: {e}")
            print("\n" + "-"*80)
            print("RAW RESPONSE:")
            print(content)
            print("-"*80)
            return 1
        
        # Save narrations
        narration_file = TEST_DIR / 'narration.json'
        narration_file.write_text(json.dumps(narrations, indent=2))
        print_info(f"Narration saved to: {narration_file}")
        
        # Save token count
        tokens_file = TEST_DIR / 'tokens_step_08.txt'
        tokens_file.write_text(str(tokens))
        
        print_info(f"Generated {len(narrations)} narration clips")
        for i, narr in enumerate(narrations):
            text = narr.get('narration_text', '')
            duration = narr.get('duration', 0)
            word_count = len(text.split())
            print_info(f"  Clip {i+1}: {duration}s, {len(text)} chars, {word_count} words")
        
        print_success("Narration generated successfully")
        return 0
        
    except Exception as e:
        print_error(f"Failed to generate narration: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

