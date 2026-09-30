# AI-assistance disclosure log

This log records every step where an AI assistant (Claude, via Claude Code) did the work or helped,
so it can be reported under the Society for Science / STS rules on AI use. The student must
understand each step well enough to reproduce it and defend it in an interview.

| Date | Step | What the AI did | What the student must verify or own | Concept to be able to explain |
|---|---|---|---|---|
| 2026-09-30 | Audit | Read the repo code, wrote independent re-analysis scripts (`sts2026/code/audit_*.py`) and drafted `01_AUDIT.md` | Re-run both scripts; open `data_loader.py` l. 399–420 and confirm the whole-block labels | **Label leakage:** a target built from data after the prediction time. **Persistence baseline:** "the future equals now". **Tort MI:** KL divergence of the gamma amplitude distribution over theta phase bins. |
| 2026-09-30 | Objective | Scored 5 candidates and recommended C1; the **student chose C1** | Be able to say why the AlphaFold and omics options were rejected | **Falsifiability:** a claim that data could prove wrong |
| 2026-09-30 | Pre-registration | Wrote hypotheses, thresholds, exclusions and frozen code (`confirmatory.py`, hash in the pre-registration) before held-out data were analysed | Check the git timestamps: the pre-registration commit precedes the results commit | **Pre-registration:** fixing the analysis before seeing outcomes, to prevent p-hacking. **Held-out data:** data not used to design the method |
| 2026-09-30 | Analysis | Ran the confirmatory, sensitivity and exploratory analyses; found that H4 was a noise proxy | Re-run the scripts; read `06_RESULTS.md`; know which results are confirmatory and which are exploratory | **ITC:** consistency of EEG phase with the stimulus clock, from 0 to 1. **ICC:** share of variance due to stable differences between people. **Permutation test:** shuffle labels to build a null distribution. **Bootstrap CI:** resample people to get uncertainty. **Holm correction:** control for multiple tests. **Partial correlation:** a correlation after removing a third variable (noise) |
| 2026-09-30 | Figures | `make_figures.py` plots values read from the results files | Check each figure against `06_RESULTS.md` | **Negative control:** a measure that should show nothing (33 Hz) |
| 2026-09-30 | Title/abstract | Wrote a 250-word **fact sheet** | **You must write the submitted title and abstract yourself** (STS rule) | — |
| 2026-09-30 | Literature, STS benchmark, dataset census | Four background research agents searched the web and databases. Every citation is to be checked against Crossref/PubMed. | Spot-check 10 random citations by hand (open the DOI) | **DOI/PMID verification:** confirm the paper exists and its metadata matches |

## Binding STS rules on AI (from `02_STS_BENCHMARK.md`; official wording and URLs are in `notes/sts_raw_notes.md`)
- Generative AI may **not** be used to write the STS application questions, to draft the Research Report, or to generate citations. Using AI tools in the research itself is allowed, but it must be disclosed and cited.
- **Consequences for this workspace:**
  1. Every prose deliverable written here (audit, memo, abstract, title) is a **research note or fact sheet only**. The student must write the submitted report, abstract and title in their own words.
  2. The literature table is a search aid. The student must open and read every reference they cite and check it themselves.
  3. Every script in `sts2026/code/` was written with AI assistance and says so in its header. The prompt log is this session transcript; export it and keep it.
