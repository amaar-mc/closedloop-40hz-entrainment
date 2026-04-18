# CSEF 2026 Poster Board Blueprint

**Print size:** 48" wide x 64" tall (on table, under 164 cm CSEF limit)
**Working size in PowerPoint:** 36" wide x 48" tall (Cobalt template)
**Print scaling:** 133% (36→48 wide, 48→64 tall)
**Category:** Medicine & Physiology
**Layout:** Standard 3-column trifold (left 9" | center 18" | right 9")

---

## Layout Overview (at 36" x 48" working size)

```
┌──────────────────────────────────────────────────┐
│              TITLE BANNER (gradient)              │  ~5"
│   Personalized Deep Learning Model for Closed-   │
│   Loop 40 Hz Entrainment to Optimize Theta-      │
│   Gamma Coupling in Alzheimer's Disease          │
│              Amaar M. Chughtai                    │
├─────────┬──────────────────────────┬─────────────┤
│         │                          │             │
│  INTRO  │   SYSTEM ARCHITECTURE    │  METHODS    │
│         │   (hero diagram)         │             │
│         │                          │             │
├─────────┤                          ├─────────────┤
│         ├──────────────────────────┤             │
│  BACK-  │                          │  DATA       │
│  GROUND │   RESULTS                │  SPLITS &   │
│  & PAC  │   (controller comp +     │  VALIDATION │
│         │    horizon sweep +       │             │
├─────────┤    per-subject scatter)  ├─────────────┤
│         │                          │             │
│  HYPO-  ├──────────────────────────┤ CONCLUSIONS │
│  THESIS │                          │             │
│         │   KEY FINDINGS           ├─────────────┤
│         │   (3 gold callout boxes) │             │
│         │                          │ FUTURE      │
│         ├──────────────────────────┤ DIRECTIONS  │
│         │                          │             │
│         │   KEY DISCOVERY          ├─────────────┤
│         │   (gold box)             │             │
│         │                          │ ACK &       │
│         │                          │ REFERENCES  │
│         │                          │             │
├─────────┴──────────────────────────┴─────────────┤
│              FOOTER BAR (gradient)                │  ~1"
└──────────────────────────────────────────────────┘
```

---

## Design Specs

**Template:** Cobalt (conceptualizingcobalt_36x48)
**Fonts:** Amaranth (headers), Titillium Web (body)

| Element | In PowerPoint | Prints As (133%) | Font | Weight |
|---------|--------------|-----------------|------|--------|
| Title | 32 pt | ~43 pt | Amaranth | Bold |
| Author name | 18 pt | ~24 pt | Titillium Web | Regular |
| Subtitle line | 11 pt | ~15 pt | Titillium Web | Regular |
| Section headers | 20 pt | ~27 pt | Amaranth | Bold, White |
| Subheaders | 13 pt | ~17 pt | Amaranth | Bold, Dark Blue |
| Body text | 10.5 pt | ~14 pt | Titillium Web | Regular |
| Bullet text | 10 pt | ~13 pt | Titillium Web | Regular |
| Figure captions | 8.5 pt | ~11 pt | Titillium Web | Italic |
| Callout numbers | 24 pt | ~32 pt | Amaranth | Bold |
| Callout labels | 10 pt | ~13 pt | Titillium Web | Bold |
| Callout sublabels | 8 pt | ~11 pt | Titillium Web | Regular |
| Stat lines | 9 pt | ~12 pt | Titillium Web | Bold |
| Small text / refs | 8 pt | ~11 pt | Titillium Web | Regular |

**Color palette (from template):**

| Use | Hex |
|-----|-----|
| Title/footer gradient start | #235078 |
| Title/footer gradient end | #1482A5 |
| Section header bars | #1482A5 |
| Content area backgrounds | #B4D3E2 |
| Callout boxes / key discovery | #D4A843 |
| Subheader / callout text | #235078 |
| Body text | #000000 |
| Header bar text | #FFFFFF |

---

## Column Dimensions (working size, 36" x 48")

| Column | X | Width | Content starts Y |
|--------|---|-------|-----------------|
| Left | 0.6" | 8.6" | 5.4" |
| Center | 9.5" | 17.0" | 5.4" |
| Right | 26.8" | 8.6" | 5.4" |
| All columns end Y | — | — | ~46.5" |

Gap between columns: 0.3"
Header bar height: 0.7"
Gap between sections within a column: 0.3"

---

## LEFT PANEL (8.6" wide)

Reading top to bottom: Introduction → Background → Hypothesis

### INTRODUCTION (Y: 5.4", H: ~11")

**Header bar:** Teal, "INTRODUCTION" in Amaranth Bold 20pt white
**Content bg:** Light blue (#B4D3E2)

Alzheimer's disease affects 55 million people worldwide with no cure. Emerging research shows 40 Hz auditory stimulation drives gamma brain rhythms that promote clearance of toxic amyloid-β plaques through microglial activation (Iaccarino et al., 2016) and glymphatic fluid exchange (Murdock et al., 2024).

Current clinical protocols deliver stimulation on a fixed schedule — the same for every patient. This ignores two problems:

• ~30% of patients habituate within minutes (Fortunato et al., 2023)
• Responding patients lose entrainment periodically, wasting stimulation during strong coupling and missing periods of need

**[FIGURE: Fixed vs. Adaptive comparison, ~8" x 3"]**
Two timelines showing fixed schedule waste vs adaptive alignment.

---

### BACKGROUND & PAC (Y: ~16.7", H: ~10")

**Header bar:** Teal, "BACKGROUND" in Amaranth Bold 20pt white
**Content bg:** Light blue

**Phase-Amplitude Coupling (PAC)** measures whether the brain's fast gamma oscillations (38–42 Hz) are synchronized with slow theta rhythms (4–8 Hz). High PAC = therapy working. Low PAC = entrainment lost. Quantified using the Modulation Index (Tort et al., 2010).

**The gap:** No existing system predicts future PAC to enable proactive intervention. Current approaches use fixed schedules (no adaptation) or reactive thresholds (respond only after decline).

**Precedent:** Adaptive deep brain stimulation for Parkinson's disease was FDA-approved in February 2025, proving biomarker-driven stimulation outperforms fixed protocols (Medtronic).

---

### HYPOTHESIS (Y: ~27.0", H: ~7")

**Header bar:** Teal, "HYPOTHESIS" in Amaranth Bold 20pt white
**Content bg:** Light blue

A causal Temporal Convolutional Network can forecast PAC at horizons beyond 3 seconds where simpler baselines fail, and integrating these forecasts into a closed-loop controller will outperform reactive threshold control.

**Goals:**
• Predict brain entrainment 5–10s into the future
• Integrate predictions into a closed-loop controller
• Validate on real patient EEG that predictive control outperforms fixed and reactive approaches

---

## CENTER PANEL (17.0" wide)

This is the hero panel. Title at top, then system architecture, results figures, key findings, and key discovery.

### SYSTEM ARCHITECTURE (Y: 5.4", H: ~10.5")

**Header bar:** Teal, "SYSTEM ARCHITECTURE" in Amaranth Bold 20pt white
**Content bg:** Light blue

**[HERO FIGURE: System architecture diagram, ~16" x 7"]**
Use results/figures/system_block_diagram.png or the presentation's Figure 1.

Pipeline: EEG (7ch) → Preprocessing → EEGNet (1,457 params) → PAC Estimate → 12-Feature Extraction → Causal TCN (22,914 params, 5s horizon) → Controller (z-score ±0.5, 5s hysteresis) → STIMULATE / REST / MAINTAIN → 40 Hz Audio → [feedback]

*Figure 1. Closed-loop 40 Hz entrainment system. Raw EEG flows through PAC estimation, 12-feature encoding, and causal TCN forecasting (<50 ms inference). The controller personalizes decisions via rolling z-score baseline with 5-second hysteresis. Author-generated diagram.*

---

### RESULTS (Y: ~16.2", H: ~14")

**Header bar:** Teal, "RESULTS" in Amaranth Bold 20pt white
**Content bg:** Light blue

**[FIGURE 2: Controller Comparison Bar Chart, ~16" x 5"]**
Use results/figures/controller_comparison.png
Shows 6 controllers across Alignment, Low-PAC Stim Rate, High-PAC Rest Rate.

*Figure 2. Controller comparison (N=35). TCN achieves 72.1% alignment vs 64.5% reactive (g = 1.31, p < 0.001) and targets 82.6% of low-PAC windows vs 51.7% (g = 4.47, p < 0.001).*

**[FIGURE 3: Horizon Sweep, ~7.8" x 4"] + [FIGURE 4: Per-Subject Scatter, ~7.8" x 4"]**
Side by side below Figure 2.

*Figure 3. Horizon sweep: TCN maintains R² = 0.37–0.67 at 3–10s where baselines collapse.*
*Figure 4. All 35/35 subjects above diagonal (binomial p < 0.001).*

---

### KEY FINDINGS (Y: ~30.5", H: ~3.5")

Three gold callout boxes side by side (~5.2" x 2.5" each):

| 72.1% | 82.6% | 35 / 35 |
|-------|-------|---------|
| Alignment | Low-PAC Targeting | Subjects Benefited |
| vs 64.5% reactive | vs 51.7% reactive | binomial p < 0.001 |
| g = 1.31 | g = 4.47 | 91% of oracle |

---

### KEY DISCOVERY (Y: ~34.3", H: ~5")

**Gold box (#D4A843), full center width with padding:**

**KEY DISCOVERY** (Amaranth Bold, centered)

Dropping 61 spectral features and keeping only 12 PAC-trajectory features raised test R² from −0.025 to 0.606 (5-seed mean ± 0.032). Spectral features encoded patient-specific anatomy, not generalizable dynamics. Feature selection mattered more than model architecture — 8 architectures all converged at R² ≈ 0.287 on spectral features.

---

## RIGHT PANEL (8.6" wide)

Reading top to bottom: Methods → Data Splits & Validation → Conclusions → Future Directions → Acknowledgements & References

### METHODS (Y: 5.4", H: ~12")

**Header bar:** Teal, "METHODS" in Amaranth Bold 20pt white
**Content bg:** Light blue

**Dataset**
• OpenNeuro ds005048 (Lahijanian et al., 2024)
• 35 elderly subjects: 17 AD, 6 MCI, 10 controls
• 7 frontal EEG channels, 250 Hz
• Protocol: 40 Hz auditory stim (40s ON / 20s OFF)

**Preprocessing**
• Bandpass: 0.5–80 Hz (Butterworth, zero-phase)
• Notch: 50 Hz, artifact rejection: ±100 µV
• Common average reference
• 2s windows (500 samples), 1s hop

**PAC Computation**
• Modulation Index (Tort et al., 2010)
• Theta (4–8 Hz) × gamma (38–42 Hz)
• 18 phase bins, epoch-level assignment

**Model**
• MultiscaleCausalTCN: 22,914 params
• 4 causal conv blocks, dilations [1,2,4,8]
• GroupNorm + SiLU, attention pooling
• Huber loss, AdamW, patience = 20
• 12 features: 7 PAC + 5 stim context

---

### DATA SPLITS & VALIDATION (Y: ~17.7", H: ~8")

**Header bar:** Teal, "VALIDATION" in Amaranth Bold 20pt white
**Content bg:** Light blue

**Subject-level splits (no leakage)**
• Train: 24 subjects (11,736 windows)
• Validation: 5 subjects (2,725 windows)
• Test: 6 subjects (2,822 windows)

**Protocol**
• Offline counterfactual replay, all 35 subjects
• Ground-truth PAC labels as TCN input
• 6 controller variants incl. oracle upper bound

**Statistics**
• Wilcoxon signed-rank (paired, non-parametric)
• Hedges' g + 95% BCa bootstrap CIs
• 5-seed reproducibility: R² = 0.606 ± 0.032

---

### CONCLUSIONS (Y: ~26.0", H: ~6.5")

**Header bar:** Teal, "CONCLUSIONS" in Amaranth Bold 20pt white
**Content bg:** Light blue

• Predictive controller reaches 91% of the oracle's targeting gap
• 12 PAC features outperform 73 spectral features five-fold
• 8 architectures converged at R² = 0.287 — bottleneck was features, not model
• TCN maintains R² = 0.37–0.67 where baselines collapse
• All 35 subjects benefited (p < 0.001)
• Robust across thresholds and fatigue models

---

### FUTURE DIRECTIONS (Y: ~32.8", H: ~5.5")

**Header bar:** Teal, "FUTURE DIRECTIONS" in Amaranth Bold 20pt white
**Content bg:** Light blue

• Real-time validation with live EEG streaming
• IRB-approved pilot at memory care facilities
• Crossover study: adaptive vs fixed, cognitive outcomes
• System cost under $250/patient (consumer EEG + headphones)
• Framework generalizes beyond 40 Hz entrainment

---

### ACKNOWLEDGEMENTS & REFERENCES (Y: ~38.6", H: ~7.6")

**Header bar:** Teal, "ACKNOWLEDGEMENTS & REFERENCES" in Amaranth Bold 20pt white
**Content bg:** Light blue

**Acknowledgements**
AP Statistics teacher consulted on statistical test selection. All other work conducted independently. Computing: personal MacBook + RTX 3080. No institutional lab or mentor.

Data: OpenNeuro ds005048, open access. All diagrams by the author.

**References**
[1] Iaccarino et al. Nature 540, 230–235, 2016.
[2] Murdock et al. Nature 627, 149–156, 2024.
[3] Chan et al. Alz & Dem 21(10), e70792, 2025.
[4] Fortunato et al. Front Neurosci 17, 2023.
[5] Lahijanian et al. Sci Rep 14, 2024.
[6] Lawhern et al. J Neural Eng 15, 056013, 2018.
[7] Tort et al. J Neurophysiol 104, 1195–1210, 2010.
[8] Rosin et al. Neuron 72, 370–384, 2011.

---

## FIGURES CHECKLIST

| # | Figure | Source | Size in PPT | Panel |
|---|--------|--------|------------|-------|
| 1 | Fixed vs Adaptive | Create or ai_generated/ | ~8" x 3" | Left: Introduction |
| 2 | System architecture | system_block_diagram.png | ~16" x 7" | Center: Architecture |
| 3 | Controller comparison | controller_comparison.png | ~16" x 5" | Center: Results |
| 4 | Horizon sweep | horizon_sweep.png | ~7.8" x 4" | Center: Results |
| 5 | Per-subject scatter | per_subject_utility.png | ~7.8" x 4" | Center: Results |
| - | 3 callout boxes | Built in PPT (gold) | ~5.2" x 2.5" ea | Center: Key Findings |
| - | Key Discovery box | Built in PPT (gold) | ~16" x 5" | Center: Key Discovery |

---

## PRINTING

- **File:** 36" x 48" in PowerPoint
- **Print at 133%** → final 48" x 64"
- **Export as PDF first** (File → Save As → PDF)
- **Matte finish** to avoid glare
- **No AC power at CSEF** — battery pack for laptop

## TABLE ITEMS

- Printed 13-page Project Presentation (required)
- Lab notebook
- Laptop with demo (battery-powered)
- Printed abstract (1-2 copies)

## SELF-CHECK

- [ ] Title readable from 10+ feet?
- [ ] 3-column trifold flow: left → center → right?
- [ ] All figures captioned?
- [ ] No school name, email, QR codes?
- [ ] References complete?
- [ ] All graphics attributed?
- [ ] Text under 500 words?
- [ ] Printed height 64" under 164 cm limit?
- [ ] File is 36x48, printing at 133%?
