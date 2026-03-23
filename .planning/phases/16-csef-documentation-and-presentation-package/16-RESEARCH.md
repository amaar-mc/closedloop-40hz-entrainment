# Phase 16: CSEF Documentation and Presentation Package - Research

**Researched:** 2026-03-22
**Domain:** Science fair documentation — written materials, presentation scripts, poster, lab notebook, research paper, PDF generation
**Confidence:** HIGH

## Summary

Phase 16 is a documentation-only phase. There is no new code, no new model training, no new experiments. The task is to update every CSEF submission artifact to reflect the v3.0 breakthrough — specifically the PAC+Stim feature discovery (dropping 61 spectral features raises R² from 0.12 to 0.60 at 7ch, 0.43 at 4ch), the audiovisual stimulation in the live Muse 2 demo, the caregiver app productization narrative, and the live HF Spaces deployment.

The existing materials are in two parallel directory trees: `docs/` (working source) and `CSEF/` (submission-ready copies). Both must stay in sync. The presentation PDF and poster PDFs are generated from Markdown source and require LaTeX/Pandoc or equivalent. The judging deadline is 2026-04-09, giving roughly 18 days from research date.

The core challenge is not writing — it is surgical accuracy. Every number, claim, and architectural detail in every document must trace to an actual source file. The project has a known history of numbers drifting across versions; the V5 poster changelog documents 14 factual corrections from prior versions. The planner must treat numerical claims as code: write the source file reference next to the number.

**Primary recommendation:** Work document-by-document with a strict audit step after each one — write, then verify every number against its source JSON/markdown before moving to the next document.

---

## What Actually Changed in v3.0 (The Things That Must Propagate)

This is the source-of-truth diff between what the existing CSEF materials say and what v3.0 proved. Every document must be updated to reflect these findings.

### Finding 1: PAC+Stim Feature Discovery — The Headline Breakthrough

**Source:** `experimental/FINDINGS.md`, `experimental/results/pac_stim_focused.json`

The previous best TCN used 73 features (61 spectral + 7 PAC-derived + 5 stim context). The spectral features encode subject-specific EEG anatomy that does not generalize across subjects, producing a catastrophic val-test gap (val R² 0.333, test R² −0.025).

Dropping spectral features and using only the 12 PAC+stim context features:

| Configuration | Previous (73 features) | New (12 features) | Source |
|---|---|---|---|
| 7ch test R² | 0.121 | 0.606 ± 0.032 (5-seed mean) | `experimental/FINDINGS.md` |
| 4ch test R² | 0.112 | 0.430 | `experimental/FINDINGS.md` |
| Val-test gap (7ch) | 0.358 | 0.246 | `experimental/FINDINGS.md` |

The 12 features: pac_current, pac_ma2, pac_ma4, pac_ma8, pac_ma16, pac_diff1, pac_diff4, stim_state, time_since_switch_60s, stim_frac_20s, cycle_phase_sin, cycle_phase_cos.

The existing CSEF presentation (PDF, slides), poster V5, paper v3, and all scripts still reference the 73-feature model. This is the primary content gap.

**What the existing presentation says about features:** "73 features (61 spectral + 7 PAC-derived + 5 stim context)." This needs to become "12 features (7 PAC-derived + 5 stim context)."

**What the existing presentation says about TCN R²:** "R² ≈ 0.25 at 5-10s" (from the original 73-feature model). The new number for raw PAC (ts=1) is R² ≈ 0.60 (7ch) / 0.43 (4ch). The horizon sweep R² values in POSTER_BOARD_V5 (0.254, 0.240, 0.278 at 5s/8s/10s) were from the old pipeline — these need to be verified against new experimental results or explicitly labeled as coming from the 73-feature model for context.

### Finding 2: Multi-Seed Robustness

**Source:** `experimental/FINDINGS.md` (multi-seed table)

5 seeds, h=64 TCN, pac_stim features, 7ch, ts=1:
- Mean test R² = 0.606 ± 0.032
- Range: 0.558–0.647

