# CSEF Judge Rubric & Q&A Deep Dive (vFinal)

Compiled from: ISEF Grand Award criteria, CSEF judging process documentation, judge guides, and Medicine & Physiology category analysis. Cross-referenced against existing Q&A bank — this document fills gaps and adds rubric context.

---

## Part 1: How CSEF Judging Actually Works

**CSEF does NOT use a numerical rubric.** There is no scoresheet. Final winners are selected by overwhelming agreement of the entire panel of Category Judges after a caucus where they discuss and debate each project. This has a direct implication for strategy: you are not optimizing for a checklist — you are making judges want to vote for you.

**The process:**

1. Judges read your Project Presentation PDF _before_ the interview — they come prepared and already have opinions
2. You are assigned a window; judges come to your booth
3. Interview: ~8–12 minutes at CSEF (more immersive than regional fairs)
4. After all interviews, judges caucus and debate
5. The student who is most convincingly remembered wins

**Who are CSEF Medicine & Physiology judges?** They must have a PhD or MD and/or 6+ years of professional experience in a related field. For M&P specifically, expect:

- Neuroscientists (cognitive, systems, or computational)
- Neurologists or psychiatrists with research backgrounds
- Biomedical engineers specializing in neural interfaces
- Clinical researchers doing Alzheimer's or neurodegeneration trials
- Physiologists who study oscillatory neural dynamics

**What this means for you:** They know what EEG is. They know what theta and gamma are. They know what PAC is and probably have opinions about it. They will NOT give you credit for defining basic terms. They will go straight to the hard science.

---

## Part 2: ISEF Grand Award Criteria (What Informs CSEF Scoring)

CSEF is an ISEF-affiliated fair. While CSEF judges use consensus not a rubric, they are trained on ISEF criteria. These are the five dimensions they carry in their heads:

| Dimension                                      | Points  | What it really asks                                           |
| ---------------------------------------------- | ------- | ------------------------------------------------------------- |
| I. Research Question                           | 10      | Did you ask something that matters and can be tested?         |
| II. Design & Methodology                       | 15      | Did you build a system that can actually answer the question? |
| III. Execution: Data, Analysis, Interpretation | 20      | Did you do the science correctly and honestly?                |
| IV. Creativity & Potential Impact              | 20      | Is this novel? Does it matter?                                |
| V. Presentation                                | 35      | Can you communicate it? Do you really understand it?          |
| **Total**                                      | **100** |                                                               |

**The interview (part of Presentation) is worth 25 of the 35 Presentation points — the single largest scorable block in the entire rubric.**

Specific interview sub-criteria judges evaluate:

- Clear understanding of basic science relevant to the project
- Understanding of the interpretation and limitations of results
- Degree of independence in conducting the project
- Recognition of potential impact in science/society/economics
- Quality of ideas for further research

---

## Part 3: Dimension-by-Dimension Analysis for This Project

### Dimension I — Research Question (10 pts)

**Your score driver:** The question is specific, testable, and justified by a demonstrated gap. "Can a causal temporal model predict PAC 5 seconds ahead well enough to outperform reactive and fixed-schedule controllers?" is not vague.

**What judges want to hear:**

- Why this question and not others
- What gap in the literature it fills
- Why 5 seconds specifically (you have the horizon sweep)

**Predicted questions — escalating:**

_Basic:_

> "What is your research question?"

_Intermediate:_

> "Why 5 seconds? Why not 1 second or 10 seconds?"

Answer: At 1–2 seconds, simple persistence baselines win — the brain barely changes. At 5 seconds, those baselines collapse to negative R². 5 seconds is also the minimum lead time a controller needs to actually change stimulation state and have it take effect before entrainment drops. It's where prediction becomes operationally necessary.

_Hard:_

> "Has anyone studied closed-loop 40 Hz entrainment control before? What makes your framing of the problem different?"

Answer: Existing closed-loop BCI work focuses on reactive thresholding — stimulate when a biomarker drops below a cutoff. No published work I found applies predictive temporal modeling to 40 Hz entrainment timing specifically. The novelty is (1) using a forecasting model instead of a reactive threshold, (2) grounding the choice of biomarker in the habituation literature, and (3) evaluating across the full prediction horizon to demonstrate WHERE the forecasting model adds value.

---

### Dimension II — Design & Methodology (15 pts)

**Your score driver:** Two-stage architecture with a clear justification for each design decision. The causal constraint is architectural. Subject-level splits. Competing baselines.

**What judges want to hear:**

- Why each design choice was made
- What controls were used
- What could go wrong and how you protected against it

**Predicted questions — escalating:**

