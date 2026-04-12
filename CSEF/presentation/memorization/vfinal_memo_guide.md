# Final Memorization Guide (vFinal)

Companion to `vfinal_mindmap.md`. Script is `scripts/vfinal_script.md`.

---

## The Core Principle

You are not memorizing a speech. You are memorizing a **story with 9 beats** and a set of **anchor numbers** inside each beat. If you memorize word-for-word, you will freeze when interrupted. If you memorize the beats and the numbers, the words come out naturally and you can resume from any point.

---

## Step 1: The 9-Beat Spine

Memorize this first. Say it out loud until you can do it in under 40 seconds.

| # | Beat | Spine anchor |
|---|---|---|
| 1 | **HOOK** | 55 million. 40 Hz. MIT 2016. Mechanism is real. |
| 2 | **GAP** | Fixed schedule. Half habituate. 35 patients. Dataset. |
| 3 | **BIOMARKER** | PAC. Gamma locks to theta. The only number that matters. |
| 4 | **CEILING** | 8 architectures. All 0.287. Data ceiling, not model. |
| 5 | **PIVOT** | New question. TCN. 20s in, 5s out. Causal by design. |
| 6 | **DISCOVERY** | 73 to 12 features. −0.025 to 0.606. Signal was in dynamics. |
| 7 | **HORIZON** | 1s: persistence wins. 5s: baselines collapse. TCN holds. |
| 8 | **RESULTS** | 82% vs 52%. 72% vs 64%. g=4.47. 35/35. 91% oracle. |
| 9 | **PRODUCT** | Muse 2. $249. Under $300. <50ms. Crossover next. |

Drill: Say the spine 5 times in a row. Then once with eyes closed. Then once pointing at each poster region as you say it.

---

## Step 2: The Story Logic

Each beat has one core logic. If you know the logic, the words are automatic.

### Beat 1 — HOOK
**Logic:** Disease is massive. Mechanism is scientifically real — not hype.
**Flow:** Scale → therapy type → Iaccarino 2016 → amyloid result → Murdock 2024 → Chan 2025 → "The mechanism is real."

### Beat 2 — GAP
**Logic:** The therapy exists, but the delivery is primitive. Fixed for everyone. That's the flaw.
**Flow:** Fixed schedule → patient heterogeneity → habituation (Thompson & Spencer 1966) → dataset

### Beat 3 — BIOMARKER
**Logic:** Before the system, ground the judge in the one signal everything tracks.
**Flow:** Name PAC → define it (gamma amplitude locked to theta phase) → what high PAC means → what low PAC means → "this is the only number that matters"

### Beat 4 — CEILING
**Logic:** I tried the obvious approach first. It failed — but the failure was informative.
**Flow:** Stage 1 goal → 8 architectures → all 0.287 → million-param model slightly worse → diagnose: data ceiling, not model ceiling → 2s window can't see epoch-level coupling

### Beat 5 — PIVOT
**Logic:** Changed the question. Architectural solution to the leakage problem.
**Flow:** "So I changed the question" → predict future PAC from sequence → Causal TCN → 20s history, 5s ahead → causal constraint is architectural (left-only padding)

### Beat 6 — DISCOVERY
**Logic:** Unexpected finding. Spectral features were memorizing patients, not learning coupling.
**Flow:** Original 73 features → test R² near zero → val-test gap investigation → spectral = skull conductivity + impedance → model memorized anatomy → dropped to 12 PAC-trajectory features → −0.025 to 0.606 → 5 seeds confirmed

### Beat 7 — HORIZON
**Logic:** The 5-second lead time is operationally necessary, and the TCN is the only method that provides it.
**Flow:** Short horizon: persistence wins (brain barely moves) → 5s: persistence AND Ridge collapse to negative R² → TCN holds → 5s is exactly the lead time for a controller to act

