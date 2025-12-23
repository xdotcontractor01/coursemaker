from manim import *
from pathlib import Path

class ImageTest(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Get absolute path
        img_path = Path(__file__).parent / "figures" / "chapter_01" / "fig_1-1.png"
        img_path = img_path.resolve()
        
        print(f"Loading image from: {img_path}")
        print(f"Image exists: {img_path.exists()}")
        
        title = Text("Testing Image Load", color=BLACK, font_size=36)
        title.to_edge(UP)
        
        figure = ImageMobject(str(img_path))
        print(f"Image loaded successfully")
        print(f"Image dimensions in Manim: {figure.width:.2f} x {figure.height:.2f}")
        
        figure.scale_to_fit_width(8)
        figure.move_to(ORIGIN)
        
        self.add(title, figure)
        self.wait(1)

