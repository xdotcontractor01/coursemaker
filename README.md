# Highway Plan Reading: Pages 5-7 Explainer Video

## 📚 Project Overview

This project creates a professional 60-65 second educational video explaining pages 5, 6, and 7 of the **Basic Highway Plan Reading** manual published by the Georgia Department of Transportation.

**Topics Covered:**
- Project Location Sketch
- Layout View  
- Sheet Identification Box
- Engineering Scale

---

## 📦 Deliverables

### Core Files

| File | Description | Size |
|------|-------------|------|
| `page5_7_explainer.py` | Main Manim script with 6 animated scenes | ~12 KB |
| `narration_script.txt` | Timestamped voiceover script (~137 words) | ~3 KB |
| `INSTALLATION_AND_USAGE.md` | Complete installation guide and render commands | ~8 KB |
| `TROUBLESHOOTING.md` | Common issues and solutions (12 scenarios) | ~15 KB |
| `ALTERNATIVE_APPROACHES.md` | Two alternative video creation methods | ~18 KB |

### Generated Assets (after first run)

| File/Directory | Description |
|----------------|-------------|
| `assets/images/` | 4 downloaded JPG images from markdown |
| `media/videos/page5_7_explainer/1080p60/` | Rendered video output |
| `page5_7_explainer.mp4` | Final video (15-25 MB) |

---

## 🚀 Quick Start

### Prerequisites

✅ Python 3.8+ (3.10 recommended)  
✅ FFmpeg installed and in PATH  
✅ Internet connection (for image downloads)

### Installation (5 minutes)

```bash
# 1. Install Python dependencies
pip install manim requests Pillow

# 2. Verify installations
python --version    # Should be 3.8+
manim --version     # Should be v0.18.0+
ffmpeg -version     # Should be 4.4+

# 3. Run the script
manim -pqh page5_7_explainer.py ExplainerScene
```

**Output Location:**  
`./media/videos/page5_7_explainer/1080p60/ExplainerScene.mp4`

---

## 📖 Documentation Structure

```
.
├── README.md                          ← You are here
├── page5_7_explainer.py              ← Main Manim script
├── narration_script.txt               ← Voiceover text with timestamps
├── INSTALLATION_AND_USAGE.md          ← Detailed setup guide
├── TROUBLESHOOTING.md                 ← Error solutions
├── ALTERNATIVE_APPROACHES.md          ← Non-Manim alternatives
│
├── assets/images/                     ← Downloaded images (auto-created)
│   ├── figure_1_3.jpg
│   ├── figure_1_4.jpg
│   ├── figure_1_9.jpg
│   └── figure_1_10.jpg
│
├── media/videos/page5_7_explainer/    ← Rendered output (auto-created)
│   └── 1080p60/
│       └── ExplainerScene.mp4
│
└── test_workflow/                     ← Source data
    └── MinerU_markdown_BasicHiwyPlanReading (1)_*.md
```

---

## 🎬 Video Specifications

| Specification | Value |
|---------------|-------|
| Duration | 60-65 seconds |
| Resolution | 1920x1080 (Full HD) |
| Frame Rate | 60 fps |
| Codec | H.264 (MP4) |
| File Size | 15-25 MB |
| Audio | None (add separately using narration script) |

### Scene Breakdown

| Scene | Duration | Content |
|-------|----------|---------|
| 1. Title | 0-5s | Introduction with title and subtitle |
| 2. Location Sketch | 5-18s | Figure 1-3 with bullet points |
| 3. Layout View | 18-30s | Figure 1-4 with annotations |
| 4. Sheet ID Box | 30-43s | Table with identification data |
| 5. Scale | 43-58s | Figures 1-9 & 1-10 with explanations |
| 6. Summary | 58-65s | Recap checklist with "Thank You" |

---

## 🎨 Customization Guide

### Change Colors

Edit `page5_7_explainer.py`:

```python
# Line ~220: Title color
color=BLUE  # Change to RED, GREEN, YELLOW, etc.

# Line ~240: Heading color
color=YELLOW  # Change to ORANGE, PURPLE, etc.
```

### Adjust Timing

```python
# Line ~230: Scene duration
self.wait(2)  # Change to 3, 4, etc. for longer pauses
```

### Modify Text

```python
# Line ~215: Change title
title = Text("Your Custom Title", font_size=56, weight=BOLD)
```

### Scale Images

```python
# Line ~275: Image size
location_img.scale(0.6)  # Increase to 0.8 for larger, 0.4 for smaller
```

---

## 🎤 Adding Voiceover

### Option 1: Manual Recording

1. Read `narration_script.txt` aloud
2. Record using Audacity, GarageBand, or phone
3. Save as `narration.mp3`
4. Combine with video:

```bash
ffmpeg -i media/videos/page5_7_explainer/1080p60/ExplainerScene.mp4 \
       -i narration.mp3 \
       -c:v copy -c:a aac \
       page5_7_explainer_with_audio.mp4
```

### Option 2: Text-to-Speech (TTS)

```bash
# Install gTTS
pip install gTTS

# Generate audio
python -c "
from gtts import gTTS
text = open('narration_script.txt').read()
tts = gTTS(text, lang='en', slow=False)
tts.save('narration.mp3')
"

# Combine with video (same FFmpeg command as above)
```

---

## 🔧 Common Issues

| Issue | Quick Fix | Details |
|-------|-----------|---------|
| **FFmpeg not found** | `brew install ffmpeg` (macOS) | See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) #1 |
| **Wrong Manim version** | `pip install manim==0.18.0` | See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) #2 |
| **Image download fails** | Download manually | See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) #3 |
| **Font errors** | Use `font="DejaVu Sans"` | See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) #4 |
| **Slow rendering** | Use `-ql` flag for testing | See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) #10 |

