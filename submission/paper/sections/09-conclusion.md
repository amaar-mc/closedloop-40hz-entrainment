# 9. Conclusion

This paper presents a computational framework for personalized closed-loop 40 Hz gamma entrainment in Alzheimer's disease,
combining static PAC estimation with temporal PAC forecasting to enable proactive rather than reactive stimulation control.
The system was trained and evaluated on real EEG recordings from 35 elderly dementia patients,
with all model development performed on held-out subject splits and primary results reported on a test set of 6 subjects never seen during training or hyperparameter selection.

The central empirical finding is the **prediction horizon inflection point** at approximately 3 seconds.
Below this threshold, auto-regressive baselines (persistence: R²=0.760 at 1s; Ridge: R²=0.812 at 1s) outperform the TCN,
and temporal modeling offers no advantage over simpler methods.
Above it — at the 5–10 second horizons operationally required for proactive stimulation preparation — both baselines collapse to negative R²
while the MultiscaleCausalTCN maintains R²≈0.25.
This +0.5 R² margin over baselines at 5–10 second horizons is the mechanistic foundation for the controller advantage:
the TCN predicts PAC state with enough directional accuracy to act before declines occur,
while reactive and persistence-based approaches cannot.

The controller comparison on 35 real EEG subjects confirms that this forecasting advantage translates to measurable control improvement.
The TCN predictive controller achieved 72.1% epoch alignment compared to 64.5% for reactive threshold control
(Wilcoxon W=0, p<0.001; Hedges' g=+1.31, 95% CI [+0.75, +1.87])
and 82.6% low-PAC stimulation rate compared to 51.7% (g=+4.47, 95% CI [+3.33, +5.62]).
The TCN's PAC targeting gap of 30.5 ×10⁻⁶ Modulation Index units reached 91.6% of the theoretical Alignment Oracle (33.3 ×10⁻⁶),
demonstrating that learned temporal prediction nearly saturates the achievable performance bound on this dataset.
Critically, all 35 subjects showed improved alignment under TCN control — including the 6 held-out test subjects —
with per-subject improvements ranging from 0.1 to 14.9 percentage points.
This universality is inconsistent with an artifact of subject selection or overfitting
and supports the conclusion that the TCN's temporal features capture generalizable structure in PAC dynamics across individuals.

This work also establishes the R²=0.287 ceiling for static PAC estimation from 7 frontal EEG channels as a scientific finding rather than a modeling failure.
Across 8 neural network architectures spanning 135 to 2 million parameters, all approaches converged to the same performance bound —
confirming that the ceiling reflects the information content of the data (epoch-level PAC labels assigned to 2-second windows) rather than model capacity.
This ceiling motivated the pivot from static estimation to temporal forecasting,
which sidesteps the ceiling by asking a different question: rather than predicting the _current_ PAC value with greater accuracy,
predict the _direction and timing_ of future PAC changes with sufficient reliability for proactive control decisions.

It is important to state precisely what this work demonstrates and what it does not.
This is a **computational validation on real EEG data**, not a clinical validation.
The controller makes decisions on real brain recordings, but cannot observe the brain's response to those decisions.
The 72.1% alignment figure measures counterfactual decision quality —
how well the controller _would have_ targeted stimulation — not realized therapeutic benefit in terms of PAC elevation or cognitive outcomes.
Confirming that proactive targeting translates to therapeutic benefit requires live closed-loop trials with human subjects under IRB oversight, as outlined in Section 8.

Within these scope boundaries, the primary contributions of this work are:
(1) characterizing the prediction horizon inflection point as a fundamental property of PAC dynamics in this population,
with a general methodology (the horizon sweep) for identifying this boundary in any EEG biomarker forecasting problem;
(2) demonstrating that temporal forecasting at 5–10 second horizons enables proactive control that substantially outperforms reactive threshold control;
(3) validating this advantage consistently across all 35 subjects including 6 held-out test subjects, establishing universality of benefit;
and (4) providing a complete, reproducible open-source pipeline — from raw BIDS EEG through feature extraction, TCN training, and controller validation — that can serve as a foundation for follow-on clinical translation work.

This work demonstrates a computational framework for personalized 40 Hz gamma entrainment that can guide clinical translation toward more efficient, individually adaptive Alzheimer's therapy.
The path from offline counterfactual validation to live closed-loop clinical benefit is defined:
end-to-end pipeline validation with EEGNet in the forecasting loop,
IRB approval for a hardware feasibility study,
and a within-subject crossover pilot trial with N=20 dementia patients.
Each step is technically feasible with existing hardware and models on standard computing equipment.
What remains is the systematic execution of that pathway, with the computational results presented here as its empirical foundation.
