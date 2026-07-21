# Venue Intelligence & Per-Venue Tailoring

**What each venue actually rewards, and how to tailor this project to fit.** Grounded in official
pages and, where public info is thin, flagged as lower-confidence. Every tailoring lever stays inside
the project's claim boundaries: retrospective / offline-replay framing, no clinical/therapeutic/
deployment claims, no fabricated affiliation, and human-authored final text where venue rules require.

> **Confidence key:** **HIGH** = grounded in the venue's official rubric/criteria pages. **MEDIUM** =
> official process described but no numeric rubric, or inferred from official "what makes a strong
> submission" guidance. **LOW** = little public detail; treat as best-estimate and re-verify at submission.

> **The project in one line (for reviewers):** _An honest target-definition audit — a causal TCN
> forecasts frontal-EEG PAC for adaptive 40 Hz stimulation, looks strong (five-seed mean R² = 0.606),
> then a leakage-free backward-looking target drops it to ~0.212 (Ridge-level), and offline controller
> replay reveals a targeting-specificity tradeoff._ The maturity story (finding and correcting a
> misleading result) is the asset — lead with it at research-competition venues; lead with the
> signal-processing/target-availability angle at engineering venues.

---

## Cross-venue patterns (what shows up everywhere)

1. **Judges reward the student's understanding over the result.** ISEF explicitly makes the physical
   display _secondary_ to how well the student understands the work; STS weights the Research Report
   heaviest and probes scientific potential; URTC scores originality + quality + fit. For this project
   that means the _audit narrative_ (why the first result was misleading, how it was tested) is worth
   more than any single R².
2. **Honesty about limitations is a strength, not a weakness.** ISEF's interview explicitly evaluates
   "interpretation and limitations of the results." This project's real limitations (event-summary PAC
   labels, single fixed split, offline replay ≠ physiology) are exactly what a mature entry states plainly.
3. **Independence and authorship are scrutinized.** ISEF Form 1C / Form 7, STS mentor-disclosure, JSHS
   Statement of Outside Assistance, URTC "full and sole work" — every serious venue wants a clear line
   between the student's work and any help. Never fabricate a mentor; disclose tool use where required.
4. **Eligibility is the most common hard blocker for an independent high-school author** — not merit.
   MIT URTC paper track, BMES general abstract, SACNAS, and (conditionally) SCCUR gate on affiliation/
   age/level. Route to the track the applicant is actually eligible for.
5. **Format compliance is a silent filter.** Character/word/page limits, required sections, and file
   format (IEEE 2-column PDF for SPMB; 5-page for URTC paper; 2-page for BCI Award) are checked before
   merit. Missing the format can mean no review at all.
6. **Generative-AI-written text is prohibited at the flagship competitions** (STS, JSHS). Those drafts
   are planning scaffolds only; the student authors the final text and discloses assistance.

---

# CLUSTER A — High-school research competitions

## Regeneron STS 2027 — HIGH confidence

**What they look for.** Holistic review by 3+ PhD scientists; **greatest weight on the Research Report**,
plus the online application essays and the student's overall scientific potential. Judges seek
"exceptional research skills, … innovative thinking, promise as a scientist, and evidence of leadership."
STS explicitly **does not share its rubric** and is a holistic fellowship-style review, not a science-fair
score sheet.
**Traits of selected work.** Original, independent, rigorous research with excellent documentation;
strong mentor letters that _confirm the student's role_; clear communication to PhD judges outside the
subfield. Many Scholars/Finalists had no prior major awards or publications — depth and maturity matter
more than prizes. ~1,900–2,600 apply; 300 Scholars (~12–15%), 40 Finalists (~2%).
**Format & logistics.** Free. Application window ~June 1 → early November (8pm ET); Scholars ~January,
Finalist Week in DC in March. Components: research report, application questions/essays, recommendations,
transcript, optional scores.
**Eligibility reality.** US high-school seniors (citizens, permanent residents, or students at US high
schools). Independent work is fine — no university affiliation required.
**Pitfalls.** AI-drafted report/application text (prohibited); team projects (not allowed — must be a
sole entrant); shallow "science-fair" depth; missing recommendation/transcript components; late tech issues.
**Tailoring levers for this project.**

