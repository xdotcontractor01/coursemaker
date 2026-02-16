#!/usr/bin/env python3
"""
Feasibility Check for Chapters 8-15 Video Production
Verifies all required assets and tools are available before production.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Get project root
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

def check_feasibility():
    """Run all feasibility checks and report results."""
    print("=" * 60)
    print("FEASIBILITY CHECK - Chapters 8-15 Video Production")
    print("=" * 60)
    
    all_passed = True
    issues = []
    
    # 1. Check markdown file
    markdown_path = PROJECT_ROOT / "test_workflow/MinerU_markdown_BasicHiwyPlanReading (1)_20251224155959_2003737404334637056.md"
    print(f"\n[1] Checking markdown file...")
    if markdown_path.exists():
        size_kb = markdown_path.stat().st_size / 1024
        print(f"    OK: Markdown exists ({size_kb:.1f} KB)")
    else:
        print(f"    FAIL: Markdown not found at {markdown_path}")
        issues.append(f"Missing: {markdown_path}")
        all_passed = False
    
    # 2. Check PDF file
    pdf_path = PROJECT_ROOT / "test_workflow/BasicHiwyPlanReading (1).pdf"
    print(f"\n[2] Checking PDF file...")
    if pdf_path.exists():
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"    OK: PDF exists ({size_mb:.1f} MB)")
    else:
        print(f"    FAIL: PDF not found at {pdf_path}")
        issues.append(f"Missing: {pdf_path}")
        all_passed = False
    
    # 3. Check logo file (SVG)
    logo_path = PROJECT_ROOT / "test_workflow/GDOT LOGO For Video watermark - 200x110.svg"
    print(f"\n[3] Checking logo file...")
    if logo_path.exists():
        print(f"    OK: Logo SVG exists")
    else:
        print(f"    FAIL: Logo not found at {logo_path}")
        issues.append(f"Missing: {logo_path}")
        all_passed = False
    
    # 4. Check OpenAI API key in config.json
    config_path = PROJECT_ROOT / "config.json"
    print(f"\n[4] Checking OpenAI API key...")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            api_key = config.get('OPENAI_API_KEY', '') or config.get('openai_api_key', '')
            if api_key and api_key != 'PASTE_YOUR_API_KEY_HERE' and len(api_key) > 20:
                print(f"    OK: API key found (sk-...{api_key[-4:]})")
            else:
                print(f"    FAIL: API key not configured in config.json")
                issues.append("OpenAI API key not configured")
                all_passed = False
        except Exception as e:
            print(f"    FAIL: Could not read config.json: {e}")
            issues.append(f"config.json error: {e}")
            all_passed = False
    else:
        print(f"    FAIL: config.json not found")
        issues.append("Missing: config.json")
        all_passed = False
    
    # 5. Check ffmpeg availability
    print(f"\n[5] Checking ffmpeg...")
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        print(f"    OK: ffmpeg found at {ffmpeg_path}")
    else:
        print(f"    WARN: ffmpeg not in PATH (needed for audio normalization)")
        issues.append("ffmpeg not in PATH")
        # Not a hard fail - can still proceed
    
    # 6. Check manim availability
    print(f"\n[6] Checking manim...")
    manim_path = shutil.which('manim')
    if manim_path:
        print(f"    OK: manim found at {manim_path}")
    else:
        # Try importing manim module
        try:
            import manim
            print(f"    OK: manim module available (v{manim.__version__})")
        except ImportError:
            print(f"    FAIL: manim not found")
            issues.append("manim not installed")
            all_passed = False
    
    # 7. Check chapter file structure guide
    structure_guide = PROJECT_ROOT / "docs/CHAPTER_FILE_STRUCTURE.md"
    print(f"\n[7] Checking structure guide...")
    if structure_guide.exists():
        print(f"    OK: CHAPTER_FILE_STRUCTURE.md exists")
    else:
        print(f"    WARN: Structure guide not found (not critical)")
    
    # 8. Check required directories exist or can be created
    print(f"\n[8] Checking/creating directories...")
    dirs_to_check = [
        PROJECT_ROOT / "manifests",
        PROJECT_ROOT / "audio",
        PROJECT_ROOT / "assets/images",
        PROJECT_ROOT / "outputs",
        PROJECT_ROOT / "logs",
        PROJECT_ROOT / "manim_scripts",
    ]
    for dir_path in dirs_to_check:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"    Created: {dir_path.relative_to(PROJECT_ROOT)}")
        else:
            print(f"    OK: {dir_path.relative_to(PROJECT_ROOT)}")
    
    # 9. Check existing manifests for chapters 1-7 (reference)
    print(f"\n[9] Checking existing chapter manifests...")
    existing_manifests = list((PROJECT_ROOT / "manifests").glob("chapter*.json"))
    print(f"    Found {len(existing_manifests)} existing manifest files")
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("FEASIBILITY - YES: All checks passed")
        print("Ready to proceed with Chapters 8-15 video production.")
    else:
        print("FEASIBILITY - NO: Some checks failed")
        print("\nIssues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease resolve these issues before proceeding.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = check_feasibility()
    sys.exit(0 if success else 1)
