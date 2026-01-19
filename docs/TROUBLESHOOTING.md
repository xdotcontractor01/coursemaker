# Troubleshooting Guide

## Common Issues and Solutions

---

## 1. FFmpeg Not Found

### Error Message
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
OSError: [Errno 2] No such file or directory: 'ffmpeg'
```

### Cause
FFmpeg is not installed or not in system PATH.

### Solutions

#### Windows
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Open "Environment Variables" in System Properties
   - Edit "Path" under System Variables
   - Add `C:\ffmpeg\bin`
4. Restart terminal/IDE
5. Verify:
   ```bash
   ffmpeg -version
   ```

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

---

## 2. Manim Version Conflicts

### Error Message
```
AttributeError: module 'manim' has no attribute 'Scene'
ImportError: cannot import name 'Scene' from 'manim'
```

### Cause
- Wrong Manim package installed (ManimGL vs ManimCE)
- Outdated Manim version
- Multiple Manim installations conflicting

### Solutions

#### Uninstall All Manim Versions
```bash
pip uninstall manim manimgl manimlib manim-ce
```

#### Install Correct Version
```bash
pip install manim==0.18.0
```

#### Verify Installation
```bash
manim --version
python -c "import manim; print(manim.__version__)"
```

Expected output: `Manim Community v0.18.0`

---

## 3. Image Download Failures

### Error Message
```
requests.exceptions.ConnectionError
requests.exceptions.Timeout
OSError: cannot identify image file
```

### Cause
- No internet connection
- Firewall blocking downloads
- CDN server temporarily down
- Corrupted image files

### Solutions

#### Check Internet Connection
```bash
ping cdn-mineru.openxlab.org.cn
```

#### Manually Download Images
If automatic download fails, download manually:

1. Open these URLs in browser:
   - https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/884ac0596cdd7c2b789731a8a7bdb94f9a4a495c38fd39e66c7798451e388708.jpg
   - https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/64f16d468bc94be67e798fa7fe9b0f7c8b0b3708ea2a20af8049fb936bd2d196.jpg
   - https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/25aa20b11bc17322942fbc4764af7c95258df8b9344efb9fe6dabc401aa15195.jpg
   - https://cdn-mineru.openxlab.org.cn/result/2025-12-24/d749dbdf-4f40-47d0-9280-402a52c61f01/a76db50d8c607aa0d9ea60c66f0dc3f1c971e837b6d2559b99083f4b3a0fc7c9.jpg

2. Save as:
   - `assets/images/figure_1_3.jpg`
   - `assets/images/figure_1_4.jpg`
   - `assets/images/figure_1_9.jpg`
   - `assets/images/figure_1_10.jpg`

3. Create directory first:
   ```bash
   mkdir -p assets/images
   ```

#### Increase Timeout
Edit `page5_7_explainer.py` line 60:
```python
response = requests.get(url, timeout=60)  # Increase from 30 to 60
```

#### Use Proxy (if behind corporate firewall)
```python
proxies = {'http': 'http://proxy.company.com:8080', 'https': 'http://proxy.company.com:8080'}
response = requests.get(url, timeout=30, proxies=proxies)
```

---

## 4. Font Rendering Issues

### Error Message
```
Warning: Font 'Arial' not found
RuntimeWarning: Glyph X missing from current font
```

### Cause
Missing system fonts or font cache issues.

### Solutions

#### Windows
Install fonts from `C:\Windows\Fonts` or download:
- Arial (default Windows font)
- Times New Roman
- Courier New

#### macOS
Install via Font Book:
```bash
# Or use Homebrew
brew install --cask font-arial
```

#### Linux
```bash
sudo apt install fonts-liberation fonts-dejavu
fc-cache -fv
```

#### Use Fallback Fonts in Script
Edit `page5_7_explainer.py` and replace `Text()` calls:
```python
Text("Your text", font="DejaVu Sans", font_size=32)
```

---

## 5. Markdown File Not Found

### Error Message
```
FileNotFoundError: [Errno 2] No such file or directory: 'test_workflow/MinerU_markdown_...'
```

### Cause
Script cannot locate the markdown file.

### Solutions

#### Option 1: Run from Correct Directory
```bash
cd /path/to/coursemaker
manim -pqh page5_7_explainer.py ExplainerScene
```

#### Option 2: Use Absolute Path
Edit line 18 in `page5_7_explainer.py`:
```python
MARKDOWN_FILE = r"C:\Users\home\coursemaker\test_workflow\MinerU_markdown_BasicHiwyPlanReading (1)_20251224155959_2003737404334637056.md"
```

#### Option 3: Comment Out Markdown Reading
The script includes hardcoded text, so markdown reading is optional:
```python
# extract_content_from_markdown()  # Comment this out
```

---

## 6. Memory/Performance Issues

### Error Message
```
MemoryError
Process killed (OOM)
Rendering extremely slow
```

### Cause
Insufficient RAM or CPU resources.

### Solutions

#### Reduce Quality
```bash
manim -pql page5_7_explainer.py ExplainerScene  # Use low quality
```

#### Close Other Applications
Free up RAM before rendering.

#### Reduce Image Size
Edit script to scale images more:
```python
location_img.scale(0.4)  # Reduce from 0.6 to 0.4
```

#### Increase Virtual Memory (Windows)
1. System Properties → Advanced → Performance Settings
2. Advanced tab → Virtual Memory → Change
3. Set custom size: Initial 4096 MB, Maximum 8192 MB

---

## 7. Python Version Incompatibility

### Error Message
```
SyntaxError: invalid syntax
TypeError: unsupported operand type(s)
f-string: empty expression not allowed
```

### Cause
Python version too old (< 3.8).

### Solutions

#### Check Python Version
```bash
python --version
```

#### Install Python 3.10
- **Windows**: Download from python.org
- **macOS**: `brew install python@3.10`
- **Linux**: `sudo apt install python3.10`

#### Use Correct Python
```bash
python3.10 -m pip install manim
python3.10 -m manim -pqh page5_7_explainer.py ExplainerScene
```

---

## 8. LaTeX/MathTex Errors

### Error Message
```
LaTeX Error: File `<package>.sty' not found
RuntimeError: Latex error converting to dvi
```

