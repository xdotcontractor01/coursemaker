"""
PDF Extraction and Video Generation Orchestrator
Extracts content from PDF pages 1-11, analyzes images, generates markdown,
and creates Manim videos with embedded figures.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "pipeline"))

from shared import print_step, print_info, print_success, print_error
from pipeline.pdf_extractor import PDFExtractor, extract_pdf_content


def clear_previous_output(output_dir: Path, figures_dir: Path):
    """Clear previous extraction results"""
    print_info("Clearing previous output...")
    
    # Clear figures
    chapter_figures = figures_dir / "chapter_01"
    if chapter_figures.exists():
        shutil.rmtree(chapter_figures)
        print_info(f"  Cleared: {chapter_figures}")
    
    # Clear video output
    video_output = output_dir / "output" / "gdot_plan_videos" / "chapter_01"
    if video_output.exists():
        shutil.rmtree(video_output)
        print_info(f"  Cleared: {video_output}")


def run_extraction_pipeline(
    pdf_path: Path,
    output_dir: Path,
    start_page: int = 1,
    end_page: int = 11,
    analyze_images: bool = True,
    clear_cache: bool = True
):
    """
    Run the complete PDF extraction and video generation pipeline.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Base output directory
        start_page: First page to extract (1-indexed)
        end_page: Last page to extract (1-indexed)
        analyze_images: Whether to use LLM for image analysis
        clear_cache: Whether to clear previous output
    """
    
    print("=" * 70)
    print("PDF EXTRACTION AND VIDEO GENERATION PIPELINE")
    print("=" * 70)
    print(f"PDF: {pdf_path}")
    print(f"Pages: {start_page} to {end_page}")
    print(f"Output: {output_dir}")
    print("=" * 70)
    
    figures_dir = output_dir / "figures"
    markdown_dir = output_dir / "input_markdown"
    
    # Step 0: Clear previous output
    if clear_cache:
        print_step(0, "Clearing Previous Output")
        clear_previous_output(output_dir, figures_dir)
    
    # Step 1: Extract PDF content
    print_step(1, "Extracting PDF Content")
    
    if not pdf_path.exists():
        print_error(f"PDF not found: {pdf_path}")
        return None
    
    try:
        extractor = PDFExtractor(pdf_path, output_dir)
        extraction_result = extractor.extract_pages(start_page, end_page)
        print_success(f"Extracted {len(extraction_result.pages)} pages")
        print_info(f"Found {extraction_result.total_images} images")
    except Exception as e:
        print_error(f"Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 2: Analyze images with LLM
    if analyze_images and extraction_result.all_images:
        print_step(2, "Analyzing Images with LLM")
        try:
            extraction_result.all_images = extractor.analyze_images_with_llm(
                extraction_result.all_images,
                use_vision=True
            )
            print_success(f"Analyzed {len(extraction_result.all_images)} images")
        except Exception as e:
            print_error(f"Image analysis failed: {e}")
            print_info("Continuing with fallback descriptions...")
    else:
        print_step(2, "Skipping Image Analysis")
    
    # Step 3: Save extraction results
    print_step(3, "Saving Extraction Results")
    try:
        result_path = extractor.save_extraction_result(extraction_result)
        print_success(f"Saved: {result_path}")
    except Exception as e:
        print_error(f"Failed to save results: {e}")
    
    # Step 4: Generate markdown content
    print_step(4, "Generating Enhanced Markdown")
    try:
        markdown_content = extractor.generate_markdown_content(extraction_result)
        
        markdown_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = markdown_dir / "chapter_01.md"
        markdown_path.write_text(markdown_content, encoding='utf-8')
        
        print_success(f"Saved: {markdown_path}")
        print_info(f"Content length: {len(markdown_content)} characters")
    except Exception as e:
        print_error(f"Markdown generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Generate image metadata JSON for video pipeline
    print_step(5, "Creating Image Metadata for Videos")
    try:
        image_metadata = {
            "chapter_id": "chapter_01",
            "extracted_from": str(pdf_path),
            "pages": f"{start_page}-{end_page}",
            "images": []
        }
        
        for img in extraction_result.all_images:
            # Make path relative
            rel_path = Path(img.file_path)
            if rel_path.is_absolute():
                try:
                    rel_path = rel_path.relative_to(output_dir)
                except ValueError:
                    pass
            
            image_metadata["images"].append({
                "id": img.image_id,
                "path": str(rel_path),
                "page": img.page_number,
                "label": img.figure_label,
                "width": img.width,
                "height": img.height,
                "description": img.description,
                "key_elements": img.key_elements or [],
                "educational_points": img.educational_points or [],
                "highlight_suggestions": img.highlight_suggestions or []
            })
        
        metadata_path = figures_dir / "chapter_01" / "image_metadata.json"
        metadata_path.write_text(json.dumps(image_metadata, indent=2))
        print_success(f"Saved: {metadata_path}")
        
    except Exception as e:
        print_error(f"Metadata creation failed: {e}")
    
    # Step 6: Run video generation pipeline
    print_step(6, "Running Video Generation Pipeline")
    
    try:
        from run_chapter import ChapterPipeline
        
        video_output = output_dir / "output" / "gdot_plan_videos"
        video_output.mkdir(parents=True, exist_ok=True)
        
        pipeline = ChapterPipeline(
            input_dir=markdown_dir,
            output_dir=video_output,
            figures_dir=figures_dir,
            pdf_path=pdf_path
        )
        
        results = pipeline.run_chapter(
            markdown_path,
            skip_render=False  # Set to True for faster testing
        )
        
        # Save pipeline results
        results_file = video_output / "chapter_01_results.json"
        results_file.write_text(json.dumps(results, indent=2))
        print_success(f"Pipeline results saved: {results_file}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)
        
        if results.get("success"):
            print_success(f"Successfully generated {len(results.get('videos', []))} videos")
        else:
            print_error(f"Some videos failed. Check results file for details.")
        
        for video in results.get("videos", []):
            status = "✓" if video.get("success") else "✗"
            print(f"  {status} {video.get('video_id')}: {video.get('title')}")
            if video.get("video_path"):
                print(f"      → {video.get('video_path')}")
        
    except ImportError as e:
        print_error(f"Pipeline import failed: {e}")
        print_info("You can run the chapter pipeline manually:")
        print(f"  python run_chapter.py {markdown_path}")
    except Exception as e:
        print_error(f"Video generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"Pages extracted: {len(extraction_result.pages)}")
    print(f"Images extracted: {extraction_result.total_images}")
    print(f"Figures directory: {figures_dir / 'chapter_01'}")
    print(f"Markdown file: {markdown_path}")
    print("=" * 70)
    
    return extraction_result


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract PDF content and generate Manim videos"
    )
    parser.add_argument(
        "--pdf", "-p",
        type=Path,
        default=None,
        help="Path to PDF file (default: BasicHiwyPlanReading (1).pdf)"
    )
    parser.add_argument(
        "--start", "-s",
        type=int,
        default=1,
        help="Start page (1-indexed, default: 1)"
    )
    parser.add_argument(
        "--end", "-e",
        type=int,
        default=11,
        help="End page (1-indexed, default: 11)"
    )
    parser.add_argument(
        "--no-analyze",
        action="store_true",
        help="Skip LLM image analysis"
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Don't clear previous output"
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Only extract PDF, don't generate videos"
    )
    
    args = parser.parse_args()
    
    # Set paths
    script_dir = Path(__file__).parent
    pdf_path = args.pdf or script_dir / "BasicHiwyPlanReading (1).pdf"
    
    if args.extract_only:
        # Just do extraction
        from pipeline.pdf_extractor import extract_pdf_content
        result = extract_pdf_content(
            pdf_path,
            script_dir,
            args.start,
            args.end,
            analyze_images=not args.no_analyze
        )
        print(f"\nExtracted {len(result.pages)} pages with {result.total_images} images")
    else:
        # Run full pipeline
        run_extraction_pipeline(
            pdf_path=pdf_path,
            output_dir=script_dir,
            start_page=args.start,
            end_page=args.end,
            analyze_images=not args.no_analyze,
            clear_cache=not args.no_clear
        )


if __name__ == "__main__":
    main()