### Beat 8 — RESULTS
**Logic:** Real data, large effect sizes, universal benefit — not an average finding.
**Flow:** Replay on 35 real patients → targeting: 82.6% vs 51.7%, g=4.47 → alignment: 72.1% vs 64.5%, g=1.31 → 91% of oracle → 35/35 benefit including 6 test subjects → fatigue makes the advantage bigger

### Beat 9 — PRODUCT
**Logic:** This is a deployable product, not a research toy. Be specific. Then be honest.
**Flow:** Muse 2 $249, 4 dry electrodes → standard headphones, 40Hz AM audio → single laptop, <50ms → under $300 total → "not a lab instrument" → honest limitation (offline replay, not live) → next step: crossover clinical study → one-sentence closer → "What would you like me to go deeper on?"

---

## Step 3: Unlock Phrases (the only words you memorize verbatim)

| Beat | Unlock phrase |
|---|---|
| 1 | "Alzheimer's affects more than 55 million people worldwide, and there is still no cure." |
| 2 | "But every clinical protocol delivers this therapy the same way." |
| 3 | "Before I walk through the system — everything here is built around one biomarker: phase-amplitude coupling, PAC." |
| 4 | "The system runs in two stages." |
| 5 | "So I changed the question." |
| 6 | "I also made an unexpected discovery." |
| 7 | "This is where the project holds together." |
| 8 | "I validated by replaying the controller on all 35 patients' real EEG recordings." |
| 9 | "I want to be clear about where this becomes a product." |

Drill: Say all 9 unlock phrases in order, 5 times from memory. Then say them out of order (3, 7, 1, 5, 9, 2, 6, 4, 8).

---

## Step 4: Number Anchors

### Group A — Disease + Mechanism (Beat 1)
- **55** million worldwide
- **2016** Iaccarino (MIT)
- **40–50%** amyloid reduction
- **2024** Murdock (glymphatic)
- **2025** Chan (long-term safety)

*Memory trick:* Years count up — **2016 → 2024 → 2025**. Disease and reduction are round numbers.

### Group B — Dataset (Beat 2)
- **35** subjects
- **7** frontal EEG channels
- **250** Hz
- **40s on / 20s off** fixed protocol

*Memory trick:* "35 patients, 7 channels, 250 Hz" — say it like a rhythm.

### Group C — PAC Definition (Beat 3)
- **40 Hz gamma** amplitude
- **4–8 Hz theta** phase
- High PAC = entrained. Low PAC = drifted.

*Memory trick:* "Gamma locked to theta." One phrase. Always the same.

### Group D — Ceiling (Beat 4)
- **8** architectures
- **~1,500** params (EEGNet) to **~2M** (ViT)
- **0.287** R² — every single one

*Memory trick:* "1,500 to 2 million, all equal 0.287."

### Group E — Pivot (Beat 5)
- **20** seconds history in
- **5** seconds ahead out

*Memory trick:* "20 in, 5 out."

### Group F — Discovery (Beat 6)
- **73** features → **12** features (**61** spectral dropped)
- **−0.025** → **0.606** R²
- **5** random seeds validated

*Memory trick:* "73 minus 61 leaves 12. Negative zero to point six."

### Group G — Results (Beat 8)
- Targeting: **82.6%** vs **51.7%**, Hedges' g = **4.47**
- Alignment: **72.1%** vs **64.5%**, Hedges' g = **1.31**
- p < **0.001**
- **91%** of oracle
- **35/35** patients benefit, including **6** test subjects

*Memory trick:* Two pairs → "83 vs 52, 72 vs 64." Two g's → "4.47 and 1.31." Three closers → "91% oracle, 35/35, 6 test."

### Group H — Product (Beat 9)
- Muse 2 at **$249**, **4** dry electrodes
- **<50 ms** end-to-end latency
- **<$300** total per patient

*Memory trick:* "$249 headset, 4 electrodes, 50ms, $300."

---

## Step 5: Memory Palace — Use the Poster

Your body walks left → center → right. Your beats follow 1 → 9. They are synchronized.

