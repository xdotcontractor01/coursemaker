from manim import *

class RequirementsAndSpecificationsScale(MovingCameraScene):
    def construct(self):
        self.camera.background_color = WHITE

        # Continuation from previous video
        continue_text = Text("Chapter 1: Beginning to Read Plans", color=BLUE_D, font_size=36, weight=BOLD)
        part_text = Text("Part 2 of 5 - Continuing...", color=GRAY, font_size=24)
        continue_text.to_edge(UP, buff=0.3)
        part_text.next_to(continue_text, DOWN, buff=0.2)
        
        self.play(FadeIn(continue_text), FadeIn(part_text))
        self.wait(0.5)
        self.play(FadeOut(continue_text), FadeOut(part_text))
        
        
        # Slide 1: [Introduction to Requirements and Specifications]
        self.clear()
        title = Text("Requirements and Specifications", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        subtitle = Text("Understanding the foundation of highway plans.", color=BLACK, font_size=24)
        subtitle.next_to(title, DOWN, buff=0.8)
        self.play(Write(subtitle))
        self.wait(2)
        
        self.clear()

        # Slide 2: [Hierarchy of Contract Documents]
        self.clear()
        title = Text("Order of Precedence", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-9.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)
        self.play(FadeIn(figure))
        self.wait(2)
        
        self.clear()

        # Slide 3: [Understanding Scale]
        self.clear()
        title = Text("Importance of Scale", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        subtitle = Text("Engineering vs. Architectural Scales", color=BLACK, font_size=24)
        subtitle.next_to(title, DOWN, buff=0.8)
        self.play(Write(subtitle))
        self.wait(2)
        
        self.clear()

        # Slide 4: [Civil Engineer's Scale]
        self.clear()
        title = Text("Civil Engineer's Scale", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        scale_info = Text("1 inch = X feet (10, 20, 30, etc.)", color=BLACK, font_size=24)
        scale_info.next_to(title, DOWN, buff=0.8)
        self.play(Write(scale_info))
        self.wait(2)
        
        self.clear()

        # Slide 5: [Bar Scale]
        self.clear()
        title = Text("Bar Scale Overview", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        bar_scale_info = Text("Quick reference for measurements.", color=BLACK, font_size=24)
        bar_scale_info.next_to(title, DOWN, buff=0.8)
        self.play(Write(bar_scale_info))
        self.wait(2)

        self.clear()

        # Slide 6: [Civil Engineer's Scale - Detailed]
        self.clear()
        title = Text("Civil Engineer's Scale", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-4.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)
        
        callout_arrow_1 = Arrow(start=UP * 2 + LEFT * 4, end=RIGHT * 1 + UP * 1, color=ORANGE)
        callout_label_1 = Text("10 Divisions", color=ORANGE, font_size=24, weight=BOLD)
        callout_label_1.next_to(callout_arrow_1.get_start(), UP)
        
        callout_arrow_2 = Arrow(start=UP * 2 + LEFT * 1, end=RIGHT * 3 + UP * 1, color=ORANGE)
        callout_label_2 = Text("Scale Markings", color=ORANGE, font_size=24, weight=BOLD)
        callout_label_2.next_to(callout_arrow_2.get_start(), UP)
        
        self.play(FadeIn(figure))
        self.play(Create(callout_arrow_1), Write(callout_label_1))
        self.play(Create(callout_arrow_2), Write(callout_label_2))
        self.wait(2)

        self.clear()

        # Slide 7: [Bar Scale - Detailed]
        self.clear()
        title = Text("Bar Scale", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-6.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)
        
        callout_arrow_1 = Arrow(start=UP * 2 + LEFT * 4, end=RIGHT * 1 + UP * 1, color=ORANGE)
        callout_label_1 = Text("0-50-100 feet", color=ORANGE, font_size=24, weight=BOLD)
        callout_label_1.next_to(callout_arrow_1.get_start(), UP)
        
        callout_arrow_2 = Arrow(start=UP * 2 + LEFT * 1, end=RIGHT * 3 + UP * 1, color=ORANGE)
        callout_label_2 = Text("Graphical Scale", color=ORANGE, font_size=24, weight=BOLD)
        callout_label_2.next_to(callout_arrow_2.get_start(), UP)

        self.play(FadeIn(figure))
        self.play(Create(callout_arrow_1), Write(callout_label_1))
        self.play(Create(callout_arrow_2), Write(callout_label_2))
        
        # Transition to next video
        self.clear()
        next_text = Text("Coming up next...", color=GRAY, font_size=28)
        next_topic_text = Text("Sheet Order & Project Length", color=BLUE_D, font_size=32, weight=BOLD)
        next_group = VGroup(next_text, next_topic_text).arrange(DOWN, buff=0.4)
        next_group.move_to(ORIGIN)
        
        self.play(FadeIn(next_group))
        self.wait(1.5)
        self.play(FadeOut(next_group))
        