# Phase 4: Finalize Lab Notebook - Research

**Researched:** 2026-03-08
**Domain:** Judge-ready lab notebook finalization, chronology control, and packaging
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Chronology and date anchoring
- Re-anchor the notebook timeline to project approval rather than the earliest private prep work.
- Use `Jan 15, 2026` as the default approval/start anchor unless stronger documentation proves a tighter `Jan 15-17, 2026` date.
- Preserve chronological order after that anchor date.
- Use active-day entries with brief gap notes between work clusters.
- Keep full date headers for active days.
- Include key planning/admin milestones when they materially change the research direction.
- Each entry must reflect only what was reasonably known at that time; avoid hindsight narration or revealing the full final project too early.

#### Entry structure and density
- Use a hybrid format: paragraph narrative where needed, with short structured blocks where they improve clarity.
- Keep the notebook concise and judge-readable rather than paper-like.
- Use moderate technical detail by default; reserve deeper detail for pivotal debugging, architecture pivots, validation, and breakthrough days.
- Include brief rationale for next steps so the notebook shows the evolving thought process without becoming diary-style.

#### Visual usage
- Embed figures or diagrams only on pivotal days and major transitions.
- Do not force visuals into every few entries.

#### Artifact handling and review workflow
- Do not delete existing files.
- Do not edit existing notebook files in place during finalization work.
- Create new files for proposed notebook updates and reorganized outputs so the user can review them safely.
- The user will generate the PDF manually via the existing utility after reviewing the new files.

#### Style reference
- Model the final notebook after Kushal's example notebook (`docs/reference/Project S-19-05 Research Notebook (1).pdf`) in overall presentation and progression.
- Aim for research-grade, robust, presentable writing that stays concise rather than bloated.

### Claude's Discretion
- Exact naming and folder organization for newly created review files.
- Exact balance of prose vs structured blocks within the approved hybrid style.
- Which pivotal days deserve embedded figures, as long as figure usage stays sparse and justified.
- Whether stronger approval-date evidence is found later; if found, update planning assumptions around the locked `Jan 15, 2026` fallback rather than changing the broader chronology rules.

### Deferred Ideas (OUT OF SCOPE)
- Full reorganization of broader submission docs beyond what directly supports final notebook readiness.
- New scientific content, new figures not grounded in existing repository data, or any project-scope expansion.
</user_constraints>

## Summary

The existing notebook already contains most of the scientific substance needed for a strong final artifact, but it is misaligned with Phase 4 in three important ways: its visible timeline starts too early for the locked approval-anchor rule, its prose is still closer to a polished retrospective paper than a judge-facing lab record, and its packaging is inconsistent with the rest of the repo. The safest plan is not a rewrite-from-scratch. It is a non-destructive finalization pass that creates a review-ready notebook candidate, an evidence map, and a small packaging layer around the current materials.

The strongest anchors for planning are already in-repo: `notebooks/P10_Lab_Notebook_FINAL.md` for base content, `archive/notebooks/LOG_NOTEBOOK.md` and `archive/notebooks/LAB_NOTEBOOK.md` for chronology/gap handling patterns, `archive/notebooks/LAB_NOTEBOOK_ERRATA.md` for correction discipline, `docs/reference/SYNOPSYS_REFERENCE.md` for fair expectations, `docs/reference/Project S-19-05 Research Notebook (1).pdf` for presentation style, and `docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md` plus `docs/reference/PROJECT_DEEP_DIVE.md` for claim verification. The repo's local skills also point the same direction: `ml-auditor` emphasizes skepticism and evidence, and `ml-engineer` emphasizes understanding before editing. For this phase, that translates to trace every date, metric, and figure before rewriting it.

The planning wrinkle is that Phase 4 has no formal requirement IDs in `ROADMAP.md`, while older planning docs still assume a December-March notebook build and an 8-10 page target. Those older assumptions conflict with the locked Phase 4 context, which says the notebook is already near the right length and now needs chronology cleanup, evidence discipline, and review-safe packaging. The most defensible approach is to treat Phase 4 as a finalization/audit overlay with a minimal new requirement set rather than trying to reuse the earlier Phase 1-3 requirement mapping unchanged.