This is the reproducibility claim for CSEF. Should appear in the paper and poster where reproducibility is discussed.

### Finding 3: 4-Channel vs 7-Channel Gap (RSRCH-05 Complete)

**Source:** `results/4ch_vs_7ch_r2_gap_report.md`

| Metric | 7ch | 4ch | Delta |
|---|---|---|---|
| Static PAC (EEGNet) | R² = 0.287 | R² = 0.016 | −0.271 |
| Temporal TCN (12 feat, 5s) | R² = 0.606 | R² = 0.430 | −0.176 |
| Dedicated 4ch TCN (73 feat) | R² = 0.170 | 0.156 | −0.014 |

Key narrative: temporal context (20-second lookback) substantially compensates for spatial coverage loss. The 4ch TCN with 12 features (R² 0.43) vastly outperforms the 73-feature model at both channel configs.

### Finding 4: Live Muse 2 Demo — Audiovisual Stimulation

**Source:** `neurocare_live.py`, `.planning/PROJECT.md`

- `neurocare_live.py`: mission control dashboard with direct PAC computation (Tort 2010 MI), band powers, real-time 40 Hz audio toggle
- `caregiver_app.py`: patient-facing app at https://huggingface.co/spaces/amaarc/neurocare-40hz
- 40 Hz click-train WAV cached with st.cache_data; 3s file looping via HTML audio element
- Muse 2 BLE not viable on Darwin 25.x (BLE not enabled); SimulatedEEGAdapter ships as demo path
- Session-adaptive normalization replaces training z-scores

The existing presentation scripts do not mention the caregiver app or the HF Spaces deployment. The elevator pitch mentions a QR code; the live URL exists and should be referenced.

### Finding 5: Productization Narrative

**Source:** `docs/CLINICAL_ROADMAP.md`, `docs/ELEVATOR_PITCH.md`, `docs/flyer/`

The productization story (3-phase clinical roadmap, facility flyer, pilot feedback form) exists in docs/ but is NOT reflected in the current CSEF presentation script or paper. This is new material to add.

---

## Current State of Each Document (What Exists, What's Stale)

### CSEF Presentation PDF

**File:** `CSEF/Presentation/CSEF_2026_Presentation.pdf` (and `docs/presentations/CSEF_2026_Presentation.pdf`)
**Format:** PDF (generated from LaTeX .tex or Pandoc Markdown)
**Page limit:** 13 pages maximum (CSEF requirement)
**Current page count:** Not verified — needs checking
**Stale elements:**
- Feature count: says "73 features" → needs "12 features (PAC+stim only)"
- TCN test R²: says "5-second prediction horizon; test R² = 0.170 (raw PAC targets)" → needs R² = 0.606 (7ch) / 0.43 (4ch)
- No mention of caregiver app, HF Spaces deployment, live demo
- No productization section

**Generation method:** The existing `.tex` file is at `docs/paper/RESEARCH_PAPER_v3.tex` (research paper). The presentation PDF source is unclear — the CSEF/Presentation/ directory has the PDF but no obvious .tex/.md source. This is a discovery gap: the planner must locate or reconstruct the presentation source.

### Poster Board V5

**File:** `docs/poster/POSTER_BOARD_V5.md` (source) and `CSEF/Poster/POSTER_BOARD_V5.md` (copy) + printed PDFs
**Current version:** V5 — already condensed and audited for numbers from the old pipeline
**Stale elements:**
- Feature description: "73 features: 61 spectral + 7 PAC-derived + 5 stim context" → needs "12 features: 7 PAC-derived + 5 stim context"
- TCN architecture: "5-second prediction horizon; test R² = 0.170" → R² = 0.606
- Horizon sweep figure data (Fig 3): the exact R² values (0.254 at 5s, 0.240 at 8s, 0.278 at 10s) came from the 73-feature pipeline and are now superseded. New values from the 12-feature pipeline may differ.
- Multiseed reproducibility should be added

