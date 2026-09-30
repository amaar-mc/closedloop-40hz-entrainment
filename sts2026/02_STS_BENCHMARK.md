# Regeneron STS benchmark for the closed-loop 40 Hz EEG project

This was compiled on 2026-09-30 for the **STS 2027** cycle. **The deadline is Nov 5, 2026 at 8:00 pm ET, and recommendations are due at the same time.** The support-request cutoff is Nov 4 at 8 pm ([Rules][R]). Raw notes with every quote are in `notes/sts_raw_notes.md`. Anything marked *Inference* is my reading, not official wording.

## a. Requirements and judging

- **Research report:** "**20 pages or less**". The title page, abstract and bibliography don't count, but "Appendices count". Format: 11 pt minimum, 1.5 spacing, 1" margins, one column, PDF of 4 MB or less. Only finished work with results qualifies; the report is "evidence of research ability, scientific originality and creative thinking." ([RRG][G]) **Every figure needs a credit line, including your own** ([Citation Guide][C]).
- **Other parts:**
  - Two essays of 200 words each (on your potential as a scientist, and on an accomplishment or challenge) and a layperson summary.
  - "What Did You Do?", in six parts of 200 words each; the form calls it "the bulk of the application". Also "What didn't you do?", limitations and impact ([AQ][Q]).
  - A Project Recommendation, which asks the mentor to credit the student's "Research Question, Procedural Design, Data Collection, Data Analysis, Drawing Conclusions" and asks about "creativity and ingenuity" ([P]). Also an Educator Recommendation and a transcript ([RQ]).
- **Judging:**
  - At least three PhDs score four areas: "Research Report and Scientific Merit; Student Contribution to the Research; Academic Aptitude and Achievement; Overall Potential as a Future Leader" ([Rules][R]).
  - The "greatest weight [is] given to the Research Report". Judges look for "exceptional research skills … innovative thinking, promise as a scientist", and the Society does "not share rubrics" ([FAQ][F]).
  - Finalist announcements cite "originality and creativity" for 2023–26 ([F26]) and "scientific rigor" for 2020–22 ([F22]).
- **Independence:** team projects are not eligible. Lab work is allowed, but "clarity and adequate acknowledgment of an individual's role and independence … is vital" ([F]).
- **Public data:** preexisting public data is IRB-exempt as long as you cite the database ([R]). The application asks "How did you get the data …?" ([Q]).
  - ⚠️ Failing to get "IRB approval before testing an invention, software or product" disqualifies an entry ([FTQ][T]).
  - *Inference:* don't test the stimulator on any person unless IRB approval came first. Keep testing to offline replay of OpenNeuro data.

## b. AI-use rules (explicit and binding)

- "Students may not use generative Artificial Intelligence (AI) to write Regeneron STS application questions, draft the Research Report or generate citations. … Use of AI tools for student research projects is permitted, and should be disclosed and appropriately cited." ([Rules, Entry Rules][R])
- The report guidelines add: "required to write the paper without the use of generative AI (ChatGPT or other programs)". AI-made reference lists are banned, and "Discovery of a fake reference will result in disqualification" ([RRG][G]). Fake references were the **#1 reason projects failed to qualify in 2026** ([FTQ][T]).
- The student and mentor both sign the Ethics Statement: "I did not use AI tools to draft the paper or responses to application questions" ([Rules][R]).
- The [AI Usage Chart][A] allows **AI-written code** "only with explicit citation stating which portions of the code were AI generated and with a log of the prompts". It allows AI suggestions of statistical tests with a prompt log, since "Interpretation of data must be done by the student researcher". Grammar-only edits must be credited. AI-written conclusions and starter bibliographies are "Never acceptable".
- The application's disclosure section is a checklist of AI uses plus a 200-word explanation. It also asks whether an AI expert should review the entry ([Q]).
- *Inference:* the report guidelines are stricter than the chart, so keep the report prose AI-free. Tag AI-assisted code in the repo and archive the prompt logs now.

