#!/usr/bin/env python3
"""
Unified Lesson Builder
Merges course content and quiz data into unified lesson JSON files.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedLessonBuilder:
    """Builds unified lesson JSON files from course content and quizzes."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.content_dir = self.workspace_root / "manifests" / "course_content"
        self.quiz_dir = self.workspace_root / "quizzes"
        self.output_dir = self.workspace_root / "unified_lessons"
        self.logs_dir = self.workspace_root / "logs"
        
        # Statistics
        self.stats = {
            "lessons_processed": 0,
            "lessons_with_quizzes": 0,
            "lessons_without_quizzes": 0,
            "total_quiz_questions": 0,
            "files_written": 0,
            "errors": 0
        }
        self.error_log = []
        
    def setup_directories(self):
        """Create output and log directories."""
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
    def find_lessons(self) -> List[str]:
        """Find all lesson directories in course_content."""
        lessons = []
        if not self.content_dir.exists():
            logger.error(f"Content directory not found: {self.content_dir}")
            return lessons
            
        for item in sorted(self.content_dir.iterdir()):
            if item.is_dir() and item.name.startswith("Chapter"):
                content_file = item / "content.json"
                if content_file.exists():
                    lessons.append(item.name)
                else:
                    logger.warning(f"No content.json in {item.name}")
                    
        return lessons
    
    def load_content(self, lesson_name: str) -> Optional[Dict]:
        """Load content.json for a lesson."""
        content_path = self.content_dir / lesson_name / "content.json"
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading content for {lesson_name}: {e}")
            self.error_log.append({
                "lesson": lesson_name,
                "error": f"Failed to load content: {str(e)}"
            })
            return None
    
    def load_quiz(self, lesson_name: str) -> Optional[Dict]:
        """Load import_ready.json for a lesson."""
        quiz_path = self.quiz_dir / lesson_name / "import_ready.json"
        if not quiz_path.exists():
            logger.info(f"No quiz file for {lesson_name}")
            return None
            
        try:
            with open(quiz_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading quiz for {lesson_name}: {e}")
            self.error_log.append({
                "lesson": lesson_name,
                "error": f"Failed to load quiz: {str(e)}"
            })
            return None
    
    def map_quiz_question(self, question: Dict, chapter: int, video: int) -> Dict:
        """Map a quiz question to unified format."""
        # Find correct option index
        correct_option = None
        mapped_options = []
        
        for idx, option in enumerate(question.get("options", [])):
            mapped_options.append({
                "text": option.get("text", ""),
                "generated_distractor": option.get("generated_distractor", False)
            })
            if option.get("correct", False):
                correct_option = idx
        
        return {
            "question_id": question.get("question_id", ""),
            "chapter": chapter,
            "video": video,
            "question_text": question.get("question_text", ""),
            "options": mapped_options,
            "correct_option": correct_option,
            "explanation": question.get("reasoning") or question.get("explanation", ""),
            "source_excerpt": question.get("source_excerpt"),
            "confidence": question.get("confidence", 0.0),
            "auto_ready": question.get("auto_ready", False)
        }
    
    def validate_unified_lesson(self, unified: Dict, lesson_name: str) -> bool:
        """Validate unified lesson structure."""
        errors = []
        
        # Check required fields
        if not unified.get("summary_bullets"):
            errors.append("summary_bullets is empty")
        if not unified.get("summary_markdown"):
            errors.append("summary_markdown is empty")
        if not isinstance(unified.get("quizzes"), list):
            errors.append("quizzes must be an array")
            
        # Validate chapter/video match folder name
        try:
            expected_chapter = int(lesson_name.split("_")[0].replace("Chapter", ""))
            expected_video = int(lesson_name.split("_")[1].replace("video", ""))
            
            if unified.get("chapter") != expected_chapter:
                errors.append(f"chapter mismatch: {unified.get('chapter')} != {expected_chapter}")
            if unified.get("video") != expected_video:
                errors.append(f"video mismatch: {unified.get('video')} != {expected_video}")
        except Exception as e:
            errors.append(f"Invalid lesson_name format: {lesson_name}")
        
        # Validate quiz questions
        for idx, quiz in enumerate(unified.get("quizzes", [])):
            if quiz.get("chapter") != unified.get("chapter"):
                errors.append(f"Quiz {idx} chapter mismatch")
            if quiz.get("video") != unified.get("video"):
                errors.append(f"Quiz {idx} video mismatch")
        
        if errors:
            logger.error(f"Validation failed for {lesson_name}: {', '.join(errors)}")
            self.error_log.append({
                "lesson": lesson_name,
                "error": f"Validation errors: {', '.join(errors)}"
            })
            return False
            
        return True
    
    def build_unified_lesson(self, lesson_name: str) -> Optional[Dict]:
        """Build unified lesson JSON from content and quiz."""
        # Load content
        content = self.load_content(lesson_name)
        if not content:
            self.stats["errors"] += 1
            return None
        
        # Load quiz (may not exist)
        quiz_data = self.load_quiz(lesson_name)
        
        # Map content fields
        chapter = content.get("chapter")
        video = content.get("video")
        bullets = content.get("bullets", [])
        
        # Generate summary_markdown from bullets
        summary_markdown = "\n".join([f"- {bullet}" for bullet in bullets])
        
        # Build unified structure
        unified = {
            "chapter": chapter,
            "video": video,
            "title": content.get("title", ""),
            "summary_bullets": bullets,
            "summary_markdown": summary_markdown,
            "video_url": content.get("video_url"),  # Usually null
            "duration_seconds": content.get("video_duration_sec"),  # May be null
            "source_pages": content.get("source_pages"),
            "content_source": content.get("content_source"),
            "generated_at": content.get("generated_at"),
            "quizzes": []
        }
        
        # Map quiz questions
        if quiz_data and quiz_data.get("questions"):
            for question in quiz_data["questions"]:
                mapped_q = self.map_quiz_question(question, chapter, video)
                unified["quizzes"].append(mapped_q)
            
            self.stats["lessons_with_quizzes"] += 1
            self.stats["total_quiz_questions"] += len(unified["quizzes"])
        else:
            self.stats["lessons_without_quizzes"] += 1
        
        # Validate
        if not self.validate_unified_lesson(unified, lesson_name):
            self.stats["errors"] += 1
            return None
        
        self.stats["lessons_processed"] += 1
        return unified
    
    def write_unified_lesson(self, lesson_name: str, unified: Dict):
        """Write unified lesson JSON to file."""
        output_path = self.output_dir / f"{lesson_name}.json"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(unified, f, indent=2, ensure_ascii=False)
            logger.info(f"Written: {output_path.name}")
            self.stats["files_written"] += 1
        except Exception as e:
            logger.error(f"Error writing {lesson_name}: {e}")
            self.error_log.append({
                "lesson": lesson_name,
                "error": f"Failed to write file: {str(e)}"
            })
            self.stats["errors"] += 1
    
    def write_logs(self):
        """Write log files."""
        # Error log
        error_log_path = self.logs_dir / "unified_builder_errors.log"
        with open(error_log_path, 'w', encoding='utf-8') as f:
            for error in self.error_log:
                f.write(f"{error['lesson']}: {error['error']}\n")
        
        # Summary JSON
        summary_path = self.logs_dir / "unified_builder_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        
        logger.info(f"Logs written to {self.logs_dir}")
    
    def print_dry_run_sample(self, lesson_name: str):
        """Print sample unified JSON for dry run."""
        unified = self.build_unified_lesson(lesson_name)
        if unified:
            print("\n" + "="*80)
            print(f"SAMPLE: {lesson_name}")
            print("="*80)
            print(json.dumps(unified, indent=2))
            print("="*80 + "\n")
        else:
            print(f"\nERROR: Could not build sample for {lesson_name}\n")
    
    def print_chapter_counts(self, lessons: List[str]):
        """Print counts per chapter."""
        chapter_counts = {}
        for lesson_name in lessons:
            chapter = lesson_name.split("_")[0]
            chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1
        
        print("\nLessons per chapter:")
        for chapter in sorted(chapter_counts.keys()):
            print(f"  {chapter}: {chapter_counts[chapter]} lessons")
        print()
    
    def run(self, dry_run: bool = False):
        """Execute the unified lesson builder."""
        logger.info("Starting Unified Lesson Builder")
        
        # Setup
        self.setup_directories()
        
        # Find all lessons
        lessons = self.find_lessons()
        logger.info(f"Found {len(lessons)} lessons")
        
        if not lessons:
            logger.error("No lessons found!")
            return
        
        # Dry run: show sample
        if dry_run:
            if "Chapter01_video01" in lessons:
                self.print_dry_run_sample("Chapter01_video01")
            else:
                self.print_dry_run_sample(lessons[0])
            
            self.print_chapter_counts(lessons)
            
            response = input("Proceed with full build? (yes/no): ").strip().lower()
            if response != "yes":
                logger.info("Build cancelled by user")
                return
        
        # Build all unified lessons
        for lesson_name in lessons:
            logger.info(f"Processing: {lesson_name}")
            unified = self.build_unified_lesson(lesson_name)
            if unified:
                self.write_unified_lesson(lesson_name, unified)
        
        # Write logs
        self.write_logs()
        
        # Print summary
        print("\n" + "="*80)
        print("UNIFIED LESSON BUILDER SUMMARY")
        print("="*80)
        for key, value in self.stats.items():
            print(f"  {key}: {value}")
        print("="*80 + "\n")
        
        logger.info("Unified Lesson Builder completed")


def main():
    """Main entry point."""
    import sys
    
    workspace = os.getcwd()
    builder = UnifiedLessonBuilder(workspace)
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    builder.run(dry_run=dry_run)


if __name__ == "__main__":
    main()
