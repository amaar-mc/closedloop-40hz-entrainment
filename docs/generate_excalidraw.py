#!/usr/bin/env python3
"""Generate a comprehensive Excalidraw file for the Closed-Loop 40 Hz Entrainment project.

Covers 7 sections from the project map that had broken mermaid diagrams:
  2. The Problem
  3. Project Evolution Timeline
  6. PAC Computation
  7. Phase 1 Architecture Marathon
  11. Causal TCN Architecture Deep Dive
  15. Controller Pipeline
  19. Key Terms Glossary
"""

import json
import random
import uuid

# ─── Helpers ───────────────────────────────────────────────────────────────

_seed_counter = 1000


def _id():
    return uuid.uuid4().hex[:20]


def _seed():
    global _seed_counter
    _seed_counter += 1
    return _seed_counter


def _rect(
    x,
    y,
    w,
    h,
    bg="transparent",
    stroke="#1e1e1e",
    sw=2,
    fill="solid",
    group=None,
    round_type=3,
    opacity=100,
):
    return {
        "id": _id(),
        "type": "rectangle",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": stroke,
        "backgroundColor": bg,
        "fillStyle": fill,
        "strokeWidth": sw,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": opacity,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": {"type": round_type},
        "seed": _seed(),
        "version": 1,
        "versionNonce": _seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1709000000000,
        "link": None,
        "locked": False,
    }


def _text(
    x,
    y,
    text,
    size=16,
    color="#1e1e1e",
    align="left",
    valign="top",
    family=1,
    group=None,
    container_id=None,
    bold=False,
):
    lines = text.split("\n")
    line_h = size * 1.25
    w = max(len(line) for line in lines) * size * 0.6
    h = len(lines) * line_h
    return {
        "id": _id(),
        "type": "text",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": None,
        "seed": _seed(),
        "version": 1,
        "versionNonce": _seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1709000000000,
        "link": None,
        "locked": False,
        "text": text,
        "fontSize": size,
        "fontFamily": 3 if bold else family,
        "textAlign": align,
        "verticalAlign": valign,
        "containerId": container_id,
        "originalText": text,
        "autoResize": True,
        "lineHeight": 1.25,
    }


def _arrow(
    x1, y1, x2, y2, color="#1e1e1e", sw=2, group=None, start_head=None, end_head="arrow"
):
    dx = x2 - x1
    dy = y2 - y1
    return {
        "id": _id(),
        "type": "arrow",
        "x": x1,
        "y": y1,
        "width": abs(dx),
        "height": abs(dy),
        "angle": 0,
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": sw,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": _seed(),
        "version": 1,
        "versionNonce": _seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1709000000000,
        "link": None,
        "locked": False,
        "points": [[0, 0], [dx, dy]],
        "lastCommittedPoint": None,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": start_head,
        "endArrowhead": end_head,
    }


def _line(x1, y1, x2, y2, color="#1e1e1e", sw=2, style="solid", group=None):
    dx = x2 - x1
    dy = y2 - y1
    return {
        "id": _id(),
        "type": "line",
        "x": x1,
        "y": y1,
        "width": abs(dx),
        "height": abs(dy),
        "angle": 0,
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": sw,
        "strokeStyle": style,
        "roughness": 1,
        "opacity": 100,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": _seed(),
        "version": 1,
        "versionNonce": _seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1709000000000,
        "link": None,
        "locked": False,
        "points": [[0, 0], [dx, dy]],
        "lastCommittedPoint": None,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": None,
    }


def _diamond(
    x, y, w, h, bg="transparent", stroke="#1e1e1e", sw=2, fill="solid", group=None
):
    return {
        "id": _id(),
        "type": "diamond",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": stroke,
        "backgroundColor": bg,
        "fillStyle": fill,
        "strokeWidth": sw,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": _seed(),
        "version": 1,
        "versionNonce": _seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1709000000000,
        "link": None,
        "locked": False,
    }


def _ellipse(
    x, y, w, h, bg="transparent", stroke="#1e1e1e", sw=2, fill="solid", group=None
):
    return {
        "id": _id(),
        "type": "ellipse",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": stroke,
        "backgroundColor": bg,
        "fillStyle": fill,
        "strokeWidth": sw,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": _seed(),
        "version": 1,
        "versionNonce": _seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1709000000000,
        "link": None,
        "locked": False,
    }


def box_with_text(
    x,
    y,
    w,
    h,
    title,
    body,
    title_size=18,
    body_size=14,
    bg="#ffffff",
    stroke="#1e1e1e",
    title_color="#1e1e1e",
    body_color="#343a40",
    group=None,
):
    """Create a rectangle with a title and body text inside."""
    els = []
    els.append(_rect(x, y, w, h, bg=bg, stroke=stroke, group=group))
    pad = 12
    els.append(
        _text(
            x + pad,
            y + pad,
            title,
            size=title_size,
            color=title_color,
            group=group,
            bold=True,
        )
    )
    if body:
        title_h = title_size * 1.25 * len(title.split("\n")) + 8
        els.append(
            _text(
                x + pad,
                y + pad + title_h,
                body,
                size=body_size,
                color=body_color,
                group=group,
            )
        )
    return els


def section_title(x, y, text, size=36, color="#1e1e1e"):
    """Create a large section title."""
    return _text(x, y, text, size=size, color=color, bold=True)


def section_subtitle(x, y, text, size=20, color="#495057"):
    return _text(x, y, text, size=size, color=color)


