"""
Generate CSEF 2026 poster using the Cobalt template style.
Slide: 36x48 inches (print at 133% → 48x64).
Template fonts: Amaranth (headers), Titillium Web (body).
Template colors: #235078 (dark blue), #1482A5 (teal), #B4D3E2 (light blue bg).
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
import copy
import os

# ── Load template ───────────────────────────────────────────────────────
TEMPLATE = "/Users/amaarchughtai/Downloads/conceptualizingcobalt_36x48 (3).pptx"
prs = Presentation(TEMPLATE)
slide = prs.slides[0]

# ── Colors (from template) ──────────────────────────────────────────────
DARK_BLUE = RGBColor(0x23, 0x50, 0x78)
TEAL = RGBColor(0x14, 0x82, 0xA5)
LIGHT_BG = RGBColor(0xB4, 0xD3, 0xE2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
GOLD = RGBColor(0xD4, 0xA8, 0x43)

# ── Font scaling ────────────────────────────────────────────────────────
# Working at 36x48, printing at 133% to 48x64
# So 36pt in file → 48pt printed. Multiply desired print size by 0.75.
# Print 52pt title → type 39pt
# Print 36pt header → type 27pt
# Print 24pt body → type 18pt
# Print 18pt caption → type 13.5pt


def clear_slide(slide):
    """Remove all shapes from the slide."""
    sp_list = list(slide.shapes)
    for sp in sp_list:
        elem = sp._element
        elem.getparent().remove(elem)


def add_rect(x, y, w, h, fill_color, line=False):
    """Add a filled rectangle."""
    shape = slide.shapes.add_shape(1, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if not line:
        shape.line.fill.background()
    return shape


def add_gradient_rect(x, y, w, h, color1_hex, color2_hex):
    """Add a rectangle with gradient fill matching template header."""
    shape = slide.shapes.add_shape(1, x, y, w, h)
    shape.line.fill.background()
    # Set gradient via XML
    sp_pr = shape._element.find(qn('a:solidFill'))
    fill_elem = shape._element.find('.//' + qn('a:solidFill'))

    # Use solid fill as fallback — gradient is complex in python-pptx
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(
        int(color1_hex[0:2], 16),
        int(color1_hex[2:4], 16),
        int(color1_hex[4:6], 16),
    )
    return shape


def add_text(x, y, w, h, text, font_name, font_size_pt, color,
             bold=False, italic=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, line_spacing=1.0):
    """Add a text box."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tb.text_frame.word_wrap = True
    tb.text_frame.auto_size = None
    p = tb.text_frame.paragraphs[0]
    p.text = text
    p.font.name = font_name
    p.font.size = Pt(font_size_pt)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.italic = italic
    p.alignment = align
    p.line_spacing = Pt(font_size_pt * line_spacing * 1.2)
    return tb


def add_section_header(x, y, w, text):
    """Add a teal section header bar with white Amaranth text."""
    add_rect(x, y, w, Inches(1.0), TEAL)
    add_text(
        x + Inches(0.3), y + Inches(0.1),
        w - Inches(0.6), Inches(0.8),
        text, "Amaranth", 27, WHITE, bold=True,
        anchor=MSO_ANCHOR.MIDDLE,
    )


def add_content_bg(x, y, w, h):
    """Add light blue content background."""
    add_rect(x, y, w, h, LIGHT_BG)