```
LEFT COLUMN              CENTER                      RIGHT COLUMN
+----------------+       +-------------------+       +------------------+
| Introduction   | B1    | PAC Biomarker     | B3    | Controller table | B8
| Background     |       +-------------------+       +------------------+
+----------------+       | Stage 1 table     | B4    | 35/35 result     |
| Fig 3: Fixed   | B2    +-------------------+       +------------------+
| vs Adaptive    |       | Stage 2 / TCN     | B5    | Fatigue table    |
+----------------+       +-------------------+       +------------------+
| Materials      |       | Feature reduction | B6    | Towards Clinical | B9
+----------------+       +-------------------+       +------------------+
                         | Data Analysis     | B7
                         | Horizon figure    |
                         +-------------------+
```

If you ever lose your place, look at your hand on the poster. That tells you which beat you are in. Resume with the next unlock phrase.

---

## Step 6: Practice Schedule

### Day −2 (2 days before)
- **Morning (20 min):** Read the script silently twice. Read this guide.
- **Evening (30 min):** Read aloud twice. Time each run. Target under 4:15.

### Day −1 (1 day before)
- **Morning (20 min):** Say the 9-beat spine 5 times from memory. Drill unlock phrases.
- **Afternoon (30 min):** Full run in a mirror, no paper. Time it.
- **Evening (45 min):** Interruption drill — someone asks a Q&A question mid-beat. Answer it. Resume at the next unlock phrase.
- **Night (10 min):** Read unlock phrases once before sleep.

### Day 0 (judging day)
- **Pre-fair (15 min):** One full run. Do not over-drill.
- **At booth before judging (5 min):** Silent spine recitation. Touch each poster region while naming the beat.

---

## Step 7: Interruption Protocol

1. **Stop mid-sentence.** Do not finish the thought.
2. **Listen fully.** No half-attention.
3. **Answer from the Q&A bank.**
4. **Look at your hand on the poster.** That tells you which beat you were in.
5. **Resume with the next unlock phrase** — not where you were interrupted, but the start of the next beat.

---

## Step 8: Cold Start Drill

Someone names a beat number — you deliver it from scratch using only the unlock phrase.

Run in this order (not sequential — tests real recovery):

| Call | Deliver |
|---|---|
| "Beat 8" | Results table — 82% vs 52%, g's, oracle, 35/35 |
| "Beat 3" | PAC biomarker — gamma, theta, high/low meaning |
| "Beat 6" | Feature discovery — 73 to 12, −0.025 to 0.606 |
| "Beat 1" | Hook — 55M, Iaccarino, Murdock, Chan |
| "Beat 9" | Product — Muse 2, $249, <50ms, limitation, closer |
| "Beat 5" | Pivot — new question, TCN, 20s in 5s out, causal |
| "Beat 7" | Horizon — 1s baselines win, 5s they collapse, TCN holds |
| "Beat 4" | Ceiling — 8 architectures, all 0.287, data not model |
| "Beat 2" | Gap — fixed schedule, habituation, dataset |

If you can cold-start all 9 in one sitting without stumbling, you are ready.

---

## Red Flags (not memorized yet)

- Can only recall a beat by starting from Beat 1
- Stumble on the g-values or the R² numbers
- Freeze when interrupted and try to go back rather than forward
- Say the same sentence twice across two different practice runs

Fix: drill Step 3 (unlock phrases) and Step 4 (number anchors). Those are the skeleton.

---

## Green Flags (ready)

- 9-beat spine in under 40 seconds, eyes closed
- Any beat cold-started from its unlock phrase
- Interrupted mid-beat → answer → resume cleanly at next unlock phrase
- Numbers come out in groups, not one at a time
- Feels like telling a story, not reciting text

---

## One Final Thing

The judges are not testing your memory. They are testing your understanding. If you forget a number, check your lab notebook calmly — a student who pauses to verify scores higher than one who recites smoothly but can't explain what the numbers mean.

You built this system. That understanding is the muscle. The memorization is just the skeleton.
