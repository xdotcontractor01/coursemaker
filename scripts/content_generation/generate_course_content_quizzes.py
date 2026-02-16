#!/usr/bin/env python3
"""
Course Content & Quiz JSON Generator -- Chapters 1-15
=====================================================
Single-run script that:
  0. Feasibility check
  1. Loads manifests, builds video map
  2. Parses markdown for questions & answers
  3. Maps questions -> videos
  4. Generates course-content bullets per video
  5. Builds quiz import_ready.json (MCQ conversion, distractors, confidence)
  6. Sanitization pass
  7. Confidence / review gating
  8. Writes all output files, prints JSON summary

Usage:
  python generate_course_content_quizzes.py                 # defaults to chapters 5-15
  python generate_course_content_quizzes.py --chapters 1-4  # chapters 1-4 only
  python generate_course_content_quizzes.py --chapters 1-15 # all chapters
"""

import argparse
import json
import os
import re
import csv
import sys
import random
import logging
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
from typing import Any

# --- constants ----------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]  # coursemaker/
MARKDOWN_PATH = ROOT / "docs" / "MinerU_markdown_BasicHiwyPlanReading (1)_20260129005532_2016555753310150656.md"
CHAPTER_FILE_STRUCTURE = ROOT / "docs" / "CHAPTER_FILE_STRUCTURE.md"

# Default chapter range (overridden by --chapters CLI argument)
CHAPTERS = list(range(5, 16))  # 5..15
CHAPTERS_SET: set[int] = set(CHAPTERS)  # for fast membership tests


def parse_chapter_range(s: str) -> list[int]:
    """Parse a chapter range string like '1-4' or '5-15' into a list of ints."""
    if "-" in s:
        parts = s.split("-")
        return list(range(int(parts[0]), int(parts[1]) + 1))
    return [int(x) for x in s.split(",")]


# Chapter 1 uses separate per-video manifests (chapter01_video01.json, ...);
# Chapters 2-4 use chapter_0X.json; Chapters 5+ use chapter0X.json.
def manifest_paths_for_chapter(ch: int) -> list[Path]:
    """Return list of manifest paths for a chapter (usually 1, but ch1 has 4)."""
    if ch == 1:
        # Chapter 1 has 4 separate per-video manifest files
        paths = []
        for v in range(1, 5):
            p = ROOT / "manifests" / f"chapter01_video{v:02d}.json"
            paths.append(p)
        return paths
    elif ch <= 4:
        return [ROOT / "manifests" / f"chapter_{ch:02d}.json"]
    return [ROOT / "manifests" / f"chapter{ch:02d}.json"]

# Output roots
COURSE_CONTENT_ROOT = ROOT / "manifests" / "course_content"
QUIZZES_ROOT        = ROOT / "quizzes"
SANITIZATION_ROOT   = ROOT / "sanitization"
LOGS_ROOT           = ROOT / "logs"
REVIEW_ROOT         = ROOT / "review"

OUTPUT_DIRS = [COURSE_CONTENT_ROOT, QUIZZES_ROOT, SANITIZATION_ROOT, LOGS_ROOT, REVIEW_ROOT]

# Video (lesson) splits for chapters that lack lesson_boundaries in their manifest.
# Derived from the Manim scene classes in manim_scripts/chapter0X.py.
FALLBACK_VIDEO_SPLITS: dict[int, list[list[int]]] = {
    5:  [[1, 2, 3, 4, 5, 6]],
    6:  [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12, 13]],
    7:  [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]],
}

NOW_ISO = datetime.now(timezone.utc).isoformat()

# --- helpers ------------------------------------------------------------------

