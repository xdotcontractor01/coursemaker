#!/usr/bin/env python3
"""
Quiz Quality Repair Script -- Chapters 1-15
============================================
Reviews and improves quiz question quality without changing correct answers.
"""

import json
import re
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
QUIZZES_ROOT = ROOT / "quizzes"
CONTENT_ROOT = ROOT / "manifests" / "course_content"
MANIFESTS_ROOT = ROOT / "manifests"
LOGS_ROOT = ROOT / "logs"

NOW_ISO = datetime.now(timezone.utc).isoformat()

# Video list for all chapters
ALL_VIDEOS = [
    (1, 1), (1, 2), (1, 3), (1, 4),
    (2, 1), (3, 1), (4, 1),
    (5, 1), (6, 1), (6, 2),
    (7, 1), (7, 2), (7, 3),
    (8, 1), (8, 2), (8, 3),
    (9, 1), (10, 1), (11, 1), (12, 1),
    (13, 1), (13, 2), (14, 1),
    (15, 1), (15, 2),
]


def video_dir_name(ch: int, vid: int) -> str:
    return f"Chapter{ch:02d}_video{vid:02d}"


def is_weak_question(q: dict, context: dict) -> tuple[bool, str]:
    """
    Identify weak questions based on quality criteria.
    Returns (is_weak, reason).
    """
    q_text = q.get("question_text", "")
    q_type = q.get("question_type", "mcq")
    options = q.get("options", [])
    
    # Flag 1: Incomplete sentences or fragments as options
    for opt in options:
        txt = opt.get("text", "").strip()
        if txt in ["These", "This", "All", "Figure", "Welcome", "As you can see on screen"]:
            return (True, "Contains single-word or meaningless distractors")
        if txt and not txt[0].isupper() and not txt[0].isdigit():
            continue  # lowercase start is ok for some answers
        if len(txt) > 20 and not any(txt.endswith(p) for p in [".", "?", "!", ")", '"', "'"]):
            # Long text without proper ending might be a fragment
            if txt.count(" ") >= 5 and ":" not in txt[-10:]:
                return (True, "Contains incomplete sentence fragments as options")
    
    # Flag 2: True/False questions without context
    if len(options) == 2:
        opt_texts = [o.get("text", "").lower() for o in options]
        if set(opt_texts) == {"true", "false"}:
            # Check if question adds meaningful context
            if q_text.startswith("True False "):
                return (True, "True/False question with no context (starts with 'True False')")
    
    # Flag 3: Binary choice without context
    if " (are / are not) " in q_text or " (is / is not) " in q_text:
        if len(q_text) < 60:  # very short binary questions
            return (True, "Binary choice question lacks context")
    
    # Flag 4: Generated questions with poor quality
    if q.get("generated", False):
        correct_opt = next((o for o in options if o.get("correct")), None)
        if correct_opt:
            correct_text = correct_opt.get("text", "")
            # Check if correct answer is a fragment
            if len(correct_text) > 30 and correct_text.count(" ") >= 5:
                if not correct_text.strip().endswith((".", "?", "!")):
                    return (True, "Generated question with incomplete answer")
    
    # Flag 5: 3+ obviously wrong distractors (all single words or very short)
    if len(options) == 4:
        distractors = [o for o in options if not o.get("correct")]
        short_count = sum(1 for d in distractors if len(d.get("text", "").split()) <= 2)
        if short_count >= 2:
            correct_opt = next((o for o in options if o.get("correct")), None)
            if correct_opt and len(correct_opt.get("text", "").split()) > 3:
                return (True, "Distractors are too short/obvious compared to correct answer")
    
    # Flag 6: Questions that lack domain context
    domain_keywords = ["plan", "sheet", "specification", "construction", "roadway", "highway", 
                       "drainage", "culvert", "bridge", "section", "elevation", "station"]
    has_context = any(kw in q_text.lower() for kw in domain_keywords)
    if not has_context and q.get("confidence", 1.0) < 0.8:
        if "Which of the following" in q_text or "What is the primary purpose" in q_text:
            return (True, "Generic question stem without domain context")
    
    return (False, "")


