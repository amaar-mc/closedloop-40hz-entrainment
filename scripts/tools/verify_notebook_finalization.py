#!/usr/bin/env python3
"""Deterministic checks for the Phase 4/5 lab notebook finalization bundle."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_NOTEBOOKS_DIR = ROOT / "archive" / "notebooks"
NOTEBOOKS_DIR = ROOT / "submission" / "lab_notebook"

ORIGINAL_MD = ARCHIVE_NOTEBOOKS_DIR / "P10_Lab_Notebook_V1.md"
ORIGINAL_PDF = ARCHIVE_NOTEBOOKS_DIR / "P10_Lab_Notebook_V1.pdf"
CORRECTED_MD = ARCHIVE_NOTEBOOKS_DIR / "P10_Lab_Notebook_V2.md"
CORRECTED_PDF = ARCHIVE_NOTEBOOKS_DIR / "P10_Lab_Notebook_V2.pdf"
FINAL_MD = NOTEBOOKS_DIR / "P10_Lab_Notebook_V3.md"
GENERATOR_PY = NOTEBOOKS_DIR / "generate_notebook_pdf.py"

CHECK_NAMES = (
    "chronology",
    "preservation",
    "packaging",
)
QUICK_CHECKS = ("preservation", "packaging")
FULL_CHECKS = CHECK_NAMES

MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
DATE_HEADER_RE = re.compile(
    rf"^## ((?:{'|'.join(MONTH_NAMES)}) \d{{1,2}}, \d{{4}}):",
    re.MULTILINE,
)
# V3 uses "## Section N: Month Day, Year -- Title" format
SECTION_DATE_RE = re.compile(
    rf"^## Section \d+:\s+((?:{'|'.join(MONTH_NAMES)}) \d{{1,2}}, \d{{4}})",
    re.MULTILINE,
)
REPO_PATH_RE = re.compile(
    r"(?P<path>(?:\.planning|archive|docs|logs|models|results|scripts|submission)/[^`\s)\]]+)"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_fenced_code_blocks(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def report(ok: bool, message: str) -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {message}")
    return ok


def check_preservation() -> bool:
    ok_all = True

    ok_all &= report(
        ORIGINAL_MD.exists(),
        f"Original markdown preserved at {ORIGINAL_MD.relative_to(ROOT)}",
    )
    ok_all &= report(
        ORIGINAL_PDF.exists(),
        f"Original PDF preserved at {ORIGINAL_PDF.relative_to(ROOT)}",
    )
    ok_all &= report(
        CORRECTED_MD.exists(),
        f"Corrected markdown exists at {CORRECTED_MD.relative_to(ROOT)}",
    )
    ok_all &= report(
        CORRECTED_PDF.exists(),
        f"Corrected PDF exists at {CORRECTED_PDF.relative_to(ROOT)}",
    )
    ok_all &= report(
        FINAL_MD.exists(),
        f"Final V3 markdown exists at {FINAL_MD.relative_to(ROOT)}",
    )
    ok_all &= report(
        CORRECTED_MD.resolve() != ORIGINAL_MD.resolve(),
        "Corrected markdown does not overwrite the original markdown path",
    )
    ok_all &= report(
        CORRECTED_PDF.resolve() != ORIGINAL_PDF.resolve(),
        "Corrected PDF does not overwrite the original PDF path",
    )

    return ok_all


def extract_repo_paths(text: str) -> set[Path]:
    paths: set[Path] = set()
    for match in REPO_PATH_RE.finditer(text):
        raw_path = match.group("path").rstrip(".,:")
        candidate = ROOT / raw_path
        if candidate.suffix:
            paths.add(candidate)
    return paths


def check_packaging() -> bool:
    ok_all = True

    ok_all &= report(
        GENERATOR_PY.exists(),
        f"PDF generator exists at {GENERATOR_PY.relative_to(ROOT)}",
    )
    ok_all &= report(
        FINAL_MD.exists(),
        f"Final V3 markdown exists at generator contract path {FINAL_MD.relative_to(ROOT)}",
    )

    if GENERATOR_PY.exists():
        generator_text = read_text(GENERATOR_PY)
        ok_all &= report(
            "P10_Lab_Notebook_V3.md" in generator_text,
            "Generator contract references P10_Lab_Notebook_V3.md",
        )

    return ok_all


def check_chronology() -> bool:
    # Check V3 if it exists, otherwise fall back to V2
    target = FINAL_MD if FINAL_MD.exists() else CORRECTED_MD
    if not target.exists():
        return report(False, f"Missing notebook: {target.relative_to(ROOT)}")

    text = strip_fenced_code_blocks(read_text(target))

    # Try V3 section-based date headers first, then V2-style headers
    matches = SECTION_DATE_RE.findall(text)
    if not matches:
        matches = DATE_HEADER_RE.findall(text)
    if not matches:
        return report(
            True,
            "No active-day date headers yet; chronology check deferred until notebook is populated",
        )

    parsed_dates = [datetime.strptime(date_text, "%B %d, %Y") for date_text in matches]
    ok_all = report(
        True,
        f"Found {len(parsed_dates)} active-day date header(s) in {target.name}",
    )
    for previous, current in zip(parsed_dates, parsed_dates[1:]):
        ok_all &= report(
            current >= previous,
            f"Chronology is monotonic: {previous.strftime('%Y-%m-%d')} <= {current.strftime('%Y-%m-%d')}",
        )
    return ok_all


def run_selected_checks(checks: tuple[str, ...]) -> bool:
    handlers = {
        "chronology": check_chronology,
        "preservation": check_preservation,
        "packaging": check_packaging,
    }

    print("=" * 80)
    print("NOTEBOOK FINALIZATION VERIFIER")
    print("=" * 80)

    ok_all = True
    for name in checks:
        print(f"\n-- {name.upper()} --")
        ok_all &= handlers[name]()

    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)
    print("PASS" if ok_all else "FAIL")
    return ok_all


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify the Phase 4 notebook finalization bundle."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="Run fast bundle checks.")
    group.add_argument(
        "--full", action="store_true", help="Run all notebook finalization checks."
    )
    group.add_argument(
        "--check",
        choices=CHECK_NAMES,
        action="append",
        help="Run one specific check. Repeat to run multiple named checks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.full:
        checks = FULL_CHECKS
    elif args.check:
        checks = tuple(dict.fromkeys(args.check))
    else:
        checks = QUICK_CHECKS

    ok = run_selected_checks(checks)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
