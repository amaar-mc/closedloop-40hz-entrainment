# Synopsys Championship: Winning Abstract Analysis

**Prepared for Amaar Chughtai — February 27, 2026**

---

## 1. About the Synopsys Championship

The Synopsys Silicon Valley Science and Technology Championship is a regional ISEF-affiliated science fair in Santa Clara County. It's the gateway to Regeneron ISEF (International Science and Engineering Fair).

- **Location:** San Jose Convention Center, South Hall
- **Your Fair Day:** March 10, 2026
- **Abstract deadline:** February 27, 2026 at 8 PM (TODAY!)
- **~500 judges** across category and sponsored awards
- **~40% of projects** receive category awards
- **10-12 Grand Prize winners** advance to ISEF

---

## 2. Judging Criteria (40 Points)

| Dimension | Points | Key Factors |
|-----------|--------|-------------|
| Scientific Thought | 10 | Problem significance, clear hypothesis, controlled variables, conclusions justified by data |
| Creativity | 10 | Uniqueness of topic/approach, novel methodology, YOUR contribution |
| Independent Work/Skill | 10 | What YOU did vs mentoring, technical proficiency, programming skill |
| Thoroughness/Clarity | 10 | Data adequacy, replication, documentation, clear communication |

---

## 3. Directly Comparable 2025 Winning Projects

These are the projects most similar to yours from the 2025 Synopsys Championship:

### 3.1 Claire Xu (Harker, 10th grade) — GRAND PRIZE, ISEF FINALIST
**"Non-Invasive Blood-Based Early Alzheimer's Detection Using Sex-Specific Brain-Blood Graph Reinforcement Learning"**
- **Relevance:** Alzheimer's + deep learning + biomarker detection
- **Why it won:** Novel approach (graph RL), clinical significance (Alzheimer's), specific technical innovation (sex-specific models)

### 3.2 Danielle Steinbach (Harker, 11th grade) — 1ST AWARD + IBM AWARD
**"A multi-institution foundation model for EEG biomarkers of brain disorder progression, classification, and drug response"**
- **Relevance:** EEG + deep learning + clinical application
- **Why it won:** Scale (multi-institution), clinical utility, EEG-specific innovation

### 3.3 Neuropod Team (BASIS Independent, 11th grade) — ACM 2ND PLACE ($600)
**"Neuropod: An Arduino-Based Mastoid EEG Device Integrating Reinforcement Learning for Tracking Neurodegenerative Diseases"**
- **Relevance:** EEG + RL + neurodegeneration
- **Why it won:** Hardware + software integration, RL applied to clinical monitoring

### 3.4 DeepSleep Team (Harker, 9th grade) — 2ND AWARD
**"DeepSleep: A Novel Convolutional Neural Network for Sleep Apnea Detection by Analyzing Electroencephalogram Data"**
- **Relevance:** EEG + CNN + clinical detection
- **Why it won:** Practical application, novel architecture for the domain

---

## 4. How YOUR Project Compares

### Strengths vs. Comparable Projects

| Dimension | Your Project | Competitors |
|-----------|-------------|-------------|
| Clinical significance | Alzheimer's + adaptive therapy | Similar (Alzheimer's, neurodegeneration) |
| Data scale | 35 real patients, public dataset | Variable (some use private data) |
| Technical novelty | **Closed-loop temporal prediction at 5-10s** | Classification tasks only (no temporal forecasting) |
| Statistical rigor | Hedges' g, Wilcoxon, 95% CIs (normal approximation), 35/35 subjects | Most use only accuracy/AUC |
| Model justification | 8 architectures tested, horizon sweep | Most test 1-2 models |
| Data integrity | Shuffle-label test, subject-level splits | Rarely reported |

**Your unique differentiator:** None of the comparable projects do **temporal prediction for proactive control**. They all do classification or detection (identifying a condition after it happens). Your project predicts a brain state before it happens and acts on it — this is a fundamentally more ambitious engineering goal.

