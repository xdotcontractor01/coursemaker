from manim import *

class SheetOrderProjectLengthAndDesignData(MovingCameraScene):
    def construct(self):
        self.camera.background_color = WHITE

        # Continuation from previous video
        continue_text = Text("Chapter 1: Beginning to Read Plans", color=BLUE_D, font_size=36, weight=BOLD)
        part_text = Text("Part 3 of 5 - Continuing...", color=GRAY, font_size=24)
        continue_text.to_edge(UP, buff=0.3)
        part_text.next_to(continue_text, DOWN, buff=0.2)
        
        self.play(FadeIn(continue_text), FadeIn(part_text))
        self.wait(0.5)
        self.play(FadeOut(continue_text), FadeOut(part_text))
        
        
        # Slide 1: [Introduction to Sheet Order]
        self.clear()  
        title = Text("Introduction to Sheet Order", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        content_group = VGroup()
        element1 = Rectangle(width=4, height=2.5, color=BLUE, fill_opacity=0.1)
        label1 = Text("Sheet Order in Highway Plans", color=BLACK, font_size=24)
        label1.move_to(element1)
        labeled_box = VGroup(element1, label1)
        content_group.add(labeled_box)

        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)

        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)

        self.clear()

        # Slide 2: [Understanding Project Length]
        self.clear()
        title = Text("Understanding Project Length", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        content_group = VGroup()
        element1 = Rectangle(width=4, height=2.5, color=BLUE, fill_opacity=0.1)
        label1 = Text("Project Length Defined", color=BLACK, font_size=24)
        label1.move_to(element1)
        labeled_box = VGroup(element1, label1)
        content_group.add(labeled_box)

        element2 = Rectangle(width=4, height=2.5, color=BLUE, fill_opacity=0.1)
        label2 = Text("Calculated from stationing", color=BLACK, font_size=24)
        label2.move_to(element2)
        content_group.add(element2)
        content_group.add(label2)

        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)

        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)

        self.clear()

        # Slide 3: [Design Data Overview]
        self.clear()
        title = Text("Design Data Overview", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        content_group = VGroup()
        element1 = Rectangle(width=4, height=1, color=BLUE, fill_opacity=0.1)
        label1 = Text("Key Design Data Elements", color=BLACK, font_size=24)
        label1.move_to(element1)
        labeled_box = VGroup(element1, label1)
        content_group.add(labeled_box)

        element2 = Rectangle(width=4, height=1, color=BLUE, fill_opacity=0.1)
        label2 = Text("Design Speed, Posted Speed, Terrain Type", color=BLACK, font_size=24)
        label2.move_to(element2)
        content_group.add(element2)
        content_group.add(label2)

        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)

        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)

        self.clear()

        # Slide 4: [Importance of Design Data]
        self.clear()
        title = Text("Importance of Design Data", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        content_group = VGroup()
        element1 = Rectangle(width=4, height=1, color=BLUE, fill_opacity=0.1)
        label1 = Text("Impact on Design Decisions", color=BLACK, font_size=24)
        label1.move_to(element1)
        labeled_box = VGroup(element1, label1)
        content_group.add(labeled_box)

        element2 = Rectangle(width=4, height=1, color=BLUE, fill_opacity=0.1)
        label2 = Text("Design decisions rely on accurate data.", color=BLACK, font_size=24)
        label2.move_to(element2)
        content_group.add(element2)
        content_group.add(label2)

        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)

        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        self.wait(2)

        self.clear()

        # Slide 5: [Conclusion and Review]
        self.clear()
        title = Text("Conclusion and Review", color=BLUE_D, font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        content_group = VGroup()
        element1 = Rectangle(width=4, height=1, color=BLUE, fill_opacity=0.1)
        label1 = Text("Recap of Key Points", color=BLACK, font_size=24)
        label1.move_to(element1)
        labeled_box = VGroup(element1, label1)
        content_group.add(labeled_box)

        element2 = Rectangle(width=4, height=1, color=BLUE, fill_opacity=0.1)
        label2 = Text("1. Sheet Order\n2. Project Length\n3. Design Data", color=BLACK, font_size=24)
        label2.move_to(element2)
        content_group.add(element2)
        content_group.add(label2)

        content_group.arrange(DOWN, buff=0.5)
        content_group.next_to(title, DOWN, buff=0.8)

        self.play(LaggedStart(*[GrowFromCenter(item) for item in content_group], lag_ratio=0.2))
        
        # Transition to next video
        self.clear()
        next_text = Text("Coming up next...", color=GRAY, font_size=28)
        next_topic_text = Text("Errors or Omissions", color=BLUE_D, font_size=32, weight=BOLD)
        next_group = VGroup(next_text, next_topic_text).arrange(DOWN, buff=0.4)
        next_group.move_to(ORIGIN)
        
        self.play(FadeIn(next_group))
        self.wait(1.5)
        self.play(FadeOut(next_group))
        