def add_body_block(x, y, w, h, sections):
    """
    Add structured body text. sections is a list of tuples:
    ('subheader', 'text') or ('body', 'text') or ('bullet', 'text')
    or ('spacer', '') or ('figure', 'placeholder text')
    """
    tb = slide.shapes.add_textbox(
        x + Inches(0.25), y + Inches(0.2),
        w - Inches(0.5), h - Inches(0.4),
    )
    tb.text_frame.word_wrap = True
    tb.text_frame.auto_size = None
    first = True

    for kind, text in sections:
        if first:
            p = tb.text_frame.paragraphs[0]
            first = False
        else:
            p = tb.text_frame.add_paragraph()

        if kind == "subheader":
            p.text = text
            p.font.name = "Amaranth"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = DARK_BLUE
            p.space_before = Pt(10)
            p.space_after = Pt(4)
        elif kind == "body":
            p.text = text
            p.font.name = "Titillium Web"
            p.font.size = Pt(13)
            p.font.color.rgb = BLACK
            p.space_before = Pt(2)
            p.space_after = Pt(2)
        elif kind == "bullet":
            p.text = text
            p.font.name = "Titillium Web"
            p.font.size = Pt(12)
            p.font.color.rgb = BLACK
            p.level = 1
            p.space_before = Pt(1)
            p.space_after = Pt(1)
        elif kind == "small":
            p.text = text
            p.font.name = "Titillium Web"
            p.font.size = Pt(10)
            p.font.color.rgb = BLACK
            p.space_before = Pt(1)
            p.space_after = Pt(1)
        elif kind == "stat":
            p.text = text
            p.font.name = "Titillium Web"
            p.font.size = Pt(11)
            p.font.color.rgb = DARK_BLUE
            p.font.bold = True
            p.space_before = Pt(1)
            p.space_after = Pt(1)
        elif kind == "caption":
            p.text = text
            p.font.name = "Titillium Web"
            p.font.size = Pt(10)
            p.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            p.font.italic = True
            p.space_before = Pt(2)
            p.space_after = Pt(2)
        elif kind == "figure":
            p.text = text
            p.font.name = "Titillium Web"
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
            p.font.italic = True
            p.alignment = PP_ALIGN.CENTER
            p.space_before = Pt(4)
            p.space_after = Pt(4)
        elif kind == "spacer":
            p.text = ""
            p.font.size = Pt(4)
            p.space_before = Pt(0)
            p.space_after = Pt(0)

    return tb


def add_callout(x, y, w, h, number, label, sublabel):
    """Gold callout box with big number."""
    add_rect(x, y, w, h, GOLD)
    add_text(
        x + Inches(0.1), y + Inches(0.15),
        w - Inches(0.2), Inches(0.8),
        number, "Amaranth", 30, DARK_BLUE, bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        x + Inches(0.1), y + Inches(0.9),
        w - Inches(0.2), Inches(0.4),
        label, "Titillium Web", 12, DARK_BLUE, bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        x + Inches(0.1), y + Inches(1.25),
        w - Inches(0.2), Inches(0.6),
        sublabel, "Titillium Web", 9.5, DARK_BLUE,
        align=PP_ALIGN.CENTER,
    )


# ════════════════════════════════════════════════════════════════════════
# Clear template placeholder content
# ════════════════════════════════════════════════════════════════════════
clear_slide(slide)

# ════════════════════════════════════════════════════════════════════════
# Layout constants
# ════════════════════════════════════════════════════════════════════════
L_MARGIN = Inches(0.8)
COL_GAP = Inches(0.5)
COL_W = Inches(16.6)  # each column width
R_COL_X = L_MARGIN + COL_W + COL_GAP
FULL_W = Inches(34.4)
HEADER_H = Inches(1.0)

# ════════════════════════════════════════════════════════════════════════
# TITLE BANNER (gradient header)
# ════════════════════════════════════════════════════════════════════════
add_gradient_rect(Inches(-0.04), Inches(-0.04), Inches(36.08), Inches(5.3),
                  "235078", "1482A5")

add_text(
    Inches(1.5), Inches(0.5), Inches(33.0), Inches(2.8),
    "Personalized Deep Learning Model for Closed-Loop\n"
    "40 Hz Entrainment to Optimize Theta-Gamma\n"
    "Coupling in Alzheimer\u2019s Disease",
    "Amaranth", 38, WHITE, bold=True,
    align=PP_ALIGN.CENTER,
)

