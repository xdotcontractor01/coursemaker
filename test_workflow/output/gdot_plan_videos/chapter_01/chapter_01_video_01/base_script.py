from manim import *

class GeneralInformationPlansRevisedAndPlansCompleted(MovingCameraScene):
    def construct(self):
        self.camera.background_color = WHITE

        # Chapter Intro
        chapter_title = Text("Chapter 1: Beginning to Read Plans", color=BLUE_D, font_size=48, weight=BOLD)
        chapter_title.move_to(ORIGIN)
        subtitle = Text("Part 1 of 5", color=GRAY, font_size=28)
        subtitle.next_to(chapter_title, DOWN, buff=0.5)
        
        self.play(Write(chapter_title))
        self.play(FadeIn(subtitle))
        self.wait(1)
        self.play(FadeOut(chapter_title), FadeOut(subtitle))
        
        
        # Slide 1: [Introduction to Highway Plans]
        self.clear()
        title = Text("Introduction to Highway Plans", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Load and display the figure
        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-1.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)
        
        # Create callout annotations
        callout_group = VGroup()
        points_to_highlight = [
            ("Project Title", RIGHT * 4 + UP * 2, RIGHT * 1.5 + UP * 0.5),
            ("Location Map", LEFT * 3 + DOWN * 1, LEFT * 1 + DOWN * 0.5),
            ("Index of Sheets", RIGHT * 3 + DOWN * 1, RIGHT * 1 + DOWN * 0.5),
            ("Project Number", LEFT * 3 + UP * 2, LEFT * 1 + UP * 1.5),
        ]
        for label_text, label_pos, arrow_end in points_to_highlight:
            arrow = Arrow(label_pos, arrow_end, color=ORANGE, stroke_width=2)
            label = Text(label_text, color=ORANGE, font_size=20)
            label.next_to(arrow.get_start(), DOWN if label_pos[1] > 0 else UP)
            callout_group.add(VGroup(arrow, label))

        # Animate figure appearance with callouts
        self.play(FadeIn(figure))
        self.wait(1)
        self.play(LaggedStart(*[Create(c) for c in callout_group], lag_ratio=0.3))
        self.wait(2)
        
        self.clear()

        # Slide 2: [Understanding Contract Documents]
        self.clear()
        title = Text("Understanding Contract Documents", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Load and display the second figure
        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-2.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)
        self.play(FadeIn(figure))
        self.wait(2)

        self.clear()

        # Slide 3: [Plans Revised Overview]
        self.clear()
        title = Text("Plans Revised Overview", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        # Load and display the third figure
        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-8.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)
        self.play(FadeIn(figure))
        self.wait(2)

        self.clear()

        # Slide 4: [Key Components of Revision Sheets]
        self.clear()
        title = Text("Key Components of Revision Sheets", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        # Load and display the fourth figure
        figure = ImageMobject(r"C:\Users\home\coursemaker\test_workflow\figures\chapter_01\fig_1-9.png")
        figure.scale_to_fit_width(9)
        figure.move_to(ORIGIN)
        self.play(FadeIn(figure))
        self.wait(2)

        self.clear()

        # Slide 5: [Conclusion and Review]
        self.clear()
        title = Text("Conclusion and Review", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        # Summary text
        summary_text = Text("Summary of Key Points", color=BLACK, font_size=24)
        summary_text.next_to(title, DOWN, buff=0.5)
        
        points = VGroup(
            Text("1. Understand contract documents", color=BLACK, font_size=20),
            Text("2. Recognize revision processes", color=BLACK, font_size=20),
        )
        points.arrange(DOWN, buff=0.2)
        points.next_to(summary_text, DOWN, buff=0.5)

        self.play(FadeIn(summary_text))
        self.play(LaggedStart(*[Write(item) for item in points], lag_ratio=0.3))
        
        # Transition to next video
        self.clear()
        next_text = Text("Coming up next...", color=GRAY, font_size=28)
        next_topic_text = Text("Requirements and Specifications & Scale", color=BLUE_D, font_size=32, weight=BOLD)
        next_group = VGroup(next_text, next_topic_text).arrange(DOWN, buff=0.4)
        next_group.move_to(ORIGIN)
        
        self.play(FadeIn(next_group))
        self.wait(1.5)
        self.play(FadeOut(next_group))
        