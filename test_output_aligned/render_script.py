from manim import *

class BridgeDesignManual(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Slide 1: Title Slide
        title = Text("Bridge Design Manual Overview", color=BLACK, font_size=40).to_edge(UP)
        
        border_top = Line(start=(-6, 3, 0), end=(6, 3, 0), color=BLUE, stroke_width=5)
        border_bottom = Line(start=(-6, -3, 0), end=(6, -3, 0), color=BLUE, stroke_width=5)
        border_left = Line(start=(-6, 3, 0), end=(-6, -3, 0), color=BLUE, stroke_width=5)
        border_right = Line(start=(6, 3, 0), end=(6, -3, 0), color=BLUE, stroke_width=5)
        
        border = VGroup(border_top, border_bottom, border_left, border_right)
        
        self.play(Write(title), run_time=1)
        self.play(Create(border), run_time=1.5)
        self.wait(25)
        self.play(FadeOut(VGroup(title, border)), run_time=1)

        # Slide 2: Bridge Components
        title = Text("Bridge Components", color=BLACK, font_size=40).to_edge(UP)

        # Visual diagram of bridge structure
        beam = Rectangle(width=6, height=0.5, color=BLACK, fill_opacity=0.2, stroke_width=3)
        bearing_left = Circle(radius=0.4, color=BLUE, fill_opacity=0.6, stroke_width=2).next_to(beam, DOWN+LEFT, buff=0.3)
        bearing_right = Circle(radius=0.4, color=BLUE, fill_opacity=0.6, stroke_width=2).next_to(beam, DOWN+RIGHT, buff=0.3)

        # Labels with arrows pointing to parts
        beam_label = Text("Beam", color=BLACK, font_size=24).next_to(beam, UP, buff=0.3)
        bearing_label = Text("Bearings", color=BLUE, font_size=24).next_to(bearing_left, DOWN, buff=0.3)

        # Bullet points on the side
        bullets = VGroup(
            Text("• Load distribution", color=BLACK, font_size=20),
            Text("• Structural support", color=BLACK, font_size=20),
            Text("• Connection points", color=BLACK, font_size=20)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(LEFT).shift(DOWN*0.5)

        diagram = VGroup(beam, bearing_left, bearing_right, beam_label, bearing_label)

        # [AUTO-INJECTED] Image for slide 2 - split_right layout
        img_2 = ImageMobject(r"test_output\images\slide_2_image.jpg")
        # Position image in designated region (split_right)
        # Region: x=[0.40, 6.51], y=[-3.40, 2.30]
        img_2_max_width = 6.11
        img_2_max_height = 5.70
        
        # Scale to fit region while maintaining aspect ratio
        if img_2.width / img_2_max_width > img_2.height / img_2_max_height:
            img_2.set_width(img_2_max_width)
        else:
            img_2.set_height(img_2_max_height)
        
        # Center in region
        img_2.move_to(RIGHT * 3.46 + UP * -0.55)
        
        # Add rounded corners and border for professional look
        img_2.z_index = -10  # Behind content but above background
        self.play(FadeIn(img_2), run_time=0.5)

        self.play(Write(title), run_time=1)
        self.play(Create(diagram), run_time=2)
        self.play(Write(bullets), run_time=1.5)
        self.wait(25)
        self.play(FadeOut(Group(title, diagram, bullets, img_2)), run_time=1)

        # Slide 3: Inspection Process
        title = Text("Inspection Process", color=BLACK, font_size=40).to_edge(UP)

        # Flow diagram with steps
        step1_box = Rectangle(width=2.5, height=1.2, color=BLUE, fill_opacity=0.3, stroke_width=2).shift(LEFT*4)
        step2_box = Rectangle(width=2.5, height=1.2, color=BLUE, fill_opacity=0.3, stroke_width=2)
        step3_box = Rectangle(width=2.5, height=1.2, color=BLUE, fill_opacity=0.3, stroke_width=2).shift(RIGHT*4)

        # Arrows connecting steps
        arrow1 = Arrow(step1_box.get_right(), step2_box.get_left(), color=GRAY, stroke_width=3)
        arrow2 = Arrow(step2_box.get_right(), step3_box.get_left(), color=GRAY, stroke_width=3)

        # Step labels inside boxes
        step1_text = VGroup(
            Text("STEP 1", color=BLACK, font_size=16, weight=BOLD),
            Text("Verify", color=BLACK, font_size=20)
        ).arrange(DOWN, buff=0.1).move_to(step1_box)

        step2_text = VGroup(
            Text("STEP 2", color=BLACK, font_size=16, weight=BOLD),
            Text("Inspect", color=BLACK, font_size=20)
        ).arrange(DOWN, buff=0.1).move_to(step2_box)

        step3_text = VGroup(
            Text("STEP 3", color=BLACK, font_size=16, weight=BOLD),
            Text("Report", color=BLACK, font_size=20)
        ).arrange(DOWN, buff=0.1).move_to(step3_box)

        flow = VGroup(step1_box, step2_box, step3_box, arrow1, arrow2, step1_text, step2_text, step3_text)

        # [AUTO-INJECTED] Image for slide 3 - split_left layout
        img_3 = ImageMobject(r"test_output\images\slide_3_image.png")
        # Position image in designated region (split_left)
        # Region: x=[-6.51, -0.40], y=[-3.40, 2.30]
        img_3_max_width = 6.11
        img_3_max_height = 5.70
        
        # Scale to fit region while maintaining aspect ratio
        if img_3.width / img_3_max_width > img_3.height / img_3_max_height:
            img_3.set_width(img_3_max_width)
        else:
            img_3.set_height(img_3_max_height)
        
        # Center in region
        img_3.move_to(RIGHT * -3.46 + UP * -0.55)
        
        # Add rounded corners and border for professional look
        img_3.z_index = -10  # Behind content but above background
        self.play(FadeIn(img_3), run_time=0.5)

        self.play(Write(title), run_time=1)
        self.play(Create(flow), run_time=2.5)
        self.wait(25)
        self.play(FadeOut(Group(title, flow, img_3)), run_time=1)

        # Slide 4: Safety Requirements
        title = Text("Safety Requirements", color=BLACK, font_size=40).to_edge(UP)

        # Warning icon (triangle with exclamation)
        warning_triangle = Polygon(
            [0, 0.8, 0], [-0.7, -0.4, 0], [0.7, -0.4, 0],
            color=ORANGE, fill_opacity=0.3, stroke_width=3
        ).shift(LEFT*4 + UP*0.5)
        exclamation = Text("!", color=ORANGE, font_size=60, weight=BOLD).move_to(warning_triangle)

        # Safety checklist with checkmarks
        check1 = VGroup(
            Circle(radius=0.15, color=BLUE, fill_opacity=0.5),
            Text("✓", color=BLUE, font_size=20)
        ).arrange(RIGHT, buff=0).move_to(RIGHT * -1.60 + UP*1)
        text1 = Text("PPE Required", color=BLACK, font_size=24).next_to(check1, RIGHT, buff=0.3)

        check2 = VGroup(
            Circle(radius=0.15, color=BLUE, fill_opacity=0.5),
            Text("✓", color=BLUE, font_size=20)
        ).arrange(RIGHT, buff=0).move_to(RIGHT * -1.60)
        text2 = Text("Torque Calibration", color=BLACK, font_size=24).next_to(check2, RIGHT, buff=0.3)

        check3 = VGroup(
            Circle(radius=0.15, color=BLUE, fill_opacity=0.5),
            Text("✓", color=BLUE, font_size=20)
        ).arrange(RIGHT, buff=0).move_to(RIGHT * -1.60 + DOWN*1)
        text3 = Text("Documentation", color=BLACK, font_size=24).next_to(check3, RIGHT, buff=0.3)

        checklist = VGroup(check1, text1, check2, text2, check3, text3)
        safety_icon = VGroup(warning_triangle, exclamation)

        # [AUTO-INJECTED] Image for slide 4 - sidebar_right layout
        img_4 = ImageMobject(r"test_output\images\slide_4_image.jpg")
        # Position image in designated region (sidebar_right)
        # Region: x=[3.01, 6.51], y=[-3.40, 2.30]
        img_4_max_width = 3.50
        img_4_max_height = 5.70
        
        # Scale to fit region while maintaining aspect ratio
        if img_4.width / img_4_max_width > img_4.height / img_4_max_height:
            img_4.set_width(img_4_max_width)
        else:
            img_4.set_height(img_4_max_height)
        
        # Center in region
        img_4.move_to(RIGHT * 4.76 + UP * -0.55)
        
        # Add rounded corners and border for professional look
        img_4.z_index = -10  # Behind content but above background
        self.play(FadeIn(img_4), run_time=0.5)

        self.play(Write(title), run_time=1)
        self.play(Create(safety_icon), run_time=1)
        self.play(Create(checklist), run_time=2)
        self.wait(25)
        self.play(FadeOut(Group(title, safety_icon, checklist, img_4)), run_time=1)

        # Slide 5: Superstructure Verification
        title = Text("Superstructure Verification", color=BLACK, font_size=40).to_edge(UP)

        # Diagram showing verification steps
        verification_box = Rectangle(width=6, height=0.5, color=BLUE, fill_opacity=0.3, stroke_width=2)
        elevation_check = Circle(radius=0.4, color=BLACK, fill_opacity=0.6, stroke_width=2).next_to(verification_box, DOWN+LEFT, buff=0.3)
        alignment_check = Circle(radius=0.4, color=BLACK, fill_opacity=0.6, stroke_width=2).next_to(verification_box, DOWN+RIGHT, buff=0.3)

        # Labels for checks
        elevation_label = Text("Verify Elevation", color=BLACK, font_size=24).next_to(elevation_check, DOWN, buff=0.3)
        alignment_label = Text("Align Layout", color=BLACK, font_size=24).next_to(alignment_check, DOWN, buff=0.3)

        # Arrows indicating process
        arrow1 = Arrow(verification_box.get_bottom(), elevation_check.get_top(), color=GRAY, stroke_width=3)
        arrow2 = Arrow(verification_box.get_bottom(), alignment_check.get_top(), color=GRAY, stroke_width=3)

        diagram = VGroup(verification_box, elevation_check, alignment_check, elevation_label, alignment_label, arrow1, arrow2)

        # [AUTO-INJECTED] Image for slide 5 - split_right layout
        img_5 = ImageMobject(r"test_output\images\slide_5_image.png")
        # Position image in designated region (split_right)
        # Region: x=[0.40, 6.51], y=[-3.40, 2.30]
        img_5_max_width = 6.11
        img_5_max_height = 5.70
        
        # Scale to fit region while maintaining aspect ratio
        if img_5.width / img_5_max_width > img_5.height / img_5_max_height:
            img_5.set_width(img_5_max_width)
        else:
            img_5.set_height(img_5_max_height)
        
        # Center in region
        img_5.move_to(RIGHT * 3.46 + UP * -0.55)
        
        # Add rounded corners and border for professional look
        img_5.z_index = -10  # Behind content but above background
        self.play(FadeIn(img_5), run_time=0.5)

        self.play(Write(title), run_time=1)
        self.play(Create(diagram), run_time=2)
        self.wait(25)
        self.play(FadeOut(Group(title, diagram, img_5)), run_time=1)

        # Slide 6: Conclusion
        title = Text("Conclusion", color=BLACK, font_size=40).to_edge(UP)

        # Summary diagram
        summary_box = Rectangle(width=6, height=0.5, color=BLUE, fill_opacity=0.3, stroke_width=2)
        safety_check = Circle(radius=0.4, color=BLACK, fill_opacity=0.6, stroke_width=2).next_to(summary_box, DOWN+LEFT, buff=0.3)
        compliance_check = Circle(radius=0.4, color=BLACK, fill_opacity=0.6, stroke_width=2).next_to(summary_box, DOWN+RIGHT, buff=0.3)

        # Labels for summary
        safety_label = Text("Ensure Safety", color=BLACK, font_size=24).next_to(safety_check, DOWN, buff=0.3)
        compliance_label = Text("Maintain Compliance", color=BLACK, font_size=24).next_to(compliance_check, DOWN, buff=0.3)

        # Arrows indicating summary points
        arrow1 = Arrow(summary_box.get_bottom(), safety_check.get_top(), color=GRAY, stroke_width=3)
        arrow2 = Arrow(summary_box.get_bottom(), compliance_check.get_top(), color=GRAY, stroke_width=3)

        summary_diagram = VGroup(summary_box, safety_check, compliance_check, safety_label, compliance_label, arrow1, arrow2)

        self.play(Write(title), run_time=1)
        self.play(Create(summary_diagram), run_time=2)
        self.wait(25)
        self.play(FadeOut(VGroup(title, summary_diagram)), run_time=1)