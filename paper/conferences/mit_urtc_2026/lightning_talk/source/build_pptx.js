// Backup .pptx for the Windows room laptop: each slide is the rendered PDF page as a full-bleed
// image (so it looks identical to the PDF), with that slide's lines from SPEAKER_SCRIPT.md as notes.
//   node build_pptx.js <slides-dir with slide-N.png> <SPEAKER_SCRIPT.md> <out.pptx>
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const [slidesDir, scriptPath, outPath] = process.argv.slice(2);
if (!slidesDir || !scriptPath || !outPath) {
  console.error('usage: node build_pptx.js <slides-dir> <SPEAKER_SCRIPT.md> <out.pptx>');
  process.exit(1);
}

// Notes per slide: everything under "## Slide N ..." up to the next "## ".
const script = fs.readFileSync(scriptPath, 'utf8');
const notes = {};
for (const block of script.split(/^## /m).slice(1)) {
  const m = block.match(/^Slide (\d+)[^\n]*\n([\s\S]*)$/);
  if (m) notes[Number(m[1])] = m[2].replace(/\*\*/g, '').replace(/\n{3,}/g, '\n\n').trim();
}

const images = fs.readdirSync(slidesDir)
  .filter((f) => /^slide-\d+\.png$/.test(f))
  .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]));
if (images.length !== 7) throw new Error(`expected 7 slide images, found ${images.length}`);

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5 in, same as the PDF
pres.author = 'Amaar Chughtai';
pres.title = 'Early and Later EEG Synchronization During 40-Hz Auditory Stimulation';

images.forEach((file, i) => {
  const slide = pres.addSlide();
  slide.background = { color: 'FFFFFF' };
  slide.addImage({ path: path.join(slidesDir, file), x: 0, y: 0, w: 13.333, h: 7.5 });
  if (notes[i + 1]) slide.addNotes(notes[i + 1]);
});

pres.writeFile({ fileName: outPath }).then((f) => console.log(`wrote ${f} (${images.length} slides)`));
