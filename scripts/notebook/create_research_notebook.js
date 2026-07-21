const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  AlignmentType,
  HeadingLevel,
  BorderStyle,
  WidthType,
  ShadingType,
  VerticalAlign,
  PageBreak,
  LevelFormat,
} = require("docx");
const fs = require("fs");

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 24 } }, // 12pt default
    },
    paragraphStyles: [
      {
        id: "Title",
        name: "Title",
        basedOn: "Normal",
        run: { size: 32, bold: true, color: "000000", font: "Arial" },
        paragraph: {
          spacing: { before: 240, after: 240 },
          alignment: AlignmentType.CENTER,
        },
      },
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 0 },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 26, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 },
      },
      {
        id: "Heading3",
        name: "Heading 3",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 24, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 120, after: 80 }, outlineLevel: 2 },
      },
      {
        id: "EntryDate",
        name: "Entry Date",
        basedOn: "Normal",
        run: { size: 24, bold: true, color: "333333", font: "Arial" },
        paragraph: { spacing: { before: 180, after: 60 } },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      {
        reference: "number-list",
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
      },
      children: [
        // Title Page
        new Paragraph({
          heading: HeadingLevel.TITLE,
          children: [new TextRun("Project P10 Research Notebook")],
        }),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 240, after: 60 },
          children: [
            new TextRun({
              text: "Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease",
              size: 26,
              bold: true,
            }),
          ],
        }),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 180, after: 60 },
          children: [
            new TextRun({ text: "Researcher: Amaar Chughtai", size: 24 }),
          ],
        }),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 60 },
          children: [
            new TextRun({
              text: "School: Valley Christian High School",
              size: 24,
            }),
          ],
        }),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 60 },
          children: [
            new TextRun({
              text: "Fair: Synopsys Science and Engineering Fair 2026",
              size: 24,
            }),
          ],
        }),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 240 },
          children: [
            new TextRun({
              text: "Date Range: December 10, 2025 - March 3, 2026",
              size: 24,
            }),
          ],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 1: Background Research
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Background Research and Project Selection")],
        }),

        new Paragraph({
          style: "EntryDate",
          children: [new TextRun("December 10, 2025 - Initial Brainstorming")],
        }),

        new Paragraph({
          children: [
            new TextRun(
              "Today I began planning my Synopsys project. I wanted to work with brain signals (EEG) and neurodegenerative disease because I find neuroscience fascinating and there is substantial publicly available data.",
            ),
          ],
        }),

        new Paragraph({
          spacing: { before: 120, after: 60 },
          children: [
            new TextRun({ text: "Key question:", bold: true }),
            new TextRun(
              " Should I focus on Alzheimer's Disease or Parkinson's Disease?",
            ),
          ],
        }),

        // Comparison Table
        (() => {
          const tableBorder = {
            style: BorderStyle.SINGLE,
            size: 1,
            color: "CCCCCC",
          };
          const cellBorders = {
            top: tableBorder,
            bottom: tableBorder,
            left: tableBorder,
            right: tableBorder,
          };

          return new Table({
            columnWidths: [2340, 3120, 3900],
            margins: { top: 100, bottom: 100, left: 180, right: 180 },
            rows: [
              new TableRow({
                tableHeader: true,
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    verticalAlign: VerticalAlign.CENTER,
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({
                            text: "Feature",
                            bold: true,
                            size: 22,
                          }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3120, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({
                            text: "Alzheimer's Disease",
                            bold: true,
                            size: 22,
                          }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3900, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({
                            text: "Parkinson's Disease",
                            bold: true,
                            size: 22,
                          }),
                        ],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("Primary symptom")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3120, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun("Memory loss, cognitive decline"),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3900, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun("Movement problems (tremor, rigidity)"),
                        ],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("EEG signature")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3120, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun("Reduced gamma oscillations (30-80 Hz)"),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3900, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun("Excessive beta oscillations (13-30 Hz)"),
                        ],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({ children: [new TextRun("Prevalence")] }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3120, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun("~6.7 million Americans (2023)"),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3900, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("~1 million Americans")],
                      }),
                    ],
                  }),
                ],
              }),
            ],
          });
        })(),

        new Paragraph({
          spacing: { before: 120 },
          children: [
            new TextRun({ text: "Decision:", bold: true }),
            new TextRun(" Alzheimer's Disease"),
          ],
        }),

        new Paragraph({
          children: [new TextRun("Rationale:")],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [new TextRun("Larger public health impact")],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [new TextRun("More EEG datasets available")],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun(
              "Recent breakthrough research on gamma enhancement therapy",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun("Personal connection - my grandmother had dementia"),
          ],
        }),

        // Continue with more entries...
        new Paragraph({
          style: "EntryDate",
          children: [
            new TextRun(
              "December 11-12, 2025 - Deep Dive into Alzheimer's Biology",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: "Key findings from literature review:",
              bold: true,
            }),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun({ text: "Gamma oscillations (30-80 Hz)", bold: true }),
            new TextRun(" are critical for memory encoding and retrieval"),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun("Generated by "),
            new TextRun({ text: "PING mechanism", bold: true }),
            new TextRun(
              " (Pyramidal-Interneuron Network Gamma): fast-spiking interneurons synchronize pyramidal neuron firing",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun({ text: "Alzheimer's disrupts gamma:", bold: true }),
            new TextRun(
              " Reduced power and poor synchronization across brain regions",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun({
              text: '"Neurons that fire together, wire together"',
              italics: true,
            }),
            new TextRun(" - gamma synchrony enables memory formation"),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun({
              text: "Phase-Amplitude Coupling (PAC):",
              bold: true,
            }),
            new TextRun(
              " Theta rhythm (4-8 Hz) modulates gamma amplitude, quantifies coupling strength",
            ),
          ],
        }),

        new Paragraph({
          style: "EntryDate",
          children: [
            new TextRun(
              "December 16, 2025 - The Pivot That Changed Everything",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "Breakthrough discovery:", bold: true }),
            new TextRun(
              ' Found Iaccarino et al. (2016) Nature paper: "Gamma frequency entrainment attenuates amyloid load and modifies microglia."',
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "Key findings from this paper:", bold: true }),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "MIT researchers exposed AD mice to 40 Hz flickering light",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "Light drove brain to oscillate at gamma frequency (entrainment)",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "Triggered microglia to clear amyloid-beta plaques by 40-50%",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "Human clinical trials by Cognito Therapeutics showed cognitive improvement",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "Critical insight:", bold: true }),
            new TextRun(
              " Current protocols use fixed schedules (40 Hz on for 1 hour, same for every patient). But individual responses vary dramatically. Some patients entrain robustly, others show minimal response.",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "New project idea:", bold: true }),
            new TextRun(
              " Build a closed-loop system that reads EEG in real-time, predicts when the brain will lose gamma entrainment, and delivers stimulation only when needed. Adaptive instead of fixed scheduling.",
            ),
          ],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Data Acquisition Section
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Data Acquisition and Technical Development")],
        }),

        new Paragraph({
          style: "EntryDate",
          children: [
            new TextRun(
              "January 3, 2026 - Dataset Download and BIDS Format Investigation",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun(
              'Downloaded 847 MB dataset from OpenNeuro. Found OpenNeuro ds005048: "40 Hz Auditory Entrainment in Dementia" (Lahijanian et al., 2024).',
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "Dataset specifications:", bold: true }),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun("35 elderly subjects from memory clinic in Tehran"),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun("19 EEG channels (10/20 system), 250 Hz sampling"),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun("Protocol: 40 Hz amplitude-modulated auditory pulses"),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [new TextRun("Design: 40s stimulation + 20s rest periods")],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun("File format: BIDS-compliant .set/.fdt pairs"),
          ],
        }),

        new Paragraph({
          style: "EntryDate",
          children: [
            new TextRun(
              "January 5-15, 2026 - Data Loading Technical Challenges",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "Major technical hurdle:", bold: true }),
            new TextRun(
              " EEGLAB .set files use MATLAB v7.3 format with HDF5 backend. Standard Python tools (MNE, EEGLAB readers) failed to load properly.",
            ),
          ],
        }),

        new Paragraph({
          children: [new TextRun({ text: "Solution developed:", bold: true })],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [new TextRun("Read .set HDF5 files directly with h5py")],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun(
              "Extract metadata from top-level fields (no EEG wrapper group)",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun(
              "Read actual data from .fdt files using numpy.fromfile()",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "Critical:", bold: true }),
            new TextRun(
              " Reshape with order='F' (Fortran/column-major) due to MATLAB storage format",
            ),
          ],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Architecture Development Section
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [
            new TextRun("Architecture Development and Model Iterations"),
          ],
        }),

        new Paragraph({
          style: "EntryDate",
          children: [
            new TextRun("February 16, 2026 - The Architecture Marathon"),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "Goal:", bold: true }),
            new TextRun(
              " Find optimal architecture for PAC prediction from 2-second EEG windows.",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "V1 - EEGNet Baseline:", bold: true }),
            new TextRun(
              " Based on Lawhern et al. (2018) - proven architecture for EEG classification. ~1,457 parameters: temporal convolution → depthwise spatial → separable convolution → FC. ",
            ),
            new TextRun({ text: "Result: R² = 0.287", bold: true }),
            new TextRun(" on test set."),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: "V3 - SpecTempNet - CRITICAL DISCOVERY:",
              bold: true,
            }),
            new TextRun(
              " Combined spectral features with temporal convolution. ",
            ),
            new TextRun({
              text: "FEATURE LEAKAGE DETECTED",
              bold: true,
              color: "FF0000",
            }),
            new TextRun(
              " - PAC features directly encoded the target (circular dependency). Inflated R² to 0.999 - completely invalid.",
            ),
          ],
        }),

        // Architecture Results Table
        (() => {
          const tableBorder = {
            style: BorderStyle.SINGLE,
            size: 1,
            color: "CCCCCC",
          };
          const cellBorders = {
            top: tableBorder,
            bottom: tableBorder,
            left: tableBorder,
            right: tableBorder,
          };

          return new Table({
            columnWidths: [2340, 1560, 1560, 3900],
            margins: { top: 100, bottom: 100, left: 180, right: 180 },
            rows: [
              new TableRow({
                tableHeader: true,
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun({ text: "Model", bold: true })],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({ text: "Parameters", bold: true }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({ text: "Test R²", bold: true }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3900, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun({ text: "Notes", bold: true })],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({ children: [new TextRun("EEGNet")] }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({ children: [new TextRun("1,457")] }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({ children: [new TextRun("0.287")] }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3900, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("Baseline architecture")],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({ children: [new TextRun("SpecTempNet")] }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({ children: [new TextRun("~10K")] }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({ text: "0.999*", color: "FF0000" }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3900, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({
                            text: "*Feature leakage - invalid",
                            color: "FF0000",
                          }),
                        ],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("Ridge Regression")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({ children: [new TextRun("427")] }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({ children: [new TextRun("0.315")] }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 3900, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("Simple linear model")],
                      }),
                    ],
                  }),
                ],
              }),
            ],
          });
        })(),

        new Paragraph({
          spacing: { before: 120 },
          children: [
            new TextRun({ text: "Key insight:", bold: true }),
            new TextRun(
              " For static PAC prediction from 7 frontal channels, the ceiling appears to be R² ≈ 0.30. This limitation led to the next major development.",
            ),
          ],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Temporal Prediction Section
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [
            new TextRun("Temporal Prediction and Multiscale TCN Development"),
          ],
        }),

        new Paragraph({
          style: "EntryDate",
          children: [new TextRun("February 17, 2026 - Reframing the Problem")],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "Breakthrough realization:", bold: true }),
            new TextRun(
              " Instead of predicting instantaneous PAC, predict future PAC states. This enables proactive control rather than reactive control.",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: "MultiscaleCausalTCN Architecture:",
              bold: true,
            }),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "Input: (batch, T=20, F=73) → Output: future PAC + delta PAC",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "Causal depthwise-separable convolutions (no future information)",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "Dilation pattern [1,2,4,8] captures multiscale temporal dependencies",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [new TextRun("Parameters: ~31,000")],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Results Section
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Results and Clinical Validation")],
        }),

        new Paragraph({
          style: "EntryDate",
          children: [new TextRun("February 19, 2026 - Horizon Sweep Analysis")],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "The Critical Experiment:", bold: true }),
            new TextRun(
              " Train separate models to predict PAC at horizons 1-10 seconds. Compare TCN against persistence and Ridge baselines.",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({ text: "Key finding:", bold: true }),
            new TextRun(
              " At 1-2 second horizons, simple baselines suffice. At 5-10 second horizons - the operationally relevant range for proactive control - baselines collapse to negative R² while TCN maintains R² ≈ 0.25.",
            ),
          ],
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: "[FIGURE PLACEMENT: Insert horizon sweep graph here]",
              italics: true,
              color: "0000FF",
            }),
          ],
        }),

        new Paragraph({
          style: "EntryDate",
          children: [new TextRun("February 21, 2026 - Real-Data Validation")],
        }),

        // Main Results Table
        (() => {
          const tableBorder = {
            style: BorderStyle.SINGLE,
            size: 1,
            color: "CCCCCC",
          };
          const cellBorders = {
            top: tableBorder,
            bottom: tableBorder,
            left: tableBorder,
            right: tableBorder,
          };

          return new Table({
            columnWidths: [2340, 1560, 1880, 1880, 1300],
            margins: { top: 100, bottom: 100, left: 180, right: 180 },
            rows: [
              new TableRow({
                tableHeader: true,
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({ text: "Controller", bold: true }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({ text: "Alignment", bold: true }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({
                            text: "Low-PAC Targeting",
                            bold: true,
                          }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({ text: "High-PAC Rest", bold: true }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1300, type: WidthType.DXA },
                    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                          new TextRun({ text: "PAC Gap", bold: true }),
                        ],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("Fixed Schedule")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("45.0%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("61.4%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("28.6%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1300, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("-6.6")],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("Reactive Threshold")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("64.5%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("51.7%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("77.3%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1300, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("+21.1")],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    shading: { fill: "E6FFE6", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        children: [
                          new TextRun({ text: "TCN Predictive", bold: true }),
                        ],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    shading: { fill: "E6FFE6", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun({ text: "72.1%", bold: true })],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    shading: { fill: "E6FFE6", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun({ text: "82.6%", bold: true })],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    shading: { fill: "E6FFE6", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("61.6%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1300, type: WidthType.DXA },
                    shading: { fill: "E6FFE6", type: ShadingType.CLEAR },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun({ text: "+30.5", bold: true })],
                      }),
                    ],
                  }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2340, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        children: [new TextRun("Alignment Oracle")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1560, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("100.0%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("100.0%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1880, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("100.0%")],
                      }),
                    ],
                  }),
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 1300, type: WidthType.DXA },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [new TextRun("+33.3")],
                      }),
                    ],
                  }),
                ],
              }),
            ],
          });
        })(),

        new Paragraph({
          spacing: { before: 120 },
          children: [
            new TextRun({ text: "Statistical significance:", bold: true }),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "TCN vs Reactive alignment: 72.1% vs 64.5% (Hedges' g = 1.31, p < 0.001)",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun(
              "Low-PAC targeting: 82.6% vs 51.7% (g = 4.47, p < 0.001)",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "bullet-list", level: 0 },
          children: [
            new TextRun({
              text: "All 35 subjects benefited from TCN controller",
              bold: true,
            }),
            new TextRun(" (binomial p < 0.001)"),
          ],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Conclusions
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Results Summary and Clinical Implications")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Key Findings")],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "Temporal advantage:", bold: true }),
            new TextRun(
              " TCN maintains R² ≈ 0.25 at 5-10s horizons where baselines fail (negative R²)",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "Clinical performance:", bold: true }),
            new TextRun(
              " 72.1% vs 64.5% epoch alignment (p < 0.001, all subjects benefit)",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "Targeting precision:", bold: true }),
            new TextRun(
              " 82.6% vs 51.7% stimulation of low-PAC windows (60% improvement)",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "Individual differences:", bold: true }),
            new TextRun(
              " 50% of subjects habituate, 50% do not, validating personalized approach",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "Efficiency:", bold: true }),
            new TextRun(
              " Reaches 91% of theoretical oracle performance with 10% less stimulation than fixed protocols",
            ),
          ],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Limitations and Future Work")],
        }),

        new Paragraph({
          children: [new TextRun({ text: "Current Limitations:", bold: true })],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "Single-site dataset:", bold: true }),
            new TextRun(
              " 35 subjects from one clinic in Tehran - generalization needs validation",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "Offline analysis:", bold: true }),
            new TextRun(
              " Real-time implementation requires optimization for <1s inference latency",
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun({ text: "EEG-only approach:", bold: true }),
            new TextRun(
              " Integration with other biomarkers could improve predictions",
            ),
          ],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Conclusions")],
        }),

        new Paragraph({
          children: [
            new TextRun(
              "This project successfully developed and validated a predictive closed-loop system for 40 Hz gamma entrainment in Alzheimer's disease. The Temporal Convolutional Network architecture enables 5-second lookahead prediction of brain state, allowing proactive rather than reactive stimulation control.",
            ),
          ],
        }),

        new Paragraph({
          spacing: { before: 120 },
          children: [
            new TextRun({ text: "Clinical impact:", bold: true }),
            new TextRun(
              " The system achieves 72.1% alignment with optimal stimulation timing compared to 64.5% for reactive control, with 82.6% vs 51.7% targeting of therapeutic windows. This represents a 60% improvement in precision while using 10% less total stimulation.",
            ),
          ],
        }),

        new Paragraph({
          spacing: { before: 120 },
          children: [
            new TextRun({ text: "Scientific contribution:", bold: true }),
            new TextRun(
              " First demonstration that future PAC can be predicted from EEG at clinically relevant horizons (5-10 seconds) where traditional baselines fail.",
            ),
          ],
        }),

        new Paragraph({
          spacing: { before: 120 },
          children: [
            new TextRun({ text: "Personalized medicine:", bold: true }),
            new TextRun(
              " Strong individual differences in habituation patterns validate the need for adaptive, personalized control rather than one-size-fits-all protocols.",
            ),
          ],
        }),

        new Paragraph({
          spacing: { before: 120 },
          children: [
            new TextRun(
              "The results support advancement to clinical trials comparing adaptive vs fixed 40 Hz entrainment protocols for Alzheimer's treatment.",
            ),
          ],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // References
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("References")],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun(
              'Iaccarino, H.F., et al. "Gamma frequency entrainment attenuates amyloid load and modifies microglia." ',
            ),
            new TextRun({ text: "Nature", italics: true }),
            new TextRun(" 540, 230-235 (2016)."),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun(
              'Tort, A.B., et al. "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies." ',
            ),
            new TextRun({ text: "J. Neurophysiol.", italics: true }),
            new TextRun(" 104(2), 1195-1210 (2010)."),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun(
              'Lawhern, V.J., et al. "EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces." ',
            ),
            new TextRun({ text: "J. Neural Eng.", italics: true }),
            new TextRun(" 15(5), 056013 (2018)."),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun(
              'Lahijanian, B., et al. "40Hz Auditory Entrainment" OpenNeuro ds005048 v1.0.1 (2024).',
            ),
          ],
        }),

        new Paragraph({
          numbering: { reference: "number-list", level: 0 },
          children: [
            new TextRun(
              'Canolty, R.T. & Knight, R.T. "The functional role of cross-frequency coupling." ',
            ),
            new TextRun({ text: "Trends Cogn. Sci.", italics: true }),
            new TextRun(" 14(11), 506-515 (2010)."),
          ],
        }),

        new Paragraph({
          spacing: { before: 240 },
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Laboratory notebook pages: 120", size: 20 }),
          ],
        }),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({
              text: "Analysis period: December 10, 2025 - March 3, 2026",
              size: 20,
            }),
          ],
        }),
      ],
    },
  ],
});

// Generate the document
Packer.toBuffer(doc)
  .then((buffer) => {
    fs.writeFileSync("P10_Research_Notebook_Amaar_Chughtai.docx", buffer);
    console.log(
      "Research notebook created successfully: P10_Research_Notebook_Amaar_Chughtai.docx",
    );
  })
  .catch((err) => {
    console.error("Error creating document:", err);
  });