add_text(
    Inches(1.5), Inches(3.3), Inches(33.0), Inches(0.7),
    "Amaar M. Chughtai",
    "Titillium Web", 24, WHITE,
    align=PP_ALIGN.CENTER,
)

add_text(
    Inches(1.5), Inches(4.0), Inches(33.0), Inches(0.7),
    "California Science and Engineering Fair 2026  \u2022  Medicine & Physiology",
    "Titillium Web", 14, RGBColor(0xCC, 0xDD, 0xEE),
    align=PP_ALIGN.CENTER,
)

# ════════════════════════════════════════════════════════════════════════
# ROW 1: INTRODUCTION (left) | SYSTEM ARCHITECTURE (right)
# ════════════════════════════════════════════════════════════════════════
ROW1_Y = Inches(5.8)

# ── INTRODUCTION ────────────────────────────────────────────────────────
add_section_header(L_MARGIN, ROW1_Y, COL_W, "INTRODUCTION")
intro_bg_y = ROW1_Y + HEADER_H + Inches(0.1)
intro_bg_h = Inches(12.5)
add_content_bg(L_MARGIN, intro_bg_y, COL_W, intro_bg_h)

add_body_block(L_MARGIN, intro_bg_y, COL_W, intro_bg_h, [
    ("body",
     "Alzheimer\u2019s disease affects 55 million people worldwide with no cure. "
     "Emerging research shows 40 Hz auditory stimulation drives gamma brain "
     "rhythms that promote clearance of toxic amyloid-\u03B2 plaques through "
     "microglial activation (Iaccarino et al., 2016) and glymphatic fluid "
     "exchange (Murdock et al., 2024)."),
    ("spacer", ""),
    ("body",
     "Current clinical protocols deliver stimulation on a fixed schedule \u2014 "
     "the same for every patient. This ignores two critical problems:"),
    ("bullet", "\u2022 ~30% of patients habituate within minutes (Fortunato et al., 2023)"),
    ("bullet", "\u2022 Responding patients still lose entrainment periodically, wasting "
     "stimulation during strong coupling and missing periods of genuine need"),
    ("spacer", ""),
    ("figure", "[INSERT: Fixed vs. Adaptive comparison diagram]\n"
     "Use results/figures/ai_generated/closedloop_vs_fixed_v2.png\n"
     "or create a simple 2-timeline diagram"),
    ("spacer", ""),
    ("subheader", "Research Question"),
    ("body",
     "Can deep learning models forecast theta-gamma phase-amplitude coupling "
     "(PAC) dynamics 5\u201310 seconds into the future, and does integrating such "
     "forecasts into a closed-loop controller improve personalized 40 Hz "
     "entrainment therapy?"),
    ("spacer", ""),
    ("subheader", "Hypothesis"),
    ("body",
     "A causal Temporal Convolutional Network can forecast PAC at horizons "
     "beyond 3 seconds where simpler baselines fail, and integrating these "
     "forecasts into a closed-loop controller will outperform reactive "
     "threshold control."),
])

# ── SYSTEM ARCHITECTURE ─────────────────────────────────────────────────
add_section_header(R_COL_X, ROW1_Y, COL_W, "SYSTEM ARCHITECTURE")
arch_bg_y = ROW1_Y + HEADER_H + Inches(0.1)
arch_bg_h = Inches(12.5)
add_content_bg(R_COL_X, arch_bg_y, COL_W, arch_bg_h)

