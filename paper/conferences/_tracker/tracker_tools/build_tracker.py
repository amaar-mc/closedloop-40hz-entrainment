#!/usr/bin/env python3
"""
build_tracker.py — regenerate the dashboard + Markdown mirror from submission_tracker.json.

submission_tracker.json is the SINGLE SOURCE OF TRUTH. Edit it, then run:

    python tracker_tools/build_tracker.py

Outputs (written next to the JSON):
    submission_dashboard.html  — self-contained interactive dashboard (no external deps)
    TRACKER.md                 — git-diffable Markdown mirror

Progress %, current gate, and priority are RE-DERIVED here from each venue's gate statuses, so you only
need to edit gate statuses / blockers / deadlines in the JSON; you do not hand-maintain the derived fields.
"""
from __future__ import annotations
import json, datetime as dt
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent                      # conf_tracker/ (or paper/conferences/ once deployed)
JSON_PATH = BASE / "submission_tracker.json"

# --- keep these in sync with bootstrap_tracker_data.py ---
WEIGHTS = {"urgency": 0.35, "fit": 0.25, "college_value": 0.25, "feasibility": 0.15}
ACTIONABILITY = {"ok": 1.0, "conditional": 0.8, "monitor": 0.8, "blocked": 0.45}


def days_until(deadline, today):
    if not deadline:
        return None
    return (dt.date.fromisoformat(deadline) - today).days


def urgency_score(deadline, today):
    d = days_until(deadline, today)
    if d is None: return 40
    if d < 0:  return 8
    if d <= 14: return 100
    if d <= 30: return 88
    if d <= 60: return 72
    if d <= 120: return 52
    return 36


def rederive(tracker, today=None):
    """Recompute scores, progress, current gate, days-to-deadline, and re-rank. Idempotent."""
    today = today or dt.date.today()
    work_gates = tracker["workflow"]["work_gates"]
    all_gates = [g["id"] for g in tracker["workflow"]["gates"]]
    for v in tracker["venues"]:
        gs = v["gates"]
        # progress
        considered = [g for g in work_gates if gs.get(g) != "na"]
        done = sum(1 for g in considered if gs.get(g) == "done")
        inprog = sum(1 for g in considered if gs.get(g) == "in_progress")
        blocked = [g for g in work_gates if gs.get(g) == "blocked"]
        total = len(considered) if considered else 1
        pct = round(100 * (done + 0.5 * inprog) / total)
        current = None
        for g in work_gates:
            if gs.get(g) in ("na", "done"):
                continue
            current = g
            break
        if gs.get("G9") == "done":
            current = "G10" if gs.get("G10") != "done" else "done"
        v["progress"] = {"pct": pct, "done": done, "in_progress": inprog,
                         "blocked_gates": blocked, "current_gate": current, "total_considered": total}
        # scores
        urg = urgency_score(v.get("deadline"), today)
        fit, col, fea = v["fit"] * 20, v["college_value"] * 20, v["feasibility"] * 20
        comp = (WEIGHTS["urgency"] * urg + WEIGHTS["fit"] * fit +
                WEIGHTS["college_value"] * col + WEIGHTS["feasibility"] * fea)
        act = ACTIONABILITY.get(v["eligibility_status"], 1.0)
        v["scores"] = {"urgency": urg, "fit": fit, "college_value": col, "feasibility": fea,
                       "composite": round(comp, 1), "actionability": act, "effective": round(comp * act, 1)}
        v["days_until_deadline"] = days_until(v.get("deadline"), today)
    tracker["venues"].sort(key=lambda x: (x["scores"]["effective"], x["scores"]["composite"]), reverse=True)
    for i, v in enumerate(tracker["venues"], 1):
        v["priority_rank"] = i
    tracker["rebuilt"] = today.isoformat()
    return tracker


# ---------------------------------------------------------------------------
# Markdown mirror
# ---------------------------------------------------------------------------
def gate_cell(status):
    return {"done": "✅", "in_progress": "🔸", "todo": "⬜", "blocked": "⛔", "na": "·"}.get(status, "?")


