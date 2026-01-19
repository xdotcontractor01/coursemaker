# Alternative Video Creation Approaches

If Manim is not available or you prefer different tools, here are two alternative approaches to create the Pages 5-7 explainer video.

---

## Approach 1: Static Slides + FFmpeg Assembly

### Overview
Generate static PNG frames using Python's Pillow library, then assemble them into a video using FFmpeg.

### Pros
- ✅ **No Manim dependency** - uses standard Python libraries
- ✅ **Lightweight** - minimal installation requirements
- ✅ **Fast rendering** - no complex animations to compute
- ✅ **Full control** - pixel-perfect positioning
- ✅ **Cross-platform** - works on any system with Python and FFmpeg

### Cons
- ❌ **No smooth animations** - only static frames with cuts/fades
- ❌ **Manual timing** - must calculate frame counts manually
- ❌ **More code** - requires manual drawing of all elements
- ❌ **Less professional** - lacks fluid motion of Manim
- ❌ **No text animations** - text appears instantly, not written

---

### Implementation

#### Step 1: Install Dependencies

```bash
pip install Pillow requests
# FFmpeg must be installed separately (see TROUBLESHOOTING.md)
```

#### Step 2: Create Frame Generator Script

Create `generate_slides.py`:

```python
#!/usr/bin/env python3
"""Generate static slides for Pages 5-7 explainer video"""

from PIL import Image, ImageDraw, ImageFont
import requests
from pathlib import Path

# Configuration
OUTPUT_DIR = Path("frames")
ASSETS_DIR = Path("assets/images")
WIDTH, HEIGHT = 1920, 1080
FPS = 30
BACKGROUND_COLOR = (25, 25, 35)  # Dark blue-gray

# Download images (same as Manim script)
IMAGE_URLS = {
    "figure_1_3": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/884ac0596cdd7c2b789731a8a7bdb94f9a4a495c38fd39e66c7798451e388708.jpg",
    "figure_1_4": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/64f16d468bc94be67e798fa7fe9b0f7c8b0b3708ea2a20af8049fb936bd2d196.jpg",
    "figure_1_9": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/25aa20b11bc17322942fbc4764af7c95258df8b9344efb9fe6dabc401aa15195.jpg",
    "figure_1_10": "https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/a76db50d8c607aa0d9ea60c66f0dc3f1c971e837b6d2559b99083f4b3a0fc7c9.jpg",
}

def download_images():
    """Download images if not cached"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in IMAGE_URLS.items():
        output_path = ASSETS_DIR / f"{name}.jpg"
        if not output_path.exists():
            print(f"Downloading {name}...")
            response = requests.get(url, timeout=30)
            output_path.write_bytes(response.content)

def create_base_slide():
    """Create blank slide with background"""
    img = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
    return img

def add_title(img, text, y_position=200, font_size=80, color=(100, 150, 255)):
    """Add centered title text to slide"""
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x_position = (WIDTH - text_width) // 2
    
    draw.text((x_position, y_position), text, fill=color, font=font)
    return img

def add_bullet_points(img, bullets, start_y=400, font_size=40):
    """Add bullet point list to slide"""
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    y = start_y
    for bullet in bullets:
        draw.text((200, y), f"• {bullet}", fill=(255, 255, 255), font=font)
        y += font_size + 30
    
    return img

def add_image_to_slide(img, image_path, position, scale=0.6):
    """Add downloaded image to slide"""
    source_img = Image.open(image_path)
    new_size = (int(source_img.width * scale), int(source_img.height * scale))
    source_img = source_img.resize(new_size, Image.Resampling.LANCZOS)
    img.paste(source_img, position)
    return img

# ============================================================================
# SLIDE GENERATION FUNCTIONS
# ============================================================================

def generate_slide_1_title():
    """Slide 1: Title (0-5s) = 150 frames"""
    frames = []
    for i in range(150):  # 5 seconds at 30 fps
        slide = create_base_slide()
        slide = add_title(slide, "Highway Plan Reading", y_position=300)
        
        draw = ImageDraw.Draw(slide)
        try:
            font = ImageFont.truetype("arial.ttf", 50)
        except:
            font = ImageFont.load_default()
        draw.text((600, 500), "Understanding Cover Sheet Elements", 
                  fill=(200, 200, 200), font=font)
        draw.text((800, 600), "Pages 5-7", fill=(150, 150, 150), font=font)
        
        frames.append(slide)
    return frames

def generate_slide_2_location():
    """Slide 2: Project Location Sketch (5-18s) = 390 frames"""
    frames = []
    for i in range(390):
        slide = create_base_slide()
        slide = add_title(slide, "Project Location Sketch", y_position=100, 
                          font_size=60, color=(255, 200, 50))
        
        # Add image
        img_path = ASSETS_DIR / "figure_1_3.jpg"
        if img_path.exists():
            slide = add_image_to_slide(slide, img_path, (100, 250), scale=0.5)
        
        # Add bullets
        bullets = [
            "Shows general geographical area",
            "Indicates project limits",
            "Located in upper left corner"
        ]
        slide = add_bullet_points(slide, bullets, start_y=350)
        
        frames.append(slide)
    return frames

def generate_slide_3_layout():
    """Slide 3: Layout View (18-30s) = 360 frames"""
    frames = []
    for i in range(360):
        slide = create_base_slide()
        slide = add_title(slide, "Layout View", y_position=100, 
                          font_size=60, color=(255, 200, 50))
        
        img_path = ASSETS_DIR / "figure_1_4.jpg"
        if img_path.exists():
            slide = add_image_to_slide(slide, img_path, (100, 250), scale=0.6)
        
        bullets = [
            "Plan view from above (like flying over)",
            "Shows beginning station",
            "Shows ending station"
        ]
        slide = add_bullet_points(slide, bullets, start_y=700)
        
        frames.append(slide)
    return frames

def generate_slide_4_sheet_id():
    """Slide 4: Sheet Identification (30-43s) = 390 frames"""
    frames = []
    for i in range(390):
        slide = create_base_slide()
        slide = add_title(slide, "Sheet Identification Box", y_position=100,
                          font_size=60, color=(255, 200, 50))
        
        # Draw table manually
        draw = ImageDraw.Draw(slide)
        table_x, table_y = 300, 300
        col_width, row_height = 350, 80
        
        # Headers
        headers = ["STATE", "PROJECT NO.", "SHEET NO.", "TOTAL"]
        for i, header in enumerate(headers):
            x = table_x + i * col_width
            draw.rectangle([x, table_y, x + col_width, table_y + row_height], 
                           outline=(255, 255, 255), width=2)
            draw.text((x + 10, table_y + 20), header, fill=(255, 255, 255))
        
        # Data row
        data = ["GA.", "STP-IM-022-1(26)", "1", "770"]
        for i, value in enumerate(data):
            x = table_x + i * col_width
            y = table_y + row_height
            draw.rectangle([x, y, x + col_width, y + row_height],
                           outline=(255, 255, 255), width=2)
            draw.text((x + 10, y + 20), value, fill=(255, 255, 255))
        
        # Description
        try:
            font = ImageFont.truetype("arial.ttf", 35)
        except:
            font = ImageFont.load_default()
        draw.text((300, 550), "Located in upper right corner of every sheet",
                  fill=(200, 200, 200), font=font)
        
        frames.append(slide)
    return frames

def generate_slide_5_scale():
    """Slide 5: Scale (43-58s) = 450 frames"""
    frames = []
    for i in range(450):
        slide = create_base_slide()
        slide = add_title(slide, "Engineering Scale", y_position=80,
                          font_size=60, color=(255, 200, 50))
        
        # Add scale images
        img1_path = ASSETS_DIR / "figure_1_9.jpg"
        img2_path = ASSETS_DIR / "figure_1_10.jpg"
        
        if img1_path.exists():
            slide = add_image_to_slide(slide, img1_path, (100, 200), scale=0.4)
        if img2_path.exists():
            slide = add_image_to_slide(slide, img2_path, (100, 500), scale=0.4)
        
        bullets = [
            "Divisions: 10, 20, 30, 40, 50, 60 per inch",
            "Common: 1\" = 10 feet, 1\" = 20 feet",
            "Multiples: 1\" = 100 feet, 1\" = 1000 feet"
        ]
        slide = add_bullet_points(slide, bullets, start_y=250)
        
        frames.append(slide)
    return frames

def generate_slide_6_summary():
    """Slide 6: Summary (58-65s) = 210 frames"""
    frames = []
    for i in range(210):
        slide = create_base_slide()
        slide = add_title(slide, "Key Elements Covered", y_position=200,
                          font_size=70, color=(100, 150, 255))
        
        bullets = [
            "✓ Location Sketch",
            "✓ Layout View",
            "✓ Sheet ID Box",
            "✓ Engineering Scale"
        ]
        slide = add_bullet_points(slide, bullets, start_y=400, font_size=50)
        
        # Thank you message
        draw = ImageDraw.Draw(slide)
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        draw.text((700, 850), "Thank You!", fill=(255, 200, 50), font=font)
        
        frames.append(slide)
    return frames

# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate_all_frames():
    """Generate all frames and save as numbered PNGs"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("Downloading images...")
    download_images()
    
    print("Generating frames...")
    all_frames = []
    
    print("- Slide 1: Title")
    all_frames.extend(generate_slide_1_title())
    
    print("- Slide 2: Location Sketch")
    all_frames.extend(generate_slide_2_location())
    
    print("- Slide 3: Layout View")
    all_frames.extend(generate_slide_3_layout())
    
    print("- Slide 4: Sheet ID")
    all_frames.extend(generate_slide_4_sheet_id())
    
    print("- Slide 5: Scale")
    all_frames.extend(generate_slide_5_scale())
    
    print("- Slide 6: Summary")
    all_frames.extend(generate_slide_6_summary())
    
    print(f"Saving {len(all_frames)} frames...")
    for i, frame in enumerate(all_frames):
        frame.save(OUTPUT_DIR / f"frame_{i:05d}.png")
    
    print(f"✓ All frames saved to {OUTPUT_DIR}/")
    return len(all_frames)

if __name__ == "__main__":
    total_frames = generate_all_frames()
    print(f"\nNext step: Assemble frames into video using FFmpeg")
    print(f"Total frames: {total_frames}")
    print(f"Duration: {total_frames / 30:.1f} seconds at 30 fps")
```