### Cause
This script doesn't use LaTeX, but if you modify it to include math:

### Solutions

#### Install LaTeX Distribution
- **Windows**: MiKTeX or TeX Live
- **macOS**: MacTeX (`brew install --cask mactex`)
- **Linux**: `sudo apt install texlive-full`

#### Or Avoid LaTeX
Use `Text()` instead of `Tex()` or `MathTex()`.

---

## 9. Video Output Not Generated

### Error Message
```
No output file generated
Render completed but no video found
```

### Cause
- Render failed silently
- Looking in wrong directory
- Permissions issue

### Solutions

#### Check Output Directory
```bash
ls -R media/videos/page5_7_explainer/
```

Expected path: `media/videos/page5_7_explainer/1080p60/ExplainerScene.mp4`

#### Enable Verbose Logging
```bash
manim -pqh --verbose DEBUG page5_7_explainer.py ExplainerScene
```

#### Check File Permissions
```bash
chmod -R 755 media/
```

---

## 10. Slow Rendering Speed

### Issue
Rendering takes 10+ minutes for a 60-second video.

### Solutions

#### Use GPU Acceleration (if available)
Manim doesn't directly use GPU, but FFmpeg does:
```bash
# Check if GPU encoding available
ffmpeg -encoders | grep nvenc
```

#### Optimize Script
- Reduce `run_time` values
- Use fewer animations per scene
- Scale images before loading
- Comment out unnecessary `wait()` calls during testing

#### Render at Lower Quality First
```bash
manim -pql page5_7_explainer.py ExplainerScene  # Preview
# Then when satisfied:
manim -qh page5_7_explainer.py ExplainerScene   # Final
```

---

## 11. Module Import Errors

### Error Message
```
ModuleNotFoundError: No module named 'manim'
ModuleNotFoundError: No module named 'requests'
```

### Cause
Packages not installed or wrong Python environment.

### Solutions

#### Install Missing Packages
```bash
pip install manim requests Pillow
```

#### Check If Using Virtual Environment
```bash
# Activate venv if exists
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Then install
pip install manim requests Pillow
```

#### Verify Installation Location
```bash
pip show manim
python -c "import manim; print(manim.__file__)"
```

---

## 12. Windows-Specific Path Issues

### Error Message
```
FileNotFoundError: [WinError 3] The system cannot find the path specified
```

### Cause
Windows path separators or spaces in filenames.

### Solutions

#### Use Raw Strings
```python
MARKDOWN_FILE = r"C:\Users\home\coursemaker\test_workflow\file.md"
```

#### Use Forward Slashes
```python
MARKDOWN_FILE = "C:/Users/home/coursemaker/test_workflow/file.md"
```

#### Use Path Object
```python
from pathlib import Path
MARKDOWN_FILE = Path("test_workflow") / "MinerU_markdown_BasicHiwyPlanReading (1)_20251224155959_2003737404334637056.md"
```

---

## Debug Checklist

Before reporting issues, verify:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] FFmpeg installed (`ffmpeg -version`)
- [ ] Manim installed (`manim --version`)
- [ ] Internet connection working
- [ ] Running from correct directory
- [ ] All dependencies installed (`pip list | grep manim`)
- [ ] Enough disk space (500 MB+ free)
- [ ] Enough RAM (4 GB+ recommended)
- [ ] Antivirus not blocking Python/FFmpeg
- [ ] File paths are correct and accessible

---

## Getting More Help

### Manim Community Resources
- **Documentation**: https://docs.manim.community/
- **Discord**: https://discord.gg/manim
- **Reddit**: r/manim
- **GitHub Issues**: https://github.com/ManimCommunity/manim/issues

### Provide This Information When Asking for Help
```bash
# System info
python --version
manim --version
ffmpeg -version

# Full error traceback
manim -pqh --verbose DEBUG page5_7_explainer.py ExplainerScene 2>&1 | tee error.log
```

---

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| FFmpeg not found | `brew install ffmpeg` (macOS) or download installer |
| Wrong Manim version | `pip install manim==0.18.0` |
| Image download fails | Download manually to `assets/images/` |
| Font missing | Use `font="DejaVu Sans"` in Text() |
| Slow rendering | Use `-ql` flag for testing |
| File not found | Use absolute path or check working directory |
| Out of memory | Render at lower quality (`-ql`) |
| Python too old | Install Python 3.10+ |

---

**Last Updated**: 2024-12-24











