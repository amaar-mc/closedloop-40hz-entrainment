# Memorization Guide

**For: 01_main_script.md (the 4-5 minute version)**

You don't memorize words. You memorize a journey through your poster. The poster is your memory palace -- 9 rooms, left to right.

---

## THE 9 ROOMS

```
LEFT COLUMN (stand left, face judge):

  [1. GREETING]        "Hi, I'm Amaar. Walk you through it?"
  [2. WHY THIS EXISTS]  Grandmother → 40 Hz science → it works
  [3. THE GAP]          Fixed schedule is broken. Half habituate. Nobody predicting.

CENTER (step to middle, start pointing):

  [4. MEASURE + WALL]   PAC = the biomarker. 6 architectures, same ceiling. Data limit.
  [5. THE PIVOT]        Predict further, not better. TCN: 73 features, 20s back, causal.
  [6. KEY CHART]        At 5 seconds, only the TCN survives. +0.5 margin.

RIGHT COLUMN (step right, pointing at results):

  [7. PROOF]            82.6% targeting vs 51.7%. 92% of oracle.
  [8. EVERY PATIENT]    35/35. Fatigue makes it stronger. Four models.

STEP BACK:

  [9. HONESTY + OPEN]   Offline replay. 2ms. Next step: live. "Questions?"
```

---

## THE CHAIN (transitions between rooms)

Say these out loud 5 times. This is what makes the story flow.

```
1 → 2   "my grandmother had dementia... that's how I found 40 Hz"
2 → 3   "the science is real... but here's what bothered me"
3 → 4   "nobody was predicting ahead of time... so my first question was"
4 → 5   "that realization told me exactly where to go next"
5 → 6   "this figure is where the whole project comes together"
6 → 7   "I validated by replaying the controller on all 35 patients"
7 → 8   "35 out of 35... and the advantage grows with fatigue"
8 → 9   "I want to be upfront about the main constraint"
9 → end "would you like me to go deeper, or do you have questions?"
```

---

## EMOTIONAL ANCHORING

| Room               | Feeling               | Inner thought                                                           |
| ------------------ | --------------------- | ----------------------------------------------------------------------- |
| 1. GREETING        | Warm, open            | "I'm glad you're here."                                                 |
| 2. WHY THIS EXISTS | Personal, then wonder | "This is real to me. And the science blew my mind."                     |
| 3. THE GAP         | Frustration           | "How is nobody doing this? It's so obviously broken."                   |
| 4. MEASURE + WALL  | Surprise → insight    | "I expected one model to win. They all tied. That _was_ the discovery." |
| 5. THE PIVOT       | Breakthrough energy   | "This is where the project changed direction."                          |
| 6. KEY CHART       | Pride, conviction     | "This is my best figure. The intellectual heart."                       |
| 7. PROOF           | Let the data speak    | "The numbers back everything up."                                       |
| 8. EVERY PATIENT   | Quiet awe             | "35 out of 35. That's the one that gets people."                        |
| 9. HONESTY         | Maturity              | "I know what this doesn't prove yet. That's strength."                  |

---

## NUMBER CLUSTERS

Six groups. Practice each as a unit.

```
THE DATA:           35 patients, 7 channels, 250 Hz
THE WALL:           6 architectures, 1457 to 2M params, all R²=0.287
THE TCN:            73 features, 20 seconds back, 5 seconds ahead
THE HORIZON SWEEP:  1s = 0.81 trivial, 5s = baselines negative, TCN = 0.25 (+0.5 margin)
THE CONTROLLER:     Reactive 51.7% targeting, TCN 82.6%, 92% of oracle
THE UNIVERSALITY:   35/35 patients, +9% to +11.2% fatigue, g = 1.7-2.4
```

---

## QUICK PRACTICE PLAN (30 minutes total)

**Pass 1 -- Read aloud (8 min):** Read 01_main_script.md out loud once. Don't try to memorize. Just hear yourself say it.

**Pass 2 -- Rooms only (5 min):** Close the script. Walk through 9 rooms using only the 8-word anchors above. Try to expand each into 2-3 sentences. Peek at the script if you get stuck on a specific room, then close it again.

**Pass 3 -- Transitions only (3 min):** Close everything. Say just the 9 chain transitions. The goal: finishing one room automatically pulls you into the next.

**Pass 4 -- Full run, no script (5 min):** Stand up. Point at your poster (or a photo on your phone). Go start to finish. When you blank, find the room on the poster, recall the anchor, and keep going. Time yourself -- you should land between 4:00 and 5:00.

**Pass 5 -- Record and listen (8 min):** Record yourself on your phone. Listen back. The parts that sound robotic are where you're reciting instead of understanding. For those, go back to the emotional anchor and re-derive in your own words.

---

## RECOVERY PROTOCOL

You will blank. Here's how to recover invisibly:

1. **Breathe.** One normal breath.
2. **Look at the poster.** Which section are you near? That's your room.
3. **Say the anchor in your head.** "Six architectures, same ceiling."
4. **Use the chain to move forward.** "That realization told me where to go next."
5. **If truly lost:** Point to the next figure and say "Let me show you this." Figures restart the story visually.

---

## POCKET CARD (screenshot this for your phone)

```
GREETING  → Hi, walk you through it?
WHY       → Grandmother → 40 Hz → MIT 2016 → works in humans
GAP       → Fixed 40/20, half habituate, nobody predicting
WALL      → 6 arch, all 0.287, data ceiling → chose EEGNet 1457p
PIVOT     → Sequences not snapshots. TCN: 73f, 20s, causal, left-pad
KEY CHART → 1s=0.81, 5s baselines die, TCN=0.25, +0.5 margin
PROOF     → 35 real EEG, 82.6% vs 51.7%, g=4.47, 92% oracle
ALL 35    → 35/35 benefit, fatigue +9-11.2%, 4 models hold
HONEST    → Offline replay, 2ms, next=live+RL. "Questions?"
```
