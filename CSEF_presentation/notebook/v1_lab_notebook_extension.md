# Project P10 Research Log Notebook (Extension)

### Continuation from March 22, 2026 through April 8, 2026

### Amaar Chughtai

### California Science & Engineering Fair 2026

---

## March 24, 2026

Spent most of the day reorganizing files. The CSEF/ directory was a mess -- Synopsys materials in three different folders, file names that made no sense, duplicates everywhere. Moved everything into a clean hierarchy: abstracts, poster files, scripts, research paper versions, flyer, clinical roadmap. Should have done this weeks ago.

Made a facility outreach flyer for local memory care homes. I want to show judges I'm actually trying to get this into the real world, not just writing papers about it. Target places: Mission Villa Alzheimer's Residence and Valley Medical Veterans Center. Haven't heard back from either yet.

Printed the abstract as P10.Abstract.pdf.

---

## March 27-28, 2026

Found a dumb bug. The hysteresis hold time in config.yaml was set to 3.0 seconds but the research paper and every presentation said 5 seconds. The controller code was reading from a hardcoded default of 5, so it was actually running correctly, but the config was wrong. Would have been embarrassing if a judge pulled up the config file.

```python
# config.yaml -- fixed
controller:
  hold_time_sec: 5.0  # was 3.0, didn't match any documentation
```

Finalized all the CSEF submission materials. Regenerated the controller comparison and per-subject utility figures because the old axis labels were cut off at print size. Also wrote a sliding window PAC computation module in experimental/ -- not using it for the main results but it's there for real-time work later.

