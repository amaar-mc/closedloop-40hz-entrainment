# 3 to 4 Minute Board Walk

Use this when a judge wants a fuller walkthrough.

This script follows the physical poster from left to right and includes direct pointing cues.

---

Hi, I'm Amaar. Thanks for coming by. Let me walk you through the project.

[Point to **Introduction**, top left.]

Alzheimer's disease affects more than 55 million people worldwide, and one promising non-drug approach is 40 Hz auditory stimulation, where sound is pulsed 40 times per second. That stimulation improves synchronization between theta and gamma rhythms and has been linked to amyloid clearance through microglial and glymphatic pathways.

The problem is that the therapy is usually delivered on a fixed schedule, typically 40 seconds on and 20 seconds off, for every patient.

[Point down to **Figure 3: Fixed vs. Adaptive Stimulation Scheduling** in the left column.]

But patients do not respond the same way. Some maintain strong coupling, while others habituate and lose synchronization during the session. So fixed scheduling can overstimulate some patients and miss the therapeutic window in others.

That is the problem I solved.

[Move slightly right and point to **Materials** and the dataset overview figure.]

I analyzed EEG from 35 subjects, using 7 frontal channels at 250 Hz, with subject-level train, validation, and test splits.

[Move to **System Architecture**, top center-left.]

The system has two stages. First, it estimates current phase-amplitude coupling, or PAC, from EEG. PAC measures how strongly 40 Hz gamma amplitude locks to theta phase, which tells us whether entrainment is holding.

[Point to **Stage 1: Architecture Decision for Static PAC Estimation**.]

I tested eight static architectures for this step, and they all plateaued at essentially the same result, R^2 equals 0.287. That told me something important: a single EEG snapshot did not contain enough information to make a strong instantaneous PAC prediction.

So I changed the question.

[Point lower in **System Architecture** to **Stage 2: Temporal Prediction; Causal TCN**.]

Instead of predicting PAC from one moment, I used 20 seconds of recent history to predict PAC 5 seconds ahead with a temporal convolutional network.

[Point to the feature reduction visuals in the middle column.]

I also found that my broader feature set was hurting generalization. When I removed 61 spectral features and kept the 12 features that tracked response trajectory and stimulation context, temporal prediction improved from negative 0.025 to 0.606.

[Move down to **Data Analysis** and point to the horizon figure.]

This figure explains why the 5-second forecast matters. At 1 to 2 seconds, simple baselines work because the brain state has barely changed. But at longer horizons, those baselines collapse, and prediction becomes useful for proactive control.

Now the important part is what that means clinically.

[Move to the **Results / Findings** column, top right. Point to the main controller table.]

On all 35 subjects' real EEG, the predictive controller achieved 72.1% alignment versus 64.5% for reactive control. It targeted 82.6% of low-PAC windows, versus 51.7% for reactive control, and it reached 91% of the oracle benchmark.

[Point to **Figure 13: Controller Performance Comparison**.]

So the predictive system was not just more accurate. It was also better at delivering stimulation to the moments when the brain actually needed it.

[Point to **Result 2: Every Patient Benefits** scatter plot.]

This was also consistent at the patient level. All 35 subjects benefited, including the held-out test subjects.

[Point to **Result 3: Advantage Increases with Fatigue**.]

And the advantage grew as fatigue worsened, which is important because habituation is exactly when personalization matters most.

[Point to the **Summary of Key Results** table, then the **Conclusions** box.]

So the main contribution of the project is that it turns 40 Hz therapy from a fixed timer into a personalized, physiology-guided system.

The main limitation is that this is still offline replay on recorded EEG, not a live closed-loop trial where stimulation changes the future brain state.

[Point to **Future Directions**.]

So the next step is a live crossover study comparing fixed and adaptive timing in real time.

[Step back slightly.]

In one sentence: I built a system that predicts when an Alzheimer's patient's brain is about to lose response to 40 Hz therapy, so stimulation can be timed to when it is actually needed.

What would you like to go deeper on?

---

## Delivery Notes

- Keep the pace direct and calm.
- Use the poster to do part of the explaining for you.
- Pause briefly before the Results column so the judge feels the transition.
- If interrupted, stop immediately and answer. The script is modular.
