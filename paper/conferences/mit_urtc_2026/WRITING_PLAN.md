# Five-Page Manuscript Writing Plan

This plan is active. The first integrated manuscript draft is stored at
[`draft/MANUSCRIPT.md`](draft/MANUSCRIPT.md).

## Narrative

The manuscript should lead with the generalization result: a compact causal TCN using PAC trajectory
and stimulation-context features predicts future entrainment better than a larger candidate feature
set that includes spectral inputs. The controller replay is a downstream diagnostic. It shows that
strong forecasting does not automatically yield a better balanced controller objective: the final
checkpoint improves low-PAC targeting but reduces high-PAC rest specificity.

## Proposed Page Budget

| Content | Approximate space |
|---|---|
| Title, author block, abstract | 0.45 page |
| Introduction and related work | 0.70 page |
| Data, PAC computation, split strategy, and model | 1.35 pages |
| Offline controller-replay methodology | 0.65 page |
| Results with compact figures and table | 1.35 pages |
| Limitations, conclusion, and references | 0.50 page |

## Drafting Order

1. Lock claims against [`EVIDENCE_MAP.md`](EVIDENCE_MAP.md).
2. Write methods first, including subject-level splits, causal indexing, and train-only normalization.
3. Write the results section from machine-readable metrics and the claim-generation audit.
4. Write limitations before the conclusion so offline replay boundaries are explicit.
5. Write the abstract last. Keep it below the official 500-word ceiling and include the problem,
   method, strongest quantitative results, and bounded conclusion.
6. Compress figures and prose to the five-page limit only after the technical story is complete.

## Abstract Quality Standard

The abstract should be self-contained and quantitative. It should state:

- Why fixed stimulation schedules are a limitation.
- What was evaluated: a causal 12-feature TCN and offline replay on 35 subjects.
- The strongest generalization result and the controller targeting-specificity tradeoff.
- The key limitation: this is retrospective replay, not a clinical efficacy study.
