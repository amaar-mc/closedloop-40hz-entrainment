// Editable PowerPoint version of the URTC 2026 lightning talk (ID-1269).
// Text is real text, figures are 300-dpi images from make_figures_v2.py, and boxes whose text is
// "EQ_NAME@size" become native PowerPoint equations afterwards (inject_math.py).
//   node build_native.js <fig dir> <SPEAKER_SCRIPT.md> <out.pptx>
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const [FIG, SCRIPT, OUT] = process.argv.slice(2);
const fig = (name) => path.join(FIG, `${name}.png`);

// Palette from the author's earlier posters.
const TITLE = '235078';
const INK = '222222';
const INK2 = '444444';
const GRAY = '666666';
const FONT = 'Arial';

// ---------------------------------------------------------------------------------------------
// Inline markup: {i:r} italic, {sub:c} subscript, {sup:1,2} superscript, {b:text} bold.
// Paragraphs are separated by "\n"; a paragraph starting with "• " becomes a bullet.
function runs(text, base) {
  text = text.replace(/ = /g, '\u00A0=\u00A0').replace(/ < /g, '\u00A0<\u00A0')
    .replace(/(\d) (Hz|s\b)/g, '$1\u00A0$2').replace(/\b(Fp2|F4)-(Pz|O2)\b/g, '$1\u2011$2');
  const out = [];
  const paras = text.split('\n');
  paras.forEach((para, pi) => {
    let bullet = false;
    if (para.startsWith('• ')) { bullet = true; para = para.slice(2); }
    const pieces = [];
    const re = /\{(i|sub|sup|b):([^}]*)\}/g;
    let last = 0; let m;
    while ((m = re.exec(para))) {
      if (m.index > last) pieces.push({ text: para.slice(last, m.index), o: {} });
      const o = { i: { italic: true }, sub: { subscript: true }, sup: { superscript: true }, b: { bold: true } }[m[1]];
      pieces.push({ text: m[2], o });
      last = re.lastIndex;
    }
    if (last < para.length) pieces.push({ text: para.slice(last), o: {} });
    pieces.forEach((p, k) => {
      const options = { ...base, ...p.o };
      if (bullet) options.bullet = { indent: 18 };
      if (k === pieces.length - 1 && pi < paras.length - 1) options.breakLine = true;
      out.push({ text: p.text, options });
    });
  });
  return out;
}

function text(slide, t, x, y, w, h, o = {}) {
  const base = {
    fontFace: FONT, fontSize: o.size || 18, color: o.color || INK, bold: !!o.bold,
    paraSpaceAfter: o.after === undefined ? 8 : o.after, lineSpacingMultiple: o.line || 1.08,
  };
  slide.addText(runs(t, base), {
    x, y, w, h, margin: 0, valign: o.valign || 'top', align: o.align || 'left', isTextBox: true,
    fit: 'none',
  });
}

function equation(slide, key, size, x, y, w, h) {
  slide.addText(`${key}@${size}`, {
    x, y, w, h, margin: 0, valign: 'middle', fontFace: 'Cambria Math', fontSize: size, color: INK,
    isTextBox: true,
  });
}

function image(slide, name, x, y, w, h, alt) {
  slide.addImage({ path: fig(name), x, y, w, h, altText: alt });
}

function footnote(slide, t, y = 6.78) {
  text(slide, t, 0.6, y, 12.1, 0.55, { size: 11, color: GRAY, after: 0, line: 1.05 });
}

