# Project Overview

## Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease

### What This Is

This project develops and validates a machine learning system that predicts when a person's brain will lose gamma entrainment during 40 Hz auditory stimulation, enabling adaptive scheduling that delivers stimulation only when it is needed. The system replaces fixed one-size-fits-all protocols with a personalized, predictive controller that achieves 91% of theoretically optimal performance across all 35 patients tested.

### The Problem

40 Hz gamma entrainment therapy is among the most promising non-pharmacological interventions for Alzheimer's disease. External 40 Hz stimulation (light or sound) drives the brain to oscillate at gamma frequency, triggering microglial clearance of amyloid-beta plaques and restoring network connectivity. Clinical trials have demonstrated slowed brain atrophy and preserved cognitive function in treated patients.

However, current clinical protocols use fixed schedules: 40 seconds of stimulation followed by 20 seconds of rest, repeated uniformly for every patient. This approach has three fundamental problems:

1. **Wasted stimulation.** Approximately half of all stimulation is delivered when the brain is already well-entrained, providing no additional benefit while contributing to habituation.
2. **Missed therapeutic windows.** During rest periods, the brain frequently loses entrainment, but the fixed schedule cannot respond.
3. **Individual variability is ignored.** Roughly half of patients habituate to stimulation over time (declining response), while the other half maintain or increase their response. A fixed protocol cannot adapt to either pattern.

### The Solution

Rather than reacting to the brain's current state, this system predicts its future state 5-10 seconds ahead using a causal Temporal Convolutional Network (TCN). This lookahead window is long enough for the controller to make proactive decisions — initiating stimulation before entrainment degrades, or pausing before habituation sets in.

The system operates in two tiers:

- **Static PAC prediction (EEGNet, 1,457 parameters):** Estimates instantaneous theta-gamma phase-amplitude coupling from a 2-second EEG window across 7 frontal channels.
- **Temporal PAC forecasting (MultiscaleCausalTCN, 31,043 parameters):** Predicts PAC 5 seconds into the future from 20 seconds of history, using 73 engineered features (spectral, PAC-derived, and stimulation context).

A closed-loop controller uses these predictions to decide, every second, whether to stimulate or rest — personalized to each patient's rolling baseline via z-score normalization.

### Core Finding

At prediction horizons of 1-2 seconds, simple baselines (persistence, Ridge regression) outperform the TCN. But at 5-10 seconds — the operationally relevant range for proactive control — all baselines collapse to negative R² (worse than predicting the mean), while the TCN maintains R² of 0.24-0.28, a margin of +0.5 R² units. This is precisely the range where a controller needs predictions.

When integrated into a closed-loop controller and validated on real EEG data from 35 dementia patients:

| Metric | TCN Predictive | Reactive Control | Effect Size |
|--------|---------------|-----------------|-------------|
| Epoch alignment | 72.1% | 64.5% | g = 1.31, p < 0.001 |
| Low-PAC targeting | 82.6% | 51.7% | g = 4.47, p < 0.001 |
| PAC targeting gap | +30.5 | +21.1 | g = 1.57, p < 0.001 |

All 35 subjects benefited. The TCN controller reached 91% of the theoretical oracle bound. Results were robust across threshold parameters (0.2-1.0) and four different fatigue model assumptions.

### What This Means

This work provides the first demonstration that future PAC can be predicted from EEG at clinically relevant horizons where traditional methods fail, and that this predictive capability translates directly into improved stimulation targeting. The strong individual differences in habituation (50% habituate, 50% do not) validate the fundamental need for adaptive, personalized control rather than one-size-fits-all protocols.

### Dataset

OpenNeuro ds005048 v1.0.1 — "40 Hz Auditory Entrainment in Dementia" (Lahijanian et al., 2024). 35 elderly dementia patients, 19-channel EEG (10/20 system), 250 Hz sampling rate, alternating 40s stimulation / 20s rest blocks with 40 Hz amplitude-modulated auditory pulses.

### Author

Amaar Chughtai, Valley Christian High School — Synopsys Science and Engineering Fair 2026