Then I went through and audited basically everything. Checked all the numbers match between the code output and the poster, checked for feature leakage again, verified subject splits are clean, made sure the scalers are fit on train only, reviewed whether Wilcoxon was the right test (it is -- can't assume normality with N=35 and skewed PAC). Checked threshold sensitivity, seed robustness, hyperparameter sensitivity. 11 separate checks total.

```python
def verify_subject_splits(train_ids, val_ids, test_ids):
    assert len(set(train_ids) & set(val_ids)) == 0
    assert len(set(train_ids) & set(test_ids)) == 0
    assert len(set(val_ids) & set(test_ids)) == 0
    assert len(train_ids) + len(val_ids) + len(test_ids) == 35
```

Everything passed. One rounding discrepancy -- the poster says PAC gap is 30.5 but the raw number is 30.47. Rounds correctly.

Also wrote a comparison doc between CSEF and Synopsys rules. The big difference: CSEF judges read your 13-page presentation beforehand and there's no scoring rubric, just consensus. That changes the whole interview strategy.

---

## April 2, 2026

Poster layout day. Board is 48 x 64 inches printed, which means designing at 36 x 48 in PowerPoint at 133% scale. Four columns. Wrote Python scripts to build the poster from content definitions so I can regenerate it quickly when numbers change.

The figure sizing took forever. The horizon sweep needs to be legible from 3 feet away but I only have maybe 5.5 x 3.5 inches of space for it in the right column. Had to bump the font size on the axis labels to 14pt and simplify the legend. Still not totally happy with it but it's readable.

---

## April 5-6, 2026

Printed the poster and did a test run where I stood across the room and tried to read every number. The Feature Discovery table was too small -- couldn't read the R-squared values from more than 2 feet away. But the poster is already at the print shop. Going to have to point directly at those cells during the presentation and read the numbers aloud. Lesson learned: design for 4 feet, not 2.

Practiced the 60-second opening a few times out loud. It's too long. Cut some of the mechanism detail and landed at about 50 seconds. The rest is Q&A anyway.

---

## April 7, 2026

Paranoid quality pass on the poster before it goes final.

Checked all 37 numbers on the poster against the actual JSON and NPZ files. Wrote a quick script to automate the spot checks:

```python
import json
with open('results/tcn_validation_results.json') as f:
    data = json.load(f)

print(f"TCN alignment: {data['tcn_predictive']['alignment']:.1f}%")
print(f"Reactive alignment: {data['reactive_threshold']['alignment']:.1f}%")
# TCN: 72.1%, Reactive: 64.5% -- matches poster
```

Found 4 discrepancies. Three were rounding (within 0.1). One was a leftover Synopsys number I'd already fixed in the text but missed in a table caption. Fixed.

Went through all 13 figures -- checked resolution is 300+ DPI, axis labels are readable at print size, colors are consistent (blue/orange for TCN/Reactive, gray for Fixed, green for Oracle). Five figures had minor issues like font sizes or axis labels getting cut off. Fixed what I could, the rest are fine at print scale.

Also walked through the poster pretending to be a judge. What would I ask? Three weak spots I identified:

1. "Why only 6 test subjects?" -- need to emphasize 35/35 total benefit, not just the test split
2. "This is offline, not real time" -- need to be upfront about this as the main limitation
3. "How do you know the model isn't memorizing?" -- leakage story + permutation test

Prepared short answers for each.

---

## April 8, 2026

Tried to integrate TRIBE V2, Meta's brain foundation model that came out March 26. The motivation was practical -- judges will ask "are you simulating how the brain responds to your stimulation?" and I wanted a better answer than "no."

TRIBE V2 takes stimulus input (audio, video, text) and predicts fMRI-level brain activation at ~70,000 cortical voxels. The idea was to feed it my 40 Hz click trains and get predicted cortical responses, then pipe those into a neural mass model to generate theta-gamma oscillations.

Didn't work. TRIBE V2's audio pathway runs through WhisperX for speech transcription first. A 40 Hz click train isn't speech. WhisperX returns nothing and the model outputs garbage. I spent a couple hours trying different audio preprocessing (padding with silence, embedding the clicks in white noise, converting to mel spectrograms manually) but nothing helped. The transcription step is baked into the pipeline.

So I built a workaround. Instead of using TRIBE V2 directly, I wrote a parametric cortical response model grounded in the ASSR literature. The time constants come from published auditory steady-state response studies. It's not TRIBE V2 running inference, but it's biophysically motivated rather than the simple exponential model I was using before.

```python
# from src/tribe_v2/cortical_model.py
class CorticalResponseConfig:
    onset_tau_sec: float = 1.5     # ASSR onset time constant
    offset_tau_sec: float = 2.0    # ASSR offset time constant
    adaptation_rate: float = 0.002

# activation computation (simplified from actual code)
if stim_state:
    tau = cfg.onset_tau_sec
    onset = 1.0 - np.exp(-time_in_state / tau)
    adapt = np.exp(-cfg.adaptation_rate * time_in_state)
    activation = onset * adapt
else:
    tau = cfg.offset_tau_sec
    activation = np.exp(-time_in_state / tau)
```

Then I connected it to a Wilson-Cowan neural mass model that generates theta and gamma oscillations from the activation envelope:

```python
# from src/tribe_v2/neural_mass.py
class NeuralMassConfig:
    tau_e: float = 0.004       # excitatory ~4ms, gamma range
    tau_i: float = 0.008       # inhibitory ~8ms, shapes gamma

# E/I dynamics (simplified)
dE = (-E + sigmoid(w_ee * E - w_ei * I + P_ext)) / cfg.tau_e * dt
dI = (-I + sigmoid(w_ie * E - w_ii * I)) / cfg.tau_i * dt
```

This gives me a simulation chain: stimulus on/off --> cortical activation (parametric) --> E/I oscillatory dynamics (Wilson-Cowan) --> theta-gamma PAC --> controller decisions. It's more biologically grounded than the old exponential rise/decay model.

Built three Alzheimer's severity profiles in `alzheimer_model.py`:

| Profile | Cortical Gain | Adaptation Rate | Gamma Power |
|---|---|---|---|
| Healthy | 1.0 | 0.002 | 1.0 |
| Mild AD | 0.5 | 0.008 | 0.6 |
| Severe AD | 0.3 | 0.015 | 0.3 |

The mild profile reduces excitability and speeds up habituation, which matches what the amyloid papers describe. Severe AD can barely generate gamma at all.

Ran the full controller comparison on the biophysical simulator. The results are qualitatively consistent with the real-data replay -- predictive control beats reactive for healthy and mild AD patients. For severe AD, the gap basically closes because there's not enough entrainment response to optimize. Which actually makes sense. If the brain can't synchronize to the stimulus, there's nothing for the controller to work with.

Ran 41 integration checks on the pipeline. All passed.

Important caveat I need to be clear about with judges: this biophysical simulation is not the same as TRIBE V2 running inference. TRIBE V2 inspired the architecture but the actual predictions come from literature-calibrated parameters, not from the foundation model. I should frame this as "a biophysical brain model informed by the TRIBE V2 framework" not "TRIBE V2 integration." Overstating it would be worse than not mentioning it.

Also updated poster specs to V7 and V8, ran the coherence audit, and wrote the judging strategy doc.

---

## Current Project Status (April 8, 2026)

Everything is done except presentation prep. CSEF judging is April 12.

The full system: EEG comes in from 7 frontal channels at 250 Hz, gets preprocessed, PAC is computed via Tort MI (18 phase bins). EEGNet (1,457 params) estimates current PAC from each 2-second window. 12 features (7 PAC-trajectory + 5 stim context) go to the Causal TCN, which predicts PAC 5 seconds ahead. The deployed model on the poster is the h=32 variant at 5,154 parameters (test R2 = 0.613); the 5-seed benchmark number of 0.606 was measured on the h=64 variant at 22,914 params. Both are in my March 10-14 entries. The personalization module converts predictions to z-scores against a 30-second rolling baseline. Controller decides: z < -0.5 means stimulate, z > +0.5 means rest, 5-second hysteresis prevents flickering.

Where things stand:

- Static prediction ceiling: R2 = 0.287, confirmed across 8 architectures
- Feature ablation: dropping 61 spectral features raised test R2 from -0.025 to 0.606 (5-seed mean, population std 0.029)
- Controller: 72.1% alignment vs 64.5% reactive, Hedges' g = 1.31, p < 0.001
- Low-PAC targeting: 82.6% vs 51.7%, g = 4.47
- 35/35 subjects benefited, 91% of oracle performance
- Inference under 50 ms on CPU
- Biophysical simulation confirms disease-stage dependency (works for early-moderate AD, not severe)

Main limitation that hasn't changed: this is offline replay, not live closed-loop. The controller makes good decisions on real brain data but we don't know if acting on those decisions actually changes outcomes. That's the next experiment.

---

## Additional References (Extension Period)

Murdock, M. H., et al. (2024). Multisensory gamma stimulation promotes glymphatic clearance of amyloid. *Nature*, 627, 149-156.

Chan, D., et al. (2025). Long-term safety of 40 Hz sensory stimulation. *Alzheimer's & Dementia*, 21(10), e70792.

Soula, M., et al. (2023). Forty-hertz light stimulation does not entrain native gamma oscillations in Alzheimer's disease model mice. *Nature Neuroscience*, 26, 570-578.

Meta AI. (2026). TRIBE V2: A Predictive Foundation Model for Brain Encoding. HuggingFace: facebook/tribev2.
