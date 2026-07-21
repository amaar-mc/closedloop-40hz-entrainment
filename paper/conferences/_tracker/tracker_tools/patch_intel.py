#!/usr/bin/env python3
"""Fold venue-intelligence findings into submission_tracker.json (idempotent).

Adds per-venue: confidence, acceptance_signals[], tailoring[] (top levers), and a
venue_intelligence pointer. Corrects a few facts discovered during research. Safe to
re-run: it overwrites only these managed keys.
"""
import json, sys
from pathlib import Path

p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("conf_tracker/submission_tracker.json")
t = json.loads(p.read_text())

# venue_id -> intelligence payload
INTEL = {
  "bmes_hs_poster_expo": {
    "confidence": "high",
    "acceptance_signals": [
      "SCORED competition: historically top-10 posters get free registration + $250 travel stipend; top-3 get cash prizes.",
      "2026 Annual Meeting in Orlando; HS Poster Expo Saturday 2026-10-24; abstract deadline ~2026-08-18.",
      "'No lab experience required - just curiosity and creativity'; posters must be specifically biomedical-engineering focused.",
      "Under-18 chaperone required; student + chaperone each register separately ($100 each).",
    ],
    "tailoring": [
      "Frame explicitly as biomedical engineering: EEG signal processing for adaptive neuromodulation; audit = engineering rigor.",
      "Use the official HS poster abstract template sections exactly (Intro/Methods/Results/Conclusions) with one clean labeled figure referenced in text.",
      "Keep retrospective framing; arrange chaperone + registrations early.",
    ],
  },
  "regeneron_sts_2027": {
    "confidence": "high",
    "acceptance_signals": [
      "Holistic review by 3+ PhD scientists; GREATEST WEIGHT on the Research Report; STS does NOT share its rubric.",
      "Judges seek exceptional research skills, innovative thinking, promise as a scientist, leadership; ~15% Scholar, ~2% Finalist.",
      "Many Scholars/Finalists had no prior major awards/publications - depth + maturity beat prizes.",
      "Free to enter; sole-entrant only (no team projects); AI-drafted report/application text prohibited.",
    ],
    "tailoring": [
      "Build the entire application around the target-definition AUDIT as a maturity story (looked strong -> found the flaw -> stricter test -> narrowed claim).",
      "Write for PhD judges outside EEG: define PAC as an engineering feature; explain participant-disjoint splits + train-only normalization plainly.",
      "Student authors the report from scratch; disclose all tool/mentor assistance; line up educator + project + counselor recommenders now.",
    ],
  },
  "mit_urtc_poster_lightning": {
    "confidence": "high",
    "acceptance_signals": [
      "Peer-reviewed by faculty/grad/industry on originality, quality of content, adherence to conference themes; must be 'full and sole work'.",
      "Unaffiliated HS students ARE eligible for poster/lightning (poster ~2x3 ft; lightning <=5 min; abstract <=1000 words).",
      "Poster/lightning does NOT publish to IEEE Xplore (only the paper track does).",
    ],
    "tailoring": [
      "Submit poster or lightning (the eligible MIT-branded route); align abstract to a URTC track; <=1000 words.",
      "Compress the polished manuscript into a poster narrative built around the audit story with professional graphics.",
    ],
  },
  "mit_urtc_paper": {
    "confidence": "high",
    "acceptance_signals": [
      "Paper track requires ASSIP/RISE/RSI/SSP-type faculty-mentored affiliation OR substantial work with university students.",
      "AP/IB or other 'college-level' HS programs do NOT count as undergraduate affiliation (confirmed on URTC FAQ).",
      "5-page max manuscript; peer-reviewed + plagiarism-checked; publishes to IEEE Xplore.",
    ],
    "tailoring": [
      "Do NOT submit the paper track unless a genuine qualifying university relationship truthfully exists; otherwise route via poster/lightning.",
    ],
  },
  "jshs_norcal_2027": {
    "confidence": "high",
    "acceptance_signals": [
      "SFSU faculty + expert reviewers use published poster/oral rubrics; rewards original lab/field/applied research, NOT library/demo/informational.",
      "NorCal advances ~10 poster presenters -> oral finalists -> top 2 to National JSHS.",
      "Statement of Outside Assistance required; generative-AI writing of abstract/paper prohibited; plagiarism = disqualification.",
    ],
    "tailoring": [
      "Frame as applied computational research with a concrete research question; prepare a live Q&A defense of the leakage audit.",
      "Student writes abstract + paper; complete the Statement of Outside Assistance honestly.",
    ],
  },
  "synopsys_championship_2027": {
    "confidence": "high",
    "acceptance_signals": [
      "ISEF 100-pt rubric (Science): Research Question 10 / Design+Methodology 15 / Execution 20 / Creativity 20 / Presentation-Interview 35.",
      "Physical display is SECONDARY to student's understanding; judges want real lab/field/theoretical work, not gadgeteering/library research.",
      "Only the CURRENT year's work is judged for continuation projects (Form 7); Adult Sponsor + ISEF forms + research plan required, often before experimentation.",
    ],
    "tailoring": [
      "Map project onto the rubric: RQ = EEG target-availability for closed-loop control; Creativity = leakage-audit reframing; Execution = disjoint benchmark + Ridge/persistence baselines.",
      "Choose a computational/systems category; frame ds005048 as public de-identified data; avoid diagnosis/treatment claims; lock forms + sponsor early; clarify continuation vs CSEF 2026 work.",
    ],
  },
  "aan_neuroscience_prize": {
    "confidence": "medium",
    "acceptance_signals": [
      "Neuroscience-specific; app form + <=300-word abstract + report + bibliography + parent/teacher/mentor e-signatures.",
      "AAN = American Academy of Neurology audience: they will notice overclaimed physiological/clinical meaning of PAC.",
      "Historically a fall deadline; 2027 cycle not yet open (monitor).",
    ],
    "tailoring": [
      "Lead with careful neuroscience-first framing: PAC as a scalar frontal-EEG timing feature; explicit caveats (not proof of theta-gamma coupling or clinical benefit).",
      "Identify a real teacher + mentor willing to e-sign; do not fabricate supervision.",
    ],
  },
  "ieee_spmb_2026": {
    "confidence": "high",
    "acceptance_signals": [
      "Small single-day regional symposium (~100 attendees); ~50% acceptance; ~12 oral + 12-15 posters; explicitly welcomes 'research in progress'.",
      "Professional audience WILL notice single fixed split, single-seed benchmark, and Ridge tie.",
      "Full paper/abstract emailed as IEEE 2-column PDF to submit@ieeespmb.org; accepted authors must attend/present; indexed in IEEE Xplore since 2014.",
    ],
    "tailoring": [
      "Reframe as a signal-processing target-definition audit: target availability + baseline comparison change the conclusion (a methods contribution SPMB values).",
      "Report robustness honestly (multi-seed, persistence + Ridge) and state the single-split limitation up front; convert to the official IEEE 2-column PDF well before the SPMB 2027 deadline.",
    ],
  },
  "icassp_2027": {
    "confidence": "medium",
    "acceptance_signals": [
      "Flagship SP conference with full-paper rigor; strong novelty + validation expected; single-split/single-seed study is below bar as-is.",
    ],
    "tailoring": [
      "Do NOT submit as-is: first add grouped/repeated CV, streaming-compatible PAC estimator, uncertainty, and a sharper SP contribution.",
      "Position target-availability audit as a general lesson for closed-loop neural signal processing.",
    ],
  },
  "sfn_late_breaking_2026": {
    "confidence": "medium",
    "acceptance_signals": [
      "Late-breaking must be genuinely NEW post-regular-deadline analysis; biology-dominated audience; abstract body <=2,300 chars excl. spaces; membership + fee.",
    ],
    "tailoring": [
      "Only submit if new analysis is completed after the regular deadline (e.g., transition-specific eval, grouped CV).",
      "Frame PAC honestly as an EEG timing feature; avoid implying demonstrated physiological coupling.",
    ],
  },
  "bci_award_2026": {
    "confidence": "medium",
    "acceptance_signals": [
      "Jury scores explicit questions: novel BCI application? new methodology? new USER benefit? speed (bit/min)? accuracy? results from real patients/users?",
      "Criteria reward real-time/online BCI function + user benefit -> an offline retrospective project is a genuine stretch.",
      "<=2-page PDF opening with a 3-5 sentence summary + ~2-min film; deadline ~2026-09-01; 12 nominees invited to a Springer chapter.",
    ],
    "tailoring": [
      "Be honest it is offline/retrospective; compete on methodological-novelty + information-boundary auditing, NOT real-time user benefit.",
      "Frame as adaptive-neurotechnology methodology, not a finished BCI; treat as an optional stretch.",
    ],
  },
  "bci_meeting_2027": {
    "confidence": "low",
    "acceptance_signals": [
      "BCI Society meeting poster/oral; abstracts ~2026-11-09 open, ~2027-01-15 deadline; travel timeline after college apps.",
    ],
    "tailoring": [
      "Prepare after URTC/STS; strengthen with repeated splits + adaptive-neurotechnology framing; good for update letters, not early apps.",
    ],
  },
  "sccur_2026": {
    "confidence": "medium",
    "acceptance_signals": [
      "Undergrad-research abstracts (<=1,500 chars) for poster/oral; HS eligible ONLY with sustained college-level/faculty-guided research.",
      "Early window through ~2026-07-31 (guaranteed decision before early registration); final ~2026-10-09; conference ~2026-11-21 at SDSU.",
    ],
    "tailoring": [
      "Only submit if faculty-guided condition is honestly met, or after directors confirm an independent HS student may present.",
      "Keep abstract <=1,500 chars; frame as computational research.",
    ],
  },
  "aises_2026": {
    "confidence": "medium",
    "acceptance_signals": [
      "Indigenous Abstract Framework (WHAT / SO WHAT / NOW WHAT) + community-impact fields; identity/mission framing must be authentic.",
    ],
    "tailoring": [
      "Apply ONLY if the framework fits honestly; if so, structure as WHAT (audit) / SO WHAT (target-availability matters) / NOW WHAT (validation before deployment) with authentic community framing.",
    ],
  },
  "sacnas_ndistem_2026": {
    "confidence": "medium",
    "acceptance_signals": [
      "Community-college through postdoc presenters; prior audit found age-18-at-conference + student/postdoc-level status + PI approval for abstract publication.",
      "A 17-year-old independent HS student is likely ineligible.",
    ],
    "tailoring": [
      "Skip unless SACNAS confirms eligibility in writing; contingency abstract only.",
    ],
  },
  "sigma_xi_showcase_2027": {
    "confidence": "medium",
    "acceptance_signals": [
      "Online presentation competition: requires a web page + technical slideshow + video, judged on presentation quality + scientific communication; HS/undergrad/grad eligible.",
      "2026 deadline was ~March; 2027 expected winter/spring; lower prestige than STS/URTC but a good communication credit.",
    ],
    "tailoring": [
      "Reuse manuscript figures (pipeline diagram, horizon sweep, controller comparison) in the slideshow; script the video around the audit narrative.",
      "Not ready until website + slides + video are built; keep claims retrospective.",
    ],
  },
  "bmes_general_abstract": {
    "confidence": "high",
    "acceptance_signals": [
      "General abstracts route to 19 technical tracks but are for GRADUATE/DOCTORAL/PROFESSIONAL submissions; $65 fee + BMES account + attendance.",
      "Wrong presenter pool for a HS sole author.",
    ],
    "tailoring": [
      "SKIP - use the HS Poster Expo instead unless BMES explicitly approves eligibility.",
    ],
  },
}

n = 0
for v in t["venues"]:
    intel = INTEL.get(v["id"])
    if not intel:
        continue
    v["confidence"] = intel["confidence"]
    v["acceptance_signals"] = intel["acceptance_signals"]
    v["tailoring"] = intel["tailoring"]
    v["venue_intelligence_ref"] = "_tracker/research/VENUE_INTELLIGENCE.md"
    n += 1

t["project"]["research_docs"] = {
    "ai_writing_tells": "_tracker/research/AI_WRITING_TELLS_AND_AVOIDANCE.md",
    "venue_intelligence": "_tracker/research/VENUE_INTELLIGENCE.md",
}
p.write_text(json.dumps(t, indent=2))
print(f"patched {n}/{len(t['venues'])} venues with confidence + acceptance_signals + tailoring")
print("venues missing intel:", [v["id"] for v in t["venues"] if "confidence" not in v])
