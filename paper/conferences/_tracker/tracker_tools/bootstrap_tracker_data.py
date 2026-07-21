#!/usr/bin/env python3
"""
Bootstrap the submission_tracker.json single-source-of-truth from curated venue data.

Run ONCE to author the initial tracker. After that, edit submission_tracker.json by
hand (or re-run to reset) and use build_tracker.py to regenerate the dashboard + markdown.

Data is grounded in:
  paper/conferences/CONFERENCE_APPLICATION_MATRIX_2026.md
  paper/conferences/tailored_submissions_2026/SUBMISSION_PRIORITY_AND_STATUS.md
  paper/conferences/tailored_submissions_2026/COMPREHENSIVE_AUDIT_2026.md
  paper/data/key_results.md
"""
from __future__ import annotations
import json, datetime as dt
from pathlib import Path

TODAY = "2026-07-03"  # reference date used for initial gate assessment

# ---------------------------------------------------------------------------
# Stage-gate workflow model. Ordered pipeline every submission passes through.
# Mirrors how research groups actually run a paper to submission: draft ->
# review -> audit -> review-2 -> audit-2 -> copyedit -> production -> QA.
# ---------------------------------------------------------------------------
GATES = [
    {"id": "G0", "key": "outline",    "name": "Outline",
     "desc": "Scope, required components, and venue-fit structure locked.",
     "pass": "Section skeleton + component checklist exists and matches the venue call."},
    {"id": "G1", "key": "draft",      "name": "Draft",
     "desc": "Complete first draft of every required component.",
     "pass": "All required components drafted end to end; no [TODO] placeholders in body."},
    {"id": "G2", "key": "review1",    "name": "Review 1 (content)",
     "desc": "Narrative/structure/clarity review by a fresh read.",
     "pass": "Story arc, logical flow, and clarity issues logged and resolved."},
    {"id": "G3", "key": "audit1",     "name": "Audit 1 (claim/evidence)",
     "desc": "Every claim and number traced to key_results.md / repo artifacts.",
     "pass": "Claim->evidence map complete; no number without a source; no cross-generation mixing."},
    {"id": "G4", "key": "review2",    "name": "Review 2 (reviewer sim)",
     "desc": "Adversarial peer-review read simulating the venue's reviewers.",
     "pass": "Reviewer-style objections raised and either fixed or explicitly acknowledged as limitations."},
    {"id": "G5", "key": "audit2",     "name": "Audit 2 (compliance)",
     "desc": "Format, length, eligibility, integrity, and claim-boundary compliance.",
     "pass": "Length/format limits met; eligibility satisfied; no fabricated affiliation; retrospective claim boundaries held."},
    {"id": "G6", "key": "copyedit",   "name": "Copyedit + AI-tell pass",
     "desc": "Line editing and removal of AI-generated-writing tells.",
     "pass": "Passes AI_WRITING_TELLS_AND_AVOIDANCE.md checklist; human-authored voice; typos/grammar clean."},
    {"id": "G7", "key": "production", "name": "Production (format/proof)",
     "desc": "Convert to the venue's required artifact (PDF/DOCX/portal/poster) with figures.",
     "pass": "Final artifact in required format renders correctly with figures/refs embedded."},
    {"id": "G8", "key": "final_qa",   "name": "Final QA gate",
     "desc": "Submission-ready check: portal fields, attachments, signatures, disclosures.",
     "pass": "Every portal field, attachment, signature, and disclosure ready; last official-site refresh done."},
    {"id": "G9", "key": "submitted",  "name": "Submitted",
     "desc": "Submitted to the venue; confirmation captured.",
     "pass": "Submission confirmed; confirmation ID / email archived."},
    {"id": "G10","key": "decision",   "name": "Decision",
     "desc": "Outcome recorded (accept / reject / revise / withdraw).",
     "pass": "Outcome and any reviewer feedback recorded."},
]
GATE_IDS = [g["id"] for g in GATES]
# Work gates that count toward "progress to submission" (G0..G8). G9 = finish line.
WORK_GATES = GATE_IDS[:9]

STATUS_VALUES = ["done", "in_progress", "todo", "blocked", "na"]

def gates(done=(), in_progress=(), blocked=(), na=()):
    """Build a per-gate status dict; anything unspecified is 'todo'."""
    out = {}
    for gid in GATE_IDS:
        if gid in na:
            out[gid] = "na"
        elif gid in blocked:
            out[gid] = "blocked"
        elif gid in done:
            out[gid] = "done"
        elif gid in in_progress:
            out[gid] = "in_progress"
        else:
            out[gid] = "todo"
    return out

