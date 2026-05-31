#!/usr/bin/env python3
"""Build a visually inspectable PDF proof from the audited MIT URTC manuscript."""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    Image,
    ListFlowable,
    ListItem,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from PIL import Image as PILImage


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "paper/conferences/mit_urtc_2026/draft/MANUSCRIPT.md"
OUTPUT = ROOT / "paper/conferences/mit_urtc_2026/draft/MIT_URTC_MANUSCRIPT.pdf"

PAGE_W, PAGE_H = letter
LEFT = 0.62 * inch
RIGHT = 0.62 * inch
TOP = 0.75 * inch
BOTTOM = 1.0 * inch
GAP = 0.25 * inch
USABLE_W = PAGE_W - LEFT - RIGHT
COLUMN_W = (USABLE_W - GAP) / 2
TITLE_H = 3.70 * inch


def inline(text: str) -> str:
    out = []
    for part in re.split(r"(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            out.append(f"<b>{escape(part[2:-2])}</b>")
        elif part.startswith("*") and part.endswith("*"):
            out.append(f"<i>{escape(part[1:-1])}</i>")
        elif part.startswith("`") and part.endswith("`"):
            out.append(escape(part[1:-1]))
        else:
            out.append(escape(part))
    return "".join(out)


def collect_section(lines: list[str], heading: str) -> list[str]:
    start = lines.index(heading) + 1
    out = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def parse_metadata(lines: list[str]) -> tuple[str, str, str, str]:
    title = lines[0].removeprefix("# ").strip()
    metadata = {}
    for line in lines[1:8]:
        match = re.match(r"\*\*(Author|Affiliation|Contact):\*\*\s*(.+?)\s*$", line)
        if match:
            metadata[match.group(1)] = match.group(2)
    return title, metadata["Author"], metadata["Affiliation"], metadata["Contact"]


def parse_abstract(lines: list[str]) -> tuple[str, str]:
    section = collect_section(lines, "## Abstract")
    abstract_lines, keyword_lines = [], []
    in_keywords = False
    for line in section:
        if line.startswith("**Keywords:**"):
            in_keywords = True
            keyword_lines.append(line.split("**Keywords:**", 1)[1].strip())
        elif in_keywords:
            keyword_lines.append(line.strip())
        else:
            abstract_lines.append(line.strip())
    return " ".join(filter(None, abstract_lines)), " ".join(filter(None, keyword_lines))


def make_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=18,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "center": ParagraphStyle(
            "Center",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=11,
            alignment=TA_CENTER,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=10.0,
            alignment=TA_JUSTIFY,
            spaceAfter=0.5,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=11,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=1,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=styles["Normal"],
            fontName="Times-Italic",
            fontSize=10,
            leading=11,
            alignment=TA_LEFT,
            spaceBefore=3,
            keepWithNext=True,
        ),
        "table": ParagraphStyle(
            "Table",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=10.0,
            alignment=TA_CENTER,
        ),
        "table_left": ParagraphStyle(
            "TableLeft",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=10.0,
            alignment=TA_LEFT,
        ),
    }


def make_doc(title: str, author: str, keywords: str) -> BaseDocTemplate:
    def apply_metadata(canvas, _doc) -> None:
        canvas.setTitle(title)
        canvas.setAuthor(author)
        canvas.setSubject("MIT URTC technical paper manuscript")
        canvas.setKeywords(keywords)

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=TOP,
        bottomMargin=BOTTOM,
    )
    first_title = Frame(
        LEFT,
        PAGE_H - TOP - TITLE_H,
        USABLE_W,
        TITLE_H,
        id="first_title",
    )
    first_left = Frame(LEFT, BOTTOM, COLUMN_W, PAGE_H - TOP - BOTTOM - TITLE_H, id="first_left")
    first_right = Frame(
        LEFT + COLUMN_W + GAP,
        BOTTOM,
        COLUMN_W,
        PAGE_H - TOP - BOTTOM - TITLE_H,
        id="first_right",
    )
    left = Frame(LEFT, BOTTOM, COLUMN_W, PAGE_H - TOP - BOTTOM, id="left")
    right = Frame(LEFT + COLUMN_W + GAP, BOTTOM, COLUMN_W, PAGE_H - TOP - BOTTOM, id="right")
    doc.addPageTemplates(
        [
            PageTemplate(
                id="TitlePage",
                frames=[first_title, first_left, first_right],
                autoNextPageTemplate="Body",
                onPage=apply_metadata,
            ),
            PageTemplate(id="Body", frames=[left, right], onPage=apply_metadata),
        ]
    )
    return doc


