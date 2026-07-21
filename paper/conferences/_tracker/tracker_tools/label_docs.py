#!/usr/bin/env python3
"""
label_docs.py — organize submission docs IN PLACE (no file moves, so cross-references stay intact).

Three jobs:
  1. Inject an idempotent, clearly-delimited SUBMISSION-STATUS header block at the top of every
     submission doc, so draft/scaffold/final/reference status is unambiguous on every file.
  2. Write a per-venue _STATUS.md into each venue folder (phase, deadline, blockers, canonical file,
     next action).
  3. Write a master SUBMISSION_MANIFEST.md mapping every file -> venue -> role -> status -> gate.

Run:  python tracker_tools/label_docs.py --apply     (default is --dry-run preview)
Idempotent: re-running replaces the managed block between the sentinels; never duplicates or touches
the document body.

REPO_ROOT is auto-discovered; falls back to the path below when run from the workspace copy.
"""
from __future__ import annotations
import argparse, json, re, sys, datetime as dt
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACKER_DIR = HERE.parent
JSON_PATH = TRACKER_DIR / "submission_tracker.json"

# Repo root = the directory that contains paper/conferences/. When deployed at
# paper/conferences/_tracker/, that's parents[2]. Allow an override for testing.
def find_repo_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    p = HERE
    for up in (p.parents[2] if len(p.parents) > 2 else p, *p.parents):
        if (up / "paper" / "conferences").is_dir():
            return up
    return Path("/Users/amaarchughtai/Developer/research/closedloop-40hz-entrainment")

SENT_START = "<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->"
SENT_END = "<!-- SUBMISSION-STATUS:END -->"
BLOCK_RE = re.compile(re.escape(SENT_START) + r".*?" + re.escape(SENT_END) + r"\n?", re.S)

# ---- file-role classification by basename ----
def classify(basename: str, is_canonical: bool, integrity_flags: list[str]) -> tuple[str, str]:
    """Return (artifact_type, doc_status). doc_status in draft|scaffold|reference|final."""
    b = basename.lower()
    scaffold = "no-AI-text" in integrity_flags
    if b in ("manuscript.md",):
        return ("manuscript", "draft")
    if "full_paper" in b:
        return ("full-paper draft", "draft")
    if b == "submission_draft.md":
        atype = "submission draft (abstract/summary)"
        return (atype, "scaffold" if scaffold else "draft")
    if "report" in b and ("draft" in b or "blueprint" in b):
        return ("research report", "scaffold" if scaffold else "draft")
    if "blueprint" in b:
        return ("report blueprint", "scaffold" if scaffold else "reference")
    if "poster_layout" in b or ("poster" in b and "layout" in b):
        return ("poster layout", "reference")
    if "two_page" in b or "description" in b:
        return ("two-page description (primary artifact)", "draft")
    if "lightning" in b or "video_script" in b or "script" in b:
        return ("talk/video script", "reference")
    if "website" in b or "plan" in b or "board" in b or "checklist" in b or "forms" in b:
        return ("plan/checklist", "reference")
    return ("supporting document", "reference")

def build_file_index(tracker: dict) -> dict[str, dict]:
    """Map repo-relative path -> metadata for every canonical + extra file."""
    idx = {}
    for v in tracker["venues"]:
        files = [(v["canonical_file"], True)] + [(f, False) for f in v.get("extra_files", [])]
        for path, is_canon in files:
            if path.lower().endswith((".pdf", ".docx")):
                continue  # binaries: listed in manifest, no header injection
            atype, dstatus = classify(Path(path).name, is_canon, v.get("integrity_flags", []))
            idx[path] = {
                "venue_id": v["id"], "venue_name": v["venue_name"], "tier": v["tier"],
                "track": v["track"], "canonical": is_canon, "artifact_type": atype,
                "doc_status": dstatus, "current_gate": v["progress"]["current_gate"],
                "gate_pct": v["progress"]["pct"], "deadline": v.get("deadline"),
                "eligibility": v["eligibility_status"], "integrity_flags": v.get("integrity_flags", []),
                "status_label": v["status_label"], "priority_rank": v["priority_rank"],
            }
    return idx

print("label_docs helpers loaded")

DOC_STATUS_BADGE = {
    "draft":     "DRAFT — working draft, not submission-ready",
    "scaffold":  "SCAFFOLD ONLY — planning aid; final text MUST be human-authored (venue AI rules)",
    "reference": "REFERENCE — supporting material (layout/plan/script/checklist)",
    "final":     "FINAL — submission-ready / submitted",
}

def days_txt(deadline, today):
    if not deadline:
        return "no date posted"
    d = (dt.date.fromisoformat(deadline) - today).days
    return f"{deadline} ({'passed' if d < 0 else str(d)+'d'})"

