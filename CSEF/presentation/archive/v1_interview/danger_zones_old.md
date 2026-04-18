# Danger Zones: Questions That Could Sink Your Project

These are the 12 questions where a wrong answer does real damage. For each: why it's dangerous, what not to say, the honest answer, and how to pivot to strength.

---

## 1. "Are you simulating the brain's response to stimulation?"

**Why dangerous:** A Synopsys judge asked this and it exposed a gap. The honest answer is nuanced -- you simulate controller decisions on real brain data, but you do NOT simulate how the brain would respond to those decisions.

**Do NOT say:** "Yes, I simulate the full brain response." (That's false and you'll get caught.)

**Say this:** No, and that's an important distinction. The controller makes decisions on real brain recordings -- real EEG from 35 patients. But those recordings are fixed. When my controller decides to stimulate, I can evaluate whether that was the right call by looking at what the brain actually did, but I can't observe what would have happened differently if we'd stimulated at that moment. The brain data doesn't change based on the controller's output. That feedback loop is exactly what a live clinical validation would test. My system architecture diagram shows where that loop closes in a real-time deployment.

**Pivot:** The offline validation still proves the controller makes better decisions than reactive control on real brain data. The question isn't whether the decisions are good -- they demonstrably are, on all 35 patients. The question is whether acting on those decisions changes outcomes. That's the next experiment.

---

## 2. "This is just offline replay. Why should I believe this works on real patients?"

**Why dangerous:** This challenges the entire clinical relevance of the project.