---

## 5. Anatomy of a Winning Abstract

### Structure (for 250-word limit)

| Section | Words | Proportion | Purpose |
|---------|-------|------------|---------|
| Hook/Motivation | 30-40 | 12-16% | Establish stakes — WHY should the judge care? |
| Problem Statement | 20-30 | 8-12% | WHAT specific gap exists? |
| Approach/Methods | 50-70 | 20-28% | HOW you solved it (concise) |
| Results | 80-100 | 32-40% | WHAT did you find? (BIGGEST section) |
| Conclusions/Impact | 30-40 | 12-16% | SO WHAT? — broader implications |

**Key insight: Results are the dominant section.** Unlike academic abstracts where methods dominate, science fair abstracts should devote 32-40% to specific, quantified results.

### What Makes Abstracts Win

1. **Lead with the disease, not the model.** Judges empathize with patient impact, not architecture elegance.

2. **Present comparisons, not absolute numbers.** "R²=0.25" means nothing alone. "+0.5 R² margin over all baselines which collapse to negative" tells a story.

3. **Use ONE concrete memorable detail.** "Every patient benefited" or "91% of oracle performance" — judges remember one killer statistic.

4. **Avoid jargon walls.** Define acronyms. Replace "operationally relevant range for proactive control" with "the time window needed to act before entrainment is lost."

5. **End with broader impact.** The last sentence should answer "who cares beyond this experiment?"

### Winning Title Formula

**[System Name]: [Technical Method] for [Clinical Application]**

Examples:
- "GRFSense: Early Parkinson's Disease Assessment..."
- "OphthaLVLM: A Locally Deployable Large Vision-Language Model..."
- "DeepSleep: A Novel Convolutional Neural Network for Sleep Apnea..."

**Consider:** A catchy system name makes your project memorable during a day of judging 12 projects.

---

## 6. ML/AI Project Specific Requirements (NEW for 2026)

The Synopsys Championship has **6 mandatory requirements** for data/ML projects:

| # | Requirement | Your Status |
|---|-------------|-------------|
| 1 | Data Source Traceability | PASS — OpenNeuro ds005048, publicly available |
| 2 | AI Rationale | PASS — TCN chosen for causal temporal prediction; EEGNet for compact EEG |
| 3 | Data Curation Plan | PASS — artifact rejection, channel selection, subject-level splits |
| 4 | Unique Insights | PASS — horizon sweep, habituation variability, efficiency gains |
| 5 | Model Development Plan | PASS — 8 architectures tested, parameter counts sized for dataset |
| 6 | Validation Strategy | PASS — subject-level splits, shuffle-label test, 6 held-out subjects |

Must test at least 2 of 5 criteria: **You test 3** (Accuracy, Generalizability, Interpretability).

---

## 7. Strategic Advice for March 10

### During the 8-10 minute interview:

1. **Open with the patient story** (30 seconds): "Imagine an Alzheimer's patient wearing headphones. Right now, they get the same stimulation schedule no matter how their brain responds. My system predicts when they'll lose the therapeutic rhythm and adapts in real time."

2. **The horizon sweep is your intellectual centerpiece.** If you can make the judge understand WHY 5-10 seconds matters and WHY baselines fail there, you've won on Scientific Thought.

3. **"All 35 subjects benefited"** — say this explicitly. It's your most powerful statistic.

4. **Anticipate the AI question:** "Did you use AI tools?" → "Yes, Claude Code for coding assistance. All experimental design, data analysis decisions, and scientific interpretation are mine."

5. **Show the timeline figure** (results/figures/timeline_example.png) during the demo — it visually shows the TCN catching a PAC decline before reactive control does.

6. **Know your limitations cold.** "Real-data validation uses offline replay, not live streaming. Live closed-loop validation is future work." Judges respect honesty.

---

*Prepared February 27, 2026*