def header_block(meta: dict, today: dt.date) -> str:
    flags = meta["integrity_flags"]
    flag_line = ""
    if flags:
        flag_line = "> ⚑ **Integrity:** " + ", ".join(flags) + "  \n"
    canon = "yes (primary submission file)" if meta["canonical"] else "no (supporting file)"
    gate = meta["current_gate"] or "—"
    lines = (
        f"{SENT_START}\n"
        f"> ### 📋 {meta['venue_name']} · priority #{meta['priority_rank']}\n"
        f"> **Doc status:** {DOC_STATUS_BADGE[meta['doc_status']]}  \n"
        f"> **Artifact type:** {meta['artifact_type']} · **Canonical:** {canon}  \n"
        f"> **Venue phase:** gate {gate} · {meta['gate_pct']}% to submission · **eligibility:** {meta['eligibility']} · label: `{meta['status_label']}`  \n"
        f"> **Deadline:** {days_txt(meta['deadline'], today)}  \n"
        f"{flag_line}"
        f"> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  \n"
        f"> **Last labeled:** {today.isoformat()} (auto — do not hand-edit this block)\n"
        f"{SENT_END}\n"
    )
    return lines

def inject_header(text: str, block: str) -> str:
    """Idempotent: replace existing managed block, else prepend. Preserves body exactly."""
    if BLOCK_RE.search(text):
        return BLOCK_RE.sub(block, text, count=1)
    sep = "\n" if not text.startswith("\n") else ""
    return block + sep + text

def per_venue_status_md(v: dict, files_for_venue: list[tuple[str, dict]], today: dt.date) -> str:
    L = [f"# _STATUS — {v['venue_name']}",
         "",
         f"> Auto-generated from `submission_tracker.json`. Priority **#{v['priority_rank']}** "
         f"(effective {v['scores']['effective']} / raw {v['scores']['composite']}).",
         "",
         f"- **Long name:** {v['long_name']}",
         f"- **Tier / track:** {v['tier']} — {v['track']}",
         f"- **Status label:** `{v['status_label']}`",
         f"- **Eligibility ({v['eligibility_status']}):** {v['eligibility_note']}",
         f"- **Deadline:** {days_txt(v.get('deadline'), today)}"
         + (f" · notif {v['notification']}" if v.get('notification') else "")
         + (f" · event {v['event_date']}" if v.get('event_date') else ""),
         f"- **Phase:** gate **{v['progress']['current_gate'] or '—'}** — {v['progress']['pct']}% to submission (G0–G8)",
         ]
    if v.get("deadline_note"):
        L.append(f"- **Deadline note:** {v['deadline_note']}")
    if v.get("integrity_flags"):
        L.append(f"- **Integrity flags:** {', '.join(v['integrity_flags'])}")
    L += ["", "## Gate status", "",
          "| Gate | Name | Status |", "|---|---|---|"]
    gmap = {g["id"]: g for g in TRACKER["workflow"]["gates"]}
    for gid in [g["id"] for g in TRACKER["workflow"]["gates"]]:
        st = v["gates"].get(gid, "todo")
        L.append(f"| {gid} | {gmap[gid]['name']} | {st} |")
    L += ["", "## Files in this venue", "", "| File | Role | Doc status |", "|---|---|---|"]
    for path, meta in files_for_venue:
        L.append(f"| `{Path(path).name}` | {meta['artifact_type']}{' · CANONICAL' if meta['canonical'] else ''} | {meta['doc_status']} |")
    # blockers / next action
    L += ["", "## Blockers"]
    if v.get("blockers"):
        for b in v["blockers"]:
            L.append(f"- ⛔ {b}")
    else:
        L.append("- none recorded")
    L += ["", "## Next action", "", f"> {v.get('notes','')}", ""]
    return "\n".join(L)

print("generators loaded")

