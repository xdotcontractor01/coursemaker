#!/usr/bin/env python3
"""
Unified Lesson Validator
Validates all unified lesson JSON files against the schema.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


def validate_lesson_structure(data: Dict, filename: str) -> List[str]:
    """Validate a unified lesson JSON structure."""
    errors = []
    
    # Required top-level fields
    required_fields = [
        "chapter", "video", "title", "summary_bullets", "summary_markdown",
        "video_url", "duration_seconds", "source_pages", "content_source",
        "generated_at", "quizzes"
    ]
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Type validations
    if not isinstance(data.get("chapter"), int):
        errors.append("chapter must be an integer")
    if not isinstance(data.get("video"), int):
        errors.append("video must be an integer")
    if not isinstance(data.get("title"), str):
        errors.append("title must be a string")
    if not isinstance(data.get("summary_bullets"), list):
        errors.append("summary_bullets must be an array")
    if not isinstance(data.get("summary_markdown"), str):
        errors.append("summary_markdown must be a string")
    if not isinstance(data.get("quizzes"), list):
        errors.append("quizzes must be an array")
    
    # Content validations
    if not data.get("summary_bullets"):
        errors.append("summary_bullets cannot be empty")
    if not data.get("summary_markdown"):
        errors.append("summary_markdown cannot be empty")
    
    # Validate chapter/video match filename
    try:
        expected_chapter = int(filename.split("_")[0].replace("Chapter", ""))
        expected_video = int(filename.split("_")[1].replace("video", "").replace(".json", ""))
        
        if data.get("chapter") != expected_chapter:
            errors.append(f"chapter {data.get('chapter')} doesn't match filename (expected {expected_chapter})")
        if data.get("video") != expected_video:
            errors.append(f"video {data.get('video')} doesn't match filename (expected {expected_video})")
    except Exception as e:
        errors.append(f"Invalid filename format: {filename}")
    
    # Validate quiz questions
    for idx, quiz in enumerate(data.get("quizzes", [])):
        quiz_errors = validate_quiz_question(quiz, idx, data.get("chapter"), data.get("video"))
        errors.extend(quiz_errors)
    
    return errors


def validate_quiz_question(quiz: Dict, idx: int, chapter: int, video: int) -> List[str]:
    """Validate a quiz question structure."""
    errors = []
    prefix = f"Quiz {idx}: "
    
    # Required fields
    required_fields = [
        "question_id", "chapter", "video", "question_text", "options",
        "correct_option", "explanation", "source_excerpt", "confidence", "auto_ready"
    ]
    
    for field in required_fields:
        if field not in quiz:
            errors.append(f"{prefix}Missing required field: {field}")
    
    # Type validations
    if not isinstance(quiz.get("question_id"), str):
        errors.append(f"{prefix}question_id must be a string")
    if not isinstance(quiz.get("chapter"), int):
        errors.append(f"{prefix}chapter must be an integer")
    if not isinstance(quiz.get("video"), int):
        errors.append(f"{prefix}video must be an integer")
    if not isinstance(quiz.get("question_text"), str):
        errors.append(f"{prefix}question_text must be a string")
    if not isinstance(quiz.get("options"), list):
        errors.append(f"{prefix}options must be an array")
    if quiz.get("correct_option") is not None and not isinstance(quiz.get("correct_option"), int):
        errors.append(f"{prefix}correct_option must be an integer or null")
    if not isinstance(quiz.get("explanation"), str):
        errors.append(f"{prefix}explanation must be a string")
    if not isinstance(quiz.get("confidence"), (int, float)):
        errors.append(f"{prefix}confidence must be a number")
    if not isinstance(quiz.get("auto_ready"), bool):
        errors.append(f"{prefix}auto_ready must be a boolean")
    
    # Validate chapter/video match lesson
    if quiz.get("chapter") != chapter:
        errors.append(f"{prefix}chapter mismatch: {quiz.get('chapter')} != {chapter}")
    if quiz.get("video") != video:
        errors.append(f"{prefix}video mismatch: {quiz.get('video')} != {video}")
    
    # Validate options
    for opt_idx, option in enumerate(quiz.get("options", [])):
        if not isinstance(option, dict):
            errors.append(f"{prefix}Option {opt_idx} must be an object")
            continue
        if "text" not in option:
            errors.append(f"{prefix}Option {opt_idx} missing 'text' field")
        if "generated_distractor" not in option:
            errors.append(f"{prefix}Option {opt_idx} missing 'generated_distractor' field")
        if not isinstance(option.get("text"), str):
            errors.append(f"{prefix}Option {opt_idx} text must be a string")
        if not isinstance(option.get("generated_distractor"), bool):
            errors.append(f"{prefix}Option {opt_idx} generated_distractor must be a boolean")
    
    # Validate correct_option index
    if quiz.get("correct_option") is not None:
        correct_idx = quiz.get("correct_option")
        num_options = len(quiz.get("options", []))
        if correct_idx < 0 or correct_idx >= num_options:
            errors.append(f"{prefix}correct_option {correct_idx} out of range (0-{num_options-1})")
    
    return errors


def main():
    """Main validation entry point."""
    workspace = Path(os.getcwd())
    unified_dir = workspace / "unified_lessons"
    
    if not unified_dir.exists():
        print(f"ERROR: unified_lessons directory not found at {unified_dir}")
        return
    
    json_files = sorted([f for f in unified_dir.iterdir() if f.suffix == ".json"])
    
    print(f"Validating {len(json_files)} unified lesson files...\n")
    
    total_errors = 0
    files_with_errors = 0
    total_quizzes = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            errors = validate_lesson_structure(data, json_file.name)
            
            quiz_count = len(data.get("quizzes", []))
            total_quizzes += quiz_count
            
            if errors:
                print(f"[FAIL] {json_file.name}")
                for error in errors:
                    print(f"  - {error}")
                print()
                files_with_errors += 1
                total_errors += len(errors)
            else:
                print(f"[OK] {json_file.name} ({quiz_count} quizzes)")
        
        except json.JSONDecodeError as e:
            print(f"[FAIL] {json_file.name}")
            print(f"  - JSON parse error: {e}")
            print()
            files_with_errors += 1
            total_errors += 1
        except Exception as e:
            print(f"[FAIL] {json_file.name}")
            print(f"  - Unexpected error: {e}")
            print()
            files_with_errors += 1
            total_errors += 1
    
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Total files: {len(json_files)}")
    print(f"Files validated successfully: {len(json_files) - files_with_errors}")
    print(f"Files with errors: {files_with_errors}")
    print(f"Total errors: {total_errors}")
    print(f"Total quiz questions: {total_quizzes}")
    print("="*80)
    
    if total_errors == 0:
        print("\n[SUCCESS] All unified lesson files are valid!")
    else:
        print(f"\n[ERROR] Validation failed with {total_errors} errors")
        exit(1)


if __name__ == "__main__":
    main()