- Build the whole application around the **target-definition audit** as a maturity story: "I built a
  model, it looked strong, I found why that was misleading, I ran a stricter test, and I narrowed the claim."
- In the essays, foreground **independent intellectual ownership** — the leakage audit, the decision to
  re-define the PAC target, the honest baseline comparison to Ridge. This is what "promise as a scientist" looks like.
- Write for PhD judges _outside_ EEG: define PAC as an engineering feature, explain participant-disjoint
  splitting and train-only normalization in plain terms.
- **Do not submit the scaffold text.** Student writes the report; disclose all tool/mentor assistance accurately.
- Line up three recommenders now (educator + project observer + counselor); the project recommendation
  must describe what was actually observed, without inventing supervision.

## Northern California JSHS 2027 — HIGH confidence

**What they look for.** Regional review by SFSU faculty + expert reviewers using published poster/oral
rubrics; rewards original laboratory/field/applied research with a logical conclusion tied to the research
problem ("what was learned?"). Explicitly **not** library/demonstration/informational projects.
**Traits of selected work.** NorCal advances ~10 poster presenters → oral finalists; **top 2 go to National
JSHS**. Clear research question, sound method, honest interpretation, strong Q&A. Continuation projects
must show genuine expansion (new methods/variables), not just more data.
**Format & logistics.** Written report + abstract + **Statement of Outside Assistance** via Ideal-Logic;
region opens ~November, deadline ~mid-January, regional symposium ~late February. Grades 9–12, NorCal region.
**Eligibility reality.** Independent HS research is fully eligible. **Generative-AI writing of the abstract/
paper is prohibited; plagiarism = disqualification.**
**Pitfalls.** AI-written text; "library research" framing; weak Statement of Outside Assistance; unverified
current-cycle packet.
**Tailoring levers.**

