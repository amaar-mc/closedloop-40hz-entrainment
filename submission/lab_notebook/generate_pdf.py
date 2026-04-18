"""
Generate a clean PDF lab notebook combining original + extension.
- Strips em-dashes (replaces with --)
- Moves Equipment/Materials/References to the end
- Embeds figures from results/figures/ at relevant points
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, Image, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

ROOT = Path(__file__).resolve().parent.parent.parent
ORIGINAL = ROOT / "CSEF" / "Lab Notebook" / "P10_Lab_Notebook_VFINAL.md"
EXTENSION = ROOT / "CSEF_presentation" / "notebook" / "lab_notebook_extension.md"
OUTPUT = ROOT / "CSEF_presentation" / "notebook" / "P10_Lab_Notebook_COMPLETE.pdf"
FIGURES = ROOT / "CSEF_figures"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="NB_Title", parent=styles["Title"],
        fontName="Times-Bold", fontSize=18, spaceAfter=6, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="NB_Subtitle", parent=styles["Normal"],
        fontName="Times-Roman", fontSize=12, alignment=TA_CENTER, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="NB_DateHeader", parent=styles["Heading2"],
        fontName="Times-Bold", fontSize=13, spaceBefore=18, spaceAfter=6,
        textColor=HexColor("#1a1a1a"),
    ))
    styles.add(ParagraphStyle(
        name="NB_SectionHeader", parent=styles["Heading3"],
        fontName="Times-Bold", fontSize=11, spaceBefore=10, spaceAfter=4,
        textColor=HexColor("#333333"),
    ))
    styles.add(ParagraphStyle(
        name="NB_Body", parent=styles["Normal"],
        fontName="Times-Roman", fontSize=10.5, leading=14, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="NB_Code", parent=styles["Code"],
        fontName="Courier", fontSize=8.5, leading=11,
        leftIndent=18, spaceAfter=8, spaceBefore=4,
        backColor=HexColor("#f5f5f5"),
    ))
    styles.add(ParagraphStyle(
        name="NB_TableCell", parent=styles["Normal"],
        fontName="Times-Roman", fontSize=9, leading=11,
    ))
    styles.add(ParagraphStyle(
        name="NB_TableHeader", parent=styles["Normal"],
        fontName="Times-Bold", fontSize=9, leading=11,
    ))
    styles.add(ParagraphStyle(
        name="NB_Caption", parent=styles["Normal"],
        fontName="Times-Italic", fontSize=9, leading=12,
        alignment=TA_CENTER, spaceAfter=10, spaceBefore=4,
        textColor=HexColor("#444444"),
    ))
    return styles


def strip_emdashes(text):
    """Replace all em-dashes with double hyphens."""
    return text.replace("\u2014", "--").replace("\u2013", "-")


def escape_xml(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def clean_md(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text


def md_to_para(line, styles):
    line = escape_xml(line)
    line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
    line = re.sub(r'\*(.+?)\*', r'<i>\1</i>', line)
    line = re.sub(r'`(.+?)`', r'<font name="Courier" size="9">\1</font>', line)
    return Paragraph(line, styles["NB_Body"])


def parse_table(lines, styles):
    rows = []
    for i, line in enumerate(lines):
        line = line.strip().strip("|")
        if re.match(r'^[\s\-|:]+$', line):
            continue
        cells = [c.strip() for c in line.split("|")]
        style_key = "NB_TableHeader" if i == 0 else "NB_TableCell"
        rows.append([Paragraph(escape_xml(clean_md(c)), styles[style_key]) for c in cells])
    if not rows:
        return None
    n_cols = max(len(r) for r in rows)
    for r in rows:
        while len(r) < n_cols:
            r.append(Paragraph("", styles["NB_TableCell"]))
    col_width = (6.5 * inch) / n_cols
    table = Table(rows, colWidths=[col_width] * n_cols, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#e8e8e8")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def add_figure(path, caption, styles, width=4.5, max_height=5.5):
    """Create a figure + caption block with aspect ratio preserved."""
    elements = []
    if path.exists():
        try:
            from PIL import Image as PILImage
            with PILImage.open(str(path)) as pil_img:
                native_w, native_h = pil_img.size
            aspect = native_h / native_w
        except Exception:
            aspect = 0.6
        target_w = width * inch
        target_h = target_w * aspect
        if target_h > max_height * inch:
            target_h = max_height * inch
            target_w = target_h / aspect
        img = Image(str(path), width=target_w, height=target_h)
        img.hAlign = "CENTER"
        elements.append(Spacer(1, 6))
        elements.append(img)
        elements.append(Paragraph(caption, styles["NB_Caption"]))
        elements.append(Spacer(1, 6))
    return elements


def process_md(md_text, styles):
    """Convert markdown to flowables, stripping em-dashes."""
    md_text = strip_emdashes(md_text)
    flowables = []
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped == "---":
            flowables.append(Spacer(1, 8))
            i += 1
            continue
        if stripped.startswith("# ") and not stripped.startswith("## "):
            flowables.append(Paragraph(escape_xml(stripped[2:].strip()), styles["NB_Title"]))
            i += 1
            continue
        if stripped.startswith("## "):
            flowables.append(Paragraph(escape_xml(clean_md(stripped[3:].strip())), styles["NB_DateHeader"]))
            i += 1
            continue
        if stripped.startswith("### "):
            flowables.append(Paragraph(escape_xml(clean_md(stripped[4:].strip())), styles["NB_SectionHeader"]))
            i += 1
            continue
        if stripped.startswith("#### "):
            flowables.append(Paragraph(escape_xml(clean_md(stripped[5:].strip())), styles["NB_SectionHeader"]))
            i += 1
            continue
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            if code_lines:
                code_text = escape_xml("\n".join(code_lines))
                flowables.append(Preformatted(code_text, styles["NB_Code"]))
            continue
        if stripped.startswith("|") and i + 1 < len(lines):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            tbl = parse_table(table_lines, styles)
            if tbl:
                flowables.append(Spacer(1, 4))
                flowables.append(tbl)
                flowables.append(Spacer(1, 4))
            continue
        if stripped.startswith("- "):
            text = stripped[2:].strip()
            flowables.append(md_to_para("  \u2022  " + text, styles))
            i += 1
            continue
        if re.match(r'^\d+\.\s', stripped):
            num = re.match(r'^(\d+)', stripped).group(1)
            text = re.sub(r'^\d+\.\s*', '', stripped)
            flowables.append(md_to_para(f"  {num}.  " + text, styles))
            i += 1
            continue
        flowables.append(md_to_para(stripped, styles))
        i += 1
    return flowables


def split_at_section(flowables, section_name):
    """Split flowables into (before, section_content) at a heading containing section_name."""
    before = []
    section = []
    in_section = False
    for f in flowables:
        text = getattr(f, 'text', '')
        if section_name.lower() in text.lower() and not in_section:
            in_section = True
            section.append(f)
            continue
        if in_section:
            section.append(f)
        else:
            before.append(f)
    return before, section


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.drawCentredString(4.25 * inch, 0.5 * inch, f"{doc.page}")
    canvas.restoreState()


def main():
    styles = build_styles()
    original_text = ORIGINAL.read_text(encoding="utf-8")
    extension_text = EXTENSION.read_text(encoding="utf-8")

    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=letter,
        topMargin=0.8 * inch, bottomMargin=0.8 * inch,
        leftMargin=1.0 * inch, rightMargin=1.0 * inch,
    )

    story = []

    # Title page
    story.append(Paragraph("Project P10 Research Log Notebook", styles["NB_Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment<br/>"
        "to Optimize Theta-Gamma Coupling in Alzheimer's Disease",
        styles["NB_Subtitle"],
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Amaar Chughtai", styles["NB_Subtitle"]))
    story.append(Paragraph("Valley Christian High School", styles["NB_Subtitle"]))
    story.append(Paragraph("California Science &amp; Engineering Fair 2026", styles["NB_Subtitle"]))
    story.append(Paragraph("Notebook Timeline: January 15, 2026 - April 8, 2026", styles["NB_Subtitle"]))
    story.append(Spacer(1, 24))

    # Process original notebook
    original_all = process_md(original_text, styles)

    # Filter out title block from original
    skip_strings = [
        "Project P10", "Personalized Deep", "Theta-Gamma",
        "Amaar Chughtai", "Valley Christian", "Synopsys Science",
        "Notebook Timeline",
    ]

    # Separate Equipment/Materials/References from the body
    body_flowables = []
    appendix_flowables = []
    in_appendix = False
    skip_title = True

    for f in original_all:
        text = getattr(f, 'text', '')

        # Skip original title block
        if any(s in text for s in skip_strings):
            continue

        # Detect Equipment/Materials/References sections
        if 'Equipment and Materials' in text or 'References' in text:
            in_appendix = True

        if in_appendix:
            appendix_flowables.append(f)
            continue

        if skip_title:
            if 'January 15, 2026' in text:
                skip_title = False
                body_flowables.append(f)
            continue

        body_flowables.append(f)

    # Add original body to story
    for f in body_flowables:
        story.append(f)

    # Poster figures section at the end of original body
    story.append(PageBreak())
    story.append(Paragraph("Poster Figures (from the printed CSEF poster)", styles["NB_DateHeader"]))
    story.append(Spacer(1, 8))

    story.extend(add_figure(
        FIGURES / "figure1.png",
        "Figure 1: Fixed vs. Adaptive Stimulation Scheduling. Fixed schedule achieves 45% alignment; "
        "the adaptive TCN controller achieves 72% by targeting periods of genuine therapeutic need.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure2.png",
        "Figure 2: Phase-Amplitude Coupling (PAC) Mechanism. Theta rhythm (4-8 Hz) phase modulates "
        "gamma amplitude (38-42 Hz). Strong PAC equals high Modulation Index, computed via Tort 2010.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure3.png",
        "Figure 3: Fixed vs. Adaptive Stimulation Scheduling (detailed). Fixed schedule treats every "
        "moment the same; adaptive schedule uses TCN forecasts to target low-PAC windows.",
        styles, width=5.0
    ))

    # Continue into extension (no label, just flows naturally)

    # Process extension
    extension_all = process_md(extension_text, styles)

    # Separate extension body from its references/appendix
    ext_body = []
    ext_appendix = []
    ext_in_appendix = False
    ext_skip_header = True

    for f in extension_all:
        text = getattr(f, 'text', '')
        if any(s in text for s in ["Additional References", "Equipment"]):
            ext_in_appendix = True
        if ext_in_appendix:
            ext_appendix.append(f)
            continue
        if ext_skip_header:
            if 'March 24' in text:
                ext_skip_header = False
                ext_body.append(f)
            continue
        ext_body.append(f)

    for f in ext_body:
        story.append(f)

    # Remaining CSEF poster figures after extension body
    story.append(Spacer(1, 8))

    story.extend(add_figure(
        FIGURES / "figure4.png",
        "Figure 4: Feature Ablation, 73 to 12 Features. All 73 features gives test R2 = -0.025 (fails). "
        "Spectral-only gives R2 = -0.420 (worse, these features encode patient-specific anatomy). "
        "PAC + Stim with 12 features gives R2 = 0.606, a five-fold improvement.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure5.png",
        "Figure 5: System Architecture Flowchart. Complete closed-loop pipeline from patient EEG through "
        "EEGNet (1,457 params) PAC estimation, 12-feature extraction, Causal TCN (5,154 params) forecasting, "
        "and audio stimulation delivery. Total prediction inference time under 50 ms.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure6.png",
        "Figure 6: Prediction Horizon Sweep. At 1-2 seconds, persistence baseline is competitive. At 3-10 "
        "seconds, baselines collapse while the TCN maintains R2 = 0.37-0.67. The 5-second operating point "
        "sits squarely in the TCN advantage zone.",
        styles, width=5.0
    ))

    story.extend(add_figure(
        FIGURES / "figure7.png",
        "Figure 7: Real-Data Controller Timeline, Sub-15 (Test Set). Same patient EEG, same threshold, same "
        "hysteresis. Only difference: reactive uses current PAC, TCN uses predicted PAC 5 seconds ahead. "
        "TCN catches decline earlier and avoids wasted stim on high-PAC windows.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure8.png",
        "Figure 8: Dataset Overview. (A) 7 frontal EEG channels selected from 19-channel 10-20 montage, "
        "250 Hz. (B) Stimulus (40 Hz AM) and Rest protocol, 40s on / 20s off, with 2-second analysis windows. "
        "(C) Subject-level train/val/test split, 24/5/6. 17,283 total windows.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure9.png",
        "Figure 9: Full Training and Validation Protocol. EEGNet training (MSE, Adam, patience 15) hits the "
        "R2 = 0.287 data ceiling. Causal TCN training (Huber, AdamW, patience 20) with 12 features reaches "
        "R2 = 0.606 (5-seed mean). Shuffle-label control gives R2 = -0.332, confirming the signal is real.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure10.png",
        "Figure 10: Future Directions Roadmap. From offline replay validation (this project) to live EEG "
        "streaming, 30-60 minute sessions, reinforcement learning controller, and multi-biomarker control. "
        "At-home wearable therapy long term.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure11.png",
        "Figure 11: Consumer Hardware for Clinical Deployment. Muse 2 headband ($249, 4 dry electrodes) "
        "paired with standard audio headphones for 40 Hz amplitude-modulated auditory therapy. "
        "Total cost per patient under $300.",
        styles, width=4.0
    ))

    story.extend(add_figure(
        FIGURES / "figure12.png",
        "Figure 12: Metric Definitions. Low-PAC Stim Rate is the percentage of low-PAC windows that receive "
        "stimulation (sensitivity). High-PAC Rest Rate is the percentage of high-PAC windows where the "
        "controller rests (specificity). Alignment is the average of the two.",
        styles, width=5.0
    ))

    story.extend(add_figure(
        FIGURES / "figure13.png",
        "Figure 13: Controller Performance Comparison (N=35). TCN predictive achieves 72.1% alignment, "
        "82.6% low-PAC stim rate, and 61.6% high-PAC rest rate. Reactive trails at 64.5% alignment and "
        "51.7% low-PAC targeting. Hedges' g = 1.31 for alignment, 4.47 for low-PAC, all p < 0.001.",
        styles, width=5.5
    ))

    story.extend(add_figure(
        FIGURES / "figure14.png",
        "Figure 14: Per-Subject Clinical Utility. 35 of 35 subjects favor TCN over reactive (binomial p < 0.001). "
        "All points sit in the advantage region above the diagonal, including the 6 held-out test subjects.",
        styles, width=5.0
    ))

    # Appendix: Equipment, Materials, References (combined from both files)
    story.append(PageBreak())
    story.append(Paragraph("Equipment and Materials", styles["NB_DateHeader"]))
    story.append(Spacer(1, 6))
    story.append(md_to_para("Compute: MacBook Pro (Apple M1 Pro, 16 GB RAM), NVIDIA GeForce RTX 3080. All computation on local hardware.", styles))
    story.append(md_to_para("Software: Python 3.13, PyTorch 2.6.0, NumPy, SciPy, scikit-learn, h5py, MNE-Python, Streamlit, reportlab. Version control with Git.", styles))
    story.append(md_to_para("Dataset: OpenNeuro ds005048 (Lahijanian et al., 2024). 35 elderly dementia patients, 7 frontal EEG channels, 250 Hz. Alternating stimulus (40 Hz AM auditory) and rest epochs. 17,283 two-second windows. Subject-level splits: 24 train / 5 val / 6 test. All data used under open access license.", styles))
    story.append(md_to_para("Hardware demo: Muse 2 consumer EEG headband ($249, 4 dry electrodes), standard headphones, laptop running controller web application. Total cost under $300 per patient.", styles))

    story.append(Spacer(1, 12))
    story.append(Paragraph("References", styles["NB_DateHeader"]))
    story.append(Spacer(1, 6))

    # References match the poster board [1]-[8] plus additional sources used in the extension
    refs = [
        "[1] Iaccarino, H. F. et al. (2016). Gamma frequency entrainment attenuates amyloid load and modifies microglia. Nature, 540(7632), 230-235.",
        "[2] Martorell, A. J. et al. (2019). Multi-sensory gamma stimulation ameliorates Alzheimer's-associated pathology and improves cognition. Cell, 177(2), 256-271.",
        "[3] Tort, A. B. L. et al. (2010). Measuring phase-amplitude coupling between neuronal oscillations of different frequencies. Journal of Neurophysiology, 104(2), 1195-1210.",
        "[4] Lawhern, V. J. et al. (2018). EEGNet: A compact convolutional neural network for EEG-based brain-computer interfaces. Journal of Neural Engineering, 15(5), 056013.",
        "[5] Lahijanian, M. et al. (2024). Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients. Scientific Reports, 14, 13153.",
        "[6] Thompson, R. F. &amp; Spencer, W. A. (1966). Habituation: A model phenomenon for the study of neuronal substrates of behavior. Psychological Review, 73(1), 16-43.",
        "[7] Chan, D. et al. (2025). Long-term safety and tolerability of gamma sensory stimulation for Alzheimer's disease. Alzheimer's &amp; Dementia, 21(10), e70792.",
        "[8] Fortunato et al. (2023). Non-responder rates in auditory gamma entrainment studies. Frontiers in Integrative Neuroscience, 17.",
        "[9] Murdock, M. H. et al. (2024). Multisensory gamma stimulation promotes glymphatic clearance of amyloid. Nature, 627, 149-156.",
        "[10] Soula, M. et al. (2023). Forty-hertz light stimulation does not entrain native gamma oscillations in Alzheimer's disease model mice. Nature Neuroscience, 26, 570-578.",
        "[11] Meta AI. (2026). TRIBE V2: A Predictive Foundation Model for Brain Encoding. HuggingFace: facebook/tribev2.",
        "[12] Wilson, H. R. &amp; Cowan, J. D. (1972). Excitatory and inhibitory interactions in localized populations of model neurons. Biophysical Journal, 12(1), 1-24.",
    ]
    for ref in refs:
        story.append(Paragraph(ref, styles["NB_Body"]))
        story.append(Spacer(1, 2))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Generated: {OUTPUT}")
    print(f"Pages: {doc.page}")


if __name__ == "__main__":
    main()
