"""
Curriculum Parser Module
Parses chapter markdown and splits into video micro-topics.
Generates chapters.json and videos_manifest.json.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from .utils.markdown_parser import (
    MarkdownParser,
    ChapterContent,
    Subsection,
    FigureReference,
    parse_chapter_markdown
)


@dataclass
class VideoTopic:
    """A micro-topic for a single video (2-3 minutes)"""
    video_id: str
    chapter_id: str
    title: str
    description: str
    subsections_covered: List[str]  # Subsection titles
    source_line_refs: List[tuple[int, int]]  # (start, end) line numbers
    pdf_page_refs: List[int]
    figure_refs: List[str]  # Figure IDs
    estimated_duration_seconds: int  # Target: 120-180 seconds
    target_word_count: int  # Target: 180-240 words
    target_slide_count: int  # Target: 4-6 slides
    has_worked_example: bool = False
    order: int = 0


@dataclass
class ChapterManifest:
    """Manifest for a single chapter"""
    chapter_id: str
    title: str
    source_file: str
    derived_from_pdf: bool
    video_count: int
    videos: List[VideoTopic]
    key_terms: List[str]
    learning_objectives: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CurriculumManifest:
    """Full curriculum manifest for all chapters"""
    project_name: str
    total_chapters: int
    total_videos: int
    chapters: List[ChapterManifest]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CurriculumParser:
    """Parses chapter markdown into video micro-topics"""
    
    # Target durations and counts
    TARGET_VIDEO_DURATION = 150  # 2.5 minutes in seconds
    TARGET_WORDS_PER_VIDEO = 210  # Middle of 180-240 range
    TARGET_SLIDES_PER_VIDEO = 5  # Middle of 4-6 range
    TARGET_WORDS_PER_SLIDE = 65  # ~50-80 words per slide
    
    def __init__(self, input_dir: Path, output_dir: Path, figures_dir: Optional[Path] = None):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.figures_dir = figures_dir or input_dir.parent / "figures"
        self.markdown_parser = MarkdownParser(figures_base_dir=self.figures_dir)
    
    def parse_chapter(self, chapter_file: Path) -> ChapterManifest:
        """Parse a single chapter markdown file into video topics"""
        # Parse the markdown
        chapter = self.markdown_parser.parse_file(chapter_file)
        
        # Split into video topics
        videos = self._split_into_videos(chapter)
        
        return ChapterManifest(
            chapter_id=chapter.chapter_id,
            title=chapter.title,
            source_file=str(chapter_file),
            derived_from_pdf=chapter.derived_from_pdf,
            video_count=len(videos),
            videos=videos,
            key_terms=chapter.key_terms,
            learning_objectives=chapter.learning_objectives
        )
    
    def parse_all_chapters(self, project_name: str = "GDOT Plan Reading") -> CurriculumManifest:
        """Parse all chapter markdown files in input directory"""
        chapters = []
        total_videos = 0
        
        # Find all chapter files
        chapter_files = sorted(self.input_dir.glob("chapter_*.md"))
        
        if not chapter_files:
            raise FileNotFoundError(f"No chapter files found in {self.input_dir}")
        
        for chapter_file in chapter_files:
            manifest = self.parse_chapter(chapter_file)
            chapters.append(manifest)
            total_videos += manifest.video_count
        
        return CurriculumManifest(
            project_name=project_name,
            total_chapters=len(chapters),
            total_videos=total_videos,
            chapters=chapters
        )
    
    def _split_into_videos(self, chapter: ChapterContent) -> List[VideoTopic]:
        """Split chapter content into video micro-topics"""
        videos = []
        subsections = chapter.subsections
        
        # Determine video count based on subsection count
        video_count = chapter.get_video_count_recommendation()
        
        # Handle special case: subsections with deep examples get their own video
        deep_example_sections = [s for s in subsections if s.has_deep_example]
        regular_sections = [s for s in subsections if not s.has_deep_example]
        
        # First, create videos for deep example sections
        for section in deep_example_sections:
            video = self._create_video_from_sections(
                chapter_id=chapter.chapter_id,
                sections=[section],
                order=len(videos) + 1,
                is_worked_example=True
            )
            videos.append(video)
        
        # Distribute remaining sections across remaining video slots
        remaining_video_slots = max(video_count - len(deep_example_sections), 1)
        
        if regular_sections:
            section_groups = self._distribute_sections(regular_sections, remaining_video_slots)
            
            for group in section_groups:
                video = self._create_video_from_sections(
                    chapter_id=chapter.chapter_id,
                    sections=group,
                    order=len(videos) + 1,
                    is_worked_example=False
                )
                videos.append(video)
        
        # Re-number videos
        for i, video in enumerate(videos):
            video.order = i + 1
            video.video_id = f"{chapter.chapter_id}_video_{i+1:02d}"
        
        return videos
    
    def _distribute_sections(self, sections: List[Subsection], num_groups: int) -> List[List[Subsection]]:
        """Distribute sections evenly across groups"""
        if not sections:
            return []
        
        if num_groups >= len(sections):
            # Each section gets its own video
            return [[s] for s in sections]
        
        # Distribute sections evenly
        groups = [[] for _ in range(num_groups)]
        for i, section in enumerate(sections):
            groups[i % num_groups].append(section)
        
        return [g for g in groups if g]  # Remove empty groups
    
    def _create_video_from_sections(
        self,
        chapter_id: str,
        sections: List[Subsection],
        order: int,
        is_worked_example: bool
    ) -> VideoTopic:
        """Create a VideoTopic from one or more subsections"""
        
        # Combine titles for video title
        if len(sections) == 1:
            title = sections[0].title
        else:
            # Create a combined title
            titles = [s.title for s in sections]
            if len(titles) <= 2:
                title = " & ".join(titles)
            else:
                title = f"{titles[0]} and Related Topics"
        
        if is_worked_example:
            title = f"Worked Example: {title}"
        
        # Collect line references
        line_refs = [(s.line_start, s.line_end) for s in sections]
        
        # Collect figure references
        figure_refs = []
        pdf_pages = set()
        for section in sections:
            for fig in section.figure_refs:
                figure_refs.append(fig.figure_id)
                if fig.pdf_page:
                    pdf_pages.add(fig.pdf_page)
        
        # Generate description
        description = self._generate_video_description(sections, is_worked_example)
        
        return VideoTopic(
            video_id=f"{chapter_id}_video_{order:02d}",
            chapter_id=chapter_id,
            title=title,
            description=description,
            subsections_covered=[s.title for s in sections],
            source_line_refs=line_refs,
            pdf_page_refs=sorted(pdf_pages),
            figure_refs=figure_refs,
            estimated_duration_seconds=self.TARGET_VIDEO_DURATION,
            target_word_count=self.TARGET_WORDS_PER_VIDEO,
            target_slide_count=self.TARGET_SLIDES_PER_VIDEO,
            has_worked_example=is_worked_example,
            order=order
        )
    
    def _generate_video_description(self, sections: List[Subsection], is_worked_example: bool) -> str:
        """Generate a brief description for the video"""
        if is_worked_example:
            return f"Step-by-step walkthrough of {sections[0].title.lower()} concepts with practical examples."
        
        topics = [s.title for s in sections]
        if len(topics) == 1:
            return f"Learn about {topics[0].lower()} in highway plan reading."
        else:
            return f"Covers {', '.join(topics[:-1])} and {topics[-1]} in highway plan reading."
    
    def save_manifests(self, curriculum: CurriculumManifest) -> tuple[Path, Path]:
        """Save chapters.json and videos_manifest.json"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save chapters.json (simplified chapter info)
        chapters_data = {
            "project_name": curriculum.project_name,
            "total_chapters": curriculum.total_chapters,
            "total_videos": curriculum.total_videos,
            "created_at": curriculum.created_at,
            "chapters": [
                {
                    "chapter_id": ch.chapter_id,
                    "title": ch.title,
                    "source_file": ch.source_file,
                    "video_count": ch.video_count,
                    "key_terms": ch.key_terms,
                    "learning_objectives": ch.learning_objectives
                }
                for ch in curriculum.chapters
            ]
        }
        
        chapters_file = self.output_dir / "chapters.json"
        chapters_file.write_text(json.dumps(chapters_data, indent=2))
        
        # Save videos_manifest.json (detailed video info)
        videos_data = {
            "project_name": curriculum.project_name,
            "total_videos": curriculum.total_videos,
            "created_at": curriculum.created_at,
            "videos": []
        }
        
        for chapter in curriculum.chapters:
            for video in chapter.videos:
                video_entry = {
                    "video_id": video.video_id,
                    "chapter_id": video.chapter_id,
                    "title": video.title,
                    "description": video.description,
                    "subsections_covered": video.subsections_covered,
                    "source_line_refs": video.source_line_refs,
                    "pdf_page_refs": video.pdf_page_refs,
                    "figure_refs": video.figure_refs,
                    "estimated_duration_seconds": video.estimated_duration_seconds,
                    "target_word_count": video.target_word_count,
                    "target_slide_count": video.target_slide_count,
                    "has_worked_example": video.has_worked_example,
                    "order": video.order,
                    "validation_status": "pending"
                }
                videos_data["videos"].append(video_entry)
        
        videos_file = self.output_dir / "videos_manifest.json"
        videos_file.write_text(json.dumps(videos_data, indent=2))
        
        return chapters_file, videos_file