📘 **Full troubleshooting guide:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🔄 Alternative Approaches

If Manim is not available or you prefer different tools:

### 1. Static Slides + FFmpeg
- Uses Pillow to generate PNG frames
- Assembles with FFmpeg
- ✅ No Manim dependency
- ❌ No smooth animations

### 2. Reveal.js + Screen Recording
- HTML presentation framework
- Record screen to create video
- ✅ Very easy to set up
- ⚠️ Requires screen recording software

📘 **Full alternative guides:** [ALTERNATIVE_APPROACHES.md](ALTERNATIVE_APPROACHES.md)

---

## 📊 Render Quality Options

| Command | Quality | Resolution | FPS | Render Time | File Size |
|---------|---------|------------|-----|-------------|-----------|
| `manim -pql` | Low (preview) | 480p | 15 | ~30-60s | ~5 MB |
| `manim -pqm` | Medium | 720p | 30 | ~1-2 min | ~10 MB |
| `manim -pqh` | **High** ⭐ | 1080p | 60 | ~2-5 min | ~20 MB |
| `manim -pqp` | Production | 1440p | 60 | ~5-10 min | ~35 MB |
| `manim -pqk` | 4K | 2160p | 60 | ~10-15 min | ~60 MB |

**Recommended:** Use `-pql` for testing, `-pqh` for final render.

---

## 🎯 Workflow Recommendations

### For Rapid Iteration

```bash
# Edit script
nano page5_7_explainer.py

# Quick preview (low quality)
manim -pql page5_7_explainer.py ExplainerScene

# If satisfied, render final
manim -qh page5_7_explainer.py ExplainerScene
```

### For Production

```bash
# Final high-quality render
manim -qh page5_7_explainer.py ExplainerScene

# Add voiceover
ffmpeg -i media/videos/page5_7_explainer/1080p60/ExplainerScene.mp4 \
       -i narration.mp3 -c:v copy -c:a aac \
       final_output.mp4

# Verify output
ffprobe final_output.mp4
```

---

## 📚 Additional Resources

### Manim Documentation
- **Official Docs:** https://docs.manim.community/
- **Tutorial:** https://docs.manim.community/en/stable/tutorials.html
- **Discord Community:** https://discord.gg/manim
- **Example Gallery:** https://docs.manim.community/en/stable/examples.html

### FFmpeg Resources
- **Official Site:** https://ffmpeg.org/
- **Documentation:** https://ffmpeg.org/documentation.html
- **Cheat Sheet:** https://github.com/yuanqing/ffmpeg-cheatsheet

### Python Libraries Used
- **Manim:** https://github.com/ManimCommunity/manim
- **Requests:** https://requests.readthedocs.io/
- **Pillow:** https://pillow.readthedocs.io/

---

## 🤝 Contributing & Customization

### Want to Extend This Project?

**Add More Pages:**
1. Identify new page ranges in the markdown file
2. Create new scene methods in `page5_7_explainer.py`
3. Add to `construct()` method
4. Update narration script

**Change Visual Style:**
- Edit color schemes (lines with `color=BLUE`, `color=YELLOW`)
- Modify fonts (add `font="Your Font"` to `Text()` calls)
- Adjust layouts (change positioning with `.shift()`, `.to_edge()`)

**Add New Animations:**
- Check Manim documentation for animation types
- Examples: `FadeIn`, `GrowFromCenter`, `Indicate`, `Flash`

---

## 📝 License & Attribution

### Source Material
- **Manual:** "Basic Highway Plan Reading" by Georgia DOT
- **Revised:** October 1, 2020
- **Copyright:** Georgia Department of Transportation

### This Script
- **Created:** December 24, 2024
- **License:** Educational use only
- **Tools:** Manim Community Edition (MIT License)

---

## ✅ Success Checklist

Before considering the project complete:

- [ ] Python 3.8+ installed
- [ ] FFmpeg installed and working
- [ ] Manim v0.18.0+ installed
- [ ] All 4 images downloaded successfully
- [ ] Video renders without errors
- [ ] Output is 60-65 seconds long
- [ ] Resolution is 1920x1080 @ 60fps
- [ ] All 6 scenes display correctly
- [ ] Text is readable and properly aligned
- [ ] Images appear at correct sizes
- [ ] Transitions are smooth
- [ ] (Optional) Voiceover added and synced

---

## 🆘 Need Help?

1. **Check Troubleshooting Guide:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Review Installation Guide:** [INSTALLATION_AND_USAGE.md](INSTALLATION_AND_USAGE.md)
3. **Try Alternative Approaches:** [ALTERNATIVE_APPROACHES.md](ALTERNATIVE_APPROACHES.md)
4. **Search Manim Discord:** https://discord.gg/manim
5. **Post Issue with Details:**
   - Python version (`python --version`)
   - Manim version (`manim --version`)
   - FFmpeg version (`ffmpeg -version`)
   - Full error traceback

---

## 🎉 Final Notes

This project demonstrates how to create educational technical videos programmatically using Manim. The same approach can be scaled to:

- Create series of videos for entire chapters
- Automate video generation from documentation
- Build interactive learning materials
- Generate consistent branded content

**Estimated Total Time:**
- Setup: 5-10 minutes
- First render: 2-5 minutes
- Adding voiceover: 10-15 minutes
- **Total:** ~20-30 minutes from scratch to finished video

---

**Last Updated:** December 24, 2024  
**Version:** 1.0  
**Compatibility:** Manim Community v0.18.0+, Python 3.8+, FFmpeg 4.4+
