# Mind Map: 3-4 Minute Board Walk (v2)

Visual structure of the script. Use this to see the whole flow at once.

---

```
                    OPENING HOOK (45s)
                    "Hi, I'm Amaar..."
                           |
            +-----------------------------+
            |   THE DISEASE + MECHANISM   |
            |   55M people, no cure       |
            |   40 Hz auditory therapy    |
            |   MIT / Iaccarino 2016      |
            |   40-50% amyloid reduction  |
            |   Murdock 2024 glymphatic   |
            |   Chan 2025 safety          |
            +-----------------------------+
                           |
                           v
                    THE GAP (40s)
                    "But every protocol..."
                           |
            +-----------------------------+
            |   Fixed 40s on / 20s off    |
            |   Half habituate            |
            |   Half get stronger         |
            |   Thompson & Spencer 1966   |
            |   Dataset: Lahijanian 2024  |
            |   35 subjects / 7 ch / 250Hz|
            |   24 train / 5 val / 6 test |
            +-----------------------------+
                           |
                           v
                STAGE 1 CEILING (45s)
                "The system runs in two stages..."
                           |
            +-----------------------------+
            |   PAC = gamma locked theta  |
            |   High = entrained          |
            |   Low = losing sync         |
            |   8 architectures tested    |
            |   1,500 to ~2M params       |
            |   ALL hit R² = 0.287        |
            |   Not model, not data ceiling|
            |   2s snapshots = limit      |
            +-----------------------------+
                           |
                           v
                THE PIVOT (25s)
                "So I changed the question..."
                           |
            +-----------------------------+
            |   Causal TCN                |
            |   20s history --> 5s ahead  |
            |   Left-only padding         |
            |   ARCHITECTURAL not trained |
            +-----------------------------+
                           |
                           v
            FEATURE DISCOVERY (35s)
            "An unexpected discovery..."
                           |
            +-----------------------------+
            |   Original: 73 features     |
            |   Test R² ≈ 0 (-0.025)      |
            |   61 spectral = anatomy     |
            |   Skull, electrode impedance|
            |   Memorization not learning |
            |   Dropped spectral          |
            |   Kept 12 (PAC + stim ctx)  |
            |   R² jumped to 0.606        |
            |   5-seed robust ±0.029      |
            +-----------------------------+
                           |
                           v
                HORIZON SWEEP (25s)
                "This is where it holds..."
                           |
            +-----------------------------+
            |   1-2s: persistence wins    |
            |   5s: baselines go NEGATIVE |
            |   TCN only method holding   |
            |   5s = controller lead time |
            +-----------------------------+
                           |
                           v
                CONTROLLER (40s)
                "I validated on all 35..."
                           |
            +-----------------------------+
            |   72.1% vs 64.5% alignment  |
            |   82.6% vs 51.7% low-PAC    |
            |   Hedges' g = 1.31 / 4.47   |
            |   p < 0.001                 |
            |   91% of oracle             |
            |   35/35 benefit             |
            |   Including 6 test subjects |
            |   Advantage grows w/ fatigue|
            +-----------------------------+
                           |
                           v
                THE PRODUCT (30s)
                "Where this becomes a product..."
                           |
            +-----------------------------+
            |   Muse 2: $249, 4 dry elec  |
            |   Standard headphones       |
            |   40 Hz AM audio            |
            |   <50 ms inference          |
            |   <$300/patient total       |
            |   Memory care facility /    |
            |   home deployment           |
            +-----------------------------+
                           |
                           v
                CLOSER (10s)
                "Offline replay limitation.
                Next: crossover study.
                One sentence: predict loss,
                time stimulation to matter."
```

---

## The 8-Section Story Arc

```
 1. HOOK          Hi, I'm Amaar. 55 million. 40 Hz. MIT.
     |
 2. GAP           Fixed schedule. Half habituate.
     |
 3. CEILING       8 architectures. 0.287. Data not model.
     |
 4. PIVOT         TCN. 20s history. 5s ahead. Causal.
     |
 5. DISCOVERY     73 -> 12 features. -0.025 -> 0.606.
     |
 6. HORIZON       Baselines collapse. TCN holds. 5s lead.
     |
 7. RESULTS       72% vs 64%. 35/35. Hedges g 4.47.
     |
 8. PRODUCT       Muse 2 $249. Under $300. Crossover next.
```

---

## The "Three Moments" That Matter Most

If you remember nothing else, remember these three beats. They are the scientific reasoning highlights that distinguish this from a tutorial project:

### Moment 1: The Ceiling Discovery
> "Eight architectures from 1,500 parameters to two million, and every single one hit R² = 0.287. That told me I was at a data ceiling, not a model ceiling."

**Why it matters:** Shows diagnostic reasoning. Most students would keep tuning. You diagnosed the root cause.

### Moment 2: The Feature Paradox
> "My 73-feature model was memorizing skull anatomy, not learning dynamics. Dropping 61 features took test R² from negative 0.025 to 0.606."