def parse_curriculum(
    input_dir: Path,
    output_dir: Path,
    project_name: str = "GDOT Plan Reading"
) -> CurriculumManifest:
    """Convenience function to parse curriculum and save manifests"""
    parser = CurriculumParser(input_dir, output_dir)
    curriculum = parser.parse_all_chapters(project_name)
    parser.save_manifests(curriculum)
    return curriculum


if __name__ == "__main__":
    import sys
    
    # Default paths
    script_dir = Path(__file__).parent.parent
    input_dir = script_dir / "input_markdown"
    output_dir = script_dir / "output" / "gdot_plan_videos"
    
    if len(sys.argv) > 1:
        input_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    
    print(f"Parsing curriculum from: {input_dir}")
    print(f"Output to: {output_dir}")
    
    try:
        curriculum = parse_curriculum(input_dir, output_dir)
        print(f"\nParsed {curriculum.total_chapters} chapters with {curriculum.total_videos} videos")
        
        for chapter in curriculum.chapters:
            print(f"\n{chapter.chapter_id}: {chapter.title}")
            print(f"  Videos: {chapter.video_count}")
            for video in chapter.videos:
                print(f"    - {video.video_id}: {video.title}")
                print(f"      Subsections: {', '.join(video.subsections_covered)}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nCreate chapter markdown files in the input directory first.")
        print("Example: input_markdown/chapter_01.md")


