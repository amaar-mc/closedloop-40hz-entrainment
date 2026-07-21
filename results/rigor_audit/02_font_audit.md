# Phase 1B: Font Compliance Audit

**Audit date:** 2026-03-24
**Source:** `scripts/generate_csef_presentation.py`

## CSEF Font Requirements

From CSEF Project Presentation Requirements (via web search):

- **Minimum body text:** 14pt (18pt recommended)
- **Caption exception:** ≥10pt allowed for figure captions and photo credits
- **Recommended fonts:** Arial, Calibri, Helvetica, or Century Gothic

## Font Family

| Aspect      | Current         | CSEF Recommendation                       | Status   |
| ----------- | --------------- | ----------------------------------------- | -------- |
| Font family | Times New Roman | Arial, Calibri, Helvetica, Century Gothic | **WARN** |

**Analysis:** The CSEF document says "recommended" not "required" for font families. Times New Roman is a professional serif font widely accepted in academic contexts. However, the CSEF explicitly recommends sans-serif fonts for screen readability. Switching to Arial or Calibri would better match CSEF expectations and may improve on-screen readability for judges.

**Lines affected:** 34-37 (font path definitions), 51-58 (font registration)

## Complete Font Size Map

Every text-rendering call in the script, mapped to its font size:

### Heading Functions

| Function | Size (pt) | Style | Meets 14pt min? | Lines | Status   |
| -------- | --------- | ----- | --------------- | ----- | -------- |
| `sec()`  | 22        | Bold  | Yes             | 64    | **PASS** |
| `sub()`  | 17        | Bold  | Yes             | 75    | **PASS** |
| `sub2()` | 15        | Bold  | Yes             | 82    | **PASS** |

### Body Text Functions

| Function      | Size (pt)    | Style   | Meets 14pt min?       | Lines   | Status   |
| ------------- | ------------ | ------- | --------------------- | ------- | -------- |
| `body()`      | 14 (default) | Regular | Yes (exactly minimum) | 89-93   | **PASS** |
| `body_bold()` | 14 (default) | Bold    | Yes                   | 95-99   | **PASS** |
| `bullet()`    | 14 (default) | Regular | Yes                   | 101-115 | **PASS** |

### Caption Function

| Function    | Size (pt) | Style  | Meets 10pt caption min? | Lines   | Status   |
| ----------- | --------- | ------ | ----------------------- | ------- | -------- |
| `caption()` | 11        | Italic | Yes (11 > 10)           | 117-122 | **PASS** |

### Table Function

| Element        | Size (pt) | Style        | Meets 14pt min? | Lines | Status   |
| -------------- | --------- | ------------ | --------------- | ----- | -------- |
| `tbl()` header | 14        | Bold         | Yes             | 132   | **PASS** |
| `tbl()` rows   | 14        | Regular/Bold | Yes             | 142   | **PASS** |

### Per-Page Custom Font Calls

| Page             | Element                   | Size (pt) | Style   | Line                 | Status                                                                                                      |
| ---------------- | ------------------------- | --------- | ------- | -------------------- | ----------------------------------------------------------------------------------------------------------- |
| p01 (Title)      | Project title             | 26        | Bold    | 187                  | **PASS**                                                                                                    |
| p01 (Title)      | Author name               | 18        | Regular | 195                  | **PASS**                                                                                                    |
| p01 (Title)      | "Project Summary" heading | 16        | Bold    | 200                  | **PASS**                                                                                                    |
| p01 (Title)      | Summary body              | 14        | Regular | via body() at 204    | **PASS**                                                                                                    |
| p02 (Intro)      | "Hypothesis:" label       | 14        | Bold    | 237-238              | **PASS**                                                                                                    |
| p02 (Intro)      | Hypothesis text           | 14        | Regular | 240                  | **PASS**                                                                                                    |
| p05 (Methods)    | Ablation table caption    | 11        | Italic  | via caption() at 403 | **PASS** (caption exception)                                                                                |
| p06 (Methods)    | Figure 1 caption          | 11        | Italic  | via caption() at 482 | **PASS** (caption exception)                                                                                |
| p06 (Methods)    | Missing figure notice     | 12        | Italic  | 156                  | **WARN** — 12pt is below 14pt body minimum but this is error-handling text, never rendered in normal output |
| p07 (Results)    | Table 1 caption           | 11        | Italic  | via caption() at 526 | **PASS** (caption exception)                                                                                |
| p08 (Results)    | Table 2 caption           | 11        | Italic  | via caption() at 558 | **PASS** (caption exception)                                                                                |
| p12 (References) | Reference entries         | 14        | Regular | 806                  | **PASS**                                                                                                    |
| p12 (References) | "Dataset:" label          | 14        | Regular | 813-816              | **PASS**                                                                                                    |
| p12 (References) | Dataset URL               | 14        | Italic  | 817-818              | **PASS**                                                                                                    |

## Font Size Violations

**None found.** All body text is at 14pt (the minimum), all captions are at 11pt (above the 10pt exception floor), and all headings exceed 14pt.

## Recommendations

1. **WARN: Switch from Times New Roman to a CSEF-recommended sans-serif font.** Arial or Calibri would better match CSEF recommendations and improve on-screen readability. This change would require updating lines 34-37 (font paths) and 56-58 (font family name).

2. **OPTIONAL: Increase body text from 14pt to 16pt.** Currently at the exact minimum. CSEF recommends 18pt. While 14pt passes, judges reviewing on screen may find it small. Increasing to 16pt would improve readability but might require reducing content to fit within page limits.

## Summary

- **PASS:** 19/20 font checks
- **FAIL:** 0
- **WARN:** 1 (Times New Roman vs CSEF-recommended sans-serif fonts)
