---
source_file: "results/rigor_audit/07_leakage_audit.md"
type: "document"
community: "Rigor Audit Reports"
tags:
  - graphify/document
  - graphify/EXTRACTED
  - community/Rigor_Audit_Reports
---

# Data Leakage Audit (7/7 checks pass, no leakage)

## Connections
- [[Epoch-Level PAC Granularity Caveat (82% same-epoch pairs)]] - `references` [EXTRACTED]
- [[Model Architecture Deep Dive Phase (Phase 3)]] - `references` [EXTRACTED]
- [[PAC Feature Circular Leakage Check (pac_current R2=0.104, matches persistence)]] - `references` [EXTRACTED]
- [[Permutation Test (shuffled R2=-0.004 vs real R2=0.734, genuine signal confirmed)]] - `references` [EXTRACTED]
- [[Rigor Audit Synthesis (HIGH overall confidence, results genuine and reproducible)]] - `references` [EXTRACTED]
- [[Subject-Level Split Disjointness Check (0 overlap across trainvaltest)]] - `references` [EXTRACTED]
- [[Temporal Causality Check (target_idx - end_idx == 5, 0 violations)]] - `references` [EXTRACTED]
- [[Z-Score Scalers Fit on Train Only Verification]] - `references` [EXTRACTED]

#graphify/document #graphify/EXTRACTED #community/Rigor_Audit_Reports