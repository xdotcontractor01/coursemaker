#!/usr/bin/env python3
"""
Feasibility check for Chapters 5, 6, and 7 video generation.
"""

import os
import json
from pathlib import Path

# Get the project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

def check_feasibility():
    """Perform feasibility check for Chapters 5, 6, and 7."""
    
    results = {}
    
    # Check source files
    markdown_path = PROJECT_ROOT / "test_workflow/MinerU_markdown_BasicHiwyPlanReading (1)_20251224155959_2003737404334637056.md"
    pdf_path = PROJECT_ROOT / "test_workflow/BasicHiwyPlanReading (1).pdf"
    logo_path = PROJECT_ROOT / "test_workflow/GDOT LOGO For Video watermark - 200x110.svg"
    
    # Check markdown
    if markdown_path.exists():
        print(f"[OK] Markdown file found: {markdown_path}")
    else:
        print(f"[ERROR] Markdown file missing: {markdown_path}")
        results['markdown'] = False
    
    # Check PDF
    if pdf_path.exists():
        print(f"[OK] PDF file found: {pdf_path}")
    else:
        print(f"[WARNING] PDF file missing: {pdf_path} (will use markdown only)")
    
    # Check logo
    if logo_path.exists():
        print(f"[OK] Logo file found: {logo_path}")
        results['logo'] = True
    else:
        print(f"[ERROR] Logo file missing: {logo_path}")
        results['logo'] = False
    
    # Check API key
    config_path = PROJECT_ROOT / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            api_key = config.get('openai_api_key', '')
            if api_key and api_key != 'PASTE_YOUR_API_KEY_HERE':
                print(f"[OK] OpenAI API key found in config.json")
                results['api_key'] = True
            else:
                print(f"[ERROR] OpenAI API key missing or invalid in config.json")
                results['api_key'] = False
    else:
        print(f"[ERROR] config.json file missing")
        results['api_key'] = False
    
    # Check Manim
    try:
        import manim
        print(f"[OK] Manim installed: version {manim.__version__}")
        results['manim'] = True
    except ImportError:
        print(f"[ERROR] Manim not installed")
        results['manim'] = False
    
    # Check FFmpeg
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] FFmpeg available")
            results['ffmpeg'] = True
        else:
            print(f"[ERROR] FFmpeg not available")
            results['ffmpeg'] = False
    except FileNotFoundError:
        print(f"[ERROR] FFmpeg not found in PATH")
        results['ffmpeg'] = False
    
    # Final feasibility assessment
    all_ok = all(results.values())
    
    print("\n" + "="*60)
    print("FEASIBILITY CHECK RESULTS")
    print("="*60)
    
    for chapter in [5, 6, 7]:
        if all_ok:
            print(f"Chapter {chapter}: FEASIBILITY — YES: all inputs ok")
        else:
            missing = [k for k, v in results.items() if not v]
            print(f"Chapter {chapter}: FEASIBILITY — NO: missing {', '.join(missing)}")
    
    return all_ok, results

if __name__ == "__main__":
    check_feasibility()




