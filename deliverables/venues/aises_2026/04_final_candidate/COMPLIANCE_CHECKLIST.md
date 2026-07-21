# COMPLIANCE_CHECKLIST.md — AISES 2026 Student Research Presentations

## A. Authenticity gate (must be TRUE before any drafting)

- [ ] Amaar has personally confirmed, in his own words, a genuine connection to Indigenous community/culture/identity relevant to this project (Section 0 of `QUESTION_BASED_OUTLINE.md`).
- [ ] If no genuine connection exists, this venue has been dropped from the active list — no further checklist items apply.

## B. RED-venue authorship rule (applies regardless of AISES's own AI policy)

- [ ] No AI-drafted sentence appears anywhere in the submitted abstract, poster text, or oral script. AISES's own AI policy could not be located and is treated as UNKNOWN — this campaign's default (human-authored-only) applies until/unless the author finds an explicit permissive policy on the official pages.
- [ ] Every sentence in the submission was typed by Amaar, from his own answers to `QUESTION_BASED_OUTLINE.md`, not copied from `EVIDENCE_PACKET.md` prose.
- [ ] Any fragment marked "ILLUSTRATIVE ONLY" in this workbench has been rewritten, not pasted.
- [ ] Drafts and version history are being kept (per `AI_WRITING_TELLS_AND_AVOIDANCE.md` §6) as evidence of authorship, in case of any detector false-flag.

## C. AI-writing tells self-check (run this pass on the finished draft — see `AI_WRITING_TELLS_AND_AVOIDANCE.md` §7 for the full scan)

- [ ] No more than 1–2 uses total of: delve, underscore, showcase, intricate, pivotal, meticulous, leverage, harness, realm, tapestry, testament, boast, comprehensive, robust.
- [ ] No two consecutive sentences/paragraphs open with Moreover/Furthermore/Additionally.
- [ ] No "It is important to note that," "In today's world," "plays a pivotal role."
- [ ] Sentence lengths vary — at least one short, blunt sentence appears.
- [ ] No promotional adjective ("groundbreaking," "transformative," "cutting-edge") that isn't backed by a stated number.
- [ ] The conclusion says something specific (a next step, a real tradeoff), not just a recap.

## D. Content-accuracy checklist (against canonical numbers — see EVIDENCE_PACKET.md)

- [ ] Static EEGNet: 1,457 params, R² = 0.287 — stated as a practical ceiling, not a shortfall.
- [ ] Five distinct parameter counts exist (four TCN variants plus the static EEGNet) — never collapse them, and never pair a count with a result from a different generation:
  - 1,457 = static EEGNet (R² = 0.287).
  - 22,914 = Gen-A **experimental** 12-feature forecasting TCN (hidden=64) — this is the model behind the feature-ablation result (−0.025 → 0.558 single-seed) and the five-seed mean R² = 0.606 (range 0.558–0.647).
  - 5,154 = a real h=32 architecture-search variant (single-seed test R² ≈ 0.613) — mention only when discussing the architecture search itself; it is NOT the deployed model and NOT the source of 0.606.
  - 27,139 = Gen-B **deployed** integrated controller checkpoint (`models/best_12feat_tcn_lb20_hz5_ts1.pth`) — this is the model behind the controller replay numbers (62.23%/73.77%/50.68%), not behind the 0.606 figure.
  - 31,043 = Gen-C historical 73-feature model — do not use (superseded controller numbers only).
  - **Never write "the 27,139-param model achieves R² = 0.606"** — 0.606 belongs to the 22,914-param Gen-A run.
- [ ] Feature ablation: −0.025 (73 feat) → 0.558 single-seed / 0.606 five-seed mean (12 feat, 22,914-param Gen-A model). Never pair 0.606 with the 0.212 stress-test number as if from the same experiment — they are different experiments (see RESULTS_CANONICAL boundary notes). The 0.212 stress-test figure uses the 27,139-param Gen-B architecture.
- [ ] Controller replay reported as a tradeoff (62.23/73.77/50.68% vs. reactive's 64.49/51.67/77.30%), attributed to the 27,139-param Gen-B checkpoint, not a clean win. Historical 72.1%/82.6%/91%/"35 of 35" figures are NOT used — those belong to a different (73-feature, 31,043-param, Gen-C) checkpoint.
- [ ] No clinical-efficacy, patient-outcome, disease-slowing, prospective-deployment, or "clinical validation" language anywhere. "Retrospective controller replay" / "offline replay" only.
- [ ] Spectral-features-encode-anatomy explanation stated as hypothesis, not fact.
- [ ] Affiliation: Valley Christian High School (author's own school, legitimate). No mentor named unless Amaar supplies verified name/institution/dates/consent — otherwise `[AUTHOR TO CONFIRM]`.

## E. AISES-specific format / logistics checklist

- [ ] Abstract written using AISES's required Indigenous-centered structure (situate-yourself + community-impact section present, honestly, only if Section A gate passed).
- [ ] Abstract addresses, implicitly or explicitly, all Four Strands: Interest in STEM, Engagement & Belonging, STEM Competencies & Confidence, Future Intentions.
- [ ] Submitted before **Priority Deadline 1: Friday, July 24, 2026, 11:59 PM PST**.
- [ ] Do NOT register for the conference before a confirmation/discount code is received post-acceptance (per official AISES instructions).
- [ ] If accepted, registration completed before the Aug 14, 2026 50%-discount cutoff (else pay full registration).
- [ ] Confirm current submission portal / format requirements (poster dimensions, oral time limit, file format) directly on https://conference.aises.org/research/student at time of submission — this workbench was verified 2026-07-16 and formats can change.

## F. Final pre-submission check

- [ ] `FINAL_CANDIDATE_STATUS.md` go/no-go re-confirmed the same day as submission.
- [ ] Nothing in this submission was uploaded, emailed, or submitted by the AI assistant — Amaar performs the actual submission.