**Physical constraint:** The poster is already printed as "Synopsys Poster FINAL.pdf" and "Synopsys Poster FINAL EDB.pdf" in CSEF/Poster/. If already submitted and printed for Synopsys, it may only need updating for CSEF (a second fair). The planner needs to determine: is CSEF a separate submission requiring a new print, or is the Synopsys poster being reused?

### Research Paper

**File:** `docs/paper/RESEARCH_PAPER_v3.md` and `CSEF/Research Paper/RESEARCH_PAPER_v3.md` and `.pdf` and `.tex`
**Word count:** ~11,647 words (per PROJECT.md)
**Stale elements:**
- Section on feature engineering: describes 73 features as the design choice
- Results section: TCN R² values from old pipeline
- No ablation section documenting the PAC+Stim discovery
- Multi-seed robustness section may exist but with old numbers
- 4ch vs 7ch gap not yet in paper

**Paper update scope is LARGE.** Sections to update: Abstract, Methods (feature engineering), Results (TCN R² table, horizon sweep discussion, feature ablation), Discussion (generalization interpretation).

### Lab Notebook

**File:** `CSEF/Lab Notebook/P10_Lab_Notebook_VFINAL.md` and `.pdf`
**Timeline:** January 15, 2026 – March 1, 2026
**Stale elements:** Notebook timeline ends at March 1. The PAC+Stim discovery, 4ch experiments, caregiver app, and live demo all happened after March 1. If CSEF requires the notebook to cover through the submission date, entries need to be added through ~March 2026.

**CSEF notebook rules (from SYNOPSYS_REFERENCE):** Must be a bound composition book or equivalent; judges expect to see the scientific method in real time — hypothesis, experiment, results, conclusions per entry. Adding entries now must be dated accurately and not backdated.

### Interview Scripts

**Files:** `CSEF/Presentation/01_main_script.md`, `02_short_version.md`, `03_memorization_guide.md`, `04_qa_bank_and_danger_zones.md`, `05_qa_complete.md`
**Stale elements:**
- All scripts say "73 features" and "R² ≈ 0.25 at 5-10s"
- No mention of the PAC+Stim insight as the narrative climax (the single most interesting finding for judges)
- Elevator pitch script: correct structure but stale numbers
- Q&A bank: needs questions about "why drop spectral features?" and "what's the live demo?"

### Elevator Pitch

**File:** `docs/ELEVATOR_PITCH.md`
**Status:** Reasonably current except for feature count and R² numbers.

---

## Architecture Patterns for This Phase

### Pattern 1: Write → Verify → Commit (per document)

Never update multiple documents in one unbroken pass. The correct flow per document:

1. Write updated content
2. Grep every number in the new content against its source file
3. Flag any number without a traceable source
4. Only then commit

Numbers that require source-file verification before writing:
- Any R² value → check `experimental/FINDINGS.md`, `results/4ch_vs_7ch_r2_gap_report.md`, `results/RESULTS_REPORT.md`
- Any controller alignment/targeting percentage → check `results/RESULTS_REPORT.md`
- Any Hedges' g, p-value → check `results/RESULTS_REPORT.md`
- Any parameter count → check model file or training log
- Any feature count → check `experimental/FINDINGS.md`

### Pattern 2: Docs Directory is Source, CSEF Directory is Copy

The `docs/` directory contains the working Markdown source. The `CSEF/` directory contains the submission-ready copies. When updating a document, update the `docs/` source first, then copy to `CSEF/`.

For PDFs: generate from the Markdown source using the same toolchain that produced the existing PDFs. Do not edit PDFs directly.

### Pattern 3: Presentation Source Discovery (High Priority for Planning)

The presentation PDF (`CSEF_2026_Presentation.pdf`) exists but the Markdown/LaTeX source file that generated it has not been confirmed. The planner must resolve this before scheduling the presentation update task.

Likely location candidates:
- `docs/presentations/` (only has script .md files, not a full presentation source)
- Possibly a Google Slides or Keynote file not in the repo
- Possibly a Pandoc beamer source that was deleted