def generate_markdown(tracker):
    today = tracker.get("rebuilt", tracker["generated"])
    gates = tracker["workflow"]["gates"]
    work_gates = tracker["workflow"]["work_gates"]
    L = []
    L.append("# Submission Tracker — Markdown Mirror")
    L.append("")
    L.append(f"> **Auto-generated from `submission_tracker.json` — do not edit by hand.** "
             f"Rebuilt {today}. Edit the JSON and run `python tracker_tools/build_tracker.py`.")
    L.append("")
    L.append(f"**{tracker['project']['name']}**")
    L.append("")
    # summary counts
    ven = tracker["venues"]
    n_ok = sum(1 for v in ven if v["eligibility_status"] == "ok")
    n_cond = sum(1 for v in ven if v["eligibility_status"] in ("conditional", "monitor"))
    n_blk = sum(1 for v in ven if v["eligibility_status"] == "blocked")
    L.append(f"**{len(ven)} venues** — {n_ok} actionable · {n_cond} conditional/monitor · {n_blk} blocked/skip")
    L.append("")
    # next deadlines
    upcoming = sorted([v for v in ven if v.get("days_until_deadline") is not None and v["days_until_deadline"] >= 0],
                      key=lambda x: x["days_until_deadline"])
    if upcoming:
        L.append("**Next hard deadlines:** " + " · ".join(
            f"{v['venue_name']} ({v['deadline']}, in {v['days_until_deadline']}d)" for v in upcoming[:4]))
        L.append("")
    # priority table
    L.append("## Priority board")
    L.append("")
    L.append("| # | Venue | Tier | Eligibility | Deadline | In | Progress | Gate | Eff / Raw |")
    L.append("|--:|---|---|---|---|--:|--:|---|--:|")
    for v in ven:
        d = v.get("days_until_deadline")
        din = "—" if d is None else (f"{d}d" if d >= 0 else "passed")
        cg = v["progress"]["current_gate"] or "—"
        L.append(f"| {v['priority_rank']} | {v['venue_name']} | {v['tier']} | {v['eligibility_status']} "
                 f"| {v.get('deadline') or '—'} | {din} | {v['progress']['pct']}% | {cg} "
                 f"| {v['scores']['effective']} / {v['scores']['composite']} |")
    L.append("")
    # gate matrix
    L.append("## Gate matrix (G0–G8 work gates)")
    L.append("")
    L.append("Legend: ✅ done · 🔸 in-progress · ⬜ todo · ⛔ blocked · · n/a")
    L.append("")
    header = "| Venue | " + " | ".join(work_gates) + " |"
    sep = "|---|" + "|".join([":-:"] * len(work_gates)) + "|"
    L.append(header)
    L.append(sep)
    for v in ven:
        row = "| " + v["venue_name"] + " | " + " | ".join(gate_cell(v["gates"].get(g)) for g in work_gates) + " |"
        L.append(row)
    L.append("")
    # per-venue detail
    L.append("## Venue detail")
    L.append("")
    for v in ven:
        L.append(f"### {v['priority_rank']}. {v['venue_name']} — {v['status_label']}")
        L.append("")
        L.append(f"- **Long name:** {v['long_name']}")
        L.append(f"- **Tier / track:** {v['tier']} — {v['track']}")
        L.append(f"- **Deadline:** {v.get('deadline') or '—'}"
                 + (f" ({v['days_until_deadline']}d)" if v.get('days_until_deadline') is not None else "")
                 + (f" · notif {v['notification']}" if v.get('notification') else "")
                 + (f" · event {v['event_date']}" if v.get('event_date') else ""))
        if v.get("deadline_note"):
            L.append(f"- **Deadline note:** {v['deadline_note']}")
        L.append(f"- **Eligibility ({v['eligibility_status']}):** {v['eligibility_note']}")
        L.append(f"- **Priority:** effective {v['scores']['effective']} (raw {v['scores']['composite']}) "
                 f"— urgency {v['scores']['urgency']}, fit {v['scores']['fit']}, "
                 f"college {v['scores']['college_value']}, feasibility {v['scores']['feasibility']}, "
                 f"actionability ×{v['scores']['actionability']}")
        L.append(f"- **Progress:** {v['progress']['pct']}% · current gate "
                 f"{v['progress']['current_gate'] or '—'}"
                 + (f" · blocked at {', '.join(v['progress']['blocked_gates'])}" if v['progress']['blocked_gates'] else ""))
        if v.get("blockers"):
            L.append(f"- **Blockers:** " + "; ".join(v["blockers"]))
        if v.get("integrity_flags"):
            L.append(f"- **Integrity flags:** " + ", ".join(v["integrity_flags"]))
        L.append(f"- **Canonical file:** `{v['canonical_file']}`")
        if v.get("extra_files"):
            L.append(f"- **Other files:** " + ", ".join(f"`{f}`" for f in v["extra_files"]))
        if v.get("notes"):
            L.append(f"- **Notes:** {v['notes']}")
        L.append("")
    # workflow legend
    L.append("## Workflow gates")
    L.append("")
    L.append("| Gate | Name | Pass criterion |")
    L.append("|---|---|---|")
    for g in gates:
        L.append(f"| {g['id']} | {g['name']} | {g['pass']} |")
    L.append("")
    # claim boundaries
    L.append("## Claim boundaries (enforced at G3 & G5)")
    L.append("")
    for c in tracker["project"]["claim_boundaries"]:
        L.append(f"- {c}")
    L.append("")
    return "\n".join(L)


def _dashboard_links(tracker):
    """Add presentation-only relative links so hrefs resolve when the HTML is opened locally.

    The dashboard is written to BASE (…/paper/conferences/_tracker). File paths in the JSON are
    repo-root-relative. We rewrite each to a path relative to BASE so a plain file:// open works,
    and detect the repo root robustly (…/paper/conferences/_tracker -> up 3). Falls back to the
    raw path if the layout is unexpected. This mutates a COPY, not submission_tracker.json.
    """
    import os, copy
    t = copy.deepcopy(tracker)
    # repo root = the ancestor that contains paper/conferences
    repo_root = None
    for up in [BASE, *BASE.parents]:
        if (up / "paper" / "conferences").is_dir():
            repo_root = up
            break

    def rel(p):
        if not p or repo_root is None:
            return p
        try:
            return os.path.relpath((repo_root / p).resolve(), BASE)
        except Exception:
            return p

    for v in t["venues"]:
        v["canonical_link"] = rel(v.get("canonical_file"))
        v["extra_links"] = [rel(f) for f in v.get("extra_files", [])]
    return t


def generate_html(tracker):
    """Self-contained interactive dashboard. Data embedded as JSON; vanilla JS renders it."""
    payload = json.dumps(_dashboard_links(tracker), ensure_ascii=False)
    tpl = (HERE / "dashboard_template.html").read_text()
    return tpl.replace("/*__TRACKER_DATA__*/null", payload)


if __name__ == "__main__":
    tracker = json.loads(JSON_PATH.read_text())
    rederive(tracker)
    (BASE / "TRACKER.md").write_text(generate_markdown(tracker))
    print("wrote", BASE / "TRACKER.md")
    (BASE / "submission_dashboard.html").write_text(generate_html(tracker))
    print("wrote", BASE / "submission_dashboard.html")
