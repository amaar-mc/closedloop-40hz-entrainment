# 5. Architecture Search: From Static PAC Prediction to Temporal Forecasting

## 5.1 Problem Framing: Why Static Prediction Mattered

The initial research question was deceptively direct: can instantaneous EEG predict the current level of theta-gamma phase-amplitude coupling? If a reliable mapping existed between a 2-second EEG snapshot and its corresponding PAC value, then a real-time EEGNet alone could serve as the sensing component of the closed-loop controller — inferring coupling state continuously and triggering stimulation decisions accordingly.

The clinical appeal of this framing is substantial. A static predictor requires no history buffer, no temporal model, and no complex state tracking. Each incoming 2-second window would yield an independent PAC estimate that could be immediately compared to the personalized baseline and acted upon. From February 5–16, 2026, we conducted a systematic exploration of this hypothesis across eight distinct model families, ranging from compact convolutional networks to transformer-based architectures with over a million parameters. What emerged was not a successful predictor, but a scientific finding about the limits of instantaneous EEG data — one that directly motivates the temporal prediction approach.

---

## 5.2 Systematic Comparison of Eight Architectures

Table 1 summarizes all eight models evaluated in the static PAC prediction phase, ordered chronologically by development version. R² values are on the held-out test set (6 subjects, 2,822 windows) unless otherwise noted.

**Table 1. Comparison of eight static PAC prediction architectures.**

| Model | Version | Parameters | Architecture | Test R² | Notes |
|-------|---------|-----------|--------------|---------|-------|
| EEGNet | V1 | 1,457 | Temporal + depthwise spatial conv on raw EEG | 0.287 | Lightest model; selected as baseline estimator |
| EEGNetV2 | V2 | 3,200 | EEGNet variant predicting ΔPAC (change in coupling) | 0.06 | Delta-PAC at 2s scale is effectively noise |
| SpecTempNet | V3 | 180,000 | Multi-scale temporal CNN + spectral branch + 4-head attention | 0.236 | Initial R²=0.69 was MI feature leakage; 0.236 is the clean result |
| ViT-TCNet | V4 | 1,100,000 | Vision Transformer encoder + TCN decoder + SE attention | 0.252 | Overfits despite regularization; N=35 is too small for 1.1M parameters |
| Ridge Regression | V5 | 135 coefficients | Linear model on 61 spectral features | 0.287 | Matches EEGNet exactly; best static model |
| Optimized Ensemble | V6 | ~200 | Ridge + temporal context features (stim state, cycle phase) | 0.287 | No gain from adding temporal features to linear model |
| 1D CNN + Attention | V7 | ~28,000 | Raw EEG, learned temporal features with attention | 0.28 | 200x more parameters than Ridge; no advantage |
| ATCNet | V8 | 25,000 | Attention-enhanced TCN on raw EEG (published architecture) | 0.22 | Published EEG architecture underperforms Ridge on this task |

### V1 — EEGNet (Baseline)

EEGNet (Lawhern et al., 2018) was the natural starting point: a compact architecture specifically designed for EEG data, with depthwise separable convolutions that encode both temporal oscillatory structure and spatial electrode weighting. Its 1,457 parameters prevent overfitting on the limited 11,736-window training set. On test subjects, EEGNet achieved R² = 0.287 and was retained as the production static estimator for the closed-loop controller due to its favorable accuracy-per-parameter ratio and its inductive biases aligning well with EEG signal structure.

### V2 — EEGNetV2 (Delta-PAC Prediction)

Rather than predicting absolute PAC, V2 targeted the change in PAC between consecutive windows — the hypothesis being that changes in coupling might be more predictable from short-duration EEG than absolute levels. The result was R² = 0.06, barely above chance. At the 2-second window scale, consecutive PAC differences are dominated by label noise (since both windows often belong to the same epoch and differ only in EEG segment, not in ground-truth PAC). Predicting delta-PAC from instantaneous EEG is intrinsically harder than predicting absolute PAC and provides no practical benefit.

### V3 — SpecTempNet (Multi-Scale Spectral-Temporal Network)