The safest path if source is missing: reconstruct as a new Pandoc + LaTeX beamer presentation from the existing content, not hand-edit the PDF.

### Pattern 4: The PAC+Stim Narrative Arc

Every document from poster to interview script needs to tell the same story in proportional depth:

> "I discovered that dropping 61 spectral features — which encode subject-specific EEG anatomy that doesn't generalize — and using only 12 PAC trajectory + stimulation context features raises test R² from 0.12 to 0.60. This was the unexpected scientific finding of the project: feature selection mattered more than architecture."

This is the strongest narrative beat for judges because:
1. It's a genuine discovery, not a hyperparameter search
2. It has a clean causal explanation (why spectral features fail)
3. It has a dramatic number (5x R² improvement)
4. It supports the broader thesis (temporal dynamics > snapshot anatomy)

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---|---|---|
| PDF generation from Markdown | Custom renderer | Pandoc + LaTeX (already used for RESEARCH_PAPER_v3.pdf) |
| LaTeX presentation | Custom beamer template | Pandoc beamer with existing theme |
| Number verification | Manual reading | Grep against source JSON/markdown files |
| Interview script Q&A | New content from scratch | Update existing `04_qa_bank_and_danger_zones.md` |

---

## Common Pitfalls

### Pitfall 1: The 0.25 vs 0.60 Ambiguity

**What goes wrong:** Mixing up the old pipeline R² (0.25, from 73-feature model, smoothed targets ts=5 for the horizon sweep) with the new R² (0.60, from 12-feature model, raw targets ts=1).

**Why it happens:** Both numbers are real. The horizon sweep figure (the "hero chart") was generated with the 73-feature model. The 0.60 comes from the PAC+Stim ablation study.

**How to avoid:** The horizon sweep chart needs new numbers generated from the 12-feature model. Until regenerated, the chart must be labeled as "73-feature model baseline" and the 0.60 stated separately as a post-baseline finding.

**Warning signs:** Any document that says "TCN R² ≈ 0.25" without explaining that this is from the old feature set is mixing contexts.

### Pitfall 2: Page Limit on Presentation

**What goes wrong:** Adding PAC+Stim finding + productization narrative to the presentation pushes past 13 pages.

**Why it happens:** Additive updates without removing old content.

**How to avoid:** For every new section added to the presentation, identify what existing content it replaces or compresses. The Methods section can compress architecture exploration (already covered by the finding that 8 models all converge to R² = 0.287) to make room for the feature ablation finding.

### Pitfall 3: Notebook Backdating

**What goes wrong:** Writing lab notebook entries with dates before they actually occurred.

**Why it happens:** Wanting the notebook to look complete and continuous.

**How to avoid:** New entries after March 1 must be dated in March 2026 and labeled as "CSEF preparation update." Do not assign them January or February dates. CSEF judges may ask about the notebook timeline.

### Pitfall 4: Sync Drift Between docs/ and CSEF/

**What goes wrong:** Updating `docs/poster/POSTER_BOARD_V5.md` but forgetting to copy the updated version to `CSEF/Poster/POSTER_BOARD_V5.md`, so submission package has stale content.

**How to avoid:** Each plan wave that modifies a document must include a sync step that copies docs/ → CSEF/ as an explicit task action.

### Pitfall 5: Feature Count Cascade

**What goes wrong:** Changing "73 features" to "12 features" in one place but missing it in 7 others — the paper Methods section, the poster approach section, the interview script, the Q&A bank, the elevator pitch, the memorization guide, and the presentation Methods slide all independently state the feature count.

**How to avoid:** Run a grep for "73 feat" and "61 spectral" across all docs before declaring a document done. There should be zero matches in updated materials (or they should be in historical/comparison context only).

### Pitfall 6: Claiming the Live Demo is Fully Functional

**What goes wrong:** Saying "live Muse 2 EEG demo" when the Muse 2 BLE hardware path is SimulatedEEGAdapter on Darwin 25.x.

