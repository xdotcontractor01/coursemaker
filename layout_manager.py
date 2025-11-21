"""
Intelligent Layout Manager for Manim Videos
Calculates non-overlapping positions for content and images
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict
from enum import Enum

class LayoutType(Enum):
    """Different layout strategies for slides"""
    BACKGROUND_ONLY = "background_only"  # Image as subtle background
    SPLIT_LEFT = "split_left"  # Image on left, content on right
    SPLIT_RIGHT = "split_right"  # Content on left, image on right
    TOP_IMAGE = "top_image"  # Image at top, content below
    BOTTOM_IMAGE = "bottom_image"  # Content at top, image below
    SIDEBAR_LEFT = "sidebar_left"  # Small image sidebar left
    SIDEBAR_RIGHT = "sidebar_right"  # Small image sidebar right

@dataclass
class BoundingBox:
    """Represents a rectangular region in the Manim frame"""
    left: float
    right: float
    top: float
    bottom: float
    
    @property
    def width(self):
        return self.right - self.left
    
    @property
    def height(self):
        return self.top - self.bottom
    
    @property
    def center(self):
        return ((self.left + self.right) / 2, (self.top + self.bottom) / 2)
    
    def to_manim_shift(self):
        """Convert to Manim shift coordinates"""
        center_x, center_y = self.center
        return f"RIGHT * {center_x:.2f} + UP * {center_y:.2f}"

class LayoutManager:
    """
    Manages layout calculations for Manim slides with images
    Ensures content and images don't overlap
    """
    
    # Standard Manim frame dimensions
    FRAME_WIDTH = 14.22  # Default config.frame_width
    FRAME_HEIGHT = 8.0   # Default config.frame_height
    FRAME_LEFT = -FRAME_WIDTH / 2
    FRAME_RIGHT = FRAME_WIDTH / 2
    FRAME_TOP = FRAME_HEIGHT / 2
    FRAME_BOTTOM = -FRAME_HEIGHT / 2
    
    # Safe margins
    MARGIN = 0.5
    TITLE_HEIGHT = 1.0
    TITLE_TOP = FRAME_TOP - 0.3
    
    @classmethod
    def get_layout_regions(cls, layout_type: LayoutType, has_title: bool = True) -> Dict[str, BoundingBox]:
        """
        Calculate non-overlapping regions for content and images
        
        Returns dict with 'image', 'content', 'title' bounding boxes
        """
        regions = {}
        
        # Title region (if present)
        if has_title:
            regions['title'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=cls.TITLE_TOP,
                bottom=cls.TITLE_TOP - cls.TITLE_HEIGHT
            )
            content_top = cls.TITLE_TOP - cls.TITLE_HEIGHT - 0.5
        else:
            content_top = cls.FRAME_TOP - cls.MARGIN
        
        content_bottom = cls.FRAME_BOTTOM + cls.MARGIN
        
        # Calculate regions based on layout type
        if layout_type == LayoutType.BACKGROUND_ONLY:
            # Image fills entire frame (will be low opacity)
            regions['image'] = BoundingBox(
                left=cls.FRAME_LEFT,
                right=cls.FRAME_RIGHT,
                top=cls.FRAME_TOP,
                bottom=cls.FRAME_BOTTOM
            )
            # Content uses full available space
            regions['content'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=content_top,
                bottom=content_bottom
            )
        
        elif layout_type == LayoutType.SPLIT_LEFT:
            # Image on left half
            regions['image'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=-0.5,
                top=content_top,
                bottom=content_bottom
            )
            # Content on right half
            regions['content'] = BoundingBox(
                left=0.5,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=content_top,
                bottom=content_bottom
            )
        
        elif layout_type == LayoutType.SPLIT_RIGHT:
            # Content on left half
            regions['content'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=-0.5,
                top=content_top,
                bottom=content_bottom
            )
            # Image on right half
            regions['image'] = BoundingBox(
                left=0.5,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=content_top,
                bottom=content_bottom
            )
        
        elif layout_type == LayoutType.TOP_IMAGE:
            # Image at top third
            image_bottom = content_top - 2.5
            regions['image'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=content_top,
                bottom=image_bottom
            )
            # Content in bottom area
            regions['content'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=image_bottom - 0.3,
                bottom=content_bottom
            )
        
        elif layout_type == LayoutType.BOTTOM_IMAGE:
            # Content at top
            content_bottom_adj = content_bottom + 2.8
            regions['content'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=content_top,
                bottom=content_bottom_adj
            )
            # Image at bottom
            regions['image'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=content_bottom_adj - 0.3,
                bottom=content_bottom
            )
        
        elif layout_type == LayoutType.SIDEBAR_LEFT:
            # Small image sidebar left
            regions['image'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=cls.FRAME_LEFT + 3.5,
                top=content_top,
                bottom=content_bottom
            )
            # Content takes most of the space
            regions['content'] = BoundingBox(
                left=cls.FRAME_LEFT + 4.0,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=content_top,
                bottom=content_bottom
            )
        
        elif layout_type == LayoutType.SIDEBAR_RIGHT:
            # Content on left
            regions['content'] = BoundingBox(
                left=cls.FRAME_LEFT + cls.MARGIN,
                right=cls.FRAME_RIGHT - 4.0,
                top=content_top,
                bottom=content_bottom
            )
            # Small image sidebar right
            regions['image'] = BoundingBox(
                left=cls.FRAME_RIGHT - 3.5,
                right=cls.FRAME_RIGHT - cls.MARGIN,
                top=content_top,
                bottom=content_bottom
            )
        
        return regions
    
    @classmethod
    def generate_manim_positioning_code(cls, layout_type: LayoutType, 
                                       image_var_name: str = "image",
                                       content_var_name: str = "content",
                                       has_title: bool = True) -> str:
        """
        Generate Manim code for positioning elements based on layout
        
        Returns Python code as string
        """
        regions = cls.get_layout_regions(layout_type, has_title)
        
        code_lines = []
        code_lines.append("# Layout positioning")
        
        # Title positioning (if present)
        if has_title:
            title_center_x, title_center_y = regions['title'].center
            code_lines.append(f"title.move_to(RIGHT * {title_center_x:.2f} + UP * {title_center_y:.2f})")
        
        # Image positioning
        img_region = regions['image']
        img_center_x, img_center_y = img_region.center
        
        if layout_type == LayoutType.BACKGROUND_ONLY:
            code_lines.append(f"# Background image (low opacity)")
            code_lines.append(f"{image_var_name}.scale_to_fit_width(config.frame_width)")
            code_lines.append(f"{image_var_name}.scale_to_fit_height(config.frame_height)")
            code_lines.append(f"{image_var_name}.set_opacity(0.25)")
        else:
            code_lines.append(f"# Position image in allocated region")
            code_lines.append(f"{image_var_name}.scale_to_fit_width({img_region.width:.2f})")
            code_lines.append(f"{image_var_name}.scale_to_fit_height({img_region.height:.2f})")
            code_lines.append(f"{image_var_name}.move_to(RIGHT * {img_center_x:.2f} + UP * {img_center_y:.2f})")
        
        # Content positioning
        content_region = regions['content']
        content_center_x, content_center_y = content_region.center
        code_lines.append(f"# Position content in allocated region")
        code_lines.append(f"{content_var_name}.move_to(RIGHT * {content_center_x:.2f} + UP * {content_center_y:.2f})")
        
        return "\n".join(code_lines)
    
    @classmethod
    def choose_best_layout(cls, content_type: str, has_image: bool) -> LayoutType:
        """
        Intelligently choose the best layout based on content type
        
        content_type: 'text_heavy', 'diagram_heavy', 'balanced', 'title_only'
        """
        if not has_image:
            # No special layout needed
            return None
        
        if content_type == 'title_only':
            return LayoutType.BACKGROUND_ONLY
        elif content_type == 'text_heavy':
            # Lots of text, put image on side
            return LayoutType.SIDEBAR_RIGHT
        elif content_type == 'diagram_heavy':
            # Lots of diagrams, use split screen
            return LayoutType.SPLIT_RIGHT
        elif content_type == 'balanced':
            # Equal content and visuals
            return LayoutType.SPLIT_LEFT
        else:
            # Default to subtle background
            return LayoutType.BACKGROUND_ONLY


def generate_layout_example():
    """Generate example code showing how to use the layout manager"""
    print("="*80)
    print("LAYOUT MANAGER USAGE EXAMPLE")
    print("="*80)
    
    # Example 1: Split screen layout
    print("\nExample 1: Split Screen Layout (Image Left, Content Right)")
    print("-"*80)
    regions = LayoutManager.get_layout_regions(LayoutType.SPLIT_LEFT, has_title=True)
    print(f"Title region: center={regions['title'].center}, size={regions['title'].width:.2f}x{regions['title'].height:.2f}")
    print(f"Image region: center={regions['image'].center}, size={regions['image'].width:.2f}x{regions['image'].height:.2f}")
    print(f"Content region: center={regions['content'].center}, size={regions['content'].width:.2f}x{regions['content'].height:.2f}")
    
    print("\nGenerated Manim code:")
    code = LayoutManager.generate_manim_positioning_code(LayoutType.SPLIT_LEFT)
    print(code)
    
    # Example 2: Background layout
    print("\n\nExample 2: Background Image Layout")
    print("-"*80)
    code = LayoutManager.generate_manim_positioning_code(LayoutType.BACKGROUND_ONLY)
    print(code)
    
    # Example 3: Sidebar layout
    print("\n\nExample 3: Sidebar Layout (Image Right)")
    print("-"*80)
    code = LayoutManager.generate_manim_positioning_code(LayoutType.SIDEBAR_RIGHT)
    print(code)
    
    print("\n" + "="*80)


if __name__ == "__main__":
    generate_layout_example()