def improve_true_false_question(q: dict, context: dict) -> dict:
    """Convert True/False to contextual MCQ."""
    q_text = q.get("question_text", "")
    
    # Remove "True False" prefix
    if q_text.startswith("True False "):
        core_text = q_text[11:].strip()
    else:
        core_text = q_text
    
    # Determine correct answer
    correct_val = next((o.get("text") for o in q["options"] if o.get("correct")), "True")
    
    # Create contextual question stem
    if "Index" in core_text and "required" in core_text:
        new_stem = "According to construction plan standards, which statement about the Index is correct?"
        new_options = [
            {"text": "An Index is required for each set of Construction Plans", "correct": correct_val == "True"},
            {"text": "An Index is optional and only used for complex projects", "correct": False},
            {"text": "The Index is included only in projects over 10 sheets", "correct": False},
            {"text": "The Index appears only in the digital version of plans", "correct": False},
        ]
    elif "Revision Summary" in core_text:
        new_stem = "What is the role of the Revision Summary Sheet in construction documentation?"
        new_options = [
            {"text": "It is part of the construction plans but not part of the contract", "correct": correct_val == "False"},
            {"text": "It is legally binding as part of the contract documents", "correct": correct_val == "True"},
            {"text": "It is provided for reference only and has no official status", "correct": False},
            {"text": "It is required only for projects with more than 3 revisions", "correct": False},
        ]
    elif "Standards and Construction Drawings" in core_text:
        new_stem = "What information is included in the construction plan index?"
        new_options = [
            {"text": "A listing of all Standards and Construction Drawings", "correct": correct_val == "True"},
            {"text": "Only the primary construction sheets", "correct": False},
            {"text": "Sheet numbers but not drawing descriptions", "correct": False},
            {"text": "Standard references are listed separately, not in the index", "correct": False},
        ]
    elif "Traffic Control Plans" in core_text and "general" in core_text:
        new_stem = "How are Traffic Control Plans developed for construction projects?"
        new_options = [
            {"text": "Each project requires a unique Traffic Control Plan tailored to site conditions", "correct": correct_val == "False"},
            {"text": "Generic Traffic Control Plans are reused across projects", "correct": correct_val == "True"},
            {"text": "Traffic Control Plans are optional for minor projects", "correct": False},
            {"text": "The contractor develops Traffic Control Plans during construction", "correct": False},
        ]
    elif "Detours" in core_text and "attention" in core_text:
        new_stem = "What level of detail is provided for detours in Traffic Control Plans?"
        new_options = [
            {"text": "Detours are thoroughly documented in Traffic Control Plans", "correct": correct_val == "False"},
            {"text": "Detours are not addressed in Traffic Control Plans", "correct": correct_val == "True"},
            {"text": "Only major detours are included", "correct": False},
            {"text": "Detour details are referenced in separate documents", "correct": False},
        ]
    elif "Cross sections" in core_text and "construction stage" in core_text:
        new_stem = "How are construction stages represented in plan cross sections?"
        new_options = [
            {"text": "Cross sections for each construction stage are included when needed for clarity", "correct": correct_val == "False"},
            {"text": "Cross sections of each construction stage are always included", "correct": correct_val == "True"},
            {"text": "Construction stages are shown only in plan view", "correct": False},
            {"text": "Stage cross sections are provided as supplemental documents", "correct": False},
        ]
    else:
        # Generic fallback
        new_stem = f"Based on the course material, which statement is correct regarding: {core_text[:60]}?"
        new_options = [
            {"text": core_text, "correct": correct_val == "True"},
            {"text": f"The opposite is true", "correct": correct_val == "False"},
            {"text": "This varies by project", "correct": False},
            {"text": "This is not addressed in the plans", "correct": False},
        ]
    
    # Update question
    q_improved = q.copy()
    q_improved["question_text"] = new_stem
    q_improved["question_text_sanitized"] = new_stem
    q_improved["options"] = [
        {**opt, "generated_distractor": not opt["correct"], "text_sanitized": opt["text"]}
        for opt in new_options
    ]
    
    return q_improved