**Primary recommendation:** Plan Phase 4 as a four-slice finalization pass: preserve originals, build a new review candidate in `notebooks/` that matches the existing PDF generator contract, attach an evidence/changelog sidecar, and gate release with both automated sanity checks and explicit human chronology/fairness review.

## Requirement Interpretation

`ROADMAP.md` leaves Phase 4 requirements as `TBD`, and `.planning/REQUIREMENTS.md` maps all existing v1 requirements to Phases 1-3 only. For planning, use a minimal Phase 4 requirement set focused on finalization rather than new content creation.

### Proposed Minimal Requirement Set

| ID | Requirement | Why this is defensible |
|----|-------------|------------------------|
| FNL-01 | Re-anchor the notebook to the approval-era start date and preserve chronological order after the anchor. | Directly required by `04-CONTEXT.md`; not covered explicitly by existing IDs. |
| FNL-02 | Produce a new review-ready notebook source without modifying or deleting existing notebook artifacts. | Directly required by `04-CONTEXT.md`; matches lab notebook preservation norms. |
| FNL-03 | Ensure every retained metric, date-sensitive claim, and pivotal figure is traceable to existing repository evidence or explicitly downgraded/removed. | Needed because the repo already contains notebook errata and chronology drift. |
| FNL-04 | Final notebook entries must use active-day headers plus explicit gap notes, with no hindsight narration and no fabricated content. | Core judge/fairness requirement for this phase. |
| FNL-05 | Package the final notebook in a review-safe way that supports manual PDF generation and resolves or documents path/tool mismatches. | Required because `docs/INDEX.md` and `notebooks/generate_notebook_pdf.py` currently disagree with the live notebook location/state. |
| FNL-06 | Provide a validation checklist separating automated sanity checks from human review of chronology, fairness, and judge readability. | Necessary because this is a docs-finalization phase with limited executable testing. |

### How to Interpret Older Requirements

| Existing item | Keep / reinterpret / drop for Phase 4 | Rationale |
|---------------|----------------------------------------|-----------|
| `CONT-*`, `ENTRY-*`, `VIS-*`, `QUAL-*` from `.planning/REQUIREMENTS.md` | Reinterpret as already-created substrate to audit/finalize, not as fresh creation work. | Phase 4 is refinement of an existing notebook, not a restart. |
| 8-10 page target in `.planning/PROJECT.md` and `ROADMAP.md` | Treat as outdated for Phase 4 planning. | `04-CONTEXT.md` says the notebook is already near the right length and should get targeted cleanup, not forced compression. |
| December 10, 2025 start in current notebook | Treat as outdated for Phase 4 final candidate. | Locked decision moves anchor to approval timeframe. |

## Standard Stack

### Core

| Library / Asset | Version | Purpose | Why Standard |
|-----------------|---------|---------|--------------|
| `notebooks/P10_Lab_Notebook_FINAL.md` | repo-local | Main source notebook to mine and refine | It already contains the strongest consolidated narrative and entry structure. |
| `notebooks/generate_notebook_pdf.py` | repo-local | Existing PDF generator | Lowest-risk render path; user explicitly wants manual PDF generation through the existing utility. |
| `docs/reference/SYNOPSYS_REFERENCE.md` | repo-local | Fair expectations and notebook rules | Closest repo-local judge constraint source. |
| `docs/reference/Project S-19-05 Research Notebook (1).pdf` | repo-local | Presentation/style reference | Locked style model for overall feel and progression. |

### Supporting

| Library / Asset | Version | Purpose | When to Use |
|-----------------|---------|---------|-------------|
| `archive/notebooks/LOG_NOTEBOOK.md` | repo-local | Gap-note and reading-period evidence | Use when current notebook needs chronology support without inventing detail. |
| `archive/notebooks/LAB_NOTEBOOK.md` | repo-local | Older structured notebook with continuation patterns | Use to recover structure, summaries, and date clusters. |
| `archive/notebooks/LAB_NOTEBOOK_ERRATA.md` | repo-local | Correction precedent | Use when a claim/date/metric in the old notebook is known to be stale. |
| `docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md` | repo-local | Verified final metrics and limits | Use to cross-check headline quantitative claims. |
| `docs/reference/PROJECT_DEEP_DIVE.md` | repo-local | Judge-facing explanations and rationale | Use to simplify dense entries without losing correctness. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Editing `notebooks/P10_Lab_Notebook_FINAL.md` in place | Create a new corrected review candidate | New-file strategy is safer and explicitly required. |
| Building a new renderer | Reuse `notebooks/generate_notebook_pdf.py` by matching its expected corrected filename | Reuse avoids tool churn; the main cost is conforming to the generator's hardcoded filenames. |
| Large docs reorg first | Content freeze first, then minimal packaging cleanup | Defers unnecessary path churn until the notebook text is stable. |

