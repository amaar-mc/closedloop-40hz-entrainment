---
phase: 18
slug: lab-notebook-comprehensive-rewrite
created: 2026-04-09
---

# Phase 18 Validation Strategy

## Validation Dimensions

1. **AI Voice Score**: Re-run voice audit agent, must score 95+ on all 6 dimensions
2. **Numerical Accuracy**: Every number in notebook matches JSON/code sources
3. **Code Alignment**: Every code snippet matches actual codebase (grep to verify)
4. **Poster Consistency**: All shared numbers between notebook and poster agree
5. **Clinical Depth**: At least one dedicated clinical context entry with molecular pathways
6. **Imperfection Quotient**: At least 5 genuine corrections/updates/failed attempts documented
7. **Tonal Consistency**: Same voice throughout both files (no break at March boundary)
8. **PDF Generation**: PDF regenerates cleanly with all figures

## Verification Commands

```bash
# Check for em-dashes
grep -c '—' "CSEF/Lab Notebook/P10_Lab_Notebook_VFINAL.md"
grep -c '—' "CSEF_presentation/notebook/v1_lab_notebook_extension.md"
# Both must return 0

# Check code params match
grep "tau_e" src/tribe_v2/neural_mass.py | head -2
grep "onset_tau" src/tribe_v2/cortical_model.py | head -2
# Compare against notebook snippets

# Regenerate PDF
python3 CSEF_presentation/notebook/generate_notebook_pdf.py
# Must complete without errors
```
