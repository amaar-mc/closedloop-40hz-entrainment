#!/usr/bin/env python3
"""
Generate print-ready facility flyer PDF using reportlab.

Usage:
    python scripts/generate_flyer_pdf.py [--output PATH]

Output:
    docs/flyer/facility_flyer.pdf
"""
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "flyer" / "facility_flyer.pdf"
QR_APP = REPO_ROOT / "docs" / "flyer" / "qr_app.png"
QR_FORM = REPO_ROOT / "docs" / "flyer" / "qr_feedback.png"


def build_pdf(output_path: Path) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Image,
        Table,
        TableStyle,
    )
    from reportlab.lib.colors import HexColor

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "FlyerTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=HexColor("#1f77b4"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "FlyerHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=HexColor("#1f77b4"),
        spaceBefore=12,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "FlyerBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    caption_style = ParagraphStyle(
        "FlyerCaption",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey,
    )

    story = []

    story.append(Paragraph("NeuroCare 40Hz", title_style))
    story.append(
        Paragraph("Personalized Neural Entrainment Therapy", heading_style)
    )
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("What It Does", heading_style))
    story.append(
        Paragraph(
            "Gently restores 40 Hz brainwave patterns disrupted in Alzheimer's "
            "and MCI patients using non-invasive sound stimulation "
            "— automatically adjusted to each patient's brain state.",
            body_style,
        )
    )

    story.append(Paragraph("How It Works", heading_style))
    steps = [
        "Patient wears lightweight EEG headset during therapy session",
        "System continuously reads brain activity in real time",
        "AI predicts optimal stimulation timing 5–10 seconds ahead",
        "40 Hz audio stimulus activates when brain synchrony is lowest",
    ]
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {step}", body_style))

    story.append(Paragraph("Why It Matters", heading_style))
    bullets = [
        "Non-invasive: no drugs, no implants, no side effects",
        "Personalized: each session adapts to the patient's unique response",
        "Evidence-based: validated on EEG recordings from 35 participants",
        "Proactive: predicts the right moment before the window passes",
    ]
    for b in bullets:
        story.append(Paragraph(f"&bull; {b}", body_style))

    story.append(Paragraph("Key Result", heading_style))
    story.append(
        Paragraph(
            "<b>72% targeting accuracy</b> vs 64% reactive baseline — "
            "statistically significant improvement across 35 subjects "
            "(Cohen's d = 1.31, p &lt; 0.001)",
            body_style,
        )
    )

    # QR code section — two columns
    story.append(Spacer(1, 0.15 * inch))
    qr_size = 1.4 * inch

    def qr_cell(qr_path: Path, caption: str) -> list:
        if qr_path.exists():
            return [
                Image(str(qr_path), width=qr_size, height=qr_size),
                Paragraph(caption, caption_style),
            ]
        else:
            placeholder = Paragraph(f"[QR: {caption}]", caption_style)
            return [Spacer(qr_size, qr_size), placeholder]

    app_cell = qr_cell(QR_APP, "Scan to try the live demo")
    form_cell = qr_cell(QR_FORM, "Share your feedback")

    table = Table(
        [[app_cell[0], form_cell[0]], [app_cell[1], form_cell[1]]],
        colWidths=[3.5 * inch, 3.5 * inch],
    )
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(table)

    story.append(Spacer(1, 0.15 * inch))
    story.append(
        Paragraph(
            "Amaar Chughtai &middot; amaardevx@gmail.com &middot; CSEF 2026",
            caption_style,
        )
    )

    doc.build(story)
    print(f"[PASS] Flyer PDF generated: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate facility flyer PDF")
    parser.add_argument(
        "--output", default=str(DEFAULT_OUTPUT), help="Output PDF path"
    )
    args = parser.parse_args()
    build_pdf(Path(args.output))


if __name__ == "__main__":
    main()
