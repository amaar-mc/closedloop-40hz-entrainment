# IEEE EMBC — Formatting Notes

**Full name:** IEEE Engineering in Medicine and Biology Conference
**Typical deadline:** January–February (check current year)
**Notification:** ~March
**Camera ready:** ~April

## Format

- **Page limit:** 4 pages + 1 page references
- **Template:** IEEE two-column (`IEEEtran.cls`)
- **Review:** Double-blind (anonymize author names, institution)
- **Supplementary:** Not standard; check CFP

## LaTeX setup

```bash
# Template available from IEEE:
# https://www.ieee.org/conferences/publishing/templates.html
# File: IEEEtran_HOWTO.pdf + IEEEtran.cls

\documentclass[conference]{IEEEtran}
```

## Word limits (approximate for 4 pages)

- Abstract: ≤ 200 words
- Body: ~3,000–3,500 words total (4 pages two-column is tight)
- References: up to 1 additional page

## Citation style

IEEE numbered `[1]`, `[2]` etc. Use `IEEEtran.bst`.

## Key sections expected

1. Abstract
2. Introduction
3. Methods / Materials
4. Results
5. Discussion / Conclusion
6. References

Architecture search + feature ablation may need to be merged into Methods to fit 4 pages.

## Blind review checklist

- Remove author names and affiliations from manuscript
- Remove acknowledgements until camera-ready
- No self-identifying references ("In our previous work [X]...")
- Check PDF metadata for author names