**Installation:**
```bash
source venv/bin/activate
python -m py_compile notebooks/generate_notebook_pdf.py
```

No new libraries should be introduced for this phase unless the existing PDF path is proven unusable.

## Architecture Patterns

### Recommended Project Structure

```text
notebooks/
├── P10_Lab_Notebook_FINAL.md                     # existing source, preserved
├── P10_Research_Log_Notebook_Corrected.md       # new review candidate, matches generator contract
├── P10_Research_Log_Notebook_Corrected_REVIEW.md  # change log + reviewer notes
└── P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md  # claim/date/figure traceability

docs/
└── notebook/
    └── README.md                                # optional pointer after content freeze
```

Treat `notebooks/` as the working source-of-truth during finalization because the live notebook artifacts and the existing generator both live there. Only add a lightweight `docs/notebook/` pointer after the review candidate is stable.

### Pattern 1: Non-Destructive Review Bundle
**What:** Preserve all existing notebook files and create a parallel finalization bundle for review.
**When to use:** Always for this phase.
**Example:**
```text
Keep:
- notebooks/P10_Lab_Notebook_FINAL.md
- notebooks/P10_Lab_Notebook_FINAL.pdf

Add:
- notebooks/P10_Research_Log_Notebook_Corrected.md
- notebooks/P10_Research_Log_Notebook_Corrected_REVIEW.md
- notebooks/P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md
```

**Why this pattern fits the repo:** `notebooks/generate_notebook_pdf.py` already hardcodes `P10_Research_Log_Notebook_Corrected.md` and `P10_Research_Log_Notebook_Corrected.pdf`, so creating that corrected source is the easiest way to reuse the existing utility without overwriting the current notebook.

### Pattern 2: Evidence-First Chronology Rewrite
**What:** Rebuild the visible timeline from anchored evidence, not memory.
**When to use:** For every entry whose date, metric, or narrative scope changes.
**Example:**
```text
Priority order for evidence:
1. Current notebook text
2. Archive notebook / log notebook
3. Verified reports and errata
4. Git commit history
5. Explicit gap note if evidence is thin
```

Use active-day entries only where evidence supports an actual day-level claim. For unsupported spans, insert a short gap note rather than synthetic day-by-day detail.

### Pattern 3: Active Day + Gap Note Layout
**What:** Use full dated headers for real work days, with short bridging notes between clusters.
**When to use:** Across the full final notebook.
**Example:**
```markdown
## January 15, 2026: Causal TCN Architecture Development

**Daily Goal:** Design and implement temporal convolutional network for PAC forecasting.

...entry body...

---

**Gap note (January 16-February 4):** Midterms limited coding time; reading and paper planning continued in the physical notebook.
```

This matches the locked format choice and is supported by the archive notebook's explicit reading-period entries.

### Pattern 4: Correct by Sidecar, Not by Silent Rewrite
**What:** When a prior notebook fact is stale or misleading, record the correction in a review note or errata sidecar instead of pretending the old state never existed.
**When to use:** Known metric/date conflicts, especially around validation results and units.
**Example:**
```markdown
## Correction: TCN validation date

Original notebook entry grouped the final TCN replay validation under Feb 21.
Repository evidence shows the TCN-integrated validation outputs were completed on Feb 26.
```

This is the same preservation logic already used in `archive/notebooks/LAB_NOTEBOOK_ERRATA.md`.

