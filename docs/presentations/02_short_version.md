# Accessible Presentation -- "The Elevator That Can Expand"

**Core: 2 minutes. Expandable to 3-4 if the judge is engaged and not interrupting.**
**For any judge. Tells the story first, invites depth second.**

---

Hi, I'm Amaar Chughtai. It's really nice to meet you. Would you like me to give you an overview of my project?

*[Wait for them. Then begin.]*

So, this project started with my grandmother. She had dementia, and watching her go through that -- losing memories, losing recognition of the people she loved -- it made me want to understand what's actually happening in the brain and whether there's anything we can do about it.

That's how I found out about 40 hertz entrainment. The idea is that when you play a rhythmic sound at 40 beats per second, the brain's electrical waves synchronize to it -- they lock on to that rhythm. And when that synchronization happens, it activates the brain's own cleanup system, which starts clearing the toxic protein buildups that cause Alzheimer's. This has been shown in animal studies and it's now being tested in human clinical trials.

*[Gesture toward Figure 1]*

The problem is that right now, every patient receives this therapy on the exact same fixed schedule -- 40 seconds of sound, 20 seconds of silence, over and over for an hour. Regardless of whether their brain is actually responding. And when I analyzed real EEG data from 35 dementia patients, I found something that really stuck with me: about half of them habituate -- their brains gradually tune out the sound, like how you stop noticing a ticking clock -- while the other half actually get *more* responsive. A one-size-fits-all schedule can't serve both groups.

*[Gesture toward Figure 3: System Architecture]*

So I built a system that listens to the brain and adapts. It measures how well the brain is synchronizing in real time using a metric called phase-amplitude coupling, and then -- this is the key part -- it *predicts* where that synchronization is headed 5 seconds into the future. Not just reacting after the brain has already lost sync, but anticipating the drop before it happens and stimulating proactively.

*[Point to Figure 5: Horizon Sweep]*

The reason 5 seconds matters is shown in this chart. I tested how well different methods predict brain state at different time horizons. At 1 to 2 seconds ahead, simple approaches work fine -- the brain barely changes. But at 5 seconds, every simple method fails completely. My model is the only one that still gives useful predictions at that range, and that's exactly the lead time a controller needs to actually make a difference.

*[Point to Result 1 table]*

When I tested the full system on all 35 patients' actual brain recordings, the predictive controller caught 83% of the moments where the brain genuinely needed stimulation. The reactive approach -- which waits for a drop before responding -- only caught 52%. And every single patient -- all 35 out of 35 -- did better with my system. Including patients the model had never seen before.

*[Pause. Make eye contact.]*

The main limitation is that this is tested on recorded data, not yet in a live clinical setting. That's the next step. But the model runs fast enough for real time, so the technology is ready -- it's the clinical validation that would come next.

Is there anything you'd like me to go deeper on?

---

## Expansion modules (use when the judge asks or leans in)

**If they ask "how does the prediction model actually work?":**

> So there are actually two models working together. The first one, called EEGNet, reads a 2-second window of raw brainwaves and estimates how synchronized the brain is right now. It's tiny -- only about 1,500 parameters. I actually tested six different architectures for this job, from 1,500 parameters up to 2 million, and they all performed identically. That told me the information ceiling is in the data itself, not the model -- which was a really important finding because it told me I needed to change my approach entirely.

> So instead of trying to predict better from a single snapshot, I built a second model -- a Temporal Convolutional Network -- that looks at the last 20 seconds of brain history and forecasts 5 seconds ahead. It's designed so it can only look backward in time, never forward. That's an architectural guarantee, not just a training rule -- important because in a real hospital, you don't have the future yet.

**If they ask "what's phase-amplitude coupling?":**

