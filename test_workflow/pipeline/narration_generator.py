"""
Narration Generator Module
Generates narration with source citations and spurious caution rejection.
Each video: 180-240 words, per-slide 50-80 words.
Requires >=3 factual references from markdown/PDF per video.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import call_llm, print_info, print_success, print_error


@dataclass
class NarrationSegment:
    """Narration for a single slide with citations"""
    slide_number: int
    text: str
    word_count: int
    source_tags: List[Dict[str, str]]  # [{"type": "md", "ref": "chapter_01.md#subsection"}]
    key_terms_used: List[str]
    has_contractor_caution: bool = False
    caution_verified: bool = False


@dataclass
class NarrationResult:
    """Complete narration for a video"""
    video_id: str
    chapter_id: str
    title: str
    segments: List[NarrationSegment]
    total_word_count: int
    factual_references: int
    review_questions: List[str]
    passes_depth_gate: bool
    passes_caution_gate: bool
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class NarrationGenerator:
    """Generates narration with source citations"""
    
    # Caution keywords to detect
    CAUTION_KEYWORDS = [
        'caution', 'warning', 'contractor', 'safety', 'specification',
        'subsection', 'standard', 'compliance', 'requirement', 'must'
    ]
    
    # PDF spec reference pattern
    SPEC_PATTERN = re.compile(r'(subsection|section|spec)\s*(\d+\.?\d*)', re.IGNORECASE)
    
    NARRATION_PROMPT = """You are a professional narrator creating educational voiceover for a GDOT highway plan reading course.

═══════════════════════════════════════════════════════════════════════════════
VIDEO INFORMATION
═══════════════════════════════════════════════════════════════════════════════

Video ID: {video_id}
Chapter: {chapter_id}
Title: {title}
Description: {description}

═══════════════════════════════════════════════════════════════════════════════
SLIDE CONTENT
═══════════════════════════════════════════════════════════════════════════════

{slide_content}

═══════════════════════════════════════════════════════════════════════════════
SOURCE MATERIAL
═══════════════════════════════════════════════════════════════════════════════

{source_material}

═══════════════════════════════════════════════════════════════════════════════
REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

1. WORD COUNT
   - Total video: 180-240 words
   - Per slide: 50-80 words
   - Number of slides: {slide_count}

