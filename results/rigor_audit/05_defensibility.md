# Phase 2B: Scientific Defensibility Audit

**Audit date:** 2026-03-24
**Source:** `scripts/generate_csef_presentation.py` and rendered PDF

## Key Defensibility Questions

### 1. Does it clearly state this is offline counterfactual replay, not live closed-loop?

**YES — prominently disclosed.**

- Methods (script line 464): "**Offline counterfactual replay** on all 35 subjects' recorded EEG — not simulated brain dynamics"
- Limitations (script line 647): "**Offline counterfactual replay**, not live closed-loop: measures decision quality, not realized therapeutic benefit. Live validation with real-time EEG streaming is required."
- Conclusions (script line 692-698): "This work is a computational validation; live closed-loop trials are needed to confirm clinical translation."

**Verdict: PASS.** This is stated three times and is not buried — it appears in Methods, Limitations, and Conclusions.

### 2. Does it disclose that EEGNet is not in the validation loop?

**YES — explicitly stated.**

- Methods (script line 466-467): "Ground-truth PAC labels used as TCN input to isolate the forecaster's predictive contribution from EEGNet error"
- Limitations (script line 650-652): "**EEGNet not in the validation loop:** ground-truth PAC was used as TCN input; a deployed system would propagate EEGNet estimation error (R² = 0.287) into forecasts."

**Verdict: PASS.** Both the methodology and its limitation are clearly disclosed.

### 3. Does it honestly present limitations?

**YES — four limitations listed (script lines 645-660):**

1. Offline replay, not live closed-loop
2. EEGNet not in validation loop (with R² = 0.287 quantified)
3. Single-site dataset (Tehran memory clinic)
4. 7 frontal channels only (parietal/temporal coupling not captured)

**Additional limitations that COULD be mentioned but are not:**
- PAC labels are epoch-level (20-40s blocks), so all windows within an epoch share the same label. This means the TCN may be partially predicting which epoch a window belongs to, not truly predicting future neural dynamics.
- The sample size (N=35) is small for clinical generalization claims.
- The offline counterfactual replay assumes the brain would respond the same way regardless of when stimulation was delivered — an assumption that would not hold in vivo due to state-dependent neural dynamics.

**Verdict: PASS with note.** The four stated limitations are honest and substantive. The epoch-level PAC assignment is mentioned in Methods (line 369-370) as methodology but not explicitly flagged as a limitation. A skeptical judge might probe this.

### 4. Is the narrative arc (feature selection > architecture) well-supported?

**YES — strongly supported by data.**

The narrative: "The bottleneck was in the features, not the architecture."

Supporting evidence presented:
1. 8 architectures (1,457 to 1.1M params) all converge to R² ≈ 0.287 on 73 features → architecture doesn't matter
2. Feature ablation: same TCN (h=64), 73 features → R² = -0.025, 12 features → R² = 0.558 → features matter
3. Val-test gap shrinks from 0.358 (73 feat) to 0.246 (12 feat) → spectral features cause overfitting

**Verdict: PASS.** The claim is precise and well-supported. The architecture search data and ablation table directly demonstrate the claim.

### 5. Are comparisons to prior work fair and accurate?

**Assessment of each comparison:**

| Comparison | Fair? | Notes |
|---|---|---|
| Rosin et al. (2011) — closed-loop DBS analogy | **FAIR** | Presented as analogous, not equivalent. Both are adaptive stimulation systems. |
| Portiloop (Lacroix 2022) — spindle detection extension | **FAIR** | Correctly notes this work extends from detection to forecasting. |
| "First system targeting PAC dynamics" claim | **FAIR** | Qualified to "specifically for 40 Hz gamma entrainment optimization at 5–10 s horizons." Narrow enough to be defensible. |

**Verdict: PASS.** Comparisons are appropriately qualified and don't overclaim.

### 6. Is anything presented as a clinical result when it's computational?

**NO — appropriately framed throughout.**

- Title says "Personalized Deep Learning Model" — a computational framing.
- All results are from offline replay on recorded EEG, clearly stated.
- The Clinical Roadmap (Conclusions, lines 701-722) is future-looking, framed as "needed next steps."
- No therapeutic efficacy claims are made. Results are about decision quality (alignment, targeting), not patient outcomes.

**Verdict: PASS.**

### 7. Would a skeptical judge find any claim indefensible?

**Potential challenges a judge might raise:**

1. **"The 12 PAC features — don't they partially encode the target?"**
   - PAC features (pac_current, pac_ma2, etc.) are derived from the same PAC computation that generates the target. A skeptical judge could argue this is a form of soft leakage.
   - **Defense:** FINDINGS.md line 150 shows pac_current[-1] alone matches persistence (R²=0.104), not the target. The model learns temporal dynamics, not a circular encoding. This is disclosed in the presentation and is scientifically valid — predicting future PAC from past PAC is the entire point.

2. **"R² = 0.606 — how much is from PAC autocorrelation?"**
   - The persistence baseline (R²=0.104 at 5s) quantifies autocorrelation. The TCN's R²=0.606 exceeds this by +0.502, which is the genuine contribution of temporal modeling.
   - **Defense:** The horizon sweep explicitly shows persistence at each horizon, providing a clean decomposition.

3. **"Why does the 10s horizon have HIGHER R² (0.669) than the 5s horizon (0.577)?"**
   - This is counterintuitive — longer horizons should be harder. The 10s result is single-seed and may reflect favorable test-set variance. The 5-seed mean is only reported at 5s (0.606).
   - **Potential weakness:** A judge could argue the 10s result is a lucky seed artifact. The presentation shows it as single-seed (table note says "single seed").

4. **"The system architecture figure shows 73 features and 31K params, but your text says 12 features and 22,914 params."**
   - This is a real inconsistency (see 03_figure_audit.md). A careful judge will notice.

**Verdict: PASS with caveats.** No claims are indefensible, but the system architecture figure inconsistency (issue #4) is the most likely source of a pointed question. The 10s horizon anomaly (#3) could also draw scrutiny.

## Overall Defensibility Rating: **STRONG**

The presentation makes honest, well-supported claims with clear limitations. The main risk areas are the figure inconsistency and potential questions about PAC feature circularity (which has a good answer).