**Why it happens:** The app is live, the code supports Muse 2 hardware, but BLE doesn't work on the current host.

**How to avoid:** The honest framing is: "live demonstration app with simulated EEG — the same app runs with real Muse 2 hardware on BLE-enabled systems." The caregiver app at HF Spaces uses simulated EEG only (by design — BLE is local-only and cannot bridge to cloud).

---

## Source Map: Numbers and Their Authoritative Files

Every number that appears in CSEF materials should be traceable to one of these files. This table is for the planner to use when writing task verification steps.

| Claim | Authoritative Source File |
|---|---|
| TCN R² = 0.606 (7ch, 12 feat, ts=1) | `experimental/FINDINGS.md` multi-seed mean |
| TCN R² = 0.430 (4ch, 12 feat, ts=1) | `experimental/FINDINGS.md` 4ch table |
| Multi-seed mean ± std: 0.606 ± 0.032 | `experimental/FINDINGS.md` multi-seed table |
| Previous baseline R² = 0.121 (7ch, 73 feat) | `experimental/FINDINGS.md` baseline table |
| 12 PAC+stim features (list) | `experimental/FINDINGS.md` feature list |
| Horizon sweep (old): 0.254/0.240/0.278 at 5s/8s/10s | `models/sweep_horizons_results.json` |
| Controller alignment 72.1% vs 64.5% | `results/RESULTS_REPORT.md` |
| Low-PAC targeting 82.6% vs 51.7% | `results/RESULTS_REPORT.md` |
| Hedges' g alignment = 1.31 | `results/RESULTS_REPORT.md` |
| Hedges' g low-PAC = 4.47 | `results/RESULTS_REPORT.md` |
| PAC gap +30.5 vs +21.1 ×10⁻⁶ | `results/RESULTS_REPORT.md` |
| 91% of oracle | 30.5/33.3 = 0.9159 → 91% (round to match paper) |
| 35/35 subjects benefit | `results/RESULTS_REPORT.md` |
| EEGNet static R² = 0.287 (7ch) | `results/4ch_vs_7ch_r2_gap_report.md` |
| EEGNet static R² = 0.016 (4ch) | `results/4ch_vs_7ch_r2_gap_report.md` |
| EEGNet params = 1,457 (7ch) / 1,409 (4ch) | `results/4ch_vs_7ch_r2_gap_report.md` |
| TCN params = 31,043 (original) | `results/RESULTS_REPORT.md` |
| TCN params = 5,154 (PAC+stim, h=32) | `experimental/FINDINGS.md` architecture search table |
| 4ch TCN params = 22,914 (h=64) | `experimental/FINDINGS.md` 4ch table |
| Caregiver app URL | `docs/PILOT_LINKS.md` or PROJECT.md |
| HF Spaces URL | https://huggingface.co/spaces/amaarc/neurocare-40hz |

---

## Document Inventory and Update Priority

| Document | Location | Priority | Effort | Key Changes |
|---|---|---|---|---|
| Interview scripts (01–05) | CSEF/Presentation/ | P1 (judging) | Medium | Feature count, R² numbers, PAC+Stim narrative, live demo |
| Elevator pitch | docs/ELEVATOR_PITCH.md | P1 (judging) | Small | R² 0.25→0.60, feature count, live demo mention |
| Poster board V6 | docs/poster/ → CSEF/Poster/ | P1 (judging) | Large | Feature section, R² values, potentially new horizon sweep chart |
| Presentation PDF | CSEF/Presentation/ | P1 (judging) | Large | Source discovery, full update |
| Research paper | docs/paper/ → CSEF/Research Paper/ | P2 (supplement) | XL | Abstract, Methods, Results, Discussion |
| Lab notebook augmentation | CSEF/Lab Notebook/ | P2 (supplement) | Medium | New entries from March onward |

---

## Validation Architecture

The nyquist_validation config is not explicitly set to false, but this is a documentation-only phase. There are no code tests to run. The "tests" for this phase are document audits:

- **Per document:** grep for every key number, verify against source file
- **Poster/presentation:** manual review against the source number table above
- **Phase gate before judging:** all documents pass the number audit with zero unverified claims

No automated test suite applies. Verification is entirely manual grep + review.

---

## Open Questions

1. **Presentation source file missing?**
   - What we know: `CSEF_2026_Presentation.pdf` exists in two locations; no obvious .tex or .md source in the repo
   - What's unclear: Was this generated from a LaTeX beamer source that wasn't committed, or from a slide tool (Keynote, Slides)?
   - Recommendation: Check git log for the PDF, then check if `.tex` file exists anywhere in the tree. If not, reconstruct from Markdown.

2. **Has the horizon sweep been regenerated with PAC+Stim features?**
   - What we know: `experimental/results/horizon_sweep_pac_stim.json` exists but hasn't been read
   - What's unclear: Whether the new sweep shows the same "baselines collapse at 3s" shape with higher TCN R² values
   - Recommendation: Read `experimental/results/horizon_sweep_pac_stim.json` in the first plan wave before finalizing any chart updates.

3. **Is the Synopsys poster the same event as CSEF, or is CSEF a separate fair?**
   - What we know: The poster says "Synopsys Championship — Santa Clara County"; CSEF is California State Science and Engineering Fair; these are two different fairs
   - What's unclear: Has Synopsys already occurred? If so, CSEF is a subsequent fair with potentially different display rules
   - Recommendation: CSEF likely has the same or similar display rules. Confirm poster board dimensions (CSEF is typically 36"x48" vs Synopsys 48"x56"). This affects layout redesign scope.

4. **What is the CSEF lab notebook format requirement?**
   - What we know: Synopsys required a bound composition notebook or equivalent
   - What's unclear: Whether CSEF accepts a printed/bound MD→PDF export or requires a physical notebook
   - Recommendation: The existing `P10_Lab_Notebook_VFINAL.pdf` may be submittable; adding new entries means updating the MD source and regenerating the PDF.

5. **Should the research paper be resubmitted or is it already submitted?**
   - What we know: A v3 paper exists and is in the CSEF/ directory
   - What's unclear: Whether the paper is already uploaded as part of a CSEF submission portal, or whether it can still be updated
   - Recommendation: If CSEF submission portal allows updates, update the paper. If already locked, focus effort on oral presentation materials.

---

## Sources

### Primary (HIGH confidence)
- `experimental/FINDINGS.md` — PAC+Stim discovery, feature ablation table, multi-seed results, 4ch results
- `results/RESULTS_REPORT.md` — controller comparison, statistical tests, effect sizes
- `results/4ch_vs_7ch_r2_gap_report.md` — 4ch vs 7ch performance gap
- `.planning/PROJECT.md` — v3.0 current state, live system URLs, key decisions
- `.planning/STATE.md` — project history, key decisions log
- `docs/poster/POSTER_BOARD_V5.md` — current poster content and compliance checklist
- `CSEF/Presentation/01_main_script.md` — current interview script
- `CSEF/Research Paper/RESEARCH_PAPER_v3.md` — current paper (first 100 lines read)

### Secondary (MEDIUM confidence)
- `experimental/results/horizon_sweep_pac_stim.json` — new horizon sweep data, not yet read
- `CSEF/Presentation/JUDGE_INTERVIEW_PREP.md` — existing Q&A preparation

### Tertiary (LOW confidence)
- Presentation PDF source file location — not confirmed

---

## Metadata

**Confidence breakdown:**
- What needs updating: HIGH — source files and existing docs are both clear
- New numbers (PAC+Stim R² values): HIGH — from `experimental/FINDINGS.md`
- Presentation source file: LOW — not confirmed, needs discovery in Wave 0
- CSEF-specific submission rules: MEDIUM — Synopsys rules known, CSEF not separately verified

**Research date:** 2026-03-22
**Valid until:** 2026-04-09 (judging day — no point re-researching after this)