#### Step 3: Generate Frames

```bash
python generate_slides.py
```

Expected output: `frames/frame_00000.png` through `frame_01949.png` (1950 frames)

#### Step 4: Assemble Video with FFmpeg

```bash
# Basic assembly (no audio)
ffmpeg -framerate 30 -i frames/frame_%05d.png -c:v libx264 -pix_fmt yuv420p -preset medium -crf 23 page5_7_explainer.mp4

# With fade transitions between scenes (advanced)
ffmpeg -framerate 30 -i frames/frame_%05d.png -vf "fade=in:0:30,fade=out:1920:30" -c:v libx264 -pix_fmt yuv420p page5_7_explainer.mp4
```

**Output**: `page5_7_explainer.mp4` (65 seconds, ~10-15 MB)

#### Step 5: Add Narration (Optional)

```bash
# Combine video with audio
ffmpeg -i page5_7_explainer.mp4 -i narration.mp3 -c:v copy -c:a aac -strict experimental output_with_audio.mp4
```

---

### Customization Tips

**Change colors**:
```python
BACKGROUND_COLOR = (15, 15, 25)  # Darker background
add_title(slide, "Text", color=(255, 100, 100))  # Red title
```

**Adjust timing**:
```python
# More frames = longer duration
for i in range(600):  # 20 seconds at 30 fps
```