print("gates + helpers defined:", len(GATES), "gates")

# ---------------------------------------------------------------------------
# Venue records. Grounded in the matrix + audits. fit/college_value/feasibility
# are 1-5 editorial scores; deadlines are official where known.
# eligibility_status: ok | conditional | blocked | monitor
# ---------------------------------------------------------------------------
TSUB = "paper/conferences/tailored_submissions_2026"
URTC = "paper/conferences/mit_urtc_2026"

VENUES = [
  {
    "id": "ieee_spmb_2026", "venue_name": "IEEE SPMB 2026",
    "long_name": "IEEE Signal Processing in Medicine and Biology Symposium 2026",
    "folder": f"{TSUB}/ieee_spmb_2026",
    "canonical_file": f"{TSUB}/ieee_spmb_2026/FULL_PAPER_DRAFT.md",
    "extra_files": [f"{TSUB}/ieee_spmb_2026/SUBMISSION_DRAFT.md"],
    "tier": "reach-professional", "track": "Full paper or abstract (emailed IEEE 2-col PDF)",
    "deadline": "2026-07-01", "deadline_note": "2026 paper deadline 2026-07-01 has PASSED (today 2026-07-03). Effectively missed. Re-target SPMB 2027.",
    "notification": "2026-09-01", "event_date": "2026-12-05",
    "eligibility_status": "ok", "eligibility_note": "No high-school exclusion found; accepted work must be presented (virtual, no-fee).",
    "blockers": ["2026 deadline passed; never converted MD -> required IEEE 2-column PDF", "Single fixed split + single-seed backward-looking benchmark + Ridge tie will draw reviewer fire"],
    "fit": 5, "college_value": 4, "feasibility": 2,
    "integrity_flags": [],
    "status_label": "missed-2026 / re-target-2027",
    "gates": gates(done=["G0","G1"], in_progress=["G3"], na=[]),
    "notes": "Strongest professional technical fit. Submit to SPMB 2027 after a robustness pass (multi-seed, repeated splits) and after converting to the official 2-column PDF. Email to submit@ieeespmb.org.",
  },
  {
    "id": "mit_urtc_paper", "venue_name": "MIT URTC 2026 (paper)",
    "long_name": "MIT IEEE Undergraduate Research Technology Conference 2026 - Paper track",
    "folder": f"{URTC}",
    "canonical_file": f"{URTC}/draft/MANUSCRIPT.md",
    "extra_files": [f"{URTC}/draft/MIT_URTC_MANUSCRIPT.pdf", f"{URTC}/draft/MIT_URTC_MANUSCRIPT.docx", f"{URTC}/EVIDENCE_MAP.md", f"{URTC}/draft/CLAIM_AUDIT.md"],
    "tier": "target-if-eligible", "track": "Paper presentation (IEEE Xplore if accepted)",
    "deadline": None, "deadline_note": "2026 cycle NOT confirmed open; 2026 dates not posted. 2025 paper deadline was 2025-08-03. Refresh official site.",
    "notification": None, "event_date": None,
    "eligibility_status": "blocked", "eligibility_note": "High-school paper track requires a qualifying university relationship (faculty-mentored program, university-faculty mentorship, or substantial work with university students). Stored record = independent work, so blocked. Gated by DECISION_REQUIRED.md (unanswered).",
    "blockers": ["Paper-track eligibility unresolved (DECISION_REQUIRED.md)", "2026 cycle/dates not confirmed"],
    "fit": 5, "college_value": 5, "feasibility": 2,
    "integrity_flags": ["no-fabricated-affiliation"],
    "status_label": "blocked-eligibility",
    "gates": gates(done=["G0","G1","G2","G3","G6","G7"], in_progress=["G4"], blocked=["G5"]),
    "notes": "Manuscript is the most mature asset in the workspace (~13 audit passes, DOCX+PDF built). Do NOT submit the paper track unless a genuine, specific university relationship exists. Otherwise route the work through the poster/lightning entry.",
  },
  {
    "id": "mit_urtc_poster_lightning", "venue_name": "MIT URTC 2026 (poster/lightning)",
    "long_name": "MIT IEEE URTC 2026 - Poster or Lightning talk",
    "folder": f"{TSUB}/mit_urtc_poster_lightning",
    "canonical_file": f"{TSUB}/mit_urtc_poster_lightning/SUBMISSION_DRAFT.md",
    "extra_files": [f"{TSUB}/mit_urtc_poster_lightning/POSTER_LAYOUT_AND_LIGHTNING_SCRIPT.md"],
    "tier": "safety-target", "track": "Poster or Lightning talk (no IEEE Xplore)",
    "deadline": None, "deadline_note": "2026 dates not posted. 2025 poster/lightning deadline was 2025-09-05. Refresh official site.",
    "notification": None, "event_date": None,
    "eligibility_status": "ok", "eligibility_note": "Unaffiliated high-school students may be eligible for poster/lightning. Minor-at-conference: adult accompaniment.",
    "blockers": ["2026 dates not posted (monitor)"],
    "fit": 5, "college_value": 4, "feasibility": 4,
    "integrity_flags": [],
    "status_label": "strong-default",
    "gates": gates(done=["G0","G1"], in_progress=["G2","G3"]),
    "notes": "The safe MIT-branded default when paper eligibility is not clean. Abstract + poster layout + lightning script drafted.",
  },
  {
    "id": "bmes_hs_poster_expo", "venue_name": "BMES 2026 HS Poster Expo",
    "long_name": "BMES 2026 Annual Meeting - High School Poster Expo",
    "folder": f"{TSUB}/bmes_high_school_poster_expo",
    "canonical_file": f"{TSUB}/bmes_high_school_poster_expo/SUBMISSION_DRAFT.md",
    "extra_files": [f"{TSUB}/bmes_high_school_poster_expo/POSTER_LAYOUT.md"],
    "tier": "target-safety", "track": "High School Poster Expo",
    "deadline": "2026-08-18", "deadline_note": "Applicants notified on/before 2026-08-25; expo 2026-10-24 (meeting 2026-10-21..24).",
    "notification": "2026-08-25", "event_date": "2026-10-24",
    "eligibility_status": "ok", "eligibility_note": "HS juniors/seniors by Fall 2026 eligible; under-18 chaperone required.",
    "blockers": ["Portal fields must be copied manually when portal opens (monitor)"],
    "fit": 5, "college_value": 4, "feasibility": 5,
    "integrity_flags": [],
    "status_label": "strong-fit",
    "gates": gates(done=["G0","G1"], in_progress=["G2","G3"]),
    "notes": "Best high-school biomedical-engineering poster target. Template-structured abstract + poster layout drafted. Use the HS Poster Expo, NOT the general abstract track.",
  },
  {
    "id": "bmes_general_abstract", "venue_name": "BMES 2026 (general abstract)",
    "long_name": "BMES 2026 Annual Meeting - General Abstract track",
    "folder": f"{TSUB}/bmes_general_abstract_2026",
    "canonical_file": f"{TSUB}/bmes_general_abstract_2026/SUBMISSION_DRAFT.md",
    "extra_files": [],
    "tier": "skip-unless-confirmed", "track": "General abstract (grad/doctoral/professional)",
    "deadline": "2026-06-15", "deadline_note": "Extended deadline 2026-06-15 PASSED; presenter registration was due 2026-08-03.",
    "notification": None, "event_date": "2026-10-24",
    "eligibility_status": "blocked", "eligibility_note": "Official page: General Abstracts are for graduate, doctoral, and professional submissions only. Wrong presenter pool for a HS sole author.",
    "blockers": ["Eligibility: not for HS sole presenter", "Deadline passed"],
    "fit": 4, "college_value": 3, "feasibility": 1,
    "integrity_flags": [],
    "status_label": "skip",
    "gates": gates(done=["G0","G1"], blocked=["G5"]),
    "notes": "Default to the HS Poster Expo instead. Only pursue if BMES explicitly approves eligibility.",
  },
  {
    "id": "sccur_2026", "venue_name": "SCCUR 2026",
    "long_name": "Southern California Conferences for Undergraduate Research 2026 (at SDSU)",
    "folder": f"{TSUB}/sccur_2026",
    "canonical_file": f"{TSUB}/sccur_2026/SUBMISSION_DRAFT.md",
    "extra_files": [f"{TSUB}/sccur_2026/POSTER_LAYOUT.md"],
    "tier": "target-conditional", "track": "Poster or oral presentation",
    "deadline": "2026-10-09", "deadline_note": "Early window through 2026-07-31 for guaranteed decision before early registration; final abstract deadline 2026-10-09; conference 2026-11-21.",
    "notification": None, "event_date": "2026-11-21",
    "eligibility_status": "conditional", "eligibility_note": "Undergrad-focused. HS eligible ONLY with sustained college-level or equivalent faculty-guided research. Must verify real faculty-guided status; email directors first if fully independent.",
    "blockers": ["Faculty-guided eligibility must be honestly satisfied or cleared with directors"],
    "fit": 4, "college_value": 3, "feasibility": 3,
    "integrity_flags": ["no-fabricated-mentor"],
    "status_label": "conditional-eligibility",
    "gates": gates(done=["G0","G1"], in_progress=["G3"]),
    "notes": "1,480-char abstract (under 1,500) + poster layout drafted. Early-accept before Nov 1 is useful for college apps. Apply by 2026-07-31 only if faculty-guided condition is truthfully met.",
  },
  {
    "id": "regeneron_sts_2027", "venue_name": "Regeneron STS 2027",
    "long_name": "Regeneron Science Talent Search 2027",
    "folder": f"{TSUB}/regeneron_sts_2027",
    "canonical_file": f"{TSUB}/regeneron_sts_2027/SUBMISSION_DRAFT.md",
    "extra_files": [f"{TSUB}/regeneron_sts_2027/REPORT_BLUEPRINT.md"],
    "tier": "reach-flagship", "track": "Senior research competition (report + application)",
    "deadline": "2026-11-05", "deadline_note": "Application open 2026-06-01 to 2026-11-05 (8pm ET); Top 300 announced 2027-01-07.",
    "notification": "2027-01-07", "event_date": None,
    "eligibility_status": "ok", "eligibility_note": "HS seniors; major application, research report, recommendations, integrity rules.",
    "blockers": ["Generative-AI text is PROHIBITED in the report/application; scaffold only", "Needs real recommenders (educator, project, HS report)"],
    "fit": 5, "college_value": 5, "feasibility": 3,
    "integrity_flags": ["no-AI-text", "no-fabricated-mentor"],
    "status_label": "scaffold-only / student-must-write",
    "gates": gates(done=["G0"], blocked=["G1"]),
    "notes": "Highest college-application upside; not a conference. Files are PLANNING SCAFFOLDS ONLY - STS prohibits AI-drafted report/application text. Student writes the final report from scratch and discloses tool use. Build around the target-definition audit story (research maturity).",
  },
  {
    "id": "aan_neuroscience_prize", "venue_name": "AAN Neuroscience Prize",
    "long_name": "AAN Neuroscience Research Prize (high school)",
    "folder": f"{TSUB}/aan_neuroscience_prize",
    "canonical_file": f"{TSUB}/aan_neuroscience_prize/SUBMISSION_DRAFT.md",
    "extra_files": [f"{TSUB}/aan_neuroscience_prize/RESEARCH_REPORT_DRAFT.md"],
    "tier": "reach-target", "track": "High-school neuroscience prize (abstract + report)",
    "deadline": None, "deadline_note": "Official page currently closed; historically a fall deadline. Monitor weekly for the 2027 cycle.",
    "notification": None, "event_date": None,
    "eligibility_status": "monitor", "eligibility_note": "HS neuroscience research; requires application form + <=300-word abstract + report + bibliography + parent/guardian, teacher, and mentor e-signatures.",
    "blockers": ["Cycle not open (monitor)", "Requires real teacher + mentor + parent e-signatures"],
    "fit": 5, "college_value": 4, "feasibility": 3,
    "integrity_flags": ["no-fabricated-mentor"],
    "status_label": "monitor-cycle",
    "gates": gates(done=["G0","G1"], in_progress=["G3"], blocked=["G8"]),
    "notes": "271-word abstract (<300) + report with bibliography drafted. Strong neuroscience category fit. Prepare a neuroscience-first version that explains PAC caveats cleanly. Blocked at final-QA until real signers exist and the cycle opens.",
  },
  {
    "id": "jshs_norcal_2027", "venue_name": "JSHS NorCal 2027",
    "long_name": "Northern California Junior Science and Humanities Symposium 2027",
    "folder": f"{TSUB}/jshs_norcal_2027",
    "canonical_file": f"{TSUB}/jshs_norcal_2027/SUBMISSION_DRAFT.md",
    "extra_files": [f"{TSUB}/jshs_norcal_2027/RESEARCH_PAPER_BLUEPRINT.md"],
    "tier": "target-reach", "track": "Regional paper / poster / oral",
    "deadline": None, "deadline_note": "2027 dates not posted. 2025 region opened 2024-11-16, deadline 2025-01-16, regional 2025-02-28. Prepare during fall; apply when region opens.",
    "notification": None, "event_date": None,
    "eligibility_status": "ok", "eligibility_note": "Grades 9-12, Northern California region; original STEM research; written report + Statement of Outside Assistance.",
    "blockers": ["Generative-AI writing of abstract/paper PROHIBITED; scaffold only", "2027 NorCal packet not yet verified"],
    "fit": 5, "college_value": 4, "feasibility": 3,
    "integrity_flags": ["no-AI-text"],
    "status_label": "scaffold-only / student-must-write",
    "gates": gates(done=["G0"], blocked=["G1"]),
    "notes": "Strong high-school research competition. Files are PLANNING SCAFFOLDS ONLY - JSHS core rules prohibit ChatGPT/generative-AI writing the abstract or paper and require a Statement of Outside Assistance. Student writes the final text.",
  },
  {
    "id": "sfn_late_breaking_2026", "venue_name": "SfN 2026 (late-breaking)",
    "long_name": "Society for Neuroscience 2026 - Late-breaking abstract",
    "folder": f"{TSUB}/sfn_late_breaking_2026",
    "canonical_file": f"{TSUB}/sfn_late_breaking_2026/SUBMISSION_DRAFT.md",
    "extra_files": [],
    "tier": "reach", "track": "Late-breaking abstract",
    "deadline": "2026-09-15", "deadline_note": "Late-breaking window 2026-09-08..2026-09-15 (or until cap). Regular abstract deadline already closed.",
    "notification": None, "event_date": None,
    "eligibility_status": "conditional", "eligibility_note": "Abstract fee + SfN membership/account. Late-breaking should be genuinely new post-regular-deadline analysis.",
    "blockers": ["Needs genuinely NEW analysis completed after the regular deadline", "SfN membership/account + fee"],
    "fit": 3, "college_value": 4, "feasibility": 2,
    "integrity_flags": [],
    "status_label": "conditional-new-analysis",
    "gates": gates(done=["G0","G1"], blocked=["G4"]),
    "notes": "1,753 non-space chars (<2,300 limit). Biological validation weaker than engineering validation. Submit ONLY if new robustness experiments are completed after the regular deadline.",
  },
  {
    "id": "sigma_xi_showcase_2027", "venue_name": "Sigma Xi Showcase 2027",
    "long_name": "Sigma Xi Student Research Showcase 2027",
    "folder": f"{TSUB}/sigma_xi_showcase_2027",
    "canonical_file": f"{TSUB}/sigma_xi_showcase_2027/SUBMISSION_DRAFT.md",
    "extra_files": [f"{TSUB}/sigma_xi_showcase_2027/WEBSITE_AND_VIDEO_PLAN.md"],
    "tier": "safety-target", "track": "Online presentation competition",
    "deadline": None, "deadline_note": "2026 cycle deadline was 2026-03-13; 2027 expected winter/spring.",
    "notification": None, "event_date": None,
    "eligibility_status": "ok", "eligibility_note": "Open to high-school, undergraduate, and graduate students.",
    "blockers": ["Requires a real website + technical slideshow + video before it is ready"],
    "fit": 4, "college_value": 3, "feasibility": 3,
    "integrity_flags": [],
    "status_label": "backup-online",
    "gates": gates(done=["G0","G1"], blocked=["G7"]),
    "notes": "206-word abstract + website/video plan drafted. Lower-friction online backup. Not ready until the website, slideshow, and video are built. Apply in the 2027 cycle.",
  },
  {
    "id": "bci_award_2026", "venue_name": "BCI Award 2026",
    "long_name": "BCI Award 2026 (Annual BCI Research Award)",
    "folder": f"{TSUB}/bci_award_2026",
    "canonical_file": f"{TSUB}/bci_award_2026/TWO_PAGE_PROJECT_DESCRIPTION.md",
    "extra_files": [f"{TSUB}/bci_award_2026/SUBMISSION_DRAFT.md", f"{TSUB}/bci_award_2026/VIDEO_SCRIPT.md"],
    "tier": "reach-stretch", "track": "Project award / nomination (2-page PDF + ~2min film)",
    "deadline": "2026-09-01", "deadline_note": "Submission deadline 2026-09-01; nominees announced 2026-09-15.",
    "notification": "2026-09-15", "event_date": None,
    "eligibility_status": "ok", "eligibility_note": "BCI/neurotechnology award; nominees present and may publish a chapter. Scoring rewards online/real-time BCI function + user benefit.",
    "blockers": ["Fit is a stretch: project is offline/retrospective, not a finished real-time BCI", "Needs final 2-page PDF + actual ~2-min film"],
    "fit": 2, "college_value": 4, "feasibility": 2,
    "integrity_flags": [],
    "status_label": "optional-stretch",
    "gates": gates(done=["G0","G1"], blocked=["G7"]),
    "notes": "2-page description (324 words) + video script drafted. Low probability because scoring rewards real-time BCI function. Submit only if narrative is rewritten around adaptive neurotechnology + information-boundary auditing.",
  },
  {
    "id": "aises_2026", "venue_name": "AISES 2026",
    "long_name": "AISES National Conference 2026 - Student research",
    "folder": f"{TSUB}/aises_2026",
    "canonical_file": f"{TSUB}/aises_2026/SUBMISSION_DRAFT.md",
    "extra_files": [],
    "tier": "conditional-mission-fit", "track": "Student research oral/poster (Indigenous Abstract Framework)",
    "deadline": "2026-09-04", "deadline_note": "Priority deadlines 2026-07-24 and 2026-08-14; final 2026-09-04; presentations 2026-10-15..16.",
    "notification": None, "event_date": "2026-10-15",
    "eligibility_status": "conditional", "eligibility_note": "Middle-school through doctoral; Indigenous-centered framework and community-impact framing. Only apply if the identity/mission fit is genuine.",
    "blockers": ["Apply ONLY if Indigenous-centered/community-impact framing is honest and not forced"],
    "fit": 3, "college_value": 3, "feasibility": 2,
    "integrity_flags": ["honest-identity-only"],
    "status_label": "conditional-mission-fit",
    "gates": gates(done=["G0","G1"], blocked=["G5"]),
    "notes": "Indigenous Abstract Framework draft (WHAT/SO WHAT/NOW WHAT) exists. Do NOT force an identity or community narrative. Apply only if the framework fits honestly.",
  },
  {
    "id": "sacnas_ndistem_2026", "venue_name": "SACNAS NDiSTEM 2026",
    "long_name": "SACNAS NDiSTEM 2026 - Student research presentation",
    "folder": f"{TSUB}/sacnas_ndistem_2026",
    "canonical_file": f"{TSUB}/sacnas_ndistem_2026/SUBMISSION_DRAFT.md",
    "extra_files": [],
    "tier": "likely-ineligible", "track": "Student research presentation",
    "deadline": "2026-07-10", "deadline_note": "Summer applications close 2026-07-10; conference 2026-10-29..31.",
    "notification": None, "event_date": "2026-10-29",
    "eligibility_status": "blocked", "eligibility_note": "Official page points to community-college, undergrad, post-bacc, grad, postdoc presenters; prior audit found an age-18-at-conference requirement + PI approval for abstract publication.",
    "blockers": ["Eligibility appears blocked: age-18-at-conference + student/postdoc-level status", "Requires PI approval for abstract publication"],
    "fit": 3, "college_value": 3, "feasibility": 1,
    "integrity_flags": [],
    "status_label": "skip-unless-confirmed",
    "gates": gates(done=["G0","G1"], blocked=["G5"]),
    "notes": "Contingency abstract (196 words) only. Skip unless SACNAS explicitly confirms a 17-year-old HS student can present.",
  },
  {
    "id": "synopsys_championship_2027", "venue_name": "Synopsys Championship 2027",
    "long_name": "Synopsys Championship 2027 (SCVSEFA) / ISEF pathway",
    "folder": f"{TSUB}/synopsys_championship_2027",
    "canonical_file": f"{TSUB}/synopsys_championship_2027/SUBMISSION_DRAFT.md",
    "extra_files": [f"{TSUB}/synopsys_championship_2027/PROJECT_BOARD_PLAN.md", f"{TSUB}/synopsys_championship_2027/RESEARCH_PLAN_AND_FORMS_CHECKLIST.md"],
    "tier": "target-local / isef-reach", "track": "Local fair -> CSEF/ISEF pathway",
    "deadline": None, "deadline_note": "2027 dates not fully posted. 2026 abstracts were due 2026-02-27, judging 2026-03-10. Work window Jan 2026 - Mar 2027.",
    "notification": None, "event_date": None,
    "eligibility_status": "ok", "eligibility_note": "Santa Clara Valley fair; ISEF rules. Requires Adult Sponsor + ISEF/SCVSEFA forms + research plan + signatures; continuation/RRI/SRC rules matter.",
    "blockers": ["Requires Adult Sponsor + ISEF/SCVSEFA forms + research plan + signatures (start early)", "Continuation vs new-work question for ISEF"],
    "fit": 4, "college_value": 4, "feasibility": 3,
    "integrity_flags": [],
    "status_label": "senior-year-fair",
    "gates": gates(done=["G0","G1"], in_progress=["G3"], blocked=["G8"]),
    "notes": "Abstract (234 words) + board plan + forms checklist drafted. Frame as computational research using public deidentified data; avoid diagnosis/treatment claims. Lock ISEF paperwork early.",
  },
  {
    "id": "bci_meeting_2027", "venue_name": "BCI Meeting 2027",
    "long_name": "8th International BCI Meeting 2027",
    "folder": f"{TSUB}/bci_meeting_2027",
    "canonical_file": f"{TSUB}/bci_meeting_2027/SUBMISSION_DRAFT.md",
    "extra_files": [],
    "tier": "reach-later", "track": "Poster / oral abstract",
    "deadline": "2027-01-15", "deadline_note": "Abstracts open 2026-11-09; deadline 2027-01-15; notification 2027-03-03; meeting 2027-06-07 onward.",
    "notification": "2027-03-03", "event_date": "2027-06-07",
    "eligibility_status": "ok", "eligibility_note": "BCI Society venue; abstract/poster. Travel timeline is after college applications.",
    "blockers": ["Improve with repeated splits + stronger adaptive-neurotechnology framing", "Later deadline - do not let it distract from fall deadlines"],
    "fit": 3, "college_value": 3, "feasibility": 3,
    "integrity_flags": [],
    "status_label": "prepare-later",
    "gates": gates(done=["G0","G1"], in_progress=[]),
    "notes": "Abstract with a fit caveat drafted. Good for update letters, not early apps. Prepare after URTC/STS.",
  },
  {
    "id": "icassp_2027", "venue_name": "ICASSP 2027",
    "long_name": "IEEE ICASSP 2027",
    "folder": f"{TSUB}/icassp_2027",
    "canonical_file": f"{TSUB}/icassp_2027/SUBMISSION_DRAFT.md",
    "extra_files": [],
    "tier": "high-reach", "track": "Full paper (flagship signal processing)",
    "deadline": "2026-09-16", "deadline_note": "Submission deadline 2026-09-16; conference 2027-05-16..21.",
    "notification": None, "event_date": "2027-05-16",
    "eligibility_status": "ok", "eligibility_note": "Top signal-processing venue; full-paper rigor expected. No HS exclusion, but bar is high.",
    "blockers": ["Current novelty/validation below bar", "Needs grouped CV + streaming PAC + signal-processing novelty before submitting"],
    "fit": 3, "college_value": 5, "feasibility": 1,
    "integrity_flags": [],
    "status_label": "do-not-submit-as-is",
    "gates": gates(done=["G0","G1"], blocked=["G4"]),
    "notes": "156-word abstract + upgrade list only. Do NOT submit as-is. Consider only after grouped CV, streaming PAC, and a stronger signal-processing contribution.",
  },
]

