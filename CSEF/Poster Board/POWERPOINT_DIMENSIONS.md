# PowerPoint Box Dimensions — 24" x 32" Slide (prints at 200% → 48" x 64")

All measurements in inches. Enter these in PowerPoint via right-click → Size and Position.
Fonts listed are what you TYPE in PowerPoint — they print at 2x.

---

## TITLE BANNER

| Property | Value |
|----------|-------|
| X | 0.3 |
| Y | 0.2 |
| W | 23.4 |
| H | 2.6 |
| Background | Dark navy (#1B2A4A) |

**Title text box** (inside banner):
| Property | Value |
|----------|-------|
| X | 0.8 |
| Y | 0.35 |
| W | 22.4 |
| H | 1.6 |
| Font | Arial Black, 26 pt (prints 52pt), White, centered |

**Author name text box** (inside banner):
| Property | Value |
|----------|-------|
| X | 0.8 |
| Y | 1.9 |
| W | 22.4 |
| H | 0.6 |
| Font | Arial Regular, 13 pt (prints 26pt), White, centered |

---

## ROW 1 — Three Columns (top sections)

All three share: **Y = 3.1**, **H = 9.5**
Gap between columns: 0.25"
Column width: 7.63"

### Column 1: INTRODUCTION

**Header bar:**
| Property | Value |
|----------|-------|
| X | 0.3 |
| Y | 3.1 |
| W | 7.63 |
| H | 0.5 |
| Background | Teal (#3A7CA5) |
| Font | Arial Bold, 11 pt (prints 22pt), White, left-aligned, vertically centered |
| Text | INTRODUCTION |

**Content area:**
| Property | Value |
|----------|-------|
| X | 0.3 |
| Y | 3.7 |
| W | 7.63 |
| H | 8.9 |
| Background | Light gray (#EEF2F5) or match template |
| Body font | Arial Regular, 8 pt (prints 16pt), Black, left-aligned |
| Subheader font | Arial Bold, 9 pt (prints 18pt), Black |
| Bullet spacing | 0.8 line spacing |

Content for this box (from blueprint):
- Problem statement (2-3 sentences on Alzheimer's + 40 Hz)
- Fixed vs Adaptive comparison figure (~3.5" tall inside this box)
- Background on PAC (2-3 sentences)
- Research Question
- Hypothesis

---

### Column 2: SYSTEM ARCHITECTURE

**Header bar:**
| Property | Value |
|----------|-------|
| X | 8.18 |
| Y | 3.1 |
| W | 7.63 |
| H | 0.5 |
| Background | Teal (#3A7CA5) |
| Font | Arial Bold, 11 pt (prints 22pt), White |
| Text | SYSTEM ARCHITECTURE |

**Content area:**
| Property | Value |
|----------|-------|
| X | 8.18 |
| Y | 3.7 |
| W | 7.63 |
| H | 8.9 |
| Background | Light gray (#EEF2F5) |

Content for this box:
- System architecture diagram (fill most of the box, ~7" W x 5" H)
- Key Discovery callout box below the diagram:
  - Inner box: gold background (#D4A843), 0.15" padding
  - Font: Arial Bold 8pt for label, Arial Regular 7.5pt for text
  - "Dropping 61 spectral features and keeping only 12 PAC-trajectory features raised R² from -0.025 to 0.606"

---

### Column 3: METHODS

**Header bar:**
| Property | Value |
|----------|-------|
| X | 16.06 |
| Y | 3.1 |
| W | 7.63 |
| H | 0.5 |
| Background | Teal (#3A7CA5) |
| Font | Arial Bold, 11 pt (prints 22pt), White |
| Text | METHODS |

**Content area:**
| Property | Value |
|----------|-------|
| X | 16.06 |
| Y | 3.7 |
| W | 7.63 |
| H | 8.9 |
| Background | Light gray (#EEF2F5) |
| Body font | Arial Regular, 8 pt (prints 16pt), Black |
| Subheader font | Arial Bold, 9 pt (prints 18pt), Black |

Content (use bullet points, not paragraphs):
- **Dataset** — OpenNeuro ds005048, 35 subjects, 7 channels, 250 Hz
- **Preprocessing** — bandpass, notch, artifact rejection, CAR, 2s windows
- **Model** — MultiscaleCausalTCN, 22,914 params, 12 features
- **Splits** — 24 train / 5 val / 6 test (subject-level)
- **Validation** — offline replay, 6 controllers, ground-truth PAC

---

## ROW 2 — Two Columns (bottom sections)

All share: **Y = 12.85**, **H = 12.0**
Gap between columns: 0.25"
Column width: 11.58"

### Column 1: RESULTS

**Header bar:**
| Property | Value |
|----------|-------|
| X | 0.3 |
| Y | 12.85 |
| W | 11.58 |
| H | 0.5 |
| Background | Teal (#3A7CA5) |
| Font | Arial Bold, 11 pt (prints 22pt), White |
| Text | RESULTS |

**Content area:**
| Property | Value |
|----------|-------|
| X | 0.3 |
| Y | 13.45 |
| W | 11.58 |
| H | 11.4 |
| Background | Light gray (#EEF2F5) |

Layout inside this box (top to bottom):
1. **Controller comparison figure** — W: 11.0", H: 4.5", centered
   - Caption below: Arial Italic 7pt (prints 14pt)
2. **Two figures side by side** (below controller comparison):
   - Horizon sweep: X offset 0.2", W: 5.2", H: 3.5"
   - Per-subject scatter: X offset 5.7", W: 5.2", H: 3.5"
   - Captions below each: Arial Italic 7pt
3. **Key Findings callout boxes** (bottom of results area):
   - Three boxes side by side, each W: 3.5", H: 1.8"
   - Gap between: 0.2"
   - Background: Gold (#D4A843)
   - Big number: Arial Black 18pt (prints 36pt), Dark navy
   - Label: Arial Bold 8pt (prints 16pt), Dark navy
   - Sublabel: Arial Regular 7pt (prints 14pt), Dark navy

Box 1: "72.1%" / "Alignment" / "vs 64.5% reactive, g = 1.31"
Box 2: "82.6%" / "Low-PAC Targeting" / "vs 51.7%, g = 4.47"
Box 3: "35/35" / "Subjects Benefited" / "p < 0.001"

---

### Column 2: CONCLUSIONS & FUTURE DIRECTIONS

**Header bar:**
| Property | Value |
|----------|-------|
| X | 12.13 |
| Y | 12.85 |
| W | 11.58 |
| H | 0.5 |
| Background | Teal (#3A7CA5) |
| Font | Arial Bold, 11 pt (prints 22pt), White |
| Text | CONCLUSIONS & FUTURE DIRECTIONS |

**Content area:**
| Property | Value |
|----------|-------|
| X | 12.13 |
| Y | 13.45 |
| W | 11.58 |
| H | 11.4 |
| Background | Light gray (#EEF2F5) |
| Body font | Arial Regular, 8 pt (prints 16pt) |
| Subheader font | Arial Bold, 9 pt (prints 18pt) |

Layout inside (top to bottom):

**CONCLUSIONS subheader** (9pt Bold):
- The predictive controller reaches 91% of the oracle's targeting gap
- Feature selection mattered more than architecture (8 models converged at R² = 0.287; 12 PAC features → R² = 0.606)
- TCN maintains R² = 0.37-0.67 at 3-10s where all baselines collapse
- All 35 subjects benefited, including 6 held-out test subjects
- Advantage holds across z-score thresholds 0.2-1.0 and four fatigue models

**STATISTICAL VALIDATION subheader** (9pt Bold):
- Effect size table (small table, 7pt font):

| Metric | g | 95% CI | p |
|--------|---|--------|---|
| Alignment | 1.31 | [0.75, 1.87] | <0.001 |
| Low-PAC | 4.47 | [3.33, 5.62] | <0.001 |
| PAC Gap | 1.57 | [0.98, 2.17] | <0.001 |

- Wilcoxon signed-rank, Hedges' g, BCa bootstrap 10,000 iterations
- 5-seed TCN: R² = 0.606 ± 0.032

**FUTURE DIRECTIONS subheader** (9pt Bold):
- Real-time validation with live EEG streaming
- IRB-approved pilot at memory care facilities (N = 5-10)
- Crossover study: adaptive vs fixed with cognitive outcome measures
- System cost under $250/patient (consumer EEG + headphones)
- Framework generalizes to other stimulation paradigms

---

## ROW 3 — Acknowledgements & References (full width)

**Header bar:**
| Property | Value |
|----------|-------|
| X | 0.3 |
| Y | 25.1 |
| W | 23.4 |
| H | 0.4 |
| Background | Teal (#3A7CA5) |
| Font | Arial Bold, 10 pt (prints 20pt), White |
| Text | ACKNOWLEDGEMENTS & REFERENCES |

**Content area:**
| Property | Value |
|----------|-------|
| X | 0.3 |
| Y | 25.6 |
| W | 23.4 |
| H | 5.5 |
| Background | Light gray (#EEF2F5) |

Layout inside — two columns:

**Left half** (Acknowledgements) — X offset 0.2", W: 11.2"
- Font: Arial Regular 7pt (prints 14pt)
- "My AP Statistics teacher was consulted on statistical test selection. All other work was conducted independently. Computing: personal Apple Silicon MacBook and personal RTX 3080 GPU. No institutional lab, university mentor, or summer research program was used."
- "Data source: OpenNeuro ds005048, used under open access license."
- "All diagrams created by the author unless otherwise noted."

**Right half** (References) — X offset 11.8", W: 11.2"
- Font: Arial Regular 6.5pt (prints 13pt)
- [1] Iaccarino HG et al. Nature 540, 230-235, 2016.
- [2] Murdock MH et al. Nature 627, 149-156, 2024.
- [3] Chan D et al. Alzheimer's & Dementia 21(10), e70792, 2025.
- [4] Fortunato C et al. Front Neurosci 17, 2023.
- [5] Lahijanian B et al. Sci Rep 14, 2024.
- [6] Lawhern VJ et al. J Neural Eng 15, 056013, 2018.
- [7] Tort ABL et al. J Neurophysiol 104, 1195-1210, 2010.
- [8] Rosin B et al. Neuron 72, 370-384, 2011.

---

## FOOTER BAR

| Property | Value |
|----------|-------|
| X | 0.3 |
| Y | 31.3 |
| W | 23.4 |
| H | 0.4 |
| Background | Dark navy (#1B2A4A) |

Optional: small text "California Science and Engineering Fair 2026" in white, 6pt, centered.

---

## FONT QUICK REFERENCE (what you type in PowerPoint)

| Element | PowerPoint Size | Prints As | Weight |
|---------|----------------|-----------|--------|
| Title | 26 pt | 52 pt | Arial Black |
| Author name | 13 pt | 26 pt | Arial Regular |
| Section headers | 11 pt | 22 pt | Arial Bold, White |
| Subheaders | 9 pt | 18 pt | Arial Bold, Black |
| Body text | 8 pt | 16 pt | Arial Regular, Black |
| Figure captions | 7 pt | 14 pt | Arial Italic, Black |
| Callout numbers | 18 pt | 36 pt | Arial Black, Navy |
| Callout labels | 8 pt | 16 pt | Arial Bold, Navy |
| Table text | 7 pt | 14 pt | Arial Regular |
| References | 6.5 pt | 13 pt | Arial Regular |
| Acknowledgements | 7 pt | 14 pt | Arial Regular |

---

## COLOR REFERENCE

| Use | Hex | Where |
|-----|-----|-------|
| Title banner / footer | #1B2A4A | Dark navy |
| Section header bars | #3A7CA5 | Teal/steel blue (match template) |
| Content backgrounds | #EEF2F5 | Light gray |
| Callout boxes | #D4A843 | Gold |
| Body text | #000000 | Black |
| Header text on bars | #FFFFFF | White |
| Slide background | #FFFFFF | White |