// Speaker notes from the script ("## Slide N ..." sections).
const notes = {};
for (const block of fs.readFileSync(SCRIPT, 'utf8').split(/^## /m).slice(1)) {
  const m = block.match(/^Slide (\d+)[^\n]*\n([\s\S]*)$/);
  if (m) notes[Number(m[1])] = m[2].replace(/\*\*/g, '').trim();
}

// ---------------------------------------------------------------------------------------------
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5 in
pres.author = 'Amaar Chughtai';
pres.title = 'Early and Later EEG Synchronization During 40-Hz Auditory Stimulation';
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

pres.defineSlideMaster({
  title: 'CONTENT',
  background: { color: 'FFFFFF' },
  objects: [{
    placeholder: {
      options: {
        name: 'title', type: 'title', x: 0.6, y: 0.42, w: 12.1, h: 1.0, margin: 0, valign: 'top', align: 'left',
        fontFace: FONT, fontSize: 30, bold: true, color: TITLE,
      },
      text: '',
    },
  }],
});

function content(title, n) {
  const s = pres.addSlide({ masterName: 'CONTENT' });
  s.addText(title, { placeholder: 'title' });
  if (notes[n]) s.addNotes(notes[n]);
  return s;
}

// 1 · title ------------------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: 'FFFFFF' };
  text(s, 'Early and Later EEG Synchronization During 40-Hz Auditory Stimulation', 0.6, 0.85, 10.8, 1.6,
    { size: 40, bold: true, color: TITLE, line: 1.0, after: 0 });
  text(s, 'Amaar Chughtai', 0.6, 2.75, 8, 0.45, { size: 24, bold: true, after: 0 });
  text(s, 'Valley Christian High School, San Jose, California', 0.6, 3.22, 9, 0.4, { size: 20, color: INK2, after: 0 });
  text(s, 'IEEE MIT URTC 2026, Lightning Talk ID-1269, October 11, 2026', 0.6, 3.68, 9, 0.4,
    { size: 16, color: INK2, after: 0 });
  image(s, 'fig_title_strip', 0.55, 4.45, 8.4, 2.35,
    '40-Hz phase-locking value in each 20-second window of one participant\'s session');
  text(s, 'One participant\'s session (sub-32, one of the stronger responders)', 0.6, 6.85, 8.4, 0.35,
    { size: 12, color: GRAY, after: 0 });
  if (notes[1]) s.addNotes(notes[1]);
}

// 2 · question ---------------------------------------------------------------------------------
{
  const s = content('Does the EEG response in the first two minutes track the response a few minutes later?', 2);
  text(s,
    'In mice, 40-Hz light and sound reduced Alzheimer\'s-like pathology.{sup:1,2} Replication has been mixed,{sup:3} and benefit in patients hasn\'t been established.{sup:4,5}\n'
    + 'Not every brain follows 40-Hz sound.{sup:6} To tailor stimulation to a person, you\'d have to decide while the session is still running. That only works if the early response says something about the later one.',
    0.6, 2.05, 6.1, 4.2, { size: 20, after: 16, line: 1.12 });
  image(s, 'fig_stimulus', 7.05, 2.0, 5.7, 2.6, 'A 40-Hz train of 1-ms, 5-kHz tone pips');
  text(s, 'The stimulus: a 1-ms, 5-kHz tone pip every 25 ms, so 40 per second, played from two loudspeakers.{sup:6}',
    7.2, 4.75, 5.4, 0.9, { size: 14, color: INK2, after: 0 });
  footnote(s, '{sup:1}Iaccarino et al., Nature 2016.  {sup:2}Martorell et al., Cell 2019.  {sup:3}Soula et al., Nat Neurosci 2023.  '
    + '{sup:4}Chan et al., PLOS ONE 2022.  {sup:5}Hajós et al., Front Neurol 2024.  {sup:6}Lahijanian et al., Sci Rep 2024.');
}

