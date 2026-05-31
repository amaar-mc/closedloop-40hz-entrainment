---
source_file: "temporal_multiscale/transition_analysis.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L117"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Fallback: reconstruct stim states from BIDS events.tsv.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[_stim_states_from_events()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features