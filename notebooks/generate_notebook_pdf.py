#!/usr/bin/env python3
"""Generate a professional research notebook PDF from markdown content."""

import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Register Times New Roman from .ttc ---
from reportlab.pdfbase.ttfonts import TTFont
import subprocess, tempfile, os

# Extract individual TTF faces from the .ttc collection
TTC_PATH = "/System/Library/Fonts/Times.ttc"
FONT_DIR = tempfile.mkdtemp()


def register_times_fonts():
    """Register Times New Roman fonts, falling back to built-in Times if needed."""
    try:
        # Try subfont indices from .ttc
        pdfmetrics.registerFont(TTFont("TimesNR", TTC_PATH, subfontIndex=0))
        pdfmetrics.registerFont(TTFont("TimesNR-Bold", TTC_PATH, subfontIndex=1))
        pdfmetrics.registerFont(TTFont("TimesNR-Italic", TTC_PATH, subfontIndex=2))
        pdfmetrics.registerFont(TTFont("TimesNR-BoldItalic", TTC_PATH, subfontIndex=3))
        pdfmetrics.registerFontFamily(
            "TimesNR",
            normal="TimesNR",
            bold="TimesNR-Bold",
            italic="TimesNR-Italic",
            boldItalic="TimesNR-BoldItalic",
        )
        return "TimesNR"
    except Exception as e:
        print(f"Warning: Could not load .ttc fonts ({e}), using built-in Times-Roman")
        return "Times-Roman"


FONT_FAMILY = register_times_fonts()
FONT_BOLD = FONT_FAMILY + "-Bold" if FONT_FAMILY == "TimesNR" else "Times-Bold"
FONT_ITALIC = FONT_FAMILY + "-Italic" if FONT_FAMILY == "TimesNR" else "Times-Italic"

# --- Colors ---
DARK_BLUE = HexColor("#1a3c5e")
LIGHT_GRAY = HexColor("#f0f0f0")
MED_GRAY = HexColor("#d0d0d0")
TABLE_HEADER_BG = HexColor("#2c5f8a")
TABLE_ALT_ROW = HexColor("#eaf2f8")

# --- Page dimensions ---
PAGE_W, PAGE_H = letter
MARGIN = 1 * inch


# --- Styles ---
def make_styles():
    s = {}
    s["title"] = ParagraphStyle(
        "Title",
        fontName=FONT_BOLD,
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=6,
        leading=20,
    )
    s["subtitle"] = ParagraphStyle(
        "Subtitle",
        fontName=FONT_FAMILY,
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=15,
    )
    s["section"] = ParagraphStyle(
        "Section",
        fontName=FONT_BOLD,
        fontSize=14,
        alignment=TA_LEFT,
        spaceBefore=18,
        spaceAfter=8,
        leading=17,
        textColor=DARK_BLUE,
    )
    s["subsection"] = ParagraphStyle(
        "Subsection",
        fontName=FONT_BOLD,
        fontSize=12,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        leading=15,
    )
    s["body"] = ParagraphStyle(
        "Body",
        fontName=FONT_FAMILY,
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=13.5,
        firstLineIndent=0,
    )
    s["bullet"] = ParagraphStyle(
        "Bullet",
        fontName=FONT_FAMILY,
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=4,
        leading=13.5,
        leftIndent=18,
        firstLineIndent=0,
        bulletIndent=6,
    )
    s["code"] = ParagraphStyle(
        "Code",
        fontName="Courier",
        fontSize=9,
        alignment=TA_LEFT,
        spaceAfter=6,
        leading=11,
        leftIndent=12,
        backColor=LIGHT_GRAY,
    )
    s["caption"] = ParagraphStyle(
        "Caption",
        fontName=FONT_ITALIC if FONT_FAMILY == "TimesNR" else "Times-Italic",
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=6,
        leading=12,
    )
    s["toc"] = ParagraphStyle(
        "TOC",
        fontName=FONT_FAMILY,
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=4,
        leading=14,
        leftIndent=12,
    )
    s["toc_header"] = ParagraphStyle(
        "TOCHeader",
        fontName=FONT_BOLD,
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=12,
        leading=17,
        textColor=DARK_BLUE,
    )
    return s


STYLES = make_styles()

# --- Header/Footer ---
HEADER_TEXT = "Project P10 Research Notebook \u2014 Amaar Chughtai"


def header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setFont(FONT_FAMILY if FONT_FAMILY == "TimesNR" else "Times-Roman", 9)
    canvas.setFillColor(HexColor("#555555"))
    canvas.drawString(MARGIN, PAGE_H - 0.6 * inch, HEADER_TEXT)
    canvas.setStrokeColor(MED_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE_H - 0.65 * inch, PAGE_W - MARGIN, PAGE_H - 0.65 * inch)
    # Page number
    canvas.drawCentredString(PAGE_W / 2, 0.5 * inch, str(doc.page))
    canvas.restoreState()


