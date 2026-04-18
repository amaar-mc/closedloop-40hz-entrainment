# 2-Minute Overview

This is the main interview opener for CSEF Medicine and Physiology judges.

Goal: clear medical impact, clear problem, clear result.

---

Hi, I'm Amaar. Thanks for stopping by.

Alzheimer's disease affects more than 55 million people worldwide, and one promising non-drug approach is 40 Hz auditory stimulation, where sound is pulsed 40 times per second. That stimulation improves synchronization between theta and gamma rhythms and has been linked to amyloid clearance through microglial and glymphatic pathways.

The problem is that it is usually delivered on a fixed schedule, typically 40 seconds on and 20 seconds off, no matter how the patient's brain is responding.

After analyzing EEG from 35 subjects, I found that response is highly variable. Some patients maintain strong coupling, while others habituate and lose synchronization during the session. So fixed scheduling can overstimulate some patients and miss the therapeutic window in others.

To solve that, I built a two-stage closed-loop system. First, it estimates current phase-amplitude coupling, or PAC, from EEG. PAC measures how strongly 40 Hz gamma amplitude locks to theta phase, which tells us whether entrainment is holding. Then a temporal convolutional network uses 20 seconds of recent history to predict PAC 5 seconds ahead, so the controller can stimulate proactively instead of reactively.

I arrived at that solution after testing eight static neural network architectures. They all plateaued at the same accuracy, R^2 equals 0.287, which showed that a single EEG snapshot did not contain enough information to make a strong instantaneous PAC prediction. I then shifted to short-term forecasting, and after reducing the model to 12 response-trajectory and stimulation-context features, the temporal model reached R^2 equals 0.606.

On all 35 subjects, the predictive controller achieved 72.1% alignment versus 64.5% for reactive control and improved low-PAC targeting from 51.7% to 82.6%. All 35 subjects benefited.

So the clinical message is simple: instead of giving 40 Hz therapy on a blind timer, we can personalize when to stimulate based on the patient's actual brain state.

The main limitation is that this is offline replay on recorded EEG, not yet a live closed-loop trial. The next step is live crossover validation.

Happy to go deeper on any part of it.

---

## What This Script Must Do

- establish disease impact
- explain why 40 Hz matters medically
- show the failure of fixed schedules
- state exactly what you built
- show how you arrived at the solution
- land on the main results
- end with limitation plus next step