add_body_block(R_COL_X, arch_bg_y, COL_W, Inches(7.0), [
    ("figure",
     "[INSERT: System Architecture Diagram \u2014 Figure 1]\n\n"
     "Use results/figures/system_block_diagram.png\n"
     "or the author-generated diagram from the presentation\n\n"
     "EEG (7ch) \u2192 Preprocessing \u2192 EEGNet (1,457 params)\n"
     "\u2192 PAC Estimate \u2192 12-Feature Extraction\n"
     "\u2192 Causal TCN (22,914 params, 5s horizon)\n"
     "\u2192 Controller (z-score \u00B10.5, 5s hysteresis)\n"
     "\u2192 STIMULATE / REST / MAINTAIN \u2192 40 Hz Audio"),
    ("caption",
     "Figure 1. System architecture of the closed-loop 40 Hz entrainment "
     "system. Raw EEG flows through signal processing, PAC estimation, "
     "12-feature temporal encoding, and causal TCN forecasting. The adaptive "
     "controller personalizes decisions using a rolling z-score baseline. "
     "Author-generated diagram."),
])

# Key Discovery callout
kd_y = arch_bg_y + Inches(7.5)
add_rect(R_COL_X + Inches(0.3), kd_y, COL_W - Inches(0.6), Inches(4.5), GOLD)
add_text(
    R_COL_X + Inches(0.6), kd_y + Inches(0.2),
    COL_W - Inches(1.2), Inches(0.5),
    "KEY DISCOVERY", "Amaranth", 16, DARK_BLUE, bold=True,
    align=PP_ALIGN.CENTER,
)
add_text(
    R_COL_X + Inches(0.6), kd_y + Inches(0.8),
    COL_W - Inches(1.2), Inches(3.4),
    "Dropping 61 spectral features and keeping only 12 PAC-trajectory "
    "and stimulation-context features raised test R\u00B2 from \u22120.025 "
    "to 0.606 (5-seed mean \u00B1 0.032). Spectral features encoded "
    "patient-specific anatomy, not generalizable dynamics.\n\n"
    "Feature selection mattered more than model architecture \u2014 "
    "8 neural network architectures (1,457 to 1.1M parameters) all "
    "converged at R\u00B2 \u2248 0.287 on spectral features.",
    "Titillium Web", 12, DARK_BLUE,
)


# ════════════════════════════════════════════════════════════════════════
# ROW 2: METHODS (left) | RESULTS (right)
# ════════════════════════════════════════════════════════════════════════
ROW2_Y = Inches(19.6)

# ── METHODS ─────────────────────────────────────────────────────────────
add_section_header(L_MARGIN, ROW2_Y, COL_W, "METHODS")
meth_bg_y = ROW2_Y + HEADER_H + Inches(0.1)
meth_bg_h = Inches(13.5)
add_content_bg(L_MARGIN, meth_bg_y, COL_W, meth_bg_h)