**Why it matters:** Counterintuitive finding. Removing information improved generalization. This is the signature of someone who understands overfitting at a deep level.

### Moment 3: The Horizon Inflection
> "At 5 seconds out, every simple method collapses to negative R². The TCN is the only thing that holds. And 5 seconds is exactly the lead time a controller needs."

**Why it matters:** Ties the ML work directly to a clinical requirement. This is the "aha" that connects your engineering to real patient outcomes.

---

## Poster as Memory Palace

Walk the poster left-to-right in your head. Each region is a "room":

```
LEFT COLUMN (Room 1)          CENTER (Room 2)              RIGHT COLUMN (Room 3)
+-------------------+         +-------------------+        +-------------------+
| Introduction      |         | System Architecture|       | Results/Findings  |
| Background        |  -->    | Stage 1 table     |  -->   | Controller table  |
| Fig 3: Fixed v    |         | Stage 2 table     |        | Every patient fig |
| Adaptive          |         | Feature reduction |        | Fatigue advantage |
| Hypothesis        |         | Data Analysis     |        | Towards Clinical  |
| Materials + data  |         | Horizon figure    |        | Conclusions       |
+-------------------+         +-------------------+        +-------------------+

Story beats:                  Story beats:                Story beats:
- Hook                        - Ceiling                   - Controller wins
- Gap                         - Pivot                     - Product demo
- Dataset                     - Discovery                 - Closer
                              - Horizon
```

---

## Transition Phrases (memorize these exactly)

These are the "glue" between sections. If you get stuck mid-script, jumping to one of these pulls you back onto track:

| From | To | Phrase |
|---|---|---|
| Mechanism | Gap | "But every clinical protocol delivers this therapy the same way." |
| Gap | Stage 1 | "The system runs in two stages." |
| Ceiling | Pivot | "So I changed the question." |
| Pivot | Discovery | "I also made an unexpected discovery." |
| Discovery | Horizon | "This is where the project holds together." |
| Horizon | Results | "I validated by replaying the controller on all 35 patients' real EEG." |
| Results | Product | "I want to be clear about where this becomes a product." |
| Product | Closer | "The honest limitation is..." |

---

## Numbers Bank (lock these in)

Arranged by when you say them in the script:

```
SECTION 1 (hook)          SECTION 5 (discovery)
- 55 million              - 73 features
- 40 Hz                   - -0.025 (test R²)
- 2016 (Iaccarino)        - 61 spectral
- 40-50% amyloid          - 12 features
- 2024 (Murdock)          - 0.606 (5-seed mean)
- 2025 (Chan)             - ±0.029

SECTION 2 (gap)           SECTION 6 (horizon)
- 40s on / 20s off        - 5 seconds ahead
- 35 subjects             - 20 seconds history
- 7 frontal channels      - (1-2s: baselines fine)
- 250 Hz                  - (5s: baselines negative)
- 24 / 5 / 6 splits

SECTION 3 (ceiling)       SECTION 7 (results)
- 8 architectures         - 72.1% vs 64.5%
- 1,500 params (EEGNet)   - 82.6% vs 51.7%
- ~2M params (ViT-TCNet)  - Hedges' g = 1.31
- R² = 0.287              - Hedges' g = 4.47
                          - p < 0.001
                          - 91% of oracle
SECTION 4 (pivot)         - 35 of 35
- 20s history             - 6 test subjects
- 5s ahead                - 5 severity levels
- Causal (left padding)

SECTION 8 (product)
- $249 (Muse 2)
- 4 dry electrodes
- <50 ms inference
- Under $300/patient
```

---

## The "If You Blank" Anchor

If your brain freezes mid-section, this single sentence will always work as a recovery line because it is your core thesis:

> "The main contribution is that the system predicts when a patient's brain is about to lose response to 40 hertz therapy, five seconds ahead, so stimulation can be timed to the moments it actually matters. And on all 35 patients, it worked."

Say that, then look at the poster, find the section you were in, and resume.

---

## Practice Protocol (48 hours before judging)

**Pass 1 - Read silently** (10 min): Read the v2 script end to end. No talking.

**Pass 2 - Read aloud, no poster** (15 min): Stand up, read aloud from paper. Time yourself. Target 3:30 to 3:45.

**Pass 3 - Cover one section at a time** (20 min): Cover each section with your hand, say it from memory, uncover to check. Do this for all 8 sections.

**Pass 4 - Full run, no paper, with poster** (10 min): Stand in front of the poster, deliver the full script without notes. Use the pointing cues. Time it.

**Pass 5 - Interruption drill** (15 min): Have someone interrupt you at random points with a question from the Q&A bank. Answer the question, then pick up from the next transition phrase.

**Pass 6 - Cold start drill** (10 min): Have someone name a section ("Feature Discovery"). Start cold from that section's transition phrase. Deliver that section only. Do this for all 8 sections out of order.

If you can do Pass 6 cleanly, you are memorized.
