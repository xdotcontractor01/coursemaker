"""
Pilot Runner
Runs the complete pipeline for Chapter 1 only (pilot chapter).
Use this to test the pipeline before running on all chapters.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
from shared import print_step, print_info, print_success, print_error

from run_chapter import ChapterPipeline


def main():
    """Run pilot chapter (Chapter 1)"""
    
    script_dir = Path(__file__).parent
    
    # Paths
    input_dir = script_dir / "input_markdown"
    output_dir = script_dir / "output" / "gdot_plan_videos"
    figures_dir = script_dir / "figures"
    pdf_path = script_dir / "BasicHiwyPlanReading (1).pdf"
    
    # Look for chapter 1
    chapter_file = input_dir / "chapter_01.md"
    
    print("="*60)
    print("GDOT VIDEO GENERATION - PILOT RUN")
    print("="*60)
    print(f"Chapter 1 file: {chapter_file}")
    print(f"Output: {output_dir}")
    print(f"PDF: {pdf_path}")
    print("="*60)
    
    # Check if chapter file exists
    if not chapter_file.exists():
        print_error(f"\nChapter 1 markdown not found: {chapter_file}")
        print_info("\nTo run the pilot, create the chapter markdown file:")
        print_info(f"  {chapter_file}")
        print_info("\nExample content:")
        print("""
---
title: "Chapter 1: Beginning to Read Plans"
chapter_id: chapter_01
key_terms:
  - Cover Sheet
  - Project Identification
  - Sheet Order
learning_objectives:
  - Identify components of a cover sheet
  - Understand document hierarchy
  - Locate project specifications
---

# Chapter 1: Beginning to Read Plans

## General Information

Highway construction plans follow a standardized format...

## Cover Sheet

The cover sheet is the first page of any plan set...

## Sheet Order

Plans are organized in a specific order...
""")
        
        # Create a sample chapter file
        print_info("\nCreating sample chapter_01.md for testing...")
        input_dir.mkdir(parents=True, exist_ok=True)
        
        sample_content = '''---
title: "Chapter 1: Beginning to Read Plans"
chapter_id: chapter_01
key_terms:
  - Cover Sheet
  - Project Identification
  - Sheet Order
  - Contract Specifications
learning_objectives:
  - Identify the key components of a cover sheet
  - Understand the hierarchy of contract documents
  - Locate project identification information
---

# Chapter 1: Beginning to Read Plans

## General Information

Highway construction plans follow a standardized format established by the Georgia Department of Transportation. Understanding this format is essential for contractors, engineers, and inspectors working on GDOT projects.

The contract documents establish the requirements for construction. When reading plans, always refer to the specifications and special provisions for detailed requirements.

## Requirements and Specifications

The Standard Specifications for Construction of Transportation Systems contains the general requirements that apply to all projects. These specifications are supplemented by:

- Special Provisions (project-specific requirements)
- Supplemental Specifications
- Standard Drawings

In case of a discrepancy, certain parts of the contract govern over others according to subsection 102.04 of the Standard Specifications.

## Cover Sheet

The cover sheet is the first and most important page of any construction plan set. It contains critical project identification information including:

- Project Number and P.I. Number
- Route and County Information  
- Project Limits (beginning and ending points)
- Project Length
- Design Data

As shown in Figure 1-1, the cover sheet provides a layout view of the entire project area. This helps orient readers to the project location and scope.

## Sheet Order

Construction plans are organized in a specific sequence to facilitate navigation:

1. Cover Sheet
2. Index and Revision Summary
3. Typical Sections
4. Summary of Quantities
5. Plan and Profile Sheets
6. Drainage Plans
7. Cross Sections
8. Standards and Details

Familiarizing yourself with this order will help you quickly locate specific information within the plan set.

## Errors or Omissions

If you discover errors or omissions in the construction plans, report them immediately to the Engineer per subsection 104.03. Do not proceed with work that may be affected by the discrepancy.

Clear communication about plan errors helps prevent costly rework and ensures project quality.
'''
        chapter_file.write_text(sample_content)
        print_success(f"Created: {chapter_file}")
    
    # Also create figures directory
    figures_chapter_dir = figures_dir / "chapter_01"
    figures_chapter_dir.mkdir(parents=True, exist_ok=True)
    print_info(f"Figures directory: {figures_chapter_dir}")
    print_info("(Add figure images here if available)")
    
    # Check PDF exists
    if pdf_path.exists():
        print_success(f"PDF found: {pdf_path}")
    else:
        print_info(f"PDF not found (optional): {pdf_path}")
        pdf_path = None
    
    # Run the pipeline
    print("\n" + "="*60)
    print("STARTING PILOT PIPELINE")
    print("="*60 + "\n")
    
    pipeline = ChapterPipeline(
        input_dir=input_dir,
        output_dir=output_dir,
        figures_dir=figures_dir,
        pdf_path=pdf_path
    )
    
    results = pipeline.run_chapter(chapter_file, skip_render=False)
    
    # Save results
    results_file = output_dir / "pilot_results.json"
    import json
    results_file.write_text(json.dumps(results, indent=2))
    
    # Print final summary
    print("\n" + "="*60)
    print("PILOT RUN COMPLETE")
    print("="*60)
    
    if results["success"]:
        print_success("All videos generated successfully!")
    else:
        print_error("Some videos failed - check results for details")
    
    print(f"\nResults: {results_file}")
    print(f"Output: {output_dir / 'chapter_01'}")
    
    # List generated files
    chapter_output = output_dir / "chapter_01"
    if chapter_output.exists():
        print("\nGenerated files:")
        for video_dir in sorted(chapter_output.iterdir()):
            if video_dir.is_dir():
                files = list(video_dir.glob("*"))
                print(f"  {video_dir.name}/")
                for f in files:
                    print(f"    - {f.name}")
    
    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())


