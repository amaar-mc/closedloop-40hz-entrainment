# Synopsys Championship Reference Guide

**Santa Clara County Science and Engineering Fair**
**Fair Day: March 10, 2026 at San Jose Convention Center, South Hall**

---

## Key Deadlines

| Date                   | Action                                        |
| ---------------------- | --------------------------------------------- |
| Feb 20, 2026 (8 PM)    | Title, category, field of study changes due   |
| Feb 27, 2026 (8 PM)    | Abstract upload deadline (250 words max, PDF) |
| Mar 5, 2026 (11:59 PM) | Abstract posted for pre-judging review        |
| Mar 8, 2026            | Judge assignments and abstract access         |
| Mar 10, 2026           | Fair Day / Judging Day                        |

---

## Judging Criteria (40 Points Total)

| Category                 | Points | What Judges Evaluate                                                                                               |
| ------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------ |
| Scientific Thought       | 10     | Problem significance, clear hypothesis, controlled variables, sufficient literature, conclusions justified by data |
| Creativity               | 10     | Originality of topic or approach, novel methodology, student's direct contribution                                 |
| Independent Work / Skill | 10     | Student's execution, software competency, appropriate acknowledgment of help                                       |
| Thoroughness / Clarity   | 10     | Data adequacy, replication, documentation completeness, clear communication                                        |

---

## Display Board Rules

- Max size: 48" wide x 15" deep x 60" tall (3-4 foot height recommended for readability)
- Min font: 24pt body, title readable from 3+ feet
- Required: Introduction, Background, Hypothesis/Goal, Methods, Results (graphs preferred over tables), Conclusions, References
- Prohibited: School names/logos, QR codes, contact info, institutional logos, active hyperlinks
- Abstract: Printed on TABLE, not board (max 250 words)
- Metric/SI measurements preferred
- Use black or dark type for legibility
- 3-5 bulleted statements per section, 10-20 words each

---

## ML/AI Project Requirements (NEW for 2026)

### 6 Mandatory Requirements

All six must be addressed in the project:

| #   | Requirement                  | How We Address It                                                                                                                                         |
| --- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Data Source Traceability** | OpenNeuro ds005048 (Lahijanian et al. 2024), publicly available, de-identified                                                                            |
| 2   | **AI Rationale**             | TCN chosen for causal temporal prediction; EEGNet for compact EEG processing. Both justified by data constraints (17K samples, 35 subjects)               |
| 3   | **Data Curation Plan**       | Artifact zeroing at +/-100 uV, 7 frontal channels selected, subject-level splits, windows with NaN excluded                                               |
| 4   | **Unique Insights**          | Horizon sweep (TCN predicts at 5-10s where baselines fail), habituation variability (49/51% split), adaptive efficiency gains                             |
| 5   | **Model Development Plan**   | Parameter counts sized for dataset (12 samples/param for EEGNet). Dilations [1,2,4,8] chosen for 31-step receptive field. 4 architectural variants tested |
| 6   | **Validation Strategy**      | Subject-level train/val/test splits (24/5/6 subjects). No subject appears in multiple splits. Shuffle-label sanity check R²=-0.332                        |

### Must Test At Least 2 of 5 Criteria

| Criterion            | Status  | Evidence                                                                                                                                |
| -------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Accuracy**         | TESTED  | R², RMSE, correlation at 6 horizons. Horizon sweep with 3 baselines                                                                     |
| **Generalizability** | TESTED  | 6 held-out test subjects never seen during training or model selection. Subject-level splits prevent data leakage                       |
| **Interpretability** | TESTED  | Ridge feature ablation: PAC features R²=0.859, spectral only R²=0.045. Shuffle-label test. TCN attention weight analysis (script ready) |
| Fairness             | N/A     | Not a decision system affecting people                                                                                                  |
| Scalability          | PARTIAL | 1,457 and 31,000 params enable embedded deployment. No formal latency benchmark                                                         |

**We test 3 of 5 criteria: Accuracy, Generalizability, and Interpretability.**

---

## Notebook Requirements

- **MANDATORY** for all participants (no notebook = no awards, even for best project)
- Paper or digital, must be present on Check-in Day and Fair Day
- Upload 4 pages to Judging Folder (first page, 2 middle pages, last page) as PDF
- Must show: chronological entries with dates, raw data, problems encountered, iterations, references
- For digital notebooks: Do NOT delete errors -- strike through and annotate instead
- For software projects: include GitHub activity logs, README files, dated progress logs
- Sufficient detail that another person could replicate the experiment
- Judges examine the notebook during the interview