def pretty_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def clean_text(text: str) -> str:
    """Clean text for use in quiz options: remove newlines, extra spaces, LaTeX."""
    t = text.replace("\n", " ").replace("\r", " ")
    t = re.sub(r'\$[^$]*\$', lambda m: m.group(0).replace('$', '').strip(), t)
    t = re.sub(r'\s{2,}', ' ', t)
    return t.strip()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(obj), encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def write_log(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def video_dir_name(ch: int, vid: int) -> str:
    return f"Chapter{ch:02d}_video{vid:02d}"


def question_id(ch: int, vid: int, q_idx: int) -> str:
    return f"ch{ch:02d}_vid{vid:02d}_q{q_idx:02d}"


# --- STEP 0: feasibility check -----------------------------------------------

def step0_feasibility() -> bool:
    print("=" * 60)
    print("STEP 0 -- FEASIBILITY CHECK")
    print("=" * 60)
    missing: list[str] = []

    # Markdown
    if not MARKDOWN_PATH.is_file():
        missing.append(str(MARKDOWN_PATH))

    # CHAPTER_FILE_STRUCTURE.md
    if not CHAPTER_FILE_STRUCTURE.is_file():
        missing.append(str(CHAPTER_FILE_STRUCTURE))

    # Manifests
    for ch in CHAPTERS:
        for mp in manifest_paths_for_chapter(ch):
            if not mp.is_file():
                missing.append(str(mp))

    # Output dirs -- try creating them
    for d in OUTPUT_DIRS:
        try:
            d.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            missing.append(f"{d} (write failed: {e})")

    if missing:
        print("FEASIBILITY -- NO")
        print("Missing paths:")
        for m in missing:
            print(f"  - {m}")
        return False

    print("FEASIBILITY -- YES")
    print(f"  Markdown : {MARKDOWN_PATH}")
    print(f"  Manifests: {len(CHAPTERS)} chapters ({CHAPTERS[0]}--{CHAPTERS[-1]})")
    print(f"  Outputs  : {', '.join(d.name for d in OUTPUT_DIRS)}")
    return True


# --- STEP 1: load manifests & build video map --------------------------------

class VideoInfo:
    """Represents a single video (lesson) within a chapter."""
    def __init__(self, chapter: int, video_num: int, title: str,
                 scene_indices: list[int], scenes: list[dict],
                 source_pages: str, manifest_path_str: str):
        self.chapter = chapter
        self.video_num = video_num
        self.title = title
        self.scene_indices = scene_indices
        self.scenes = scenes
        self.source_pages = source_pages
        self.manifest_path_str = manifest_path_str

    @property
    def page_range(self) -> tuple[int, int]:
        """Return (start_page, end_page) from collected scene source_pages."""
        pages: list[int] = []
        for sc in self.scenes:
            for p in str(sc.get("source_pages", "")).replace("-", " ").split():
                try:
                    pages.append(int(p))
                except ValueError:
                    pass
        if not pages:
            return (0, 0)
        return (min(pages), max(pages))


def step1_load_manifests() -> tuple[dict[int, dict], list[VideoInfo]]:
    """Load all manifests and build a flat list of VideoInfo objects."""
    print("\n" + "=" * 60)
    print("STEP 1 -- LOAD MANIFESTS & BUILD VIDEO MAP")
    print("=" * 60)

    manifests: dict[int, dict] = {}
    videos: list[VideoInfo] = []

    for ch in CHAPTERS:
        mpaths = manifest_paths_for_chapter(ch)

        if ch == 1:
            # Chapter 1: separate per-video manifests (chapter01_video01..04.json)
            # Each file is one video with its own scenes list.
            combined_scenes: list[dict] = []
            for vid_num, mp in enumerate(mpaths, start=1):
                with open(mp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                all_scenes = data.get("scenes", [])
                combined_scenes.extend(all_scenes)
                idxs = [s["index"] for s in all_scenes]
                page_nums = set()
                for sc in all_scenes:
                    for p in str(sc.get("source_pages", "")).replace("-", " ").split():
                        try:
                            page_nums.add(int(p))
                        except ValueError:
                            pass
                if page_nums:
                    sp = f"{min(page_nums)}-{max(page_nums)}" if min(page_nums) != max(page_nums) else str(min(page_nums))
                else:
                    sp = data.get("pages", "")
                videos.append(VideoInfo(
                    chapter=ch, video_num=vid_num,
                    title=data.get("title", f"Video {vid_num}"),
                    scene_indices=idxs, scenes=all_scenes,
                    source_pages=sp, manifest_path_str=str(mp.relative_to(ROOT)),
                ))
            # Store a combined manifest for chapter-level lookups
            manifests[ch] = {"chapter": 1, "pages": "1-11", "scenes": combined_scenes}
            continue

        # Chapters 2+ : single manifest file
        mp = mpaths[0]
        with open(mp, "r", encoding="utf-8") as f:
            data = json.load(f)
        manifests[ch] = data

        all_scenes = data.get("scenes", [])
        scene_by_index = {s["index"]: s for s in all_scenes}

        # Determine lesson/video splits
        if "lesson_boundaries" in data and data["lesson_boundaries"]:
            # Chapters 8-15 style
            lb = data["lesson_boundaries"]
            for vid_num, (key, info) in enumerate(sorted(lb.items()), start=1):
                idxs = info["scenes"]
                selected = [scene_by_index[i] for i in idxs if i in scene_by_index]
                # Compute page range string
                page_nums = set()
                for sc in selected:
                    for p in str(sc.get("source_pages", "")).replace("-", " ").split():
                        try:
                            page_nums.add(int(p))
                        except ValueError:
                            pass
                if page_nums:
                    sp = f"{min(page_nums)}-{max(page_nums)}" if min(page_nums) != max(page_nums) else str(min(page_nums))
                else:
                    sp = data.get("pages", "")
                videos.append(VideoInfo(
                    chapter=ch, video_num=vid_num,
                    title=info.get("title", f"Lesson {vid_num}"),
                    scene_indices=idxs, scenes=selected,
                    source_pages=sp, manifest_path_str=str(mp.relative_to(ROOT)),
                ))
        elif ch in FALLBACK_VIDEO_SPLITS:
            splits = FALLBACK_VIDEO_SPLITS[ch]
            for vid_num, idxs in enumerate(splits, start=1):
                selected = [scene_by_index[i] for i in idxs if i in scene_by_index]
                page_nums = set()
                for sc in selected:
                    for p in str(sc.get("source_pages", "")).replace("-", " ").split():
                        try:
                            page_nums.add(int(p))
                        except ValueError:
                            pass
                if page_nums:
                    sp = f"{min(page_nums)}-{max(page_nums)}" if min(page_nums) != max(page_nums) else str(min(page_nums))
                else:
                    sp = data.get("pages", "")
                # Generate a title from scenes
                title_parts = [sc.get("title", "") for sc in selected[:2]]
                title = " / ".join(t for t in title_parts if t and t != "Title") or f"Part {vid_num}"
                videos.append(VideoInfo(
                    chapter=ch, video_num=vid_num,
                    title=title, scene_indices=idxs, scenes=selected,
                    source_pages=sp, manifest_path_str=str(mp.relative_to(ROOT)),
                ))
        else:
            # Single video chapter (ch2, ch3, ch4, ch9, ch10, ch11, ch12, ch14)
            idxs = [s["index"] for s in all_scenes]
            videos.append(VideoInfo(
                chapter=ch, video_num=1,
                title=data.get("title", f"Chapter {ch}"),
                scene_indices=idxs, scenes=all_scenes,
                source_pages=data.get("pages", ""),
                manifest_path_str=str(mp.relative_to(ROOT)),
            ))

    print(f"  Loaded {len(manifests)} manifests -> {len(videos)} videos")
    for v in videos:
        print(f"    Ch{v.chapter:02d} vid{v.video_num:02d}: scenes {v.scene_indices} pages={v.source_pages} \"{v.title}\"")
    return manifests, videos


# --- STEP 2: parse markdown for questions & answers --------------------------

class ParsedQuestion:
    def __init__(self, chapter: int, q_num: int, text: str, line_num: int,
                 q_type: str = "open", answer: str = ""):
        self.chapter = chapter
        self.q_num = q_num
        self.text = text
        self.line_num = line_num
        self.q_type = q_type      # "true_false", "binary_choice", "fill_blank", "open", "matching"
        self.answer = answer
        self.video_num: int | None = None
        self.ambiguous = False

    def __repr__(self):
        return f"Q({self.chapter}-{self.q_num} [{self.q_type}] vid={self.video_num})"


def classify_question_type(text: str) -> str:
    t = text.strip()
    # True/False
    if re.search(r'\bTrue\s+False\b', t, re.IGNORECASE) or re.search(r'\b(true|false)\b.*\b(true|false)\b', t, re.IGNORECASE):
        return "true_false"
    # Binary choice: (are / are not), (is / is not), (do / do not), (greater / less), (over / under)
    if re.search(r'\([^)]+\s*/\s*[^)]+\)', t):
        return "binary_choice"
    # Fill-in-the-blank
    if '______' in t or '________' in t:
        return "fill_blank"
    # Matching (like "Match the Columns")
    if re.search(r'[Mm]atch', t):
        return "matching"
    return "open"


def step2_parse_markdown() -> list[ParsedQuestion]:
    print("\n" + "=" * 60)
    print("STEP 2 -- PARSE MARKDOWN FOR QUESTIONS & ANSWERS")
    print("=" * 60)

    md_text = MARKDOWN_PATH.read_text(encoding="utf-8")
    lines = md_text.split("\n")

    # -- Parse questions --
    # Pattern: line starts with digit(s)-digit(s) followed by space and text
    # e.g. "8-1 Drainage structures (are / are not) pictured..."
    # Also handle "# 4-1 Match the Columns" (prefixed with # and chapter-relative numbering)
    q_pattern = re.compile(r'^#?\s*(\d{1,2})-(\d{1,3})\s+(.+)')
    chapter_heading_re = re.compile(r'^#\s*Chapter\s+(\d+)', re.IGNORECASE)

    questions: list[ParsedQuestion] = []
    seen_keys: set[tuple[int, int]] = set()

    # --- Pre-scan: find the LAST "Answers to Chapter Questions" heading and
    # the first REAL chapter content heading (has a colon, e.g., "# Chapter 1: ...").
    # This avoids confusing the Table of Contents entries with real content.
    answers_section_start: int | None = None
    real_content_start: int | None = None
    for i, line in enumerate(lines, start=1):
        if re.match(r'^#\s*Answers\s+to\s+Chapter\s+Questions', line, re.IGNORECASE):
            answers_section_start = i  # last occurrence wins
        # Real chapter content headings have "Chapter N:" with a colon
        if real_content_start is None and re.match(r'^#\s*Chapter\s+\d+\s*:', line, re.IGNORECASE):
            real_content_start = i

    if real_content_start is None:
        real_content_start = 1

    print(f"  Real content starts at line {real_content_start}")
    print(f"  Answers section at line {answers_section_start}")

    # Determine the end line for question scanning
    scan_end = answers_section_start if answers_section_start and answers_section_start > real_content_start else len(lines)

    # --- Parse questions from real content area only ---
    current_chapter: int | None = None

    for i, line in enumerate(lines, start=1):
        if i < real_content_start:
            continue
        if i >= scan_end:
            break

        # Track chapter headings (both "# Chapter 8: Drainage" and "# CHAPTER 8")
        chm = chapter_heading_re.match(line)
        if chm:
            current_chapter = int(chm.group(1))

        m = q_pattern.match(line.strip())
        if m:
            ch_num = int(m.group(1))
            q_num = int(m.group(2))
            q_text = m.group(3).strip()

            # Handle OCR errors: e.g., "14-1" extracted as "4-1".
            # If ch_num doesn't match current_chapter but could be a suffix,
            # use current_chapter instead.
            if current_chapter is not None and ch_num != current_chapter:
                ch_str = str(current_chapter)
                parsed_str = str(ch_num)
                if ch_str.endswith(parsed_str):
                    ch_num = current_chapter

            # Sanity: chapter number should be in the target set
            if ch_num not in CHAPTERS_SET:
                continue

            # Multi-line: gather continuation lines (non-empty, non-heading, no new question)
            j = i  # 1-based index of current line
            while j < len(lines):
                next_line = lines[j].strip()  # lines is 0-indexed so lines[j] is line j+1
                if not next_line or next_line.startswith("#") or q_pattern.match(next_line):
                    break
                # Skip image lines
                if next_line.startswith("![") or next_line.startswith("<"):
                    break
                q_text += " " + next_line
                j += 1

            key = (ch_num, q_num)
            if key not in seen_keys:
                seen_keys.add(key)
                q_type = classify_question_type(q_text)
                questions.append(ParsedQuestion(
                    chapter=ch_num, q_num=q_num, text=q_text,
                    line_num=i, q_type=q_type
                ))

    print(f"  Found {len(questions)} questions in content section")

    # -- Parse answers --
    if answers_section_start is None:
        # Try to find it by searching for the heading; take the LAST occurrence
        # to skip the Table of Contents entry
        for i, line in enumerate(lines, start=1):
            if re.match(r'^#\s*Answers\s+to\s+Chapter\s+Questions', line, re.IGNORECASE):
                answers_section_start = i  # keep updating; last match wins

    if answers_section_start is None:
        print("  WARNING: Could not find 'Answers to Chapter Questions' section")
        return questions

    ans_pattern = re.compile(r'^(\d{1,2})-(\d{1,3})[.\s]+(.+)')
    current_ans_chapter = None
    ans_chapter_re = re.compile(r'^#\s*CHAPTER\s+(\d+)', re.IGNORECASE)

    answers: dict[tuple[int, int], str] = {}

    for i in range(answers_section_start - 1, len(lines)):
        line = lines[i].strip()

        # Track answer chapter headings
        acm = ans_chapter_re.match(line)
        if acm:
            current_ans_chapter = int(acm.group(1))
            continue

        # Stop if we hit non-answer sections
        if re.match(r'^#\s*(APPENDICES|Index)\b', line, re.IGNORECASE):
            break

        m = ans_pattern.match(line)
        if m:
            ch_num = int(m.group(1))
            q_num = int(m.group(2))
            ans_text = m.group(3).strip()

            # Multi-line answers: gather continuation lines
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line or next_line.startswith("#") or ans_pattern.match(next_line):
                    break
                ans_text += " " + next_line
                j += 1

            # Clean up LaTeX artifacts
            ans_text = re.sub(r'\$[^$]*\$', lambda m2: m2.group(0).replace('$', '').strip(), ans_text)

            answers[(ch_num, q_num)] = ans_text

    print(f"  Found {len(answers)} answers in answers section")

    # Match answers to questions
    matched = 0
    for q in questions:
        key = (q.chapter, q.q_num)
        if key in answers:
            q.answer = answers[key]
            matched += 1
    print(f"  Matched {matched}/{len(questions)} questions to answers")

    # Summary per chapter
    ch_counts: dict[int, int] = defaultdict(int)
    for q in questions:
        ch_counts[q.chapter] += 1
    for ch in sorted(ch_counts):
        print(f"    Ch{ch:02d}: {ch_counts[ch]} questions")

    return questions


# --- STEP 3: map questions -> videos ------------------------------------------

def step3_map_questions_to_videos(
    questions: list[ParsedQuestion],
    videos: list[VideoInfo],
    manifests: dict[int, dict],
) -> dict[tuple[int, int], list[ParsedQuestion]]:
    """
    For each question, determine which video it belongs to.
    Returns dict keyed by (chapter, video_num) -> list of questions.
    """
    print("\n" + "=" * 60)
    print("STEP 3 -- MAP QUESTIONS -> VIDEOS")
    print("=" * 60)

    # Build lookup: chapter -> list of VideoInfo sorted by video_num
    ch_videos: dict[int, list[VideoInfo]] = defaultdict(list)
    for v in videos:
        ch_videos[v.chapter].append(v)
    for ch in ch_videos:
        ch_videos[ch].sort(key=lambda v: v.video_num)

    # Read the markdown to find page context for questions
    md_text = MARKDOWN_PATH.read_text(encoding="utf-8")
    md_lines = md_text.split("\n")

    # Build a mapping of markdown line number -> approximate page number
    # We use chapter headings and page references to estimate page numbers
    # The manifest's chapter.pages gives us the page range for each chapter
    chapter_line_ranges: dict[int, tuple[int, int]] = {}

    # Use "real" chapter headings (with colon, like "# Chapter 1: ...") to skip TOC entries
    chapter_heading_re = re.compile(r'^#\s*Chapter\s+(\d+)\s*:', re.IGNORECASE)
    chapter_heading_re_no_colon = re.compile(r'^#\s*Chapter\s+(\d+)', re.IGNORECASE)

    chapter_starts: list[tuple[int, int]] = []  # (line_num, chapter)

    # Find the LAST "Answers to Chapter Questions" heading (skip TOC entry)
    answers_line = len(md_lines)
    for i, line in enumerate(md_lines):
        if re.match(r'^#\s*Answers\s+to\s+Chapter\s+Questions', line, re.IGNORECASE):
            answers_line = i  # keep updating to get the LAST one

    # First try headings with colon (real content headings)
    for i, line in enumerate(md_lines[:answers_line]):
        m = chapter_heading_re.match(line)
        if m:
            chapter_starts.append((i, int(m.group(1))))

    # If no colon headings found, fall back to any chapter heading after line 300
    # (skipping Table of Contents entries)
    if not chapter_starts:
        for i, line in enumerate(md_lines[:answers_line]):
            if i < 300:
                continue
            m = chapter_heading_re_no_colon.match(line)
            if m:
                chapter_starts.append((i, int(m.group(1))))

    # Map each question to a video using its position relative to scene content
    # Strategy: for each chapter, compute the fraction of questions by position
    # and split them across videos proportionally to scene count.
    video_questions: dict[tuple[int, int], list[ParsedQuestion]] = defaultdict(list)

    for ch in CHAPTERS:
        ch_qs = [q for q in questions if q.chapter == ch]
        if not ch_qs:
            continue

        vids = ch_videos.get(ch, [])
        if not vids:
            continue

        if len(vids) == 1:
            # All questions go to the single video
            for q in ch_qs:
                q.video_num = 1
                video_questions[(ch, 1)].append(q)
            continue

        # Multiple videos -- TWO strategies attempted in order:
        #   A) Page estimation from figure references in the markdown
        #   B) Scene source_text markers in the markdown (fallback)

        # --- Strategy A: figure-based page estimation ---
        # Find chapter's line range in the markdown
        ch_start_line = 0
        ch_end_line = len(md_lines)
        for ci, (cline, cnum) in enumerate(chapter_starts):
            if cnum == ch:
                ch_start_line = cline
                if ci + 1 < len(chapter_starts):
                    ch_end_line = chapter_starts[ci + 1][0]
                break

        # Build page anchors from figure references within chapter lines
        fig_re = re.compile(r'Figure\s+' + str(ch) + r'-(\d+)', re.IGNORECASE)
        page_anchors: list[tuple[int, int]] = []  # (line, page)
        fig_path_re_cache: dict[int, re.Pattern] = {}
        for li in range(ch_start_line, min(ch_end_line, len(md_lines))):
            m = fig_re.search(md_lines[li])
            if m:
                fig_num = int(m.group(1))
                if fig_num not in fig_path_re_cache:
                    fig_path_re_cache[fig_num] = re.compile(
                        rf'figure_{ch}_{fig_num}(?!\d)')
                fig_path_pattern = fig_path_re_cache[fig_num]
                matched_anchor = False
                for v in vids:
                    if matched_anchor:
                        break
                    for sc in v.scenes:
                        if matched_anchor:
                            break
                        for ip in sc.get("image_paths", []):
                            if ip is not None and fig_path_pattern.search(ip):
                                sp = str(sc.get("source_pages", ""))
                                try:
                                    pg = int(sp.split("-")[0])
                                    page_anchors.append((li, pg))
                                    matched_anchor = True
                                except ValueError:
                                    pass
                                break

        # Deduplicate: keep first per line
        seen_lines: set[int] = set()
        page_anchors = [a for a in page_anchors if not (a[0] in seen_lines or seen_lines.add(a[0]))]  # type: ignore[func-returns-value]

        use_page_estimation = len(page_anchors) >= 2  # need at least 2 anchors

        if use_page_estimation:
            ch_manifest = manifests.get(ch, {})
            ch_pages = str(ch_manifest.get("pages", ""))
            if "-" in ch_pages:
                try:
                    ch_page_start = int(ch_pages.split("-")[0])
                    ch_page_end = int(ch_pages.split("-")[1])
                except ValueError:
                    ch_page_start, ch_page_end = 1, 1
            else:
                try:
                    ch_page_start = ch_page_end = int(ch_pages) if ch_pages else 1
                except ValueError:
                    ch_page_start = ch_page_end = 1

            page_anchors.sort()
            page_anchors = [(ch_start_line, ch_page_start)] + page_anchors + [(ch_end_line, ch_page_end)]

            for q in ch_qs:
                q_line = q.line_num - 1

                est_page = ch_page_start
                for ai in range(len(page_anchors) - 1):
                    a_line, a_page = page_anchors[ai]
                    b_line, b_page = page_anchors[ai + 1]
                    if a_line <= q_line <= b_line:
                        if b_line > a_line:
                            frac = (q_line - a_line) / (b_line - a_line)
                        else:
                            frac = 0.0
                        est_page = a_page + frac * (b_page - a_page)
                        break
                else:
                    est_page = page_anchors[-1][1]

                # Find video whose page range best matches
                best_vid = vids[0].video_num
                best_dist = 9999.0
                for v in vids:
                    p_start, p_end = v.page_range
                    if p_start <= est_page <= p_end:
                        dist = 0.0
                    else:
                        dist = min(abs(est_page - p_start), abs(est_page - p_end))
                    if dist < best_dist:
                        best_dist = dist
                        best_vid = v.video_num

                # Overlapping page ranges -> mark ambiguous, prefer later video
                candidates = [v.video_num for v in vids
                              if v.page_range[0] <= est_page <= v.page_range[1]]
                if len(candidates) > 1:
                    q.ambiguous = True
                    best_vid = max(candidates)

                q.video_num = best_vid
                video_questions[(ch, best_vid)].append(q)
            continue

        # --- Strategy B: scene source_text markers ---
        scene_markers: list[tuple[int, int, int]] = []  # (md_line, scene_index, video_num)
        for v in vids:
            for sc in v.scenes:
                src_text = sc.get("source_text", "")
                if len(src_text) > 20:
                    search_str = src_text[:40].strip()
                    for li, ml in enumerate(md_lines):
                        if search_str in ml:
                            scene_markers.append((li, sc["index"], v.video_num))
                            break

        if not scene_markers:
            # Last resort: distribute evenly
            qs_per_vid = len(ch_qs) // len(vids)
            remainder = len(ch_qs) % len(vids)
            idx = 0
            for v in vids:
                count = qs_per_vid + (1 if v.video_num <= remainder else 0)
                for q in ch_qs[idx:idx + count]:
                    q.video_num = v.video_num
                    video_questions[(ch, v.video_num)].append(q)
                idx += count
            continue

        scene_markers.sort(key=lambda x: x[0])

        for q in ch_qs:
            q_line = q.line_num - 1
            assigned_vid = vids[0].video_num

            for md_line, sc_idx, vid_num in reversed(scene_markers):
                if md_line <= q_line:
                    assigned_vid = vid_num
                    break

            next_vid_markers = [(ml, si, vn) for ml, si, vn in scene_markers if vn > assigned_vid]
            if next_vid_markers:
                next_vid_first_line = next_vid_markers[0][0]
                if abs(q_line - next_vid_first_line) < 20:
                    q.ambiguous = True

            q.video_num = assigned_vid
            video_questions[(ch, assigned_vid)].append(q)

    # Summary
    total_mapped = sum(1 for q in questions if q.video_num is not None)
    total_ambig = sum(1 for q in questions if q.ambiguous)
    print(f"  Mapped {total_mapped}/{len(questions)} questions to videos")
    print(f"  Ambiguous mappings: {total_ambig}")
    for key in sorted(video_questions):
        ch, vid = key
        qs = video_questions[key]
        print(f"    Ch{ch:02d} vid{vid:02d}: {len(qs)} questions")

    return video_questions


# --- STEP 4: course content JSON ---------------------------------------------

def extract_key_phrases_from_narration(narration: str, max_bullets: int = 6) -> list[str]:
    """Extract short key phrases from narration text."""
    # Split into sentences
    sentences = re.split(r'[.!?]\s+', narration)
    phrases: list[str] = []
    for sent in sentences:
        sent = sent.strip()
        if not sent or len(sent) < 10:
            continue
        # Skip greeting/transition sentences
        if re.match(r'^(Welcome|Let\'s|In this|In the next|This chapter)', sent, re.IGNORECASE):
            continue
        # Truncate to ~12 words
        words = sent.split()
        if len(words) > 12:
            words = words[:12]
        phrase = " ".join(words)
        # Clean trailing punctuation
        phrase = phrase.rstrip(".,;:")
        if phrase and phrase not in phrases:
            phrases.append(phrase)
        if len(phrases) >= max_bullets:
            break
    return phrases


def step4_generate_course_content(videos: list[VideoInfo]) -> dict[str, Any]:
    """Generate course content bullets for each video."""
    print("\n" + "=" * 60)
    print("STEP 4 -- GENERATE COURSE CONTENT JSON")
    print("=" * 60)

    content_outputs: dict[str, Any] = {}

    for v in videos:
        # Aggregate bullets from all scenes
        all_bullets: list[str] = []
        for sc in v.scenes:
            for b in sc.get("bullets", []):
                if b and b not in all_bullets:
                    all_bullets.append(b)

        # Select 4-6 diverse bullets
        selected_bullets = all_bullets[:6]

        # If fewer than 4, supplement from narration text
        if len(selected_bullets) < 4:
            for sc in v.scenes:
                narr = sc.get("narration_text", "")
                extra = extract_key_phrases_from_narration(narr, 6 - len(selected_bullets))
                for phrase in extra:
                    if phrase not in selected_bullets:
                        selected_bullets.append(phrase)
                    if len(selected_bullets) >= 6:
                        break
                if len(selected_bullets) >= 6:
                    break

        # Ensure bullets are within 10-12 words
        trimmed: list[str] = []
        for b in selected_bullets[:6]:
            words = b.split()
            if len(words) > 12:
                b = " ".join(words[:12]).rstrip(".,;:")
            trimmed.append(b)

        content = {
            "chapter": v.chapter,
            "video": v.video_num,
            "title": v.title,
            "source_pages": v.source_pages,
            "source_manifest": v.manifest_path_str,
            "scene_range": [v.scene_indices[0], v.scene_indices[-1]] if v.scene_indices else [],
            "bullets": trimmed,
            "generated_at": NOW_ISO,
        }

        dir_name = video_dir_name(v.chapter, v.video_num)
        content_outputs[dir_name] = content
        print(f"  {dir_name}: {len(trimmed)} bullets")

    return content_outputs


# --- STEP 5: build quiz JSONs ------------------------------------------------

def extract_binary_choices(text: str) -> list[str]:
    """Extract options from binary choice patterns like (are / are not)."""
    m = re.search(r'\(([^/]+)/([^)]+)\)', text)
    if m:
        return [m.group(1).strip(), m.group(2).strip()]
    return []


def get_chapter_terms(videos: list[VideoInfo], chapter: int) -> list[str]:
    """Collect technical terms from a chapter's narration for distractor generation."""
    # Common English words that should NOT be used as distractors
    STOP_WORDS = {
        "the", "this", "that", "these", "those", "here", "there", "where",
        "when", "what", "which", "who", "how", "why", "now", "then", "also",
        "very", "just", "only", "even", "still", "some", "many", "much",
        "more", "most", "such", "each", "both", "its", "you", "your",
        "they", "them", "their", "our", "his", "her", "she", "him",
        "was", "were", "are", "been", "being", "have", "has", "had",
        "will", "would", "could", "should", "may", "might", "can",
        "let", "not", "but", "and", "for", "with", "from", "into",
        "over", "under", "about", "above", "below", "between",
        "welcome", "chapter", "rather", "however", "therefore",
        "next", "first", "second", "third", "last", "new", "old",
        "one", "two", "three", "four", "five", "six", "seven", "eight",
        "note", "see", "figure", "example", "page",
    }

    terms: list[str] = []
    for v in videos:
        if v.chapter != chapter:
            continue
        for sc in v.scenes:
            # Collect bullet points (good distractor candidates)
            for b in sc.get("bullets", []):
                if b and len(b.split()) >= 2:  # require at least 2-word phrases
                    terms.append(b)
            # Extract technical noun phrases from narration (multi-word only)
            narr = sc.get("narration_text", "")
            # Find multi-word capitalized phrases (likely proper nouns or technical terms)
            caps = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', narr)
            terms.extend(caps)
            # Also find key phrases around "is", "are", "called", "means", "refers to"
            key_phrases = re.findall(
                r'(?:called|is a|are |refers to|known as)\s+(?:the\s+)?([A-Za-z][\w\s]{4,30}?)(?:[.,;!?]|$)',
                narr, re.IGNORECASE)
            for kp in key_phrases:
                kp = kp.strip()
                if len(kp.split()) >= 2:
                    terms.append(kp)

    # Patterns that should never appear as distractors
    BAD_PATTERNS = re.compile(
        r'^chapter\s+(one|two|three|four|five|six|seven|eight|nine|ten|'
        r'eleven|twelve|thirteen|fourteen|fifteen|\d+)',
        re.IGNORECASE
    )

    # Deduplicate while preserving order, and filter out stop words / short terms
    seen: set[str] = set()
    unique: list[str] = []
    for t in terms:
        tl = t.lower().strip()
        # Skip single stop words and very short terms
        if tl in STOP_WORDS:
            continue
        if len(tl) < 4:  # skip terms shorter than 4 chars
            continue
        # Skip "Chapter X" patterns
        if BAD_PATTERNS.match(tl):
            continue
        if tl not in seen:
            seen.add(tl)
            unique.append(t)
    return unique


def generate_distractors(correct_answer: str, chapter_terms: list[str],
                         question_text: str, count: int = 3) -> list[str]:
    """Generate plausible distractors from chapter terms."""
    correct_lower = correct_answer.lower().strip()
    q_lower = question_text.lower()
    distractors: list[str] = []

    # Filter terms that aren't the correct answer
    candidates: list[str] = []
    for t in chapter_terms:
        tl = t.lower().strip()
        if tl != correct_lower and len(t) >= 4 and tl not in correct_lower:
            candidates.append(t)

    # Try to find same-length or similar-type distractors
    # Check if answer is numeric
    if re.match(r'^[\d.,]+\s*(%|feet|ft|inches?|degrees?|\'|\")?', correct_answer.strip()):
        # Generate numeric distractors
        num_match = re.match(r'^([\d.]+)', correct_answer.strip())
        if num_match:
            base_val = float(num_match.group(1))
            suffix = correct_answer.strip()[len(num_match.group(1)):].strip()
            offsets = [0.5, 1.5, 2.0, 0.25, 3.0]
            random.seed(hash(question_text) % 2**31)
            random.shuffle(offsets)
            for offset in offsets:
                d = f"{base_val + offset}{' ' + suffix if suffix else ''}"
                if d.lower() != correct_lower and d not in distractors:
                    distractors.append(d)
                if len(distractors) >= count:
                    break

    # Prefer multi-word candidates that are similar in length to the answer
    if len(distractors) < count:
        answer_words = len(correct_answer.split())
        # Sort candidates by relevance: prefer similar word-count and multi-word terms
        def relevance_score(term: str) -> float:
            tw = len(term.split())
            # Prefer terms with similar word count
            word_diff = abs(tw - answer_words)
            # Prefer multi-word terms (bullets)
            multi_bonus = 2.0 if tw >= 2 else 0.0
            # Prefer shorter terms over very long ones
            length_penalty = max(0, len(term) - 60) * 0.1
            return multi_bonus - word_diff * 0.5 - length_penalty

        random.seed(hash(question_text) % 2**31)  # deterministic per question
        # Score and sort, then shuffle within same-score groups for variety
        scored = [(relevance_score(c), random.random(), c) for c in candidates]
        scored.sort(key=lambda x: (-x[0], x[1]))

        for _, _, c in scored:
            if c not in distractors and c.lower() != correct_lower:
                distractors.append(c)
            if len(distractors) >= count:
                break

    # If still not enough, generate domain-relevant generic distractors
    generic = [
        "Not shown on the plan sheets",
        "Determined by the project engineer",
        "Varies by project specifications",
        "Not applicable to this plan type",
        "Specified in supplemental documents",
        "Depends on field conditions",
    ]
    random.seed(hash(question_text + "generic") % 2**31)
    random.shuffle(generic)
    for g in generic:
        if len(distractors) >= count:
            break
        if g not in distractors and g.lower() != correct_lower:
            distractors.append(g)

    return distractors[:count]


def generate_questions_from_narration(
    video: VideoInfo, start_q_idx: int
) -> list[dict]:
    """Generate 2 quiz questions from narration bullets when no PDF questions exist."""
    generated: list[dict] = []

    # Collect key facts from narration
    facts: list[tuple[str, str]] = []  # (concept, detail)
    for sc in video.scenes:
        narr = sc.get("narration_text", "")
        bullets = sc.get("bullets", [])
        title = sc.get("title", "")

        # Extract factual statements from narration
        sentences = re.split(r'[.!?]\s+', narr)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 20 or re.match(r'^(Welcome|Let\'s|In this|This chapter)', sent):
                continue
            # Look for definitional or factual sentences
            if any(kw in sent.lower() for kw in ['is ', 'are ', 'means', 'refers to', 'used to', 'shows', 'provides']):
                facts.append((title, sent))

    if len(facts) < 2:
        # Use bullets instead
        for sc in video.scenes:
            for b in sc.get("bullets", []):
                if b:
                    facts.append((sc.get("title", ""), b))

    # Select best 2 facts and create questions
    templates = [
        "Which of the following best describes {concept}?",
        "What is the primary purpose of {concept}?",
        "According to the course material, which statement about {concept} is correct?",
        "Which of the following is true regarding {concept}?",
    ]

    selected_facts = facts[:4]  # take first 4 for 2 questions
    for i, (concept, detail) in enumerate(selected_facts[:2]):
        q_idx = start_q_idx + i
        template = templates[i % len(templates)]
        q_text = template.format(concept=concept if concept else video.title)

        # Correct option: truncate detail to reasonable length, clean newlines
        correct = clean_text(detail.split(",")[0].strip() if len(detail) > 60 else detail)
        if len(correct) > 80:
            words = correct.split()[:15]
            correct = " ".join(words)

        # Generate distractors from other facts
        other_details = [f[1] for f in facts if f[1] != detail]
        distractor_options: list[str] = []
        for od in other_details[:3]:
            d = clean_text(od.split(",")[0].strip() if len(od) > 60 else od)
            if len(d) > 80:
                d = " ".join(d.split()[:15])
            distractor_options.append(d)

        # Pad with generic options if needed
        generics = [
            "This topic is not covered in the course material",
            "It depends on the specific project requirements",
            "This applies only to interstate highways",
        ]
        while len(distractor_options) < 3:
            distractor_options.append(generics[len(distractor_options)])

        options = [
            {"text": correct, "correct": True, "generated_distractor": False},
        ]
        for d in distractor_options[:3]:
            options.append({"text": d, "correct": False, "generated_distractor": True})

        # Shuffle options deterministically
        random.seed(hash(q_text) % 2**31)
        random.shuffle(options)

        generated.append({
            "question_id": question_id(video.chapter, video.video_num, q_idx),
            "question_text": q_text,
            "question_type": "mcq",
            "options": options,
            "answer_source": "generated_from_narration",
            "confidence": 0.7,
            "reasoning": f"Generated from narration content for {video.title}",
            "source_excerpt": detail[:200],
            "page": video.source_pages,
            "generated": True,
            "auto_ready": False,
        })

    return generated


def build_mcq_from_question(
    q: ParsedQuestion, q_idx: int, vid: VideoInfo,
    chapter_terms: list[str]
) -> dict:
    """Convert a parsed question into MCQ format."""
    qid = question_id(q.chapter, vid.video_num, q_idx)
    base = {
        "question_id": qid,
        "question_text": q.text,
        "question_type": "mcq",
        "source_excerpt": q.text[:200],
        "page": vid.source_pages,
        "generated": False,
    }

    if q.q_type == "true_false":
        # True/False question -- answer is the correct boolean
        answer_lower = q.answer.lower().strip()
        # Some answers have explanation after: "false, dashed"
        is_false = answer_lower.startswith("false")
        is_true = answer_lower.startswith("true")

        correct_text = "False" if is_false else "True"
        explanation = ""
        if "," in q.answer:
            explanation = q.answer.split(",", 1)[1].strip()

        options = [
            {"text": "True", "correct": correct_text == "True", "generated_distractor": False},
            {"text": "False", "correct": correct_text == "False", "generated_distractor": False},
        ]
        reasoning = f"True/False from PDF Q{q.chapter}-{q.q_num}"
        if explanation:
            reasoning += f". Explanation: {explanation}"

        base.update({
            "options": options,
            "answer_source": "pdf_explicit",
            "confidence": 1.0,
            "reasoning": reasoning,
            "auto_ready": True,
        })

    elif q.q_type == "binary_choice":
        # Binary choice: extract the two options
        choices = extract_binary_choices(q.text)
        if choices and q.answer:
            answer_lower = q.answer.lower().strip()
            # For answers with explanation after comma (e.g., "false, approximate location"),
            # use only the part before the comma for matching.
            answer_match = answer_lower.split(",")[0].strip()

            # Sort choices by length descending so "is not" is checked before "is"
            # to avoid substring false positives.
            sorted_choices = sorted(choices, key=lambda c: len(c), reverse=True)

            # Find which choice matches the answer
            correct_choice: str | None = None
            for c in sorted_choices:
                cl = c.lower().strip()
                if cl == answer_match or answer_match == cl:
                    correct_choice = c
                    break
            if correct_choice is None:
                # Fallback: check if the answer contains a choice (longest first)
                for c in sorted_choices:
                    cl = c.lower().strip()
                    if cl in answer_match or answer_match in cl:
                        correct_choice = c
                        break
            if correct_choice is None:
                correct_choice = choices[0]  # last resort

            options = []
            for c in choices:
                options.append({
                    "text": c,
                    "correct": c == correct_choice,
                    "generated_distractor": False,
                })

            base.update({
                "options": options,
                "answer_source": "pdf_explicit",
                "confidence": 1.0,
                "reasoning": f"Binary choice from PDF Q{q.chapter}-{q.q_num}. Answer: {q.answer}",
                "auto_ready": True,
            })
        else:
            # Couldn't parse binary choice -- treat as open
            base.update(_build_open_mcq(q, chapter_terms))

    elif q.q_type == "fill_blank" or q.q_type == "open":
        base.update(_build_open_mcq(q, chapter_terms))

    elif q.q_type == "matching":
        # Matching questions are complex; represent as a single MCQ
        base.update({
            "options": [
                {"text": q.answer if q.answer else "See answer key", "correct": True, "generated_distractor": False},
                {"text": "None of the options match correctly", "correct": False, "generated_distractor": True},
                {"text": "The matching order is reversed", "correct": False, "generated_distractor": True},
                {"text": "Only some columns can be matched", "correct": False, "generated_distractor": True},
            ],
            "answer_source": "pdf_explicit",
            "confidence": 0.75,
            "reasoning": f"Matching question from PDF Q{q.chapter}-{q.q_num}. Converted to MCQ.",
            "generated_distractors": True,
            "auto_ready": False,
        })

    else:
        base.update(_build_open_mcq(q, chapter_terms))

    return base


def _build_open_mcq(q: ParsedQuestion, chapter_terms: list[str]) -> dict:
    """Build MCQ for fill-in-blank or open-ended question with known answer."""
    if not q.answer:
        return {
            "options": [
                {"text": "Answer not available", "correct": True, "generated_distractor": False},
                {"text": "Not specified", "correct": False, "generated_distractor": True},
                {"text": "Cannot be determined", "correct": False, "generated_distractor": True},
                {"text": "None of the above", "correct": False, "generated_distractor": True},
            ],
            "answer_source": "pdf_explicit",
            "confidence": 0.5,
            "reasoning": f"Open question from PDF Q{q.chapter}-{q.q_num} -- answer not parsed",
            "generated_distractors": True,
            "auto_ready": False,
        }

    correct = q.answer.strip()
    distractors = generate_distractors(correct, chapter_terms, q.text, 3)

    options = [
        {"text": correct, "correct": True, "generated_distractor": False},
    ]
    for d in distractors:
        options.append({"text": d, "correct": False, "generated_distractor": True})

    # Shuffle deterministically
    random.seed(hash(q.text) % 2**31)
    random.shuffle(options)

    return {
        "options": options,
        "answer_source": "pdf_with_generated_distractors",
        "confidence": 0.85,
        "reasoning": f"From PDF Q{q.chapter}-{q.q_num}. Correct answer: {correct}. Distractors generated from chapter content.",
        "generated_distractors": True,
        "auto_ready": True,  # will be re-evaluated in step 7
    }


def step5_build_quizzes(
    video_questions: dict[tuple[int, int], list[ParsedQuestion]],
    videos: list[VideoInfo],
) -> dict[str, dict]:
    """Build quiz data for each video."""
    print("\n" + "=" * 60)
    print("STEP 5 -- BUILD QUIZ JSONs")
    print("=" * 60)

    # Pre-compute chapter terms for distractor generation
    chapter_terms_cache: dict[int, list[str]] = {}
    for ch in CHAPTERS:
        chapter_terms_cache[ch] = get_chapter_terms(videos, ch)

    quiz_outputs: dict[str, dict] = {}  # dir_name -> {"extracted_raw": ..., "import_ready": ...}

    for v in videos:
        key = (v.chapter, v.video_num)
        qs = video_questions.get(key, [])
        dir_name = video_dir_name(v.chapter, v.video_num)
        terms = chapter_terms_cache.get(v.chapter, [])

        extracted_raw: list[dict] = []
        import_ready_items: list[dict] = []

        if qs:
            # Process PDF questions
            for q_idx, q in enumerate(qs, start=1):
                # Raw extraction
                raw_entry = {
                    "question_id": question_id(v.chapter, v.video_num, q_idx),
                    "chapter": q.chapter,
                    "question_number": f"{q.chapter}-{q.q_num}",
                    "question_text": q.text,
                    "answer_text": q.answer,
                    "question_type": q.q_type,
                    "line_in_markdown": q.line_num,
                    "ambiguous": q.ambiguous,
                }
                extracted_raw.append(raw_entry)

                # Build MCQ
                mcq = build_mcq_from_question(q, q_idx, v, terms)
                import_ready_items.append(mcq)
        else:
            # No PDF questions for this video -- generate 2
            generated = generate_questions_from_narration(v, start_q_idx=1)
            for g in generated:
                import_ready_items.append(g)
                extracted_raw.append({
                    "question_id": g["question_id"],
                    "chapter": v.chapter,
                    "question_number": "generated",
                    "question_text": g["question_text"],
                    "answer_text": next((o["text"] for o in g["options"] if o["correct"]), ""),
                    "question_type": "generated",
                    "line_in_markdown": None,
                    "ambiguous": False,
                })

        quiz_outputs[dir_name] = {
            "extracted_raw": {
                "chapter": v.chapter,
                "video": v.video_num,
                "title": v.title,
                "source_pages": v.source_pages,
                "questions": extracted_raw,
                "generated_at": NOW_ISO,
            },
            "import_ready": {
                "chapter": v.chapter,
                "video": v.video_num,
                "title": v.title,
                "source_pages": v.source_pages,
                "questions": import_ready_items,
                "generated_at": NOW_ISO,
            },
        }

        pdf_count = sum(1 for q in import_ready_items if not q.get("generated", False))
        gen_count = sum(1 for q in import_ready_items if q.get("generated", False))
        print(f"  {dir_name}: {pdf_count} PDF questions, {gen_count} generated")

    return quiz_outputs


# --- STEP 6: sanitization ----------------------------------------------------

# Sanitization rules: replace station numbers, project IDs, etc.
SANITIZATION_RULES = [
    # Station numbers like 192+50 -> "station one-ninety-two plus fifty"
    (re.compile(r'\b(\d{1,3})\+(\d{2})\b'), r'Station \1+\2'),
    # Project ID patterns
    (re.compile(r'STP-IM-\d+-\d+\(\d+\)'), 'the project number'),
    (re.compile(r'P\.I\.\s*No\.\s*\d+'), 'the P.I. number'),
    # Sheet references
    (re.compile(r'(?:Construction\s+)?Plan\s+Sheet(?:s)?\s+(?:No\.\s*)?\d+'), 'the referenced plan sheet'),
    # LaTeX math artifacts
    (re.compile(r'\$[^$]+\$'), lambda m: m.group(0).replace('$', '').strip()),
    # Multiple spaces
    (re.compile(r'\s{2,}'), ' '),
]


def sanitize_text(text: str) -> tuple[str, list[dict]]:
    """Apply sanitization rules, return (sanitized_text, list of replacements)."""
    replacements: list[dict] = []
    result = text
    for pattern, replacement in SANITIZATION_RULES:
        matches = list(pattern.finditer(result))
        if matches:
            for m in matches:
                replacements.append({
                    "original": m.group(0),
                    "replacement": pattern.sub(replacement, m.group(0)) if isinstance(replacement, str)
                                   else replacement(m),
                    "rule": pattern.pattern,
                })
            result = pattern.sub(replacement, result)
    return result, replacements


def step6_sanitization(
    quiz_outputs: dict[str, dict],
) -> dict[int, dict]:
    """Apply sanitization to question/option text in import_ready, keep raw in extracted_raw."""
    print("\n" + "=" * 60)
    print("STEP 6 -- SANITIZATION")
    print("=" * 60)

    sanitization_maps: dict[int, dict] = {}

    for dir_name, data in quiz_outputs.items():
        ch = data["import_ready"]["chapter"]
        if ch not in sanitization_maps:
            sanitization_maps[ch] = {
                "chapter": ch,
                "replacements": [],
                "generated_at": NOW_ISO,
            }

        for q in data["import_ready"]["questions"]:
            # Sanitize question text
            sanitized_q, q_repls = sanitize_text(q["question_text"])
            q["question_text_sanitized"] = sanitized_q
            sanitization_maps[ch]["replacements"].extend(q_repls)

            # Sanitize option text
            for opt in q.get("options", []):
                sanitized_o, o_repls = sanitize_text(opt["text"])
                opt["text_sanitized"] = sanitized_o
                sanitization_maps[ch]["replacements"].extend(o_repls)

    total_repls = sum(len(m["replacements"]) for m in sanitization_maps.values())
    print(f"  Applied sanitization across {len(sanitization_maps)} chapters, {total_repls} total replacements")
    return sanitization_maps


# --- STEP 7: confidence & review gating --------------------------------------

def step7_review_gating(
    quiz_outputs: dict[str, dict],
) -> dict[int, list[dict]]:
    """Flag low-confidence questions for review."""
    print("\n" + "=" * 60)
    print("STEP 7 -- CONFIDENCE & REVIEW GATING")
    print("=" * 60)

    review_items: dict[int, list[dict]] = defaultdict(list)

    for dir_name, data in quiz_outputs.items():
        ch = data["import_ready"]["chapter"]
        for q in data["import_ready"]["questions"]:
            confidence = q.get("confidence", 0.0)
            if confidence < 0.8:
                q["auto_ready"] = False
                review_items[ch].append({
                    "question_id": q["question_id"],
                    "question_text": q["question_text"][:100],
                    "confidence": confidence,
                    "reason": q.get("reasoning", "Low confidence"),
                    "source_excerpt": q.get("source_excerpt", "")[:100],
                })
            else:
                q["auto_ready"] = True

    total_flagged = sum(len(items) for items in review_items.values())
    total_auto = sum(
        sum(1 for q in d["import_ready"]["questions"] if q.get("auto_ready", False))
        for d in quiz_outputs.values()
    )
    print(f"  Auto-ready: {total_auto}")
    print(f"  Flagged for review: {total_flagged}")
    for ch in sorted(review_items):
        print(f"    Ch{ch:02d}: {len(review_items[ch])} items for review")

    return review_items


# --- STEP 8: write outputs ---------------------------------------------------

def step8_write_outputs(
    content_outputs: dict[str, Any],
    quiz_outputs: dict[str, dict],
    sanitization_maps: dict[int, dict],
    review_items: dict[int, list[dict]],
    videos: list[VideoInfo],
) -> dict:
    """Write all output files and return summary."""
    print("\n" + "=" * 60)
    print("STEP 8 -- WRITE ALL OUTPUTS")
    print("=" * 60)

    files_created: list[str] = []

    # Course content JSONs
    for dir_name, content in content_outputs.items():
        path = COURSE_CONTENT_ROOT / dir_name / "content.json"
        write_json(path, content)
        files_created.append(str(path.relative_to(ROOT)))

    # Quiz JSONs
    for dir_name, data in quiz_outputs.items():
        raw_path = QUIZZES_ROOT / dir_name / "extracted_raw.json"
        write_json(raw_path, data["extracted_raw"])
        files_created.append(str(raw_path.relative_to(ROOT)))

        ready_path = QUIZZES_ROOT / dir_name / "import_ready.json"
        write_json(ready_path, data["import_ready"])
        files_created.append(str(ready_path.relative_to(ROOT)))

    # Sanitization maps
    for ch, smap in sanitization_maps.items():
        path = SANITIZATION_ROOT / f"sanitization_map_chapter{ch:02d}.json"
        write_json(path, smap)
        files_created.append(str(path.relative_to(ROOT)))

    # Logs
    for ch in CHAPTERS:
        log_lines = [
            f"Extraction log for Chapter {ch}",
            f"Generated at: {NOW_ISO}",
            f"---",
        ]
        ch_videos = [v for v in videos if v.chapter == ch]
        for v in ch_videos:
            dir_name = video_dir_name(v.chapter, v.video_num)
            q_data = quiz_outputs.get(dir_name, {})
            q_count = len(q_data.get("import_ready", {}).get("questions", []))
            log_lines.append(f"Video {v.video_num}: \"{v.title}\" -- scenes {v.scene_indices}, {q_count} questions")

        path = LOGS_ROOT / f"extraction_chapter{ch:02d}.log"
        write_log(path, log_lines)
        files_created.append(str(path.relative_to(ROOT)))

    # Review CSVs
    review_fieldnames = ["question_id", "question_text", "confidence", "reason", "source_excerpt"]
    for ch, items in review_items.items():
        if items:
            path = REVIEW_ROOT / f"review_chapter{ch:02d}.csv"
            write_csv(path, items, review_fieldnames)
            files_created.append(str(path.relative_to(ROOT)))

    print(f"  Created {len(files_created)} files")

    # Compute summary statistics
    total_pdf_qs = 0
    total_gen_qs = 0
    total_auto_ready = 0
    total_flagged = 0

    for data in quiz_outputs.values():
        for q in data["import_ready"]["questions"]:
            if q.get("generated", False):
                total_gen_qs += 1
            else:
                total_pdf_qs += 1
            if q.get("auto_ready", False):
                total_auto_ready += 1
            else:
                total_flagged += 1

    summary = {
        "generated_at": NOW_ISO,
        "chapters_processed": CHAPTERS,
        "videos_processed": len(videos),
        "questions_found_pdf": total_pdf_qs,
        "questions_generated": total_gen_qs,
        "questions_auto_ready": total_auto_ready,
        "questions_flagged_for_review": total_flagged,
        "files_created": len(files_created),
        "file_paths": files_created,
    }

    return summary


# --- main ---------------------------------------------------------------------

def main():
    global CHAPTERS, CHAPTERS_SET

    parser = argparse.ArgumentParser(description="Course Content & Quiz Generator")
    parser.add_argument("--chapters", type=str, default="5-15",
                        help="Chapter range, e.g. '1-4' or '5-15' or '1-15' (default: 5-15)")
    args = parser.parse_args()

    CHAPTERS = parse_chapter_range(args.chapters)
    CHAPTERS_SET = set(CHAPTERS)

    label = f"{CHAPTERS[0]}--{CHAPTERS[-1]}" if len(CHAPTERS) > 1 else str(CHAPTERS[0])
    print("=" * 60)
    print(f"COURSE CONTENT & QUIZ GENERATOR -- Chapters {label}")
    print(f"Run at: {NOW_ISO}")
    print("=" * 60)

    # Step 0
    if not step0_feasibility():
        sys.exit(1)

    # Step 1
    manifests, videos = step1_load_manifests()

    # Step 2
    questions = step2_parse_markdown()

    # Step 3
    video_questions = step3_map_questions_to_videos(questions, videos, manifests)

    # Step 4
    content_outputs = step4_generate_course_content(videos)

    # Step 5
    quiz_outputs = step5_build_quizzes(video_questions, videos)

    # Step 6
    sanitization_maps = step6_sanitization(quiz_outputs)

    # Step 7
    review_items = step7_review_gating(quiz_outputs)

    # Step 8
    summary = step8_write_outputs(content_outputs, quiz_outputs, sanitization_maps, review_items, videos)

    # Final output
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(pretty_json(summary))

    return summary


if __name__ == "__main__":
    main()
