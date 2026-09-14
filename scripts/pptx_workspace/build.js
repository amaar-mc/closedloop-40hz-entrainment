/**
 * Build CSEF 2026 Presentation as .pptx
 *
 * Uses html2pptx to convert 12 HTML slides, then adds tables via PptxGenJS API.
 * Run: node scripts/pptx_workspace/build.js
 */

const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");
const HTML2PPTX_PATH = process.env.HTML2PPTX_PATH;
if (!HTML2PPTX_PATH) {
  throw new Error("Set HTML2PPTX_PATH to the absolute path of html2pptx.js");
}
const html2pptx = require(HTML2PPTX_PATH);

const PROJECT_ROOT = path.resolve(__dirname, "..", "..");
const WORKSPACE = __dirname;
const OUTPUT_PRIMARY = path.join(
  PROJECT_ROOT,
  "docs",
  "presentations",
  "CSEF_2026_Presentation.pptx",
);
const OUTPUT_CSEF = path.join(
  PROJECT_ROOT,
  "CSEF",
  "Presentation",
  "CSEF_2026_Presentation.pptx",
);

// Table styling constants
const HDR_FILL = "282828";
const HDR_TEXT = "FFFFFF";
const ROW_ALT = "F2F2F2";
const ROW_WHITE = "FFFFFF";
const BODY_TEXT = "000000";
const FONT = "Times New Roman";
const TBL_FONT_SZ = 14;

// Helper: create header cell
function hdr(text) {
  return {
    text,
    options: {
      fill: { color: HDR_FILL },
      color: HDR_TEXT,
      bold: true,
      align: "center",
      fontFace: FONT,
      fontSize: TBL_FONT_SZ,
    },
  };
}

// Helper: create body cell (first col left-aligned, rest center)
function cell(text, isFirst, isBold, rowIdx) {
  const fill = rowIdx % 2 === 1 ? ROW_ALT : ROW_WHITE;
  return {
    text,
    options: {
      fill: { color: fill },
      color: BODY_TEXT,
      bold: isBold || false,
      align: isFirst ? "left" : "center",
      fontFace: FONT,
      fontSize: TBL_FONT_SZ,
    },
  };
}

