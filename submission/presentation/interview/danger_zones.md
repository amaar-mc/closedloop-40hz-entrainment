# Danger Zones: v2 Condensed

These are the highest-risk questions for tomorrow.

The rule is simple: answer honestly, clinically, and without overclaiming.

---

## 1. "Is this already proven in live patients?"

Say:

"Not yet. What I have shown is that the predictive controller makes better decisions on real patient EEG in offline replay. The next step is live closed-loop validation, because in a live system the stimulation also changes the future brain state."

## 2. "Are you claiming this cures Alzheimer's?"

Say:

"No. I am not claiming a cure. I am working on the timing of a promising non-drug therapy. My contribution is making the delivery more adaptive and physiologically informed."

## 3. "Why should I trust a project with only 35 subjects?"

Say:

"Thirty-five is still a limitation, but it is a published human dataset, I split by subject so the test patients were truly unseen, and all 35 subjects improved under the predictive controller. The right next step is larger and multi-site validation."

## 4. "Why did you use PAC?"

Say:

"Because PAC reflects whether the 40 Hz response is actually organized with theta timing, not just present. It is a more physiologically meaningful biomarker of entrainment than raw gamma power alone."

## 5. "How do you know the model is not memorizing?"

Say:

"The dataset split is by subject, the forecasting model is causal, and I found that the broad spectral feature set hurt generalization. The model improved when I reduced it to the features that actually tracked response dynamics."

## 6. "Why is predicting 5 seconds ahead important?"

Say:

"Because reactive control is always late. At very short horizons, simple baselines work. At 5 seconds, they break down, and prediction becomes useful for proactive therapy timing."

## 7. "What is the weakest part of your project?"

Say:

"The main weakness is that the validation is offline replay, not live closed-loop control. The controller makes better decisions on real data, but we still need to test whether acting on those decisions improves outcomes in real time."

## 8. "What did you personally do?"

Say:

"I did the literature review, built the pipeline, tested the model approaches, made the feature reduction decision, designed the controller, and ran the validation. The key scientific decisions were mine."

## 9. "Why should Medicine and Physiology judges care about the computational part?"

Say:

"Because the computational part is only the tool. The physiological contribution is that I am trying to time therapy according to the patient's actual entrainment state instead of using a fixed schedule."

## 10. "What is the immediate next step?"

Say:

"A live crossover study where the same patients receive fixed and adaptive stimulation on different days, so we can test whether adaptive timing improves entrainment in real time."

---

## Three Phrases To Avoid

- "This proves it works clinically."
- "This cures Alzheimer's."
- "The AI figured it out."

## Three Better Phrases

- "The data shows improved decision quality on real EEG."
- "My contribution is adaptive therapy timing."
- "The next step is live validation."