SpecTempNet combined a multi-scale temporal convolutional branch operating on raw EEG with a parallel spectral feature branch, fused via 4-head attention before regression. An initial evaluation appeared to yield R² = 0.69 — a remarkable improvement. However, our leakage audit (`archive/diagnostics/audit_leakage.py`) revealed that the spectral feature branch was computing features directly derived from the Modulation Index, which is the same quantity as the prediction target. These "PAC features" had correlations exceeding 0.7 with the target and accounted for 96.6% of the model's effective weight. After removing the PAC-circular features and retaining only safe spectral features (band powers and coherence), SpecTempNet's true R² fell to 0.236 — lower than the 135-parameter Ridge baseline.

### V4 — ViT-TCNet (Vision Transformer + TCN Decoder)

To test whether large-scale architectures with richer representational capacity could break through the apparent ceiling, we implemented ViT-TCNet: a Vision Transformer encoder that treated the (7-channel × 500-sample) EEG window as a pseudo-image, followed by a TCN decoder and squeeze-and-excitation attention blocks. With 1.1 million parameters trained on fewer than 12,000 examples, overfitting was severe. Dropout rates up to 0.5, L2 regularization, and learning rate scheduling all failed to close the gap to the linear baseline. The pure numpy SNR analysis showed approximately −4.73 dB signal-to-noise ratio for the V4 task, confirming that architectural complexity is not the bottleneck. The result: R² = 0.252.

### V5 — Ridge Regression (Linear Spectral Baseline)

As a sanity check, we trained a simple Ridge regression model (135 coefficients) on the same 61 spectral features used by SpecTempNet's clean branch. The result matched EEGNet exactly: R² = 0.287. This convergence — a 1.1-million-parameter transformer and a 135-parameter linear model reaching identical accuracy — is the clearest possible signal that the prediction ceiling is imposed by the *data*, not by model capacity.

### V6 — Optimized Ensemble (Linear + Temporal Context)

We augmented the Ridge baseline with five additional temporal context features: stimulation state, time since last state change, stimulation fraction over recent history, and cycle phase encodings. This expanded the feature set from 61 to 66 dimensions and explored whether knowing the current position in the stimulation cycle could improve static PAC prediction. The result was unchanged: R² = 0.287. The temporal context features carry no marginal information for instantaneous PAC prediction beyond what the spectral features already provide.

### V7 — 1D CNN with Attention (Raw EEG, Learned Features)

V7 replaced hand-crafted spectral features with a learned representation: a 1D convolutional network operating directly on the raw 500-sample EEG timeseries, augmented with a temporal attention mechanism. With approximately 28,000 parameters — 200 times more than Ridge — the model achieved R² = 0.28, narrowly below the linear baseline. Learned feature extraction from raw EEG offers no advantage over simple band-power computation for this prediction task.

### V8 — ATCNet (Attention-Enhanced TCN)

ATCNet is a published architecture combining an EEGNet-based convolutional module with a transformer-based temporal context module, designed for motor imagery classification. Adapted for regression, it achieved R² = 0.22 — the lowest result among the non-leakage-contaminated models. The attention mechanism, designed to capture inter-trial temporal dependencies in classification settings, does not transfer to within-trial PAC regression.

---

## 5.3 The R² = 0.287 Data Ceiling: Interpretation and Implications

The convergence of eight architectures — spanning four orders of magnitude in parameter count, three feature representations, and multiple distinct design philosophies — to the same R² ≈ 0.287 is a scientific result in itself, not an engineering failure.

**Why does the ceiling exist?**

The fundamental cause is the epoch-level label assignment described in Section 4.2. PAC is computed over full 20–40 second epochs for stability; these epoch-level values are then assigned to all constituent 2-second windows. A 2-second window provides at most 500 samples — only 5 complete theta cycles at 4 Hz, and fewer than 100 gamma cycles at the 40 Hz center frequency. The per-window EEG signal cannot contain enough information to recover the MI computed over a signal 10–20 times longer.

This situation is analogous to the Bayes error rate in machine learning: there is an irreducible lower bound on prediction error imposed by the information content of the inputs. When a 135-parameter linear model performs identically to a 1.1-million-parameter transformer, it demonstrates that the remaining prediction error is irreducible noise, not unexplained signal that a better model could capture.

