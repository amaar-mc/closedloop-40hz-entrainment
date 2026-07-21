# Submission Workspace — Organization & How-To-Use Report

**Generated:** 2026-07-03 · **Project:** closedloop-40hz-entrainment (retrospective EEG/PAC forecasting & offline replay)
**Scope:** conference/competition submission tracking, document organization, and research support for the 2026–2027 application cycle.

---

## 1. What this system is

A single, editable source of truth (`submission_tracker.json`) drives an interactive dashboard, a
git-diffable Markdown mirror, in-place status labels on every submission document, a master manifest,
and two grounded research guides. You edit **one JSON file**, run **one build command**, and every
view regenerates. Nothing is hand-maintained in two places.

It covers **17 venue tracks** across high-school research competitions, IEEE/professional conferences,
and poster/identity symposia — prioritized by a transparent scoring model, staged through an 11-gate
research workflow, and annotated with per-venue acceptance intelligence and tailoring levers.

---

## 2. Where everything lives

All paths are relative to `paper/conferences/` in the repo.

```
paper/conferences/
├── SUBMISSION_MANIFEST.md            ← master index of every submission doc (auto-generated)
├── CONFERENCE_APPLICATION_MATRIX_2026.md   (pre-existing narrative matrix — still valid background)
├── _tracker/                         ← THE TRACKER SYSTEM
│   ├── submission_dashboard.html     ← open this in a browser (interactive, self-contained)
│   ├── TRACKER.md                    ← Markdown mirror for git diffing / quick reading
│   ├── submission_tracker.json       ← ★ SINGLE SOURCE OF TRUTH — edit this
│   ├── WORKFLOW_SYSTEM.md            ← the 11-gate stage-gate model, defined
│   ├── research/
│   │   ├── AI_WRITING_TELLS_AND_AVOIDANCE.md   ← what makes writing read as AI-generated + how to avoid it
│   │   └── VENUE_INTELLIGENCE.md              ← per-venue "what gets in" + tailoring levers
│   └── tracker_tools/                ← the generators (Python, stdlib only)
│       ├── build_tracker.py          ← rebuilds dashboard + TRACKER.md from the JSON
│       ├── bootstrap_tracker_data.py ← (re)generates the JSON from scratch if ever needed
│       ├── label_docs.py             ← injects status headers + _STATUS.md + manifest
│       ├── patch_intel.py            ← folds venue intelligence into the JSON
│       └── dashboard_template.html   ← HTML/CSS/JS shell (data injected at build)
├── tailored_submissions_2026/        ← 16 venue folders, each with drafts + a _STATUS.md
│   └── <venue>/
│       ├── _STATUS.md                ← per-venue status snapshot (auto-generated)
│       ├── SUBMISSION_DRAFT.md       ← labeled with a status header block
│       └── ... (poster layouts, blueprints, scripts — all labeled)
└── mit_urtc_2026/                    ← MIT URTC manuscript + audits (+ its own _STATUS.md)
    └── draft/MANUSCRIPT.md           ← the source manuscript (labeled)
```

**Counts (verified 2026-07-03):** 17 venue tracks · 31 labeled submission documents · 17 `_STATUS.md`
files · 1 master manifest · 33 total referenced files (31 text docs + 2 binaries: the URTC `.docx`/`.pdf`).

---

## 3. The workflow system (11 gates, G0–G10)

Researchers don't write a paper in one pass — they cycle through drafting, independent review, and
claim/compliance auditing, often twice. This system encodes that as an explicit stage-gate pipeline.
Full definitions are in `_tracker/WORKFLOW_SYSTEM.md`; the summary:

| Gate    | Name                     | What "done" means                                       |
| ------- | ------------------------ | ------------------------------------------------------- |
| **G0**  | Outline                  | Structure + section skeleton agreed                     |
| **G1**  | Draft                    | Full first draft of the venue artifact exists           |
| **G2**  | Review 1 (content)       | Substantive content/clarity review completed            |
| **G3**  | Audit 1 (claim/evidence) | Every claim checked against `paper/data/key_results.md` |
| **G4**  | Review 2 (reviewer sim)  | Read as a venue reviewer would; weaknesses surfaced     |
| **G5**  | Audit 2 (compliance)     | Format/eligibility/integrity rules verified             |
| **G6**  | Copyedit + AI-tell pass  | Line edit + `AI_WRITING_TELLS` checklist applied        |
| **G7**  | Production               | Converted to the venue's required format, proofed       |
| **G8**  | Final QA                 | Last read; limits/counts/links confirmed                |
| **G9**  | Submitted                | Actually submitted through the venue portal/email       |
| **G10** | Decision                 | Outcome recorded (accept/reject/waitlist)               |