_Basic:_

> "Walk me through your experimental design."

_Intermediate:_

> "Why subject-level splits? What would have happened with random splits?"

Answer: Random splits would mix data from the same patient across train and test. Since the model learns individual PAC dynamics, it would effectively memorize patients and inflate R². Subject-level splits ensure that the 6 test subjects are completely unknown to the model — no brain it has seen before. This is standard in EEG machine learning and was the only way to make a valid generalization claim.

_Hard:_

> "You compare against four controllers. Why those four? What controls against the possibility that any adaptive system beats fixed — i.e., that your result is about adaptiveness, not prediction?"

Answer: The reactive controller is already adaptive — it responds to current PAC levels. The PI controller is also adaptive with feedback dynamics. My predictive controller's advantage over reactive shows that PREDICTION specifically adds value beyond reactivity. If it only beat the fixed schedule, you'd be right that it proves adaptiveness, not forecasting. Beating reactive with statistical significance (g = 4.47) isolates the contribution of forecasting.

_Expert-level:_

> "Did you consider doing a prospective power calculation before deciding on 35 subjects?"

Answer: The sample size was determined by what's publicly available — ds005048 is the largest accessible dataset with this exact protocol. Post-hoc: with n=35, Hedges' g = 4.47 for targeting, a power analysis shows well over 99% power at α=0.001, so the study was adequately powered for the effect size observed. For future work, a crossover study would require a prospective power calculation based on expected effect size from this data.

---

### Dimension III — Execution: Data, Analysis, Interpretation (20 pts)

**Your score driver:** This is the highest-scrutiny dimension for a medicine/physiology judge. They will go deep here. The key answers: Wilcoxon rationale, Hedges' g vs Cohen's d, PAC computation method, leakage prevention, the spectral feature ablation discovery.

**What judges want to hear:**

- Appropriate statistical choices with justification
- Honest reporting of what didn't work
- That you know the difference between a result and a claim

**Predicted questions — escalating:**

_Basic:_

> "What statistical tests did you use?"

_Intermediate:_

> "Why Wilcoxon signed-rank? What are the assumptions of that test?"

Answer: Wilcoxon signed-rank is a non-parametric paired test. It ranks the magnitude of differences between paired observations rather than assuming the differences are normally distributed. With n=35, I can't confidently invoke the central limit theorem for the differences, so Wilcoxon makes fewer distributional assumptions. It's the appropriate test for paired before-after comparisons with small samples. If I had used a t-test here, a statistician would rightly ask whether the normality assumption was checked.

_Hard:_

> "Your R² of 0.606 is on a smoothed target. What does that mean for how we should interpret the model's clinical usefulness?"

Answer: Critical point. The target is a 5-window causal moving average — a smoothed PAC state, not instantaneous raw PAC. The model predicts the near-future trend, not an exact point value. This is intentional: the controller needs to know whether PAC is trending toward low, not the exact value at t+5s. The clinical translation is: when my model says PAC will be low in 5 seconds, the controller triggers stimulation. That decision is binary — stimulate or not — so smoothing to get directional signal is appropriate. If the target were raw PAC (which I also tested), R² drops to near zero because raw PAC is too noisy to predict precisely.

_Expert-level:_

> "How did you validate that phase-amplitude coupling computed with Tort's Modulation Index is actually measuring entrainment and not noise? What alternative PAC metrics did you consider?"

Answer: Three checks. First, PAC is significantly higher during stimulation epochs than rest epochs across the dataset, which is the expected signal if it's measuring entrainment (PAC should be higher when 40 Hz stimulus is present). Second, the temporal model can predict future PAC with R²=0.606 — if PAC were pure noise, no temporal model would find structure. Third, I considered Canolty's mean vector length and Phase-Locking Value as alternative metrics. Tort's MI is the most established in the Alzheimer's entrainment literature specifically (cited by Iaccarino and follow-up work), so it's the appropriate choice for comparability.

_Expert-level (statistics deep dive):_

> "What is Hedges' g, and why does it differ from Cohen's d in your case?"

Answer: Cohen's d is the standardized mean difference — the difference in means divided by the pooled standard deviation. Hedges' g applies a small-sample correction factor (proportional to 1 - 3/(4n-5)), which reduces the effect size estimate. With large N, Cohen's d and Hedges' g are nearly identical. With n=35, the correction matters — Cohen's d would slightly overstate the effect. I used Hedges' g throughout to be conservative and because it's the recommended choice when sample sizes are under 50.

---

### Dimension IV — Creativity & Potential Impact (20 pts)

