# Simplified Presentation Script

**For: General judges, non-technical judges, business/community judges**
**When to use: The judge seems unfamiliar with ML/neuroscience, asks broad questions like "so what does your project do?", or introduces themselves as a businessperson, teacher, parent, etc.**
**Time: ~3.5 minutes spoken naturally**

This version explains the same project with intuition and analogies instead of jargon. Every technical concept is translated into plain language. You still sound smart -- you just sound accessible.

---

## THE SCRIPT

_[Judge approaches your poster. Stand to the side. Smile. Shake their hand.]_

Hi, I'm Amaar. It's great to meet you. Thank you for stopping by.

_[If they say "tell me about your project," go. If they're reading the poster title, give them a moment, then start.]_

So, my project is about making a brain therapy for Alzheimer's disease smarter. Let me show you what I mean.

_[Gesture toward Introduction, top-left]_

Alzheimer's affects over 55 million people worldwide. There's no cure. But researchers have discovered something promising: if you play a specific sound -- a clicking sound at 40 beats per second -- the brain's electrical waves synchronize to it. And when that happens, it activates the brain's cleanup system. Immune cells start clearing out the toxic proteins that cause Alzheimer's. This has been shown in animal studies and is now being tested in human clinical trials.

So the therapy exists. The problem is how it's delivered.

_[Point to Figure 1: Fixed vs. Adaptive diagram]_

Right now, every patient gets the exact same schedule: 40 seconds of sound on, 20 seconds off, repeating for an hour. Same timing, every patient, every session.

But brains are different. When I looked at data from 35 dementia patients, I found that about half of them gradually stop responding -- their brains tune out the sound, the way you might stop noticing a ticking clock. But the other half actually get _more_ responsive over time. A fixed schedule can't handle that. It's like watering a garden on a timer -- some plants are drowning while others are drying out.

So I asked: what if the system could _listen_ to the brain and deliver stimulation only when the brain actually needs it?

_[Move to Model Approach column]_

To do that, I needed to solve two problems.

_[Point to Figure 3: System Architecture Flowchart]_

First, I needed a way to measure, in real time, how well the brain is synchronizing to the sound. There's a metric for this called phase-amplitude coupling, or PAC. Think of it as a score: high PAC means the brain is locked on and the therapy is working, low PAC means the brain has lost sync and isn't benefiting.

Second -- and this is the key part -- I needed to _predict_ that score into the future. Not just know where the brain is now, but know where it's going to be 5 seconds from now. That's the difference between a thermostat that turns on the heat after you're already cold, versus one that sees the temperature dropping and turns it on before you feel it.

_[Point to the EEGNet vs TCN comparison table]_

So I built two models. The first one, called EEGNet, reads the raw brainwaves and estimates the current coupling score. It's tiny -- only about 1,500 parameters -- and runs in real time. The second one, called a Causal TCN, looks at the last 20 seconds of brain activity and predicts what the coupling score will be 5 seconds from now. Together, they feed into a controller that decides: play the sound, or give the brain a rest.

_[Point to Figure 5: Prediction Horizon Sweep]_

This chart is probably the most important thing on the poster. I tested how well different prediction methods work at different time horizons. At 1 to 2 seconds ahead, the brain barely changes -- you can just say "it'll be the same as now" and you're mostly right. But at 5 seconds, that simple approach completely fails. My model is the only one that still gives useful predictions at that range. And 5 seconds is exactly how far ahead the controller needs to see to make good decisions.

_[Move to Results column. Point to Result 1 table.]_

So does it actually work? I tested the system on all 35 patients' real brain recordings.

The current clinical approach -- the fixed schedule -- only makes the right call about 45% of the time. A reactive approach, which waits until coupling drops and then responds, gets up to about 65%. My predictive system hits 72%.

But here's the number that matters most: when I look specifically at the moments where the brain genuinely needed help -- where coupling was fading -- my system caught 83% of those moments. The reactive approach only caught 52%. That's a 60% improvement in getting stimulation to the patients who need it, when they need it.

_[Point to Figure 9: Per-Subject scatter plot]_

And this wasn't just an average. Every single patient -- all 35 out of 35 -- did better with my system than with the reactive approach. Including 6 patients the model had never seen before during training.

_[Point to the Result 3 fatigue table]_

The advantage also gets bigger for patients who habituate more. The worse the brain's fatigue, the more the system helps -- which is exactly when you need personalization the most.

_[Step back. Eye contact.]_

I want to be honest about the limitation: I tested this by replaying recorded brain data, not in a live hospital setting. The system makes decisions on real patient data, but it can't yet observe how the brain responds to those decisions in real time. That's the next step. The model is fast enough -- it runs in about 2 milliseconds -- so the technology isn't the barrier. It's getting access to a real-time clinical setup.

_[Pause. Let them respond.]_

---

## TIMING

| Section                                      | Time              |
| -------------------------------------------- | ----------------- |
| Greeting + intro                             | 10 sec            |
| The therapy + the problem                    | 35 sec            |
| What I built: two models + controller        | 40 sec            |
| Horizon sweep (the key chart)                | 30 sec            |
| Results: 72% alignment, 83% targeting, 35/35 | 45 sec            |
| Fatigue scaling                              | 10 sec            |
| Limitation + next steps                      | 15 sec            |
| **Total**                                    | **~3 min 25 sec** |

---

## ANALOGIES TO HAVE READY (for follow-up questions)

Use these if the judge looks confused or asks you to explain something differently:

**PAC (phase-amplitude coupling):**
"Think of the theta wave as a slow drumbeat and the gamma wave as a fast melody riding on top. PAC measures how tightly the melody follows the beat. High PAC means they're in sync -- the brain is locked on."

**Why prediction matters vs. reaction:**
"It's like the difference between a fire alarm that goes off _during_ the fire and one that goes off when it _smells_ smoke. By the time reactive control detects a drop, you've already lost the therapeutic window. Predicting 5 seconds ahead lets you intervene before the drop."

**The data ceiling (6 architectures converging):**
"Imagine six different people all trying to guess your age from the same blurry photo. They might all guess slightly different numbers, but they all land around the same answer -- because the photo only contains so much information. That's what happened with my models. The EEG snapshot only has so much signal."

**Causal (no future leakage):**
"The model can only look backward in time, never forward. Like driving a car using only the rearview mirror and what's out the windshield right now -- you can't peek at what's around the next corner."

**Hedges' g / effect size (if asked about statistics):**
"Effect size tells you how _big_ a difference is, not just whether it exists. A g of 1.31 means the two approaches are separated by more than one standard deviation. That's considered a large, clinically meaningful difference."

**35 out of 35:**
"The probability of every single patient doing better by pure chance is less than one in 34 billion. It's not a fluke."

---

## IF THE JUDGE GETS INTERESTED AND ASKS FOR MORE DEPTH

You can smoothly escalate:

**"How does the TCN actually work?"**

> It uses something called dilated causal convolutions. Each layer looks at the data with wider and wider gaps -- like zooming out on a timeline. The first layer sees individual seconds, the second sees pairs of seconds, the fourth sees 8-second chunks. By stacking four layers, the network can consider 20 seconds of brain history while staying small enough to run in real time. And the "causal" part means it can only look at past data -- it never peeks at the future, which would be cheating.

**"What exactly are the 73 features?"**

> 61 are spectral power features -- how much energy the brain has at different frequencies across 7 channels. 7 are derived from the PAC score itself -- the current value plus moving averages and trends. And 5 capture the stimulation context -- whether the sound is currently on or off, how long it's been in that state, and where we are in the session.

**"How did you make sure the model isn't cheating?"**

> Three safeguards. First, subject-level splits -- the 6 test patients were completely separate from training. Second, the model architecture physically cannot see future data. Third, I ran a shuffle test: I randomized the labels and retrained. The model learned nothing -- R-squared dropped to negative 0.33. That confirms it's picking up real brain patterns, not artifacts.

**"Could this actually be used on real patients?"**

> The model runs in 2 milliseconds on a laptop, so speed isn't an issue. The real challenges are regulatory -- this would need clinical validation trials and FDA clearance as a medical device. But the engineering foundation is here. The immediate next step would be a crossover study: same patients get both fixed and adaptive sessions on different days, with real-time EEG monitoring.