def master_manifest_md(tracker: dict, file_index: dict, today: dt.date, missing: list, extra_binaries: list) -> str:
    L = ["# Submission Manifest — Master Index", "",
         f"> Auto-generated from `submission_tracker.json` on {today.isoformat()}. "
         f"Maps every submission file to its venue, role, and status. Do not hand-edit.", "",
         f"**{len(tracker['venues'])} venues · {len(file_index)} labeled text docs "
         f"· {len(extra_binaries)} binary artifacts (PDF/DOCX).**", "",
         "Legend — doc status: **DRAFT** (working) · **SCAFFOLD** (planning only; human must author final) "
         "· **REFERENCE** (layout/plan/script) · **FINAL** (submission-ready/submitted).", "",
         "## Master file map", "",
         "| Priority | Venue | File | Role | Canonical | Doc status | Venue gate | Deadline |",
         "|--:|---|---|---|:-:|---|:-:|---|"]
    rows = sorted(file_index.items(), key=lambda kv: (kv[1]["priority_rank"], not kv[1]["canonical"], kv[0]))
    for path, m in rows:
        L.append(f"| #{m['priority_rank']} | {m['venue_name']} | `{path}` | {m['artifact_type']} "
                 f"| {'✔' if m['canonical'] else ''} | {m['doc_status'].upper()} | {m['current_gate'] or '—'} "
                 f"| {days_txt(m['deadline'], today)} |")
    if extra_binaries:
        L += ["", "## Binary artifacts (not header-labeled)", "",
              "| Venue | File |", "|---|---|"]
        for vname, path in extra_binaries:
            L.append(f"| {vname} | `{path}` |")
    # pre-existing master docs reconciliation
    L += ["", "## Pre-existing master documents (superseded / linked)", "",
          "These earlier planning docs are retained for context. The tracker system now supersedes them "
          "as the live status source:", "",
          "| Document | Role now |", "|---|---|",
          "| `paper/conferences/CONFERENCE_APPLICATION_MATRIX_2026.md` | Rationale & source-of-record for venue selection, dates, and recommendations. **Superseded for live status** by the tracker. |",
          "| `paper/conferences/tailored_submissions_2026/SUBMISSION_PRIORITY_AND_STATUS.md` | Original priority narrative + hard gates. **Superseded for live status** by the tracker; hard-gate rules folded into claim boundaries + per-venue blockers. |",
          "| `paper/conferences/tailored_submissions_2026/COMPREHENSIVE_AUDIT_2026.md` | 2026-06-14 audit snapshot + local-evidence audit. Retained as an audit record; live compliance now tracked at gate G5. |",
          "| `paper/conferences/tailored_submissions_2026/README.md` | Folder use-order + global claim rules. Still valid; claim rules mirrored in the tracker. |",
          "| `paper/conferences/mit_urtc_2026/DECISION_REQUIRED.md` | Open eligibility question gating MIT URTC paper track. Reflected as the `blocked` eligibility on that venue. |",
          ""]
    if missing:
        L += ["## ⚠ Files referenced by tracker but not found on disk", ""]
        for path in missing:
            L.append(f"- `{path}`")
        L.append("")
    return "\n".join(L)

def main():
    global TRACKER
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run preview)")
    ap.add_argument("--repo-root", default=None)
    args = ap.parse_args()
    apply = args.apply
    today = dt.date.today()
    repo = find_repo_root(args.repo_root)
    TRACKER = json.loads(JSON_PATH.read_text())
    file_index = build_file_index(TRACKER)

    missing, wrote_headers, extra_binaries = [], [], []
    # collect binaries for manifest
    for v in TRACKER["venues"]:
        for path in [v["canonical_file"]] + v.get("extra_files", []):
            if path.lower().endswith((".pdf", ".docx")):
                extra_binaries.append((v["venue_name"], path))

    # 1. inject headers
    for path, meta in file_index.items():
        fpath = repo / path
        if not fpath.exists():
            missing.append(path); continue
        block = header_block(meta, today)
        orig = fpath.read_text()
        new = inject_header(orig, block)
        if new != orig:
            wrote_headers.append(path)
            if apply:
                fpath.write_text(new)

    # 2. per-venue _STATUS.md
    venue_files = {}
    for path, meta in file_index.items():
        venue_files.setdefault(meta["venue_id"], []).append((path, meta))
    status_written = []
    for v in TRACKER["venues"]:
        folder = repo / v["folder"]
        if not folder.is_dir():
            continue
        md = per_venue_status_md(v, venue_files.get(v["id"], []), today)
        outp = folder / "_STATUS.md"
        status_written.append(str(outp.relative_to(repo)))
        if apply:
            outp.write_text(md)

    # 3. master manifest
    manifest = master_manifest_md(TRACKER, file_index, today, missing, extra_binaries)
    manifest_path = repo / "paper" / "conferences" / "SUBMISSION_MANIFEST.md"
    if apply:
        manifest_path.write_text(manifest)

    print(f"repo root: {repo}")
    print(f"{'APPLIED' if apply else 'DRY-RUN'} — headers: {len(wrote_headers)} docs, "
          f"per-venue _STATUS.md: {len(status_written)}, manifest: {manifest_path.relative_to(repo)}")
    if missing:
        print(f"  MISSING ({len(missing)}):")
        for m in missing:
            print("   -", m)
    if not apply:
        print("\n(preview) header docs to write:")
        for p in wrote_headers:
            print("   +", p)
    return 0

TRACKER = None
if __name__ == "__main__":
    sys.exit(main())