print("venues defined:", len(VENUES))
assert len({v["id"] for v in VENUES}) == len(VENUES), "duplicate venue id"

# ---------------------------------------------------------------------------
# Transparent priority score: composite of four 0-100 sub-scores.
# ---------------------------------------------------------------------------
WEIGHTS = {"urgency": 0.35, "fit": 0.25, "college_value": 0.25, "feasibility": 0.15}

def days_until(deadline, today=TODAY):
    if not deadline:
        return None
    return (dt.date.fromisoformat(deadline) - dt.date.fromisoformat(today)).days

def urgency_score(deadline, today=TODAY):
    d = days_until(deadline, today)
    if d is None: return 40
    if d < 0:  return 8
    if d <= 14: return 100
    if d <= 30: return 88
    if d <= 60: return 72
    if d <= 120: return 52
    return 36

# Actionability multiplier: can the applicant actually act on this now? A blocked
# or likely-ineligible venue should not outrank real targets just because its
# deadline is near. We keep the raw desirability ("composite") visible for
# transparency and rank by the adjusted "effective" score.
ACTIONABILITY = {"ok": 1.0, "conditional": 0.8, "monitor": 0.8, "blocked": 0.45}

def composite_score(v, today=TODAY):
    urg = urgency_score(v["deadline"], today)
    fit, col, fea = v["fit"]*20, v["college_value"]*20, v["feasibility"]*20
    comp = (WEIGHTS["urgency"]*urg + WEIGHTS["fit"]*fit +
            WEIGHTS["college_value"]*col + WEIGHTS["feasibility"]*fea)
    act = ACTIONABILITY.get(v["eligibility_status"], 1.0)
    eff = comp * act
    return {"urgency": urg, "fit": fit, "college_value": col, "feasibility": fea,
            "composite": round(comp,1), "actionability": act, "effective": round(eff,1)}