# ─── Color Palette ─────────────────────────────────────────────────────────
RED_BG = "#ffcccc"
RED_STROKE = "#cc0000"
GREEN_BG = "#ccffcc"
GREEN_STROKE = "#00cc00"
BLUE_BG = "#e6f3ff"
BLUE_STROKE = "#0066cc"
ORANGE_BG = "#fff2e6"
ORANGE_STROKE = "#cc6600"
YELLOW_BG = "#fff2cc"
YELLOW_STROKE = "#cc9900"
PURPLE_BG = "#f2e6ff"
PURPLE_STROKE = "#6600cc"
GREY_BG = "#f5f5f5"
GREY_STROKE = "#868e96"
DARK_GREEN_BG = "#e6ffe6"
DARK_GREEN_STROKE = "#009900"


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 2: THE PROBLEM
# ═══════════════════════════════════════════════════════════════════════════
def build_section_2():
    els = []
    ox, oy = 0, 0  # origin

    # Title
    els.append(section_title(ox, oy, "2. THE PROBLEM: Why Fixed Schedules Fail"))
    els.append(
        section_subtitle(
            ox,
            oy + 50,
            "Alzheimer's patients need adaptive stimulation, not one-size-fits-all",
        )
    )

    # ── Row 1: The Disease + Current Protocol ──
    row1_y = oy + 120
    bw, bh = 360, 160

    els += box_with_text(
        ox,
        row1_y,
        bw,
        bh,
        "Alzheimer's Disease",
        "55M+ people worldwide\nNo cure, only symptom management\n40 Hz gamma entrainment shows\npromise in reducing amyloid plaques",
        bg=RED_BG,
        stroke=RED_STROKE,
    )

    els += box_with_text(
        ox + bw + 60,
        row1_y,
        bw,
        bh,
        "40 Hz Gamma Entrainment",
        "Sound/light at 40 Hz drives brain\noscillations. Reduces amyloid plaques\nin mice (Iaccarino et al., 2016).\nShows benefits in human trials.",
        bg=BLUE_BG,
        stroke=BLUE_STROKE,
    )

    els += box_with_text(
        ox + 2 * (bw + 60),
        row1_y,
        bw,
        bh,
        "Current Protocol: FIXED Schedule",
        "40 seconds stimulation ON\n20 seconds silence OFF\nRepeat for 1 hour\nSAME for EVERY patient",
        bg=ORANGE_BG,
        stroke=ORANGE_STROKE,
    )

    # Arrows row 1
    for i in range(2):
        ax = ox + bw + i * (bw + 60)
        els.append(
            _arrow(ax, row1_y + bh // 2, ax + 60, row1_y + bh // 2, color="#868e96")
        )

    # ── Row 2: Three problems with fixed schedule ──
    row2_y = row1_y + bh + 80
    pw, ph = 340, 120
    gap = 50
    problems = [
        (
            "Problem 1: Waste",
            "Wastes stimulation when brain\nis ALREADY entrained.\nUnnecessary energy expenditure.",
        ),
        (
            "Problem 2: Missed Windows",
            "Misses therapeutic windows when\nbrain LOSES entrainment during\nthe 20s OFF period.",
        ),
        (
            "Problem 3: Ignores Variability",
            "50% of patients habituate\n(response weakens over time)\n50% facilitate (response grows).\nOne protocol can't serve both.",
        ),
    ]
    for i, (title, body) in enumerate(problems):
        px = ox + i * (pw + gap)
        els += box_with_text(
            px, row2_y, pw, ph, title, body, bg=RED_BG, stroke=RED_STROKE, title_size=16
        )

    # Arrow from fixed schedule down to problems
    center_fixed = ox + 2 * (bw + 60) + bw // 2
    els.append(
        _arrow(center_fixed, row1_y + bh, center_fixed, row2_y - 10, color=RED_STROKE)
    )

    # ── Row 3: Two patient types ──
    row3_y = row2_y + ph + 80
    ptw, pth = 380, 180

    els += box_with_text(
        ox,
        row3_y,
        ptw,
        pth,
        "Patient A: Habituator (48.6%)",
        "Block 1: Strong coupling\nBlock 2: Weaker coupling\nBlock 3: Very weak (-66.8% decline)\n\nBrain 'tunes out' repeated stimulus\n(neural habituation)",
        bg=ORANGE_BG,
        stroke=ORANGE_STROKE,
    )

    els += box_with_text(
        ox + ptw + 100,
        row3_y,
        ptw,
        pth,
        "Patient B: Facilitator (51.4%)",
        "Block 1: Moderate coupling\nBlock 2: Stronger coupling\nBlock 3: Very strong (+149.1% increase)\n\nBrain responds MORE over time\n(neural facilitation)",
        bg=DARK_GREEN_BG,
        stroke=DARK_GREEN_STROKE,
    )

    # ── Row 4: The Solution ──
    row4_y = row3_y + pth + 80
    sw2, sh2 = 500, 200

    els += box_with_text(
        ox + 130,
        row4_y,
        sw2,
        sh2,
        "THIS PROJECT'S SOLUTION: Adaptive Control",
        "1. PREDICT when brain will lose entrainment\n"
        "   5-10 seconds ahead using Causal TCN\n"
        "2. ADAPT stimulation timing to each\n"
        "   patient's brain state in real-time\n"
        "3. PROACTIVE not REACTIVE:\n"
        "   Intervene BEFORE decline happens",
        bg=GREEN_BG,
        stroke=GREEN_STROKE,
        title_size=20,
    )

    # Arrows from patients to solution
    for px_start in [ox + ptw // 2, ox + ptw + 100 + ptw // 2]:
        els.append(
            _arrow(
                px_start,
                row3_y + pth,
                ox + 130 + sw2 // 2,
                row4_y - 10,
                color=GREEN_STROKE,
            )
        )

    return els


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 3: PROJECT EVOLUTION TIMELINE
# ═══════════════════════════════════════════════════════════════════════════
def build_section_3():
    els = []
    ox, oy = 0, 1400

    els.append(section_title(ox, oy, "3. PROJECT EVOLUTION TIMELINE"))
    els.append(
        section_subtitle(
            ox, oy + 50, "From planning to submission: Jan 15 - Mar 1, 2026"
        )
    )

    # Timeline line
    line_y = oy + 140
    total_w = 1800
    els.append(_line(ox, line_y, ox + total_w, line_y, color="#868e96", sw=3))

    # Timeline phases
    phases = [
        (
            "Jan 15",
            "Planning",
            "Research framing\nChose PAC biomarker (Tort MI)\nDefined subject-level splits\nPlanned pipeline stages",
            GREY_BG,
            GREY_STROKE,
        ),
        (
            "Jan 16-\nFeb 5",
            "Gap Period",
            "Reading papers\nRefining PAC method\nPreliminary data loader",
            GREY_BG,
            GREY_STROKE,
        ),
        (
            "Feb 6",
            "Phase 1:\nStatic PAC",
            "Built end-to-end pipeline\nSolved HDF5/FDT format issue\nImplemented PAC (Tort MI)\nTrained EEGNet: R2=0.287\n17,283 windows from 35 subjects",
            BLUE_BG,
            BLUE_STROKE,
        ),
        (
            "Feb 16",
            "Architecture\nMarathon",
            "Tested 6+ architectures\nDiscovered R2=0.287 ceiling\nCaught SpecTempNet leakage\nRidge matched EEGNet exactly\nCONCLUSION: data ceiling",
            RED_BG,
            RED_STROKE,
        ),
        (
            "Feb 17-18",
            "Phase 2:\nTemporal Pivot",
            "Pivoted to temporal forecasting\n73-feature representation\nMultiscaleCausalTCN (31K params)\nHabituation analysis (48.6/51.4)\nData integrity verification",
            GREEN_BG,
            GREEN_STROKE,
        ),
        (
            "Feb 19-21",
            "Validation",
            "Horizon sweep (1-10s)\nTCN wins at 5-10s horizons\nController integration\nReplay framework built\nFatigue sensitivity analysis",
            PURPLE_BG,
            PURPLE_STROKE,
        ),
        (
            "Feb 26-\nMar 1",
            "Final +\nSubmission",
            "Controller comparison locked\n72.1% alignment (TCN)\nvs 64.5% (reactive)\n35/35 patients benefited\nPoster, abstract, notebook",
            YELLOW_BG,
            YELLOW_STROKE,
        ),
    ]

    bw = 220
    gap = (total_w - len(phases) * bw) / (len(phases) - 1) if len(phases) > 1 else 0
    for i, (date, title, body, bg, stroke) in enumerate(phases):
        bx = ox + i * (bw + gap)
        by = line_y + 20

        # Date label above line
        els.append(_text(bx + 10, line_y - 40, date, size=12, color="#868e96"))

        # Tick mark
        els.append(
            _line(
                bx + bw // 2,
                line_y - 8,
                bx + bw // 2,
                line_y + 8,
                color="#868e96",
                sw=2,
            )
        )

        # Phase box
        bh = 200
        els += box_with_text(
            bx,
            by,
            bw,
            bh,
            title,
            body,
            bg=bg,
            stroke=stroke,
            title_size=14,
            body_size=11,
        )

    return els


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 6: PAC COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════
def build_section_6():
    els = []
    ox, oy = 0, 2200

    els.append(section_title(ox, oy, "6. PAC COMPUTATION: The Core Biomarker"))

    # ── What is PAC? ──
    row1_y = oy + 60
    els += box_with_text(
        ox,
        row1_y,
        500,
        180,
        "What is Phase-Amplitude Coupling (PAC)?",
        "How strongly the AMPLITUDE of fast oscillations\n"
        "(gamma 38-42 Hz) is modulated by the PHASE of\n"
        "slow oscillations (theta 4-8 Hz)\n\n"
        "High PAC = Brain is entrained = Therapy working\n"
        "Low PAC = Lost synchronization = Need stimulation",
        bg=BLUE_BG,
        stroke=BLUE_STROKE,
        title_size=16,
    )

    els += box_with_text(
        ox + 540,
        row1_y,
        400,
        180,
        "Why Theta-Gamma Coupling?",
        "Theta provides temporal windows\n"
        "for memory encoding.\n"
        "Gamma bursts within theta = items\n"
        "stored in working memory.\n"
        "This is the neural mechanism for\n"
        "memory (Canolty and Knight, 2010)",
        bg=YELLOW_BG,
        stroke=YELLOW_STROKE,
        title_size=16,
    )

    # ── Tort MI Steps ──
    steps_y = row1_y + 220
    els.append(
        section_subtitle(
            ox,
            steps_y - 10,
            "Tort Modulation Index (Tort et al., 2010) -- Step by Step",
        )
    )

    step_w, step_h = 280, 140
    step_gap = 30
    steps = [
        (
            "Step 1: Bandpass Filter",
            "Theta: 4-8 Hz\nGamma: 38-42 Hz\n4th-order Butterworth\nZero-phase (filtfilt)",
            BLUE_BG,
            BLUE_STROKE,
        ),
        (
            "Step 2: Hilbert Transform",
            "Theta -> instantaneous PHASE\nGamma -> instantaneous AMPLITUDE\n(envelope extraction)",
            BLUE_BG,
            BLUE_STROKE,
        ),
        (
            "Step 3: Phase Binning",
            "Divide -pi to pi into 18 bins\nEach bin = 20 degrees\nCompute MEAN gamma amplitude\nper theta phase bin",
            ORANGE_BG,
            ORANGE_STROKE,
        ),
        (
            "Step 4: Normalize",
            "P_i = mean_amp_i / sum(all)\nNow a probability distribution\nIf uniform: no coupling\nIf non-uniform: PAC exists",
            ORANGE_BG,
            ORANGE_STROKE,
        ),
        (
            "Step 5: KL Divergence",
            "KL = sum(P_i * log(P_i * N))\nMeasures distance from uniform\nUniform = no coupling = KL=0",
            PURPLE_BG,
            PURPLE_STROKE,
        ),
        (
            "Step 6: Normalize to MI",
            "MI = KL / log(n_bins)\nRange: 0 to 1\nTypical: 6e-6 to 7e-4\nMean: ~4.4e-5",
            PURPLE_BG,
            PURPLE_STROKE,
        ),
    ]

    # 2 rows of 3
    for i, (title, body, bg, stroke) in enumerate(steps):
        col = i % 3
        row = i // 3
        sx = ox + col * (step_w + step_gap)
        sy = steps_y + 30 + row * (step_h + 60)
        els += box_with_text(
            sx,
            sy,
            step_w,
            step_h,
            title,
            body,
            bg=bg,
            stroke=stroke,
            title_size=14,
            body_size=12,
        )

        # Arrow between sequential steps (horizontal within row, vertical between rows)
        if i < 5:
            if col < 2:  # horizontal arrow
                els.append(
                    _arrow(
                        sx + step_w,
                        sy + step_h // 2,
                        sx + step_w + step_gap,
                        sy + step_h // 2,
                        color="#868e96",
                    )
                )
            elif col == 2 and row == 0:  # down to next row
                els.append(
                    _arrow(
                        sx + step_w // 2,
                        sy + step_h,
                        ox + step_w // 2,
                        sy + step_h + 60,
                        color="#868e96",
                    )
                )

    # ── Why these frequency bands? ──
    bands_y = steps_y + 30 + 2 * (step_h + 60) + 40
    band_w = 300
    els += box_with_text(
        ox,
        bands_y,
        band_w,
        120,
        "Why Theta 4-8 Hz?",
        "Dominant rhythm during memory\nencoding. Provides 'time slots'\nfor gamma bursts.\nMost affected in Alzheimer's.",
        bg=GREY_BG,
        stroke=GREY_STROKE,
        title_size=14,
        body_size=12,
    )

    els += box_with_text(
        ox + band_w + 40,
        bands_y,
        band_w,
        120,
        "Why Gamma 38-42 Hz?",
        "Centered on 40 Hz = stimulation\nfrequency. Narrow band (4 Hz)\ncaptures entrainment response.\nNot general gamma (30-100 Hz).",
        bg=GREY_BG,
        stroke=GREY_STROKE,
        title_size=14,
        body_size=12,
    )

    els += box_with_text(
        ox + 2 * (band_w + 40),
        bands_y,
        band_w,
        120,
        "Why 18 Phase Bins?",
        "18 bins x 20 degrees = 360 deg\nStandard in PAC literature.\nEnough resolution without\ntoo few samples per bin.",
        bg=GREY_BG,
        stroke=GREY_STROKE,
        title_size=14,
        body_size=12,
    )

    return els


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 7: PHASE 1 ARCHITECTURE MARATHON
# ═══════════════════════════════════════════════════════════════════════════
def build_section_7():
    els = []
    ox, oy = 0, 3400

    els.append(section_title(ox, oy, "7. PHASE 1: Architecture Marathon"))
    els.append(
        section_subtitle(
            ox,
            oy + 50,
            "Goal: Estimate current PAC from a single 2s EEG window. 8 architectures tested.",
        )
    )

    # ── Architecture grid ──
    arch_y = oy + 100
    aw, ah = 260, 170
    agap = 30
    archs = [
        (
            "EEGNet V1 (WINNER)",
            "1,457 params\nR2 = 0.287\nBASELINE model\nTemporal + Spatial Conv\nBest efficiency",
            GREEN_BG,
            GREEN_STROKE,
        ),
        (
            "EEGNet-Delta V2",
            "~3,200 params\nR2 = 0.06\nFAILED: 2s delta band\nis too noisy for PAC",
            RED_BG,
            RED_STROKE,
        ),
        (
            "SpecTempNet V3",
            "180,000 params\nR2 = 0.69 then 0.236\nLEAKED! PAC features\nin input (96.6% weight)\nAfter fix: worse",
            RED_BG,
            RED_STROKE,
        ),
        (
            "ViT-TCNet V4",
            "~2,000,000 params\nR2 = 0.252\nOVERFITTING:\nsamples/params = 0.006\nOnly 11K training samples",
            RED_BG,
            RED_STROKE,
        ),
        (
            "Ridge Regression V5",
            "135 coefficients\nR2 = 0.287\nSHOCKING: Simplest model\nmatched EEGNet exactly.\nProved it's a data ceiling.",
            YELLOW_BG,
            YELLOW_STROKE,
        ),
        (
            "ATCNet V6",
            "~25,000 params\nR2 = 0.075\nUNDERPERFORMED\nToo complex for this\ndata/label structure",
            RED_BG,
            RED_STROKE,
        ),
        (
            "EEGNet-LSTM",
            "~15,000 params\nR2 < 0.287\nNo improvement over\nstandard EEGNet.\nSequential overhead wasted.",
            RED_BG,
            RED_STROKE,
        ),
        (
            "EEGNetLarge",
            "141,000 params\nR2 = 0.287\nSAME CEILING\n100x more params\n= zero benefit",
            ORANGE_BG,
            ORANGE_STROKE,
        ),
    ]

    for i, (title, body, bg, stroke) in enumerate(archs):
        col = i % 4
        row = i // 4
        ax = ox + col * (aw + agap)
        ay = arch_y + row * (ah + agap)
        els += box_with_text(
            ax,
            ay,
            aw,
            ah,
            title,
            body,
            bg=bg,
            stroke=stroke,
            title_size=14,
            body_size=12,
        )

    # ── The Pattern / Ceiling Discovery ──
    ceil_y = arch_y + 2 * (ah + agap) + 40
    cw = 4 * aw + 3 * agap

    els += box_with_text(
        ox,
        ceil_y,
        cw // 2 - 15,
        180,
        "THE PATTERN: R2 = 0.287 Ceiling",
        "Models from 135 to 2,000,000 parameters\n"
        "ALL converge to R2 = 0.287 or worse.\n"
        "Larger models = MORE overfitting.\n\n"
        "This is a DATA CEILING, not a model problem.\n"
        "SNR = -4.73 dB (signal weaker than noise).",
        bg=RED_BG,
        stroke=RED_STROKE,
        title_size=16,
    )

    els += box_with_text(
        ox + cw // 2 + 15,
        ceil_y,
        cw // 2 - 15,
        180,
        "WHY the Ceiling Exists",
        "1. Epoch-level PAC labeling: all 2s windows\n"
        "   in same epoch share ONE PAC value\n"
        "2. Only 7 frontal channels at 250 Hz\n"
        "3. Individual variability across 35 patients\n"
        "4. Need to change the QUESTION, not the model\n"
        "   --> This led to the TEMPORAL PIVOT",
        bg=YELLOW_BG,
        stroke=YELLOW_STROKE,
        title_size=16,
    )

    # ── SpecTempNet Leakage Lesson ──
    leak_y = ceil_y + 220
    els += box_with_text(
        ox,
        leak_y,
        cw,
        120,
        "DATA LEAKAGE LESSON (SpecTempNet V3)",
        "Initial R2 = 0.69 (exciting!) --> Checked feature correlations --> PAC-derived features in input had r=0.73 with target\n"
        "Ridge analysis: PAC features carried 96.6% of model weight --> After removing: R2 = 0.236 (worse than EEGNet)\n"
        "LESSON: Always check for leakage. High R2 + high feature-target correlation = smell test failure.",
        bg=ORANGE_BG,
        stroke=ORANGE_STROKE,
        title_size=16,
        body_size=13,
    )

    return els


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 11: CAUSAL TCN ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════
def build_section_11():
    els = []
    ox, oy = 0, 4700

    els.append(section_title(ox, oy, "11. CAUSAL TCN ARCHITECTURE DEEP DIVE"))
    els.append(
        section_subtitle(
            ox,
            oy + 50,
            "MultiscaleCausalTCN: 31,043 parameters | Predicts PAC 5 seconds ahead",
        )
    )

    # ── Main architecture flow (vertical) ──
    arch_y = oy + 100
    bw = 400
    center_x = ox + 300

    # Input
    els += box_with_text(
        center_x,
        arch_y,
        bw,
        60,
        "INPUT: (batch, 20, 73)",
        "20 timesteps x 73 features",
        bg=GREY_BG,
        stroke=GREY_STROKE,
        title_size=16,
        body_size=13,
    )

    # Projection
    proj_y = arch_y + 90
    els += box_with_text(
        center_x,
        proj_y,
        bw,
        80,
        "Input Projection (4,800 params)",
        "Linear 73 to 64 + LayerNorm(64) + SiLU\nTranspose: (B,20,64) to (B,64,20)",
        bg=BLUE_BG,
        stroke=BLUE_STROKE,
        title_size=14,
        body_size=12,
    )
    els.append(
        _arrow(
            center_x + bw // 2, arch_y + 60, center_x + bw // 2, proj_y, color="#868e96"
        )
    )

    # TCN Blocks
    blocks = [
        (
            "TCN Block 1: Dilation=1",
            "Causal Pad: 2 zeros left\nDepthwise Conv1d (groups=64, k=3)\nPointwise Conv1d (64 to 64)\nGroupNorm(1,64) + SiLU + Dropout(0.1)\n+ Residual Connection\n4,416 params",
        ),
        (
            "TCN Block 2: Dilation=2",
            "Causal Pad: 4 zeros left\nSees every OTHER timestep\n= 2-second patterns\nSame structure as Block 1\n4,416 params",
        ),
        (
            "TCN Block 3: Dilation=4",
            "Causal Pad: 8 zeros left\nSees every 4th timestep\n= 4-second patterns\n4,416 params",
        ),
        (
            "TCN Block 4: Dilation=8",
            "Causal Pad: 16 zeros left\nSees every 8th timestep\n= 8-second patterns\n4,416 params",
        ),
    ]

    block_y = proj_y + 110
    block_h = 130
    for i, (title, body) in enumerate(blocks):
        by = block_y + i * (block_h + 20)
        els += box_with_text(
            center_x,
            by,
            bw,
            block_h,
            title,
            body,
            bg=PURPLE_BG,
            stroke=PURPLE_STROKE,
            title_size=14,
            body_size=11,
        )
        if i > 0:
            els.append(
                _arrow(
                    center_x + bw // 2,
                    by - 20,
                    center_x + bw // 2,
                    by,
                    color=PURPLE_STROKE,
                )
            )
        else:
            els.append(
                _arrow(
                    center_x + bw // 2,
                    proj_y + 80,
                    center_x + bw // 2,
                    by,
                    color="#868e96",
                )
            )

    # Attention Pooling
    pool_y = block_y + 4 * (block_h + 20) + 10
    els += box_with_text(
        center_x,
        pool_y,
        bw,
        80,
        "Attention Pooling (65 params)",
        "Conv1d 64 to 1 --> Softmax over time\nWeighted sum: learned importance per timestep",
        bg=YELLOW_BG,
        stroke=YELLOW_STROKE,
        title_size=14,
        body_size=12,
    )
    els.append(
        _arrow(
            center_x + bw // 2,
            pool_y - 10,
            center_x + bw // 2,
            pool_y,
            color=PURPLE_STROKE,
        )
    )

    # Dual heads
    head_y = pool_y + 110
    head_w = 180

    els += box_with_text(
        center_x,
        head_y,
        head_w,
        100,
        "Future Head",
        "Linear 64 to 64 + SiLU\nDropout(0.1)\nLinear 64 to 1\n= Predicted PAC",
        bg=GREEN_BG,
        stroke=GREEN_STROKE,
        title_size=14,
        body_size=11,
    )

    els += box_with_text(
        center_x + head_w + 40,
        head_y,
        head_w,
        100,
        "Delta Head",
        "Linear 64 to 64 + SiLU\nDropout(0.1)\nLinear 64 to 1\n= Predicted Change",
        bg=GREEN_BG,
        stroke=GREEN_STROKE,
        title_size=14,
        body_size=11,
    )

    # Arrows to heads
    els.append(
        _arrow(
            center_x + bw // 2 - 40,
            pool_y + 80,
            center_x + head_w // 2,
            head_y,
            color=GREEN_STROKE,
        )
    )
    els.append(
        _arrow(
            center_x + bw // 2 + 40,
            pool_y + 80,
            center_x + head_w + 40 + head_w // 2,
            head_y,
            color=GREEN_STROKE,
        )
    )

    # ── Side panel: Design decisions ──
    side_x = center_x + bw + 80
    side_w = 360
    decisions = [
        (
            "GroupNorm(1,C) vs BatchNorm",
            "BatchNorm averages across batch;\nmixes patients. GroupNorm normalizes\neach sample independently.\nPreserves individual patient traits.",
            BLUE_BG,
            BLUE_STROKE,
        ),
        (
            "Depthwise-Separable vs Standard",
            "Standard: 12,288 params/block\nDepthwise+Pointwise: 4,288/block\n= 3x fewer parameters\n= less overfitting on 11K samples",
            BLUE_BG,
            BLUE_STROKE,
        ),
        (
            "Huber Loss vs MSE",
            "MSE: outliers dominate gradient.\nHuber: quadratic small, linear large\n(delta=1.0). PAC has outliers.",
            ORANGE_BG,
            ORANGE_STROKE,
        ),
        (
            "Causal Padding: Left-Only",
            "Standard: pads both sides = leaks\nCausal: pads LEFT only = no future\nF.pad(x, (left_pad, 0))\nEssential for real-time deployment",
            RED_BG,
            RED_STROKE,
        ),
        (
            "Receptive Field = 31 steps",
            "RF = 1 + (k-1) x sum(dilations)\n= 1 + 2 x (1+2+4+8) = 31\nCovers full 20-step input\nwith margin. 31 seconds of context.",
            YELLOW_BG,
            YELLOW_STROKE,
        ),
    ]

    for i, (title, body, bg, stroke) in enumerate(decisions):
        dy = arch_y + i * 160
        els += box_with_text(
            side_x,
            dy,
            side_w,
            140,
            title,
            body,
            bg=bg,
            stroke=stroke,
            title_size=14,
            body_size=12,
        )

    return els


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 15: CONTROLLER PIPELINE
# ═══════════════════════════════════════════════════════════════════════════
def build_section_15():
    els = []
    ox, oy = 0, 6400

    els.append(section_title(ox, oy, "15. CONTROLLER PIPELINE"))
    els.append(
        section_subtitle(
            ox,
            oy + 50,
            "Full Two-Stage System: EEG -> EEGNet -> Features -> TCN -> Decision",
        )
    )

    # ── Pipeline flow ──
    pipe_y = oy + 110
    bw, bh = 320, 120

    # Stage boxes
    stages = [
        (
            "EEG Input",
            "7 frontal channels\n250 Hz sampling\n2-second windows (500 samples)",
            GREY_BG,
            GREY_STROKE,
        ),
        (
            "Stage 1: EEGNet",
            "1,457 parameters\nEstimates CURRENT PAC\nInference: under 1ms\nz-score normalized output",
            BLUE_BG,
            BLUE_STROKE,
        ),
        (
            "Feature Extraction (73-dim)",
            "61 spectral (5 bands x 7ch + coherence)\n7 PAC-derived (current + MAs + diffs)\n5 stim context (state, timing, cycle)",
            ORANGE_BG,
            ORANGE_STROKE,
        ),
        (
            "Stage 2: Causal TCN",
            "31,043 parameters\n20-step rolling buffer\nPredicts PAC 5s ahead\nInference: under 3ms",
            GREEN_BG,
            GREEN_STROKE,
        ),
    ]

    for i, (title, body, bg, stroke) in enumerate(stages):
        sx = ox + i * (bw + 40)
        els += box_with_text(
            sx,
            pipe_y,
            bw,
            bh,
            title,
            body,
            bg=bg,
            stroke=stroke,
            title_size=14,
            body_size=12,
        )
        if i > 0:
            els.append(
                _arrow(sx - 40, pipe_y + bh // 2, sx, pipe_y + bh // 2, color="#868e96")
            )

    # ── Decision logic ──
    dec_y = pipe_y + bh + 80
    dec_w = 500

    # Predictive path
    els += box_with_text(
        ox,
        dec_y,
        dec_w,
        160,
        "TCN PREDICTIVE PATH (Priority)",
        "delta_pac < -0.3  -->  TCN predicts DECLINE\n"
        "                       = STIMULATE proactively\n\n"
        "delta_pac > +0.3  -->  TCN predicts RISE\n"
        "                       = REST proactively\n\n"
        "abs(delta_pac) <= 0.3  -->  Dead zone\n"
        "                            = Fall back to reactive",
        bg=GREEN_BG,
        stroke=GREEN_STROKE,
        title_size=16,
        body_size=13,
    )

    # Reactive path
    els += box_with_text(
        ox + dec_w + 60,
        dec_y,
        400,
        160,
        "REACTIVE PATH (Fallback)",
        "Uses rolling z-score of PAC:\n\n"
        "z < -0.5  = PAC below baseline\n"
        "            = weak coupling = STIMULATE\n\n"
        "z > +0.5  = PAC above baseline\n"
        "            = strong coupling = REST\n\n"
        "-0.5 <= z <= +0.5  = normal range",
        bg=BLUE_BG,
        stroke=BLUE_STROKE,
        title_size=16,
        body_size=13,
    )

    # Arrow from TCN to predictive
    els.append(
        _arrow(
            ox + 3 * (bw + 40) + bw // 2,
            pipe_y + bh,
            ox + dec_w // 2,
            dec_y,
            color=GREEN_STROKE,
        )
    )

    # Hysteresis + Output
    out_y = dec_y + 200
    els += box_with_text(
        ox + 100,
        out_y,
        350,
        80,
        "Hysteresis Guard",
        "Must stay in current state for 5 seconds\nbefore switching. Prevents rapid oscillation.",
        bg=YELLOW_BG,
        stroke=YELLOW_STROKE,
        title_size=14,
        body_size=12,
    )

    els += box_with_text(
        ox + 500,
        out_y,
        180,
        80,
        "STIMULATE",
        "Turn ON 40 Hz audio\nfor this patient",
        bg=GREEN_BG,
        stroke=GREEN_STROKE,
        title_size=16,
        body_size=12,
    )

    els += box_with_text(
        ox + 720,
        out_y,
        180,
        80,
        "REST",
        "Turn OFF audio\nconserve response",
        bg=RED_BG,
        stroke=RED_STROKE,
        title_size=16,
        body_size=12,
    )

    els.append(_arrow(ox + 450, out_y + 40, ox + 500, out_y + 30, color=GREEN_STROKE))
    els.append(_arrow(ox + 450, out_y + 40, ox + 720, out_y + 30, color=RED_STROKE))

    # ── Four Controllers Compared ──
    comp_y = out_y + 130
    els.append(section_subtitle(ox, comp_y, "Four Controllers Compared"))
    comp_y += 35

    cw, ch = 280, 160
    controllers = [
        (
            "Fixed Schedule\n(Clinical Standard)",
            "40s ON, 20s OFF\nNo brain feedback\nSame for everyone\n\nAlignment: 45.0%\nPAC Gap: -6.6 (WRONG)",
            RED_BG,
            RED_STROKE,
        ),
        (
            "Reactive Threshold",
            "z-score on CURRENT PAC\nz < -0.5: stimulate\nz > +0.5: rest\n\nAlignment: 64.5%\nLow-PAC targeting: 51.7%",
            ORANGE_BG,
            ORANGE_STROKE,
        ),
        (
            "TCN Predictive\n(THIS PROJECT)",
            "z-score + TCN 5s lookahead\nPredicted decline: stimulate\nPredicted rise: rest\n\nAlignment: 72.1%\nLow-PAC targeting: 82.6%",
            GREEN_BG,
            GREEN_STROKE,
        ),
        (
            "Oracle (Upper Bound)",
            "Perfect future knowledge\nTheoretical maximum\nNot achievable in practice\n\nAlignment: 100%\nLow-PAC targeting: 100%",
            BLUE_BG,
            BLUE_STROKE,
        ),
    ]

    for i, (title, body, bg, stroke) in enumerate(controllers):
        cx = ox + i * (cw + 20)
        els += box_with_text(
            cx,
            comp_y,
            cw,
            ch,
            title,
            body,
            bg=bg,
            stroke=stroke,
            title_size=14,
            body_size=12,
        )
        if i > 0:
            els.append(
                _arrow(cx - 20, comp_y + ch // 2, cx, comp_y + ch // 2, color="#868e96")
            )

    # Performance
    perf_y = comp_y + ch + 30
    els += box_with_text(
        ox,
        perf_y,
        600,
        60,
        "System Performance",
        "EEGNet: under 1ms | TCN: under 3ms | Total: under 5ms | Memory: under 100 MB | Decision rate: 1 Hz",
        bg=GREY_BG,
        stroke=GREY_STROKE,
        title_size=14,
        body_size=13,
    )

    return els


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 19: KEY TERMS GLOSSARY
# ═══════════════════════════════════════════════════════════════════════════
def build_section_19():
    els = []
    ox, oy = 0, 7900

    els.append(section_title(ox, oy, "19. KEY TERMS GLOSSARY FOR JUDGES"))

    # Category columns
    categories = [
        (
            "NEUROSCIENCE",
            BLUE_BG,
            BLUE_STROKE,
            [
                (
                    "Gamma Oscillations",
                    "30-100 Hz brain waves. Essential for\nmemory and attention. Generated by\nPV interneurons. Disrupted in AD.",
                ),
                (
                    "Theta Oscillations",
                    "4-8 Hz brain waves. Dominant during\nmemory encoding. Provides temporal\nwindows for gamma bursts.",
                ),
                (
                    "Phase-Amplitude Coupling",
                    "How gamma amplitude locks to theta\nphase. Measured by Modulation Index.\nHigh PAC = entrained brain.",
                ),
                (
                    "Neural Habituation",
                    "Brain tunes out repeated stimulus.\nResponse progressively weakens.\nThompson and Spencer, 1966.",
                ),
                (
                    "Entrainment",
                    "External stimulus drives brain to\noscillate at matching frequency.\n40 Hz sound drives gamma.",
                ),
                (
                    "Microglia",
                    "Brain immune cells activated by\n40 Hz stimulation. Clear amyloid\nplaques in Alzheimer's disease.",
                ),
            ],
        ),
        (
            "SIGNAL PROCESSING",
            ORANGE_BG,
            ORANGE_STROKE,
            [
                (
                    "Bandpass Filter",
                    "Passes frequencies in a range,\nblocks everything outside.\n4th-order Butterworth, zero-phase.",
                ),
                (
                    "Hilbert Transform",
                    "Extracts instantaneous phase and\namplitude envelope from a\nnarrowband signal.",
                ),
                (
                    "KL Divergence",
                    "Kullback-Leibler divergence.\nMeasures distance between two\nprobability distributions.",
                ),
                (
                    "Z-Score",
                    "Standard deviations from mean.\nz = (x - mean) / std.\nNormalizes across patients.",
                ),
                (
                    "Modulation Index (MI)",
                    "Tort et al., 2010. KL divergence\nnormalized by log(num_bins).\nQuantifies PAC strength.",
                ),
            ],
        ),
        (
            "MACHINE LEARNING",
            GREEN_BG,
            GREEN_STROKE,
            [
                (
                    "EEGNet",
                    "Compact CNN for EEG.\nTemporal then spatial convolutions.\nLawhern et al., 2018. 1,457 params.",
                ),
                (
                    "TCN",
                    "Temporal Convolutional Network.\nDilated causal convolutions.\nParallel, not sequential.",
                ),
                (
                    "Causal",
                    "Model cannot see future data.\nLeft-only padding ensures no leakage.\nEssential for real-time systems.",
                ),
                (
                    "Dilated Convolution",
                    "Kernel with gaps (dilation 1,2,4,8).\nExponentially growing receptive field.\nCaptures multi-scale patterns.",
                ),
                (
                    "R-squared",
                    "Fraction of variance explained.\n1.0 = perfect, 0.0 = predicting mean,\nNegative = worse than mean.",
                ),
                (
                    "Huber Loss",
                    "Quadratic for small errors, linear\nfor large errors. Robust to outliers\nin PAC values (delta=1.0).",
                ),
                (
                    "Overfitting",
                    "Model memorizes training data,\nfails on new data. More params\nwith little data = overfitting.",
                ),
            ],
        ),
        (
            "STUDY DESIGN",
            PURPLE_BG,
            PURPLE_STROKE,
            [
                (
                    "Subject-Level Split",
                    "No patient in multiple splits.\nPrevents memorization of\npatient-specific patterns.",
                ),
                (
                    "Offline Replay",
                    "Replay recorded EEG through\ncontroller post-hoc.\nCounterfactual analysis method.",
                ),
                (
                    "Hedges' g Effect Size",
                    "Standardized mean difference,\nbias-corrected. > 0.8 = large effect.\nAll our results are large.",
                ),
                (
                    "Wilcoxon Signed-Rank",
                    "Non-parametric paired test.\nDoes not assume normality.\nCompares same subjects across methods.",
                ),
                (
                    "Bootstrap CI",
                    "Resample data 1000 times.\nGet distribution of statistic.\n95% confidence bounds.",
                ),
            ],
        ),
    ]

    col_w = 300
    col_gap = 30
    start_y = oy + 60

    for ci, (cat_name, bg, stroke, terms) in enumerate(categories):
        cx = ox + ci * (col_w + col_gap)

        # Category header
        els += box_with_text(
            cx, start_y, col_w, 36, cat_name, None, bg=bg, stroke=stroke, title_size=14
        )

        # Terms
        for ti, (term, defn) in enumerate(terms):
            ty = start_y + 50 + ti * 100
            els += box_with_text(
                cx,
                ty,
                col_w,
                90,
                term,
                defn,
                bg="#ffffff",
                stroke=stroke,
                title_size=13,
                body_size=11,
                title_color=stroke,
            )

    return els


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN: Assemble and write
# ═══════════════════════════════════════════════════════════════════════════
def main():
    all_elements = []
    all_elements += build_section_2()
    all_elements += build_section_3()
    all_elements += build_section_6()
    all_elements += build_section_7()
    all_elements += build_section_11()
    all_elements += build_section_15()
    all_elements += build_section_19()

    excalidraw_data = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": all_elements,
        "appState": {
            "gridSize": 20,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }

    out_path = "docs/COMPREHENSIVE_PROJECT_MAP.excalidraw"
    with open(out_path, "w") as f:
        json.dump(excalidraw_data, f, indent=2)

    print(f"Generated {out_path}")
    print(f"  Total elements: {len(all_elements)}")
    print(f"  Sections: 7")
    print(f"  File size: {len(json.dumps(excalidraw_data)):,} bytes")


if __name__ == "__main__":
    main()
