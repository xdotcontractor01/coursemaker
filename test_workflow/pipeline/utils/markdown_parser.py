"""
Markdown Parser Module
Parses chapter markdown files with YAML frontmatter support.
Extracts: title, subsections (H2), key_terms, learning_objectives, figure references.
"""

import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any


@dataclass
class FigureReference:
    """Reference to a PDF figure or local image"""
    figure_id: str  # e.g., "fig_1_1"
    pdf_page: Optional[int] = None
    pdf_figure_num: Optional[str] = None  # e.g., "1-1"
    local_path: Optional[str] = None
    caption: Optional[str] = None
    line_number: int = 0


@dataclass
class Subsection:
    """A subsection (H2) within a chapter"""
    title: str
    content: str
    line_start: int
    line_end: int
    figure_refs: List[FigureReference] = field(default_factory=list)
    has_deep_example: bool = False  # Contains step-by-step or Q&A


@dataclass
class ChapterContent:
    """Parsed chapter content with metadata"""
    chapter_id: str
    title: str
    subsections: List[Subsection]
    key_terms: List[str]
    learning_objectives: List[str]
    figure_refs: List[FigureReference]
    raw_content: str
    source_file: str
    derived_from_pdf: bool = False
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def subsection_count(self) -> int:
        return len(self.subsections)
    
    def get_video_count_recommendation(self) -> int:
        """Recommend number of videos based on subsection count"""
        if self.subsection_count >= 6:
            return 5
        elif self.subsection_count >= 4:
            return 4
        else:
            return 3


