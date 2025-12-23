"""Fix all image paths in video scripts"""
from pathlib import Path
import re

base_path = Path(r"C:\Users\home\coursemaker\test_workflow")
figures_path = base_path / "figures" / "chapter_01"

# Fix all scripts
for video_num in range(1, 6):
    script_path = base_path / f"output/gdot_plan_videos/chapter_01/chapter_01_video_0{video_num}/base_script.py"
    
    if not script_path.exists():
        print(f"Video {video_num}: Script not found")
        continue
    
    content = script_path.read_text()
    original_content = content
    
    # Pattern to match ImageMobject with relative paths
    pattern = r'ImageMobject\(["\']?([^"\']*figures[^"\']*fig_[^"\']*\.png)["\']?\)'
    
    def replace_path(match):
        path_str = match.group(1)
        # Extract filename
        filename = Path(path_str.replace('\\', '/')).name
        abs_path = figures_path / filename
        
        if abs_path.exists():
            return f'ImageMobject(r"{abs_path}")'
        else:
            print(f"  Warning: {abs_path} not found")
            return match.group(0)
    
    content = re.sub(pattern, replace_path, content)
    
    if content != original_content:
        script_path.write_text(content)
        fixes = len(re.findall(r'ImageMobject\(r"C:', content))
        print(f"Video {video_num}: Fixed {fixes} paths")
    else:
        print(f"Video {video_num}: Already fixed or no images")

print("\nDone!")