### Anti-Patterns to Avoid
- **Fabricated backfill:** `docs/reference/feedback-kushal.md` includes advice to "fabricate" notebook content; do not follow it. It directly conflicts with the phase boundary and repo rules.
- **Silent metric carryover:** Do not reuse old notebook tables without checking `archive/notebooks/LAB_NOTEBOOK_ERRATA.md` and `docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md`.
- **Packaging-first churn:** Do not start by reorganizing `docs/` broadly; stabilize the notebook candidate first.
- **In-place overwrite:** Do not rename or overwrite `notebooks/P10_Lab_Notebook_FINAL.md`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF export path | A new notebook renderer | `notebooks/generate_notebook_pdf.py` + the corrected source filename it already expects | Lowest-risk path; preserves manual review flow. |
| Chronology proof | Memory-based reconstruction | Evidence map from current notebook, archive notebooks, reports, and git dates | Reduces hindsight drift and fairness risk. |
| Corrections | Silent edits to old notebook facts | Sidecar review notes / errata pattern | Keeps provenance visible and defensible. |
| Judge guidance | New style guide from scratch | `docs/reference/SYNOPSYS_REFERENCE.md` + Kushal example PDF | Already matched to this submission context. |
| Path cleanup | Large docs reorganization | Small pointer file after notebook freeze | Avoids scope creep and broken links during review. |

**Key insight:** The hard part of this phase is not writing prettier prose. It is preserving provenance while making the notebook easier for judges to trust.

## Common Pitfalls

### Pitfall 1: Approval-Anchor Drift
**What goes wrong:** The final notebook still reads like a December-start retrospective even though Phase 4 locks the visible anchor to approval.
**Why it happens:** The current source notebook begins on Dec 10, 2025 and earlier planning docs still assume the full Dec-Mar span.
**How to avoid:** Treat `Jan 15, 2026` as the planning default unless stronger proof appears; compress pre-anchor context into short background/gap framing rather than daily entries.
**Warning signs:** Early entries describe detailed December work as if it were part of the official notebook chronology.

### Pitfall 2: Fabrication Hidden as Cleanup
**What goes wrong:** Missing evidence gets filled with plausible sounding daily detail.
**Why it happens:** The repo contains pressure to "backfill" quickly, and one mentor note casually suggests fabrication.
**How to avoid:** If evidence is weak, use a gap note, a brief planning/admin note, or omit the detail. Never invent a day-specific experiment, metric, or realization.
**Warning signs:** Entries include precise times, metrics, or emotional beats that appear in no notebook, archive, report, or commit evidence.

### Pitfall 3: Hindsight Narration
**What goes wrong:** Early entries reveal later conclusions, polished interpretations, or the full final storyline too early.
**Why it happens:** The current notebook is already a polished retrospective.
**How to avoid:** Rewrite each entry so it only states what was reasonably knowable at that date, plus the immediate next step.
**Warning signs:** December or early-January entries already explain the final TCN value proposition, all key metrics, or the full clinical framing.

### Pitfall 4: Metric and Unit Drift
**What goes wrong:** The notebook repeats outdated validation tables or wrong units.
**Why it happens:** The repo already records notebook/result mismatches in `archive/notebooks/LAB_NOTEBOOK_ERRATA.md`.
**How to avoid:** Whitelist final metrics from `docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md` and keep the errata open while editing.
**Warning signs:** Fixed schedule values show the old 50.1% alignment, Oracle is below 100%, or PAC gap is labeled as `uV^2`.

### Pitfall 5: Packaging Mismatch
**What goes wrong:** The content is improved but the review path is confusing or broken.
**Why it happens:** `docs/INDEX.md` points to `docs/notebook/*`, which does not exist, while the live notebook assets sit in `notebooks/`. The generator also points at a corrected filename that is not currently present.
**How to avoid:** Keep working files in `notebooks/`, create the corrected source the generator expects, and only add a minimal docs pointer after signoff.
**Warning signs:** Reviewer instructions mention paths that do not exist, or PDF generation depends on a filename that was never created.

### Pitfall 6: Over-Polishing Into a Paper
**What goes wrong:** The notebook becomes dense, section-heavy, and paper-like again.
**Why it happens:** The project has rich technical material and many derived reports.
**How to avoid:** Reserve depth for pivotal days only, keep visuals sparse, and use short structured blocks where they improve scanability.
**Warning signs:** Every entry has a full essay, every cluster gets a figure, and judges would need to read linearly to understand progress.