// 3 · data and protocol ------------------------------------------------------------------------
{
  const s = content('35 people, 40 s of sound, 20 s of silence', 3);
  text(s, 'Public EEG from a memory clinic in Tehran (OpenNeuro ds005048). 10 people were cognitively normal, 6 had mild cognitive impairment, 17 had Alzheimer\'s disease, and 2 were unclassified.',
    0.6, 1.2, 12.1, 0.8, { size: 18, color: INK2, after: 0 });
  image(s, 'fig_protocol', 0.45, 2.2, 9.0, 4.0, 'Protocol timeline and group-mean 40-Hz PLV in every 20-second window');
  text(s, 'In every cycle shown, the group\'s 40-Hz PLV was higher with sound than in the silence right after it.\n'
    + 'Over the whole session, sound minus silence was +0.077 (95% CI 0.045 to 0.112), and it was higher with sound in 27 of 35 people.',
    9.75, 2.75, 3.0, 3.6, { size: 17, after: 14 });
  footnote(s, 'Bands show ±1 standard error across people. Each 40-s sound block is split into two 20-s windows. Sessions had 5 ({i:n} = 8) or 9 ({i:n} = 27) complete cycles, because the last silence of each recording is cut short. '
    + '19-channel EEG at 250 Hz, cleaned by the dataset authors (Lahijanian, Aghajan & Vahabi, Sci Rep 2024).', 6.55);
}

// 4 · the measure ------------------------------------------------------------------------------
{
  const s = content('How I measured synchronization', 4);
  image(s, 'fig_phase', 0.55, 1.3, 5.4, 3.12, 'Distribution of phase differences and their mean arrow, during sound and during silence');
  text(s, 'One pair of signals from sub-01 (largest early contrast), cycle 1, the median of its 200 pairs. The bars show where the phase difference fell over the 20-s window.',
    0.65, 4.45, 5.7, 0.62, { size: 13, color: GRAY, after: 0 });
  equation(s, 'EQ_PLV', 18, 0.65, 5.1, 5.7, 0.95);
  text(s, '{i:N} = 5000 samples per window. The reported PLV is the mean over all 200 pairs.', 0.65, 6.1, 5.7, 0.3,
    { size: 13, color: GRAY, after: 0 });

  image(s, 'fig_headmap', 6.75, 1.25, 2.8, 2.99, 'Electrode map: five frontal and five posterior electrodes, with the example pair');
  text(s, 'Each signal is one frontal minus one posterior electrode. 25 signals make 200 pairs that share no electrode. The two lines are the example pair, Fp2-Pz and F4-O2.',
    9.7, 1.7, 3.1, 2.4, { size: 14, color: INK2, after: 0 });

  text(s, 'For each cycle {i:k}, I subtract the silence right after:', 6.8, 4.4, 6.0, 0.4, { size: 16, after: 0 });
  equation(s, 'EQ_CK', 18, 6.8, 4.82, 6.0, 0.58);
  equation(s, 'EQ_EARLY_LATER', 16, 6.8, 5.42, 2.9, 1.0);
  text(s, 'Raw PLV alone mostly describes the person. Block 1 and the last three blocks correlate at {i:r} = 0.87 to 0.93, at every frequency.',
    9.85, 5.45, 2.95, 1.1, { size: 13, color: INK2, after: 0 });
  footnote(s, 'The bar marks the mean of the sound block\'s two 20-s windows. Each window is filtered on its own (Butterworth band-pass, 39.5 to 40.5 Hz, zero-phase), with phase from the Hilbert transform. '
    + 'Montage and filter follow Lahijanian et al. 2024. PLV: Lachaux et al. 1999; Mormann et al. 2000.', 6.72);
}

// 5 · result -----------------------------------------------------------------------------------
{
  const s = content('People with a larger early contrast had a larger later contrast', 5);
  image(s, 'fig_scatter', 0.45, 1.3, 7.0, 5.3, 'Scatter plot of early versus later sound-minus-silence PLV contrast for 35 participants');
  text(s,
    'Each dot is one person.\n'
    + 'The rank correlation agrees (Spearman {i:ρ} = 0.688).\n'
    + 'Lin\'s concordance is 0.771, so the values agree, not just the order.\n'
    + 'The group mean barely moved (-0.015, {i:p} = 0.25), but individuals did. 95% limits of agreement: -0.16 to +0.13.\n'
    + 'Without the most influential person (top right), {i:r} = 0.747.',
    7.85, 1.75, 4.95, 4.8, { size: 18, after: 14, line: 1.1 });
  footnote(s, 'CI from 50,000 participant bootstrap resamples; {i:p} from a paired {i:t}-test. Early: cycles 1-2 (0-120 s after the first sound). Later: cycles 4-5 (180-300 s).');
}

