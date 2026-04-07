# Visual Cohesion Audit — CSEF Poster V2

**Audited:** 2026-04-07
**Artifact:** `CSEF/Poster/csef_posters/CSEF_poster_v2.pdf` (1.7 MB)
**Spec Reference:** `docs/poster/POSTER_BOARD_V8.md`
**Auditor:** Phase 17 execution agent

---

## Overall Visual Cohesion Verdict

**PASS WITH MINOR ISSUES** — The poster achieves strong visual cohesion. The four-column layout is balanced, the color palette is applied consistently, and the poster tells a coherent scientific story from problem to solution to results. Several minor issues need attention before judging.

---

## Dimension 1: Layout and Reading Flow

**Verdict: PASS**

| Criterion | Observation | Status |
|---|---|---|
| Left-to-right reading order | Column 1 (Intro/Background/Hypothesis) → Column 2 (System Architecture) → Column 3 (Materials/Procedures/Clinical) → Column 4 (Results/Conclusions). Flow is natural. | PASS |
| Top-to-bottom within columns | Each column progresses logically: problem framing → methodology → results. No section breaks the narrative flow. | PASS |
| Visual hierarchy | Title banner → column headers → body text → figure captions. Hierarchy is clear at poster scale. | PASS |
| Whitespace balance | Column 3 (Materials + Procedures) is relatively text-heavy with the Training/Validation Protocol figure occupying a large portion. Column 2 and Column 4 balance figures and text well. Overall whitespace usage is acceptable. | PASS |
| Story structure | Problem (C1) → Architecture Search (C2) → Key Discovery/Feature Ablation (C2, gold box) → Methodology (C3) → Results (C4) → Conclusions (C4). The arc is coherent. | PASS |
| Section grouping | Sections within columns are visually demarcated by teal header bars. No sections bleed across column boundaries. | PASS |

**Notable strength:** The "Key Discovery" gold callout box in Column 2 successfully acts as a visual pivot point — it draws the eye from methods to results. The placement mid-column is effective.

**Minor issue:** The "Data Analysis" label and Figure 6 (Horizon Sweep) appear in Column 3, not Column 4. Given the horizon sweep is the core analytical finding supporting Results, its placement in the Materials/Procedures column creates a slight narrative disruption. A reader scanning Column 4 for all results will miss Figure 6 entirely.

---

## Dimension 2: Typography

**Verdict: NEEDS-ATTENTION**

| Criterion | Observation | Status |
|---|---|---|
| Header font (Amaranth Bold) | Section headers (Introduction, Background, Hypothesis, System Architecture, Materials, etc.) render in a bold sans-serif consistent with Amaranth. Headers are white on dark teal background bars. | PASS |
| Body font (Titillium Web) | Body text appears in a clean condensed sans-serif consistent with Titillium Web. | PASS |
| Font size — headers | Column section headers read as approximately 20pt printed; legible at poster-scale viewing distance (>2 ft). | PASS |
| Font size — body text | Body text is dense in several sections, particularly the Procedure validation bullet list and the Towards Clinical Use section. At poster scale these are borderline legible for viewers at 2+ ft. | NEEDS-ATTENTION |
| Font size — table text | All four data tables (Result 1, Result 3, Result 4, Stage 1 Architecture) use small tabular text. The Stage 1 Architecture table (EEGNet vs Causal TCN comparison) appears particularly small. | NEEDS-ATTENTION |
| Heading hierarchy | Three levels visible: (1) column section headers on teal bars, (2) bolded result sub-headers ("Result 1: TCN Predictive Controller..."), (3) inline bold for key terms. Hierarchy is consistent. | PASS |
| Font rendering in PDF | No visible font substitution artifacts. Text renders cleanly throughout. | PASS |
| Font consistency | No mixed fonts detected — single-family treatment is consistent. | PASS |

