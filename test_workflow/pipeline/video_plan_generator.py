"""
Video Plan Generator Module
Generates detailed video plans (video_{id}.plan.json) for each video topic.
Each plan includes per-slide visual goals, visual recipes, narration, and timings.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Import from parent for LLM access
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import call_llm, print_info, print_success, print_error


@dataclass
class SlideSourceRef:
    """Source reference for traceability"""
    source_type: str  # "markdown" or "pdf"
    file: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    page: Optional[int] = None
    figure: Optional[str] = None


@dataclass
class SlidePlan:
    """Plan for a single slide within a video"""
    slide_number: int
    title: str
    visual_goal: str  # What student should notice
    visual_recipe: Dict[str, Any]  # Manim objects and animations
    narration_text: str  # 50-80 words
    timing_seconds: int  # Target duration for this slide
    source_refs: List[SlideSourceRef]
    key_terms_used: List[str]
    animation_types: List[str]  # For validation
    has_dynamic_element: bool  # MoveAlongPath, Updater, etc.


@dataclass
class VideoPlan:
    """Complete plan for a single video"""
    video_id: str
    chapter_id: str
    title: str
    description: str
    total_duration_seconds: int
    total_word_count: int
    slides: List[SlidePlan]
    learning_objectives: List[str]
    review_questions: List[str]
    figure_paths: List[str]  # Paths to figures to embed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class VideoPlanGenerator:
    """Generates detailed video plans from video topics"""
    
    # Slide planning prompt
    PLAN_PROMPT = """You are an expert instructional designer creating a video plan for a GDOT highway plan reading course.

Create a detailed plan for a 2-3 minute instructional video with the following structure.

VIDEO TOPIC:
Title: {title}
Description: {description}
Subsections Covered: {subsections}
Target Duration: {duration} seconds
Target Word Count: {word_count} words
Target Slides: {slide_count} slides

SOURCE CONTENT:
{content}

═══════════════════════════════════════════════════════════════════════════════
FIGURES AVAILABLE - YOU MUST USE THESE IN YOUR SLIDES
═══════════════════════════════════════════════════════════════════════════════
{figures}

CRITICAL: When figures are provided above, you MUST include them as ImageMobject elements 
in the visual_recipe. Each slide that shows a figure should have:
- type: "ImageMobject" with the exact path provided
- Callout annotations pointing to key elements in the figure
- The figure as the MAIN visual focus of that slide

Create a JSON plan with this EXACT structure:
{{
    "slides": [
        {{
            "slide_number": 1,
            "title": "Introduction to [Topic]",
            "visual_goal": "Student should understand the main concept being introduced",
            "visual_recipe": {{
                "background": "WHITE or gradient",
                "main_elements": [
                    {{"type": "Text", "content": "Title text", "position": "UP", "style": "title"}},
                    {{"type": "ImageMobject", "path": "figure_path_if_applicable", "position": "CENTER"}}
                ],
                "animations": [
                    {{"type": "Write", "target": "title", "duration": 1.0}},
                    {{"type": "FadeIn", "target": "image", "duration": 0.5}},
                    {{"type": "Create", "target": "arrow", "duration": 0.5}}
                ],
                "dynamic_elements": [
                    {{"type": "MoveAlongPath", "description": "Tracer moves along centerline"}}
                ],
                "camera": {{"zoom": 1.0, "pan": null}}
            }},
            "narration_text": "50-80 words of narration for this slide, referencing the visuals shown...",
            "timing_seconds": 30,
            "source_refs": [
                {{"source_type": "markdown", "file": "chapter_01.md", "line_start": 10, "line_end": 25}}
            ],
            "key_terms_used": ["term1", "term2"],
            "animation_types": ["Write", "FadeIn", "Create"],
            "has_dynamic_element": true
        }}
    ],
    "learning_objectives": [
        "Understand the purpose of cover sheets",
        "Identify key components of project identification"
    ],
    "review_questions": [
        "What information is found on a cover sheet?",
        "How do you identify the project limits?"
    ]
}}

REQUIREMENTS:
1. Each slide MUST have at least 2 different animation types
2. At least ONE slide must have a dynamic element (MoveAlongPath, Updater, Transform, Succession)
3. Narration must reference specific content from the source material
4. Include source_refs for every factual claim
5. Total narration should be {word_count} words (50-80 per slide)
6. Use available figures where relevant
7. Vary visual elements - avoid plain rectangles
8. Include camera animations for emphasis when showing details