// 6 · checks -----------------------------------------------------------------------------------
{
  const s = content('It held up when I tried to break it', 6);
  text(s, 'Other frequencies', 0.6, 1.3, 4.6, 0.4, { size: 18, bold: true, after: 0 });
  text(s, 'Other phase measures', 5.65, 1.3, 3.4, 0.4, { size: 18, bold: true, after: 0 });
  text(s, 'Other later windows', 9.4, 1.3, 3.4, 0.4, { size: 18, bold: true, after: 0 });
  image(s, 'fig_frequency', 0.45, 1.75, 4.8, 3.55, 'Early-later correlation at 35 to 45 Hz');
  image(s, 'fig_measures', 5.5, 1.75, 3.55, 3.55, 'Early-later correlation for PLV, PLI and wPLI');
  image(s, 'fig_positions', 9.25, 1.75, 3.55, 3.55, 'Early-later correlation for each later window from cycles 3-4 to 8-9');
  text(s, 'The six neighbors range from -0.10 to 0.26. The smallest gap from 40 Hz is 0.52 (95% CI 0.08 to 0.65).',
    0.6, 5.4, 4.6, 1.2, { size: 15, after: 0 });
  text(s, 'PLI and wPLI ignore zero-lag coupling, which one source reaching both electrodes would produce.',
    5.65, 5.4, 3.4, 1.2, { size: 15, after: 0 });
  text(s, 'Cycles 4-5 gave the highest {i:r}. The other five windows gave 0.61 to 0.77, all {i:p} < 0.05 after Bonferroni correction.',
    9.4, 5.4, 3.4, 1.2, { size: 15, after: 0 });
  footnote(s, 'Dots are early vs. later {i:r} with 95% participant-bootstrap intervals; the early window is always cycles 1-2. Cycles 6-9 exist only in the 27 longer sessions. '
    + 'PLI: phase-lag index (Stam et al. 2007). wPLI: weighted PLI (Vinck et al. 2011).');
}

// 7 · meaning ----------------------------------------------------------------------------------
{
  const s = content('Enough to justify a prospective test, and no more', 7);
  text(s, 'The contrast in the first two minutes tracked the contrast 3 to 5 minutes in ({i:r} = 0.78), most strongly at 40 Hz.',
    0.6, 1.35, 7.9, 1.1, { size: 22, after: 0, line: 1.1 });
  text(s, 'What limits it', 0.6, 2.72, 7.6, 0.4, { size: 18, bold: true, after: 0 });
  text(s,
    '• I picked cycles 4-5 after looking at the data.\n'
    + '• The EEG was cleaned offline, using whole recordings.\n'
    + '• Silence always followed sound, and there was no sham.\n'
    + '• Scalp EEG can\'t rule out a shared response or an artifact.',
    0.6, 3.15, 7.6, 1.9, { size: 18, after: 6 });
  text(s, 'Not yet tested: repeat sessions, whether it can guide stimulation, and any link to clinical benefit.\n'
    + 'Next: a preregistered, real-time test with a sham or counterbalanced order.',
    0.6, 5.05, 7.6, 1.3, { size: 18, after: 10 });
  image(s, 'fig_scatter_small', 8.85, 1.5, 4.1, 3.2, 'The main result again: early versus later contrast, r = 0.78');
  footnote(s, 'Data: Lahijanian, Aghajan & Vahabi, OpenNeuro ds005048 (CC0). Thank you to the participants and the dataset authors.');
}

pres.writeFile({ fileName: OUT }).then((f) => console.log(`wrote ${f}`));
