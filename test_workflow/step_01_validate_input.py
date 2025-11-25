"""
Step 1: Validate Markdown Input
Validates markdown content and saves it for processing
"""

import sys
from shared import *

def main():
    """Validate markdown input"""
    print_step(1, "Validate Markdown Input")
    
    try:
        # Get markdown content from command line or use sample
        if len(sys.argv) > 1:
            input_path = Path(sys.argv[1])
            if not input_path.exists():
                print_error(f"Input file not found: {input_path}")
                return 1
            md_content = input_path.read_text(encoding='utf-8')
            print_info(f"Loaded markdown from: {input_path}")
        else:
            md_content = SAMPLE_MD
            print_info("Using built-in SAMPLE_MD content")
        
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

