"""Generate CSEF 2026 poster board PPTX — 24x32 inches (prints at 200% → 48x64)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import os

# ── Colors ──────────────────────────────────────────────────────────────
NAVY = RGBColor(0x1B, 0x2A, 0x4A)
TEAL = RGBColor(0x3A, 0x7C, 0xA5)
GOLD = RGBColor(0xD4, 0xA8, 0x43)
LIGHT_GRAY = RGBColor(0xEE, 0xF2, 0xF5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)

# ── Slide dimensions ────────────────────────────────────────────────────
SLIDE_W = Inches(24)
SLIDE_H = Inches(32)

# ── Layout constants ────────────────────────────────────────────────────
MARGIN = Inches(0.3)
GAP = Inches(0.25)
HEADER_H = Inches(0.5)
COL3_W = Inches(7.63)
COL2_W = Inches(11.58)
FULL_W = Inches(23.4)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout


def add_box(x, y, w, h, fill_color):
    """Add a colored rectangle."""
    shape = slide.shapes.add_shape(1, x, y, w, h)  # 1 = rectangle
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


def add_text_box(x, y, w, h, text, font_name, font_size, font_color,
                 bold=False, italic=False, alignment=PP_ALIGN.LEFT,
                 anchor=MSO_ANCHOR.TOP):
    """Add a text box with styled text."""
    txBox = slide.shapes.add_textbox(x, y, w, h)
    txBox.text_frame.word_wrap = True
    txBox.text_frame.auto_size = None
    p = txBox.text_frame.paragraphs[0]
    p.text = text
    p.font.name = font_name
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_color
    p.font.bold = bold
    p.font.italic = italic
    p.alignment = alignment
    try:
        txBox.text_frame.paragraphs[0].space_before = Pt(0)
        txBox.text_frame.paragraphs[0].space_after = Pt(2)
    except Exception:
        pass
    return txBox


def add_section_header(x, y, w, text):
    """Add a teal header bar with white text."""
    add_box(x, y, w, HEADER_H, TEAL)
    add_text_box(
        x + Inches(0.15), y + Inches(0.05),
        w - Inches(0.3), HEADER_H - Inches(0.1),
        text, "Arial", 11, WHITE, bold=True,
        anchor=MSO_ANCHOR.MIDDLE,
    )


def add_content_bg(x, y, w, h):
    """Add light gray content background."""
    add_box(x, y, w, h, LIGHT_GRAY)


def add_body_text(x, y, w, h, lines, font_size=8):
    """Add multi-line body text with bullet points."""
    txBox = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.1),
                                     w - Inches(0.3), h - Inches(0.2))
    txBox.text_frame.word_wrap = True
    txBox.text_frame.auto_size = None
    first = True
    for line in lines:
        if first:
            p = txBox.text_frame.paragraphs[0]
            first = False
        else:
            p = txBox.text_frame.add_paragraph()

        is_subheader = line.startswith("##")
        is_bullet = line.startswith("- ")

        if is_subheader:
            p.text = line.replace("## ", "")
            p.font.name = "Arial"
            p.font.size = Pt(9)
            p.font.bold = True
            p.font.color.rgb = BLACK
            p.space_before = Pt(6)
            p.space_after = Pt(2)
        elif is_bullet:
            p.text = line[2:]
            p.font.name = "Arial"
            p.font.size = Pt(font_size)
            p.font.color.rgb = BLACK
            p.level = 1
            p.space_before = Pt(1)
            p.space_after = Pt(1)
        else:
            p.text = line
            p.font.name = "Arial"
            p.font.size = Pt(font_size)
            p.font.color.rgb = BLACK
            p.space_before = Pt(2)
            p.space_after = Pt(2)
    return txBox


def add_callout_box(x, y, w, h, big_text, label, sublabel):
    """Add a gold metric callout box."""
    add_box(x, y, w, h, GOLD)
    # Big number
    add_text_box(
        x + Inches(0.1), y + Inches(0.1),
        w - Inches(0.2), Inches(0.7),
        big_text, "Arial", 18, NAVY, bold=True,
        alignment=PP_ALIGN.CENTER,
    )
    # Label
    add_text_box(
        x + Inches(0.1), y + Inches(0.75),
        w - Inches(0.2), Inches(0.35),
        label, "Arial", 8, NAVY, bold=True,
        alignment=PP_ALIGN.CENTER,
    )
    # Sublabel
    add_text_box(
        x + Inches(0.1), y + Inches(1.05),
        w - Inches(0.2), Inches(0.5),
        sublabel, "Arial", 7, NAVY,
        alignment=PP_ALIGN.CENTER,
    )


# ════════════════════════════════════════════════════════════════════════
#  TITLE BANNER
# ════════════════════════════════════════════════════════════════════════
add_box(Inches(0.3), Inches(0.2), FULL_W, Inches(2.6), NAVY)

add_text_box(
    Inches(0.8), Inches(0.35), Inches(22.4), Inches(1.6),
    "Personalized Deep Learning Model for Closed-Loop 40 Hz\n"
    "Entrainment to Optimize Theta-Gamma Coupling\n"
    "in Alzheimer's Disease",
    "Arial", 26, WHITE, bold=True,
    alignment=PP_ALIGN.CENTER,
)

add_text_box(
    Inches(0.8), Inches(1.95), Inches(22.4), Inches(0.6),
    "Amaar M. Chughtai",
    "Arial", 13, WHITE,
    alignment=PP_ALIGN.CENTER,
)


# ════════════════════════════════════════════════════════════════════════
#  ROW 1 — Three columns
# ════════════════════════════════════════════════════════════════════════
ROW1_Y = Inches(3.1)
ROW1_CONTENT_Y = Inches(3.7)
ROW1_CONTENT_H = Inches(8.9)

# ── Column 1: INTRODUCTION ──────────────────────────────────────────────
c1_x = Inches(0.3)
add_section_header(c1_x, ROW1_Y, COL3_W, "INTRODUCTION")
add_content_bg(c1_x, ROW1_CONTENT_Y, COL3_W, ROW1_CONTENT_H)

add_body_text(c1_x, ROW1_CONTENT_Y, COL3_W, ROW1_CONTENT_H, [
    "Alzheimer's disease affects 55 million people worldwide "
    "with no cure. Emerging research shows 40 Hz auditory "
    "stimulation drives gamma brain rhythms that promote "
    "clearance of toxic amyloid-\u03B2 plaques through microglial "
    "activation and glymphatic fluid exchange "
    "(Iaccarino et al., 2016; Murdock et al., 2024).",
    "",
    "Current clinical protocols deliver stimulation on a "
    "fixed schedule \u2014 the same for every patient. "
    "This ignores two critical problems:",
    "",
    "- ~30% of patients habituate within minutes (Fortunato et al., 2023)",
    "- Responding patients still lose entrainment periodically, "
    "wasting stimulation during strong coupling and missing "
    "periods of genuine need",
    "",
    "[FIGURE: Fixed vs. Adaptive comparison diagram]",
    "",
    "## Research Question",
    "Can deep learning models forecast theta-gamma PAC "
    "dynamics 5\u201310 seconds into the future, and does "
    "integrating such forecasts into a closed-loop controller "
    "improve personalized 40 Hz entrainment therapy?",
    "",
    "## Hypothesis",
    "A causal TCN can forecast PAC at horizons beyond "
    "3 seconds where simpler baselines fail, and integrating "
    "these forecasts into a closed-loop controller will "
    "outperform reactive threshold control.",
])


# ── Column 2: SYSTEM ARCHITECTURE ──────────────────────────────────────
c2_x = Inches(8.18)
add_section_header(c2_x, ROW1_Y, COL3_W, "SYSTEM ARCHITECTURE")
add_content_bg(c2_x, ROW1_CONTENT_Y, COL3_W, ROW1_CONTENT_H)

# Placeholder for architecture diagram
add_text_box(
    c2_x + Inches(0.3), ROW1_CONTENT_Y + Inches(0.3),
    COL3_W - Inches(0.6), Inches(5.0),
    "[INSERT: System architecture diagram — Figure 1]\n\n"
    "Use results/figures/system_block_diagram.png\n"
    "or the author-generated diagram from the presentation.\n\n"
    "EEG \u2192 Preprocessing \u2192 EEGNet (1,457 params) \u2192\n"
    "PAC Estimate \u2192 12-Feature Extraction \u2192\n"
    "Causal TCN (22,914 params, 5s horizon) \u2192\n"
    "Controller (z-score \u00B10.5, 5s hysteresis) \u2192\n"
    "STIMULATE / REST / MAINTAIN \u2192 40 Hz Audio",
    "Arial", 7, RGBColor(0x66, 0x66, 0x66), italic=True,
    alignment=PP_ALIGN.CENTER,
)

# Key Discovery callout
add_box(
    c2_x + Inches(0.2), ROW1_CONTENT_Y + Inches(5.6),
    COL3_W - Inches(0.4), Inches(2.8), GOLD,
)
add_text_box(
    c2_x + Inches(0.35), ROW1_CONTENT_Y + Inches(5.7),
    COL3_W - Inches(0.7), Inches(0.35),
    "KEY DISCOVERY",
    "Arial", 9, NAVY, bold=True,
    alignment=PP_ALIGN.CENTER,
)
add_text_box(
    c2_x + Inches(0.35), ROW1_CONTENT_Y + Inches(6.1),
    COL3_W - Inches(0.7), Inches(2.1),
    "Dropping 61 spectral features and keeping only 12 "
    "PAC-trajectory and stimulation-context features raised "
    "test R\u00B2 from \u22120.025 to 0.606 (5-seed mean \u00B1 0.032). "
    "Spectral features encoded patient-specific anatomy, "
    "not generalizable dynamics. Feature selection mattered "
    "more than model architecture \u2014 8 architectures all "
    "converged at R\u00B2 = 0.287 on spectral features.",
    "Arial", 7.5, NAVY,
)


# ── Column 3: METHODS ──────────────────────────────────────────────────
c3_x = Inches(16.06)
add_section_header(c3_x, ROW1_Y, COL3_W, "METHODS")
add_content_bg(c3_x, ROW1_CONTENT_Y, COL3_W, ROW1_CONTENT_H)

add_body_text(c3_x, ROW1_CONTENT_Y, COL3_W, ROW1_CONTENT_H, [
    "## Dataset",
    "- OpenNeuro ds005048 (Lahijanian et al., 2024)",
    "- 35 elderly subjects: 17 AD, 6 MCI, 10 controls",
    "- 7 frontal EEG channels (Fp1, Fp2, F7, F3, Fz, F4, F8)",
    "- 250 Hz sampling rate",
    "- Protocol: 40 Hz auditory stimulation (40s ON / 20s OFF)",
    "",
    "## Preprocessing",
    "- Bandpass: 0.5\u201380 Hz (4th-order Butterworth, zero-phase)",
    "- Notch: 50 Hz (Q = 30) for power-line removal",
    "- Artifact rejection: \u00B1100 \u00B5V threshold",
    "- Common average reference",
    "- 2-second windows (500 samples), 1-second hop",
    "",
    "## PAC Computation",
    "- Modulation Index (Tort et al., 2010)",
    "- Theta phase (4\u20138 Hz) \u00D7 gamma amplitude (38\u201342 Hz)",
    "- KL divergence over 18 phase bins (20\u00B0)",
    "- Computed at epoch level (20\u201340s blocks)",
    "",
    "## Model",
    "- MultiscaleCausalTCN: 22,914 parameters",
    "- 4 causal depthwise-separable conv blocks",
    "- Dilations [1, 2, 4, 8], receptive field = 31 steps",
    "- GroupNorm + SiLU, attention pooling",
    "- Huber loss, AdamW, early stopping (patience = 20)",
    "- 12 input features: 7 PAC-derived + 5 stim context",
    "",
    "## Data Splits (subject-level, no leakage)",
    "- Train: 24 subjects (11,736 windows)",
    "- Validation: 5 subjects (2,725 windows)",
    "- Test: 6 subjects (2,822 windows)",
    "",
    "## Validation",
    "- Offline counterfactual replay on all 35 subjects",
    "- Ground-truth PAC labels used as TCN input",
    "- 6 controller variants compared incl. oracle",
    "- Wilcoxon signed-rank, Hedges\u2019 g, BCa bootstrap CIs",
])


# ════════════════════════════════════════════════════════════════════════
#  ROW 2 — Two columns
# ════════════════════════════════════════════════════════════════════════
ROW2_Y = Inches(12.85)
ROW2_CONTENT_Y = Inches(13.45)
ROW2_CONTENT_H = Inches(11.4)

# ── Column 1: RESULTS ──────────────────────────────────────────────────
r1_x = Inches(0.3)
add_section_header(r1_x, ROW2_Y, COL2_W, "RESULTS")
add_content_bg(r1_x, ROW2_CONTENT_Y, COL2_W, ROW2_CONTENT_H)

# Figure placeholders
add_text_box(
    r1_x + Inches(0.3), ROW2_CONTENT_Y + Inches(0.2),
    COL2_W - Inches(0.6), Inches(4.2),
    "[INSERT: Figure 2 — Controller Comparison Bar Chart]\n\n"
    "Use results/figures/controller_comparison.png\n"
    "Resize to fill ~11\" x 4.2\" in this box\n\n"
    "Shows all 6 controllers: Fixed, PI, Reactive, TCN, Hybrid, Oracle\n"
    "across Alignment, Low-PAC Stim Rate, High-PAC Rest Rate",
    "Arial", 7, RGBColor(0x66, 0x66, 0x66), italic=True,
    alignment=PP_ALIGN.CENTER,
)

add_text_box(
    r1_x + Inches(0.3), ROW2_CONTENT_Y + Inches(0.2),
    COL2_W - Inches(0.6), Inches(0.3),
    "Figure 2. Controller comparison on 35 subjects\u2019 real EEG. "
    "TCN achieves 72.1% alignment vs 64.5% reactive "
    "(g = 1.31, p < 0.001).",
    "Arial", 6.5, BLACK, italic=True,
)

# Two side-by-side figure placeholders
add_text_box(
    r1_x + Inches(0.3), ROW2_CONTENT_Y + Inches(4.7),
    Inches(5.2), Inches(3.3),
    "[INSERT: Figure 3 — Horizon Sweep]\n\n"
    "results/figures/horizon_sweep.png\n"
    "R\u00B2 across 1\u201310s horizons\n"
    "TCN maintains 0.37\u20130.67\n"
    "Baselines collapse beyond 3s",
    "Arial", 7, RGBColor(0x66, 0x66, 0x66), italic=True,
    alignment=PP_ALIGN.CENTER,
)

add_text_box(
    r1_x + Inches(5.8), ROW2_CONTENT_Y + Inches(4.7),
    Inches(5.2), Inches(3.3),
    "[INSERT: Figure 4 — Per-Subject Scatter]\n\n"
    "results/figures/per_subject_utility.png\n"
    "All 35 dots above diagonal\n"
    "Train/Val/Test splits marked\n"
    "Binomial p < 0.001",
    "Arial", 7, RGBColor(0x66, 0x66, 0x66), italic=True,
    alignment=PP_ALIGN.CENTER,
)

# Key findings callout boxes
callout_y = ROW2_CONTENT_Y + Inches(8.5)
callout_w = Inches(3.5)
callout_h = Inches(1.8)
callout_gap = Inches(0.29)

add_callout_box(
    r1_x + Inches(0.2), callout_y,
    callout_w, callout_h,
    "72.1%", "Alignment",
    "vs 64.5% reactive\ng = 1.31, p < 0.001",
)
add_callout_box(
    r1_x + Inches(0.2) + callout_w + callout_gap, callout_y,
    callout_w, callout_h,
    "82.6%", "Low-PAC Targeting",
    "vs 51.7% reactive\ng = 4.47, p < 0.001",
)
add_callout_box(
    r1_x + Inches(0.2) + (callout_w + callout_gap) * 2, callout_y,
    callout_w, callout_h,
    "35 / 35", "Subjects Benefited",
    "binomial p < 0.001\n91% of oracle gap",
)

# Summary sentence below callouts
add_text_box(
    r1_x + Inches(0.3), callout_y + callout_h + Inches(0.15),
    COL2_W - Inches(0.6), Inches(0.6),
    "The predictive controller reaches 91% of the theoretical oracle\u2019s "
    "targeting gap, demonstrating that 5-second PAC forecasting enables "
    "personalized therapy outperforming both fixed and reactive protocols.",
    "Arial", 7.5, BLACK, bold=True,
    alignment=PP_ALIGN.CENTER,
)


# ── Column 2: CONCLUSIONS & FUTURE DIRECTIONS ──────────────────────────
r2_x = Inches(12.13)
add_section_header(r2_x, ROW2_Y, COL2_W, "CONCLUSIONS & FUTURE DIRECTIONS")
add_content_bg(r2_x, ROW2_CONTENT_Y, COL2_W, ROW2_CONTENT_H)

add_body_text(r2_x, ROW2_CONTENT_Y, COL2_W, ROW2_CONTENT_H, [
    "## Conclusions",
    "- The predictive controller reaches 91% of the theoretical "
    "oracle\u2019s targeting gap across all 35 subjects",
    "- Feature selection was the breakthrough: 12 PAC-trajectory "
    "features outperform 73 spectral features five-fold "
    "(R\u00B2 = 0.606 vs. \u22120.025)",
    "- Eight neural network architectures (1,457 to 1.1M params) "
    "all converged at R\u00B2 = 0.287 on spectral features \u2014 "
    "the bottleneck was data representation, not model capacity",
    "- The TCN maintains R\u00B2 = 0.37\u20130.67 at 3\u201310s horizons "
    "where all baselines collapse to negative R\u00B2",
    "- All 35 subjects benefited, including 6 held-out test "
    "subjects never seen during training",
    "- Advantage is robust across z-score thresholds 0.2\u20131.0 "
    "and four fatigue model assumptions",
    "",
    "## Statistical Validation",
    "",
    "TCN vs. Reactive Threshold (N = 35, paired):",
    "",
    "  Alignment:        g = 1.31 [0.75, 1.87]    p < 0.001",
    "  Low-PAC targeting: g = 4.47 [3.33, 5.62]    p < 0.001",
    "  PAC Gap:           g = 1.57 [0.98, 2.17]    p < 0.001",
    "",
    "- Wilcoxon signed-rank tests (non-parametric, paired)",
    "- Hedges\u2019 g with 95% BCa bootstrap CIs (10,000 iterations)",
    "- 5-seed TCN validation: R\u00B2 = 0.606 \u00B1 0.032 "
    "(range 0.558\u20130.647)",
    "",
    "## Future Directions",
    "- Deploy with live EEG streaming for real-time "
    "closed-loop validation",
    "- IRB-approved observational pilot at regional "
    "memory care facilities (N = 5\u201310)",
    "- Crossover feasibility study: adaptive vs. fixed "
    "stimulation with cognitive outcome measures",
    "- Complete system cost under $250 per patient "
    "(consumer EEG headset + standard headphones)",
    "- Extend to multi-biomarker control "
    "(PAC + spectral power + connectivity)",
    "",
    "## Broader Impact",
    "The closed-loop control framework generalizes beyond "
    "40 Hz entrainment. The principle \u2014 using a biomarker "
    "forecast to time interventions proactively \u2014 applies to "
    "any brain stimulation paradigm where response is variable "
    "and predictable. Adaptive DBS for Parkinson\u2019s disease, "
    "FDA-approved in February 2025, validates this approach "
    "in a different modality.",
])


# ════════════════════════════════════════════════════════════════════════
#  ROW 3 — Acknowledgements & References
# ════════════════════════════════════════════════════════════════════════
ROW3_Y = Inches(25.1)
add_section_header(Inches(0.3), ROW3_Y, FULL_W, "ACKNOWLEDGEMENTS & REFERENCES")
add_content_bg(Inches(0.3), ROW3_Y + HEADER_H + Inches(0.1), FULL_W, Inches(5.5))

# Acknowledgements (left half)
add_body_text(
    Inches(0.3), ROW3_Y + HEADER_H + Inches(0.1),
    Inches(11.5), Inches(5.5),
    [
        "## Acknowledgements",
        "My AP Statistics teacher was consulted on statistical "
        "test selection. All other work \u2014 literature review, "
        "software development, experimental design, and analysis "
        "\u2014 was conducted independently.",
        "",
        "Computing: personal Apple Silicon MacBook and personal "
        "RTX 3080 GPU. No institutional lab, university mentor, "
        "or summer research program was used.",
        "",
        "Data: OpenNeuro ds005048, used under open access license.",
        "All diagrams created by the author unless otherwise noted.",
    ],
    font_size=7,
)

# References (right half)
add_body_text(
    Inches(12.0), ROW3_Y + HEADER_H + Inches(0.1),
    Inches(11.7), Inches(5.5),
    [
        "## References",
        "[1] Iaccarino HG et al. Gamma frequency entrainment "
        "attenuates amyloid load. Nature 540, 230\u2013235, 2016.",
        "[2] Murdock MH et al. Multisensory gamma stimulation "
        "promotes glymphatic clearance. Nature 627, 149\u2013156, 2024.",
        "[3] Chan D et al. Gamma sensory stimulation in mild "
        "Alzheimer\u2019s dementia: open-label extension. "
        "Alzheimer\u2019s & Dementia 21(10), e70792, 2025.",
        "[4] Fortunato C et al. Gamma entrainment for cognitive "
        "improvement in neurodegeneration. Front Neurosci 17, 2023.",
        "[5] Lahijanian B et al. Auditory gamma entrainment enhances "
        "DMN connectivity in dementia. Sci Rep 14, 2024.",
        "[6] Lawhern VJ et al. EEGNet: compact CNN for "
        "EEG-based BCIs. J Neural Eng 15, 056013, 2018.",
        "[7] Tort ABL et al. Measuring phase-amplitude coupling. "
        "J Neurophysiol 104, 1195\u20131210, 2010.",
        "[8] Rosin B et al. Closed-loop DBS for Parkinson\u2019s "
        "disease. Neuron 72, 370\u2013384, 2011.",
    ],
    font_size=6.5,
)


# ════════════════════════════════════════════════════════════════════════
#  FOOTER BAR
# ════════════════════════════════════════════════════════════════════════
add_box(Inches(0.3), Inches(31.3), FULL_W, Inches(0.4), NAVY)
add_text_box(
    Inches(0.3), Inches(31.3), FULL_W, Inches(0.4),
    "California Science and Engineering Fair 2026  \u2022  "
    "Medicine & Physiology",
    "Arial", 6, WHITE,
    alignment=PP_ALIGN.CENTER,
    anchor=MSO_ANCHOR.MIDDLE,
)


# ════════════════════════════════════════════════════════════════════════
#  SAVE
# ════════════════════════════════════════════════════════════════════════
out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "CSEF_2026_Poster.pptx")
prs.save(out_path)
print(f"Saved: {out_path}")
print(f"Slide size: {prs.slide_width / 914400:.0f}\" x {prs.slide_height / 914400:.0f}\"")
print("Print at 200% for final size 48\" x 64\"")
