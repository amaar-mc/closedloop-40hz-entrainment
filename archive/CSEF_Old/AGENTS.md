# Repository Guidelines

## Project Structure & Module Organization
This repository stores CSEF deliverables rather than the underlying training code. `Research Paper/` is the technical source of truth: `RESEARCH_PAPER_v3.tex` is the typeset paper, `RESEARCH_PAPER_v3.md` is the prose version, `RESULTS_REPORT.md` and `SUPPLEMENTARY.md` capture supporting analysis, and `Figures/` holds the paper figures. `Presentation/` is organized by speaking workflow: `01_main_script.md` is the canonical 4-5 minute script, `02_*` and `03_*` are shortened and memorization variants, and `04_*`, `05_*`, and `JUDGE_INTERVIEW_PREP.md` cover Q&A prep. `Poster/`, `Abstract/`, `Flyer/`, and `Lab Notebook/` each combine editable Markdown with exported PDF or DOCX artifacts. `Forms/` and `Early Research/` are submission/reference archives and should only change when the official paperwork or background source changes.

## Source-of-Truth Workflow
Edit Markdown or LaTeX sources first, then regenerate the exported PDF/DOCX artifact manually; no build system is checked in here. Keep shared scientific claims synchronized across all outward-facing materials. The same core numbers and framing recur in the paper, abstract, poster, flyer, notebook, and presentation scripts, so a metric change in one file usually requires coordinated edits in several folders. When revising visuals, update both the figure asset in `Research Paper/Figures/` and every narrative reference that explains that figure.

## Writing & Naming Conventions
Follow the naming scheme already used in the repo: versioned deliverables use explicit suffixes such as `v3`, `V5`, and `VFINAL`, and presentation files use numeric prefixes to preserve delivery order. Keep the existing house style of Markdown headings, bold metadata labels, and bullet-heavy method/result summaries. Preserve fair-specific constraints already documented in `Poster/POSTER_BOARD_V5.md`, including the compliance checklist, board dimensions, font minimums, and AI-disclosure requirements.

## Validation
There is no package manager, formatter, test harness, or Git history in this checkout. Validate edits by checking that every referenced asset still exists, exported artifacts still match their editable sources, and repeated statistics remain identical across public-facing documents. If you touch flyer content, verify the paired QR assets in `Flyer/`; if you touch paper figures, verify the corresponding files in `Research Paper/Figures/`.