**Add transitions**:
Use FFmpeg's `-vf` filters for fades, wipes, or dissolves.

---

## Approach 2: Reveal.js Web Presentation + Screen Capture

### Overview
Create an interactive HTML presentation using Reveal.js, then record/export as video.

### Pros
- ✅ **Web-based** - runs in any browser, no Python required
- ✅ **Interactive** - can navigate slides manually
- ✅ **Beautiful transitions** - built-in slide animations
- ✅ **Easy editing** - just edit HTML/CSS/JavaScript
- ✅ **Responsive** - works on any screen size
- ✅ **Export options** - PDF or video via screen recording

### Cons
- ❌ **Not standalone MP4** - requires screen recording or export tool
- ❌ **Manual recording** - must capture screen to get video
- ❌ **Timing control** - less precise than frame-based approaches
- ❌ **Web dependencies** - requires browser and possibly server
- ❌ **File size** - HTML bundle can be large with embedded images

---

### Implementation

#### Step 1: Install Reveal.js

```bash
# Option 1: Download from GitHub
wget https://github.com/hakimel/reveal.js/archive/master.zip
unzip master.zip
cd reveal.js-master

# Option 2: Use CDN (no installation needed)
# Skip to Step 2
```

#### Step 2: Create Presentation

Create `pages5_7_presentation.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Highway Plan Reading: Pages 5-7</title>
    
    <!-- Reveal.js CSS from CDN -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/night.css">
    
    <style>
        .reveal h1 { color: #5DADE2; }
        .reveal h2 { color: #F4D03F; }
        .reveal ul { text-align: left; }
        .reveal img { max-height: 500px; border: 2px solid white; }
        .checklist li { list-style: none; font-size: 1.5em; }
        .checklist li:before { content: "✓ "; color: #2ECC71; }
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            
            <!-- SLIDE 1: Title -->
            <section>
                <h1>Highway Plan Reading</h1>
                <h3>Understanding Cover Sheet Elements</h3>
                <p>Pages 5-7</p>
            </section>
            
            <!-- SLIDE 2: Project Location Sketch -->
            <section>
                <h2>Project Location Sketch</h2>
                <img src="https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/884ac0596cdd7c2b789731a8a7bdb94f9a4a495c38fd39e66c7798451e388708.jpg" 
                     alt="Location Sketch">
                <ul>
                    <li class="fragment">Shows general geographical area</li>
                    <li class="fragment">Indicates project limits</li>
                    <li class="fragment">Located in upper left corner</li>
                </ul>
            </section>
            
            <!-- SLIDE 3: Layout View -->
            <section>
                <h2>Layout View</h2>
                <img src="https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/64f16d468bc94be67e798fa7fe9b0f7c8b0b3708ea2a20af8049fb936bd2d196.jpg" 
                     alt="Layout View">
                <p><em>Plan view from above (like flying over the project)</em></p>
                <ul>
                    <li class="fragment">Beginning station</li>
                    <li class="fragment">Ending station</li>
                </ul>
            </section>
            
            <!-- SLIDE 4: Sheet Identification -->
            <section>
                <h2>Sheet Identification Box</h2>
                <table style="font-size: 0.8em; margin: 20px auto;">
                    <thead>
                        <tr>
                            <th>STATE</th>
                            <th>PROJECT NUMBER</th>
                            <th>SHEET NO.</th>
                            <th>TOTAL SHEETS</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>GA.</td>
                            <td>STP-IM-022-1(26)</td>
                            <td>1</td>
                            <td>770</td>
                        </tr>
                    </tbody>
                </table>
                <p style="margin-top: 40px;"><em>Located in upper right corner of every sheet</em></p>
            </section>
            
            <!-- SLIDE 5: Engineering Scale -->
            <section>
                <h2>Engineering Scale</h2>
                <div style="display: flex; justify-content: space-around;">
                    <img src="https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/25aa20b11bc17322942fbc4764af7c95258df8b9344efb9fe6dabc401aa15195.jpg" 
                         alt="Scale" style="max-height: 200px; margin: 10px;">
                    <img src="https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/a76db50d8c607aa0d9ea60c66f0dc3f1c971e837b6d2559b99083f4b3a0fc7c9.jpg" 
                         alt="Scale Detail" style="max-height: 200px; margin: 10px;">
                </div>
                <ul style="font-size: 0.9em;">
                    <li>Divisions: 10, 20, 30, 40, 50, 60 per inch</li>
                    <li>Common scales: 1" = 10 feet, 1" = 20 feet</li>
                    <li>Multiples: 1" = 100 feet, 1" = 1000 feet</li>
                </ul>
            </section>
            
            <!-- SLIDE 6: Summary -->
            <section>
                <h2>Key Elements Covered</h2>
                <ul class="checklist">
                    <li class="fragment">Location Sketch</li>
                    <li class="fragment">Layout View</li>
                    <li class="fragment">Sheet ID Box</li>
                    <li class="fragment">Engineering Scale</li>
                </ul>
                <h3 style="margin-top: 60px; color: #F4D03F;">Thank You!</h3>
            </section>
            
        </div>
    </div>
    
    <!-- Reveal.js JavaScript from CDN -->
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            transition: 'slide',
            transitionSpeed: 'default',
            autoPlayMedia: true,
            controls: true,
            progress: true,
            center: true,
            // Auto-advance slides (optional)
            autoSlide: 12000,  // 12 seconds per slide
            loop: false
        });
    </script>
</body>
</html>
```

