# Deep Technical Presentation Script

**For: Judges with science/engineering/CS backgrounds**
**When to use: The judge introduces themselves as a professor, engineer, researcher, or asks a sharp technical question early on**
**Time: ~4.5 minutes spoken naturally**

Read this aloud until the structure is second nature. Then memorize it word-for-word. When you present, it should sound like you're explaining it to a smart colleague, not reading off a page.

---

## THE SCRIPT

*[Judge approaches your poster. Stand to the side. Smile. Shake their hand.]*

Hi, I'm Amaar. It's a pleasure to meet you. Thank you for taking the time to come by.

*[Brief pause. Let them settle. If they say "tell me about your project," go. If they're reading the title, give them a second, then start.]*

So my project is a personalized deep learning system for Alzheimer's therapy. Let me walk you through it.

*[Gesture toward Introduction, top-left of poster]*

There's a therapy called 40 Hz auditory entrainment. You play a clicking sound at 40 hertz, and the brain's gamma oscillations synchronize to it. In mouse models, this activates microglia -- the brain's immune cells -- which clear amyloid-beta plaques, one of the main drivers of Alzheimer's. This has been shown in humans too. A 2024 study showed it enhances default mode network connectivity in dementia patients.

The therapy works. The problem is delivery. Every clinical protocol right now uses a fixed schedule: 40 seconds of stimulation, 20 seconds of rest, repeating for an hour. Same timing for every patient.

*[Point to Figure 1: Fixed vs. Adaptive diagram]*

But when I analyzed EEG from 35 dementia patients, I found that roughly half of them habituate -- their brains progressively tune out the stimulus -- while the other half actually facilitate, getting stronger over time. At the population level there's no net trend, the p-value is 0.54, but the individual variability is massive. A fixed schedule serves neither group well. It wastes stimulation when coupling is already strong and misses windows when it's fading.

So I built a system that predicts when a patient's brain is about to lose entrainment, 5 seconds before it happens, and adapts stimulation proactively.

*[Move to Model Approach column, center-left]*

The system has two stages. Stage one is estimating current entrainment from raw EEG. The biomarker I use is phase-amplitude coupling -- PAC -- which quantifies how strongly gamma amplitude at 40 hertz locks to the phase of theta oscillations between 4 and 8 hertz. I compute it using Tort's Modulation Index over 2-second windows.

*[Point to the Stage 1 architecture table]*

For the estimation model, I ran what I call an architecture marathon. I tested six architectures ranging from 1,457 parameters up to 2 million -- EEGNet, SpecTempNet, a Vision Transformer variant, Ridge regression, ATCNet, and a large EEGNet. Every single one converged to R-squared 0.287. The simplest models matched the most complex ones. The 2-million-parameter ViT-TCNet actually scored *lower* than the 1,457-parameter EEGNet due to overfitting.

That convergence tells you 0.287 is a data ceiling, not a model limitation. Seven frontal channels at 250 hertz in 2-second windows simply contain that much information about epoch-level PAC. So I chose EEGNet -- matches the ceiling with the fewest parameters, fast enough for real-time inference on embedded hardware.

*[Point to Stage 2: the EEGNet vs TCN comparison table]*

Stage two is the core contribution. Since no single-window architecture could break through the ceiling, I shifted the question: instead of predicting PAC *better* from one snapshot, predict it *further into the future* from a sequence of snapshots. The Causal TCN takes 20 timesteps of history -- 73 features each, including 61 spectral power features, 7 PAC-derived features like moving averages and trends, and 5 stimulation context features -- and outputs predicted PAC 5 seconds ahead.

The architecture uses dilated causal convolutions with dilation factors 1, 2, 4, and 8, giving a 31-step receptive field. Crucially, it's causally constrained -- left-only padding means the network architecturally cannot access future data. In deployment, it only sees what a real-time system would actually have.

*[Point to Figure 5: Prediction Horizon Sweep]*

This figure is the intellectual centerpiece of the project. I trained separate models at horizons from 1 to 10 seconds. At 1 to 2 seconds, PAC is autocorrelated enough that persistence -- just repeating the last value -- gets R-squared of 0.81. You don't need a neural network.

But at 5 seconds, persistence collapses to negative R-squared. Ridge regression does the same. Negative R-squared means worse than predicting the mean. The TCN holds at 0.25 -- a plus-0.5 margin over the best baseline. And this margin is stable out to 10 seconds.

Five to ten seconds is exactly the operationally relevant horizon. A controller needs that much lead time to schedule stimulation before the brain loses coupling. The TCN is the only model providing useful signal at the range that matters for proactive control.

*[Move to Results column, right side of poster. Point to Result 1 table.]*

For validation, I replayed the TCN controller on all 35 subjects' actual EEG recordings. Not simulation -- real brain data, with counterfactual decisions. I compared against fixed schedule, reactive threshold, a PI controller, and a theoretical alignment oracle with perfect future knowledge.

The TCN achieved 72.1% epoch alignment versus 64.5% for reactive -- Hedges' g of 1.31, p less than 0.001. But the more important metric is low-PAC targeting: of all windows where the brain genuinely needed stimulation, the TCN caught 82.6%. Reactive caught 51.7%. That's Hedges' g of 4.47 -- a very large effect. And the TCN's PAC targeting gap reaches 92% of the oracle's theoretical maximum.

*[Point to Figure 9: Per-Subject Utility scatter plot]*

35 out of 35 patients showed higher clinical utility with TCN versus reactive. All of them. Including 6 held-out test subjects the model never saw during training. Binomial p less than 0.001.

*[Point to Result 3 fatigue table]*

And in simulation, the adaptive advantage scales with neural fatigue severity -- from plus 9% at no fatigue to plus 11.2% at severe -- with Hedges' g ranging from 1.7 to 2.4. I also tested across four fundamentally different fatigue model assumptions -- exponential decay, step function, heterogeneous population, and synaptic saturation -- and the advantage holds across all four.

*[Step back slightly. Make eye contact.]*

The main limitation I want to be transparent about: this is offline replay on recorded EEG, not live closed-loop streaming. The system makes decisions on real brain data, but it can't observe the brain's response to those decisions. That's the next step -- real-time validation. The model runs in under 2 milliseconds, so latency isn't the barrier. The barrier is access to a live EEG streaming setup and a clinical crossover protocol.

*[Pause. Let them respond.]*

---

## TIMING

| Section | Time |
|---|---|
| Greeting + intro | 10 sec |
| Problem: 40 Hz therapy + fixed schedule gap | 40 sec |
| Stage 1: Architecture marathon + data ceiling | 40 sec |
| Stage 2: TCN architecture + features | 35 sec |
| Horizon sweep | 35 sec |
| Results: controller comparison + 35/35 + fatigue | 50 sec |
| Limitation + next steps | 20 sec |
| **Total** | **~4 min 10 sec** |

---

## IF YOU NEED TO EXPAND (judge is nodding, not interrupting, you have time)

**After the architecture marathon:** "One of the models, SpecTempNet, initially appeared to hit R-squared 0.69, which was suspiciously high. I traced it to PAC features leaking into the input -- the model was essentially being given a version of the answer. Once I removed that, it dropped to 0.236, consistent with everything else. That taught me to be extremely careful about what information flows into the model."

**After the horizon sweep:** "0.25 might seem low in absolute terms. But the controller doesn't need the exact PAC value -- it needs direction. Is coupling trending down? That's enough to decide: stimulate now, or wait. The proof is downstream: 72% alignment and 83% therapeutic targeting from a 0.25 prediction."

**After the results:** "The fixed schedule actually targets stimulation in the *wrong direction* -- its PAC gap is negative 6.6, meaning it stimulates more during high-PAC periods than low-PAC periods. It's not just suboptimal, it's anti-correlated with therapeutic need."

**After the limitation:** "Beyond real-time validation, I'd want to extend to multi-biomarker control -- combining PAC with spectral power and connectivity -- and potentially replace the heuristic controller thresholds with reinforcement learning."

---

## KEY TECHNICAL TERMS TO DEFINE ONLY IF ASKED

Don't volunteer definitions during the presentation -- it slows you down. But have them ready:

- **Phase-amplitude coupling (PAC):** How strongly the amplitude of fast gamma oscillations (38-42 Hz) is modulated by the phase of slow theta oscillations (4-8 Hz). Computed via Tort's Modulation Index using the Hilbert transform.
- **Modulation Index:** Kullback-Leibler divergence between the observed gamma amplitude distribution across theta phase bins and a uniform distribution. Ranges 0 to 1.
- **Causal convolution:** Convolution that uses left-only padding so the output at time t depends only on inputs at times t and earlier. Prevents future information leakage.
- **Dilated convolution:** Convolution with gaps between filter taps. Dilation d=4 means the filter skips 3 steps between each tap. Exponentially increases receptive field without adding parameters.
- **Hedges' g:** Bias-corrected effect size measure. Like Cohen's d but adjusted for small samples. 0.2 = small, 0.5 = medium, 0.8 = large. Your main result is 1.31 = large.
- **Wilcoxon signed-rank:** Non-parametric paired test. Used instead of t-test because you can't assume normality with 35 subjects.
