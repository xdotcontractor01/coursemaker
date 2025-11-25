"""
Step 2: Generate Summary
Generates a concise 100-word summary from markdown input
"""

from shared import *

def main():
    """Generate summary from markdown content"""
    print_step(2, "Generate Summary")
    
    try:
        # Read input markdown
        input_file = TEST_DIR / 'input.md'
        if not input_file.exists():
            print_error("Input file not found. Run step_01 first.")
            return 1
        
        md_content = input_file.read_text(encoding='utf-8')
        print_info(f"Loaded input: {len(md_content)} characters")
        
        # Generate summary with LLM
        prompt = f"""{SYSTEM_GDOT}

Task: Generate a concise 100-word summary of the following Markdown document.
Focus on:
- Main technical concepts
- Key safety or compliance points
- Practical applications for DOT contractors
- Critical takeaways

Markdown Document:
{md_content}

Provide only the summary text, no additional formatting or commentary."""
        
        print_info("Calling LLM for summary...")
        summary, tokens = call_llm(prompt, max_tokens=300)
        
        print_info(f"Tokens used: {tokens}")
        print_info(f"Summary length: {len(summary)} characters")
        print("\n" + "-"*80)
        print("SUMMARY:")
        print(summary)
        print("-"*80)
        
        # Save summary
        summary_file = TEST_DIR / 'summary.txt'
        summary_file.write_text(summary, encoding='utf-8')
        print_info(f"Summary saved to: {summary_file}")
        
        # Save token count
        tokens_file = TEST_DIR / 'tokens_step_02.txt'
        tokens_file.write_text(str(tokens))
        
        print_success("Summary generated successfully")
        return 0
        
    except Exception as e:
        print_error(f"Failed to generate summary: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

