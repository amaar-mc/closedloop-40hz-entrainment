# Submission Workflow System — Stage-Gate Pipeline (G0 → G10)

**Purpose.** One explicit, researcher-grade pipeline that every submission passes through, so
"status" always means the same thing across 17 venues. Modeled on how research groups actually run
a manuscript to submission: draft → review → audit → second review → second audit → copyedit →
production → final QA. Each stage is a **gate** with an explicit pass criterion; a submission does
not advance until the gate's criterion is met.

The gates are the single vocabulary used by `submission_tracker.json`, the HTML dashboard, the
Markdown mirror, and every per-file status header.

## The Gates

| Gate    | Name                      | What happens                                                                | Pass criterion                                                                              |
| ------- | ------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **G0**  | Outline                   | Lock scope, required components, venue-fit structure                        | Section skeleton + component checklist matches the venue call                               |
| **G1**  | Draft                     | Complete first draft of every required component                            | All components drafted end to end; no `[TODO]` in body                                      |
| **G2**  | Review 1 (content)        | Fresh read for narrative, structure, clarity                                | Story arc / flow / clarity issues logged and resolved                                       |
| **G3**  | Audit 1 (claim/evidence)  | Trace every claim & number to `key_results.md` / repo artifacts             | Claim→evidence map complete; no unsourced number; no cross-generation mixing                |
| **G4**  | Review 2 (reviewer sim)   | Adversarial peer-review read simulating the venue's reviewers               | Reviewer objections fixed or explicitly acknowledged as limitations                         |
| **G5**  | Audit 2 (compliance)      | Format, length, eligibility, integrity, claim-boundary check                | Limits met; eligibility satisfied; no fabricated affiliation; retrospective boundaries held |
| **G6**  | Copyedit + AI-tell pass   | Line editing + removal of AI-generated-writing tells                        | Passes `AI_WRITING_TELLS_AND_AVOIDANCE.md`; human voice; grammar clean                      |
| **G7**  | Production (format/proof) | Convert to the venue's required artifact (PDF/DOCX/portal/poster) + figures | Final artifact renders correctly with figures/refs                                          |
| **G8**  | Final QA gate             | Portal fields, attachments, signatures, disclosures, last site refresh      | Everything submission-ready; official site re-checked                                       |
| **G9**  | Submitted                 | Submitted; confirmation captured                                            | Confirmation ID / email archived                                                            |
| **G10** | Decision                  | Outcome recorded                                                            | Accept / reject / revise / withdraw + feedback recorded                                     |

**Work gates** = G0–G8 (these count toward the progress bar). **G9** is the finish line; **G10** is
outcome tracking.

## Gate status values

Each gate for each venue is one of:

- `done` — criterion met.
- `in_progress` — actively being worked.
- `todo` — not started.
- `blocked` — cannot proceed (records _why_ in the venue's `blockers`).
- `na` — not applicable for this venue/track (excluded from the progress denominator).

## Progress metric

`progress.pct = round(100 × (done + 0.5 × in_progress) / work_gates_considered)` over G0–G8, with
`na` gates removed from the denominator. In-progress counts as half credit so the bar moves as work
advances, not only when a gate flips to done.

`current_gate` = the first work gate that is not `done`/`na`. A `blocked` gate that is the frontier
shows as the current gate, which is exactly the "what is stopping me" signal you want.

## Priority score (why the list is ordered the way it is)

Two numbers per venue:

1. **composite (raw desirability, 0–100)** = weighted sum of four 0–100 sub-scores:
   - `urgency` (0.35) — from days-to-deadline (≤14d = 100, ≤30d = 88, ≤60d = 72, ≤120d = 52,
     > 120d = 36, unposted = 40, passed = 8).
   - `fit` (0.25) — editorial 1–5 topic/venue fit ×20.
   - `college_value` (0.25) — editorial 1–5 college-application value ×20.
   - `feasibility` (0.15) — editorial 1–5 readiness / few-blockers ×20.
2. **effective = composite × actionability**, where actionability = `ok` 1.0, `conditional`/`monitor`
   0.8, `blocked` 0.45.

**Venues are ranked by `effective`.** This stops a blocked or ineligible venue from outranking a real
target just because its deadline is near. The raw `composite` stays visible so you can see a venue's
underlying desirability independent of whether you can act on it right now.

## How to update status

`submission_tracker.json` is the **single source of truth**. To change anything:

1. Edit the venue's `gates` (set a gate to `done`/`in_progress`/`blocked`/`na`), `blockers`,
   `eligibility_status`, `deadline`, or `notes` in `submission_tracker.json`.
2. Re-run `python conf_tracker/tracker_tools/build_tracker.py` to regenerate the HTML dashboard and
   the Markdown mirror from the JSON. (Progress %, current gate, and priority re-derive automatically.)

Do **not** hand-edit the dashboard HTML or `TRACKER.md` — they are generated artifacts. Edit the JSON.

## Claim boundaries (enforced at G3 and G5)

Carried in `submission_tracker.json → project.claim_boundaries`, applied to every venue:

- Use "retrospective", "offline replay", "target-definition audit", "scalar frontal EEG timing target".
- No therapy / clinical validation / patient benefit / prospective deployment / disease-slowing claims.
- Do not claim the TCN beats Ridge under the backward-looking PAC target.
- Keep event-summary and backward-looking PAC results separate; never mix controller generations.
- No mentor / university / lab / affiliation unless real and specific to this work.
- STS and JSHS drafts are planning scaffolds only; final text must be human-authored per venue rules.