2. SOURCE CITATIONS (CRITICAL)
   - Each slide must reference at least 1 fact from the source material
   - Total video must have at least 3 factual references
   - Tag each fact with its source using: [source:md:filename#section] or [source:pdf:page]
   - Example: "The cover sheet contains project identification [source:md:chapter_01.md#cover-sheet]"

3. CONTRACTOR CAUTIONS
   - ONLY include cautions/warnings if they appear EXACTLY in the source material
   - Do NOT add generic safety advice
   - If including a caution, cite the exact source: [source:pdf:page:X]
   - If no cautions in source, do NOT add any

4. STYLE
   - Professional, educational tone
   - Reference visuals: "As shown in the diagram...", "Notice how..."
   - Clear explanations suitable for training
   - Include at least 2 review questions at the end

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (JSON)
═══════════════════════════════════════════════════════════════════════════════

Return ONLY valid JSON:

{{
    "narration": [
        {{
            "slide_number": 1,
            "text": "Welcome to our lesson on cover sheets. The cover sheet is the first page of any construction plan set and contains critical project identification information [source:md:chapter_01.md#cover-sheet]. As shown in the diagram, it includes the project number, route information, and county designation.",
            "source_tags": [
                {{"type": "md", "ref": "chapter_01.md#cover-sheet"}}
            ],
            "key_terms": ["cover sheet", "project identification"]
        }},
        ...
    ],
    "review_questions": [
        "What information is typically found on a cover sheet?",
        "How do you identify the project limits from the cover sheet?"
    ]
}}
"""

    def __init__(self, output_dir: Path, pdf_path: Optional[Path] = None):
        self.output_dir = output_dir
        self.pdf_path = pdf_path
        self._pdf_text_cache = None
    
    def generate_narration(
        self,
        video_id: str,
        chapter_id: str,
        title: str,
        description: str,
        slides: List[Dict],
        source_content: str,
        source_file: str = ""
    ) -> NarrationResult:
        """Generate narration for a video with citations"""
        
        # Format slide content
        slide_content = self._format_slides(slides)
        
        # Build prompt
        prompt = self.NARRATION_PROMPT.format(
            video_id=video_id,
            chapter_id=chapter_id,
            title=title,
            description=description,
            slide_content=slide_content,
            source_material=source_content[:4000],
            slide_count=len(slides)
        )
        
        print_info(f"Generating narration for: {video_id}")
        
        # Call LLM
        response, tokens = call_llm(prompt, max_tokens=2000, temperature=0.4)
        print_info(f"LLM tokens used: {tokens}")
        
        # Parse response
        segments, review_questions = self._parse_response(response, len(slides))
        
        # Verify cautions
        has_unverified_cautions = False
        for segment in segments:
            if segment.has_contractor_caution:
                segment.caution_verified = self._verify_caution(
                    segment.text, source_content
                )
                if not segment.caution_verified:
                    has_unverified_cautions = True
                    print_error(f"Slide {segment.slide_number}: Unverified caution detected")
        
        # Calculate totals
        total_words = sum(s.word_count for s in segments)
        factual_refs = sum(len(s.source_tags) for s in segments)
        
        # Check gates
        passes_depth = factual_refs >= 3 and len(review_questions) >= 2
        passes_caution = not has_unverified_cautions
        
        result = NarrationResult(
            video_id=video_id,
            chapter_id=chapter_id,
            title=title,
            segments=segments,
            total_word_count=total_words,
            factual_references=factual_refs,
            review_questions=review_questions,
            passes_depth_gate=passes_depth,
            passes_caution_gate=passes_caution
        )
        
        # Print summary
        print_info(f"Total words: {total_words} (target: 180-240)")
        print_info(f"Factual references: {factual_refs} (minimum: 3)")
        print_info(f"Review questions: {len(review_questions)} (minimum: 2)")
        
        if passes_depth:
            print_success("Narrative depth gate: PASSED")
        else:
            print_error("Narrative depth gate: FAILED")
        
        if passes_caution:
            print_success("No-spurious-caution gate: PASSED")
        else:
            print_error("No-spurious-caution gate: FAILED")
        
        return result
    
    def _format_slides(self, slides: List[Dict]) -> str:
        """Format slides for the prompt"""
        lines = []
        for i, slide in enumerate(slides, 1):
            lines.append(f"Slide {i}: {slide.get('title', f'Slide {i}')}")
            lines.append(f"  Visual Goal: {slide.get('visual_goal', 'N/A')}")
            if 'narration_text' in slide and slide['narration_text']:
                lines.append(f"  Draft Narration: {slide['narration_text']}")
            lines.append("")
        return "\n".join(lines)
    
    def _parse_response(
        self,
        response: str,
        expected_slides: int
    ) -> tuple[List[NarrationSegment], List[str]]:
        """Parse LLM response into narration segments"""
        
        segments = []
        review_questions = []
        
        try:
            # Clean up response
            response_clean = response.strip()
            if response_clean.startswith("```"):
                response_clean = re.sub(r'^```\w*\n?', '', response_clean)
                response_clean = re.sub(r'\n?```$', '', response_clean)
            
            data = json.loads(response_clean)
            
            for item in data.get("narration", []):
                text = item.get("text", "")
                
                # Extract source tags from text
                source_tags = item.get("source_tags", [])
                
                # Also parse inline [source:...] tags
                inline_tags = re.findall(r'\[source:(md|pdf):([^\]]+)\]', text)
                for tag_type, tag_ref in inline_tags:
                    source_tags.append({"type": tag_type, "ref": tag_ref})
                
                # Remove inline tags from text for clean narration
                clean_text = re.sub(r'\[source:[^\]]+\]', '', text).strip()
                clean_text = re.sub(r'\s+', ' ', clean_text)  # Normalize whitespace
                
                # Check for cautions
                has_caution = any(kw in text.lower() for kw in self.CAUTION_KEYWORDS)
                
                segments.append(NarrationSegment(
                    slide_number=item.get("slide_number", len(segments) + 1),
                    text=clean_text,
                    word_count=len(clean_text.split()),
                    source_tags=source_tags,
                    key_terms_used=item.get("key_terms", []),
                    has_contractor_caution=has_caution
                ))
            
            review_questions = data.get("review_questions", [])
            
        except json.JSONDecodeError as e:
            print_error(f"Failed to parse narration JSON: {e}")
            # Create fallback narration
            segments = self._create_fallback_narration(expected_slides)
        
        return segments, review_questions
    
    def _create_fallback_narration(self, slide_count: int) -> List[NarrationSegment]:
        """Create fallback narration if LLM fails"""
        segments = []
        for i in range(1, slide_count + 1):
            segments.append(NarrationSegment(
                slide_number=i,
                text=f"This slide covers important concepts in highway plan reading. Please refer to the visual content.",
                word_count=15,
                source_tags=[],
                key_terms_used=[]
            ))
        return segments
    
    def _verify_caution(self, text: str, source_content: str) -> bool:
        """Verify that a caution exists in the source material"""
        
        # Look for specification references
        spec_matches = self.SPEC_PATTERN.findall(text)
        if spec_matches:
            for spec_type, spec_num in spec_matches:
                pattern = f"{spec_type}\\s*{spec_num}"
                if re.search(pattern, source_content, re.IGNORECASE):
                    return True
        
        # Look for keyword phrases in source
        caution_phrases = re.findall(
            r'(caution|warning|must|required|shall)[\s:]+([^.!?]+)',
            text,
            re.IGNORECASE
        )
        
        for _, phrase in caution_phrases:
            # Check if similar phrase exists in source
            words = phrase.lower().split()[:5]  # First 5 words
            if len(words) >= 3:
                pattern = r'\b' + r'\s+'.join(words[:3]) + r'\b'
                if re.search(pattern, source_content.lower()):
                    return True
        
        return False
    
    def save_narration(self, result: NarrationResult) -> Path:
        """Save narration to JSON file"""
        video_dir = self.output_dir / result.chapter_id / result.video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        
        narration_file = video_dir / "narration.json"
        
        data = {
            "video_id": result.video_id,
            "chapter_id": result.chapter_id,
            "title": result.title,
            "total_word_count": result.total_word_count,
            "factual_references": result.factual_references,
            "passes_depth_gate": result.passes_depth_gate,
            "passes_caution_gate": result.passes_caution_gate,
            "review_questions": result.review_questions,
            "created_at": result.created_at,
            "segments": [
                {
                    "slide_number": seg.slide_number,
                    "text": seg.text,
                    "word_count": seg.word_count,
                    "source_tags": seg.source_tags,
                    "key_terms_used": seg.key_terms_used,
                    "has_contractor_caution": seg.has_contractor_caution,
                    "caution_verified": seg.caution_verified
                }
                for seg in result.segments
            ]
        }
        
        narration_file.write_text(json.dumps(data, indent=2))
        print_success(f"Narration saved: {narration_file}")
        
        return narration_file
    
    def load_narration(self, narration_file: Path) -> NarrationResult:
        """Load narration from JSON file"""
        data = json.loads(narration_file.read_text())
        
        segments = []
        for seg_data in data.get("segments", []):
            segments.append(NarrationSegment(
                slide_number=seg_data["slide_number"],
                text=seg_data["text"],
                word_count=seg_data["word_count"],
                source_tags=seg_data.get("source_tags", []),
                key_terms_used=seg_data.get("key_terms_used", []),
                has_contractor_caution=seg_data.get("has_contractor_caution", False),
                caution_verified=seg_data.get("caution_verified", False)
            ))
        
        return NarrationResult(
            video_id=data["video_id"],
            chapter_id=data["chapter_id"],
            title=data["title"],
            segments=segments,
            total_word_count=data["total_word_count"],
            factual_references=data["factual_references"],
            review_questions=data.get("review_questions", []),
            passes_depth_gate=data["passes_depth_gate"],
            passes_caution_gate=data["passes_caution_gate"],
            created_at=data.get("created_at", "")
        )


def generate_narration_from_plan(
    plan_path: Path,
    source_content_path: Path,
    output_dir: Path
) -> NarrationResult:
    """Convenience function to generate narration from a plan"""
    
    plan_data = json.loads(plan_path.read_text())
    source_content = source_content_path.read_text() if source_content_path.exists() else ""
    
    generator = NarrationGenerator(output_dir)
    
    result = generator.generate_narration(
        video_id=plan_data["video_id"],
        chapter_id=plan_data["chapter_id"],
        title=plan_data["title"],
        description=plan_data["description"],
        slides=plan_data["slides"],
        source_content=source_content,
        source_file=str(source_content_path)
    )
    
    generator.save_narration(result)
    
    return result


if __name__ == "__main__":
    print("Narration Generator - Run via orchestrator scripts")

