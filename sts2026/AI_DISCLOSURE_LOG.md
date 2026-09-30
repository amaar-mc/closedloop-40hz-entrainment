# AI-assistance disclosure log

This log records every step where an AI assistant (Claude, via Claude Code) did the work or helped,
so it can be reported under the Society for Science / STS rules on AI use. The student must
understand each step well enough to reproduce it and defend it in an interview.

| Date | Step | What the AI did | What the student must verify or own | Concept to be able to explain |
|---|---|---|---|---|
| 2026-09-30 | Audit | Read the repo code, wrote independent re-analysis scripts (`sts2026/code/audit_*.py`) and drafted `01_AUDIT.md` | Re-run both scripts; open `data_loader.py` l. 399–420 and confirm the whole-block labels | **Label leakage:** a target built from data after the prediction time. **Persistence baseline:** "the future equals now". **Tort MI:** KL divergence of the gamma amplitude distribution over theta phase bins. |
| 2026-09-30 | Literature, STS benchmark, dataset census | Four background research agents searched the web and databases. Every citation is to be checked against Crossref/PubMed. | Spot-check 10 random citations by hand (open the DOI) | **DOI/PMID verification:** confirm the paper exists and its metadata matches |

## Binding STS rules on AI (from `02_STS_BENCHMARK.md`; official wording and URLs are in `notes/sts_raw_notes.md`)
- Generative AI may **not** be used to write the STS application questions, to draft the Research Report, or to generate citations. Using AI tools in the research itself is allowed, but it must be disclosed and cited.
- **Consequences for this workspace:**
  1. Every prose deliverable written here (audit, memo, abstract, title) is a **research note or fact sheet only**. The student must write the submitted report, abstract and title in their own words.
  2. The literature table is a search aid. The student must open and read every reference they cite and check it themselves.
  3. Every script in `sts2026/code/` was written with AI assistance and says so in its header. The prompt log is this session transcript; export it and keep it.
