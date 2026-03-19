# Phase 6: Write Research Paper - Context

**Gathered:** 2026-03-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Write a comprehensive, publication-grade research paper documenting the full closed-loop 40 Hz entrainment system — from clinical motivation through architecture exploration to TCN-based predictive control and validated results. The paper is venue-agnostic initially; once target journals are finalized, it will be reformatted to specific submission guidelines. This phase covers writing the paper and identifying suitable journals; reformatting to a specific journal's template is a separate step after journal selection.

</domain>

<decisions>
## Implementation Decisions

### Target venue & format
- Write venue-agnostic first — no page limits, no specific template
- Be thorough with no length constraint; comprehensive coverage of the full research
- Supplement structure (main paper + supplementary materials) to follow whatever is standard for the target journals identified
- Present as independent computational neuroscience research — no mention of Synopsys/CSEF
- Solo author: Amaar Chughtai
- Journal search running in parallel to identify prestigious, fast-turnaround venues that accept computational biology / neural engineering / biomedical AI papers from independent researchers

### Paper structure & depth
- Full IMRAD structure with additional sections:
  - Introduction (clinical motivation, lead with Alzheimer's burden)
  - Full standalone Literature Review section (40 Hz entrainment studies, PAC in AD, closed-loop neuromodulation, EEG prediction models)
  - Methods (data, preprocessing, PAC computation, EEGNet, feature engineering, TCN, closed-loop controller design)
  - Full Architecture Search section — dedicated section documenting all 8 EEGNet variants (V1-V8), what each tried, why each hit the R²≈0.287 ceiling, and how this justified the temporal prediction pivot
  - Results with full experimental subsection for closed-loop controller comparison (all 4 strategies, fatigue analysis, threshold sensitivity, per-subject results)
  - Discussion
  - Future Directions — dedicated subsection outlining clinical translation pathway (IRB, pilot study design, real-time hardware requirements)
  - Conclusion
- Clinical impact story as the narrative arc — technical innovation serves the clinical narrative
- Limitations: brief and forward-looking, acknowledge key limitations concisely, pivot to future directions

### Figure selection
- New system architecture diagram needed: clean block diagram showing EEG → Preprocessing → EEGNet → Features → TCN → Controller → Stimulation decision
- New horizon sweep figure needed: TCN vs baselines (persistence, Ridge) across 1-10s prediction horizons — key result showing TCN advantage at 5-10s
- 7 existing figures available in results/figures/ (controller comparison, PAC targeting gap, per-subject utility, stim vs alignment, threshold sensitivity, timeline example)
- Claude decides which existing figures are essential for main paper vs. supplement based on narrative flow
- Figure budget: system architecture diagram + horizon sweep + best subset of existing figures in main text

### Tone & audience
- Formal academic tone, publication-grade writing
- Target audience: journal reviewers in computational neuroscience / biomedical engineering
- No AI tool usage disclosure — development tools treated like IDEs
- Data availability: reference OpenNeuro ds005048 (public dataset); code kept private
- No code availability statement beyond "available upon reasonable request"
- Future Directions subsection: outline path from computational validation to clinical deployment (IRB, pilot study, hardware)

### Claude's Discretion
- Which of the 7 existing figures belong in main paper vs. supplement
- Exact section ordering within IMRAD framework
- How deep to go in literature review (breadth vs. depth of coverage)
- Statistical reporting format (inline vs. tables vs. both)
- Reference/citation style (to be determined by journal selection)
- How to structure the architecture search section (chronological narrative vs. systematic comparison)

</decisions>

<specifics>
## Specific Ideas

- The abstract is already written (247 words, `docs/abstract/ABSTRACT.md`) — paper should be consistent with its claims
- Key narrative: at short horizons (1-2s) persistence beats the TCN, but at the operationally useful 5-10s range the TCN is the only model that doesn't collapse — this is the core contribution
- The 8-architecture exploration showing a R²≈0.287 ceiling from static prediction is a scientific finding in itself — it demonstrates that instantaneous EEG cannot capture PAC dynamics, motivating temporal approaches
- All results validated on real EEG from 35 dementia patients (not simulated) — this is a key strength
- 91% of oracle performance is the headline number for the closed-loop system
- Poster board V5 (`docs/poster/POSTER_BOARD_V5.md`) and methodology doc (`docs/methodology/CURRENT_METHODOLOGY.md`) are rich source material

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/abstract/ABSTRACT.md`: 247-word abstract already written and submitted — paper must be consistent
- `docs/methodology/CURRENT_METHODOLOGY.md`: comprehensive methodology documentation — primary source for Methods section
- `docs/poster/POSTER_BOARD_V5.md`: condensed poster content with validated claims — source for Results framing
- `results/RESULTS_REPORT.md`: comprehensive statistics for all claims
- `results/figures/`: 7 PNG+PDF publication figures (controller_comparison, pac_targeting_gap, per_subject_utility, stim_vs_alignment, threshold_sensitivity, timeline_example)
- `results/*.json`: raw results data for all experiments
- `docs/methodology/CODE_MAP.md`: documents all 8 architecture attempts and the ceiling finding
- `docs/reports/TEMPORAL_PREDICTION_DEEP_DIVE.md`: detailed temporal prediction methodology
- `docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md`: validated summary of final results

### Established Patterns
- All metrics use Wilcoxon signed-rank tests and Hedges' g effect sizes (N=35 subjects)
- PAC values reported in dimensionless ×10⁻⁶ units
- TCN patience=20 (not 10), EEGNet loss=MSE (not Huber), best epoch=53
- Subject-level splits (no within-subject leakage)

### Integration Points
- Paper generation should read existing docs for accuracy — no reinvention of claims
- Figures referenced by their existing filenames in results/figures/
- New figures (architecture diagram, horizon sweep) to be generated as part of this phase

</code_context>

<deferred>
## Deferred Ideas

- Reformatting paper to specific journal template — happens after journal selection is finalized
- Submission cover letter — write after journal is chosen
- Response to reviewers template — premature until submission
- Preprint server posting (arXiv/bioRxiv) — discuss after main paper is written

</deferred>

---

*Phase: 06-write-research-paper*
*Context gathered: 2026-03-15*