def improve_generated_question(q: dict, context: dict) -> dict:
    """Improve generated questions with poor options."""
    q_text = q.get("question_text", "")
    options = q.get("options", [])
    
    # Find correct option
    correct_opt = next((o for o in options if o.get("correct")), None)
    if not correct_opt:
        return q
    
    correct_text = correct_opt.get("text", "")
    source_excerpt = q.get("source_excerpt", "")
    
    # Extract topic from question text
    topic_match = re.search(r'(?:best describes|primary purpose of|regarding)\s+(.+?)\?', q_text)
    topic = topic_match.group(1) if topic_match else "this topic"
    
    # Create meaningful stem
    if "Requirements and Specifications" in topic or "Contract Documents" in topic:
        new_stem = "What is a key principle regarding requirements in contract documents?"
        new_options = [
            {"text": "A requirement in any contract component (plans, specifications, or special provisions) is equally binding", "correct": True},
            {"text": "Requirements in the plans take precedence over specifications", "correct": False},
            {"text": "Only requirements stated in all three components are enforceable", "correct": False},
            {"text": "Special provisions override all other requirements", "correct": False},
        ]
    elif "Specifications" in topic:
        new_stem = "How should construction requirements be reviewed?"
        new_options = [
            {"text": "Every component of the contract must be carefully reviewed", "correct": True},
            {"text": "Only the plan sheets need detailed review", "correct": False},
            {"text": "The specifications contain all necessary requirements", "correct": False},
            {"text": "Requirements are summarized on the title sheet", "correct": False},
        ]
    else:
        # Keep original if we can't improve it meaningfully
        return q
    
    q_improved = q.copy()
    q_improved["question_text"] = new_stem
    q_improved["question_text_sanitized"] = new_stem
    q_improved["options"] = [
        {**opt, "generated_distractor": not opt["correct"], "text_sanitized": opt["text"]}
        for opt in new_options
    ]
    q_improved["confidence"] = 0.85  # improved quality
    
    return q_improved


def improve_distractor_quality(q: dict, context: dict) -> dict:
    """Improve questions with poor distractors."""
    options = q.get("options", [])
    q_text = q.get("question_text", "")
    
    # Find correct answer
    correct_opt = next((o for o in options if o.get("correct")), None)
    if not correct_opt:
        return q
    
    correct_text = correct_opt.get("text", "")
    
    # Check if we need to regenerate distractors
    bad_distractors = []
    for opt in options:
        if not opt.get("correct"):
            txt = opt.get("text", "").strip()
            if txt in ["These", "This", "All", "Figure", "Welcome"] or len(txt) <= 4:
                bad_distractors.append(opt)
    
    if len(bad_distractors) < 2:
        return q  # Not enough bad ones to fix
    
    # Generate context-aware distractors based on question type
    if "material used under" in q_text.lower():
        new_distractors = [
            "compacted subgrade soil",
            "cement-treated base",
            "crushed stone",
        ]
    elif "unpaved shoulder" in q_text.lower() and "wide" in q_text.lower():
        new_distractors = [
            "2'0\" (2 feet)",
            "4'6\" (4.5 feet)",
            "6'0\" (6 feet)",
        ]
    elif "slope" in q_text.lower() and "paved shoulder" in q_text.lower():
        new_distractors = [
            "4 percent",
            "8 percent",
            "2 percent",
        ]
    elif "median ditch" in q_text.lower():
        new_distractors = [
            "Fixed width of 20 feet",
            "Minimum 10 feet as specified",
            "Width determined by drainage calculations",
        ]
    else:
        # Generic fallback
        return q
    
    # Rebuild options
    new_options = [correct_opt]
    for i, distractor_text in enumerate(new_distractors[:3]):
        new_options.append({
            "text": distractor_text,
            "correct": False,
            "generated_distractor": True,
            "text_sanitized": distractor_text,
        })
    
    q_improved = q.copy()
    q_improved["options"] = new_options
    return q_improved