add_body_block(L_MARGIN, meth_bg_y, COL_W, meth_bg_h, [
    ("subheader", "Dataset"),
    ("bullet", "\u2022 OpenNeuro ds005048 (Lahijanian et al., 2024)"),
    ("bullet", "\u2022 35 elderly subjects: 17 AD, 6 MCI, 10 healthy controls"),
    ("bullet", "\u2022 7 frontal EEG channels (Fp1, Fp2, F7, F3, Fz, F4, F8), 250 Hz"),
    ("bullet", "\u2022 Protocol: 40 Hz auditory stimulation (40s ON / 20s OFF cycles)"),
    ("spacer", ""),
    ("subheader", "Preprocessing"),
    ("bullet", "\u2022 Bandpass: 0.5\u201380 Hz (4th-order Butterworth, zero-phase)"),
    ("bullet", "\u2022 Notch: 50 Hz (Q = 30), artifact rejection: \u00B1100 \u00B5V"),
    ("bullet", "\u2022 Common average reference"),
    ("bullet", "\u2022 2-second windows (500 samples), 1-second hop"),
    ("spacer", ""),
    ("subheader", "PAC Computation"),
    ("bullet", "\u2022 Modulation Index (Tort et al., 2010)"),
    ("bullet", "\u2022 Theta phase (4\u20138 Hz) \u00D7 gamma amplitude (38\u201342 Hz)"),
    ("bullet", "\u2022 KL divergence over 18 phase bins (20\u00B0)"),
    ("bullet", "\u2022 Computed at epoch level (20\u201340s), assigned to 2s windows"),
    ("spacer", ""),
    ("subheader", "Model Architecture"),
    ("bullet", "\u2022 MultiscaleCausalTCN: 22,914 parameters"),
    ("bullet", "\u2022 4 causal depthwise-separable conv blocks, dilations [1,2,4,8]"),
    ("bullet", "\u2022 Receptive field: 31 time steps (31 seconds of history)"),
    ("bullet", "\u2022 GroupNorm + SiLU activation, attention pooling"),
    ("bullet", "\u2022 Huber loss, AdamW optimizer, early stopping (patience = 20)"),
    ("bullet", "\u2022 12 input features: 7 PAC-derived + 5 stimulation context"),
    ("spacer", ""),
    ("subheader", "Data Splits (subject-level, no within-subject leakage)"),
    ("bullet", "\u2022 Train: 24 subjects (11,736 windows)"),
    ("bullet", "\u2022 Validation: 5 subjects (2,725 windows)"),
    ("bullet", "\u2022 Test: 6 subjects (2,822 windows)"),
    ("spacer", ""),
    ("subheader", "Validation Protocol"),
    ("bullet", "\u2022 Offline counterfactual replay on all 35 subjects\u2019 EEG"),
    ("bullet", "\u2022 Ground-truth PAC labels used as TCN input"),
    ("bullet", "\u2022 6 controller variants compared including alignment oracle"),
    ("bullet", "\u2022 Wilcoxon signed-rank tests, Hedges\u2019 g, BCa bootstrap CIs"),
])

# ── RESULTS ─────────────────────────────────────────────────────────────
add_section_header(R_COL_X, ROW2_Y, COL_W, "RESULTS")
res_bg_y = ROW2_Y + HEADER_H + Inches(0.1)
res_bg_h = Inches(13.5)
add_content_bg(R_COL_X, res_bg_y, COL_W, res_bg_h)

# Figure placeholders
add_body_block(R_COL_X, res_bg_y, COL_W, Inches(5.0), [
    ("figure",
     "[INSERT: Figure 2 \u2014 Controller Comparison Bar Chart]\n\n"
     "Use results/figures/controller_comparison.png\n"
     "Resize to fill ~15.5\" wide x 4.5\" tall"),
    ("caption",
     "Figure 2. Controller comparison on 35 subjects\u2019 real EEG. "
     "TCN Predictive achieves 72.1% alignment vs 64.5% for Reactive "
     "(g = 1.31, p < 0.001) and targets 82.6% of low-PAC windows "
     "vs 51.7% (g = 4.47, p < 0.001)."),
])

add_body_block(R_COL_X, res_bg_y + Inches(5.0), Inches(8.0), Inches(4.5), [
    ("figure",
     "[INSERT: Figure 3 \u2014 Horizon Sweep]\n\n"
     "results/figures/horizon_sweep.png\n"
     "TCN maintains R\u00B2 = 0.37\u20130.67\n"
     "Baselines collapse beyond 3s"),
    ("caption",
     "Figure 3. Prediction horizon sweep (1\u201310s)."),
])

add_body_block(R_COL_X + Inches(8.5), res_bg_y + Inches(5.0), Inches(8.0), Inches(4.5), [
    ("figure",
     "[INSERT: Figure 4 \u2014 Per-Subject Scatter]\n\n"
     "results/figures/per_subject_utility.png\n"
     "All 35/35 above diagonal"),
    ("caption",
     "Figure 4. Per-subject alignment (35/35 benefit)."),
])

# Callout boxes
callout_y2 = res_bg_y + Inches(10.0)
cw = Inches(5.0)
ch = Inches(2.2)
cg = Inches(0.3)
cx_start = R_COL_X + Inches(0.3)

add_callout(cx_start, callout_y2, cw, ch,
            "72.1%", "Alignment",
            "vs 64.5% reactive\ng = 1.31, p < 0.001")
