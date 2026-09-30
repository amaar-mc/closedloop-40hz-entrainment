// Pre-render the LaTeX in deck.src.html with KaTeX so the PDF needs no JavaScript or network.
// Inline math: \( ... \)   Display math: \[ ... \]
const fs = require('fs');
const path = require('path');
const katex = require('katex');

const here = __dirname;
const src = fs.readFileSync(path.join(here, 'deck.src.html'), 'utf8');
const decode = (t) => t.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
const render = (tex, displayMode) =>
  katex.renderToString(decode(tex), { displayMode, throwOnError: true, output: 'htmlAndMathml', strict: 'error' });

let n = 0;
const out = src
  .replace(/\\\[([\s\S]+?)\\\]/g, (_, tex) => { n++; return render(tex, true); })
  .replace(/\\\(([\s\S]+?)\\\)/g, (_, tex) => { n++; return render(tex, false); });

// Keep unit expressions (40-Hz, 20-s, 1-ms, 5-kHz) and IDs (sub-01, ID-1269) from breaking at the hyphen.
// Only text inside <body>, outside tags and outside rendered math, is touched.
const [head, body] = out.split(/(?=<body>)/);
const noBreak = body
  .split(/(<[^>]+>)/)
  .map((seg, i, all) => {
    if (seg.startsWith('<')) return seg;
    return seg.replace(/\b(\d+-(?:Hz|kHz|ms|s)|sub-\d+|ID-\d+)\b/g, '<span class="nw">$1</span>');
  })
  .join('');
fs.writeFileSync(path.join(here, 'deck.html'), head + noBreak);
fs.mkdirSync(path.join(here, 'katex'), { recursive: true });
const dist = path.join(here, 'node_modules', 'katex', 'dist');
if (fs.existsSync(dist)) {
  fs.copyFileSync(path.join(dist, 'katex.min.css'), path.join(here, 'katex', 'katex.min.css'));
  // Chrome only needs the woff2 files; the stylesheet's woff/ttf fallbacks are never requested.
  fs.mkdirSync(path.join(here, 'katex', 'fonts'), { recursive: true });
  for (const f of fs.readdirSync(path.join(dist, 'fonts')).filter((n) => n.endsWith('.woff2'))) {
    fs.copyFileSync(path.join(dist, 'fonts', f), path.join(here, 'katex', 'fonts', f));
  }
}
console.log(`rendered ${n} math expressions`);
