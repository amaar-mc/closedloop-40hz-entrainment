# Lab Notebook Preparation Guide

Your notebook isn't mandatory at CSEF, but bringing one demonstrates rigor. Some judges will ask to see it. Make it easy for them to find what they need.

---

## What Judges Want to See

1. **Chronological entries** with dates -- shows the project progressed over time, not in one weekend
2. **Design decisions** documented as they happened -- "tried X, it didn't work because Y, pivoted to Z"
3. **Dead ends** recorded -- the 8-architecture search, the spectral feature failure. These show real scientific process.
4. **Data processing steps** -- what you did to the raw EEG and why
5. **Results logged when they happened** -- not all written up at the end
6. **Handwritten annotations** where possible -- even just sticky notes or margin notes on printed pages show personal engagement

## How to Organize (Tab System)

Use sticky tabs to mark key sections. A judge should be able to flip to any of these in 5 seconds:

| Tab Color | Section | Key Content |
|-----------|---------|-------------|
| Red | Literature Review | Iaccarino, Murdock, Lahijanian -- key papers with notes |
| Orange | Data Pipeline | Preprocessing steps, PAC computation, feature engineering |
| Yellow | Architecture Search | 8 models tested, convergence at 0.287, the ceiling realization |
| Green | Feature Discovery | 73 -> 12 features, spectral vs. PAC ablation results |
| Blue | TCN Training | Hyperparameters, training curves, multi-seed results |
| Purple | Controller Validation | 6 controllers compared, 35-subject results, statistical tests |
| Pink | Future Work | Clinical trial design, regulatory notes, product concept |

## Critical Entries to Include

### Early Entries (January-February 2026)
- Literature review notes on 40 Hz therapy
- Dataset selection process (why ds005048)
- Initial preprocessing pipeline decisions
- PAC computation implementation notes

### The Turning Point (Late February)
- 8-architecture comparison results table
- **The realization entry** -- document the moment you understood 0.287 was a data ceiling, not a model problem. This is one of the most impressive parts of the project. Make sure it's in the notebook.
- Decision to pivot to temporal prediction

### Feature Discovery (March)
- Initial 73-feature model results (negative R2)
- Val-test gap analysis
- Feature ablation systematic results
- **The "aha" entry** -- when you realized spectral features were the problem
- 12-feature model results (0.60)
- Multi-seed validation

### Validation (March-April)
- Controller comparison design
- Statistical test selection (why Wilcoxon, why Hedges' g)
- Per-subject results
- Fatigue sensitivity analysis

## If Your Notebook Is Digital

The existing `CSEF/Lab Notebook/P10_Lab_Notebook_VFINAL.md` can be printed. Format:
- Print double-sided
- Use a 3-ring binder or spiral binding
- Add handwritten sticky notes to key pages ("This was the turning point" etc.)
- Date every section clearly

## If a Judge Asks to See It

- "Of course. What would you like to see? I have tabs for each major phase."
- Hand it to them oriented correctly. Point to the relevant tab.
- Let them browse. Don't narrate every page.
- If they ask about a specific entry: explain the context and what you were thinking at that point.

## What NOT to Include
- AI conversation logs (keep these separate if needed for disclosure)
- Unrelated notes or homework
- Overly polished entries that look written after the fact
- Anything that contradicts your poster or presentation