class MarkdownParser:
    """Parser for chapter markdown files with YAML frontmatter"""
    
    # Pattern for YAML frontmatter
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    # Pattern for H1 title
    H1_PATTERN = re.compile(r'^#\s+(.+)$', re.MULTILINE)
    
    # Pattern for H2 subsections
    H2_PATTERN = re.compile(r'^##\s+(.+)$', re.MULTILINE)
    
    # Pattern for figure references: pdf_fig: p:XX fig:Y or embed_figure: page:X, fig:Y
    PDF_FIG_PATTERN = re.compile(
        r'(?:pdf_fig|embed_figure):\s*(?:p(?:age)?:?\s*(\d+))?,?\s*(?:fig(?:ure)?:?\s*([\d\-]+))?',
        re.IGNORECASE
    )
    
    # Pattern for local figure reference: ![caption](path)
    LOCAL_FIG_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    
    # Pattern for deep_example blocks
    DEEP_EXAMPLE_PATTERN = re.compile(r'```deep_example|<deep_example>', re.IGNORECASE)
    
    def __init__(self, figures_base_dir: Optional[Path] = None):
        self.figures_base_dir = figures_base_dir or Path("figures")
    
    def parse_file(self, filepath: Path) -> ChapterContent:
        """Parse a markdown file and return structured content"""
        if not filepath.exists():
            raise FileNotFoundError(f"Markdown file not found: {filepath}")
        
        content = filepath.read_text(encoding='utf-8')
        return self.parse_content(content, str(filepath))
    
    def parse_content(self, content: str, source_file: str = "unknown") -> ChapterContent:
        """Parse markdown content string"""
        lines = content.split('\n')
        
        # Extract frontmatter
        frontmatter, content_without_frontmatter = self._extract_frontmatter(content)
        
        # Extract chapter ID from filename or frontmatter
        chapter_id = frontmatter.get('chapter_id', self._extract_chapter_id(source_file))
        
        # Extract title (H1)
        title = self._extract_title(content_without_frontmatter, frontmatter)
        
        # Extract subsections
        subsections = self._extract_subsections(content_without_frontmatter, lines)
        
        # Extract key terms and learning objectives
        key_terms = frontmatter.get('key_terms', [])
        learning_objectives = frontmatter.get('learning_objectives', [])
        
        # If not in frontmatter, try to extract from content
        if not key_terms:
            key_terms = self._extract_key_terms(content_without_frontmatter)
        if not learning_objectives:
            learning_objectives = self._extract_learning_objectives(content_without_frontmatter)
        
        # Collect all figure references
        figure_refs = self._extract_all_figure_refs(content_without_frontmatter, lines)
        
        # Check if derived from PDF
        derived_from_pdf = frontmatter.get('derived_from_pdf', False)
        
        return ChapterContent(
            chapter_id=chapter_id,
            title=title,
            subsections=subsections,
            key_terms=key_terms if isinstance(key_terms, list) else [key_terms],
            learning_objectives=learning_objectives if isinstance(learning_objectives, list) else [learning_objectives],
            figure_refs=figure_refs,
            raw_content=content,
            source_file=source_file,
            derived_from_pdf=derived_from_pdf,
            frontmatter=frontmatter
        )
    
    def _extract_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter from content"""
        match = self.FRONTMATTER_PATTERN.match(content)
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1)) or {}
                content_without = content[match.end():]
                return frontmatter, content_without
            except yaml.YAMLError:
                return {}, content
        return {}, content
    
    def _extract_chapter_id(self, source_file: str) -> str:
        """Extract chapter ID from filename (e.g., chapter_01.md -> chapter_01)"""
        filename = Path(source_file).stem
        # Match patterns like chapter_01, ch01, chapter1
        match = re.match(r'(chapter[_\s]?(\d+)|ch(\d+))', filename, re.IGNORECASE)
        if match:
            num = match.group(2) or match.group(3)
            return f"chapter_{int(num):02d}"
        return filename
    
    def _extract_title(self, content: str, frontmatter: Dict) -> str:
        """Extract chapter title from H1 or frontmatter"""
        if 'title' in frontmatter:
            return frontmatter['title']
        
        match = self.H1_PATTERN.search(content)
        if match:
            return match.group(1).strip()
        
        return "Untitled Chapter"
    
    def _extract_subsections(self, content: str, lines: List[str]) -> List[Subsection]:
        """Extract all H2 subsections with their content"""
        subsections = []
        
        # Find all H2 headers with their positions
        h2_matches = list(self.H2_PATTERN.finditer(content))
        
        if not h2_matches:
            # No subsections, treat entire content as one section
            return [Subsection(
                title="Main Content",
                content=content,
                line_start=1,
                line_end=len(lines),
                figure_refs=self._extract_figure_refs(content, 1),
                has_deep_example=bool(self.DEEP_EXAMPLE_PATTERN.search(content))
            )]
        
        for i, match in enumerate(h2_matches):
            title = match.group(1).strip()
            start_pos = match.end()
            
            # Find end position (start of next H2 or end of content)
            if i + 1 < len(h2_matches):
                end_pos = h2_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            section_content = content[start_pos:end_pos].strip()
            
            # Calculate line numbers
            line_start = content[:match.start()].count('\n') + 1
            line_end = content[:end_pos].count('\n') + 1
            
            # Extract figure refs for this section
            figure_refs = self._extract_figure_refs(section_content, line_start)
            
            # Check for deep examples
            has_deep_example = bool(self.DEEP_EXAMPLE_PATTERN.search(section_content))
            
            subsections.append(Subsection(
                title=title,
                content=section_content,
                line_start=line_start,
                line_end=line_end,
                figure_refs=figure_refs,
                has_deep_example=has_deep_example
            ))
        
        return subsections
    
    def _extract_figure_refs(self, content: str, base_line: int = 1) -> List[FigureReference]:
        """Extract figure references from content"""
        refs = []
        
        # Find PDF figure references
        for match in self.PDF_FIG_PATTERN.finditer(content):
            page = int(match.group(1)) if match.group(1) else None
            fig_num = match.group(2) if match.group(2) else None
            
            line_num = base_line + content[:match.start()].count('\n')
            
            fig_id = f"fig_{fig_num.replace('-', '_')}" if fig_num else f"fig_p{page}"
            
            refs.append(FigureReference(
                figure_id=fig_id,
                pdf_page=page,
                pdf_figure_num=fig_num,
                line_number=line_num
            ))
        
        # Find local image references
        for match in self.LOCAL_FIG_PATTERN.finditer(content):
            caption = match.group(1)
            path = match.group(2)
            line_num = base_line + content[:match.start()].count('\n')
            
            # Generate figure ID from path
            fig_id = Path(path).stem
            
            refs.append(FigureReference(
                figure_id=fig_id,
                local_path=path,
                caption=caption,
                line_number=line_num
            ))
        
        return refs
    
    def _extract_all_figure_refs(self, content: str, lines: List[str]) -> List[FigureReference]:
        """Extract all figure references from entire content"""
        return self._extract_figure_refs(content, 1)
    
    def _extract_key_terms(self, content: str) -> List[str]:
        """Extract key terms from content (look for key_terms: or **bold** definitions)"""
        terms = []
        
        # Look for key_terms section
        match = re.search(r'key[_\s]?terms?:\s*\n((?:[-*]\s+.+\n?)+)', content, re.IGNORECASE)
        if match:
            for line in match.group(1).split('\n'):
                term = re.sub(r'^[-*]\s+', '', line).strip()
                if term:
                    terms.append(term)
        
        # Also extract bold terms as potential key terms (limited to avoid noise)
        bold_terms = re.findall(r'\*\*([^*]+)\*\*', content)
        for term in bold_terms[:10]:  # Limit to first 10
            if term not in terms and len(term.split()) <= 4:  # Max 4 words
                terms.append(term)
        
        return terms
    
    def _extract_learning_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from content"""
        objectives = []
        
        # Look for learning_objectives section
        match = re.search(
            r'learning[_\s]?objectives?:\s*\n((?:[-*\d.]\s+.+\n?)+)',
            content,
            re.IGNORECASE
        )
        if match:
            for line in match.group(1).split('\n'):
                obj = re.sub(r'^[-*\d.]+\s+', '', line).strip()
                if obj:
                    objectives.append(obj)
        
        return objectives


def parse_chapter_markdown(filepath: Path, figures_dir: Optional[Path] = None) -> ChapterContent:
    """Convenience function to parse a chapter markdown file"""
    parser = MarkdownParser(figures_base_dir=figures_dir)
    return parser.parse_file(filepath)


if __name__ == "__main__":
    # Test with a sample file
    import sys
    
    if len(sys.argv) > 1:
        test_file = Path(sys.argv[1])
        if test_file.exists():
            content = parse_chapter_markdown(test_file)
            print(f"Chapter: {content.chapter_id}")
            print(f"Title: {content.title}")
            print(f"Subsections: {content.subsection_count}")
            for sub in content.subsections:
                print(f"  - {sub.title} (lines {sub.line_start}-{sub.line_end})")
            print(f"Key Terms: {content.key_terms}")
            print(f"Learning Objectives: {content.learning_objectives}")
            print(f"Figure References: {len(content.figure_refs)}")
            print(f"Recommended Videos: {content.get_video_count_recommendation()}")
        else:
            print(f"File not found: {test_file}")
    else:
        print("Usage: python markdown_parser.py <chapter_file.md>")