> It's a way of measuring how well two brain rhythms are coordinated. The brain has a slow rhythm called theta -- around 4 to 8 beats per second -- and a fast rhythm called gamma at 40 hertz, which is what the stimulus targets. When the therapy is working, the fast rhythm's strength becomes tightly locked to the slow rhythm's timing -- they move together. PAC measures how tight that lock is. High PAC means the brain is entrained and the therapy is having its effect. Low PAC means the brain has fallen out of sync.

**If they ask "how do you know the model isn't just memorizing?":**

> Three safeguards. First, no patient's data appears in more than one split -- the 6 test patients were completely separated from training. Second, the model architecture physically prevents it from seeing future data. And third, I ran a sanity check where I shuffled all the labels randomly and retrained. The model learned absolutely nothing -- R-squared dropped to negative 0.33. That confirms it's finding real patterns in the brain signals, not artifacts of the data processing.

**If they ask "did you run into problems during the project?":**

> Absolutely. One of the early models I tested -- called SpecTempNet -- appeared to get an R-squared of 0.69, which was way higher than everything else. That was suspicious. When I dug into it, I found that the input features accidentally included a version of the PAC score itself -- so the model was essentially being given the answer. Once I removed that, performance dropped right back down to the same level as everything else. That was actually a pivotal moment in the project because it taught me to be extremely careful about what information flows into the model, and it reinforced that the 0.287 ceiling was real. That's what pushed me to completely rethink the approach and move to temporal prediction instead of trying to beat the ceiling from a single window.

**If they ask "could this actually help patients?":**

> The core model runs in about 2 milliseconds on a regular laptop, so speed isn't the issue. The real pathway would be a crossover clinical study -- same patients receive both fixed and adaptive stimulation on different days, measuring whether the adaptive approach maintains better brain synchronization with less total stimulation time. If it does, that could mean shorter, less burdensome therapy sessions that are actually more effective. The long-term vision is a wearable device that monitors brain activity and delivers personalized stimulation -- but that's further out and would require regulatory approval.

**If they ask "how long did this take / how much did you do yourself?":**

> This has been about four months of focused work. I wrote all the code myself in Python using PyTorch -- everything from loading the raw EEG data, computing the signal processing, building and training both models, the controller logic, and all the statistical validation. I ran it on my own laptop using Apple Silicon, no cloud GPUs. I used AI tools as a learning resource for understanding concepts -- similar to using a textbook or asking a professor -- but every design decision, every architecture choice, and every scientific judgment call was mine. The most important decisions -- like recognizing the data ceiling, pivoting to temporal prediction, and choosing which validation approach to trust -- those came from me sitting with the data and thinking through what it was telling me.

---

## What this script implicitly addresses for the judge

| Judging criterion | Where it's addressed |
|---|---|
| **Research Problem** (10 pts) | Grandmother = personal stake; fixed schedule waste = practical need; 5-second lead time = constraint |
| **Design & Methodology** (15 pts) | Explored 6 architectures (expansion module); identified the data ceiling; pivoted to temporal approach |
| **Execution & Testing** (20 pts) | 35 patients, all real EEG, multiple controllers compared, statistical significance, fatigue robustness |
| **Creativity** (20 pts) | "Nobody was trying to predict ahead of time"; the architecture marathon as a method to prove a ceiling; the horizon sweep concept |
| **Presentation - Interview** (25 pts) | Conversational, responds to judge's direction, honest about limitations, shows understanding through explanation not just recitation |

| Judge mindset question | Where it's addressed |
|---|---|
| How much did you do yourself? | Expansion module ready; first-person throughout; "I found something that stuck with me" |
| How deeply do you understand it? | Explains PAC intuitively, knows why 0.25 is useful, can describe causal guarantees |
| Did you discover errors? | SpecTempNet leakage story (expansion module) |
| Do conclusions follow from data? | "83% vs 52%" tied directly to the replay; "all 35 out of 35" |
| How new or different is this? | "Not just reacting... anticipating the drop before it happens" |
| Is the work complete? | Honest: "tested on recorded data, not yet live" -- shows maturity |
| What's next? | Live validation, crossover study, wearable device pathway |