- Frame as **applied computational research** with a concrete research question ("are PAC forecasts still
  useful after the target is stress-tested?"), not a literature survey.
- Prepare a crisp oral/Q&A story on the leakage audit — judges reward students who can defend method choices live.
- Student writes the abstract + paper; complete the Statement of Outside Assistance honestly.

## Synopsys Championship 2027 / ISEF pathway — HIGH confidence (ISEF rubric)

**What they look for.** ISEF's 100-point Grand Award rubric (Science): **Research Question 10 · Design &
Methodology 15 · Execution/Data Analysis & Interpretation 20 · Creativity 20 · Presentation/Interview 35.**
The physical display is _secondary_ to the student's understanding; judges look for real
laboratory/field/theoretical work, not "gadgeteering" or library research.
**Traits of selected work.** Clear, focused, testable question that identifies a contribution; well-designed
methods with defined variables/controls; sound data analysis with honest interpretation of limitations;
demonstrated creativity in approach; a confident, well-understood interview. **Only the current year's work
is judged** for continuation projects (Form 7).
**Format & logistics.** Local SCVSEFA fair → CSEF → ISEF. Requires Adult Sponsor, ISEF forms (1, 1A, 1B,
research plan; 1C if at an institution), possible SRC/IRB pre-approval, signatures with correct dates.
2026 abstracts were due late February; 2027 dates TBA.
**Eligibility reality.** Eligible, but the **forms/approvals must be completed before experimentation** in
many cases — start early. Public-data secondary analysis has specific rules; frame as computational research
on public de-identified data.
**Pitfalls.** Late/incomplete forms; diagnosis/treatment claims (avoid — frame as computational method);
treating a continuation as new work without a Form 7.
**Tailoring levers.**

- Map the project onto the rubric explicitly: **Research Question** = target-availability of EEG features
  for closed-loop control; **Creativity** = the leakage audit reframing; **Execution** = participant-disjoint
  benchmark + Ridge/persistence baselines; **Interview** = be ready to explain PAC, leakage, and limitations.
- Choose a computational/systems category; frame ds005048 as public de-identified data; avoid clinical claims.
- Lock the Adult Sponsor + forms + research plan early; clarify continuation status vs the CSEF 2026 work.

## AAN Neuroscience Research Prize — MEDIUM confidence

**What they look for.** Neuroscience-specific merit; application form + ≤300-word abstract + research report

- bibliography; requires parent/guardian, teacher, and mentor e-signatures. (Historically a fall deadline;
  2027 cycle not yet open — monitor.)
  **Traits of selected work.** Clean neuroscience framing with correct interpretation of neural measures;
  strong, honest write-up appropriate for a clinical-neuroscience audience (AAN = American Academy of Neurology).
  **Format & logistics.** Abstract (≤300 words), report + bibliography, signatures. Portal opens in the fall cycle.
  **Eligibility reality.** HS neuroscience research; the **e-signature requirement means a real teacher and
  mentor must sign** — line these up before finalizing.
  **Pitfalls.** Overclaiming physiological/clinical meaning of PAC (AAN is a neurology audience — they will
  notice); missing signatures; submitting before the cycle opens.
  **Tailoring levers.**

* Lead with a careful, **neuroscience-first** framing: PAC as a scalar frontal-EEG timing feature, with
  explicit caveats that this is not proof of physiological theta–gamma coupling or clinical benefit.
* Emphasize the dementia-cohort context (ds005048) honestly and the _retrospective_ nature; no therapy claims.
* Identify a real teacher + mentor willing to sign; do not fabricate supervision.

## Sigma Xi Student Research Showcase 2027 — MEDIUM confidence

**What they look for.** An online presentation competition: a **web page + technical slideshow + video**,
judged on presentation quality and scientific communication; open to HS/undergrad/grad.
**Traits of selected work.** Clear visual storytelling, a well-structured slideshow, and a confident video
walkthrough; strong asynchronous Q&A with judges/visitors.
**Format & logistics.** 2026 deadline was ~March; 2027 expected winter/spring. Requires the built website,
slideshow, and video — not just an abstract.
**Eligibility reality.** Fully eligible (HS allowed). Lower prestige than STS/URTC but a good communication credit.
**Pitfalls.** Treating it as "abstract-only" — it is not ready until the website + slides + video exist.
**Tailoring levers.**

- Reuse the manuscript figures (pipeline diagram, horizon sweep, controller comparison) in the slideshow;
  script the video around the audit narrative.
- Keep claims retrospective; the video is a chance to explain the leakage audit visually.

---

# CLUSTER B — IEEE / professional technical venues

## IEEE SPMB (Signal Processing in Medicine and Biology) — HIGH confidence

**What they look for.** A small, single-day regional symposium (~100 attendees) on biomedical signal
processing; peer-reviewed papers and posters, **explicitly encouraging students to present research in
progress.** ~50% acceptance; typically ~12 oral papers + 12–15 posters; papers not accepted for oral are
offered a poster slot. Indexed in IEEE Xplore since 2014.
**Traits of accepted work.** Solid biomedical signal-processing method with honest evaluation; a
professional audience that _will_ notice single fixed splits, single-seed benchmarks, and a Ridge tie —
but the "research in progress" ethos means a well-scoped, honestly-bounded study is welcome.
**Format & logistics.** **Full paper or abstract emailed as a PDF to submit@ieeespmb.org**; IEEE 2-column
template (10pt Times body, 9pt captions); Acknowledgement section before References; 1-page min / 4-page max
for posters (1 page preferred). **Accepted authors must attend and present** or the work is removed from the
record. Virtual (Zoom) in recent years; no fee noted. **2026 paper deadline (2026-07-01) has passed — re-target 2027.**
**Eligibility reality.** No high-school exclusion; student participation explicitly encouraged. Fully
accessible for an independent author who can attend the virtual symposium.
**Pitfalls.** Missing the IEEE 2-column PDF format (Markdown is not acceptable); overclaiming beyond the
data; not being able to attend/present.
**Tailoring levers.**

- Reframe as a **signal-processing target-definition audit**: the contribution is showing that target
  availability + baseline comparison change the conclusion — a methods contribution the SPMB audience values.
- Report the robustness honestly (multi-seed, persistence + Ridge baselines) and state the single-split
  limitation up front rather than letting a reviewer find it.
- Convert the draft to the official IEEE 2-column PDF well ahead of the SPMB 2027 deadline; include the
  Acknowledgement/References structure the template requires.

## IEEE ICASSP 2027 — MEDIUM confidence

**What they look for.** A flagship signal-processing conference with full-paper rigor; strong methodological
novelty and validation expected. Reviewer bar is high; a single-split, single-seed study is below the
typical acceptance bar as-is.
**Traits of accepted work.** Clear signal-processing novelty, rigorous evaluation (multiple splits/seeds,
baselines, uncertainty), and a contribution that generalizes.
**Format & logistics.** Full paper (IEEE format), deadline ~2026-09-16 for ICASSP 2027; strict page limits.
**Eligibility reality.** No HS exclusion, but the merit bar — not eligibility — is the blocker.
**Pitfalls.** Submitting current work as-is; insufficient novelty/validation for a flagship venue.
**Tailoring levers (only if pursuing later).**

- Do **not** submit as-is. First add grouped/repeated cross-validation, a streaming-compatible PAC
  estimator, uncertainty estimates, and a sharper signal-processing contribution.
- Position the target-availability audit as a _general_ lesson for closed-loop neural signal processing,
  not a single-dataset result.

## SfN Neuroscience 2026 — late-breaking — MEDIUM confidence

**What they look for.** A major professional neuroscience meeting; late-breaking abstracts should present
**genuinely new** post-regular-deadline analysis. Biology-dominated audience.
**Format & logistics.** Late-breaking window ~2026-09-08 to 09-15 (or until cap); abstract body ≤2,300
characters excluding spaces; SfN membership/account + abstract fee required.
**Eligibility reality.** Requires membership/account mechanics; the scientific bar for a computational
abstract at a biology venue is real (biological validation here is weaker than engineering validation).
**Pitfalls.** Submitting old analysis as "late-breaking"; missing membership/account setup; over-biological claims.
**Tailoring levers.**

- Only submit if **new** analysis is completed after the regular deadline (e.g., transition-specific
  evaluation, grouped CV) — the current 1,753-character abstract fits the limit but needs a genuinely new result.
- Frame PAC honestly as an EEG timing feature; avoid implying demonstrated physiological coupling.

## BCI Award 2026 — MEDIUM confidence (criteria are explicit; fit is the issue)

**What they look for.** The jury scores against explicit questions: **novel BCI application? new
methodological approach? new benefit for users? improvement in speed (bit/min)? improvement in accuracy?
results from real patients/users?** A project should score high on several of these.
**Traits of nominated work.** Real-time/online BCI function with demonstrated user benefit; the criteria
clearly reward _deployed/online_ systems and user outcomes.
**Format & logistics.** ≤2-page English PDF, opening with a 3–5 sentence summary, plus figures/tables and
current status; a ~2-minute film. Deadline ~2026-09-01; 12 projects nominated (~Sep 15); nominees invited
to a Springer chapter.
**Eligibility reality.** Open to any BCI group worldwide; no HS exclusion — but this is an **offline,
retrospective** project, and the scoring rewards real-time function and user benefit, so it is a genuine stretch.
**Pitfalls.** Overclaiming real-time/user-benefit that the project does not have; the criteria mismatch is
the core risk.
**Tailoring levers.**

- Be honest that this is **offline/retrospective**; compete on the **methodological-novelty** and
  **information-boundary auditing** axes (novel framing of target availability for adaptive neurotech),
  not on real-time user benefit.
- Frame as adaptive-neurotechnology _methodology_ rather than a finished BCI; treat this as an optional
  stretch, not a core target.
  > **Naming caution:** the academic "BCI Award" here is the _Annual BCI Research Award_ (bci-award.com).
  > Do not confuse it with the Business Continuity Institute or British Construction Industry awards (unrelated).

## International BCI Meeting 2027 — LOW/MEDIUM confidence

**What they look for.** BCI Society meeting; poster/oral abstracts framed for the adaptive-neurotechnology /
closed-loop community.
**Format & logistics.** Abstracts open ~2026-11-09, deadline ~2027-01-15, notification ~2027-03-03, meeting
~2027-06-07. Travel timeline sits after college applications.
**Tailoring levers.** Prepare after URTC/STS; strengthen with repeated splits and an adaptive-neurotechnology
framing. Good for update letters, not early apps.

---

# CLUSTER C — Poster/symposia + identity venues

## MIT URTC 2026 — poster/lightning — HIGH confidence

**What they look for.** Peer-reviewed by faculty, grad students, and industry pros on **originality,
quality of content, and adherence to conference themes.** Submissions must be the author's "full and sole work."
**Traits of accepted work.** Clear, well-presented undergraduate-level research aligned to a URTC track;
professional graphics; a comprehensible narrative.
**Format & logistics.** Poster ~2×3 ft (title in ~1" CAPS); lightning talk ≤5 min; poster/lightning abstract
≤1,000 words. **Poster/lightning does NOT publish to IEEE Xplore** (paper track does). Peer-reviewed; plagiarism-checked.
**Eligibility reality — the key finding.** **Unaffiliated high-school students may submit poster/lightning.**
The **paper track** requires affiliation with a faculty-mentored program (ASSIP/RISE/RSI/SSP) _or_ substantial
work with university students. **AP/IB or other "college-level" high-school programs do NOT count.** On the
stored record (independent work), the paper track is not available — **poster/lightning is the correct route.**
**Pitfalls.** Attempting the paper track without genuine university affiliation; exceeding the 5-page paper
limit (if paper); not aligning to a track.
**Tailoring levers.**

- Submit **poster or lightning talk** — the safe, eligible, MIT-branded route. Reserve the paper track only
  if a genuine ASSIP/RISE/RSI/SSP-type affiliation or substantial university-student collaboration truthfully exists.
- Align the abstract to a relevant URTC track (computation / engineering / health tech); keep it ≤1,000 words.
- Reuse the polished manuscript content, compressed into a poster narrative built around the audit story.

## BMES 2026 High School Poster Expo — HIGH confidence — **TOP PRIORITY**

**What they look for.** Posters "focused specifically on biomedical engineering areas"; **"No lab experience
required — just curiosity and creativity."** It is a **scored competition**: historically the **top-10
highest-scoring posters get free registration + a $250 travel stipend, and the top 3 receive cash prizes.**
**Traits of accepted/winning work.** Clear BME framing, a well-structured template abstract with an
informative labeled figure, and a concise conclusion stating implications/significance.
**Format & logistics.** 2026 Annual Meeting in **Orlando; HS Poster Expo on Saturday, Oct 24**; abstract
deadline ~2026-08-18. Uses the official HS poster abstract template (Intro / Methods / Results / Conclusions,
Times New Roman, labeled figure with 10pt bold caption). **Under-18 chaperone required** (separate $100
registration each). Accepted students may attend select Saturday sessions.
**Eligibility reality.** HS juniors/seniors by Fall 2026 — **fully eligible for an independent author.** This
is the strongest near-term actionable target.
**Pitfalls.** Framing that isn't clearly biomedical engineering; missing the abstract template structure;
forgetting the chaperone registration.
**Tailoring levers.**

- Frame explicitly as **biomedical engineering**: EEG signal processing for adaptive neuromodulation, with
  the audit as an engineering-rigor contribution.
- Use the official template sections exactly; include one clean, well-captioned figure (the controller
  comparison or horizon sweep) referenced in the abstract text.
- Keep it retrospective; arrange the chaperone + registrations early.

## BMES 2026 General Abstract — HIGH confidence — **SKIP**

**What they look for.** General abstracts route to the 19 technical tracks for podium/poster — but this track
is for **graduate, doctoral, and professional** submissions, with a $65 fee, BMES account, and required attendance.
**Eligibility reality.** **Wrong presenter pool for a high-school sole author.** Use the HS Poster Expo instead.
**Tailoring levers.** None — default to the HS Poster Expo unless BMES explicitly approves eligibility.

## SCCUR 2026 — MEDIUM confidence

**What they look for.** Undergraduate-research abstracts (≤1,500 characters) for poster/oral; a California
conference useful for an "accepted/presented" line before college deadlines.
**Eligibility reality — conditional.** High-school students are eligible **only** if they participated in
**sustained college-level or equivalent faculty-guided research.** Independent work does not clearly qualify —
**email the directors first** if fully independent.
**Format & logistics.** Early window through ~2026-07-31 (guaranteed decision before early registration);
final deadline ~2026-10-09; conference ~2026-11-21 at SDSU.
**Pitfalls.** Asserting faculty-guided status that isn't real; the eligibility condition is the blocker.
**Tailoring levers.**

- Only submit if the faculty-guided condition is honestly met, or after directors confirm an independent HS
  student may present. Keep the abstract ≤1,500 characters; frame as computational research.

## AISES National Conference 2026 — MEDIUM confidence

**What they look for.** Student research via the **Indigenous Abstract Framework (WHAT / SO WHAT / NOW WHAT)**
with community-impact fields; Indigenous-centered mission framing.
**Eligibility reality — conditional on genuine mission fit.** Middle-school through doctoral eligible, but the
identity/community-impact framing **must be authentic.**
**Pitfalls.** Forcing an identity or community-impact narrative that isn't genuine — do not do this.
**Tailoring levers.** Apply **only** if the framework fits honestly. If it does, structure the abstract as
WHAT (the audit) / SO WHAT (target-availability matters for adaptive neurotech) / NOW WHAT (what must be
validated before deployment), with authentic community framing.

## SACNAS NDiSTEM 2026 — MEDIUM confidence — **LIKELY SKIP**

**What they look for.** Student research presentations (community-college through postdoc).
**Eligibility reality — blocked.** The official page points to community-college/undergrad/post-bacc/grad/
postdoc presenters; a prior audit found an **age-18-at-conference** requirement plus student/postdoc-level
status and **PI approval for abstract publication.** A 17-year-old independent HS student is likely ineligible.
**Tailoring levers.** Skip unless SACNAS confirms eligibility in writing. Contingency abstract only.

---

## Sources (official pages and rubric documents)

- Regeneron STS judging/awards & FAQ: https://www.societyforscience.org/regeneron-sts/judging-and-awards/ ,
  https://www.societyforscience.org/regeneron-sts/frequently-asked-questions/ ,
  https://www.societyforscience.org/regeneron-sts/application-requirements/
- ISEF Grand Award judging criteria: https://www.societyforscience.org/isef/grand-award/criteria/ ; affiliated-fair
  judging: https://www.societyforscience.org/isef/affiliated-fair-network/judging-at-your-fair/ (100-pt rubric breakdown)
- JSHS core rules + NorCal region: https://www.jshs.org/ , https://www.jshs.org/national-symposium/presentation-guidelines/ ,
  https://cob.sfsu.edu/initiatives-centers/jshs (NorCal student guidelines)
- IEEE SPMB guidelines + CFP: https://www.ieeespmb.org/ , https://isip.piconepress.com/conferences/ieee_spmb/ ,
  https://www.ieeespmb.org/2025/forms/cfp/ieee_spmb_2025_cfp.pdf (~50% acceptance; 12 oral + 12–15 posters)
- MIT URTC submission + FAQ: https://urtc.mit.edu/submission , https://urtc.mit.edu/faq (HS eligibility rule)
- BCI Award criteria: https://www.bci-award.com/Home (scoring questions; 2-page + film format)
- BMES 2026 HS Poster Expo: https://www.bmes.org/2026/annualmeeting/high-school-poster-expo ; abstract template:
  https://www.bmes.org/hubfs/2025%20BMES%20Annual%20Meeting%20High%20School%20Poster%20Abstract%20Template.pdf ;
  general abstracts: https://www.bmes.org/2026/annualmeeting/abstracts
- SCCUR: https://www.sccur.org/ , https://www.sccur.org/abstracts , https://research.sdsu.edu/sccur-2026
- AISES: https://conference.aises.org/research/student ; SACNAS: https://www.sacnas.org/conference/research-presentations
- ICASSP 2027: https://2027.ieeeicassp.org/ ; SfN 2026: https://www.sfn.org/meetings/neuroscience-2026/call-for-abstracts ;
  BCI Meeting 2027: https://bcisociety.org/bci-meeting/

_Deadlines and cycle openings drift year to year. The tracker's `submission_tracker.json` holds the current
working dates; always re-verify against the official page before submitting._