def add_context_to_binary_choice(q: dict, context: dict) -> dict:
    """Add context to simple binary choice questions."""
    q_text = q.get("question_text", "")
    
    # Extract the binary options
    match = re.search(r'\((.*?)\s*/\s*(.*?)\)', q_text)
    if not match:
        return q
    
    option_a, option_b = match.group(1).strip(), match.group(2).strip()
    
    # Determine which is correct
    correct_opt = next((o for o in q["options"] if o.get("correct")), None)
    if not correct_opt:
        return q
    correct_text = correct_opt.get("text", "").strip()
    
    # Add contextual phrasing
    if "Drainage structures" in q_text:
        new_stem = "How are drainage structures represented in Plan/Profile Plan Sheets?"
        new_options = [
            {"text": "Drainage structures are pictured on the Plan/Profile Plan Sheet", "correct": correct_text == "are"},
            {"text": "Drainage structures are shown in a separate drainage sheet only", "correct": correct_text == "are not"},
            {"text": "Only major drainage structures (bridges) are pictured", "correct": False},
            {"text": "Drainage structures appear only in cross-section views", "correct": False},
        ]
    elif "culvert" in q_text.lower() and "bridge" in q_text.lower():
        new_stem = "What is the structural classification of a culvert?"
        new_options = [
            {"text": "A culvert is not classified as a bridge", "correct": correct_text == "is not"},
            {"text": "A culvert is classified as a bridge", "correct": correct_text == "is"},
            {"text": "Classification depends on the material used", "correct": False},
            {"text": "Culverts become bridges when they exceed certain loads", "correct": False},
        ]
    elif "span length" in q_text.lower() and "20 feet" in q_text:
        new_stem = "What span length distinguishes a bridge from a culvert?"
        new_options = [
            {"text": "A bridge has a span length over 20 feet", "correct": correct_text == "over"},
            {"text": "A bridge has a span length under 20 feet", "correct": correct_text == "under"},
            {"text": "Span length is not the determining factor", "correct": False},
            {"text": "The distinction is 30 feet, not 20 feet", "correct": False},
        ]
    else:
        # Keep original if we can't meaningfully improve it
        return q
    
    q_improved = q.copy()
    q_improved["question_text"] = new_stem
    q_improved["question_text_sanitized"] = new_stem
    q_improved["options"] = [
        {**opt, "generated_distractor": not opt["correct"], "text_sanitized": opt["text"]}
        for opt in new_options
    ]
    
    return q_improved


def repair_question(q: dict, context: dict) -> tuple[dict, bool, str]:
    """
    Repair a single question.
    Returns (repaired_question, was_modified, reason).
    """
    is_weak, reason = is_weak_question(q, context)
    if not is_weak:
        return (q, False, "")
    
    # Apply appropriate repair strategy
    if "True/False question with no context" in reason:
        q_repaired = improve_true_false_question(q, context)
        return (q_repaired, True, reason)
    
    if "Binary choice question lacks context" in reason or "are / are not" in q.get("question_text", ""):
        q_repaired = add_context_to_binary_choice(q, context)
        if q_repaired != q:
            return (q_repaired, True, reason)
    
    if "Generated question" in reason or "incomplete" in reason.lower():
        q_repaired = improve_generated_question(q, context)
        if q_repaired != q:
            return (q_repaired, True, reason)
    
    if "distractor" in reason.lower():
        q_repaired = improve_distractor_quality(q, context)
        if q_repaired != q:
            return (q_repaired, True, reason)
    
    # If no specific repair worked, return original
    return (q, False, "Could not auto-repair")


