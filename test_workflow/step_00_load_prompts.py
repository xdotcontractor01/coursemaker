"""
Step 0: Load System Prompts
Loads and saves the SYSTEM_GDOT prompt to disk
"""

from shared import *

def main():
    """Load and save system prompts"""
    print_step(0, "Load System Prompts")
    
    try:
        # Save system prompt to file
        prompt_file = TEST_DIR / 'system_prompt.txt'
        prompt_file.write_text(SYSTEM_GDOT)
        print_info(f"System prompt saved to: {prompt_file}")
        print_info(f"Prompt length: {len(SYSTEM_GDOT)} characters")
        
        print_success("System prompts loaded successfully")
        return 0
        
    except Exception as e:
        print_error(f"Failed to load prompts: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

