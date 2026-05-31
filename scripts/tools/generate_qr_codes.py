#!/usr/bin/env python3
"""
Generate QR code PNGs for the caregiver app URL and pilot feedback Google Form URL.

Usage:
    python scripts/tools/generate_qr_codes.py --app-url URL --form-url URL [--output-dir PATH]
    python scripts/tools/generate_qr_codes.py --check   # verify output files exist

Outputs:
    submission/flyer/qr_app.png       -- QR code for the Streamlit app
    submission/flyer/qr_feedback.png  -- QR code for the pilot feedback Google Form
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "submission" / "flyer"


def make_qr(url: str, output_path: Path) -> None:
    import qrcode

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path))
    print(f"[PASS] QR saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate QR code PNGs")
    parser.add_argument("--app-url", help="Streamlit app URL")
    parser.add_argument("--form-url", help="Google Form URL")
    parser.add_argument(
        "--output-dir", default=str(DEFAULT_OUTPUT), help="Output directory"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check output files exist"
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    app_qr = out_dir / "qr_app.png"
    form_qr = out_dir / "qr_feedback.png"

    if args.check:
        missing = [str(p) for p in [app_qr, form_qr] if not p.exists()]
        if missing:
            print(f"[FAIL] Missing QR files: {missing}")
            raise SystemExit(1)
        print("[PASS] QR files present")
        raise SystemExit(0)

    if not args.app_url and not args.form_url:
        print("[FAIL] No URLs provided. Use --app-url and --form-url.")
        raise SystemExit(1)

    if args.app_url:
        make_qr(args.app_url, app_qr)
    if args.form_url:
        make_qr(args.form_url, form_qr)


if __name__ == "__main__":
    main()