#### Step 3: View Presentation

```bash
# Option 1: Open directly in browser
open pages5_7_presentation.html  # macOS
start pages5_7_presentation.html  # Windows
xdg-open pages5_7_presentation.html  # Linux

# Option 2: Serve with Python
python -m http.server 8000
# Then open http://localhost:8000/pages5_7_presentation.html
```

Navigate slides: Arrow keys or Space

#### Step 4: Export to Video

**Method A: Screen Recording (Recommended)**

1. **Windows**: Use Xbox Game Bar (Win+G) or OBS Studio
2. **macOS**: QuickTime Player → File → New Screen Recording
3. **Linux**: SimpleScreenRecorder or OBS Studio

Steps:
1. Open presentation in fullscreen (F11)
2. Start screen recording
3. Advance through slides manually or let auto-advance run
4. Stop recording
5. Save as MP4

**Method B: Automated with Puppeteer (Advanced)**

Install Node.js, then:

```bash
npm install -g decktape
decktape reveal pages5_7_presentation.html slides.pdf

# Convert PDF to video (requires additional tools)
```

#### Step 5: Add Narration

Use video editing software (iMovie, DaVinci Resolve, FFmpeg) to add voiceover.

---

### Customization Tips

**Change theme**:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/league.css">
<!-- Themes: black, white, league, sky, beige, simple, serif, blood, night, moon, solarized -->
```

**Adjust auto-advance**:
```javascript
autoSlide: 8000,  // 8 seconds per slide
```

**Add animations**:
```html
<p class="fragment fade-in">Fade in text</p>
<p class="fragment grow">Grow text</p>
<p class="fragment shrink">Shrink text</p>
```

**Disable auto-advance** (manual control):
```javascript
autoSlide: 0,  // No auto-advance
```

---

## Comparison Matrix

| Feature | Manim (Original) | Static Slides + FFmpeg | Reveal.js + Screen Record |
|---------|------------------|------------------------|---------------------------|
| **Smooth Animations** | ✅ Excellent | ❌ None | ⚠️ Basic transitions |
| **Setup Complexity** | ⚠️ High | ✅ Low | ✅ Very low |
| **Rendering Speed** | ⚠️ Slow (2-5 min) | ✅ Fast (<1 min) | ✅ Real-time |
| **Ease of Editing** | ⚠️ Requires code | ✅ Python code | ✅ HTML/CSS |
| **Output Quality** | ✅ Excellent | ✅ Good | ⚠️ Depends on recording |
| **File Size** | ✅ 15-25 MB | ✅ 10-15 MB | ⚠️ 20-40 MB |
| **Professional Look** | ✅ Highly professional | ⚠️ Basic | ✅ Professional |
| **Voiceover Integration** | ✅ Built-in support | ⚠️ Manual | ⚠️ Manual |
| **Cross-platform** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Learning Curve** | ⚠️ Steep | ✅ Easy | ✅ Very easy |

---

## Recommendation

- **Best for production**: Use **Manim** (original approach) for professional quality
- **Best for quick prototype**: Use **Reveal.js** for fastest setup
- **Best for no dependencies**: Use **Static Slides + FFmpeg** for minimal requirements
- **Best for non-programmers**: Use **Reveal.js** with screen recording

---

## Hybrid Approach

Combine methods for best results:

1. Use **Reveal.js** for rapid prototyping and layout testing
2. Once satisfied, recreate in **Manim** for final professional render
3. Use **Static Slides** as backup if Manim rendering fails

---

**Last Updated**: 2024-12-24