**Issues:**
1. The EEGNet vs Causal TCN comparison table in Column 2 is particularly compact. The six-column table (Purpose, Parameters, Input, Architecture, Output, Key Feature) may challenge readability at poster distance.
2. The Procedure validation bullet list in Column 3 packs statistical validation details into small text. Judges who want to verify methodology will need to step close.

---

## Dimension 3: Color Palette

**Verdict: PASS**

| Palette Element | Specified | Observed in PDF | Status |
|---|---|---|---|
| Background | #FFFFFF | Pure white background throughout | PASS |
| Primary / TCN / positive (#1B6B6E dark teal) | Used for TCN bars, positive callouts, section header backgrounds | Dark teal used consistently for: section header bars, TCN bar in Controller Comparison chart, teal zone shading in timeline figure | PASS |
| Secondary text/axes (#1B2A4A dark navy) | Body text, axis labels, table text | Body text renders as dark (navy/near-black) throughout | PASS |
| Accent gold (#D4A843) | Callout boxes, Key Discovery box | Gold background on "Key Discovery" box and on the "Summary of Key Results" callout boxes (72.1%, 82.6%, 35/35) | PASS |
| Accent coral (#C85A4A) | Fixed schedule bars, negative results | Coral/red used for Fixed Schedule in controller comparison; red X marks in Fixed Schedule panel of Figure 1 | PASS |
| Accent amber (#E8963E) | Reactive/intermediate | Amber used for Reactive bar in controller comparison chart. Distinct from coral. | PASS |

**Color consistency observations:**
- The controller comparison bar chart (Figure 13 on poster) correctly uses: coral = Fixed Schedule, amber = Reactive, teal = TCN Predictive, with Oracle shown separately. Consistent with palette spec.
- The feature ablation figure (Figure 4 in PDF layout) uses red for 73-feature model (negative result) and teal for 12-feature model (positive result). Correct.
- The horizon sweep figure uses teal for TCN advantage zone and persistence lines in a contrasting style. Readable.

**Color accessibility:** The teal (#1B6B6E) and coral (#C85A4A) are both distinguishable to deuteranopia (red-green color blindness) because they differ in lightness and hue position. The teal vs amber distinction may be less clear in print under certain lighting. This is a minor accessibility concern that is acceptable for a poster context.

**No palette violations detected.**

---

## Dimension 4: PDF vs PPTX Consistency

**Verdict: PASS WITH NOTES**

Direct PDF inspection shows:

| Element | PDF Status | Issue |
|---|---|---|
| All four columns present | Yes — visible column structure matches the 4-column spec | PASS |
| Title banner | Present: "Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease" + "Amaar M. Chughtai" | PASS |
| All 10 figures present | The PDF includes: Figure 1 (Fixed vs Adaptive), Figure 2 (PAC Mechanism brain diagram), Figure 3 (Fixed vs Adaptive Scheduling detail), Figure 4 (Feature Ablation), Figure 5 (System Architecture Flowchart), Figure 6 (Horizon Sweep), Figure 7 (Training/Validation Protocol), Figure 8 (Real-Data Controller Timeline), Figure 9 (Controller Comparison Bar + Per-Subject), Figure 12 (Metric Definitions). All expected figures are rendered. | PASS |
| Text clipping | No visible text clipping detected in any section | PASS |
| Element alignment | No visible misalignment between text blocks and figures | PASS |
| Missing content vs V8 spec | The PDF does not include separate "Conclusions" numbered list as a distinct section — Conclusions (1-4) appear embedded in the Results column, which is consistent with the actual layout decision. Conclusion 5 ("Half of patients habituate...") does NOT appear in the PDF. | NOTE |
| Future Directions | Present in PDF with 4 bullets (not 5 as in V8 spec — "System cost under $250/patient" omitted from PDF) | NOTE |
| Attribution text | "Diagram created by Amaar Chughtai" attribution text visible on several figures | PASS |
| AI disclosure in Acknowledgements | Present: "AI coding assistant (Claude Code, Anthropic) used for software development" | PASS — NOTE: phrase "AI coding assistant" present but longer disclosure ("All experimental design, analysis, interpretation, and conclusions are the student's own work") also present |

**Key differences between PDF and V8 spec:**
- Conclusion 5 (habituation claim) is absent from the PDF — this is actually better (see Judge-Readiness Audit, as this claim is unsubstantiated)
- "System cost under $250/patient" Future Direction bullet appears in PDF as "System cost under $300/patient (consumer EEG + headphones)" — minor dollar figure discrepancy between V8 spec ($250) and PDF ($300). The PDF version ($300) is consistent with the "Towards Clinical Use" section on the same poster which also says "Under $300"

---

## Dimension 5: CSEF Compliance

**Verdict: PASS**

| Requirement | Observed | Status |
|---|---|---|
| No school name or logo | No school name visible on the board | PASS |
| No student email/postal/web/social | No contact information visible | PASS |
| No QR codes on board | No QR codes visible | PASS |
| No photos of people | No photos of humans — all figures are data plots and diagrams | PASS |
| No previous fair awards mentioned | No award references | PASS |
| No category label | No category designation on board | PASS |
| AI disclosure | "AI coding assistant (Claude Code, Anthropic) used for software development. All experimental design, analysis, interpretation, and conclusions are the student's own work." — present in Acknowledgements | PASS |
| Author attribution on figures | "Diagram created by Amaar Chughtai" visible on multiple figures | PASS |
| References on board | 8 references present in bottom of Column 1 | PASS |

---

## Overall Visual Story Assessment

The poster tells a coherent visual story:

1. **Problem setup (C1):** Introduction + Background + Hypothesis establish the clinical need and scientific gap clearly. Figure 1 (Fixed vs Adaptive) immediately visualizes the core problem.
2. **Solution narrative (C2):** Architecture table → Key Discovery callout (gold) → Stage 2 TCN description + System Architecture flowchart build the solution story step by step. The gold Key Discovery box is the strongest visual element on the poster.
3. **Methodology (C3):** Dataset, Procedure, and Training/Validation Protocol provide methodological credibility without overwhelming the non-expert viewer.
4. **Results payoff (C4):** The four results — controller comparison, per-subject universality, fatigue robustness × severity, fatigue robustness × model type — progressively strengthen the argument. The three gold callout boxes (72.1%, 82.6%, 35/35) act as an effective summary anchor.
5. **Clinical vision (C3 bottom / C4 bottom):** "Towards Clinical Use" and Future Directions close the loop from bench to bedside.

**The poster succeeds as a visual document.** A judge can grasp the thesis ("predictive control outperforms reactive") in 30 seconds from the title + Key Results boxes alone. Supporting evidence is layered for deeper engagement.

---

## Issues Summary for Pre-Judging Action

| # | Dimension | Issue | Severity | Location |
|---|---|---|---|---|
| V1 | Typography | Stage 1 architecture comparison table (EEGNet vs Causal TCN) is small — may be hard to read at distance | LOW | Column 2, middle section |
| V2 | Typography | Procedure validation bullet list is text-dense | LOW | Column 3, Procedure section |
| V3 | Layout | Figure 6 (Horizon Sweep) appears in Column 3 (Data Analysis) rather than Column 4 (Results) — results-oriented readers may miss it | LOW | Column 3 / Column 4 boundary |
| V4 | PDF vs spec | Future Directions says "$300" in PDF, "$250" in V8 spec — minor inconsistency within poster itself | LOW | Column 4, Future Directions vs Column 3, Towards Clinical Use |
| V5 | PDF vs spec | Conclusion 5 (habituation claim) absent from PDF — this is actually correct behavior given the claim is unsubstantiated | INFO | N/A — no action needed |

**No HIGH severity visual issues detected. The poster is visually ready for judging.**
