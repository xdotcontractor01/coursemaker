# Installation and Usage Guide

## Prerequisites

Before running the Manim script, ensure you have:

- **Python 3.8+** (Python 3.10 recommended)
- **pip** (Python package manager)
- **FFmpeg** (video encoding)
- **Internet connection** (for downloading images)

---

## Step 1: Check Python Installation

```bash
python --version
# or
python3 --version
```

Expected output: `Python 3.8.x` or higher

---

## Step 2: Install FFmpeg

### Windows
Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use Chocolatey:
```bash
choco install ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Verify Installation
```bash
ffmpeg -version
```

---

## Step 3: Install Python Dependencies

### Install Manim Community Edition and Required Packages

```bash
pip install manim requests Pillow
```

**Package Breakdown:**
- `manim` - Manim Community Edition (v0.18.0+)
- `requests` - HTTP library for downloading images
- `Pillow` - Image processing library

### Verify Manim Installation

```bash
manim --version
```

Expected output: `Manim Community v0.18.0` or higher

---

## Step 4: Run the Script

Navigate to the directory containing `page5_7_explainer.py`:

```bash
cd /path/to/your/project
```

### Option A: High Quality Render (Recommended)

```bash
manim -pqh page5_7_explainer.py ExplainerScene
```

**Flags Explained:**
- `-p` = Preview after rendering (opens video automatically)
- `-q` = Quality setting
- `h` = High quality (1080p60)

**Expected Output:**
- Resolution: 1920x1080 @ 60fps
- File size: ~15-25 MB
- Render time: 2-5 minutes (depending on hardware)
- Output location: `./media/videos/page5_7_explainer/1080p60/ExplainerScene.mp4`

### Option B: Preview Quality (Faster)

For testing and iteration:

```bash
manim -pql page5_7_explainer.py ExplainerScene
```

**Flags Explained:**
- `l` = Low quality (480p15)
- Render time: ~30-60 seconds
- Output location: `./media/videos/page5_7_explainer/480p15/ExplainerScene.mp4`

### Option C: Production Quality (4K)

For maximum quality:

```bash
manim -pqk page5_7_explainer.py ExplainerScene
```

**Flags Explained:**
- `k` = 4K quality (2160p60)
- File size: ~50-80 MB
- Render time: 5-15 minutes

### Option D: No Preview (Background Render)

```bash
manim -qh page5_7_explainer.py ExplainerScene
```

(Omit the `-p` flag to skip auto-preview)

---

## Step 5: Locate Your Rendered Video

After successful rendering, find your video at:

```
./media/videos/page5_7_explainer/1080p60/ExplainerScene.mp4
```

Or simply copy it to the current directory:

```bash
# Windows PowerShell
copy media\videos\page5_7_explainer\1080p60\ExplainerScene.mp4 page5_7_explainer.mp4

# macOS/Linux
cp media/videos/page5_7_explainer/1080p60/ExplainerScene.mp4 page5_7_explainer.mp4
```

---

## Advanced Options

### Render Specific Scene Range

If you modify the script to have multiple scenes:

```bash
manim -pqh page5_7_explainer.py Scene1 Scene2
```

### Custom Output Filename

Rename after rendering:

```bash
manim -qh page5_7_explainer.py ExplainerScene
mv media/videos/page5_7_explainer/1080p60/ExplainerScene.mp4 ./highway_plans_pages5-7.mp4
```

### Save Partial Renders (for debugging)

```bash
manim -pql --save_sections page5_7_explainer.py ExplainerScene
```

### Transparent Background

```bash
manim -pqh --transparent page5_7_explainer.py ExplainerScene
```

---

## Quick Reference: All Quality Flags

| Flag | Resolution | FPS | Use Case | Render Time |
|------|------------|-----|----------|-------------|
| `-ql` | 480p | 15 | Testing/Preview | ~30-60s |
| `-qm` | 720p | 30 | Medium quality | ~1-2 min |
| `-qh` | 1080p | 60 | High quality (recommended) | ~2-5 min |
| `-qp` | 1440p | 60 | Production | ~5-10 min |
| `-qk` | 2160p | 60 | 4K/Cinema | ~10-15 min |

---

## Image Download Behavior

The script automatically downloads 4 images from the markdown file:

1. **First Run**: Downloads all images to `./assets/images/`
2. **Subsequent Runs**: Uses cached images (skips download)

To force re-download, delete the assets folder:

```bash
# Windows
rmdir /s assets

# macOS/Linux
rm -rf assets
```

---

## Environment Variables (Optional)

### Custom Output Directory

```bash
export MEDIA_DIR="./my_custom_output"
manim -pqh page5_7_explainer.py ExplainerScene
```

### Disable Preview Auto-Open

```bash
export MANIM_NO_PREVIEW=1
manim -qh page5_7_explainer.py ExplainerScene
```

---

## Full Command Examples

### Example 1: First Time Setup and Render

```bash
# Install dependencies
pip install manim requests Pillow

# Verify installation
manim --version

# Run high-quality render with preview
manim -pqh page5_7_explainer.py ExplainerScene
```

### Example 2: Quick Iteration Workflow

```bash
# Edit script, then preview quickly
manim -pql page5_7_explainer.py ExplainerScene

# Once satisfied, render final version
manim -qh page5_7_explainer.py ExplainerScene
```

### Example 3: Batch Processing

```bash
# Render multiple quality versions
manim -ql page5_7_explainer.py ExplainerScene  # Low
manim -qm page5_7_explainer.py ExplainerScene  # Medium
manim -qh page5_7_explainer.py ExplainerScene  # High
```

---

## Performance Tips

1. **Use low quality (`-ql`) for testing** - renders 10x faster
2. **Close other applications** during high-quality renders
3. **Use SSD storage** for faster I/O operations
4. **Increase Python heap size** for complex scenes:
   ```bash
   python -Xms4g -Xmx8g -m manim ...
   ```

---

## Next Steps

After rendering:
1. Review the video in `./media/videos/page5_7_explainer/1080p60/`
2. Optionally add voiceover using the `narration_script.txt`
3. Edit timing by modifying `wait()` calls in the Python script
4. Customize colors, fonts, and animations as needed

---

## Need Help?

- **Manim Documentation**: https://docs.manim.community/
- **Manim Discord**: https://discord.gg/manim
- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **Troubleshooting Guide**: See `TROUBLESHOOTING.md`

---

## License

This script is provided as-is for educational purposes.
Manim Community Edition is licensed under MIT License.