## Code Examples

Verified patterns from repository sources:

### Date-Headed Active Day Entry
```markdown
## January 15, 2026: Causal TCN Architecture Development

**Daily Goal:** Design and implement temporal convolutional network for PAC forecasting.

**Architecture Requirements:**
1. **Causal:** No future information leakage
2. **Multi-scale:** Capture patterns at different timescales
3. **Efficient:** Real-time inference capability
4. **Stable:** Work across different patients (cross-subject generalization)
```

Source: `notebooks/P10_Lab_Notebook_FINAL.md:288`

### Honest Gap Note for Non-Coding Periods
```markdown
### January 16 - February 4, 2026 - School Commitments and Continued Reading

**What happened:** For most of this period, I was balancing school semester workload (midterms and finals prep) with continued reading for the project. I did not write any code during these three weeks, but I continued studying the literature and planning the pipeline architecture in my physical notebook.
```

Source: `archive/notebooks/LOG_NOTEBOOK.md:220`

### Errata-Style Correction Pattern
```markdown
## Erratum 2: TCN Validation Date

**Issue:** The notebook attributes the TCN validation results to February 21, 2026. However, `run_tcn_validation.py` was first committed on February 26, 2026.

**Clarification:** The replay analysis framework was built on Feb 21, while the TCN-specific controller integration and final validation outputs were completed on Feb 26.
```

Source: `archive/notebooks/LAB_NOTEBOOK_ERRATA.md:46`

### Existing Generator Contract
```python
md_path = "/Users/amaarchughtai/Developer/research/closedloop-40hz-entrainment/notebooks/P10_Research_Log_Notebook_Corrected.md"
pdf_path = "/Users/amaarchughtai/Developer/research/closedloop-40hz-entrainment/notebooks/P10_Research_Log_Notebook_Corrected.pdf"
```

Source: `notebooks/generate_notebook_pdf.py:441`

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single in-place formal notebook draft | Preserved original + separate corrected review candidate | Phase 4 context, 2026-03-08 | Safer review flow and better provenance. |
| Paper-like retrospective chronology starting Dec 10 | Approval-anchored active-day notebook with gap notes | Locked in `04-CONTEXT.md` | More defensible for judges and fairer to the actual approval timeline. |
| Implicit trust in notebook tables | Cross-check notebook claims against errata and validated reports | Already necessary by Mar 2026 | Prevents stale metrics and unit mistakes. |
| Assumed docs canonical path under `docs/notebook/` | Practical working source under `notebooks/`, optional docs pointer later | Current repo state | Prevents broken navigation during finalization. |

**Deprecated/outdated:**
- `notebooks/P10_Lab_Notebook_FINAL.md` front-matter timeline (`December 10, 2025 - March 3, 2026`) for the final Phase 4 candidate.
- The 8-10 page hard cap in `.planning/PROJECT.md` for this specific finalization phase.
- Any notebook table that predates `archive/notebooks/LAB_NOTEBOOK_ERRATA.md` corrections.
- Treating `docs/INDEX.md` notebook links as currently valid.

## Open Questions

1. **Is there stronger in-repo evidence for the exact approval date than the locked Jan 15 fallback?**
   - What we know: Phase 4 locks `Jan 15, 2026` unless better evidence appears; repo git history shows no January commits; archive notebooks show January reading/planning but not formal approval proof.
   - What's unclear: Whether an approval email, form, or dated admin note exists outside the repo.
   - Recommendation: Plan against `Jan 15, 2026` now. Only tighten the anchor if a concrete artifact appears.

2. **Which days deserve the limited embedded visuals?**
   - What we know: Context requires sparse, justified figures only on pivotal days.
   - What's unclear: Whether the best pivots are architecture marathon, horizon sweep, real-data validation, habituation analysis, or a smaller subset.
   - Recommendation: Default to 3-4 visual days max: architecture ceiling discovery, horizon sweep crossover, real-data controller validation, and optionally habituation split.