**Your score driver:** Judges want to see that you made non-obvious design decisions and that the result actually matters to someone. The feature ablation discovery is your creativity story. The Muse 2 deployment is your impact story.

**What judges want to hear:**

- What was novel in your approach (not what exists in the field)
- What surprised you (and showed independent scientific thinking)
- Who benefits and how specifically

**Predicted questions — escalating:**

_Basic:_

> "What's new about what you did?"

_Intermediate:_

> "The idea of closed-loop stimulation exists in BCI research. What specifically is your contribution?"

Answer: Three contributions. First, applying predictive temporal modeling specifically to 40 Hz entrainment — closed-loop BCI mostly uses reactive thresholding. Second, the horizon sweep methodology: rather than picking one prediction horizon and reporting it, I evaluated the model across all horizons from 1–10 seconds and showed empirically where forecasting adds value over baselines. That's a methodological contribution. Third, systematically proving the static prediction ceiling through an architecture marathon, then using that finding to justify the pivot to temporal modeling. The science of the failure was as important as the success.

_Hard (creativity focus):_

> "Tell me about something you discovered unexpectedly."

Answer: The spectral feature ablation. My original model used 73 features including 61 spectral power features. Test R² was essentially zero despite good validation performance. When I traced the val-test gap, I found the spectral features were encoding patient-specific skull conductivity and electrode impedance — essentially memorizing individual anatomy, not learning coupling dynamics. Dropping them and keeping only 12 PAC-trajectory features raised test R² from -0.025 to 0.606. I hadn't expected that spatial EEG features would be the enemy of generalization for this task. That was a genuine scientific discovery, not something I read in a paper.

_Hard (impact focus):_

> "Who is this for? Be specific. What would it change in a memory care setting?"

Answer: The immediate patient is someone receiving 40 Hz auditory entrainment as part of a clinical trial or early-access protocol. Currently, every patient gets 40 minutes of fixed cycling. My system would adapt that schedule to their real-time neural response — patients who habituate get more breaks and restimulation at recovery, patients who facilitate get sustained stimulation. On a practical level, this potentially means less wasted stimulation time, shorter effective treatment windows, and better matching of stimulus to neural state. At $300 total hardware cost (Muse 2 + standard headphones), it's accessible for memory care facilities or home use without clinical-grade EEG.

---

### Dimension V — Presentation (35 pts)

**Poster: 10 pts** — logical organization, clear graphics, information density
**Interview: 25 pts** — understanding, limitations, independence, next steps

The interview accounts for 71% of your Presentation score. Notes for M&P judges specifically:

- They care about mechanistic explanation over method details
- They will test whether you understand the physiology, not just the model
- They value intellectual honesty about limitations over polished confidence
- They reward curiosity and forward thinking over comprehensive recitation

---

## Part 4: Medicine & Physiology Specific Hard Questions

These are questions that a working neuroscientist or neurologist would ask — not covered or only partially covered in the existing Q&A bank.

---

**"PAC as a biomarker for 40 Hz entrainment — isn't that somewhat circular? You're using a frequency-specific coupling measure to assess a frequency-specific stimulus."**

Answer: That's a fair challenge. The reason PAC is non-circular is the specificity of phase coupling. Raw 40 Hz gamma power would be circular — you're delivering 40 Hz and measuring 40 Hz. But PAC measures whether that gamma amplitude is organized around the _phase_ of theta oscillations at 4–8 Hz, which is a distinct, independently generated rhythm. High PAC means the gamma is not just present — it's rhythmically modulated by the background theta cycle in a way that reflects actual thalamo-cortical network engagement. Low gamma power with high PAC would mean the network is entrained but weak. High gamma power with low PAC would mean broadband noise. PAC separates those cases; raw power doesn't.

---

**"Theta phase coupling with gamma amplitude is a well-established phenomenon in hippocampal memory consolidation. Why do you expect it to be a valid marker in _frontal_ channels for _auditory_ stimulation?"**

Answer: That's a nuanced distinction. Frontal theta-gamma coupling is less studied than hippocampal, but it's been observed in working memory tasks and attentional states. In the context of 40 Hz auditory stimulation, the Lahijanian 2024 paper specifically showed that auditory 40 Hz entrainment enhances default mode network connectivity including prefrontal regions, and that PAC computed at frontal channels distinguishes stimulation from rest epochs in the same dataset I'm using. So the evidence base for frontal PAC as a marker in this specific protocol exists, even if the mechanistic story is less established than hippocampal coupling. I'm also agnostic about the underlying mechanism — I'm using PAC because it empirically distinguishes stimulation quality in this dataset, not because I have a complete mechanistic account.

---

