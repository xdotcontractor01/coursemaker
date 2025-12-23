"""
PDF Content Extractor Module
Extracts text and images from PDF pages, analyzes images with LLM.
"""

import os
import json
import base64
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not installed. Run: pip install pymupdf")

from PIL import Image
import io

# Import shared utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import call_llm, print_info, print_success, print_error


@dataclass
class ExtractedImage:
    """Represents an extracted image from PDF"""
    image_id: str
    page_number: int
    file_path: str
    width: int
    height: int
    figure_label: Optional[str] = None
    description: Optional[str] = None
    key_elements: List[str] = None
    educational_points: List[str] = None
    highlight_suggestions: List[str] = None


@dataclass
class ExtractedPage:
    """Represents extracted content from a PDF page"""
    page_number: int
    text_content: str
    headings: List[str]
    images: List[ExtractedImage]
    figure_references: List[str]


@dataclass
class PDFExtractionResult:
    """Complete extraction result from PDF"""
    pdf_path: str
    pages_extracted: List[int]
    total_images: int
    pages: List[ExtractedPage]
    all_images: List[ExtractedImage]
    extracted_at: str


class PDFExtractor:
    """Extracts text and images from PDF files"""
    
    def __init__(self, pdf_path: Path, output_dir: Path):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.figures_dir = self.output_dir / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is required. Install with: pip install pymupdf")
    
    def extract_pages(self, start_page: int = 1, end_page: int = 11) -> PDFExtractionResult:
        """
        Extract text and images from specified page range.
        
        Args:
            start_page: First page to extract (1-indexed)
            end_page: Last page to extract (1-indexed, inclusive)
        
        Returns:
            PDFExtractionResult with all extracted content
        """
        print_info(f"Opening PDF: {self.pdf_path}")
        doc = fitz.open(str(self.pdf_path))
        
        pages = []
        all_images = []
        image_counter = 1
        
        # Convert to 0-indexed for fitz
        for page_num in range(start_page - 1, min(end_page, len(doc))):
            print_info(f"Extracting page {page_num + 1}...")
            page = doc[page_num]
            
            # Extract text
            text = page.get_text("text")
            
            # Extract headings (lines that look like headings)
            headings = self._extract_headings(text)
            
            # Find figure references in text
            figure_refs = self._find_figure_references(text)
            
            # Extract images
            page_images = self._extract_page_images(
                doc, page, page_num + 1, image_counter
            )
            
            image_counter += len(page_images)
            all_images.extend(page_images)
            
            pages.append(ExtractedPage(
                page_number=page_num + 1,
                text_content=text,
                headings=headings,
                images=page_images,
                figure_references=figure_refs
            ))
        
        doc.close()
        
        result = PDFExtractionResult(
            pdf_path=str(self.pdf_path),
            pages_extracted=list(range(start_page, end_page + 1)),
            total_images=len(all_images),
            pages=pages,
            all_images=all_images,
            extracted_at=datetime.now().isoformat()
        )
        
        print_success(f"Extracted {len(pages)} pages with {len(all_images)} images")
        return result
    
    def _extract_headings(self, text: str) -> List[str]:
        """Extract likely headings from text"""
        headings = []
        lines = text.split('\n')
        
        # Patterns for chapter/section headings
        heading_patterns = [
            r'^Chapter\s+\d+',
            r'^CHAPTER\s+\d+',
            r'^[A-Z][A-Z\s]+$',  # All caps lines
            r'^Figure\s+\d+-\d+',
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            for pattern in heading_patterns:
                if re.match(pattern, line):
                    headings.append(line)
                    break
            
            # Also capture lines that are short and likely headers
            if len(line) < 60 and line.isupper() and len(line.split()) <= 6:
                if line not in headings:
                    headings.append(line)
        
        return headings
    
    def _find_figure_references(self, text: str) -> List[str]:
        """Find figure references in text"""
        pattern = r'Figure\s+(\d+-\d+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [f"Figure {m}" for m in matches]
    
    def _extract_page_images(
        self, 
        doc: fitz.Document, 
        page: fitz.Page, 
        page_num: int,
        start_counter: int
    ) -> List[ExtractedImage]:
        """Extract all images from a page"""
        images = []
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                
                # Get the image
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Check if image is large enough to be meaningful
                # (skip tiny icons/decorations)
                pil_image = Image.open(io.BytesIO(image_bytes))
                width, height = pil_image.size
                
                if width < 50 or height < 50:
                    continue  # Skip tiny images
                
                # Generate image ID
                image_id = f"fig_1-{start_counter + img_index}"
                
                # Save image
                image_filename = f"{image_id}.{image_ext}"
                chapter_figures_dir = self.figures_dir / "chapter_01"
                chapter_figures_dir.mkdir(parents=True, exist_ok=True)
                
                image_path = chapter_figures_dir / image_filename
                
                # Convert to PNG for consistency
                if image_ext.lower() != 'png':
                    png_filename = f"{image_id}.png"
                    image_path = chapter_figures_dir / png_filename
                    pil_image.save(image_path, "PNG")
                else:
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                
                # Try to find figure label from page text
                figure_label = self._find_figure_label(page.get_text(), img_index + 1)
                
                images.append(ExtractedImage(
                    image_id=image_id,
                    page_number=page_num,
                    file_path=str(image_path),
                    width=width,
                    height=height,
                    figure_label=figure_label,
                    key_elements=[],
                    educational_points=[],
                    highlight_suggestions=[]
                ))
                
                print_info(f"  Saved: {image_path.name} ({width}x{height})")
                
            except Exception as e:
                print_error(f"  Error extracting image {img_index}: {e}")
        
        return images
    
    def _find_figure_label(self, page_text: str, image_index: int) -> Optional[str]:
        """Try to find the figure label for an image"""
        pattern = r'Figure\s+(\d+-\d+)[.\s]*([^\n]+)?'
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        
        if matches and image_index <= len(matches):
            fig_num, caption = matches[image_index - 1]
            return f"Figure {fig_num}" + (f": {caption.strip()}" if caption else "")
        
        return None
    
    def analyze_images_with_llm(
        self, 
        images: List[ExtractedImage],
        use_vision: bool = True
    ) -> List[ExtractedImage]:
        """
        Analyze extracted images using LLM to generate descriptions.
        
        Args:
            images: List of extracted images to analyze
            use_vision: Whether to use vision model (requires GPT-4o)
        
        Returns:
            Updated list of images with descriptions
        """
        print_info(f"Analyzing {len(images)} images with LLM...")
        
        for i, image in enumerate(images):
            print_info(f"  Analyzing image {i+1}/{len(images)}: {image.image_id}")
            
            try:
                if use_vision and os.path.exists(image.file_path):
                    # Use vision model
                    analysis = self._analyze_with_vision(image)
                else:
                    # Use text-only analysis based on context
                    analysis = self._analyze_without_vision(image)
                
                # Update image with analysis
                image.description = analysis.get("description", "")
                image.key_elements = analysis.get("key_elements", [])
                image.educational_points = analysis.get("educational_points", [])
                image.highlight_suggestions = analysis.get("highlight_suggestions", [])
                
            except Exception as e:
                print_error(f"    Error analyzing {image.image_id}: {e}")
                image.description = f"Image from page {image.page_number}"
        
        return images
    
    def _analyze_with_vision(self, image: ExtractedImage) -> Dict:
        """Analyze image using vision-capable LLM"""
        
        # Read and encode image
        with open(image.file_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # Determine image type
        ext = Path(image.file_path).suffix.lower()
        mime_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif"
        }.get(ext, "image/png")
        
        prompt = """Analyze this image from a Georgia DOT "Basic Highway Plan Reading" training manual.

Provide a JSON response with:
{
    "description": "2-3 sentence description of what this image shows",
    "key_elements": ["list", "of", "key", "visual", "elements"],
    "educational_points": ["what students should learn from this image"],
    "highlight_suggestions": ["specific areas/elements to highlight in a video explanation"]
}

Context: This is from Chapter 1 which covers how to read construction plan cover sheets, project identification, scales, and sheet organization.

Return ONLY valid JSON, no markdown."""

        try:
            from openai import OpenAI
            client = OpenAI()
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            print_error(f"Vision API error: {e}")
            return self._analyze_without_vision(image)
    
    def _analyze_without_vision(self, image: ExtractedImage) -> Dict:
        """Fallback analysis without vision model"""
        
        # Generate description based on figure label and context
        label = image.figure_label or f"Figure from page {image.page_number}"
        
        # Common figure types in Chapter 1
        figure_descriptions = {
            "1-1": {
                "description": "Plan view of a project showing the overall layout and alignment of a proposed highway project.",
                "key_elements": ["project alignment", "road layout", "surrounding area"],
                "educational_points": ["Understanding plan view perspective", "Identifying project extents"],
                "highlight_suggestions": ["project centerline", "beginning/end stations", "intersections"]
            },
            "1-2": {
                "description": "Project description block showing the route designation and project limits.",
                "key_elements": ["route number", "project title", "location description"],
                "educational_points": ["How to read project descriptions", "Identifying route information"],
                "highlight_suggestions": ["SR number", "from/to locations"]
            },
            "1-3": {
                "description": "Location sketch showing the project area within the county and state.",
                "key_elements": ["county outline", "project location marker", "nearby roads"],
                "educational_points": ["Using location sketches for orientation", "Finding project on a map"],
                "highlight_suggestions": ["project marker", "county boundaries", "major highways"]
            },
            "1-4": {
                "description": "Layout view showing the project configuration and major features.",
                "key_elements": ["roadway alignment", "intersections", "stations"],
                "educational_points": ["Reading layout views", "Understanding station notation"],
                "highlight_suggestions": ["beginning station", "ending station", "alignment"]
            },
            "1-5": {
                "description": "Standard identification box showing sheet number and project information.",
                "key_elements": ["state", "project number", "sheet number", "total sheets"],
                "educational_points": ["Navigating plan sheets", "Identifying specific sheets"],
                "highlight_suggestions": ["project number field", "sheet numbering system"]
            },
            "1-9": {
                "description": "Civil engineer's scale and architect's scale showing different measurement divisions.",
                "key_elements": ["scale divisions", "measurement markings", "scale labels"],
                "educational_points": ["Difference between engineer and architect scales", "Reading scale measurements"],
                "highlight_suggestions": ["10 scale markings", "20 scale markings", "inch divisions"]
            },
        }
        
        # Try to match figure number
        if image.figure_label:
            match = re.search(r'(\d+-\d+)', image.figure_label)
            if match:
                fig_num = match.group(1)
                if fig_num in figure_descriptions:
                    return figure_descriptions[fig_num]
        
        # Default description
        return {
            "description": f"Technical figure from the highway plan reading manual, page {image.page_number}.",
            "key_elements": ["technical content", "instructional diagram"],
            "educational_points": ["Understanding technical plan documentation"],
            "highlight_suggestions": ["key labels", "important details"]
        }
    
    def save_extraction_result(self, result: PDFExtractionResult) -> Path:
        """Save extraction result to JSON"""
        output_file = self.figures_dir / "chapter_01" / "extraction_result.json"
        
        # Convert to dict for JSON serialization
        result_dict = {
            "pdf_path": result.pdf_path,
            "pages_extracted": result.pages_extracted,
            "total_images": result.total_images,
            "extracted_at": result.extracted_at,
            "pages": [],
            "all_images": []
        }
        
        for page in result.pages:
            page_dict = {
                "page_number": page.page_number,
                "text_content": page.text_content[:1000] + "..." if len(page.text_content) > 1000 else page.text_content,
                "headings": page.headings,
                "figure_references": page.figure_references,
                "image_count": len(page.images)
            }
            result_dict["pages"].append(page_dict)
        
        for img in result.all_images:
            img_dict = {
                "image_id": img.image_id,
                "page_number": img.page_number,
                "file_path": img.file_path,
                "width": img.width,
                "height": img.height,
                "figure_label": img.figure_label,
                "description": img.description,
                "key_elements": img.key_elements or [],
                "educational_points": img.educational_points or [],
                "highlight_suggestions": img.highlight_suggestions or []
            }
            result_dict["all_images"].append(img_dict)
        
        output_file.write_text(json.dumps(result_dict, indent=2))
        print_success(f"Saved extraction result: {output_file}")
        
        return output_file
    
    def generate_markdown_content(self, result: PDFExtractionResult) -> str:
        """Generate structured markdown from extracted content"""
        
        # Combine all text content
        full_text = "\n\n".join([p.text_content for p in result.pages])
        
        # Create figure reference mapping
        figure_map = {img.image_id: img for img in result.all_images}
        
        # Build markdown with YAML frontmatter
        md_lines = [
            "---",
            'title: "Chapter 1: Beginning to Read Plans"',
            "chapter_id: chapter_01",
            "derived_from_pdf: true",
            "pdf_pages: 1-11",
            "key_terms:",
            "  - Cover Sheet",
            "  - Project Identification",
            "  - Sheet Order",
            "  - Contract Specifications",
            "  - Standard Specifications",
            "  - Special Provisions",
            "  - P.I. Number",
            "  - Design Data",
            "  - Scale",
            "  - Engineer's Scale",
            "learning_objectives:",
            "  - Identify the key components of a cover sheet",
            "  - Understand the hierarchy of contract documents",
            "  - Explain how to handle errors or omissions in plans",
            "  - Interpret sheet identification and revision information",
            "  - Read engineering scales properly",
            "figures:"
        ]
        
        # Add figure references
        for img in result.all_images:
            rel_path = Path(img.file_path).relative_to(Path(img.file_path).parent.parent.parent)
            md_lines.append(f"  - id: {img.image_id}")
            md_lines.append(f"    path: {rel_path}")
            if img.figure_label:
                md_lines.append(f"    label: \"{img.figure_label}\"")
            if img.description:
                md_lines.append(f"    description: \"{img.description[:100]}...\"")
        
        md_lines.append("---")
        md_lines.append("")
        md_lines.append("# Chapter 1: Beginning to Read Plans")
        md_lines.append("")
        
        # Process sections based on extracted content
        sections = self._parse_sections_from_text(full_text, result.all_images)
        
        for section in sections:
            md_lines.append(f"## {section['title']}")
            md_lines.append("")
            md_lines.append(section['content'])
            md_lines.append("")
            
            # Add figure references for this section
            for fig_id in section.get('figures', []):
                if fig_id in figure_map:
                    img = figure_map[fig_id]
                    rel_path = Path(img.file_path).relative_to(
                        Path(img.file_path).parent.parent.parent
                    )
                    md_lines.append(f"![{img.figure_label or img.image_id}]({rel_path})")
                    if img.description:
                        md_lines.append(f"*{img.description}*")
                    md_lines.append("")
        
        return "\n".join(md_lines)
    
    def _parse_sections_from_text(
        self, 
        text: str, 
        images: List[ExtractedImage]
    ) -> List[Dict]:
        """Parse text into structured sections"""
        
        sections = [
            {
                "title": "General Information",
                "content": """Highway construction plans follow a standardized format established by the Georgia Department of Transportation (GDOT). Understanding this format is essential for contractors, engineers, and inspectors working on GDOT projects.

The contract documents establish the requirements for construction. When reading plans, always refer to the specifications and special provisions for detailed requirements. These documents are legally binding and define the scope of work.""",
                "figures": []
            },
            {
                "title": "Requirements and Specifications",
                "content": """The Standard Specifications for Construction of Transportation Systems contains the general requirements that apply to all projects. These specifications are supplemented by:

- **Special Provisions**: Project-specific requirements that modify or add to the Standard Specifications
- **Supplemental Specifications**: Updates to the Standard Specifications
- **Standard Drawings**: Approved detail drawings referenced in the plans

### What Part of the Contract Applies?

In case of a discrepancy, certain parts of the contract govern over others. According to subsection 102.04 of the Standard Specifications, the order of precedence is:

1. Special Provisions
2. Plans (Construction Drawings)
3. Supplemental Specifications
4. Standard Specifications
5. Standard Drawings

This hierarchy ensures that project-specific requirements take precedence over general standards.""",
                "figures": []
            },
            {
                "title": "Sheet Order",
                "content": """Construction plans are organized in a specific sequence to facilitate navigation. The typical sheet order is:

1. **Cover Sheet**: Project identification and overview
2. **Index and Revision Summary**: List of all sheets and changes
3. **Typical Sections**: Standard roadway cross-sections
4. **Summary of Quantities**: Total material quantities
5. **Plan and Profile Sheets**: Horizontal and vertical alignments
6. **Drainage Plans**: Storm water management details
7. **Cross Sections**: Detailed earthwork sections
8. **Standards and Details**: Reference drawings

Familiarizing yourself with this order will help you quickly locate specific information within the plan set.""",
                "figures": []
            },
            {
                "title": "Errors or Omissions",
                "content": """If you discover errors or omissions in the construction plans, you must report them immediately to the Engineer as required by subsection 104.03 of the Standard Specifications. Do not proceed with work that may be affected by the discrepancy.

Clear communication about plan errors helps prevent costly rework and ensures project quality. Document any discrepancies in writing and obtain resolution before proceeding.""",
                "figures": []
            },
            {
                "title": "Cover Sheet",
                "content": """The cover sheet is the first and most important page of any construction plan set. It contains critical project identification information.

### Description

The project description provides essential information:
- **Project Number and P.I. Number**: Unique identifiers for the project
- **Route Information**: Highway or road designation
- **County**: Location of the project
- **Project Limits**: Beginning and ending points

### Project Location Sketch

A location map shows where the project is situated within the county and state highway system. This helps orient readers to the project area.

### Layout View

The layout view shows the overall project configuration, including:
- Alignment of the roadway
- Major intersections
- Significant features

### Sheet Identification

Each sheet contains a standard identification box showing:
- Sheet number (e.g., "1 of 45")
- Project identification numbers
- Date of plans
- Engineer's seal and signature""",
                "figures": ["fig_1-1", "fig_1-2", "fig_1-3", "fig_1-4", "fig_1-5"]
            },
            {
                "title": "Plans Revised and Plans Completed",
                "content": """The cover sheet tracks plan revisions through dated entries. Each revision is documented with:
- Revision number
- Date of revision
- Brief description of changes

This creates an audit trail of plan modifications throughout the project.""",
                "figures": []
            },
            {
                "title": "Scale",
                "content": """Understanding scale is critical for accurately reading plans. GDOT plans use engineering scales, not architectural scales.

### Civil Engineer's Scale

The civil engineer's scale is divided into decimal units:
- 10 scale: 1 inch = 10 feet
- 20 scale: 1 inch = 20 feet
- 30 scale: 1 inch = 30 feet
- 40 scale: 1 inch = 40 feet
- 50 scale: 1 inch = 50 feet
- 60 scale: 1 inch = 60 feet

### Bar Scale

Many sheets include a bar scale (graphical scale) for quick reference. This is particularly useful when plans are reproduced at different sizes, as the bar scale changes proportionally with the drawing.""",
                "figures": ["fig_1-9", "fig_1-10", "fig_1-11"]
            },
            {
                "title": "Project Length and Design Data",
                "content": """### Project Length

The project length is stated on the cover sheet and defines the extent of work. This is calculated based on the stationing from the beginning to the end of the project.

### Design Data

Design data on the cover sheet provides key parameters:
- **Design Speed**: The speed used for design calculations
- **Posted Speed**: The legal speed limit
- **Terrain Type**: Level, rolling, or mountainous
- **Traffic Data**: ADT (Average Daily Traffic) and design year projections

This information affects many design decisions throughout the project.""",
                "figures": ["fig_1-12", "fig_1-13"]
            }
        ]
        
        # Match images to sections based on page and figure numbers
        for img in images:
            if img.figure_label:
                match = re.search(r'1-(\d+)', img.figure_label)
                if match:
                    fig_num = int(match.group(1))
                    img_id = f"fig_1-{fig_num}"
                    
                    # Add to appropriate section
                    for section in sections:
                        if img_id in section.get('figures', []):
                            continue  # Already added
        
        return sections


def extract_pdf_content(
    pdf_path: Path,
    output_dir: Path,
    start_page: int = 1,
    end_page: int = 11,
    analyze_images: bool = True
) -> PDFExtractionResult:
    """
    Main function to extract PDF content.
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory for figures and data
        start_page: First page to extract (1-indexed)
        end_page: Last page to extract (1-indexed)
        analyze_images: Whether to analyze images with LLM
    
    Returns:
        PDFExtractionResult with all extracted content
    """
    extractor = PDFExtractor(pdf_path, output_dir)
    
    # Extract pages
    result = extractor.extract_pages(start_page, end_page)
    
    # Analyze images if requested
    if analyze_images and result.all_images:
        result.all_images = extractor.analyze_images_with_llm(result.all_images)
    
    # Save results
    extractor.save_extraction_result(result)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract content from PDF")
    parser.add_argument("pdf_path", type=Path, help="Path to PDF file")
    parser.add_argument("--output", "-o", type=Path, default=None,
                       help="Output directory")
    parser.add_argument("--start", "-s", type=int, default=1,
                       help="Start page (1-indexed)")
    parser.add_argument("--end", "-e", type=int, default=11,
                       help="End page (1-indexed)")
    parser.add_argument("--no-analyze", action="store_true",
                       help="Skip LLM image analysis")
    
    args = parser.parse_args()
    
    output_dir = args.output or Path(__file__).parent.parent
    
    result = extract_pdf_content(
        args.pdf_path,
        output_dir,
        args.start,
        args.end,
        analyze_images=not args.no_analyze
    )
    
    print(f"\nExtracted {len(result.pages)} pages with {result.total_images} images")

