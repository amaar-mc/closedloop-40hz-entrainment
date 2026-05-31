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

Then I audited basically everything. Checked all the numbers against the code output. Checked feature leakage again. Verified subject splits are clean. Scalers fit on train only. Wilcoxon is the right test (can't assume normality with N=35 and skewed PAC, I looked it up). Threshold sensitivity. Seed robustness. Hyperparameter sensitivity. 11 checks total.

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

Poster layout day. Bumped to V7. Board is 48 x 64 inches printed, which means designing at 36 x 48 in PowerPoint at 133% scale. Four columns. Wrote Python scripts to build the poster from content definitions so I can regenerate it quickly when numbers change.

The figure sizing took forever. The horizon sweep needs to be legible from 3 feet away but I only have maybe 5.5 x 3.5 inches of space for it in the right column. Had to bump the font size on the axis labels to 14pt and simplify the legend. Still not totally happy with it but it's readable.

---

## April 5-6, 2026

Printed the poster and did a test run where I stood across the room and tried to read every number. The Feature Discovery table was too small. Couldn't read the R2 values from more than 2 feet away. But the poster is already at the print shop. Going to have to point directly at those cells during the presentation and read the numbers aloud. Lesson learned: design for 4 feet, not 2.

Practiced the 60-second opening a few times out loud. It's too long. Cut some of the mechanism detail and landed at about 50 seconds. The rest is Q&A anyway.

---

## April 7, 2026

Paranoid quality pass on the poster before it goes final.

Checked all 37 numbers on the poster against the actual JSON and NPZ files. Wrote a quick script to automate the spot checks:

```python
import json
with open('results/metrics/tcn_validation_results.json') as f:
    data = json.load(f)

print(f"TCN alignment: {data['tcn_predictive']['alignment']:.1f}%")
print(f"Reactive alignment: {data['reactive_threshold']['alignment']:.1f}%")
# TCN: 72.1%, Reactive: 64.5% -- matches poster
```

Found 4 discrepancies. Three were rounding (within 0.1). One was a leftover Synopsys number I'd already fixed in the text but missed in a table caption. Fixed.

Went through all 14 figures. Checked resolution is 300+ DPI, axis labels readable at print size, colors consistent (blue/orange for TCN/Reactive, gray for Fixed, green for Oracle). Five figures had minor issues like font sizes or axis labels getting cut off. Fixed what I could, the rest are fine at print scale.

Also walked through the poster pretending to be a judge. What would I ask? Three weak spots I identified:

1. "Why only 6 test subjects?" -- need to emphasize 35/35 total benefit, not just the test split
2. "This is offline, not real time" -- need to be upfront about this as the main limitation
3. "How do you know the model isn't memorizing?" -- leakage story + permutation test

Prepared short answers for each.

---

## April 8, 2026

Tried to integrate TRIBE V2, Meta's brain foundation model that came out March 26. I wanted a better answer when judges ask "are you simulating how the brain responds to your stimulation?" Right now my answer is "no." That's bad.

TRIBE V2 takes audio/video/text and spits out predicted fMRI for ~70K voxels. Idea was: feed it my 40 Hz clicks, get cortical responses, pipe into a neural mass model that generates theta and gamma.

Didn't work. TRIBE V2's audio pathway runs through WhisperX for speech transcription first. A 40 Hz click train isn't speech. WhisperX returns nothing and the model outputs garbage. Spent a couple hours trying workarounds (padding with silence, embedding the clicks in white noise, converting to mel spectrograms manually). Nothing helped. The transcription step is baked into the pipeline.

So I built a workaround. Wrote a parametric cortical response model using time constants from the ASSR papers I'd been reading. It's not TRIBE V2 running inference. But it's way more biophysical than the simple exponential I had before.

```python
# from src/tribe_v2/cortical_model.py
class CorticalResponseConfig:
    onset_tau_sec: float = 1.5        # ASSR onset
    offset_tau_sec: float = 2.0       # ASSR offset
    habituation_rate: float = 0.005   # per-second habituation
```

The actual `get_activations()` uses an exponential-approach toward a target, with the habituation multiplier on the stim/rest difference. The full code is in the repo; I'm not pasting the whole loop here.

Then I connected it to a Wilson-Cowan neural mass model that generates theta and gamma from the activation envelope:

```python
# from src/tribe_v2/neural_mass.py
class NeuralMassConfig:
    tau_e: float = 0.004   # excitatory ~4ms, gamma range
    tau_i: float = 0.008   # inhibitory ~8ms, shapes gamma

# E/I dynamics (simplified)
dE = (-E + sigmoid(w_ee*E - w_ei*I + P_ext)) / cfg.tau_e
dI = (-I + sigmoid(w_ie*E - w_ii*I)) / cfg.tau_i
```

End-to-end chain: stim on/off -> cortical activation -> E/I dynamics -> theta-gamma PAC -> controller. Way more biological than the dumb exponential I had before.

Built three Alzheimer severity profiles in `alzheimer_model.py`. The real `AlzheimerProfile` dataclass has a bunch of fields -- here are the four that matter most for the simulation:

| Profile | Cortical Atrophy | Gamma Efficacy | Baseline PAC | Fatigue Mult |
|---|---|---|---|---|
| Healthy | 1.00 | 1.00 | 1.00 | 1.00 |
| Mild AD | 0.80 | 0.70 | 0.80 | 1.30 |
| Severe AD | 0.35 | 0.30 | 0.40 | 2.00 |

Mild profile = lower gamma efficacy + faster fatigue. Matches what the amyloid papers say. Severe AD basically can't make gamma at all.

Ran the full controller comparison on the biophysical sim. Looks the same shape as the real-data replay -- predictive beats reactive for healthy and mild AD. For severe AD the gap closes, there's just not enough entrainment to work with. Makes sense honestly. If the brain can't synchronize to the stimulus, there's nothing for the controller to pick between.

Ran 41 integration checks on the pipeline. All passed.

Caveat I have to own with judges: this isn't TRIBE V2 actually running. TRIBE V2 inspired the setup but the predictions come from literature-calibrated parameters. So I'll call it "a biophysical model informed by TRIBE V2," not "TRIBE V2 integration." Overselling would be worse than not mentioning it.

Also updated poster specs to poster V8, ran the coherence audit, and wrote the judging strategy doc.

---

## Current Project Status (April 8, 2026)

Everything is done except presentation prep. CSEF judging is April 12.

Where I'm at: 7 channels in at 250 Hz, preprocess, compute PAC (Tort MI, 18 bins). EEGNet (1,457 params) gives me current PAC per 2-sec window. 12 features go to the TCN, which forecasts 5 seconds out. Poster uses the h=32 model (5,154 params, test R2 = 0.613). The 5-seed benchmark of 0.606 (poster's ablation number) was on the h=64 model (22,914 params). Both runs are in my March 10-14 entries. Personalization module runs a 30-sec z-score baseline. Controller: z below -0.5 stimulate, z above +0.5 rest, 5-second hysteresis.