**Work gates are G0–G8** (the writing/review/audit effort). G9–G10 are terminal states. Progress % is
computed as `round(100 × (done + 0.5 × in_progress) / considered)` over the work gates, with `n/a`
gates excluded. Every venue's per-gate state lives in the JSON and renders as a segmented progress bar.

---

## 4. Priority ranking — how venues are ordered

Each venue gets a **composite score** from four weighted factors, then an **effective score** that
demotes venues you can't actually act on:

- **Composite** = `0.35·urgency + 0.25·fit + 0.25·college_value + 0.15·feasibility`
  - _urgency_ is derived from days-to-deadline (≤14d = 100, ≤30d = 88, ≤60d = 72, ≤120d = 52, >120d = 36,
    unposted = 40, passed = 8).
  - _fit_, _college_value_, _feasibility_ are editorial 1–5 ratings × 20.
- **Effective** = `composite × actionability`, where actionability = `ok 1.0 · conditional/monitor 0.8 · blocked 0.45`.
  This is why a technically strong but **blocked** venue (e.g. MIT URTC _paper_ track, raw 70.0) sorts
  below real, eligible targets (effective 31.5) — the ranking reflects what you can actually pursue, while
  the raw composite stays visible so nothing is hidden.

**Current top of the board (effective score):**

1. **BMES 2026 HS Poster Expo** — 85.2 · deadline 2026-08-18 · eligible now · _the strongest near-term actionable target_
2. **Regeneron STS 2027** — 71.6 · window to 2026-11-05 · highest college-app upside
3. **MIT URTC 2026 (poster/lightning)** — 71.0 · MIT-branded, eligible route
4. **JSHS NorCal 2027** — 68.0 · strong HS research competition
5. **Synopsys Championship 2027** — 63.0 · local fair → ISEF pathway

Blocked/skip (kept for transparency, demoted): MIT URTC _paper_ (needs real university affiliation),
SACNAS (age/level eligibility), BMES _general abstract_ (grad/professional pool).

---

## 5. How to use it — daily workflow

**To view status:** open `_tracker/submission_dashboard.html` in any browser. It's fully self-contained
(no server, no internet). Filter by eligibility, deadline window, or search; sort by priority, deadline,
or progress; expand any card for gates, acceptance signals, tailoring levers, blockers, and file links.
Deadline countdowns recompute live from the current date each time you open it.

**To update status** (the only editing you do):

1. Open `_tracker/submission_tracker.json`.
2. Edit the venue's `gates` (set a gate to `done` / `in_progress` / `todo` / `blocked` / `na`), or
   update `deadline`, `notes`, `eligibility_status`, `fit`/`college_value`/`feasibility`, etc.
3. Rebuild:
   ```bash
   cd paper/conferences/_tracker
   python tracker_tools/build_tracker.py      # regenerates dashboard + TRACKER.md
   ```
4. If document _statuses_ changed, refresh the headers/manifest:
   ```bash
   python tracker_tools/label_docs.py --apply --repo-root ../../..
   ```
   (Idempotent — safe to re-run; only changed files are rewritten.)

**Never hand-edit** `submission_dashboard.html`, `TRACKER.md`, the `_STATUS.md` files, the manifest, or
the in-document status headers — they are all generated and will be overwritten on the next build.

---

## 6. The research guides (use these while writing)

**`research/AI_WRITING_TELLS_AND_AVOIDANCE.md`** — a grounded guide to what makes writing read as
AI-generated (lexical crutches, uniform rhythm, hollow structure, epistemic over-hedging, fabricated
citations), _why_ it happens, and concrete practices to avoid it. Includes a 5-minute red-flag scan.
Grounded in 8 verified sources (Kobak et al. on excess vocabulary; Stanford/Liang on detector bias
against non-native writers; Walters & Wilder on GPT citation fabrication). **Give this to anyone
drafting venue text** — but note detectors are unreliable, so the goal is genuinely good writing, not
"beating a detector." At STS and JSHS, AI-drafted text is prohibited outright; there, use it as a
self-review checklist for human-authored prose only.