def table_flowable(styles, caption: str, lines: list[str]):
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    header, body = rows[0], rows[2:]
    widths = [1.85 * inch, 0.62 * inch, 0.83 * inch] if len(header) == 3 else [
        1.15 * inch,
        0.50 * inch,
        0.55 * inch,
        0.55 * inch,
        0.55 * inch,
    ]
    data = [[Paragraph(f"<b>{inline(value).replace('R-squared', 'R2')}</b>", styles["table"]) for value in header]]
    for row in body:
        data.append(
            [
                Paragraph(inline(value.replace("**", "")), styles["table_left" if col == 0 else "table"])
                for col, value in enumerate(row)
            ]
        )
    caption_p = Paragraph(escape(caption.upper()), styles["h1"])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return [caption_p, table, Spacer(1, 2)]


def image_flowable(styles, alt: str, relative_path: str):
    image_path = (SOURCE.parent / relative_path).resolve()
    with PILImage.open(image_path) as image:
        width_px, height_px = image.size
    width = COLUMN_W
    height = width * height_px / width_px
    return [
        Image(str(image_path), width=width, height=height),
        Paragraph(f"<i>Figure 1. {escape(alt)}</i>", styles["table"]),
        Spacer(1, 2),
    ]


def build() -> None:
    lines = SOURCE.read_text().splitlines()
    title, author, affiliation, contact = parse_metadata(lines)
    abstract, keywords = parse_abstract(lines)
    styles = make_styles()
    story = [
        Paragraph(escape(title), styles["title"]),
        Paragraph(f"<b>{escape(author)}</b>", styles["center"]),
        Paragraph(escape(affiliation), styles["center"]),
        Paragraph(escape(contact), styles["center"]),
        Spacer(1, 8),
        Paragraph(f"<b><i>Abstract:</i></b> {inline(abstract)}", styles["body"]),
        Paragraph(f"<b><i>Keywords:</i></b> {inline(keywords)}", styles["body"]),
        FrameBreak(),
    ]

    body_lines = lines[lines.index("## I. Introduction") :]
    pending: list[str] = []
    pending_caption = ""
    i = 0

    def flush() -> None:
        nonlocal pending
        text = " ".join(line.strip() for line in pending).strip()
        if text:
            story.append(Paragraph(inline(text), styles["body"]))
        pending = []

    while i < len(body_lines):
        line = body_lines[i]
        if line.startswith("## "):
            flush()
            story.append(Paragraph(escape(line[3:].strip().upper()), styles["h1"]))
            i += 1
        elif line.startswith("### "):
            flush()
            story.append(Paragraph(escape(line[4:].strip()), styles["h2"]))
            i += 1
        elif line.startswith("**Table ") and line.endswith("**"):
            flush()
            pending_caption = line.strip("*")
            i += 1
        elif line.startswith("|"):
            flush()
            table_lines = []
            while i < len(body_lines) and body_lines[i].startswith("|"):
                table_lines.append(body_lines[i])
                i += 1
            story.extend(table_flowable(styles, pending_caption, table_lines))
            pending_caption = ""
        elif match := re.match(r"^!\[(.+)\]\((.+)\)$", line):
            flush()
            story.extend(image_flowable(styles, match.group(1), match.group(2)))
            i += 1
        elif re.match(r"^\d+\.\s+", line):
            flush()
            items = []
            while i < len(body_lines) and re.match(r"^\d+\.\s+", body_lines[i]):
                text = re.sub(r"^\d+\.\s+", "", body_lines[i]).strip()
                i += 1
                while i < len(body_lines) and body_lines[i].startswith("   "):
                    text += " " + body_lines[i].strip()
                    i += 1
                items.append(ListItem(Paragraph(inline(text), styles["body"])))
            story.append(ListFlowable(items, bulletType="1", leftIndent=13, bulletFontSize=10))
        elif line.startswith("- "):
            flush()
            items = []
            while i < len(body_lines) and body_lines[i].startswith("- "):
                text = body_lines[i][2:].strip()
                i += 1
                while i < len(body_lines) and body_lines[i].startswith("  "):
                    text += " " + body_lines[i].strip()
                    i += 1
                items.append(ListItem(Paragraph(inline(text.rstrip(";")), styles["body"])))
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=13, bulletFontSize=10))
        elif not line.strip():
            flush()
            i += 1
        else:
            pending.append(line)
            i += 1
    flush()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    make_doc(title, author, keywords).build(story)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
