"""
Step 1: Validate Markdown Input
Validates markdown content and saves it for processing

INPUT OPTIONS (in priority order):
1. Command line argument: python step_01_validate_input.py path/to/file.md
2. INPUT.md file in test_workflow folder (RECOMMENDED - easy to edit!)
3. Built-in SAMPLE_MD (fallback)
"""

import sys
from shared import *

# Path to the easy-to-edit INPUT.md file
_SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_FILE = _SCRIPT_DIR / 'INPUT.md'

def main():
    """Validate markdown input"""
    print_step(1, "Validate Markdown Input")
    
    try:
        # Priority 1: Command line argument
        if len(sys.argv) > 1:
            input_path = Path(sys.argv[1])
            if not input_path.exists():
                print_error(f"Input file not found: {input_path}")
                return 1
            md_content = input_path.read_text(encoding='utf-8')
            print_info(f"Loaded markdown from: {input_path}")
        
        # Priority 2: INPUT.md file in test_workflow folder
        elif INPUT_FILE.exists():
            md_content = INPUT_FILE.read_text(encoding='utf-8')
            print_info(f"Loaded from INPUT.md: {INPUT_FILE}")
            print_info("TIP: Edit INPUT.md to change content!")
        
        # Priority 3: Built-in sample
        else:
            md_content = SAMPLE_MD
            print_info("Using built-in SAMPLE_MD content")
            print_info("TIP: Create INPUT.md in test_workflow/ for custom content!")
        
        # Validate content
        print_info(f"Content length: {len(md_content)} characters")
        print_info(f"Lines: {len(md_content.split(chr(10)))}")
        
        if len(md_content) < 50:
            print_error("Content too short (minimum 50 characters)")
            return 1
        
        # Save validated input
        input_file = TEST_DIR / 'input.md'
        input_file.write_text(md_content, encoding='utf-8')
        print_info(f"Input saved to: {input_file}")
        
        print_success("Input validation passed")
        return 0
        
    except Exception as e:
        print_error(f"Failed to validate input: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

