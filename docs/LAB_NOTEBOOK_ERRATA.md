# Lab Notebook Errata

These corrections apply to `docs/LAB_NOTEBOOK.md`. The original notebook is preserved as-is (per lab notebook best practice of never erasing entries). This errata document records corrections identified during a cross-reference audit against commit history and the verified RESULTS_REPORT.md.

---

## Erratum 1: Controller Results Table (p. 52, Study 10)

**Location:** Study 10, "Real-Data TCN Validation" section, results table on page 52

**Original entry (in notebook):**

| Controller | Alignment | Low-PAC Targeting | PAC Gap (uV^2) | Stim % |
|-----------|-----------|-------------------|----------------|--------|
| Fixed Schedule | 50.1% | 33.2% | 15.3 | 66.7% |
| Reactive Threshold | 64.5% | 51.7% | 21.1 | 34.5% |
| Multi-Biomarker | 62.8% | 49.3% | 19.7 | 21.3% |
| Phase-Aware | 63.1% | 50.1% | 20.2 | 36.4% |
| TCN Predictive | 72.1% | 82.6% | 30.5 | 42.7% |
| Oracle | 78.4% | 91.3% | 33.5 | 49.0% |

**Corrected values (from final `run_tcn_validation.py` output, verified in `results/RESULTS_REPORT.md`):**

| Controller | Alignment | Low-PAC Targeting | PAC Gap (x10^-6) | Stim % |
|-----------|-----------|-------------------|-------------------|--------|
| Fixed Schedule | 45.0% | 61.4% | -6.6 | 66.6% |
| Reactive Threshold | 64.5% | 51.7% | +21.1 | 36.7% |
| **TCN Predictive** | **72.1%** | **82.6%** | **+30.5** | **59.7%** |
| Oracle | 100.0% | 100.0% | +33.3 | 48.3% |

**What changed:**
- Fixed Schedule alignment dropped from 50.1% to 45.0% (earlier version used different alignment definition)
- Fixed Schedule Low-PAC Targeting changed from 33.2% to 61.4% (metric definition updated)
- Fixed Schedule PAC Gap changed from +15.3 to -6.6 (corrected to show the gap is in the WRONG direction)
- Oracle changed from 78.4%/91.3% to 100%/100% (corrected Alignment Oracle definition: perfect knowledge = 100%)
- TCN Stim % changed from 42.7% to 59.7% (updated controller implementation)
- Reactive Stim % changed from 34.5% to 36.7% (minor recalculation)
- Multi-Biomarker and Phase-Aware controllers removed from poster (simplified for presentation)

**Reason:** The notebook's table reflects an earlier version of `run_tcn_validation.py` that used different metric definitions and controller implementations. The final version (commit 34c3ac2, Feb 26) corrected the alignment definition and oracle implementation. The TCN Predictive and Reactive Threshold core comparison numbers (72.1% vs 64.5%, 82.6% vs 51.7%, 30.5 vs 21.1) are consistent between both versions.

**The key claims are unaffected:** TCN vs Reactive effect sizes (g=1.31, g=4.47, g=1.57), 35/35 subject consistency, and all p-values remain the same.

---

## Erratum 2: TCN Validation Date

**Location:** Study 10, page 52 header — "February 21, 2026"

**Issue:** The notebook attributes the TCN validation results to February 21 evening. However, `run_tcn_validation.py` was first committed on February 26, 2026 (commit 34c3ac2). The February 21 commits include replay analysis scripts and architecture experiments, but the specific TCN-integrated validation (producing the 72.1% alignment result) was developed and run on February 26.

**Clarification:** The Study 10 entry conflates work done across Feb 21-26. The replay analysis (commit 4140775, Feb 21) and rigorous statistical framework (commit d65d690, Feb 21) were indeed developed on Feb 21. The TCN-specific controller integration and epoch-level validation were completed on Feb 26 (commits 6e575d3, 34c3ac2, beeddf7). The notebook was likely written or updated after the full validation was complete, and the Feb 21 date reflects when the validation *framework* was built, not when the final TCN results were produced.

---

## Erratum 3: PAC Gap Units

**Location:** Multiple tables throughout the notebook

**Issue:** PAC Gap is labeled as "uV^2" in some tables. The Tort Modulation Index is dimensionless (a normalized KL divergence). The values (e.g., 30.5) are in units of x10^-6 (dimensionless), not microvolts squared.

**Correction:** All PAC Gap values should be read as dimensionless x10^-6, not as µV².

---

*Errata compiled: March 4, 2026*
*Source: Cross-reference audit of LAB_NOTEBOOK.md against commit history and RESULTS_REPORT.md*
