from manim import *

class CoverSheet(MovingCameraScene):
    def construct(self):
        self.camera.background_color = WHITE

        # Continuation from previous video
        continue_text = Text("Chapter 1: Beginning to Read Plans", color=BLUE_D, font_size=36, weight=BOLD)
        part_text = Text("Part 5 of 5 - Continuing...", color=GRAY, font_size=24)
        continue_text.to_edge(UP, buff=0.3)
        part_text.next_to(continue_text, DOWN, buff=0.2)
        
        self.play(FadeIn(continue_text), FadeIn(part_text))
        self.wait(0.5)
        self.play(FadeOut(continue_text), FadeOut(part_text))
        
        
        # Slide 1: Introduction to Cover Sheet
        self.clear()
        title = Text("Introduction to Cover Sheet", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        content_group = VGroup()
        element1 = Rectangle(width=4, height=2.5, color=BLUE, fill_opacity=0.1)
        label1 = Text("Cover Sheet Overview", color=BLACK, font_size=24)
        label1.move_to(element1)
        labeled_box = VGroup(element1, label1)
        content_group.add(labeled_box)

        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)
        self.play(GrowFromCenter(labeled_box))
        self.wait(2)

        self.clear()

        # Slide 2: Key Components of the Cover Sheet
        self.clear()
        title = Text("Key Components of the Cover Sheet", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        project_number = Text("Project Number, Route, County", color=BLACK, font_size=24)
        project_limits = Text("Project Limits", color=BLACK, font_size=24)

        content_group = VGroup(project_number, project_limits)
        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)

        self.play(LaggedStart(*[Write(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)

        self.clear()

        # Slide 3: Project Location Sketch
        self.clear()
        title = Text("Project Location Sketch", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-2.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)

        self.play(FadeIn(figure))
        self.wait(2)

        self.clear()

        # Slide 4: Layout View
        self.clear()
        title = Text("Layout View", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-3.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)

        self.play(FadeIn(figure))
        self.wait(2)

        self.clear()

        # Slide 5: Sheet Identification
        self.clear()
        title = Text("Sheet Identification", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-4.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)

        self.play(FadeIn(figure))
        
        # Chapter conclusion
        self.clear()
        complete_text = Text("Chapter 1 Complete!", color=GREEN_D, font_size=40, weight=BOLD)
        summary_text = Text("You've learned the basics of reading highway plans", color=BLACK, font_size=24)
        complete_group = VGroup(complete_text, summary_text).arrange(DOWN, buff=0.5)
        complete_group.move_to(ORIGIN)
        
        self.play(GrowFromCenter(complete_text))
        self.play(FadeIn(summary_text))
        self.wait(2)
        