## c. Strongest computational / no-wet-lab precedents (2020–2026)

In the table, F = finalist and ordinals = top-10 place. **Tags:** V = independent validation; R = replicates or falsifies a prior claim; M = interpretability that leads to a mechanism; S = ground-truth simulation; T = new public tool or resource; F = reframes the problem; X = works across conditions or datasets; C = clinical link.

| Year | Student | Title (as listed) | Data source | Beyond "trained a model" | Tags |
|---|---|---|---|---|---|
| 2020 F | Victoria Graf | Determining Stimulus Selection Parameters for Treatment of Neurological Disorders Using Statistical Analysis of EEG Signal Entropy | EEG and music data from a Stanford study ([book][B20]) | Tested whether a stimulus tailored to the listener raises EEG complexity; linked to low-complexity activity in Alzheimer's | C |
| 2020 F | Cynthia Chen | Decoding Neural Networks: Discovery of Anti-Tumor B Cell Receptor Motifs … | Pan-cancer dataset | Decoded the network and "discovered and validated 65 … motif signatures of 13 … cancer types" ([page][F20]) | M V X |
| 2021 2nd | Noah Getz | A Novel High Throughput Method for Prescreening Drugs … Alzheimer's Disease and COVID-19 | Imbalanced drug datasets | Recast classification as information retrieval; nominated two drug candidates ([winners][W21]) | F C |
| 2021 F | Tali Finger | A Genomic-Based Investigation of Repetitive Behaviors Across Four Neurodevelopmental Disorders … | Genomic / miRNA data | Treated four disorders as one spectrum, then tested that idea ([book][B21]) | F X |
| 2022 1st | Christine Ye | Inferring the Neutron Star Maximum Mass … with Spin | Public LIGO data plus simulated observations | Forecast future observations with simulations; showed spin must be accounted for ([winners][W22]) | S |
| 2022 3rd | Amber Luo | RiboBayes: A Wavelet Transform-Based Computational Platform … | Ribosome-profiling data | A new platform where "current algorithms are unable" to do the job ([winners][W22]) | T |
| 2022 5th | Neil Chowdhury | Modeling the Effect of Histone Methylation on Chromosomal Organization … | Own molecular-dynamics simulation | "accurately reproduced recent experimental results" and then proposed a mechanism ([winners][W22]) | S R |
| 2022 F | Rohan S. Ghotra | Uncovering Motif Interactions from Convolutional Attention Networks … | Simulated DNA with known ground truth | GLIFAC tool; beat existing methods on the simulated ground truth ([book][B22]) | S M T |
| 2022 F | Benjamin Choi | An Ultra-Low Cost, Mind-Controlled Transhumeral Prosthesis … Brainwave Interpretation Algorithm | Own EEG recordings from volunteers | Built a $300 device and compared it in physical tests ([book][B22]) | V C |
| 2023 1st | Neel Moudgal | Using Unassigned NMR Chemical Shifts To Model RNA Secondary Structure | NMR shifts plus a structure library | Removed a known bottleneck: "eliminates the need to assign" shifts ([winners][W23]) | F |
| 2023 F | Kevin Zhu | Recurrent Repeat Contractions and Micro-Changing Short Tandem Repeats … | Genomic database | Mined the database, then ran "experiments which validated" detection in plasma ([profile][KZ]) | V |
| 2024 2nd | Thomas Cong | Overlooked Covariates in Metabolite Abundance Levels … Across Multiple Cancer Types | Multi-cancer omics data | Tested a widely assumed premise "and found it questionable" ([winners][W24]) | R X |
| 2024 F | Riya Tyagi | Using Computer Vision To Disentangle Features Enabling AI To Learn Self-Reported Race … | 11,000 retinal images | Trained hundreds of CNNs as an experiment and traced the bias to U-Net ([page][F24]) | M |
| 2024 F | Alexis Li | BrainSTEAM: A Practical Pipeline for Connectome-Based fMRI Analysis … | fMRI | Covered ASD, ADHD and depression; "outperformed" existing tools ([page][F24]) | T X |
| 2025 1st | Matteo Paz | The VarWISE All-Sky Infrared Variability Survey — Classification of 1.9 Million Astronomical Objects … | NASA WISE, about 200 TB | A complete census with 1.5 M new objects ([winners][W25]) | T |
| 2025 F | Siddharth Nirgudkar | Contextualized Transfer Learning … in Resource-Limited Settings | "publicly sourced data" | New method for heterogeneous data; beat other methods on Alzheimer's diagnosis ([page][F25]) | F C |
| 2026 2nd | Edward Kang | RetinaMind: Convergent In Silico and In Vitro Evidence … | "large public dataset" of retinal images | Interpreted the model, then checked it in cell models ×2. The Society's president said: "He didn't just build a model" ([winners][W26], [Smithsonian][SM]) | M V C |
| 2026 8th | Leon Wang | Repurposing Idiopathic Pulmonary Fibrosis Drugs To Treat Vascular Alzheimer's Dementia … | Public data plus a cell model | "confirmed previous findings" in public data, then tested two FDA-approved drugs ([winners][W26]) | R V C |
| 2026 F | Frances Liang | PLI-Analyzer: A Novel Platform for Quantitative Assessment … of AI-Predicted Protein-Protein Complexes | Sequence databases | Audited AlphaFold3 and Boltz-2 (about half accurate); released an open-source tool and web app ([page][F26]) | R T |
| 2026 F | Jashvi Desai | Neuroinflammatory Signatures and Compensatory Prefrontal Mechanisms in Long COVID-19: Insights From 7T MRI and Cognitive Modeling | MRI plus memory tests | Linked brain structure to cognition ([page][F26]) | C |

