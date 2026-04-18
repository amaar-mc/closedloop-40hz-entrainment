# CSEF v2: Medicine and Physiology Focus Bundle

This folder is the reduced memorization set for tomorrow.

It is optimized for the judging pattern described by CSEF and Society for Science:

- judges pre-read your presentation
- interview quality matters heavily
- they care about basic science, interpretation, limitations, independence, impact, and future direction
- Medicine and Physiology judges will care more about the disease, the therapy, the biomarker, and the clinical meaning than about deep model architecture

## What To Memorize

In order:

1. `scripts/v2_2min_medphys_overview.md`
2. `scripts/v2_3to4min_medphys_boardwalk.md`
3. `reference/v2_numbers_sheet.md`
4. `reference/v2_danger_zones.md`
5. `reference/v2_key_citations.md`

Use the memorization guides only to structure recall:

- `memorization/v2_2min_map.md`
- `memorization/v2_3to4min_boardwalk_map.md`
- `memorization/v2_reference_map.md`

## Design Principles For This Version

- Start with impact and why the problem matters medically.
- Explain fixed-schedule 40 Hz therapy in plain clinical language.
- Frame the computational work as a tool for solving a physiological timing problem.
- Keep the pivot story: static snapshot ceiling -> predict trajectory instead.
- Use exact board numbers where they matter.
- Follow the physical poster flow so your hand movements support the story.
- End with an honest limitation and a credible clinical next step.

## Main Message To Leave With Judges

"I built a system that predicts when an Alzheimer's patient's brain is about to lose response to 40 Hz therapy, so stimulation can be timed to when it is actually needed, and it improved decision quality on all 35 patients in the dataset."

## What To Hold For Q&A

Do not volunteer unless asked:

- dilation factors
- parameter counts beyond the basic EEGNet ceiling story
- full feature list
- exact loss functions
- deep implementation details

Do volunteer:

- why 40 Hz matters biologically
- why fixed schedules are clinically weak
- why PAC is a meaningful biomarker
- why 5 seconds matters
- what you discovered
- what the main limitation is
- what the next clinical step is
