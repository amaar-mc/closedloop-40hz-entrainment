#!/usr/bin/env python3
"""
Generate print-ready facility flyer PDF using reportlab canvas for full
visual control — gradients, rounded boxes, custom typography, QR codes.

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


def _hex(h: str):
    """Convert '#RRGGBB' to reportlab Color."""
    from reportlab.lib.colors import HexColor
    return HexColor(h)


def _rounded_rect(c, x, y, w, h, r, fill_color, stroke_color=None):
    """Draw a rounded rectangle on canvas."""
    c.saveState()
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(0.5)
    else:
        c.setStrokeColor(fill_color)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1 if stroke_color else 0)
    c.restoreState()


def _gradient_rect(c, x, y, w, h, color_top, color_bot, steps=40):
    """Simulate a vertical gradient with thin horizontal strips."""
    from reportlab.lib.colors import Color
    rt, gt, bt = color_top.red, color_top.green, color_top.blue
    rb, gb, bb = color_bot.red, color_bot.green, color_bot.blue
    strip_h = h / steps
    for i in range(steps):
        frac = i / steps
        r = rt + (rb - rt) * frac
        g = gt + (gb - gt) * frac
        b = bt + (bb - bt) * frac
        c.setFillColor(Color(r, g, b))
        c.rect(x, y + h - (i + 1) * strip_h, w, strip_h + 0.5, fill=1, stroke=0)


def build_pdf(output_path: Path) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    output_path.parent.mkdir(parents=True, exist_ok=True)
    W, H = letter  # 612 x 792
    c = canvas.Canvas(str(output_path), pagesize=letter)

    # Colors
    NAVY = _hex("#1E3A5F")
    BLUE = _hex("#3B82F6")
    LIGHT_BLUE = _hex("#DBEAFE")
    TEAL = _hex("#0D9488")
    LIGHT_TEAL = _hex("#CCFBF1")
    WHITE = _hex("#FFFFFF")
    GRAY_50 = _hex("#F9FAFB")
    GRAY_100 = _hex("#F3F4F6")
    GRAY_600 = _hex("#4B5563")
    GRAY_800 = _hex("#1F2937")
    GREEN = _hex("#059669")
    AMBER = _hex("#D97706")

    margin = 0.6 * inch
    content_w = W - 2 * margin

    # === HEADER BANNER ===
    banner_h = 1.4 * inch
    banner_y = H - margin - banner_h
    _gradient_rect(c, margin, banner_y, content_w, banner_h, NAVY, _hex("#2563EB"))

    # Title text
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W / 2, banner_y + banner_h - 42, "NeuroCare 40Hz")
    c.setFont("Helvetica", 13)
    c.drawCentredString(W / 2, banner_y + banner_h - 62,
                        "Personalized Neural Entrainment Therapy")
    c.setFont("Helvetica", 9)
    c.setFillColor(_hex("#93C5FD"))
    c.drawCentredString(W / 2, banner_y + 14,
                        "Non-invasive  |  AI-powered  |  Real-time  |  Personalized")

    # === WHAT IT DOES (card) ===
    card_y = banner_y - 1.15 * inch
    card_h = 0.95 * inch
    _rounded_rect(c, margin, card_y, content_w, card_h, 8, LIGHT_BLUE, BLUE)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 14, card_y + card_h - 22, "What It Does")
    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRAY_800)
    lines = [
        "Restores disrupted 40 Hz gamma brainwave patterns in Alzheimer's and MCI patients",
        "using non-invasive auditory stimulation that automatically adapts to each patient's",
        "brain state in real time. No drugs. No implants. No side effects.",
    ]
    for i, line in enumerate(lines):
        c.drawString(margin + 14, card_y + card_h - 40 - i * 13, line)

    # === HOW IT WORKS (4 steps) ===
    steps_y = card_y - 1.65 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, steps_y + 1.45 * inch, "How It Works")

    steps = [
        ("1", "Wear", "Patient wears a lightweight\nEEG headset"),
        ("2", "Read", "System reads brain activity\nin real time"),
        ("3", "Predict", "AI predicts optimal timing\n5-10 seconds ahead"),
        ("4", "Stimulate", "40 Hz audio activates when\nbrain sync is lowest"),
    ]
    step_w = (content_w - 3 * 8) / 4
    for i, (num, title, desc) in enumerate(steps):
        sx = margin + i * (step_w + 8)
        sy = steps_y

        # Step box
        _rounded_rect(c, sx, sy, step_w, 1.3 * inch, 6, GRAY_50, _hex("#E5E7EB"))

        # Number circle
        circle_x = sx + step_w / 2
        circle_y = sy + 1.3 * inch - 20
        c.setFillColor(BLUE)
        c.circle(circle_x, circle_y, 11, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(circle_x, circle_y - 4, num)

        # Title
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(sx + step_w / 2, sy + 1.3 * inch - 42, title)

        # Description
        c.setFillColor(GRAY_600)
        c.setFont("Helvetica", 7.5)
        for j, dline in enumerate(desc.split("\n")):
            c.drawCentredString(sx + step_w / 2, sy + 1.3 * inch - 58 - j * 10, dline)

    # === KEY RESULTS (2 stat boxes) ===
    results_y = steps_y - 1.1 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, results_y + 0.9 * inch, "Key Results")

    stat_w = (content_w - 12) / 2

    # Stat 1: Targeting accuracy
    _rounded_rect(c, margin, results_y, stat_w, 0.75 * inch, 6, _hex("#F0FDF4"), GREEN)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(margin + stat_w / 2, results_y + 0.75 * inch - 32, "72%")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY_800)
    c.drawCentredString(margin + stat_w / 2, results_y + 0.75 * inch - 48,
                        "Targeting Accuracy (vs 64% reactive)")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRAY_600)
    c.drawCentredString(margin + stat_w / 2, results_y + 8,
                        "Cohen's d = 1.31, p < 0.001, N = 35")

    # Stat 2: Prediction R2
    sx2 = margin + stat_w + 12
    _rounded_rect(c, sx2, results_y, stat_w, 0.75 * inch, 6, _hex("#FFF7ED"), AMBER)
    c.setFillColor(AMBER)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(sx2 + stat_w / 2, results_y + 0.75 * inch - 32, "R\u00b2 = 0.60")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY_800)
    c.drawCentredString(sx2 + stat_w / 2, results_y + 0.75 * inch - 48,
                        "PAC Prediction (5s ahead, held-out subjects)")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRAY_600)
    c.drawCentredString(sx2 + stat_w / 2, results_y + 8,
                        "5x improvement over previous best (0.12)")

    # === WHY IT MATTERS (bullet points) ===
    why_y = results_y - 1.0 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, why_y + 0.85 * inch, "Why It Matters")

    bullets = [
        "Non-invasive — safe for daily use, no clinical setting required",
        "Personalized — adapts to each patient's unique neural response",
        "Proactive — predicts optimal timing before the window passes",
        "Validated — tested on EEG recordings from 35 participants",
    ]
    c.setFont("Helvetica", 9.5)
    for i, b in enumerate(bullets):
        by = why_y + 0.85 * inch - 20 - i * 16
        c.setFillColor(TEAL)
        c.circle(margin + 6, by + 3, 2.5, fill=1, stroke=0)
        c.setFillColor(GRAY_800)
        c.drawString(margin + 16, by, b)

    # === QR CODES ===
    qr_y = why_y - 1.25 * inch
    qr_size = 0.95 * inch

    # App QR
    qr_app_x = W / 2 - qr_size - 0.6 * inch
    _rounded_rect(c, qr_app_x - 8, qr_y - 8, qr_size + 16, qr_size + 40, 6,
                  GRAY_100, _hex("#D1D5DB"))
    if QR_APP.exists():
        c.drawImage(ImageReader(str(QR_APP)), qr_app_x, qr_y,
                     width=qr_size, height=qr_size, preserveAspectRatio=True)
    c.setFillColor(GRAY_800)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(qr_app_x + qr_size / 2, qr_y - 14, "Try the Live Demo")

    # Form QR
    qr_form_x = W / 2 + 0.6 * inch
    _rounded_rect(c, qr_form_x - 8, qr_y - 8, qr_size + 16, qr_size + 40, 6,
                  GRAY_100, _hex("#D1D5DB"))
    if QR_FORM.exists():
        c.drawImage(ImageReader(str(QR_FORM)), qr_form_x, qr_y,
                     width=qr_size, height=qr_size, preserveAspectRatio=True)
    c.setFillColor(GRAY_800)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(qr_form_x + qr_size / 2, qr_y - 14, "Share Your Feedback")

    # === FOOTER ===
    footer_y = 0.4 * inch
    c.setFillColor(GRAY_600)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, footer_y,
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
