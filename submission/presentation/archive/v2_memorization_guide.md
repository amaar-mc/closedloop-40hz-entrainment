# Memorization Guide for the Full Technical Script

You don't memorize words. You memorize a journey. The words come from understanding where you are in the journey and what comes next.

This guide gives you **the architecture of the script in your head** so that even if you blank on a sentence, you always know what block you're in, what the point of that block is, and what comes after it.

---

## THE POSTER IS YOUR MEMORY PALACE

You're not memorizing a script on a page. You're walking through your poster left to right, and each physical location on the poster is a room in your mind. When you point at a section, you know what to say because you're _standing in that room_.

```
YOUR POSTER, LEFT TO RIGHT:

[1. GREETING]     [2. THE SCIENCE]   [3. THE GAP]        [4. HYPOTHESIS]
   (you)           (Background)       (Intro + Fig 1)     (Hypothesis box)

[5. MEASURING]    [6. THE WALL]      [7. THE PIVOT]      [8. THE KEY CHART]
   (PAC box)       (Stage 1 table)    (Stage 2 / TCN)     (Figure 5)

[9. PROOF]        [10. EVERY PATIENT] [11. FATIGUE]       [12. HONESTY]
   (Result 1)      (Figure 9)          (Result 3+4)        (step back)
```

That's 12 rooms. Learn the rooms, not the words.

---

## THE EIGHT-WORD METHOD

For each room, there is one sentence of 8 words or fewer that captures the entire block. If you know these 12 sentences, you can reconstruct the full presentation from understanding alone.

Say these out loud right now. Slowly. One at a time.

```
 1. GREETING:      "Hi, I'm Amaar. Walk you through it?"
 2. THE SCIENCE:    "Sound at 40 hertz clears Alzheimer's plaques."
 3. THE GAP:        "Every patient gets the same dumb schedule."
 4. HYPOTHESIS:     "Predict 5 seconds ahead, adapt stimulation proactively."
 5. MEASURING:      "PAC measures how locked on the brain is."
 6. THE WALL:       "Six models, same ceiling. Data is the limit."
 7. THE PIVOT:      "Don't predict better. Predict further. Use sequences."
 8. THE KEY CHART:  "At 5 seconds, only the TCN survives."
 9. PROOF:          "72% alignment, 83% targeting, 92% of oracle."
10. EVERY PATIENT:  "35 out of 35. Every single one."
11. FATIGUE:        "Worse the fatigue, bigger the advantage."
12. HONESTY:        "Offline replay. Real data. Next step: live."
```

These are your anchors. If you ever lose your place, find which room you're in, say the anchor in your head, and the rest flows.

---

## THE CHAIN: HOW EACH BLOCK LEADS TO THE NEXT

The script isn't 12 disconnected blocks. It's a chain where the last thought of each block _becomes_ the first thought of the next. This is the connective tissue. Memorize the transitions, not the paragraphs.

```
GREETING → THE SCIENCE
  "my grandmother had dementia... that's how I found 40 Hz entrainment"

THE SCIENCE → THE GAP
  "the science is real... but here's what bothered me"

THE GAP → HYPOTHESIS
  "nobody was predicting ahead of time... that gap is what this project is about"

HYPOTHESIS → MEASURING
  "before I could predict anything, I had to figure out how to measure it"

MEASURING → THE WALL
  "so my first challenge was: can I estimate PAC from raw EEG?"

THE WALL → THE PIVOT
  "that realization told me exactly where to go next"

THE PIVOT → THE KEY CHART
  "this figure is where the whole project comes together"

THE KEY CHART → PROOF
  "the proof that this prediction is useful is in the controller performance"

PROOF → EVERY PATIENT
  "but the most compelling result is this..."

EVERY PATIENT → FATIGUE
  "and when I tested across fatigue levels..."

FATIGUE → HONESTY
  "now, I want to be upfront about the constraints"

HONESTY → OPEN
  "would you like me to go deeper, or do you have questions?"
```

Practice saying ONLY the transitions. Just the bridge sentences. Do it 5 times. This is what makes the presentation feel like a single flowing story instead of bullet points.

