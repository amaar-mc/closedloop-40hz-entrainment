# Figures — Source Scripts

Scripts here generate publication-quality figures for the conference paper.
Run from the repo root with the venv active.

## Existing figures (already generated — in results/figures/)

| Figure                | Script                                        | Output                                          |
| --------------------- | --------------------------------------------- | ----------------------------------------------- |
| Horizon sweep         | `scripts/figures/horizon_sweep_pac_stim.py`   | `results/figures/horizon_sweep.pdf`             |
| Controller comparison | `scripts/figures/generate_figures.py`         | `results/figures/controller_comparison_v2.pdf`  |
| PAC targeting gap     | `scripts/figures/generate_figures.py`         | `results/figures/pac_targeting_gap.pdf`         |
| Per-subject utility   | `scripts/figures/generate_figures.py`         | `results/figures/per_subject_utility.pdf`       |
| Threshold sensitivity | `scripts/figures/generate_figures.py`         | `results/figures/threshold_sensitivity.pdf`     |
| Timeline example      | `scripts/figures/generate_timeline_figure.py` | `submission/paper/figures/timeline_example.pdf` |

## Figures still needed for conference paper

| Figure                             | Status                             | Notes                                                           |
| ---------------------------------- | ---------------------------------- | --------------------------------------------------------------- |
| Feature ablation table / bar chart | TODO                               | Visualize the 73 → 12 feature R² jump                           |
| System pipeline diagram (clean)    | exists (submission/paper/figures/) | May need updated version with Stage 1 + Stage 2 clearly labeled |
| Architecture search comparison     | TODO                               | Bar chart: 8 models × R²; show size irrelevance                 |

## Figure style guide

- Use `matplotlib` with `seaborn` styling
- Color palette: match existing figures (blue=TCN, orange=reactive, gray=fixed, green=oracle)
- Font: 11pt for axes, 13pt for titles, match IEEE two-column body text size
- Export as both `.pdf` (vector) and `.png` (300 dpi) for flexibility
- All figures must be self-contained with captions
