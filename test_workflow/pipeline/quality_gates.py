"""
Quality Gates Module
Validates generated content against quality requirements:
1. Visual Diversity Gate: >=2 animation types per slide, >=1 dynamic element
2. Narrative Depth Gate: >=3 facts/definitions, 2 review questions
3. No-Spurious-Caution Gate: Verify contractor cautions against PDF
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import print_info, print_success, print_error


@dataclass
class GateResult:
    """Result of a single quality gate check"""
    gate_name: str
    passed: bool
    score: int
    max_score: int
    details: Dict[str, Any]
    failures: List[str]
    suggestions: List[str]


@dataclass
class QualityReport:
    """Complete quality report for a video"""
    video_id: str
    chapter_id: str
    all_gates_passed: bool
    gates: List[GateResult]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "video_id": self.video_id,
            "chapter_id": self.chapter_id,
            "all_gates_passed": self.all_gates_passed,
            "created_at": self.created_at,
            "gates": [
                {
                    "gate_name": g.gate_name,
                    "passed": g.passed,
                    "score": g.score,
                    "max_score": g.max_score,
                    "details": g.details,
                    "failures": g.failures,
                    "suggestions": g.suggestions
                }
                for g in self.gates
            ]
        }


class QualityGates:
    """Quality gate validation for video generation"""
    
    # Visual diversity requirements
    MIN_ANIMATION_TYPES_PER_SLIDE = 2
    MIN_DYNAMIC_ELEMENTS = 1
    MIN_COLORS = 3
    MIN_SHAPE_TYPES = 2
    
    # Narrative depth requirements
    MIN_FACTUAL_REFS = 3
    MIN_REVIEW_QUESTIONS = 2
    MIN_WORDS_PER_SLIDE = 40
    MAX_WORDS_PER_SLIDE = 90
    
    # Dynamic element patterns
    DYNAMIC_PATTERNS = [
        'MoveAlongPath', 'add_updater', 'ValueTracker',
        'self.camera.frame.animate', 'Succession', 'always_redraw'
    ]
    
    # Animation type patterns
    ANIMATION_PATTERNS = [
        'Write', 'Create', 'FadeIn', 'FadeOut', 'GrowFrom',
        'Transform', 'ReplacementTransform', 'MoveAlongPath',
        'Indicate', 'Circumscribe', 'Flash', 'DrawBorderThenFill',
        'SpinInFromNothing', 'MoveToTarget', 'Rotate', 'ApplyMethod'
    ]
    
    # Shape patterns
    SHAPE_PATTERNS = [
        'Circle', 'Rectangle', 'Square', 'Triangle', 'Arrow',
        'Line', 'Arc', 'Polygon', 'Brace', 'NumberLine', 'Dot'
    ]
    
    # Color patterns
    COLOR_PATTERNS = [
        'BLUE', 'RED', 'GREEN', 'ORANGE', 'YELLOW', 'PURPLE',
        'TEAL', 'GOLD', 'PINK', 'MAROON', 'GRAY'
    ]
    
    def __init__(self, pdf_path: Optional[Path] = None):
        self.pdf_path = pdf_path
        self._pdf_content = None
    
    def check_all_gates(
        self,
        video_id: str,
        chapter_id: str,
        script_path: Optional[Path] = None,
        script_content: Optional[str] = None,
        narration_path: Optional[Path] = None,
        narration_data: Optional[Dict] = None
    ) -> QualityReport:
        """Run all quality gates and return combined report"""
        
        gates = []
        
        # Load content if paths provided
        if script_path and not script_content:
            script_content = script_path.read_text() if script_path.exists() else None
        
        if narration_path and not narration_data:
            narration_data = json.loads(narration_path.read_text()) if narration_path.exists() else None
        
        # Visual Diversity Gate
        if script_content:
            gates.append(self.visual_diversity_gate(script_content))
        
        # Narrative Depth Gate
        if narration_data:
            gates.append(self.narrative_depth_gate(narration_data))
        
        # No-Spurious-Caution Gate
        if narration_data:
            gates.append(self.no_spurious_caution_gate(narration_data))
        
        # Determine overall pass
        all_passed = all(g.passed for g in gates)
        
        return QualityReport(
            video_id=video_id,
            chapter_id=chapter_id,
            all_gates_passed=all_passed,
            gates=gates
        )
    
    def visual_diversity_gate(self, script_content: str) -> GateResult:
        """Check visual diversity requirements"""
        
        failures = []
        suggestions = []
        details = {}
        score = 0
        max_score = 5
        
        # Check 1: Dynamic elements
        dynamic_found = []
        for pattern in self.DYNAMIC_PATTERNS:
            if pattern in script_content:
                dynamic_found.append(pattern)
        
        details["dynamic_elements"] = dynamic_found
        if len(dynamic_found) >= self.MIN_DYNAMIC_ELEMENTS:
            score += 2
        else:
            failures.append(f"Missing dynamic elements (found {len(dynamic_found)}, need {self.MIN_DYNAMIC_ELEMENTS})")
            suggestions.append("Add MoveAlongPath, ValueTracker, or camera animations")
        
        # Check 2: Animation variety per slide
        slides = re.findall(r'# Slide \d+:.*?(?=# Slide \d+:|$)', script_content, re.DOTALL)
        slide_animation_counts = []
        
        for i, slide in enumerate(slides, 1):
            types_found = set()
            for pattern in self.ANIMATION_PATTERNS:
                if pattern in slide:
                    types_found.add(pattern)
            slide_animation_counts.append({
                "slide": i,
                "animation_types": list(types_found),
                "count": len(types_found)
            })
        
        details["slides_animation_variety"] = slide_animation_counts
        
        all_slides_pass = all(s["count"] >= self.MIN_ANIMATION_TYPES_PER_SLIDE for s in slide_animation_counts)
        if all_slides_pass and slide_animation_counts:
            score += 1
        else:
            failing_slides = [s["slide"] for s in slide_animation_counts if s["count"] < self.MIN_ANIMATION_TYPES_PER_SLIDE]
            if failing_slides:
                failures.append(f"Slides {failing_slides} have insufficient animation variety")
                suggestions.append(f"Add more animation types to slides {failing_slides}")
        
        # Check 3: Shape variety
        shapes_found = []
        for pattern in self.SHAPE_PATTERNS:
            if pattern in script_content:
                shapes_found.append(pattern)
        
        details["shapes_used"] = shapes_found
        if len(shapes_found) >= self.MIN_SHAPE_TYPES:
            score += 1
        else:
            failures.append(f"Insufficient shape variety (found {len(shapes_found)}, need {self.MIN_SHAPE_TYPES})")
            suggestions.append("Use more shape types: Circle, Arrow, Line, Brace")
        
        # Check 4: Color variety
        colors_found = []
        for color in self.COLOR_PATTERNS:
            if color in script_content:
                colors_found.append(color)
        
        details["colors_used"] = colors_found
        if len(colors_found) >= self.MIN_COLORS:
            score += 1
        else:
            failures.append(f"Insufficient color variety (found {len(colors_found)}, need {self.MIN_COLORS})")
            suggestions.append("Add more colors: ORANGE, GREEN, GOLD, etc.")
        
        passed = score >= 3 and len(dynamic_found) >= 1
        
        return GateResult(
            gate_name="Visual Diversity",
            passed=passed,
            score=score,
            max_score=max_score,
            details=details,
            failures=failures,
            suggestions=suggestions
        )
    
    def narrative_depth_gate(self, narration_data: Dict) -> GateResult:
        """Check narrative depth requirements"""
        
        failures = []
        suggestions = []
        details = {}
        score = 0
        max_score = 4
        
        segments = narration_data.get("segments", [])
        
        # Check 1: Factual references
        total_refs = 0
        for seg in segments:
            total_refs += len(seg.get("source_tags", []))
        
        details["factual_references"] = total_refs
        if total_refs >= self.MIN_FACTUAL_REFS:
            score += 2
        else:
            failures.append(f"Insufficient factual references (found {total_refs}, need {self.MIN_FACTUAL_REFS})")
            suggestions.append("Add more source citations using [source:md:...] tags")
        
        # Check 2: Review questions
        review_questions = narration_data.get("review_questions", [])
        details["review_questions"] = len(review_questions)
        if len(review_questions) >= self.MIN_REVIEW_QUESTIONS:
            score += 1
        else:
            failures.append(f"Insufficient review questions (found {len(review_questions)}, need {self.MIN_REVIEW_QUESTIONS})")
            suggestions.append("Add at least 2 review questions")
        
        # Check 3: Word count per slide
        word_counts = []
        word_count_issues = []
        for seg in segments:
            wc = seg.get("word_count", 0)
            word_counts.append(wc)
            if wc < self.MIN_WORDS_PER_SLIDE:
                word_count_issues.append(f"Slide {seg.get('slide_number')}: too short ({wc} words)")
            elif wc > self.MAX_WORDS_PER_SLIDE:
                word_count_issues.append(f"Slide {seg.get('slide_number')}: too long ({wc} words)")
        
        details["word_counts"] = word_counts
        details["total_words"] = sum(word_counts)
        
        if not word_count_issues:
            score += 1
        else:
            failures.extend(word_count_issues)
            suggestions.append(f"Adjust narration to {self.MIN_WORDS_PER_SLIDE}-{self.MAX_WORDS_PER_SLIDE} words per slide")
        
        passed = score >= 3
        
        return GateResult(
            gate_name="Narrative Depth",
            passed=passed,
            score=score,
            max_score=max_score,
            details=details,
            failures=failures,
            suggestions=suggestions
        )
    
    def no_spurious_caution_gate(self, narration_data: Dict) -> GateResult:
        """Check for spurious contractor cautions"""
        
        failures = []
        suggestions = []
        details = {}
        
        segments = narration_data.get("segments", [])
        
        # Find segments with cautions
        caution_segments = []
        unverified_cautions = []
        
        for seg in segments:
            if seg.get("has_contractor_caution", False):
                caution_segments.append(seg.get("slide_number"))
                if not seg.get("caution_verified", False):
                    unverified_cautions.append(seg.get("slide_number"))
        
        details["caution_slides"] = caution_segments
        details["unverified_cautions"] = unverified_cautions
        
        passed = len(unverified_cautions) == 0
        
        if not passed:
            failures.append(f"Unverified contractor cautions in slides {unverified_cautions}")
            suggestions.append("Remove cautions that aren't in source material, or add proper citations")
        
        return GateResult(
            gate_name="No-Spurious-Caution",
            passed=passed,
            score=1 if passed else 0,
            max_score=1,
            details=details,
            failures=failures,
            suggestions=suggestions
        )
    
    def save_report(self, report: QualityReport, output_path: Optional[Path] = None) -> Path:
        """Save quality report to JSON"""
        if output_path is None:
            output_path = Path(f"quality_report_{report.video_id}.json")
        
        output_path.write_text(json.dumps(report.to_dict(), indent=2))
        return output_path
    
    def print_report(self, report: QualityReport):
        """Print a formatted quality report"""
        print("\n" + "="*60)
        print(f"QUALITY REPORT: {report.video_id}")
        print("="*60)
        
        overall = "[PASS] ALL GATES PASSED" if report.all_gates_passed else "[FAIL] SOME GATES FAILED"
        print(f"\nOverall: {overall}\n")
        
        for gate in report.gates:
            status = "[PASS]" if gate.passed else "[FAIL]"
            print(f"{gate.gate_name}: {status} ({gate.score}/{gate.max_score})")
            
            if gate.failures:
                print("  Failures:")
                for f in gate.failures:
                    print(f"    - {f}")
            
            if gate.suggestions and not gate.passed:
                print("  Suggestions:")
                for s in gate.suggestions:
                    print(f"    → {s}")
        
        print("="*60)


def check_video_quality(
    video_id: str,
    chapter_id: str,
    video_dir: Path,
    pdf_path: Optional[Path] = None
) -> QualityReport:
    """Convenience function to check quality for a video directory"""
    
    script_path = video_dir / "base_script.py"
    narration_path = video_dir / "narration.json"
    
    gates = QualityGates(pdf_path)
    
    report = gates.check_all_gates(
        video_id=video_id,
        chapter_id=chapter_id,
        script_path=script_path if script_path.exists() else None,
        narration_path=narration_path if narration_path.exists() else None
    )
    
    # Save report
    report_path = video_dir / "quality_report.json"
    gates.save_report(report, report_path)
    
    # Print report
    gates.print_report(report)
    
    return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python quality_gates.py <video_dir>")
        sys.exit(1)
    
    video_dir = Path(sys.argv[1])
    
    if not video_dir.exists():
        print(f"Directory not found: {video_dir}")
        sys.exit(1)
    
    # Extract video_id and chapter_id from path
    video_id = video_dir.name
    chapter_id = video_dir.parent.name
    
    report = check_video_quality(video_id, chapter_id, video_dir)
    
    sys.exit(0 if report.all_gates_passed else 1)