## d. Patterns

Counts come from my own tagging of the 20 rows above (*inference*).

| Pattern | Count (of 20) | Why judges value it | Application to 40 Hz EEG (idea only) |
|---|---|---|---|
| C: clinical link | 7 | Shows impact; "Project Benefits and Impact" is a required question | Correlate the 40 Hz response metric with cognition in public Alzheimer's data. Make **no diagnostic claims or apps** ([Rules][R]) |
| V: independent validation | 5 | The Society president's "didn't just build a model" comment ([SM]) | Replay recorded EEG through the real-time loop on actual hardware to measure end-to-end latency and phase error |
| T: new public tool | 5 | Reusable; shows the student owns the method | Release an open closed-loop phase-tracking benchmark: code plus simulated ground truth |
| R: replicate or falsify | 4 | Rigor, and the answer is not predetermined | Pick one specific published 40 Hz ASSR or entrainment claim and test it; report nulls |
| F: reframe | 4 | Originality (the 2023–26 selection wording) | Treat stimulus timing as a phase-targeting control problem instead of open-loop flicker |
| M: mechanism | 4 | Explains *why*, not only how accurate | Test whether the response is a rhythm that persists after the stimulus stops or only an evoked response, using a pre-registered test |
| X: cross-dataset | 4 | Shows the result generalizes | Run the same pipeline, frozen in advance, on at least two OpenNeuro datasets from different sites |
| S: ground-truth simulation | 3 | Supplies the truth that public data lacks | Inject synthetic 40 Hz signals with known phase into real resting EEG and report error against SNR |

*Inference:* every top-10 winner in the table carries at least one of V, R, S, T or F. At scholar level, EEG classify-or-decode titles appear 2–4 times a year ([2025 scholars][S25], [2026][S26]). I found no 2023–26 finalist title containing "EEG".

## e. Best-fit category

The official list: Animal Sci; Behavioral Sci; Biochemistry; Bioengineering; Cellular & Molecular Bio; Chemistry; **Computational Biology & Bioinformatics**; Computational Humanities; Computer Sci; Earth & Planetary; Engineering; Environmental Sci; Genomics; Materials Sci; Mathematics; **Medicine & Health**; **Neuroscience**; Physics; Plant Sci; Social Sci; Space Sci ([Categories][K]).

