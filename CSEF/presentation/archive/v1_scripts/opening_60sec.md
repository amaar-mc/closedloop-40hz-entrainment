# 60-Second Opening

When a judge walks up and says "Tell me about your project." You have about 60 seconds before they jump in with a question. That's fine -- let them. This is a conversation starter, not a speech.

---

Hi, I'm Amaar. Thanks for coming by.

So -- 55 million people worldwide have Alzheimer's, and one of the most promising non-drug treatments is 40 hertz sound therapy. You play a rhythmic tone and it drives the brain's gamma waves to synchronize, which activates microglia and triggers glymphatic clearance of amyloid plaques. The science is solid -- Iaccarino 2016 in Nature showed 40 to 50 percent amyloid reduction in mice, and Murdock 2024 identified the actual clearance mechanism through aquaporin-4 channels.

*[gesture toward Background/Introduction]*

But here's what bothered me. Every clinical protocol -- including Cognito's ongoing 670-patient Phase 3 trial -- delivers this therapy on a fixed timer. Forty seconds on, twenty off, for an hour. Same schedule for every patient. And when I looked at actual EEG from 35 elderly subjects, about half of them habituate within minutes. Their brains tune out the sound. A fixed schedule has no way to handle that.

*[gesture toward Figure 2: Fixed vs. Adaptive]*

So I built a system that predicts when a patient's brain is about to lose its response -- five seconds before it happens -- and times stimulation to the moments it actually matters. On all 35 patients, it matched the right action to the right moment 72 percent of the time, versus 64 percent for a system that can only react to what's already happened. And every single patient benefited.

*[pause, eye contact]*

Happy to go into any part of it.

---

## Timing breakdown (~150 words/min)

| Section | Words | Time |
|---------|-------|------|
| Greeting | 8 | 3s |
| Problem + science | 62 | 25s |
| The gap + habituation | 55 | 22s |
| What I built + result | 52 | 21s |
| Invitation | 7 | 3s |
| **Total** | **~184** | **~74s** |

Slightly over 60s. That's deliberate -- judges will interrupt somewhere in the gap/habituation section with a question, which is ideal. If they don't interrupt, you land the result naturally.

## Key numbers in this script
- 55 million: global Alzheimer's patients (WHO 2023)
- 40-50%: amyloid reduction from Iaccarino 2016
- 670 patients: Cognito HOPE trial (Phase 3)
- 35 subjects: your dataset (OpenNeuro ds005048)
- 5 seconds: prediction horizon
- 72% vs 64%: alignment, TCN vs. reactive
- 35/35: every patient benefited

## If they interrupt early (after ~20 seconds)
You've planted: the disease, the therapy mechanism, and the fact that current protocols are blind. That's enough. Answer their question, then weave back to your result when there's an opening.

## What this does NOT mention (hold for Q&A)
- The 8-architecture search and 0.287 ceiling (say it if asked about methodology)
- The feature discovery / spectral drop (say it if asked what you discovered)
- The TCN architecture details (say it if asked how the prediction works)
- Statistical methods (say it if asked about validation rigor)
- Specific model parameters (say it if asked about technical details)
- Product/commercialization (say it if asked about future directions or real-world use)
