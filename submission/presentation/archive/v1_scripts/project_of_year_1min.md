# 1-Minute Project of the Year Synopsis

If you win First Place in Medicine & Physiology, a panel representative delivers this synopsis to the Project of the Year judges. The 1-minute limit is strictly enforced. These judges are from ALL categories -- physicists, chemists, engineers, biologists -- so it must be accessible.

Note: the panel representative (not you) may deliver this. Write it so anyone can read it and convey the core achievement. But also memorize it yourself in case you present.

---

This project addresses a fundamental flaw in how 40 hertz auditory therapy is delivered to Alzheimer's patients. Current protocols -- including the 670-patient Cognito Phase 3 trial -- use a fixed schedule: same timing for every patient, regardless of whether the brain is responding. Analysis of EEG from 35 elderly subjects showed that half habituate within minutes.

Amaar built a two-stage deep learning system that first measures brain synchronization in real time using phase-amplitude coupling, then forecasts where that synchronization is headed five seconds into the future. A key discovery was that dropping 61 spectral EEG features -- which encoded individual brain anatomy, not generalizable dynamics -- and keeping only 12 PAC-trajectory features raised prediction accuracy from R-squared near zero to 0.60. At this horizon, every baseline method fails completely.

When tested on all 35 patients' real brain recordings, the predictive controller matched stimulation to need 72 percent of the time versus 64 percent for reactive control, reaching 91 percent of the theoretical maximum. All 35 patients benefited. The system runs on a $200 consumer headset and a laptop -- deployable for home use.

---

## Word count: ~172 words = ~69 seconds at 150 wpm

## What this hits (POTY criteria from handbook p.14)

- **Original thought:** First system to predict brain entrainment loss before it happens
- **Scientific impact:** Feature ablation discovery, architectural convergence proof, horizon sweep methodology
- **Societal impact:** 55M Alzheimer's patients globally, deployable on consumer hardware
- **Worldly application:** $200 headset + laptop, no clinical hardware needed, ready for pilot studies