def first_page_header_footer(canvas, doc):
    """No header on title page, just page number."""
    canvas.saveState()
    canvas.setFont(FONT_FAMILY if FONT_FAMILY == "TimesNR" else "Times-Roman", 9)
    canvas.drawCentredString(PAGE_W / 2, 0.5 * inch, str(doc.page))
    canvas.restoreState()


# --- Markdown-to-flowable parser ---


def md_inline(text):
    """Convert inline markdown (**bold**, *italic*, `code`) to reportlab XML."""
    # Escape XML entities first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r'<font face="Courier" size="9">\1</font>', text)
    # Superscript for common patterns
    text = text.replace("R^2", "R\u00b2")
    text = text.replace("x 10^-6", "\u00d710\u207b\u2076")
    text = text.replace("x 10^-5", "\u00d710\u207b\u2075")
    text = text.replace("10^-6", "10\u207b\u2076")
    text = text.replace("10^-5", "10\u207b\u2075")
    text = text.replace("10^-8", "10\u207b\u2078")
    # Greek - only whole words or specific technical patterns
    text = re.sub(r"\btheta\b", "\u03b8", text)
    text = re.sub(r"\bgamma\b", "\u03b3", text)
    # pi only in math context like [-pi, pi]
    text = re.sub(r"\[-pi,", "[-\u03c0,", text)
    text = re.sub(r", pi\]", ", \u03c0]", text)
    text = re.sub(r"2\*pi\*", "2\u03c0", text)
    # Em-dash (the prompt says NO em-dashes, use en-dashes)
    text = text.replace(" -- ", " \u2013 ")
    text = text.replace("--", "\u2013")
    return text


def parse_table(lines):
    """Parse markdown table lines into a list of lists."""
    rows = []
    for line in lines:
        line = line.strip().strip("|")
        if re.match(r"^[\s\-:|]+$", line):
            continue  # separator row
        cells = [c.strip() for c in line.split("|")]
        rows.append(cells)
    return rows


def build_table_flowable(rows):
    """Create a reportlab Table with professional styling."""
    if not rows:
        return None

    n_cols = max(len(r) for r in rows)
    # Normalize row lengths
    for r in rows:
        while len(r) < n_cols:
            r.append("")

    # Convert cells to Paragraphs
    header_style = ParagraphStyle(
        "TH",
        fontName=FONT_BOLD,
        fontSize=9.5,
        alignment=TA_CENTER,
        textColor=white,
        leading=12,
    )
    cell_style = ParagraphStyle(
        "TD", fontName=FONT_FAMILY, fontSize=9.5, alignment=TA_LEFT, leading=12
    )

    table_data = []
    for i, row in enumerate(rows):
        styled_row = []
        for cell in row:
            cell_text = md_inline(cell)
            if i == 0:
                styled_row.append(Paragraph(cell_text, header_style))
            else:
                styled_row.append(Paragraph(cell_text, cell_style))
        table_data.append(styled_row)

    # Calculate column widths
    avail_width = PAGE_W - 2 * MARGIN
    col_width = avail_width / n_cols
    col_widths = [col_width] * n_cols

    t = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Style
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#999999")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    # Alternating row shading
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT_ROW))

    t.setStyle(TableStyle(style_cmds))
    return t