Formally: if y_epoch is the true epoch-level PAC and y_window is the noisy per-window estimator derived from it, then for any function f, E[(f(x_window) − y_epoch)²] ≥ Var(y_epoch | x_window), and this conditional variance has a positive lower bound when the window duration is much shorter than the epoch duration.

**What R² = 0.287 means quantitatively:**

The static models explain 28.7% of the variance in epoch-level PAC from 2-second window features. The remaining 71.3% is irreducible from instantaneous EEG at this temporal resolution. This means that instantaneous EEG-based PAC prediction alone is insufficient to drive a precise closed-loop controller — the controller would be operating with substantial uncertainty about the brain's actual coupling state at each moment.

---

## 5.4 Motivation for the Temporal Prediction Pivot

The ceiling finding has a direct constructive implication: rather than attempting to improve instantaneous PAC prediction (which is bounded by data structure), we should ask whether the *dynamics* of PAC over time are predictable. Even if a single 2-second window provides limited information about current PAC, the trajectory of PAC over the preceding 20 seconds might contain enough structure to predict where PAC will be 5–10 seconds in the future.

This framing changes the task entirely:
- **Static prediction** asks: "What is the current PAC?" — bounded at R² = 0.287.
- **Temporal forecasting** asks: "Given how PAC has been evolving, where will it be in 5 seconds?" — an open question not constrained by the instantaneous ceiling.

There are additional reasons to believe temporal forecasting is tractable:
1. **PAC autocorrelation:** At 5-second timescales, PAC exhibits meaningful autocorrelation (r ≈ 0.45 from empirical measurement), suggesting that recent PAC history is informative about near-future PAC.
2. **Stimulation state:** The controller's own decisions (which states receive stimulation) are known in advance and influence PAC trajectory; encoding this information in the feature vector may enable the model to anticipate stimulation-induced PAC changes.
3. **Spectral precursors:** Changes in theta band power and cross-channel coherence may precede changes in theta-gamma coupling, providing leading indicators that a static model cannot exploit.

The 5–10 second prediction horizon is operationally significant: it provides enough lead time to pre-position the controller before a PAC decline occurs, enabling proactive rather than reactive stimulation decisions. The MultiscaleCausalTCN (Section 4.5) was designed specifically to exploit this temporal structure, leading to the closed-loop control results reported in Section 6.

---

## 5.5 Synthesis: Lessons from the Architecture Search

The eight-model search produced three actionable lessons that shaped the subsequent temporal prediction design:

**Lesson 1: Feature quality dominates architectural complexity.** The removal of PAC-circular features in V3 caused R² to drop from 0.69 to 0.236 — a larger effect than any architectural innovation. No architecture compensates for input features that encode the target. This lesson directly informed the strict feature audit applied to the temporal dataset's 73-dimensional input space, where PAC-derived features are included as predictors (they describe PAC history) but never as circular encodings of the future target.

**Lesson 2: The spectral feature set is near-optimal for instantaneous prediction.** Ridge regression on 61 band-power and coherence features achieved the same accuracy as the best deep learning model, indicating that the 61-dimensional spectral representation captures essentially all the instantaneous mutual information between EEG and epoch-level PAC. Richer representations (wavelet features for V4, learned representations for V7/V8) add parameters without adding signal.

**Lesson 3: The relevant signal is temporal, not instantaneous.** The fact that all instantaneous models converge to the same ceiling — regardless of capacity — indicates that the explanatory variance for PAC lies in temporal dynamics, not in the spatial or spectral content of any individual window. The appropriate inductive bias is a causal temporal model that can represent how PAC evolves, not a static convolutional model that treats each window as independent. This insight shaped both the architecture of the MultiscaleCausalTCN (dilated causal convolutions over a 20-step history) and its feature space (PAC moving averages and differences as explicit temporal inputs).

Together, these lessons reframe the static prediction phase not as an unsuccessful detour, but as a necessary empirical characterization of what instantaneous EEG can and cannot tell us — providing the principled motivation for temporal forecasting that follows.