add_callout(cx_start + cw + cg, callout_y2, cw, ch,
            "82.6%", "Low-PAC Targeting",
            "vs 51.7% reactive\ng = 4.47, p < 0.001")
add_callout(cx_start + (cw + cg) * 2, callout_y2, cw, ch,
            "35 / 35", "Subjects Benefited",
            "binomial p < 0.001\n91% of oracle\u2019s gap")

# Summary line
add_text(
    R_COL_X + Inches(0.3), callout_y2 + ch + Inches(0.2),
    COL_W - Inches(0.6), Inches(0.8),
    "The predictive controller reaches 91% of the theoretical oracle\u2019s "
    "targeting gap, demonstrating that 5-second PAC forecasting enables "
    "personalized therapy outperforming both fixed and reactive protocols.",
    "Titillium Web", 11, DARK_BLUE, bold=True,
    align=PP_ALIGN.CENTER,
)


# ════════════════════════════════════════════════════════════════════════
# ROW 3: CONCLUSIONS (left) | ACKNOWLEDGEMENTS & REFERENCES (right)
# ════════════════════════════════════════════════════════════════════════
ROW3_Y = Inches(34.4)

# ── CONCLUSIONS & FUTURE DIRECTIONS ─────────────────────────────────────
add_section_header(L_MARGIN, ROW3_Y, COL_W, "CONCLUSIONS & FUTURE DIRECTIONS")
conc_bg_y = ROW3_Y + HEADER_H + Inches(0.1)
conc_bg_h = Inches(12.0)
add_content_bg(L_MARGIN, conc_bg_y, COL_W, conc_bg_h)

add_body_block(L_MARGIN, conc_bg_y, COL_W, conc_bg_h, [
    ("subheader", "Conclusions"),
    ("bullet", "\u2022 The predictive controller reaches 91% of the oracle\u2019s targeting gap"),
    ("bullet", "\u2022 Feature selection was the breakthrough: 12 PAC features outperform "
     "73 spectral features five-fold (R\u00B2 = 0.606 vs. \u22120.025)"),
    ("bullet", "\u2022 8 architectures (1,457 to 1.1M params) converged at R\u00B2 = 0.287 "
     "on spectral features \u2014 the bottleneck was data, not model capacity"),
    ("bullet", "\u2022 TCN maintains R\u00B2 = 0.37\u20130.67 at 3\u201310s horizons where "
     "all baselines collapse"),
    ("bullet", "\u2022 All 35 subjects benefited, including 6 held-out test subjects"),
    ("bullet", "\u2022 Robust across thresholds 0.2\u20131.0 and four fatigue models"),
    ("spacer", ""),
    ("subheader", "Statistical Validation"),
    ("stat", "  Alignment:           g = 1.31 [0.75, 1.87]   p < 0.001"),
    ("stat", "  Low-PAC targeting:  g = 4.47 [3.33, 5.62]   p < 0.001"),
    ("stat", "  PAC Gap:              g = 1.57 [0.98, 2.17]   p < 0.001"),
    ("small", "Wilcoxon signed-rank (paired, non-parametric), "
     "Hedges\u2019 g with 95% BCa bootstrap CIs (10,000 iterations)"),
    ("small", "5-seed TCN: R\u00B2 = 0.606 \u00B1 0.032 (range 0.558\u20130.647)"),
    ("spacer", ""),
    ("subheader", "Future Directions"),
    ("bullet", "\u2022 Real-time validation with live EEG streaming"),
    ("bullet", "\u2022 IRB-approved pilot at memory care facilities (N = 5\u201310)"),
    ("bullet", "\u2022 Crossover study: adaptive vs. fixed with cognitive outcomes"),
    ("bullet", "\u2022 System cost under $250/patient (consumer EEG + headphones)"),
    ("bullet", "\u2022 Framework generalizes to other brain stimulation paradigms"),
    ("spacer", ""),
    ("subheader", "Broader Impact"),
    ("body",
     "The closed-loop principle \u2014 using a biomarker forecast to time "
     "interventions proactively \u2014 applies to any stimulation paradigm "
     "where response is variable and predictable. Adaptive DBS for "
     "Parkinson\u2019s, FDA-approved February 2025, validates this approach."),
])

