"""
Chapter Orchestrator
Runs the complete video generation pipeline for a single chapter.
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add parent to path for shared utilities
sys.path.insert(0, str(Path(__file__).parent))
from shared import print_step, print_info, print_success, print_error

# Pipeline imports
from pipeline.utils.markdown_parser import parse_chapter_markdown
from pipeline.parse_curriculum import CurriculumParser
from pipeline.video_plan_generator import VideoPlanGenerator
from pipeline.manim_script_generator import ManimScriptGenerator
from pipeline.dry_run_validator import DryRunValidator
from pipeline.llm_repair_loop import LLMRepairLoop
from pipeline.narration_generator import NarrationGenerator
from pipeline.quality_gates import QualityGates


class ChapterPipeline:
    """Orchestrates the complete video generation pipeline for a chapter"""
    
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        figures_dir: Optional[Path] = None,
        pdf_path: Optional[Path] = None,
        max_repair_attempts: int = 3
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.figures_dir = figures_dir or input_dir.parent / "figures"
        self.pdf_path = pdf_path
        self.max_repair_attempts = max_repair_attempts
        
        # Initialize components
        self.curriculum_parser = CurriculumParser(input_dir, output_dir, self.figures_dir)
        self.plan_generator = VideoPlanGenerator(output_dir, self.figures_dir)
        self.script_generator = ManimScriptGenerator(output_dir, self.figures_dir)
        self.validator = DryRunValidator(output_dir)
        self.repairer = LLMRepairLoop(output_dir)
        self.narration_generator = NarrationGenerator(output_dir, pdf_path)
        self.quality_gates = QualityGates(pdf_path)
    
    def run_chapter(self, chapter_file: Path, skip_render: bool = False) -> dict:
        """Run the complete pipeline for a single chapter"""
        
        results = {
            "chapter_file": str(chapter_file),
            "started_at": datetime.now().isoformat(),
            "videos": [],
            "success": False
        }
        
        print_step(1, f"Parsing Chapter: {chapter_file.name}")
        
        # Step 1: Parse chapter markdown
        try:
            chapter_content = parse_chapter_markdown(chapter_file, self.figures_dir)
            print_success(f"Parsed: {chapter_content.title}")
            print_info(f"Subsections: {chapter_content.subsection_count}")
            print_info(f"Recommended videos: {chapter_content.get_video_count_recommendation()}")
        except Exception as e:
            print_error(f"Failed to parse chapter: {e}")
            results["error"] = str(e)
            return results
        
        # Step 2: Create chapter manifest
        print_step(2, "Creating Video Manifest")
        try:
            chapter_manifest = self.curriculum_parser.parse_chapter(chapter_file)
            print_success(f"Created manifest with {chapter_manifest.video_count} videos")
        except Exception as e:
            print_error(f"Failed to create manifest: {e}")
            results["error"] = str(e)
            return results
        
        # Step 3-N: Process each video
        for i, video_topic in enumerate(chapter_manifest.videos, 1):
            video_result = self._process_video(
                video_topic,
                chapter_content,
                video_num=i,
                total_videos=chapter_manifest.video_count,
                skip_render=skip_render
            )
            results["videos"].append(video_result)
        
        # Final summary
        successful = sum(1 for v in results["videos"] if v.get("success", False))
        results["success"] = successful == len(results["videos"])
        results["completed_at"] = datetime.now().isoformat()
        results["summary"] = {
            "total_videos": len(results["videos"]),
            "successful": successful,
            "failed": len(results["videos"]) - successful
        }
        
        print("\n" + "="*60)
        print(f"CHAPTER COMPLETE: {chapter_content.title}")
        print("="*60)
        print(f"Videos: {successful}/{len(results['videos'])} successful")
        
        return results
    
    def _process_video(
        self,
        video_topic,
        chapter_content,
        video_num: int,
        total_videos: int,
        skip_render: bool = False
    ) -> dict:
        """Process a single video through the pipeline"""
        
        video_result = {
            "video_id": video_topic.video_id,
            "title": video_topic.title,
            "success": False,
            "steps": {}
        }
        
        video_dir = self.output_dir / video_topic.chapter_id / video_topic.video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"VIDEO {video_num}/{total_videos}: {video_topic.title}")
        print(f"{'='*60}")
        
        # Step A: Generate video plan
        print_step("A", "Generating Video Plan")
        try:
            # Get content for this video's subsections
            video_content = self._get_subsection_content(
                chapter_content, video_topic.subsections_covered
            )
            
            plan = self.plan_generator.generate_plan(
                video_id=video_topic.video_id,
                chapter_id=video_topic.chapter_id,
                title=video_topic.title,
                description=video_topic.description,
                subsections=video_topic.subsections_covered,
                content=video_content,
                figure_refs=video_topic.figure_refs,
                target_duration=video_topic.estimated_duration_seconds,
                target_word_count=video_topic.target_word_count,
                target_slide_count=video_topic.target_slide_count
            )
            self.plan_generator.save_plan(plan)
            video_result["steps"]["plan"] = "success"
            print_success(f"Plan created: {len(plan.slides)} slides")
        except Exception as e:
            print_error(f"Failed to generate plan: {e}")
            video_result["steps"]["plan"] = f"error: {e}"
            return video_result
        
        # Step B: Generate Manim script
        print_step("B", "Generating Manim Script")
        try:
            script_result = self.script_generator.generate_script(
                video_id=video_topic.video_id,
                chapter_id=video_topic.chapter_id,
                title=video_topic.title,
                description=video_topic.description,
                slides=[{
                    "title": s.title,
                    "visual_goal": s.visual_goal,
                    "visual_recipe": s.visual_recipe,
                    "timing_seconds": s.timing_seconds
                } for s in plan.slides],
                figure_paths=plan.figure_paths,
                source_file=chapter_content.source_file
            )
            video_result["steps"]["script"] = "success"
            video_result["diversity_score"] = script_result.diversity_score
            print_success(f"Script generated (diversity: {script_result.diversity_score})")
        except Exception as e:
            print_error(f"Failed to generate script: {e}")
            video_result["steps"]["script"] = f"error: {e}"
            return video_result
        
        # Step C: Validate script
        print_step("C", "Validating Script")
        validation = self.validator.validate_script(script_result.script_path, video_topic.video_id)
        self.validator.save_validation_report(validation)
        
        if not validation.passed:
            print_error(f"Validation failed: {len(validation.errors)} errors")
            
            # Step D: Repair loop
            print_step("D", "Running Repair Loop")
            repair_result = self.repairer.repair_script(
                script_result.script_path,
                video_topic.video_id,
                validation
            )
            self.repairer.save_repair_history(repair_result)
            
            if repair_result.final_success:
                print_success("Script repaired successfully")
                video_result["steps"]["repair"] = "success"
            else:
                print_error("Repair failed - manual intervention needed")
                video_result["steps"]["repair"] = "failed"
                video_result["failure_ticket"] = str(repair_result.failure_ticket_path)
                return video_result
        else:
            print_success("Validation passed")
            video_result["steps"]["validation"] = "success"
        
        # Step E: Generate narration
        print_step("E", "Generating Narration")
        try:
            narration_result = self.narration_generator.generate_narration(
                video_id=video_topic.video_id,
                chapter_id=video_topic.chapter_id,
                title=video_topic.title,
                description=video_topic.description,
                slides=[{
                    "title": s.title,
                    "visual_goal": s.visual_goal,
                    "narration_text": s.narration_text
                } for s in plan.slides],
                source_content=video_content,
                source_file=chapter_content.source_file
            )
            self.narration_generator.save_narration(narration_result)
            video_result["steps"]["narration"] = "success"
            print_success(f"Narration: {narration_result.total_word_count} words")
        except Exception as e:
            print_error(f"Failed to generate narration: {e}")
            video_result["steps"]["narration"] = f"error: {e}"
            return video_result
        
        # Step F: Quality gates
        print_step("F", "Running Quality Gates")
        quality_report = self.quality_gates.check_all_gates(
            video_id=video_topic.video_id,
            chapter_id=video_topic.chapter_id,
            script_path=script_result.script_path,
            narration_data={
                "segments": [
                    {
                        "slide_number": seg.slide_number,
                        "word_count": seg.word_count,
                        "source_tags": seg.source_tags,
                        "has_contractor_caution": seg.has_contractor_caution,
                        "caution_verified": seg.caution_verified
                    }
                    for seg in narration_result.segments
                ],
                "review_questions": narration_result.review_questions
            }
        )
        self.quality_gates.save_report(quality_report, video_dir / "quality_report.json")
        self.quality_gates.print_report(quality_report)
        
        video_result["quality_passed"] = quality_report.all_gates_passed
        video_result["steps"]["quality"] = "passed" if quality_report.all_gates_passed else "failed"
        
        # Step G: Render (if not skipped)
        if not skip_render:
            print_step("G", "Rendering Video")
            try:
                render_result = self._render_video(
                    video_dir=video_dir,
                    script_path=script_result.script_path,
                    video_id=video_topic.video_id
                )
                if render_result["success"]:
                    video_result["steps"]["render"] = "success"
                    video_result["video_path"] = render_result["video_path"]
                    print_success(f"Video rendered: {render_result['video_path']}")
                else:
                    print_error(f"Render failed: {render_result['error']}")
                    video_result["steps"]["render"] = f"error: {render_result['error']}"
            except Exception as e:
                print_error(f"Render exception: {e}")
                video_result["steps"]["render"] = f"error: {e}"
        
        video_result["success"] = True
        print_success(f"Video {video_topic.video_id} completed!")
        
        return video_result
    
    def _render_video(self, video_dir: Path, script_path: Path, video_id: str) -> dict:
        """Render the Manim script to a video file"""
        import subprocess
        import re
        
        result = {"success": False, "video_path": None, "error": None}
        
        # Find the scene class name in the script
        script_content = script_path.read_text()
        class_match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', script_content)
        
        if not class_match:
            result["error"] = "Could not find Scene class in script"
            return result
        
        scene_name = class_match.group(1)
        print_info(f"Rendering scene: {scene_name}")
        
        # Run manim to render the video
        # Use medium quality for faster rendering (-qm), high quality would be -qh
        cmd = [
            sys.executable, "-m", "manim",
            "render",
            "-qm",  # Medium quality (720p30)
            "--media_dir", str(video_dir / "media"),
            str(script_path),
            scene_name
        ]
        
        print_info(f"Running: {' '.join(cmd)}")
        
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if process.returncode != 0:
                result["error"] = f"Manim failed: {process.stderr[:500]}"
                return result
            
            # Find the output video
            media_videos = video_dir / "media" / "videos" / script_path.stem
            
            # Look for the rendered video in any quality folder
            for quality_dir in media_videos.iterdir() if media_videos.exists() else []:
                if quality_dir.is_dir():
                    for video_file in quality_dir.glob("*.mp4"):
                        result["success"] = True
                        result["video_path"] = str(video_file)
                        return result
            
            # Fallback: search recursively
            for video_file in (video_dir / "media").rglob("*.mp4"):
                result["success"] = True
                result["video_path"] = str(video_file)
                return result
            
            result["error"] = "Video file not found after render"
            return result
            
        except subprocess.TimeoutExpired:
            result["error"] = "Render timed out after 5 minutes"
            return result
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def _get_subsection_content(self, chapter_content, subsection_titles: List[str]) -> str:
        """Extract content for specific subsections"""
        content_parts = []
        for subsection in chapter_content.subsections:
            if subsection.title in subsection_titles:
                content_parts.append(f"## {subsection.title}\n\n{subsection.content}")
        
        if not content_parts:
            # Fallback to raw content
            return chapter_content.raw_content[:3000]
        
        return "\n\n".join(content_parts)


def main():
    parser = argparse.ArgumentParser(description="Run video generation for a chapter")
    parser.add_argument("chapter_file", type=Path, help="Path to chapter markdown file")
    parser.add_argument("--output", "-o", type=Path, default=None, 
                       help="Output directory (default: output/gdot_plan_videos)")
    parser.add_argument("--figures", "-f", type=Path, default=None,
                       help="Figures directory")
    parser.add_argument("--pdf", "-p", type=Path, default=None,
                       help="Path to PDF for caution verification")
    parser.add_argument("--skip-render", action="store_true",
                       help="Skip video rendering step")
    
    args = parser.parse_args()
    
    # Set defaults
    script_dir = Path(__file__).parent
    output_dir = args.output or script_dir / "output" / "gdot_plan_videos"
    figures_dir = args.figures or script_dir / "figures"
    
    if not args.chapter_file.exists():
        print_error(f"Chapter file not found: {args.chapter_file}")
        return 1
    
    print("="*60)
    print("GDOT VIDEO GENERATION PIPELINE")
    print("="*60)
    print(f"Chapter: {args.chapter_file}")
    print(f"Output: {output_dir}")
    print(f"Figures: {figures_dir}")
    print("="*60)
    
    pipeline = ChapterPipeline(
        input_dir=args.chapter_file.parent,
        output_dir=output_dir,
        figures_dir=figures_dir,
        pdf_path=args.pdf
    )
    
    results = pipeline.run_chapter(args.chapter_file, skip_render=args.skip_render)
    
    # Save results
    results_file = output_dir / f"results_{args.chapter_file.stem}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2))
    print_info(f"\nResults saved: {results_file}")
    
    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())