def parse_markdown_to_flowables(md_text):
    """Convert markdown text to a list of reportlab flowables."""
    lines = md_text.split("\n")
    flowables = []
    i = 0
    in_code_block = False
    code_lines = []
    table_lines = []
    in_table = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block
        if stripped.startswith("```"):
            if in_code_block:
                # End code block
                code_text = "\n".join(code_lines)
                code_text = (
                    code_text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                code_text = code_text.replace("\n", "<br/>")
                flowables.append(Spacer(1, 4))
                flowables.append(Paragraph(code_text, STYLES["code"]))
                flowables.append(Spacer(1, 4))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table detection
        if "|" in stripped and stripped.startswith("|"):
            table_lines.append(stripped)
            i += 1
            # Check if next line is also table
            if i < len(lines) and "|" in lines[i].strip():
                continue
            else:
                # End of table
                tbl = build_table_flowable(parse_table(table_lines))
                if tbl:
                    flowables.append(Spacer(1, 6))
                    flowables.append(tbl)
                    flowables.append(Spacer(1, 6))
                table_lines = []
                continue
        elif table_lines:
            # Flush remaining table
            tbl = build_table_flowable(parse_table(table_lines))
            if tbl:
                flowables.append(Spacer(1, 6))
                flowables.append(tbl)
                flowables.append(Spacer(1, 6))
            table_lines = []

        # Empty line
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # Title (# )
        if stripped.startswith("# ") and not stripped.startswith("## "):
            text = md_inline(stripped[2:])
            flowables.append(Paragraph(text, STYLES["title"]))
            i += 1
            continue

        # Section header (## )
        if stripped.startswith("## ") and not stripped.startswith("### "):
            text = md_inline(stripped[3:])
            # Add underline via XML
            flowables.append(Spacer(1, 8))
            flowables.append(Paragraph(f"<u>{text}</u>", STYLES["section"]))
            i += 1
            continue

        # Subsection header (### )
        if stripped.startswith("### "):
            text = md_inline(stripped[4:])
            flowables.append(Paragraph(text, STYLES["subsection"]))
            i += 1
            continue

        # Bullet points
        if stripped.startswith("- ") or stripped.startswith("* "):
            text = md_inline(stripped[2:])
            flowables.append(Paragraph(f"\u2022 {text}", STYLES["bullet"]))
            i += 1
            continue

        # Numbered list
        m = re.match(r"^(\d+)\.\s+(.*)", stripped)
        if m:
            num = m.group(1)
            text = md_inline(m.group(2))
            flowables.append(Paragraph(f"{num}. {text}", STYLES["bullet"]))
            i += 1
            continue

        # Regular paragraph
        # Collect continuation lines
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if (
                not next_line
                or next_line.startswith("#")
                or next_line.startswith("|")
                or next_line.startswith("```")
                or next_line.startswith("- ")
                or next_line.startswith("* ")
                or next_line == "---"
                or re.match(r"^\d+\.\s+", next_line)
            ):
                break
            para_lines.append(next_line)
            i += 1

        text = md_inline(" ".join(para_lines))
        flowables.append(Paragraph(text, STYLES["body"]))

    # Flush any remaining table
    if table_lines:
        tbl = build_table_flowable(parse_table(table_lines))
        if tbl:
            flowables.append(tbl)

    return flowables


def build_title_page():
    """Create title page flowables."""
    elements = []
    elements.append(Spacer(1, 2 * inch))
    elements.append(Paragraph("Project P10 Research Notebook", STYLES["title"]))
    elements.append(Spacer(1, 24))

    long_title = (
        "Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment "
        "to Optimize Theta-Gamma Phase-Amplitude Coupling in Alzheimer's Disease"
    )
    elements.append(Paragraph(long_title, STYLES["subtitle"]))
    elements.append(Spacer(1, 36))

    info_style = ParagraphStyle(
        "Info",
        fontName=FONT_FAMILY,
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=6,
        leading=16,
    )
    for line in [
        "Amaar Chughtai",
        "Valley Christian High School",
        "Synopsys Science and Engineering Fair 2026",
        "",
        "Research Period: December 10, 2025 \u2013 March 3, 2026",
        "Total Pages: 22",
    ]:
        if line:
            elements.append(Paragraph(line, info_style))
        else:
            elements.append(Spacer(1, 12))

    elements.append(PageBreak())
    return elements


def build_toc():
    """Create table of contents page."""
    elements = []
    elements.append(Paragraph("<u>Table of Contents</u>", STYLES["toc_header"]))
    elements.append(Spacer(1, 12))

    toc_entries = [
        ("Section 1:", "Background Research and Project Selection"),
        ("Section 2:", "Dataset Analysis and Technical Implementation"),
        ("Section 3:", "Model Architecture Evolution"),
        ("Section 4:", "Temporal Prediction Innovation"),
        ("Section 5:", "Horizon Sweep Analysis"),
        ("Section 6:", "Closed-Loop Controller Integration"),
        ("Section 7:", "Advanced Analysis and Validation"),
        ("Section 8:", "Statistical Rigor and Reproducibility"),
        ("Section 9:", "Conclusions and Future Work"),
        ("", "References"),
    ]

    for prefix, title in toc_entries:
        text = f"<b>{prefix}</b> {title}" if prefix else f"<b>{title}</b>"
        elements.append(Paragraph(text, STYLES["toc"]))

    elements.append(PageBreak())
    return elements


def main():
    md_path = "/Users/amaarchughtai/Developer/research/closedloop-40hz-entrainment/notebooks/P10_Lab_Notebook_V2.md"
    pdf_path = "/Users/amaarchughtai/Developer/research/closedloop-40hz-entrainment/notebooks/P10_Lab_Notebook_V2.pdf"

    # Read markdown
    with open(md_path, "r") as f:
        md_text = f.read()

    # Skip the title block in markdown (we build our own title page)
    # Find where "Section 1" starts
    sections_start = md_text.find("## Section 1:")
    if sections_start == -1:
        sections_start = md_text.find("## Background")

    body_md = md_text[sections_start:] if sections_start > 0 else md_text

    # Build document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.85 * inch,
        bottomMargin=0.75 * inch,
    )

    story = []

    # Title page
    story.extend(build_title_page())

    # Table of contents
    story.extend(build_toc())

    # Main body
    body_flowables = parse_markdown_to_flowables(body_md)
    story.extend(body_flowables)

    # Build PDF
    doc.build(story, onFirstPage=first_page_header_footer, onLaterPages=header_footer)
    print(f"PDF created: {pdf_path}")
    print(f"Total flowables: {len(story)}")


if __name__ == "__main__":
    main()