async function main() {
  const pptx = new pptxgen();

  // Custom layout: 11" x 8.5" landscape letter
  pptx.defineLayout({ name: "LETTER_L", width: 11, height: 8.5 });
  pptx.layout = "LETTER_L";
  pptx.title = "CSEF 2026 - Closed-Loop 40 Hz Entrainment";
  pptx.author = "Amaar Chughtai";

  // Track placeholders per slide for table insertion
  const slideData = [];

  // Process all 12 slides
  for (let i = 1; i <= 12; i++) {
    const num = String(i).padStart(2, "0");
    const htmlFile = path.join(WORKSPACE, `slide${num}.html`);

    if (!fs.existsSync(htmlFile)) {
      console.error(`Missing: ${htmlFile}`);
      process.exit(1);
    }

    console.log(`Processing slide ${num}...`);
    const result = await html2pptx(htmlFile, pptx);
    slideData.push(result);
  }

  // --- Add tables to placeholder areas ---

  // Slide 5 (index 4): Feature ablation table
  const slide5 = slideData[4];
  const ph5 = slide5.placeholders.find((p) => p.id === "table-ablation");
  if (ph5) {
    const rows = [
      [hdr("Feature Subset"), hdr("# Features"), hdr("Test R\u00b2")],
      [
        cell("All (spectral + PAC + stim)", true, false, 0),
        cell("73", false, false, 0),
        cell("\u22120.025", false, false, 0),
      ],
      [
        cell("PAC only", true, false, 1),
        cell("7", false, false, 1),
        cell("0.344", false, false, 1),
      ],
      [
        cell("PAC + Stim context (final)", true, true, 2),
        cell("12", false, true, 2),
        cell("0.558*", false, true, 2),
      ],
      [
        cell("Spectral only", true, false, 3),
        cell("61", false, false, 3),
        cell("\u22120.420", false, false, 3),
      ],
    ];
    slide5.slide.addTable(rows, {
      x: ph5.x,
      y: ph5.y,
      w: ph5.w,
      border: { type: "solid", pt: 0.5, color: "999999" },
      colW: [4.5 * (ph5.w / 8.4), 1.8 * (ph5.w / 8.4), 2.1 * (ph5.w / 8.4)],
      rowH: 0.3,
      fontFace: FONT,
      fontSize: TBL_FONT_SZ,
    });
  }

  // Slide 7 (index 6): Horizon sweep table
  const slide7 = slideData[6];
  const ph7 = slide7.placeholders.find((p) => p.id === "table-horizon");
  if (ph7) {
    const rows = [
      [
        hdr("Horizon"),
        hdr("Persistence R\u00b2"),
        hdr("TCN R\u00b2 (7ch)"),
        hdr("TCN R\u00b2 (4ch)"),
        hdr("TCN Margin"),
      ],
      [
        cell("1 s", true, false, 0),
        cell("0.726", false, false, 0),
        cell("0.725", false, false, 0),
        cell("0.642", false, false, 0),
        cell("\u22120.001", false, false, 0),
      ],
      [
        cell("3 s", true, false, 1),
        cell("0.178", false, false, 1),
        cell("0.607", false, false, 1),
        cell("0.391", false, false, 1),
        cell("+0.429", false, false, 1),
      ],
      [
        cell("5 s", true, false, 2),
        cell("0.104", false, false, 2),
        cell("0.577", false, false, 2),
        cell("0.398", false, false, 2),
        cell("+0.473", false, false, 2),
      ],
      [
        cell("8 s", true, false, 3),
        cell("\u22120.007", false, false, 3),
        cell("0.370", false, false, 3),
        cell("0.419", false, false, 3),
        cell("+0.377", false, false, 3),
      ],
      [
        cell("10 s", true, false, 4),
        cell("\u22120.081", false, false, 4),
        cell("0.669", false, false, 4),
        cell("0.387", false, false, 4),
        cell("+0.750", false, false, 4),
      ],
    ];
    slide7.slide.addTable(rows, {
      x: ph7.x,
      y: ph7.y,
      w: ph7.w,
      border: { type: "solid", pt: 0.5, color: "999999" },
      colW: [
        1.2 * (ph7.w / 9.3),
        2.1 * (ph7.w / 9.3),
        2.1 * (ph7.w / 9.3),
        2.1 * (ph7.w / 9.3),
        1.8 * (ph7.w / 9.3),
      ],
      rowH: 0.3,
      fontFace: FONT,
      fontSize: TBL_FONT_SZ,
    });
  }

  // Slide 8 (index 7): Controller comparison table
  const slide8 = slideData[7];
  const ph8ctrl = slide8.placeholders.find((p) => p.id === "table-controller");
  if (ph8ctrl) {
    const rows = [
      [
        hdr("Controller"),
        hdr("Alignment"),
        hdr("Low-PAC Stim"),
        hdr("Stim %"),
        hdr("PAC Gap"),
      ],
      [
        cell("Fixed Schedule", true, false, 0),
        cell("45.0%", false, false, 0),
        cell("61.4%", false, false, 0),
        cell("66.6%", false, false, 0),
        cell("\u22126.6", false, false, 0),
      ],
      [
        cell("Reactive Threshold", true, false, 1),
        cell("64.5%", false, false, 1),
        cell("51.7%", false, false, 1),
        cell("36.7%", false, false, 1),
        cell("+21.1", false, false, 1),
      ],
      [
        cell("TCN Predictive", true, true, 2),
        cell("72.1%", false, true, 2),
        cell("82.6%", false, true, 2),
        cell("59.7%", false, true, 2),
        cell("+30.5", false, true, 2),
      ],
      [
        cell("Alignment Oracle", true, false, 3),
        cell("100%", false, false, 3),
        cell("100%", false, false, 3),
        cell("48.3%", false, false, 3),
        cell("+33.3", false, false, 3),
      ],
    ];
    slide8.slide.addTable(rows, {
      x: ph8ctrl.x,
      y: ph8ctrl.y,
      w: ph8ctrl.w,
      border: { type: "solid", pt: 0.5, color: "999999" },
      colW: [
        2.4 * (ph8ctrl.w / 8.4),
        1.6 * (ph8ctrl.w / 8.4),
        1.7 * (ph8ctrl.w / 8.4),
        1.3 * (ph8ctrl.w / 8.4),
        1.4 * (ph8ctrl.w / 8.4),
      ],
      rowH: 0.3,
      fontFace: FONT,
      fontSize: TBL_FONT_SZ,
    });
  }

  // Slide 8 (index 7): Multi-seed robustness table
  const ph8seed = slide8.placeholders.find((p) => p.id === "table-seeds");
  if (ph8seed) {
    const rows = [
      [hdr("Seed"), hdr("Val R\u00b2"), hdr("Test R\u00b2")],
      [
        cell("42", true, false, 0),
        cell("0.804", false, false, 0),
        cell("0.558", false, false, 0),
      ],
      [
        cell("123", true, false, 1),
        cell("0.822", false, false, 1),
        cell("0.620", false, false, 1),
      ],
      [
        cell("456", true, false, 2),
        cell("0.799", false, false, 2),
        cell("0.597", false, false, 2),
      ],
      [
        cell("789", true, false, 3),
        cell("0.831", false, false, 3),
        cell("0.608", false, false, 3),
      ],
      [
        cell("2024", true, false, 4),
        cell("0.846", false, false, 4),
        cell("0.647", false, false, 4),
      ],
      [
        cell("Mean \u00b1 Std", true, true, 5),
        cell("0.820 \u00b1 0.019", false, true, 5),
        cell("0.606 \u00b1 0.032", false, true, 5),
      ],
    ];
    slide8.slide.addTable(rows, {
      x: ph8seed.x,
      y: ph8seed.y,
      w: ph8seed.w,
      border: { type: "solid", pt: 0.5, color: "999999" },
      colW: [
        2.2 * (ph8seed.w / 7.0),
        2.4 * (ph8seed.w / 7.0),
        2.4 * (ph8seed.w / 7.0),
      ],
      rowH: 0.3,
      fontFace: FONT,
      fontSize: TBL_FONT_SZ,
    });
  }

  // Save
  fs.mkdirSync(path.dirname(OUTPUT_PRIMARY), { recursive: true });
  await pptx.writeFile({ fileName: OUTPUT_PRIMARY });
  console.log(`Saved: ${OUTPUT_PRIMARY}`);

  // Copy to CSEF directory
  fs.mkdirSync(path.dirname(OUTPUT_CSEF), { recursive: true });
  fs.copyFileSync(OUTPUT_PRIMARY, OUTPUT_CSEF);
  console.log(`Copied: ${OUTPUT_CSEF}`);

  const stats = fs.statSync(OUTPUT_PRIMARY);
  console.log(`Size: ${Math.round(stats.size / 1024)} KB`);
  console.log("Done.");
}

main().catch((err) => {
  console.error("Build failed:", err);
  process.exit(1);
});