The category "will determine the expertise of the initial review only". Evaluators "are able to request additional expertise … or suggest category reassignment" ([K]).

**Recommendation: Neuroscience** (*inference*).
- Its definition covers "perception … the functional organization of large scale cerebral systems", which is what a 40 Hz auditory-entrainment finding is about.
- Recent precedents placed their brain-data ML projects in Neuroscience: Alexis Li (2024), Edward Kang (2nd place 2026) and Leon Wang (2026) ([F24], [W26]).
- **Alternative: Computational Biology & Bioinformatics**, if the headline result is the algorithm or benchmark itself. Nirgudkar's Alzheimer's model was entered there ([F25]).
- Avoid Medicine & Health: there are no clinical data, and the rules forbid diagnosing or treating conditions. Bioengineering fits only if the hardware is the main contribution (Choi's precedent, [B22]).

## f. What makes a title flag-worthy (observations)

- **None of the seven first-place titles from 2020–26 contains "Novel", "AI", "machine learning" or "deep learning"**, even though Petersen, Rajaram and Paz were ML or computational projects. By contrast, "Novel" appears in about 19% of finalist titles (about 50 of 270). The winners name the object and the claim instead ([notes §10]).
- **Scope words signal a complete answer:** "Continent-Wide", "All-Sky … 1.9 Million", "The Complete Set", "Across Four … Disorders", "Across Multiple Cancer Types".
- **Titles state the type of evidence or the finding:** "Convergent In Silico and In Vitro Evidence", "Reveals an Oncogenic Role", "Overlooked Covariates".
- **Named tools with an "ACRONYM:" prefix are common**, in about 24 of 270 titles (BrainSTEAM, RiboBayes, PLI-Analyzer). They work when the subtitle says what the tool tests or finds.
- **Format rules:** AP title case, a short title of 100 characters or less, and symbols written out in capitals, e.g. "GAMMA" ([AQ][Q]).

[R]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Official-Rules.pdf
[G]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Research-Report-Guidelines.pdf
[A]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/AI-Usage-Chart.pdf
[K]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Categories.pdf
[C]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Citation-Guide.pdf
[Q]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Application-Questions.pdf
[P]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Project-Rec.pdf
[T]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Common-FTQs.pdf
[F]: https://www.societyforscience.org/regeneron-sts/frequently-asked-questions/
[RQ]: https://www.societyforscience.org/regeneron-sts/application-requirements/
[F20]: https://www.societyforscience.org/regeneron-sts/2020-finalists/
[F22]: https://www.societyforscience.org/regeneron-sts/2022-finalists/
[F24]: https://www.societyforscience.org/regeneron-sts/2024-finalists/
[F25]: https://www.societyforscience.org/regeneron-sts/2025-finalists/
[F26]: https://www.societyforscience.org/regeneron-sts/2026-finalists/
[W21]: https://www.societyforscience.org/regeneron-sts/2021-sts-winners/
[W22]: https://www.societyforscience.org/regeneron-sts/2022-sts-winners/
[W23]: https://www.societyforscience.org/regeneron-sts/2023-sts-winners/
[W24]: https://www.societyforscience.org/regeneron-sts/2024-sts-winners/
[W25]: https://www.societyforscience.org/regeneron-sts/2025-sts-winners/
[W26]: https://www.societyforscience.org/regeneron-sts/2026-sts-winners/
[B20]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2020/Program-Books/Finalist.pdf
[B21]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2021/Program-Books/Finalist.pdf
[B22]: https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2022/Program-Books/Finalist.pdf
[KZ]: https://www.societyforscience.org/regeneron-sts/2023-student-finalists/kevin-zhu/
[SM]: https://www.smithsonianmag.com/innovation/this-high-schooler-developed-an-ai-tool-to-diagnose-autism-and-adhd-using-the-retina-180988694/
[S25]: https://www.societyforscience.org/regeneron-sts/2025-scholars/
[S26]: https://www.societyforscience.org/regeneron-sts/2026-scholars/