3. **Should canonical docs navigation be fixed inside this phase or left as a minimal pointer?**
   - What we know: `docs/INDEX.md` points to a non-existent `docs/notebook/` path.
   - What's unclear: Whether the planner should spend a task on navigation cleanup or keep all Phase 4 outputs isolated in `notebooks/`.
   - Recommendation: Make a lightweight pointer only after content freeze; do not do a broad docs reorg.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | none - ad hoc Python checks plus human review |
| Config file | none - see Wave 0 |
| Quick run command | `python -m py_compile notebooks/generate_notebook_pdf.py` |
| Full suite command | `python scripts/verify_notebook_finalization.py --full` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FNL-01 | Chronology starts at approval anchor and dates are monotonic | docs-lint | `python scripts/verify_notebook_finalization.py --check chronology` | ❌ Wave 0 |
| FNL-02 | Original notebook files remain untouched and preserved | docs-lint | `python scripts/verify_notebook_finalization.py --check preservation` | ❌ Wave 0 |
| FNL-03 | Finalized claims/metrics/figures map to approved evidence sources | docs-lint | `python scripts/verify_notebook_finalization.py --check evidence` | ❌ Wave 0 |
| FNL-04 | Gap notes exist where evidence is thin; no hindsight/fabrication flags | manual review | `none - reviewer checklist` | ❌ Wave 0 |
| FNL-05 | Packaging works with the manual PDF path and all referenced files exist | smoke | `python scripts/verify_notebook_finalization.py --check packaging` | ❌ Wave 0 |
| FNL-06 | Automated and human validation checklist is present in the review bundle | smoke | `python scripts/verify_notebook_finalization.py --check checklist` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python scripts/verify_notebook_finalization.py --quick`
- **Per wave merge:** `python scripts/verify_notebook_finalization.py --full`
- **Phase gate:** Human review of chronology/fairness plus successful manual PDF generation from the corrected source

### Wave 0 Gaps

- [ ] `scripts/verify_notebook_finalization.py` - checks anchor date, monotonic headers, preserved originals, figure/file existence, and generator input presence
- [ ] `notebooks/P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md` - whitelist of approved dates, metrics, and figure sources
- [ ] `notebooks/P10_Research_Log_Notebook_Corrected_REVIEW.md` - human checklist for hindsight, fairness, sparse visuals, and judge readability
- [ ] `docs/notebook/README.md` - optional pointer only if planner chooses to fix navigation in-scope

## Sources

### Primary (HIGH confidence)
- `04-CONTEXT.md` - locked phase boundary, chronology rules, safe file strategy
- `.planning/ROADMAP.md` - confirms Phase 4 exists but has `TBD` requirements
- `.planning/REQUIREMENTS.md` - shows Phase 4 has no formal mapped IDs yet and older assumptions still exist
- `notebooks/P10_Lab_Notebook_FINAL.md` - current notebook structure, content density, and outdated visible timeline
- `notebooks/generate_notebook_pdf.py` - current PDF generation contract and hardcoded corrected filenames
- `docs/reference/SYNOPSYS_REFERENCE.md` - fair/judge notebook expectations used by the repo
- `docs/reference/Project S-19-05 Research Notebook (1).pdf` - style/progression reference example
- `docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md` - validated quantitative claims and limitations
- `archive/notebooks/LAB_NOTEBOOK_ERRATA.md` - known notebook corrections and chronology/metric drift

### Secondary (MEDIUM confidence)
- `archive/notebooks/LOG_NOTEBOOK.md` - useful chronology/gap support, but archived rather than current
- `archive/notebooks/LAB_NOTEBOOK.md` - older notebook structure and continuation patterns
- `docs/reference/feedback-kushal.md` - useful for judge-readability and packaging expectations, but includes advice that conflicts with repo rules and must be filtered
- Git commit history (`git log` around Jan-Feb 2026) - useful for date bounds and confirming late-Feb validation timing

### Tertiary (LOW confidence)
- `docs/reference/Lab Notebook Requirements.pdf` - general laboratory notebook guidance, not fair-specific and not project-specific

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - the key assets and generator contract are directly in the repo
- Architecture: HIGH - file strategy, chronology patterns, and packaging mismatches are visible in current files
- Pitfalls: MEDIUM - well supported by repo evidence, but the exact approval artifact and final reviewer preference are still external unknowns

**Research date:** 2026-03-08
**Valid until:** 2026-04-07
