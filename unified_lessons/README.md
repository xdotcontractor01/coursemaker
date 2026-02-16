# Unified Lesson JSON Files

## Overview

This directory contains unified lesson JSON files that merge course content and quiz data for each lesson in the course. Each file represents one lesson and contains:

- Lesson metadata (chapter, video, title)
- Course content (summary bullets and markdown)
- All quiz questions for that lesson

## File Structure

**Total Files:** 25 unified lesson JSON files  
**Total Quiz Questions:** 163 questions across all lessons

### Files by Chapter

- **Chapter 01:** 4 lessons (video01-04)
- **Chapter 02:** 1 lesson (video01)
- **Chapter 03:** 1 lesson (video01)
- **Chapter 04:** 1 lesson (video01)
- **Chapter 05:** 1 lesson (video01)
- **Chapter 06:** 2 lessons (video01-02)
- **Chapter 07:** 3 lessons (video01-03)
- **Chapter 08:** 3 lessons (video01-03)
- **Chapter 09:** 1 lesson (video01)
- **Chapter 10:** 1 lesson (video01)
- **Chapter 11:** 1 lesson (video01)
- **Chapter 12:** 1 lesson (video01)
- **Chapter 13:** 2 lessons (video01-02)
- **Chapter 14:** 1 lesson (video01)
- **Chapter 15:** 2 lessons (video01-02)

## JSON Schema

Each unified lesson JSON file follows this strict schema:

```json
{
  "chapter": <number>,
  "video": <number>,
  "title": <string>,
  "summary_bullets": <array of strings>,
  "summary_markdown": <string>,
  "video_url": <string|null>,
  "duration_seconds": <number|null>,
  "source_pages": <string|null>,
  "content_source": <string|null>,
  "generated_at": <ISO-8601 timestamp>,
  "quizzes": [
    {
      "question_id": <string>,
      "chapter": <number>,
      "video": <number>,
      "question_text": <string>,
      "options": [
        {
          "text": <string>,
          "generated_distractor": <boolean>
        }
      ],
      "correct_option": <number|null>,
      "explanation": <string>,
      "source_excerpt": <string|null>,
      "confidence": <number>,
      "auto_ready": <boolean>
    }
  ]
}
```

## Field Descriptions

### Lesson Metadata
- `chapter`: Chapter number (integer)
- `video`: Video number within the chapter (integer)
- `title`: Lesson title
- `source_pages`: Page range from source material (e.g., "1-2", "91-94")
- `content_source`: URL to the source PDF document ([BasicHiwyPlanReading.pdf](https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view))
- `generated_at`: ISO-8601 timestamp when content was generated

### Course Content
- `summary_bullets`: Array of key points for the lesson
- `summary_markdown`: Markdown-formatted summary (bullets joined with newlines)
- `video_url`: URL to video file (typically null - backend handles video separately)
- `duration_seconds`: Video duration in seconds (may be null)

### Quiz Questions
- `question_id`: Unique identifier (e.g., "ch01_vid01_q01")
- `question_text`: The question text
- `options`: Array of answer options
  - `text`: Option text
  - `generated_distractor`: Whether this is an AI-generated incorrect option
- `correct_option`: Index of correct option (0-based), may be null
- `explanation`: Explanation of the correct answer
- `source_excerpt`: Relevant excerpt from source material (may be null)
- `confidence`: Confidence score (0.0-1.0)
- `auto_ready`: Whether the question is ready for auto-import

## Source Data

These unified files were created by merging:

1. **Course Content:** `manifests/course_content/ChapterXX_videoYY/content.json`
2. **Quiz Data:** `quizzes/ChapterXX_videoYY/import_ready.json`

No content was regenerated or modified - this is a deterministic merge only.

## Generation Details

**Script:** `scripts/utilities/build_unified_lessons.py`  
**Build Date:** 2026-02-15  
**Build Status:** ✓ All 25 lessons processed successfully  
**Errors:** 0

## Usage

These unified JSON files are designed for:
- Backend ingestion into the learning management system
- Serving lesson content and quizzes via API
- Frontend display of lesson summaries and assessments
- Analytics and reporting on lesson structure

### Content Source Reference

All lessons reference the source material:
- **Document:** Basic Highway Plan Reading
- **URL:** [BasicHiwyPlanReading.pdf](https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view)
- **Page Numbers:** Stored in `source_pages` field (e.g., "1-2", "91-94")

**Frontend Display Recommendation:**  
Display the content source as a hyperlinked reference at the bottom of each lesson with the format:  
`"Source: [Basic Highway Plan Reading](https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view) (Pages: {source_pages})"`

**Example:** Source: [Basic Highway Plan Reading](https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view) (Pages: 1-2)

## Validation

All files have been validated to ensure:
- ✓ Non-empty summary_bullets
- ✓ Valid summary_markdown derived from bullets
- ✓ quizzes is an array (empty allowed)
- ✓ chapter/video numbers match folder naming
- ✓ All quiz questions have matching chapter/video numbers

## Logs

Build logs available at:
- **Summary:** `logs/unified_builder_summary.json`
- **Errors:** `logs/unified_builder_errors.log` (empty - no errors)

---

**Generated by:** Unified Lesson Builder  
**Last Updated:** 2026-02-15
