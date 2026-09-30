# AI-assistance disclosure log

This log records every step where an AI assistant (Claude, via Claude Code) did the work or helped,
so it can be reported under the Society for Science / STS rules on AI use. The student must
understand each step well enough to reproduce it and defend it in an interview.

| Date | Step | What the AI did | What the student must verify or own | Concept to be able to explain |
|---|---|---|---|---|
| 2026-09-30 | Audit | Read the repo code, wrote independent re-analysis scripts (`sts2026/code/audit_*.py`) and drafted `01_AUDIT.md` | Re-run both scripts; open `data_loader.py` l. 399–420 and confirm the whole-block labels | **Label leakage:** a target built from data after the prediction time. **Persistence baseline:** "the future equals now". **Tort MI:** KL divergence of the gamma amplitude distribution over theta phase bins. |
| 2026-09-30 | Literature, STS benchmark, dataset census | Four background research agents searched the web and databases. Every citation is to be checked against Crossref/PubMed. | Spot-check 10 random citations by hand (open the DOI) | **DOI/PMID verification:** confirm the paper exists and its metadata matches |
