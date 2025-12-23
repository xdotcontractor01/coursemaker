"""Fix image paths in all video scripts to use absolute paths"""
import re
from pathlib import Path

base_dir = Path(__file__).parent.resolve()
figures_base = base_dir / 'figures' / 'chapter_01'

print(f"Base dir: {base_dir}")
print(f"Figures dir: {figures_base}")
print()

# Fix paths in all video scripts
for i in range(1, 6):
    script_path = base_dir / f'output/gdot_plan_videos/chapter_01/chapter_01_video_0{i}/base_script.py'
    if script_path.exists():
        content = script_path.read_text()
        
        # Find and replace ImageMobject paths
        # Pattern matches: ImageMobject("figures/chapter_01/fig_1-1.png") or similar
        pattern = r'ImageMobject\(["\']([^"\']+)["\']'
        
        def fix_path(match):
            original_path = match.group(1)
            # Extract just the filename
            filename = Path(original_path).name
            
            # Build absolute path
            abs_path = figures_base / filename
            
            if abs_path.exists():
                # Use forward slashes for cross-platform compatibility
                abs_path_str = str(abs_path).replace('\\', '/')
                return f'ImageMobject(r"{abs_path_str}"'
            else:
                print(f"  Warning: Image not found: {abs_path}")
                return match.group(0)
        
        new_content = re.sub(pattern, fix_path, content)
        
        if new_content != content:
            script_path.write_text(new_content)
            
            # Count how many paths were fixed
            fixes = len(re.findall(r'ImageMobject\(r"', new_content))
            print(f"Video {i}: Fixed {fixes} image paths")
        else:
            print(f"Video {i}: No changes needed")
    else:
        print(f"Video {i}: Script not found")

print("\nDone!")

