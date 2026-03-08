#!/usr/bin/env python3
"""Deterministic checks for the Phase 4 lab notebook finalization bundle."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = ROOT / "notebooks"

ORIGINAL_MD = NOTEBOOKS_DIR / "P10_Lab_Notebook_FINAL.md"
ORIGINAL_PDF = NOTEBOOKS_DIR / "P10_Lab_Notebook_FINAL.pdf"
CORRECTED_MD = NOTEBOOKS_DIR / "P10_Research_Log_Notebook_Corrected.md"
REVIEW_MD = NOTEBOOKS_DIR / "P10_Research_Log_Notebook_Corrected_REVIEW.md"
EVIDENCE_MD = NOTEBOOKS_DIR / "P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md"
GENERATOR_PY = NOTEBOOKS_DIR / "generate_notebook_pdf.py"

CHECK_NAMES = (
    "chronology",
    "preservation",
    "evidence",
    "checklist",
    "packaging",
)
QUICK_CHECKS = ("preservation", "checklist", "packaging")
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
REPO_PATH_RE = re.compile(
    r"(?P<path>(?:\.planning|archive|docs|logs|models|notebooks|results|scripts)/[^`\s)\]]+)"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def report(ok: bool, message: str) -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {message}")
    return ok


def check_preservation() -> bool:
    ok_all = True
    expected_files = (CORRECTED_MD, REVIEW_MD, EVIDENCE_MD)

    ok_all &= report(
        ORIGINAL_MD.exists(),
        f"Original markdown preserved at {ORIGINAL_MD.relative_to(ROOT)}",
    )
    ok_all &= report(
        ORIGINAL_PDF.exists(),
        f"Original PDF preserved at {ORIGINAL_PDF.relative_to(ROOT)}",
    )

    for path in expected_files:
        ok_all &= report(
            path.exists(), f"Review bundle file exists at {path.relative_to(ROOT)}"
        )

    for path in expected_files:
        ok_all &= report(
            path.resolve() != ORIGINAL_MD.resolve(),
            f"{path.name} does not overwrite the original markdown path",
        )
        ok_all &= report(
            path.resolve() != ORIGINAL_PDF.resolve(),
            f"{path.name} does not overwrite the original PDF path",
        )

    return ok_all


def check_checklist() -> bool:
    if not REVIEW_MD.exists():
        return report(False, f"Missing review sidecar: {REVIEW_MD.relative_to(ROOT)}")

    text = read_text(REVIEW_MD)
    required_sections = (
        "## Change Log",
        "## Unresolved Questions",
        "## Reviewer Checklist",
        "## Human Chronology and Fairness Review",
        "## Manual PDF Export After Approval",
    )
    required_phrases = (
        "approval anchor",
        "hindsight",
        "judge readability",
        "python notebooks/generate_notebook_pdf.py",
        "P10_Research_Log_Notebook_Corrected.pdf",
    )

    ok_all = True
    for section in required_sections:
        ok_all &= report(section in text, f"Review sidecar includes section: {section}")

    lowered = text.lower()
    for phrase in required_phrases:
        ok_all &= report(
            phrase.lower() in lowered,
            f"Review sidecar includes checklist/manual PDF phrase: {phrase}",
        )

    return ok_all


def check_evidence() -> bool:
    if not EVIDENCE_MD.exists():
        return report(False, f"Missing evidence map: {EVIDENCE_MD.relative_to(ROOT)}")

    text = read_text(EVIDENCE_MD)
    required_headers = (
        "| Entry ID | Entry Type | Notebook Target | Claim / Date / Figure | Source Path | Source Evidence | Disposition | Notes |",
        "## Disposition Legend",
        "## Entry Templates",
    )
    required_terms = (
        "claim",
        "date",
        "figure",
        "source path",
        "keep",
        "rewrite",
        "drop",
        "gap note",
    )

    ok_all = True
    for header in required_headers:
        ok_all &= report(header in text, f"Evidence map includes structure: {header}")

    lowered = text.lower()
    for term in required_terms:
        ok_all &= report(
            term in lowered, f"Evidence map includes required evidence term: {term}"
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
        CORRECTED_MD.exists(),
        f"Corrected markdown exists at generator contract path {CORRECTED_MD.relative_to(ROOT)}",
    )

    if GENERATOR_PY.exists():
        generator_text = read_text(GENERATOR_PY)
        ok_all &= report(
            "P10_Research_Log_Notebook_Corrected.md" in generator_text,
            "Generator contract references P10_Research_Log_Notebook_Corrected.md",
        )
        ok_all &= report(
            "P10_Research_Log_Notebook_Corrected.pdf" in generator_text,
            "Generator contract references P10_Research_Log_Notebook_Corrected.pdf",
        )

    if not REVIEW_MD.exists():
        return ok_all and report(
            False, f"Missing review sidecar: {REVIEW_MD.relative_to(ROOT)}"
        )

    referenced_paths = sorted(extract_repo_paths(read_text(REVIEW_MD)))
    ok_all &= report(
        bool(referenced_paths),
        "Review sidecar references local bundle files for packaging",
    )
    for path in referenced_paths:
        ok_all &= report(
            path.exists(), f"Referenced local file exists: {path.relative_to(ROOT)}"
        )

    return ok_all


def check_chronology() -> bool:
    if not CORRECTED_MD.exists():
        return report(
            False, f"Missing corrected notebook: {CORRECTED_MD.relative_to(ROOT)}"
        )

    text = read_text(CORRECTED_MD)
    matches = DATE_HEADER_RE.findall(text)
    if not matches:
        return report(
            True,
            "No active-day date headers yet; chronology check deferred until notebook is populated",
        )

    parsed_dates = [datetime.strptime(date_text, "%B %d, %Y") for date_text in matches]
    ok_all = True
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
        "evidence": check_evidence,
        "checklist": check_checklist,
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