# ── ACKNOWLEDGEMENTS & REFERENCES ───────────────────────────────────────
add_section_header(R_COL_X, ROW3_Y, COL_W, "ACKNOWLEDGEMENTS & REFERENCES")
ack_bg_y = ROW3_Y + HEADER_H + Inches(0.1)
ack_bg_h = Inches(12.0)
add_content_bg(R_COL_X, ack_bg_y, COL_W, ack_bg_h)

add_body_block(R_COL_X, ack_bg_y, COL_W, ack_bg_h, [
    ("subheader", "Acknowledgements"),
    ("body",
     "My AP Statistics teacher was consulted on statistical test selection. "
     "All other work \u2014 literature review, software development, "
     "experimental design, and analysis \u2014 was conducted independently."),
    ("small",
     "Computing: personal Apple Silicon MacBook and personal RTX 3080 GPU. "
     "No institutional lab, university mentor, or summer research program."),
    ("small", "Data: OpenNeuro ds005048, open access license."),
    ("small", "All diagrams created by the author unless otherwise noted."),
    ("spacer", ""),
    ("subheader", "References"),
    ("small", "[1] Iaccarino HG et al. Gamma frequency entrainment attenuates "
     "amyloid load. Nature 540, 230\u2013235, 2016."),
    ("small", "[2] Murdock MH et al. Multisensory gamma stimulation promotes "
     "glymphatic clearance. Nature 627, 149\u2013156, 2024."),
    ("small", "[3] Chan D et al. Gamma sensory stimulation in mild "
     "Alzheimer\u2019s dementia: open-label extension. Alzheimer\u2019s & "
     "Dementia 21(10), e70792, 2025."),
    ("small", "[4] Fortunato C et al. Gamma entrainment for cognitive "
     "improvement in neurodegeneration. Front Neurosci 17, 2023."),
    ("small", "[5] Lahijanian B et al. Auditory gamma entrainment enhances "
     "DMN connectivity in dementia. Sci Rep 14, 2024."),
    ("small", "[6] Lawhern VJ et al. EEGNet: compact CNN for EEG-based BCIs. "
     "J Neural Eng 15, 056013, 2018."),
    ("small", "[7] Tort ABL et al. Measuring phase-amplitude coupling. "
     "J Neurophysiol 104, 1195\u20131210, 2010."),
    ("small", "[8] Rosin B et al. Closed-loop DBS for Parkinson\u2019s disease. "
     "Neuron 72, 370\u2013384, 2011."),
])


# ════════════════════════════════════════════════════════════════════════
# FOOTER BAR
# ════════════════════════════════════════════════════════════════════════
add_gradient_rect(Inches(-0.04), Inches(46.79), Inches(36.08), Inches(1.21),
                  "235078", "1482A5")


# ════════════════════════════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════════════════════════════
out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "CSEF_2026_Poster_v2.pptx")
prs.save(out_path)
print(f"Saved: {out_path}")
print(f"Slide: 36\" x 48\" \u2192 print at 133% \u2192 48\" x 64\"")
print()
print("Font reference (in file \u2192 printed):")
print("  Amaranth 38pt title \u2192 ~51pt")
print("  Amaranth 27pt headers \u2192 ~36pt")
print("  Amaranth 16pt subheaders \u2192 ~21pt")
print("  Titillium Web 13pt body \u2192 ~17pt")
print("  Titillium Web 12pt bullets \u2192 ~16pt")
print("  Titillium Web 10pt small/refs \u2192 ~13pt")