---

## EMOTIONAL ANCHORING

Each room has a feeling. You lived this project. These aren't facts you're reciting; they're experiences you had. When you're in each room, feel it.

| Room              | Feeling                  | What you're thinking as you speak                                     |
| ----------------- | ------------------------ | --------------------------------------------------------------------- |
| 1. GREETING       | Warm, confident          | "I'm glad you're here. I'm excited to share this."                    |
| 2. THE SCIENCE    | Wonder, respect          | "This discovery blew my mind when I first read it."                   |
| 3. THE GAP        | Frustration, disbelief   | "How is nobody doing this? This is so obviously broken."              |
| 4. HYPOTHESIS     | Determination            | "I knew exactly what I wanted to prove."                              |
| 5. MEASURING      | Precision, craftsmanship | "I need to explain this clearly because PAC is the foundation."       |
| 6. THE WALL       | Surprise, then insight   | "I expected one model to win. They all tied. That was the discovery." |
| 7. THE PIVOT      | Excitement, breakthrough | "This is where the whole project changed direction."                  |
| 8. THE KEY CHART  | Pride, conviction        | "This is my best figure. This is the intellectual heart."             |
| 9. PROOF          | Confidence, data speaks  | "The numbers back everything up. Let me show you."                    |
| 10. EVERY PATIENT | Awe, the mic-drop        | "35 out of 35. That's the one that gets people."                      |
| 11. FATIGUE       | Thoroughness             | "I didn't stop at one test. I stress-tested it."                      |
| 12. HONESTY       | Maturity, self-awareness | "I know what this doesn't prove yet. That's strength, not weakness."  |

When you practice, don't just say the words. Put yourself back in the moment you discovered each thing. The Wall felt like a wall. The Pivot felt like a breakthrough. The 35/35 result felt like disbelief. Channel that.

---

## NUMBER CLUSTERS

Don't memorize numbers as isolated facts. They live in clusters of 3, tied to meaning.

**Cluster 1: The Data**

```
35 patients, 7 channels, 250 hertz
  (who you studied, what you measured, how fast)
```

**Cluster 2: The Wall**

```
6 architectures, 1457 to 2 million params, all R² = 0.287
  (how many you tried, the range, what they all hit)
```

**Cluster 3: The TCN**

```
73 features, 20 seconds of history, 5 seconds ahead
  (what goes in, how far back, how far forward)
```

**Cluster 4: The Horizon Sweep**

```
At 1 second: 0.81 (trivial, don't need DL)
At 5 seconds: baselines negative, TCN = 0.25
The margin: +0.5 (the value proposition)
```

**Cluster 5: The Controller**

```
Fixed:    45% alignment, PAC gap negative (wrong direction)
Reactive: 64.5% alignment, catches 52% of low-PAC
TCN:      72.1% alignment, catches 83% of low-PAC, 92% of oracle
```

**Cluster 6: The Universality**

```
35/35 patients, including 6 unseen test subjects
Fatigue advantage: +9% to +11.2%, g = 1.7 to 2.4
4 different fatigue models, all hold
```

Practice each cluster as a group. Say the cluster label, then rattle off the three items. Do this while walking around. The physical movement helps encode them.

---

## THE FIVE-PASS PRACTICE METHOD

Don't read the script 10 times robotically. Use these 5 passes, each with a different purpose.

### Pass 1: "Read and Absorb" (15 min)

Read the full script out loud, slowly. Don't try to memorize. Just listen to yourself say it. Notice where the story feels natural and where it feels forced. Mark the transitions that feel awkward.

### Pass 2: "Rooms Only" (5 min)

Close the script. Walk through the 12 rooms using only the 8-word anchors. Point at an imaginary poster. Say the anchor sentence for each room, then try to say 2-3 sentences expanding it. If you get stuck, open the script, read just that room, close it, and try again.

### Pass 3: "Transitions Only" (5 min)

Close the script. Say only the 12 chain transitions out loud. Just the bridge sentences. The goal is to make these automatic -- so that finishing one block _pulls_ you into the next without thinking.

