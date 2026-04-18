#!/usr/bin/env python3
"""
Generate print-ready facility flyer PDF.
Clean single-column layout with generous spacing. No overlaps.

Usage:
    python scripts/generate_flyer_pdf.py [--output PATH]
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
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.colors import HexColor

    output_path.parent.mkdir(parents=True, exist_ok=True)
    W, H = letter
    c = canvas.Canvas(str(output_path), pagesize=letter)

    # --- Colors ---
    NAVY = HexColor("#1A2744")
    BLUE = HexColor("#2563EB")
    DARK = HexColor("#111827")
    MED = HexColor("#374151")
    LIGHT = HexColor("#6B7280")
    RULE = HexColor("#D1D5DB")
    BG_CARD = HexColor("#F3F4F6")
    WHITE = HexColor("#FFFFFF")
    TEAL = HexColor("#0F766E")
    GREEN_BG = HexColor("#ECFDF5")
    AMBER_BG = HexColor("#FFFBEB")

    mx = 0.75 * inch  # margins
    cw = W - 2 * mx   # content width
    cursor = H - 0.7 * inch  # top-down cursor

    def text(txt, x, y, font="Helvetica", size=10, color=DARK):
        c.setFont(font, size)
        c.setFillColor(color)
        c.drawString(x, y, txt)

    def centered(txt, y, font="Helvetica", size=10, color=DARK):
        c.setFont(font, size)
        c.setFillColor(color)
        c.drawCentredString(W / 2, y, txt)

    def rule(y):
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(mx, y, W - mx, y)

    # =========================================================
    # HEADER
    # =========================================================
    centered("NeuroCare 40Hz", cursor, "Helvetica-Bold", 30, NAVY)
    cursor -= 22
    centered("Personalized Neural Entrainment Therapy", cursor, "Helvetica", 12, BLUE)
    cursor -= 28
    rule(cursor)
    cursor -= 24

    # =========================================================
    # WHAT IT DOES
    # =========================================================
    text("WHAT IT DOES", mx, cursor, "Helvetica-Bold", 11, NAVY)
    cursor -= 18
    desc = [
        "Restores disrupted 40 Hz gamma brainwave patterns in Alzheimer's and",
        "MCI patients using non-invasive auditory stimulation that automatically",
        "adapts to each patient's brain state in real time.",
    ]
    for line in desc:
        text(line, mx, cursor, "Helvetica", 9.5, MED)
        cursor -= 14
    cursor -= 6
    text("No drugs.  No implants.  No side effects.", mx, cursor, "Helvetica-Bold", 9.5, TEAL)
    cursor -= 24
    rule(cursor)
    cursor -= 24

    # =========================================================
    # HOW IT WORKS (horizontal steps)
    # =========================================================
    text("HOW IT WORKS", mx, cursor, "Helvetica-Bold", 11, NAVY)
    cursor -= 24

    steps = [
        ("1", "WEAR", "Lightweight EEG headset"),
        ("2", "READ", "Real-time brain activity"),
        ("3", "PREDICT", "AI forecasts 5-10s ahead"),
        ("4", "STIMULATE", "40 Hz audio when needed"),
    ]
    step_w = cw / 4
    for i, (num, title, desc) in enumerate(steps):
        sx = mx + i * step_w + step_w / 2

        # Number
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(sx, cursor, num)

        # Title
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(sx, cursor - 16, title)

        # Desc
        c.setFillColor(LIGHT)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(sx, cursor - 28, desc)

    # Arrow connectors
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    for i in range(3):
        ax = mx + (i + 1) * step_w
        c.line(ax - 8, cursor - 2, ax + 8, cursor - 2)

    cursor -= 46
    rule(cursor)
    cursor -= 24

    # =========================================================
    # KEY RESULTS (two side-by-side stat cards)
    # =========================================================
    text("KEY RESULTS", mx, cursor, "Helvetica-Bold", 11, NAVY)
    cursor -= 16

    card_w = (cw - 16) / 2
    card_h = 72

    # Card 1: Targeting accuracy
    c.setFillColor(GREEN_BG)
    c.roundRect(mx, cursor - card_h, card_w, card_h, 6, fill=1, stroke=0)
    centered_x1 = mx + card_w / 2
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(HexColor("#047857"))
    c.drawCentredString(centered_x1, cursor - 32, "72%")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(MED)
    c.drawCentredString(centered_x1, cursor - 48, "Targeting Accuracy vs 64% reactive")
    c.setFont("Helvetica", 7)
    c.setFillColor(LIGHT)
    c.drawCentredString(centered_x1, cursor - 62, "d = 1.31, p < 0.001, N = 35")

    # Card 2: R2
    x2 = mx + card_w + 16
    c.setFillColor(AMBER_BG)
    c.roundRect(x2, cursor - card_h, card_w, card_h, 6, fill=1, stroke=0)
    centered_x2 = x2 + card_w / 2
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(HexColor("#B45309"))
    c.drawCentredString(centered_x2, cursor - 32, "R\u00b2 = 0.60")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(MED)
    c.drawCentredString(centered_x2, cursor - 48, "PAC prediction 5s ahead")
    c.setFont("Helvetica", 7)
    c.setFillColor(LIGHT)
    c.drawCentredString(centered_x2, cursor - 62, "5x improvement, held-out test subjects")

    cursor -= card_h + 20
    rule(cursor)
    cursor -= 24

    # =========================================================
    # WHY IT MATTERS
    # =========================================================
    text("WHY IT MATTERS", mx, cursor, "Helvetica-Bold", 11, NAVY)
    cursor -= 20

    bullets = [
        ("Non-invasive", "safe for daily use, no clinical setting required"),
        ("Personalized", "adapts to each patient's unique neural response"),
        ("Proactive", "predicts optimal timing before the window passes"),
        ("Validated", "tested on EEG recordings from 35 participants"),
    ]
    for bold_part, rest in bullets:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(NAVY)
        bw = c.stringWidth(bold_part, "Helvetica-Bold", 9)
        c.drawString(mx + 12, cursor, bold_part)
        c.setFont("Helvetica", 9)
        c.setFillColor(MED)
        c.drawString(mx + 12 + bw + 4, cursor, "-- " + rest)
        cursor -= 16

    cursor -= 16
    rule(cursor)
    cursor -= 24

    # =========================================================
    # QR CODES
    # =========================================================
    qr_size = 0.85 * inch
    qr_gap = 1.2 * inch

    qr1_x = W / 2 - qr_size - qr_gap / 2
    qr2_x = W / 2 + qr_gap / 2

    for qr_path, qr_x, label in [
        (QR_APP, qr1_x, "Try the Live Demo"),
        (QR_FORM, qr2_x, "Share Your Feedback"),
    ]:
        # Light background
        c.setFillColor(BG_CARD)
        c.roundRect(qr_x - 6, cursor - qr_size - 24, qr_size + 12, qr_size + 20, 4,
                     fill=1, stroke=0)
        if qr_path.exists():
            c.drawImage(ImageReader(str(qr_path)), qr_x, cursor - qr_size,
                         width=qr_size, height=qr_size, preserveAspectRatio=True)
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(NAVY)
        c.drawCentredString(qr_x + qr_size / 2, cursor - qr_size - 16, label)

    cursor -= qr_size + 40

    # =========================================================
    # FOOTER
    # =========================================================
    c.setFont("Helvetica", 7.5)
    c.setFillColor(LIGHT)
    c.drawCentredString(W / 2, 0.5 * inch,
                        "Amaar Chughtai  |  amaardevx@gmail.com  |  CSEF 2026")

    c.save()
    print(f"[PASS] Flyer PDF generated: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate facility flyer PDF")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output PDF path")
    args = parser.parse_args()
    build_pdf(Path(args.output))


if __name__ == "__main__":
    main()