def gate_progress(gs):
    considered = [g for g in WORK_GATES if gs.get(g) != "na"]
    done = sum(1 for g in considered if gs.get(g)=="done")
    inprog = sum(1 for g in considered if gs.get(g)=="in_progress")
    blocked = [g for g in WORK_GATES if gs.get(g)=="blocked"]
    total = len(considered) if considered else 1
    pct = round(100*(done + 0.5*inprog)/total)
    current = None
    for g in WORK_GATES:
        if gs.get(g) in ("na","done"): continue
        current = g; break
    if gs.get("G9")=="done":
        current = "G10" if gs.get("G10")!="done" else "done"
    return {"pct": pct, "done": done, "in_progress": inprog, "blocked_gates": blocked,
            "current_gate": current, "total_considered": total}

for v in VENUES:
    v["scores"] = composite_score(v)
    v["progress"] = gate_progress(v["gates"])
    v["days_until_deadline"] = days_until(v["deadline"])

ranked = sorted(VENUES, key=lambda x: (x["scores"]["effective"], x["scores"]["composite"]), reverse=True)
for i, v in enumerate(ranked, 1):
    v["priority_rank"] = i

tracker = {
    "schema_version": "1.0",
    "generated": TODAY,
    "project": {
        "name": "Retrospective EEG/PAC forecasting for adaptive 40 Hz auditory entrainment",
        "repo_subpath": "paper/conferences",
        "source_of_truth_claims": "paper/data/key_results.md",
        "claim_boundaries": [
            "Use 'retrospective', 'offline replay', 'target-definition audit', 'scalar frontal EEG timing target'.",
            "Do NOT claim therapy, clinical validation, patient benefit, prospective deployment, or disease slowing.",
            "Do NOT claim the TCN beats Ridge under the backward-looking PAC target.",
            "Keep event-summary and backward-looking PAC results separate; do not mix controller generations.",
            "Do NOT list a mentor, university, lab, or affiliation unless real and specific to this work.",
            "For STS and JSHS, drafts are planning scaffolds only; final text must be human-authored per venue rules.",
        ],
    },
    "workflow": {
        "model_name": "Stage-gate submission pipeline (G0 -> G10)",
        "gates": GATES, "work_gates": WORK_GATES, "status_values": STATUS_VALUES,
        "priority_formula": {
            "description": "composite 0-100 = weighted sum of four 0-100 sub-scores (raw desirability). effective = composite x actionability; venues are RANKED by effective so a blocked/ineligible venue does not outrank real targets on deadline urgency alone.",
            "weights": WEIGHTS,
            "actionability_multiplier": ACTIONABILITY,
            "subscore_defs": {
                "urgency": "days-to-deadline: <=14d=100,<=30d=88,<=60d=72,<=120d=52,>120d=36,unposted=40,passed=8.",
                "fit": "Editorial 1-5 topic/venue fit x20.",
                "college_value": "Editorial 1-5 college-application value x20.",
                "feasibility": "Editorial 1-5 readiness/few-blockers x20.",
                "actionability": "ok=1.0, conditional/monitor=0.8, blocked=0.45.",
            },
        },
    },
    "venues": ranked,
}

out = Path("conf_tracker/submission_tracker.json")
out.write_text(json.dumps(tracker, indent=2))
print("WROTE", out, out.stat().st_size, "bytes")
print("\nRanked priority (effective | composite | rank | venue | deadline | elig | prog):")
for v in ranked:
    print(f"  eff={v['scores']['effective']:5.1f} raw={v['scores']['composite']:5.1f}  #{v['priority_rank']:>2}  {v['venue_name']:<32} {str(v['deadline']):<12} {v['eligibility_status']:<11} {v['progress']['pct']}%")
