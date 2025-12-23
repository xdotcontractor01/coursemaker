from manim import *

class ErrorsOrOmissions(MovingCameraScene):
    def construct(self):
        self.camera.background_color = WHITE

        # Continuation from previous video
        continue_text = Text("Chapter 1: Beginning to Read Plans", color=BLUE_D, font_size=36, weight=BOLD)
        part_text = Text("Part 4 of 5 - Continuing...", color=GRAY, font_size=24)
        continue_text.to_edge(UP, buff=0.3)
        part_text.next_to(continue_text, DOWN, buff=0.2)
        
        self.play(FadeIn(continue_text), FadeIn(part_text))
        self.wait(0.5)
        self.play(FadeOut(continue_text), FadeOut(part_text))
        
        
        # Slide 1: Introduction to Errors or Omissions
        self.clear()
        title = Text("Errors or Omissions", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        content_group = VGroup()
        subtitle = Text("Understanding discrepancies in highway plans.", color=BLACK, font_size=24)
        content_group.add(subtitle)
        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)
        
        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)
        
        self.clear()

        # Slide 2: Reporting Errors
        self.clear()
        title = Text("Reporting Errors", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        content_group = VGroup()
        report_text = Text("Report immediately to the Engineer.", color=BLACK, font_size=24)
        spec_text = Text("Subsection 104.03 of Standard Specifications.", color=BLACK, font_size=24)
        content_group.add(report_text, spec_text)
        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)
        
        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)
        
        self.clear()

        # Slide 3: Avoiding Costly Rework
        self.clear()
        title = Text("Avoiding Costly Rework", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        content_group = VGroup()
        prevent_text = Text("Prevent costly rework.", color=BLACK, font_size=24)
        communication_text = Text("Clear communication is key.", color=BLACK, font_size=24)
        content_group.add(prevent_text, communication_text)
        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)
        
        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)
        
        self.clear()

        # Slide 4: Documenting Discrepancies
        self.clear()
        title = Text("Documenting Discrepancies", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        content_group = VGroup()
        document_text = Text("Document discrepancies in writing.", color=BLACK, font_size=24)
        resolution_text = Text("Obtain resolution before proceeding.", color=BLACK, font_size=24)
        content_group.add(document_text, resolution_text)
        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)
        
        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)
        
        self.clear()

        # Slide 5: Conclusion
        self.clear()
        title = Text("Conclusion", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        content_group = VGroup()
        key_takeaways_text = Text("Key Takeaways", color=BLACK, font_size=24)
        actions_text = Text("Report, document, and communicate effectively.", color=BLACK, font_size=24)
        content_group.add(key_takeaways_text, actions_text)
        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)
        
        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)
        
        self.clear()

        # Slide 6: Typical Roadway Cross Section
        self.clear()
        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-9.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)
        
        frame = SurroundingRectangle(figure, color=BLUE_D, buff=0.1, stroke_width=2)
        
        callout_arrow1 = Arrow(start=RIGHT * 4 + DOWN * 2, end=RIGHT * 1.5 + UP * 0.5, color=ORANGE, stroke_width=3)
        callout_label1 = Text("Travel Lanes", color=ORANGE, font_size=24, weight=BOLD)
        callout_label1.next_to(callout_arrow1.get_start(), RIGHT)
        
        callout_arrow2 = Arrow(start=RIGHT * 3 + DOWN * 4, end=RIGHT * 1 + DOWN * 2.5, color=ORANGE, stroke_width=3)
        callout_label2 = Text("Right of Way", color=ORANGE, font_size=24, weight=BOLD)
        callout_label2.next_to(callout_arrow2.get_start(), RIGHT)

        self.play(FadeIn(figure), Create(frame))
        self.wait(1)
        self.play(Create(callout_arrow1), Write(callout_label1))
        self.play(Indicate(callout_label1, color=RED))
        self.wait(1)
        self.play(Create(callout_arrow2), Write(callout_label2))
        self.play(Indicate(callout_label2, color=RED))
        
        # Transition to next video
        self.clear()
        next_text = Text("Coming up next...", color=GRAY, font_size=28)
        next_topic_text = Text("Cover Sheet", color=BLUE_D, font_size=32, weight=BOLD)
        next_group = VGroup(next_text, next_topic_text).arrange(DOWN, buff=0.4)
        next_group.move_to(ORIGIN)
        
        self.play(FadeIn(next_group))
        self.wait(1.5)
        self.play(FadeOut(next_group))
        