**Do NOT say:** "It definitely works on real patients." (You haven't tested that.)

**Say this:** You shouldn't -- yet. And I'm careful about that distinction. What I've shown is that the predictive controller makes significantly better decisions than reactive control when evaluated on real brain data from 35 patients. The decisions are better. Whether those better decisions translate to better clinical outcomes requires a crossover study -- same patients receiving both fixed and adaptive stimulation on different days. The model runs in under 50 milliseconds, the hardware costs $200, and the controller is designed for real-time deployment. The technology is ready. The clinical validation is the next step.

**Pivot:** This is actually how modern medical device development works. Closed-loop DBS for Parkinson's went through exactly this path -- offline optimization first, then clinical validation. FDA approved that in February 2025.

---

## 3. "The spectral feature drop isn't in your project presentation. When did you do this?"

**Why dangerous:** Judges pre-read the 13-page presentation. If the biggest result isn't there, they'll wonder about timing and whether the work is really yours.

**Do NOT say:** "Oh, I forgot to include it." (Sounds careless.)

**Say this:** I did that work after submitting the project presentation. The presentation was locked in early March, and I discovered the spectral feature issue in late March during deeper ablation studies. I noticed the validation R-squared was 0.33 but test was negative 0.03 -- a 0.358 gap. I traced the problem to the 61 spectral features encoding subject-specific brain anatomy rather than dynamics that transfer across patients. When I dropped them and kept 12 PAC-trajectory features, test R-squared jumped to 0.60 and the gap shrank to 0.246. The finding is on the poster because I updated the display after the presentation deadline.

**Pivot:** This is actually one of the most scientifically interesting findings. Ten different architectures all converge to R-squared 0.61-0.65 on those 12 features. It's not a model result -- it's a data representation result.

---

## 4. "Did AI write your code? Your presentation? Your poster?"

**Why dangerous:** AI usage is heavily scrutinized. Getting this wrong can mean disqualification.

**Do NOT say:** "I didn't use AI at all." (Dishonest, and they can tell.) Also don't say: "AI did the heavy lifting." (Undermines your contribution.)

**Say this:** I used Claude and ChatGPT during development as coding assistants -- for debugging, generating boilerplate, and exploring implementation options. All of that is documented in my Assistance Disclosure Form per ISEF rules. But the intellectual contributions were mine: identifying the research gap, designing the feature ablation study, discovering the 12-feature representation, designing the controller, choosing the statistical methods, and interpreting the results. AI didn't design the experiment or interpret the data. The most important decisions -- recognizing the 0.287 ceiling, pivoting to temporal prediction, understanding why spectral features fail -- came from me sitting with the data and thinking through what it was telling me.

**Pivot:** The 8-architecture convergence that led to the whole pivot -- no AI suggested that. I ran those experiments, saw the pattern, and drew the conclusion myself.

---

## 5. "Your dataset is from one clinic. How does any of this generalize?"

**Why dangerous:** Single-site data is a legitimate weakness. The dataset is from Iran (Lahijanian et al.), which adds a cultural/demographic dimension.

**Do NOT say:** "It generalizes because the biology is universal." (Too hand-wavy.)

**Say this:** It's a real limitation, and I'm transparent about it. Single-site data means recording conditions, equipment, electrode placement, and patient demographics are all fixed. My model could be learning site-specific artifacts. Two things give me some confidence: first, the 6 test subjects are genuinely new to the model -- not the same patients on a different day. Second, the 12 features I selected are biologically motivated and invariant to recording setup. They capture the shape of PAC over time, not absolute power levels. The spectral features I explicitly removed were the ones encoding site-specific characteristics. But the definitive test is multi-site replication, and I list that as the top priority for future work.

**Pivot:** This is exactly why the feature discovery matters. The spectral features were the site-specific ones. Removing them was a step toward generalization, even if it doesn't guarantee it.

---

## 6. "R-squared of 0.60 -- that's 40% unexplained. Is that good enough for medicine?"

**Why dangerous:** Medical judges hold higher standards for clinical tools. 60% might sound mediocre.

**Do NOT say:** "0.60 is really good for this kind of data." (Sounds defensive.)

**Say this:** In isolation, no -- 0.60 isn't enough to make clinical decisions. But the question isn't whether the predictions are perfect. It's whether they're good enough to improve controller decisions compared to the alternative. And the answer is clearly yes. The controller built on these predictions achieved 72% alignment versus 64% for reactive, with Hedges' g of 1.31 -- a large effect. The low-PAC targeting went from 52% to 83%. And at the 5-second horizon, every baseline method gives negative R-squared -- literally worse than guessing the average. So 0.60 isn't perfect, but it's the only method that gives useful predictions at the horizon where proactive control is possible.

**Pivot:** The TCN's targeting reaches 91% of the theoretical oracle -- a system with perfect future knowledge. The remaining gap is more about the 5-second prediction horizon than prediction accuracy.

---

## 7. "What if Cognito's Phase 3 fails and 40Hz just doesn't work?"

**Why dangerous:** If the therapeutic foundation collapses, your project looks pointless.

**Do NOT say:** "It definitely works." (You don't know that yet.) Also don't panic.

**Say this:** That's a real possibility, and I've thought about it. Even if 40 hertz specifically doesn't pan out, the closed-loop control framework generalizes. The approach -- use a biomarker to forecast neural state and time interventions proactively -- applies to any brain stimulation where the response is variable and predictable. Closed-loop DBS for Parkinson's uses the same principle with beta power instead of PAC. If 40 hertz doesn't work, the controller architecture transfers to other frequencies, other modalities, or other conditions. The methodology isn't tied to one therapy.

**Pivot:** And honestly, the data from the last two years is encouraging. The Murdock mechanism paper, Chan's 2-year safety data, the FDA Breakthrough Device Designation -- the field is moving toward validation, not away from it.

---

## 8. "You're a high school student working alone. How do I know you understand the neuroscience?"

**Why dangerous:** They're testing whether you're a "snow job" -- impressive display but shallow understanding. The handbook explicitly warns judges to watch for this.

**Do NOT say:** Anything defensive. Don't name-drop or inflate.

**Say this:** Ask me anything. [Then answer whatever they ask.] The best way I can demonstrate understanding is through this conversation. I can explain PAC computation at the mathematical level -- Tort's Modulation Index uses KL divergence across 18 phase bins. I can explain why I chose Hedges' g over Cohen's d for N=35. I can tell you why spectral features encode individual brain anatomy and PAC features don't. I can explain the aquaporin-4 pathway in Murdock's glymphatic clearance mechanism. If there's something I don't know, I'll tell you -- but I've spent four months deeply immersed in this.

**Pivot:** The proof is in the work. I tested eight architectures, identified a data ceiling, pivoted my entire approach, discovered that 61 features were harmful, and validated across 5 seeds and 35 patients. That's not following a tutorial. That's iterating on a research problem.

---

## 9. "Why should I trust computational results over an actual clinical trial?"

**Why dangerous:** Medical judges may view computational work as "lesser" than clinical evidence.

**Do NOT say:** "Computational results are just as good." (They're not, and doctors know it.)

**Say this:** You shouldn't trust them equally -- clinical trials are the gold standard. What computational validation does is establish proof of concept and justify the investment of a clinical trial. I've shown that predictive control makes better decisions than reactive control on real brain data. That's enough to design a crossover study with a clear hypothesis: adaptive stimulation maintains better theta-gamma coupling with less total stimulation than fixed schedules. The in-silico step saves time and money. The FDA is actually moving in this direction -- they announced in April 2025 that they're phasing out mandatory animal testing for many drugs in favor of computational methods. Computational validation before clinical validation is becoming standard, not a shortcut.

**Pivot:** The system costs $200 and runs on a laptop. The barrier to a clinical pilot isn't cost or technology -- it's IRB approval and clinical partnerships.

---

## 10. "Your EEGNet only gets R-squared 0.287. That's terrible. Why trust the TCN?"

**Why dangerous:** If the first stage is weak, the whole pipeline seems questionable.

**Do NOT say:** "0.287 is actually fine." (It sounds bad and defending it looks worse.)

**Say this:** You're right that 0.287 is a low ceiling, and that's actually one of the most important findings. I proved it's a ceiling by testing 8 architectures up to 1.1 million parameters -- they all land there. That told me a 2-second snapshot doesn't contain enough information about epoch-level PAC. But the TCN doesn't depend on EEGNet's accuracy in the way you might think. In the controller validation, I fed the TCN ground-truth PAC labels, not EEGNet estimates, specifically to isolate the forecaster's contribution. The question was: given accurate PAC measurements, can the TCN predict where PAC is going? The answer is yes, with R-squared 0.60. EEGNet's ceiling affects the real-time deployment pipeline but not the forecasting validation.

**Pivot:** In a clinical system, you could use clinical-grade PAC computation instead of EEGNet -- the TCN's performance is independent of the estimation method.

---

## 11. "Only 6 test subjects. You can't conclude anything from that."

**Why dangerous:** Small test sets are a legitimate statistical concern, especially for medical judges.

**Do NOT say:** "6 is enough." (It sounds naive.)

**Say this:** Six held-out subjects is small, and I'm transparent about it. That's why I also report results on all 35 subjects -- including training and validation -- and show the advantage is consistent across all three splits. The per-subject scatter plot shows no systematic difference between train, val, and test subjects. If the model were overfitting to training subjects, you'd see the training dots clustered above the diagonal and test dots below. Instead, they're interleaved. But yes, a larger multi-site dataset is a clear next step, and I list it as a limitation.

**Pivot:** 35/35 subjects benefiting -- including those 6 test subjects -- has a binomial probability of less than 0.001 by chance. The effect is consistent, even if the test set is small.

---

## 12. "You're talking about productizing a $200 device for Alzheimer's patients. Isn't that irresponsible without clinical evidence?"

**Why dangerous:** Medical judges may see premature commercialization talk as reckless.

**Do NOT say:** "We should get this to patients as fast as possible." (Sounds like you'd skip safety steps.)

**Say this:** I wouldn't sell this to patients tomorrow -- that would be irresponsible. When I talk about the $200 system, I'm describing the cost structure that makes clinical research accessible. Most neurostimulation research requires $50,000+ equipment. A Muse 2 headset and headphones means an IRB-approved pilot study could run at a memory care facility without a capital grant. The path is: observational pilot first, where I collect real-time data during supervised sessions. Then a small feasibility study comparing adaptive versus fixed. Then, if the data supports it, a regulatory submission. The product framing isn't about skipping steps -- it's about showing this can eventually reach the 55 million people who need it, not stay locked in a research lab.

**Pivot:** Cognito spent $105 million to get to Phase 3 with a proprietary device. The intelligence layer I built is device-agnostic and could integrate with their system or any other. That's the real commercial angle -- not selling headsets, but providing the adaptive control that every protocol is missing.