**`research/VENUE_INTELLIGENCE.md`** — per-venue "what actually gets in": the rubric or judging process,
traits of selected work, format/logistics, the real eligibility blocker, common rejection reasons, and
3–6 concrete tailoring levers per venue — all inside the project's claim boundaries. Confidence is
flagged HIGH/MEDIUM/LOW per venue (HIGH = grounded in the venue's official rubric page). The same
acceptance signals + tailoring levers are embedded in the dashboard cards.

---

## 7. Claim boundaries (enforced everywhere)

Every draft, tailoring lever, and piece of intelligence respects these non-negotiable boundaries, drawn
from `paper/data/key_results.md` and the MIT URTC `CLAIM_AUDIT.md`:

1. Use **retrospective controller replay** / **offline replay** — never "clinical validation."
2. **No** claims of clinical efficacy, patient benefit, disease slowing, prospective deployment, or live therapy.
3. Keep event-summary and backward-looking PAC results **separate**; state the target definition when quoting a metric.
4. **Do not** claim the TCN beats Ridge under the backward-looking target (R² ≈ 0.212 vs 0.216 — a tie).
5. Report persistence + Ridge baselines next to any TCN forecasting claim.
6. **Never** list a mentor, lab, university, or affiliation unless it is real and specific to this work.

These are stored in `submission_tracker.json → project.claim_boundaries` and shown in the dashboard legend.

---

## 8. Document status vocabulary

Every submission document carries an in-place status header (between `<!-- SUBMISSION-STATUS -->`
sentinels) classifying it as one of:

- **FINAL** — submitted or submission-ready in the required format.
- **DRAFT** — active working draft, human-editable, being moved through the gates.
- **SCAFFOLD** — planning-only structure for venues where AI-drafted text is prohibited (STS, JSHS).
  The final text **must be written by the student**; the scaffold is a thinking aid, not submittable prose.
- **REFERENCE** — supporting material (layouts, blueprints, checklists, scripts) that informs a submission
  but isn't itself the submitted artifact.

The header also shows priority rank, current gate, progress %, integrity flags, and deadline. `_STATUS.md`
in each folder summarizes that venue's whole document set at a glance.

---

## 9. Honest limitations of this system

- **Dates drift.** Several 2027 cycles aren't posted yet; the tracker uses best-known/working dates flagged
  in `deadline_note`. **Always re-verify against the official page before submitting.**
- **Editorial scores are judgments.** `fit`, `college_value`, and `feasibility` are considered ratings, not
  measured quantities — adjust them in the JSON as your situation changes.
- **Venue intelligence confidence varies.** LOW/MEDIUM-confidence venues (e.g. BCI Meeting, SfN specifics)
  should be re-checked at submission time; HIGH-confidence entries are grounded in official rubric pages.
- **This is a planning-and-tracking system, not an auto-submitter.** It organizes and prioritizes the work;
  the actual writing, eligibility confirmation, form completion, and submission remain human tasks.
- **Eligibility is the recurring blocker, not merit.** For an independent high-school author, the most
  common reason a strong-fit venue is demoted is an affiliation/age/level rule — route to the eligible track.

---

## 10. Provenance note (how this was built)

The AI-writing-tells guide and venue intelligence were researched via web search against official venue
pages and peer-reviewed sources, then written and cross-checked against the repository's own claim
boundaries. (A parallel sub-agent research team was planned, but delegation was unavailable for part of
the session, so the research was completed directly — same sources, same grounding standard.) All
numeric project results trace to `paper/data/key_results.md`; no metric in any draft or tailoring note
was invented. Deadlines and rubric details carry confidence flags and should be re-verified at submission.

---

## Quick reference — the two commands you'll actually run

```bash
cd paper/conferences/_tracker

# 1. after editing submission_tracker.json — rebuild the dashboard + markdown mirror
python tracker_tools/build_tracker.py

# 2. after a document's status changes — refresh headers, _STATUS.md, and the manifest
python tracker_tools/label_docs.py --apply --repo-root ../../..
```

Open `submission_dashboard.html` to work. Edit `submission_tracker.json` to update. Rebuild. That's it.
