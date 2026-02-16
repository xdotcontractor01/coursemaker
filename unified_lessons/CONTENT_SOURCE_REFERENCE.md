# Content Source Reference

All unified lesson files reference the source PDF document with specific page ranges.

## Source Document

**Title:** Basic Highway Plan Reading  
**URL:** [BasicHiwyPlanReading.pdf](https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view)  
**Format:** PDF Document (Google Drive)

---

## Lesson Page References

| Lesson File | Chapter | Video | Title | Pages |
|-------------|---------|-------|-------|-------|
| Chapter01_video01.json | 1 | 1 | Requirements and Contract Documents | 1-2 |
| Chapter01_video02.json | 1 | 2 | Plan Organization | 2-4 |
| Chapter01_video03.json | 1 | 3 | Sheet Layout and Drawing Conventions | 5-8 |
| Chapter01_video04.json | 1 | 4 | Scales and Measurement | 8-11 |
| Chapter02_video01.json | 2 | 1 | Stationing and Centerline | 11-12 |
| Chapter03_video01.json | 3 | 1 | Vertical Alignment and Profile | 13-14 |
| Chapter04_video01.json | 4 | 1 | Cross Sections and Typical Sections | 15-17 |
| Chapter05_video01.json | 5 | 1 | Earthwork and Grading | 19-21 |
| Chapter06_video01.json | 6 | 1 | Roadway Design Elements | 23-27 |
| Chapter06_video02.json | 6 | 2 | Superelevation and Transitions | 28-36 |
| Chapter07_video01.json | 7 | 1 | Drainage Concepts | 37-41 |
| Chapter07_video02.json | 7 | 2 | Storm Drainage Systems | 41-47 |
| Chapter07_video03.json | 7 | 3 | Culverts and Inlets | 47-50 |
| Chapter08_video01.json | 8 | 1 | Bridge Plans Overview | 53-55 |
| Chapter08_video02.json | 8 | 2 | Box Culverts and Wing Walls | 56-59 |
| Chapter08_video03.json | 8 | 3 | Bridge Details and Specifications | 60-65 |
| Chapter09_video01.json | 9 | 1 | Traffic Control Plans | 67-68 |
| Chapter10_video01.json | 10 | 1 | Utilities and Relocations | 69-70 |
| Chapter11_video01.json | 11 | 1 | Erosion Control and Sediment Management | 71-72 |
| Chapter12_video01.json | 12 | 1 | Pavement Marking and Signage | 73-76 |
| Chapter13_video01.json | 13 | 1 | Construction Sequence | 77-79 |
| Chapter13_video02.json | 13 | 2 | Phasing and Traffic Maintenance | 80-84 |
| Chapter14_video01.json | 14 | 1 | Quantities and Cost Estimation | 85-86 |
| Chapter15_video01.json | 15 | 1 | Right of Way Plans | 87-91 |
| Chapter15_video02.json | 15 | 2 | Plan Sheets and Symbols | 91-94 |

---

## JSON Structure

Each unified lesson JSON file contains:

```json
{
  "chapter": <number>,
  "video": <number>,
  "title": "<string>",
  "source_pages": "<page range>",
  "content_source": "https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view",
  ...
}
```

---

## Frontend Display Recommendation

When displaying lesson content, include a reference link at the bottom:

**Format:**
```
Source: [Basic Highway Plan Reading](https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view) (Pages: {source_pages})
```

**Example for Chapter 1, Video 1:**
```
Source: [Basic Highway Plan Reading](https://drive.google.com/file/d/1RX1xGE3GvK6z2d_u-hGAiPF1i7EGEDgq/view) (Pages: 1-2)
```

**Implementation:**
```javascript
const sourceLink = `Source: [Basic Highway Plan Reading](${lesson.content_source}) (Pages: ${lesson.source_pages})`;
```

---

## Coverage Summary

- **Total Lessons:** 25
- **Total Chapters:** 15
- **Source Pages Covered:** Pages 1-94 (with some gaps)
- **All Lessons Include:** 
  - Valid content_source URL
  - Specific page range references
  - Direct link to source material

---

**Last Updated:** 2026-02-15  
**Content Source Added:** All 25 lesson files updated
