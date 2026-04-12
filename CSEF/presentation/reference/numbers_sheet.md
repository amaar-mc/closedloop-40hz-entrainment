# Numbers Sheet: v2 Medicine and Physiology Focus

Know these cold. If you forget a minor number, that is fine. Do not forget the story numbers.

---

## 1. Disease and Field

- Alzheimer's disease worldwide: 55 million
- Alzheimer's disease in the U.S.: 6.9 million
- Iaccarino 2016 amyloid reduction in mice: 40 to 50%
- Cognito Phase 3 trial size: 670 patients
- Approximate non-responder rate in the literature: about 30%

## 2. Dataset

- Dataset: OpenNeuro ds005048
- Subjects: 35
- Breakdown: 17 AD, 6 MCI, 10 healthy controls, 2 unspecified
- EEG channels used: 7 frontal channels
- Sampling rate: 250 Hz
- Train / validation / test split by subject: 24 / 5 / 6

## 3. The Pivot Story

- Static architectures tested: 8
- Static ceiling: R^2 = 0.287
- Lookback used for forecasting: 20 seconds
- Prediction horizon: 5 seconds
- Final feature set: 12 features
- On-board temporal result after feature reduction: R^2 = 0.606
- Multi-seed forecasting result from the wider project record: R^2 = 0.606 +/- 0.032

## 4. Main Results

- Alignment: 72.1% predictive vs 64.5% reactive
- Low-PAC targeting: 82.6% predictive vs 51.7% reactive
- PAC gap: 30.5 vs 21.1
- Subjects benefiting: 35 out of 35
- Oracle proximity: 91%

## 5. Deployment and Next Step

- Inference time: under 50 ms
- Consumer hardware cost: about $250
- Main limitation: offline replay, not live closed-loop validation
- Next step: live crossover clinical study

---

## The Five Numbers That Must Never Be Missed

If you only remember five things, remember these:

1. 55 million people with Alzheimer's worldwide
2. 35 subjects in the dataset
3. 8 architectures all hit the same ceiling
4. 72.1% vs 64.5% alignment
5. 35 out of 35 subjects benefited

## Fast Recall Line

"55 million, 35 subjects, 8 models hit the wall, 5-second prediction, 72 versus 64, and 35 out of 35 improved."