### Pass 4: "Full Run, No Script" (6 min)

Put the script face-down. Stand up. Point at an imaginary poster. Do the whole thing start to finish. When you blank, pause for 3 seconds and try to recall which room you're in and what the anchor is. If you still can't, glance at the anchor list (not the full script) and keep going. Time yourself.

### Pass 5: "Full Run, Record Yourself" (6 min)

Use your phone voice recorder. Do the full presentation standing up, pointing at your poster (or a photo of it on a screen). Listen back. You'll immediately hear where you sound natural and where you sound robotic. The robotic parts are where you're reciting memorized words instead of explaining from understanding. Fix those by going back to the room's emotional anchor and the 8-word summary, and re-derive your own phrasing.

---

## THE RECOVERY PROTOCOL

You will blank at some point. Every presenter does. Here's how to recover without the judge noticing.

**Step 1: Breathe.** One breath. Not a dramatic pause, just a normal breath.

**Step 2: Where am I?** Look at the poster. Which section are you pointing at? That tells you which room you're in.

**Step 3: What's the anchor?** Say the 8-word anchor for that room in your head. "Six models, same ceiling. Data is the limit."

**Step 4: What's the next room?** Use the chain. "That realization told me exactly where to go next." Now you're moving forward.

**Step 5: If you truly blank**, just say to the judge: "Let me show you this figure" -- point to the next major visual and start talking about what it shows. You can always restart from a figure because the figures tell the story visually.

---

## PHYSICAL REHEARSAL MAP

When you practice, physically move. Your body remembers positions.

```
START:    Stand LEFT of poster. Facing judge.
          Rooms 1-4 (greeting through hypothesis).
          Your hands are open, gesturing generally at the left column.

MIDDLE:   Step to CENTER of poster.
          Rooms 5-8 (measuring, wall, pivot, key chart).
          You're pointing at specific tables and figures now.
          Your dominant hand traces lines on the charts.

END:      Step to RIGHT of poster.
          Rooms 9-12 (proof, every patient, fatigue, honesty).
          You're pointing at results tables and scatter plots.
          For room 12 (honesty), step BACK slightly. Open posture.
          You're no longer pointing at the poster. You're looking at the judge.
```

Your body position anchors your brain to the content. Practice the physical movement along with the words. After 3 reps, you'll find that stepping to the center of the poster automatically triggers "so my first challenge was..."

---

## THE "EXPLAIN IT TO SOMEONE RIGHT NOW" TEST

The ultimate test of memorization isn't reciting. It's explaining to another person.

Find someone tonight -- a parent, sibling, friend -- and say: "Can I practice my presentation on you? It's about 5 minutes." Then do it.

If you can do it for a real human, making eye contact, responding to their facial expressions, and not losing the thread -- you're ready.

If you can't find someone, do it in a mirror. Talking to your own eyes forces the same presence.

---

## QUICK REFERENCE: ALL 12 ROOMS ON ONE CARD

Print this or keep it on your phone. Glance at it once before each judge. That's all you need.

```
 1. GREETING      → Hi, walk you through it?
 2. SCIENCE       → 40 Hz clears plaques (MIT 2016, Lahijanian 2024)
 3. GAP           → Fixed schedule, half habituate, nobody predicting
 4. HYPOTHESIS    → Predict 5s ahead, adaptive closed-loop, beat fixed+reactive
 5. PAC           → Gamma locked to theta, Tort's Modulation Index
 6. WALL          → 6 architectures, all 0.287, data ceiling not model ceiling
 7. PIVOT         → Sequence of snapshots, not one snapshot. TCN: 73 feat, 20s, causal
 8. KEY CHART     → 1s trivial, 5s baselines die, TCN +0.5 margin
 9. PROOF         → 72.1% align, 82.6% targeting, fixed is NEGATIVE
10. EVERY PATIENT → 35/35, including 6 unseen, p < one in 34 billion
11. FATIGUE       → +9% to +11.2%, 4 models, g=1.7-2.4
12. HONESTY       → Offline replay, 2ms inference, next = live streaming + RL
    → "Questions?"
```