---

## Interview Format

- Judge preview (12:30-1:30 PM): Judges review boards WITHOUT students present
- Interviews (1:30-4:30 PM): ~8-10 min per project
- 1-2 minute verbal summary (conversational, no slides, no reading from board)
- Then judge Q&A (probing questions to test understanding)
- Judges review notebook during interview
- Software demos expected for computational projects (short video acceptable)
- Adults/parents NOT allowed in hall during judging
- ~40% of projects in each group receive awards

---

## Category

Our project falls under:

- **Category:** Biological Science and Engineering
- **Field:** Computational Biology and Bioinformatics (Project code 5)
- **ISEF Subcategory:** Computational Neuroscience (NEU)

---

## AI Ethics Disclosure

- AI tools (Claude Code) used for code development assistance
- All experimental design, research decisions, and scientific interpretation done by the student
- All code is original or properly attributed
- No AI used to generate the abstract, poster text, or scientific claims
- Must be disclosed if asked by judges

---

## Awards

- Category Awards: 1st, 2nd, Honorable Mention (~40% of projects receive awards)
- Grand Prize: Top projects evaluated by doctoral-level judges, ISEF trip
- ~100 projects advance to California State Fair
- ~40 sponsored awards from companies
- Total ~$60,000 in prizes

---

## Questions to Prepare For

1. "Why is static R² only 0.287?" -- PAC has SNR=-4.73 dB, 8 architectures converge at this ceiling. This is not a failure — it's the dataset's information limit
2. "Did the TCN beat persistence?" -- Only at 3+ second horizons, but those are the horizons that matter for control. At 5-10s, baselines give negative R² (worse than guessing the mean). The TCN is the only method with useful signal there (+0.5 R² margin)
3. "How do you know there is no leakage?" -- Shuffle-label test (R²=-0.332), subject-level splits (6 test subjects never seen), causal construction (left-only padding), train-only normalization
4. "Is the simulation realistic?" -- The simulation is one validation layer. The primary results come from real-data replay on all 35 subjects' actual EEG. No simulation involved in the main controller comparison
5. "What did the model learn?" -- Ridge ablation shows PAC features dominate (R²=0.859 vs 0.045 spectral-only). The model learns temporal PAC dynamics — how coupling evolves over time. This is the relevant signal for predicting future entrainment state
6. "Why not use a larger model?" -- 8 architectures tested (1.5K to 1.1M params). All converge near R²=0.287 for static prediction. Data is the bottleneck, not architecture
7. "How does this help patients?" -- TCN controller targets 82.6% of low-PAC windows (vs 51.7% reactive, 61.4% fixed). In adaptive music therapy, this means therapeutic sound is delivered almost exclusively when the brain needs it, reducing unnecessary stimulation and session fatigue
8. "Does the TCN drive the closed-loop controller?" -- Yes. The trained TCN is integrated into a predictive controller (`run_tcn_validation.py`) that was replayed on all 35 subjects' real EEG data. The TCN predictive controller achieves 72.1% epoch alignment vs 64.5% reactive (Hedges' g = 1.31, p < 0.001), targets 82.6% of low-PAC windows (vs 51.7%), and reaches 91% of the oracle bound. All 35/35 subjects benefit.
9. "Did you use AI tools?" -- Yes, Claude Code was used for code development assistance. All experimental design, data analysis decisions, research direction, and scientific interpretation are my own work. This is disclosed on the poster board.

---

## Pre-Submission Checklist

| Task                                | Deadline        | Status                                                             |
| ----------------------------------- | --------------- | ------------------------------------------------------------------ |
| Title/category submitted            | Feb 20 (passed) | Confirm done                                                       |
| Abstract PDF upload (250 words max) | Feb 27, 8 PM    | Text ready, needs PDF formatting                                   |
| Notebook 4-page PDF upload          | Before fair day | Select first page, 2 middle pages, last page                       |
| Physical poster board construction  | Before Mar 10   | Text ready in POSTER_BOARD.md                                      |
| Software demo video (60-90 sec)     | Before Mar 10   | Record: run_tcn_validation.py output + timeline_example.png figure |
| Practice 1-2 min verbal summary     | Before Mar 10   | Use questions above to prepare                                     |
| Print abstract for table            | Before Mar 10   | From POSTER_BOARD.md abstract section                              |