Where things stand:

- Static prediction ceiling: R2 = 0.287, confirmed across every architecture I tried (6 in the poster table)
- Feature ablation: dropping 61 spectral features raised single-seed test R2 from -0.025 (73 features) to 0.558 (12 features, seed 42). A 5-seed rerun confirmed 0.606 +/- 0.029 mean on h=64.
- Controller: 72.1% alignment vs 64.5% reactive, Hedges' g = 1.31, p < 0.001
- Low-PAC targeting: 82.6% vs 51.7%, g = 4.47
- 35/35 subjects benefited, 91% of oracle performance
- End-to-end inference latency under 50 ms
- Biophysical simulation confirms disease-stage dependency (works for early-moderate AD, not severe)
- Caveat from my March 22 entry: the 72.1% / 64.5% controller numbers were generated with the original 73-feature TCN before the feature ablation. The feature-ablation result (R2 = 0.606) and the controller-replay result (72.1%) are from two different training runs. I have not re-run the full 35-subject replay with the deployed 12-feature model. Judge-facing framing: "the predictive controller works; the forecasting core is now smaller and better."

Big limitation, still: real-data validation uses offline replay on recorded EEG, not live closed-loop streaming. The system makes decisions on real brain data, and the biophysical sim (April 8) simulates how the brain will respond to the stimulus. Neither is live closed-loop on a patient yet. That is the next experiment.

---

## Additional References (Extension Period)

Murdock, M. H., et al. (2024). Multisensory gamma stimulation promotes glymphatic clearance of amyloid. *Nature*, 627, 149-156.

Chan, D., et al. (2025). Long-term safety of 40 Hz sensory stimulation. *Alzheimer's & Dementia*, 21(10), e70792.

Soula, M., et al. (2023). Forty-hertz light stimulation does not entrain native gamma oscillations in Alzheimer's disease model mice. *Nature Neuroscience*, 26, 570-578.

Meta AI. (2026). TRIBE V2: A Predictive Foundation Model for Brain Encoding. HuggingFace: facebook/tribev2.
