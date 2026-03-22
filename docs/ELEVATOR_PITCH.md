    # Elevator Pitch — 1 Minute Script

**Target audience:** CSEF judges, facility administrators, clinicians
**Duration:** ~60 seconds at natural speaking pace (~130 words)
**Framing:** Predictive model for neural state with temporal forecasting — NOT "AI cures Alzheimer's"

---

## The Script

40 Hz gamma oscillations are disrupted in Alzheimer's patients. Restoring them through
non-invasive sound stimulation has shown promising results in animal models and early human
trials.

But current systems are reactive — they stimulate and wait. By the time the brain responds,
the optimal window may have passed. Half of patients habituate within minutes, and a fixed
schedule cannot adapt.

I built a causal temporal convolutional network that predicts where a patient's neural state
will be 5 to 10 seconds in the future — with R-squared of 0.25 where simpler baselines go
negative. The system uses that forecast to stimulate proactively, when it is most effective.

On 35 subjects' real EEG data, the predictive strategy achieved 72% targeting accuracy versus
64% for reactive control — a statistically significant improvement across every single patient.

Scan the QR code to try the live caregiver app. The next step is a formal pilot at a memory
care facility to collect real caregiver feedback.

---

## Timing Map

| Beat | Time | Words |
|------|------|-------|
| Hook — 40 Hz disruption, restoration via sound | ~10s | ~25 |
| Problem — reactive systems, habituation | ~15s | ~35 |
| Solution — causal TCN, 5-10s ahead, R-squared 0.25 | ~20s | ~35 |
| Results — 72% vs 64%, 35 subjects, all benefit | ~15s | ~30 |
| Demo + Next Steps — QR code, pilot at facility | ~10s | ~25 |

---

## Q&A Quick Handles

**"Is this FDA approved?"**

No, this is research-stage. The clinical roadmap includes IND filing and IRB-approved clinical
trials after validating on a larger cohort. Right now the system operates on recorded EEG data
and simulated signals — no live patient treatment without regulatory approval.

**"Does it actually cure Alzheimer's?"**

We are not claiming a cure. We are restoring a disrupted neural rhythm that multiple studies
associate with cognitive function and amyloid clearance. Think of it as a hearing aid for the
brain's synchrony — it does not fix the underlying disease, but it may slow progression and
improve quality of life.

**"Why consumer EEG instead of research-grade hardware?"**

It makes the system accessible. A Muse 2 headset costs $200 and requires no gel or technician.
Research-grade hardware (OpenBCI, then clinical 64-channel caps) is in the scaling roadmap. The
intelligence layer is the same — only the sensor changes. Starting with consumer hardware means
we can deploy in homes and memory care facilities, not just hospitals.

---

## Key Numbers to Have Ready

| Metric | Value | Source |
|--------|-------|--------|
| Alignment (TCN vs Reactive) | 72.1% vs 64.5% | results/RESULTS_REPORT.md |
| Low-PAC targeting | 82.6% vs 51.7% | results/RESULTS_REPORT.md |
| Effect size (alignment) | g = 1.31, p < 0.001 | Hedges' g |
| Oracle proximity | 91% of theoretical best | 30.5 / 33.3 PAC gap |
| Subjects benefiting | 35/35 (100%) | Per-subject scatter |
| TCN R-squared at 5-10s | 0.24-0.28 | models/sweep_horizons_results.json |
| Model size | 1,457 + 31,043 params | EEGNet + TCN |
| Inference latency | < 50ms total | Real-time capable |

---

## Dos and Don'ts

**Do say:**
- "Predictive model for neural state"
- "Temporal forecasting" and "causal architecture"
- "Decision support for therapy scheduling"
- "Validated on real EEG from 35 participants"

**Do not say:**
- "AI cures Alzheimer's"
- "Treatment" (use "stimulation" or "therapy scheduling")
- "Our product" (this is research)
- "We proved" (use "we demonstrated" or "the data shows")