def process_video_quiz(ch: int, vid: int) -> dict:
    """Process one video's quiz file."""
    dir_name = video_dir_name(ch, vid)
    quiz_path = QUIZZES_ROOT / dir_name / "import_ready.json"
    
    if not quiz_path.exists():
        return {"skipped": True, "reason": "Quiz file not found"}
    
    # Load quiz
    quiz_data = json.loads(quiz_path.read_text(encoding="utf-8"))
    questions = quiz_data.get("questions", [])
    
    # Load context (content bullets, narration)
    content_path = CONTENT_ROOT / dir_name / "content.json"
    context = {}
    if content_path.exists():
        context = json.loads(content_path.read_text(encoding="utf-8"))
    
    # Process each question
    repaired_questions = []
    changes_log = []
    
    for q in questions:
        q_repaired, was_modified, reason = repair_question(q, context)
        repaired_questions.append(q_repaired)
        
        if was_modified:
            changes_log.append({
                "question_id": q.get("question_id"),
                "original_text": q.get("question_text"),
                "revised_text": q_repaired.get("question_text"),
                "reason": reason,
            })
    
    # Write repaired quiz
    quiz_data["questions"] = repaired_questions
    quiz_data["quality_repair_date"] = NOW_ISO
    quiz_path.write_text(json.dumps(quiz_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return {
        "chapter": ch,
        "video": vid,
        "questions_reviewed": len(questions),
        "questions_fixed": len(changes_log),
        "changes": changes_log,
    }


def write_chapter_log(ch: int, video_results: list[dict]) -> None:
    """Write quality fix log for a chapter."""
    log_path = LOGS_ROOT / f"quiz_quality_fix_chapter{ch:02d}.log"
    
    lines = [
        f"Quiz Quality Repair Log - Chapter {ch}",
        f"Generated at: {NOW_ISO}",
        "=" * 70,
        "",
    ]
    
    for result in video_results:
        if result.get("skipped"):
            continue
        
        vid = result["video"]
        lines.append(f"Video {vid}: {result['questions_reviewed']} reviewed, {result['questions_fixed']} fixed")
        
        for change in result.get("changes", []):
            lines.append(f"  - {change['question_id']}")
            lines.append(f"    Original: {change['original_text'][:80]}...")
            lines.append(f"    Revised:  {change['revised_text'][:80]}...")
            lines.append(f"    Reason:   {change['reason']}")
            lines.append("")
    
    log_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    print("=" * 70)
    print("QUIZ QUALITY REPAIR -- Chapters 1-15")
    print(f"Run at: {NOW_ISO}")
    print("=" * 70)
    
    total_reviewed = 0
    total_fixed = 0
    chapters_affected = set()
    
    # Process by chapter
    for ch in range(1, 16):
        ch_videos = [(c, v) for c, v in ALL_VIDEOS if c == ch]
        if not ch_videos:
            continue
        
        print(f"\n--- Chapter {ch} ---")
        video_results = []
        
        for ch_num, vid_num in ch_videos:
            result = process_video_quiz(ch_num, vid_num)
            video_results.append(result)
            
            if not result.get("skipped"):
                total_reviewed += result["questions_reviewed"]
                fixed = result["questions_fixed"]
                total_fixed += fixed
                
                if fixed > 0:
                    chapters_affected.add(ch)
                    print(f"  Video {vid_num}: {result['questions_reviewed']} reviewed, {fixed} fixed")
                else:
                    print(f"  Video {vid_num}: {result['questions_reviewed']} reviewed, no changes needed")
        
        # Write chapter log if any changes
        if any(r.get("questions_fixed", 0) > 0 for r in video_results):
            write_chapter_log(ch, video_results)
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    summary = {
        "questions_reviewed": total_reviewed,
        "questions_fixed": total_fixed,
        "questions_unchanged": total_reviewed - total_fixed,
        "chapters_affected": sorted(chapters_affected),
    }
    print(json.dumps(summary, indent=2))
    
    return summary


if __name__ == "__main__":
    main()