**"How do you know your habituation finding is real habituation (neurological) and not just signal drift, electrode impedance changes, or fatigue artifacts?"**

Answer: I can't fully rule out artifact contributions with the current dataset, and I should be honest about that. What I can say: the dataset was preprocessed by Makoto's pipeline including ICA artifact removal and common average reference, which reduces electrode impedance drift effects. The split is approximately 50/50 between habituators and facilitators — if it were pure signal drift from electrode impedance, you'd expect a consistent directional effect, not a bimodal split. The variability in direction and magnitude is more consistent with genuine neurobiological heterogeneity. But confirming that this is true habituation (as in Thompson & Spencer, acquired modification of a neural response) would require a more controlled experimental design, which is a real limitation of working with a retrospective dataset.

---

**"In the context of Alzheimer's disease pathophysiology, why would 40 Hz gamma entrainment be therapeutic? What is the proposed mechanism?"**

Answer: The leading hypothesis is glymphatic clearance. Iaccarino 2016 showed that 40 Hz photic stimulation reduced amyloid plaques and tau phosphorylation in mouse models by ~40–50%, accompanied by increased microglial activity and reduced APP cleavage. Murdock 2024 linked this to glymphatic clearance — the brain's waste-clearance system, which is primarily active during slow-wave sleep, may also be activated by synchronized 40 Hz oscillations. The idea is that gamma synchronization entrains inhibitory interneuron networks, which modulate astrocyte calcium dynamics and perivascular space dilation, driving interstitial fluid flow and amyloid clearance. Chan 2025 showed long-term safety in human trials, with trends toward reduced ventricular enlargement. The exact mechanism is still being characterized, but the animal evidence is strong enough to justify clinical trials.

---

**"Your validation is offline replay. Can you explain specifically what that means, what it can and cannot tell you, and what assumptions you're making?"**

Answer: Offline replay means I take the recorded EEG from a session where fixed stimulation was delivered, run my controller's logic on that recording, and measure what decisions it would have made. What it tells you: whether the model's predictions are correct and whether its decision logic would have targeted low-PAC windows better than the alternatives. What it cannot tell you: how the brain would have responded to those different stimulation decisions. In a live system, stimulation changes the future brain state — so the EEG at time t+5 might be different depending on whether you stimulated or not. Offline replay treats the brain state as fixed regardless of the controller's decisions. This means the performance numbers are optimistic for a scenario where adaptive stimulation improves entrainment, and possibly pessimistic for a scenario where over-stimulation causes fatigue. Offline replay is the standard initial validation in BCI research precisely because it lets you evaluate decision logic without confounding from real-time neurofeedback. The next step is live crossover validation.

---

**"Your project uses a publicly available dataset. Walk me through your IRB considerations and the ethical framework for using this patient data."**

Answer: The dataset was collected under IRB approval at the originating institution (Lahijanian et al. 2024 at their facility) and published with patient consent for research use on OpenNeuro, which is a federally supported data-sharing platform with its own data use policies. Using a publicly shared, de-identified dataset for secondary analysis does not require separate IRB approval — this is standard practice in neuroscience research. At CSEF, my forms document the use of secondary human data. I did not collect any data from human subjects myself. The original consent covered research use, which includes my analysis. This is the same framework used in any computational study that reanalyzes a published EEG dataset.

---

**"If you had to identify the single weakest link in your scientific chain — the step where you're least confident — what would it be?"**

Answer: The PAC computation at the epoch-to-window assignment step. PAC is computed over full 20–40 second epochs, then assigned uniformly to all 2-second windows within that epoch. That means windows from the same epoch share the same label — they're not independent. This could slightly inflate my model's apparent performance if the model learns epoch identity rather than within-epoch dynamics. I've partially mitigated this by using the TCN's temporal context (20 steps of history), which should capture genuine dynamics rather than epoch labels, but I can't rule this out entirely without per-window PAC estimates, which require more sophisticated methods (like wavelet-based instantaneous PAC).

---

## Part 5: Escalating Probe Map — How Deep Will They Go?

This is the pattern based on judge training documents and ISEF guidance. A judge starts basic and escalates until they hit a ceiling. Your goal is to push that ceiling as high as possible.