ANIMATION TYPES TO USE:
- Write, Create, DrawBorderThenFill (for text/shapes)
- FadeIn, FadeOut, GrowFromCenter, SpinInFromNothing
- Transform, ReplacementTransform, MoveToTarget
- MoveAlongPath (for tracers), Succession, AnimationGroup
- self.camera.frame.animate (zoom/pan)

Return ONLY valid JSON, no markdown formatting or explanation.
"""

    def __init__(self, output_dir: Path, figures_dir: Optional[Path] = None):
        self.output_dir = output_dir
        self.figures_dir = figures_dir
        self._image_metadata_cache = {}
    
    def _load_image_metadata(self, chapter_id: str) -> Dict[str, Any]:
        """Load image metadata from image_metadata.json"""
        if chapter_id in self._image_metadata_cache:
            return self._image_metadata_cache[chapter_id]
        
        if not self.figures_dir:
            return {}
        
        metadata_path = self.figures_dir / chapter_id / "image_metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self._image_metadata_cache[chapter_id] = json.load(f)
                    return self._image_metadata_cache[chapter_id]
            except Exception as e:
                print_error(f"Failed to load image metadata: {e}")
        
        return {}
    
    def generate_plan(
        self,
        video_id: str,
        chapter_id: str,
        title: str,
        description: str,
        subsections: List[str],
        content: str,
        figure_refs: List[str],
        target_duration: int = 150,
        target_word_count: int = 210,
        target_slide_count: int = 5
    ) -> VideoPlan:
        """Generate a detailed video plan using LLM"""
        
        # Load image metadata directly from file
        image_metadata = self._load_image_metadata(chapter_id)
        
        # Build figures list from metadata or figure_refs
        figures_text = "None available"
        figure_paths = []
        available_figures = []
        
        # First try to use image_metadata (most complete info)
        if image_metadata and 'images' in image_metadata:
            for img in image_metadata['images']:
                img_path = img.get('path', '')
                if img_path:
                    # Make sure path is relative to script execution
                    full_path = self.figures_dir.parent / img_path if self.figures_dir else Path(img_path)
                    if full_path.exists():
                        figure_paths.append(str(full_path))
                        fig_info = f"- {img.get('id', 'unknown')}: {full_path}"
                        if img.get('label'):
                            fig_info += f"\n  Label: {img['label']}"
                        if img.get('description'):
                            fig_info += f"\n  Description: {img['description'][:150]}..."
                        if img.get('key_elements'):
                            fig_info += f"\n  Key elements: {', '.join(img['key_elements'][:4])}"
                        if img.get('highlight_suggestions'):
                            fig_info += f"\n  Highlight these: {', '.join(img['highlight_suggestions'][:3])}"
                        available_figures.append(fig_info)
        
        # Fallback to figure_refs if no metadata
        elif figure_refs and self.figures_dir:
            for fig_id in figure_refs:
                for ext in ['.png', '.jpg', '.jpeg', '.svg']:
                    fig_path = self.figures_dir / chapter_id / f"{fig_id}{ext}"
                    if fig_path.exists():
                        available_figures.append(f"- {fig_id}: {fig_path}")
                        figure_paths.append(str(fig_path))
                        break
        
        if available_figures:
            figures_text = "\n".join(available_figures)
        
        # Build prompt
        prompt = self.PLAN_PROMPT.format(
            title=title,
            description=description,
            subsections=", ".join(subsections),
            duration=target_duration,
            word_count=target_word_count,
            slide_count=target_slide_count,
            content=content[:3000],  # Limit content length
            figures=figures_text
        )
        
        # Call LLM
        print_info(f"Generating plan for: {video_id}")
        response, tokens = call_llm(prompt, max_tokens=2500)
        print_info(f"LLM tokens used: {tokens}")
        
        # Parse response
        try:
            # Clean up response (remove markdown code blocks if present)
            response_clean = response.strip()
            if response_clean.startswith("```"):
                response_clean = response_clean.split("```")[1]
                if response_clean.startswith("json"):
                    response_clean = response_clean[4:]
            response_clean = response_clean.strip()
            
            plan_data = json.loads(response_clean)
        except json.JSONDecodeError as e:
            print_error(f"Failed to parse LLM response as JSON: {e}")
            # Create a fallback plan
            plan_data = self._create_fallback_plan(
                title, description, subsections, target_slide_count
            )
        
        # Convert to dataclasses
        slides = []
        for slide_data in plan_data.get("slides", []):
            source_refs = []
            for ref in slide_data.get("source_refs", []):
                source_refs.append(SlideSourceRef(
                    source_type=ref.get("source_type", "markdown"),
                    file=ref.get("file", ""),
                    line_start=ref.get("line_start"),
                    line_end=ref.get("line_end"),
                    page=ref.get("page"),
                    figure=ref.get("figure")
                ))
            
            slides.append(SlidePlan(
                slide_number=slide_data.get("slide_number", len(slides) + 1),
                title=slide_data.get("title", f"Slide {len(slides) + 1}"),
                visual_goal=slide_data.get("visual_goal", ""),
                visual_recipe=slide_data.get("visual_recipe", {}),
                narration_text=slide_data.get("narration_text", ""),
                timing_seconds=slide_data.get("timing_seconds", 30),
                source_refs=source_refs,
                key_terms_used=slide_data.get("key_terms_used", []),
                animation_types=slide_data.get("animation_types", []),
                has_dynamic_element=slide_data.get("has_dynamic_element", False)
            ))
        
        # Calculate totals
        total_duration = sum(s.timing_seconds for s in slides)
        total_words = sum(len(s.narration_text.split()) for s in slides)
        
        return VideoPlan(
            video_id=video_id,
            chapter_id=chapter_id,
            title=title,
            description=description,
            total_duration_seconds=total_duration,
            total_word_count=total_words,
            slides=slides,
            learning_objectives=plan_data.get("learning_objectives", []),
            review_questions=plan_data.get("review_questions", []),
            figure_paths=figure_paths
        )
    
    def _create_fallback_plan(
        self,
        title: str,
        description: str,
        subsections: List[str],
        slide_count: int
    ) -> Dict:
        """Create a basic fallback plan if LLM fails"""
        slides = []
        
        # Intro slide
        slides.append({
            "slide_number": 1,
            "title": f"Introduction: {title}",
            "visual_goal": "Introduce the topic",
            "visual_recipe": {
                "main_elements": [{"type": "Text", "content": title}],
                "animations": [{"type": "Write", "target": "title"}]
            },
            "narration_text": f"Welcome to this lesson on {title}. {description}",
            "timing_seconds": 30,
            "source_refs": [],
            "key_terms_used": [],
            "animation_types": ["Write"],
            "has_dynamic_element": False
        })
        
        # Content slides for each subsection
        for i, subsection in enumerate(subsections[:slide_count - 2]):
            slides.append({
                "slide_number": i + 2,
                "title": subsection,
                "visual_goal": f"Explain {subsection}",
                "visual_recipe": {
                    "main_elements": [{"type": "Text", "content": subsection}],
                    "animations": [{"type": "Write"}, {"type": "FadeIn"}]
                },
                "narration_text": f"Now let's discuss {subsection}. This is an important concept in plan reading.",
                "timing_seconds": 30,
                "source_refs": [],
                "key_terms_used": [],
                "animation_types": ["Write", "FadeIn"],
                "has_dynamic_element": False
            })
        
        # Summary slide
        slides.append({
            "slide_number": len(slides) + 1,
            "title": "Summary",
            "visual_goal": "Review key points",
            "visual_recipe": {
                "main_elements": [{"type": "BulletedList"}],
                "animations": [{"type": "Create"}, {"type": "FadeIn"}]
            },
            "narration_text": f"To summarize, we covered {', '.join(subsections)}. These concepts are essential for reading highway plans.",
            "timing_seconds": 30,
            "source_refs": [],
            "key_terms_used": [],
            "animation_types": ["Create", "FadeIn"],
            "has_dynamic_element": False
        })
        
        return {
            "slides": slides,
            "learning_objectives": [f"Understand {title}"],
            "review_questions": [f"What are the key components of {title}?"]
        }
    
    def save_plan(self, plan: VideoPlan) -> Path:
        """Save video plan to JSON file"""
        # Create chapter output directory
        chapter_dir = self.output_dir / plan.chapter_id
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        # Save plan
        plan_file = chapter_dir / f"{plan.video_id}.plan.json"
        
        # Convert to dict for JSON serialization
        plan_dict = {
            "video_id": plan.video_id,
            "chapter_id": plan.chapter_id,
            "title": plan.title,
            "description": plan.description,
            "total_duration_seconds": plan.total_duration_seconds,
            "total_word_count": plan.total_word_count,
            "learning_objectives": plan.learning_objectives,
            "review_questions": plan.review_questions,
            "figure_paths": plan.figure_paths,
            "created_at": plan.created_at,
            "slides": []
        }
        
        for slide in plan.slides:
            slide_dict = {
                "slide_number": slide.slide_number,
                "title": slide.title,
                "visual_goal": slide.visual_goal,
                "visual_recipe": slide.visual_recipe,
                "narration_text": slide.narration_text,
                "timing_seconds": slide.timing_seconds,
                "source_refs": [
                    {
                        "source_type": ref.source_type,
                        "file": ref.file,
                        "line_start": ref.line_start,
                        "line_end": ref.line_end,
                        "page": ref.page,
                        "figure": ref.figure
                    }
                    for ref in slide.source_refs
                ],
                "key_terms_used": slide.key_terms_used,
                "animation_types": slide.animation_types,
                "has_dynamic_element": slide.has_dynamic_element
            }
            plan_dict["slides"].append(slide_dict)
        
        plan_file.write_text(json.dumps(plan_dict, indent=2))
        print_success(f"Saved plan: {plan_file}")
        
        return plan_file
    
    def load_plan(self, plan_file: Path) -> VideoPlan:
        """Load a video plan from JSON file"""
        data = json.loads(plan_file.read_text())
        
        slides = []
        for slide_data in data.get("slides", []):
            source_refs = []
            for ref in slide_data.get("source_refs", []):
                source_refs.append(SlideSourceRef(**ref))
            
            slides.append(SlidePlan(
                slide_number=slide_data["slide_number"],
                title=slide_data["title"],
                visual_goal=slide_data["visual_goal"],
                visual_recipe=slide_data["visual_recipe"],
                narration_text=slide_data["narration_text"],
                timing_seconds=slide_data["timing_seconds"],
                source_refs=source_refs,
                key_terms_used=slide_data.get("key_terms_used", []),
                animation_types=slide_data.get("animation_types", []),
                has_dynamic_element=slide_data.get("has_dynamic_element", False)
            ))
        
        return VideoPlan(
            video_id=data["video_id"],
            chapter_id=data["chapter_id"],
            title=data["title"],
            description=data["description"],
            total_duration_seconds=data["total_duration_seconds"],
            total_word_count=data["total_word_count"],
            slides=slides,
            learning_objectives=data.get("learning_objectives", []),
            review_questions=data.get("review_questions", []),
            figure_paths=data.get("figure_paths", []),
            created_at=data.get("created_at", "")
        )


def generate_video_plans_for_chapter(
    chapter_manifest_path: Path,
    videos_manifest_path: Path,
    chapter_content_path: Path,
    output_dir: Path,
    figures_dir: Optional[Path] = None
) -> List[VideoPlan]:
    """Generate plans for all videos in a chapter"""
    
    # Load manifests
    videos_manifest = json.loads(videos_manifest_path.read_text())
    chapter_content = chapter_content_path.read_text()
    
    generator = VideoPlanGenerator(output_dir, figures_dir)
    plans = []
    
    for video_data in videos_manifest.get("videos", []):
        plan = generator.generate_plan(
            video_id=video_data["video_id"],
            chapter_id=video_data["chapter_id"],
            title=video_data["title"],
            description=video_data["description"],
            subsections=video_data["subsections_covered"],
            content=chapter_content,
            figure_refs=video_data.get("figure_refs", []),
            target_duration=video_data.get("estimated_duration_seconds", 150),
            target_word_count=video_data.get("target_word_count", 210),
            target_slide_count=video_data.get("target_slide_count", 5)
        )
        
        generator.save_plan(plan)
        plans.append(plan)
    
    return plans


if __name__ == "__main__":
    print("Video Plan Generator - Run via orchestrator scripts")