```
Level 1 — Basic check (30 seconds per question)
"What is your project?" / "What is PAC?" / "What were your results?"

Level 2 — Method check (1-2 min per question)
"How did you compute PAC?" / "Why this architecture?" / "What statistics?"

Level 3 — Scientific reasoning (2-3 min per question)
"Why does the 5-second horizon matter?" / "What does the spectral feature discovery mean?"
"Walk me through how you diagnosed the val-test gap."

Level 4 — Domain expertise test (2-3 min per question — M&P specific)
"Why is PAC the right biomarker vs raw gamma?" / "What's the theta-gamma coupling mechanism?"
"What does Murdock 2024 say about glymphatic clearance?"

Level 5 — Challenge questions (3-5 min — the most important ones)
"Is offline replay sufficient?" / "Isn't this circular?" / "What's the weakest link?"
"If I were a neurologist considering this — what would I still need to know?"
```

If you answer Level 4 fluently, you are in the top 5% of presenters. If you can answer Level 5 honestly and with depth, you win the room.

---

## Part 6: What M&P Judges Specifically Reward vs Penalize

### They Reward:

- Literature citations by name and year — they check
- Mechanistic thinking ("why" not just "what")
- Statistical humility — acknowledging what your test can and can't prove
- Self-directed discovery — the spectral ablation story is gold here
- Honest discussion of limitations without prompting
- Connecting your work to clinical practice with appropriate caveats
- Saying "I don't know, but here's my thinking" when genuinely uncertain

### They Penalize:

- Overselling: "This will cure Alzheimer's" ends your chances
- Vague statistics: "the results were significant" without context
- Being unable to go deeper on neurophysiology after claiming it's your biomarker
- Pointing to the poster when asked a direct question ("it's on there")
- Pausing after a question and saying "let me check my notes" for basic facts
- Not knowing your citations (if you say Iaccarino 2016 and they ask what journal, know: _Nature_)
- Treating ML architecture as your main contribution to an M&P judge

---

## Part 7: Citation Quick Reference (Say These Without Hesitating)

These are the citations in your script. Know them cold.

| Citation                | What it showed                                                                 | Journal                      |
| ----------------------- | ------------------------------------------------------------------------------ | ---------------------------- |
| Iaccarino 2016          | 40 Hz photic → 40-50% amyloid reduction, microglial activation (mice)          | _Nature_                     |
| Martorell 2019          | Multi-sensory 40 Hz (audio+visual) → greater plaque reduction                  | _Cell_                       |
| Murdock 2024            | Glymphatic clearance mechanism for 40 Hz entrainment                           | _Nature_                     |
| Chan 2025               | Long-term safety in human trials, trend toward reduced ventricular enlargement | _(confirm journal)_          |
| Lahijanian 2024         | Auditory 40 Hz in 35 elderly patients, enhances DMN connectivity; your dataset | OpenNeuro ds005048           |
| Thompson & Spencer 1966 | Habituation: neural response decreases with repeated stimulation               | _Psychological Review_       |
| Tort 2010               | Modulation Index for PAC computation using KL divergence                       | _Journal of Neurophysiology_ |

---

## Part 8: Gaps in the Existing Q&A Bank (New Answers to Add)

The existing `v2_qa_complete.md` is thorough on ML/engineering questions. These are gaps specific to M&P judges:

1. ✅ Covered in Part 4: PAC circularity challenge
2. ✅ Covered in Part 4: Frontal vs hippocampal theta-gamma coupling
3. ✅ Covered in Part 4: Habituation vs artifact
4. ✅ Covered in Part 4: Mechanistic explanation of 40 Hz therapy
5. ✅ Covered in Part 4: Offline replay full explanation
6. ✅ Covered in Part 4: IRB and ethics for secondary data
7. ✅ Covered in Part 4: Weakest link — epoch-to-window PAC assignment

**One additional gap not elsewhere addressed:**

> "What would a power analysis for your study look like, and is n=35 sufficient?"

With Hedges' g = 1.31 for alignment and 4.47 for targeting, a post-hoc power analysis at α=0.001 and β=0.80:

- For g=1.31: required n ≈ 14 subjects. We have 35. Well-powered.
- For g=4.47: required n ≈ 4 subjects. We have 35. Massively over-powered for this effect.

This doesn't mean n=35 is large in absolute terms — it means the effects are large enough to detect even with small samples. For future multi-site generalization, you'd need substantially more subjects, especially to characterize subgroups (habituators vs facilitators) across demographics.

---

## Closing Note

The judges in Medicine & Physiology are clinicians and researchers who have spent careers on problems like this. They are not trying to trick you — they want to find students who think scientifically. The most impressive thing you can do is acknowledge a real limitation, explain why it exists, and describe how you would address it. That is what scientists do.

Your weakest answers in the room will be on pure neurophysiology mechanism — not because you don't know it, but because it's hard to anticipate every mechanistic probe. The right approach: go deep on what you studied, and when you hit the edge of your knowledge, name it explicitly and say what you would need to go further.
