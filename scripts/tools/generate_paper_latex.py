#!/usr/bin/env python3
"""
Generate journal-quality LaTeX from RESEARCH_PAPER_v3.md and compile to PDF.

Converts markdown to a properly formatted .tex file using article class with
Times New Roman fonts, proper math mode, figure/table environments, and
running headers. Compiles via tectonic.
"""

import os
import re
import subprocess
import sys

# ─── Paths ───────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_MD = os.path.join(PROJECT_ROOT, "docs", "paper", "RESEARCH_PAPER_v3.md")
OUTPUT_TEX = os.path.join(PROJECT_ROOT, "docs", "paper", "RESEARCH_PAPER_v3.tex")
OUTPUT_PDF = os.path.join(PROJECT_ROOT, "docs", "paper", "RESEARCH_PAPER_v3.pdf")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
TECTONIC = "/opt/homebrew/bin/tectonic"


# ─── Unicode → LaTeX replacements ───────────────────────────────────────────
UNICODE_MAP = [
    # Must come before individual char replacements
    ("×10⁻⁶", r"$\times 10^{-6}$"),
    ("x10^-6", r"$\times 10^{-6}$"),
    ("x10^-5", r"$\times 10^{-5}$"),
    ("x10^-4", r"$\times 10^{-4}$"),
    ("x10^-3", r"$\times 10^{-3}$"),
    ("x 10^-6", r"$\times 10^{-6}$"),
    ("x 10^-5", r"$\times 10^{-5}$"),
    ("x 10^-4", r"$\times 10^{-4}$"),
    ("x 10^-3", r"$\times 10^{-3}$"),
    ("1x10^-3", r"$1 \times 10^{-3}$"),
    ("1x10^-4", r"$1 \times 10^{-4}$"),
    # Superscripts
    ("R²", r"$R^2$"),
    ("R-squared", r"$R^2$"),
    # Greek letters
    ("θ", r"$\theta$"),
    ("γ", r"$\gamma$"),
    ("β", r"$\beta$"),
    ("σ", r"$\sigma$"),
    ("φ", r"$\varphi$"),
    ("δ", r"$\delta$"),
    ("µ", r"$\mu$"),
    ("μ", r"$\mu$"),
    # Math symbols
    ("≈", r"$\approx$"),
    ("≤", r"$\leq$"),
    ("≥", r"$\geq$"),
    ("±", r"$\pm$"),
    ("+/-", r"$\pm$"),
    ("×", r"$\times$"),
    # Dashes
    ("—", "---"),
    ("–", "--"),
    # Quotes
    ("\u201c", "``"),
    ("\u201d", "''"),
    ("\u2018", "`"),
    ("\u2019", "'"),
]


def escape_latex(text):
    """Escape LaTeX special characters in body text, preserving existing
    LaTeX commands and math mode."""
    # Protect existing LaTeX commands and math mode
    protected = []
    counter = [0]

    def protect(match):
        protected.append(match.group(0))
        counter[0] += 1
        return f"@@PROTECTED{counter[0] - 1}@@"

    # Protect $...$ math mode
    text = re.sub(r'\$[^$]+\$', protect, text)
    # Protect \url{...}, \label{...}, \includegraphics[...]{...}, \footnote{\url{...}}
    # (these contain paths/URLs that should NOT be escaped)
    text = re.sub(r'\\url\{[^}]*\}', protect, text)
    text = re.sub(r'\\label\{[^}]*\}', protect, text)
    text = re.sub(r'\\includegraphics\[[^\]]*\]\{[^}]*\}', protect, text)
    text = re.sub(r'\\footnote\{[^}]*\}', protect, text)
    # Protect bare \command sequences (e.g., \theta, \approx)
    text = re.sub(r'\\[a-zA-Z]+(?![{])', protect, text)

    # Now escape special chars
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("#", r"\#")
    # Underscore: escape only outside math
    text = text.replace("_", r"\_")
    # Tilde → $\sim$ (protect from later $ escaping)
    text = text.replace("~", "@@TILDE@@")
    text = text.replace("^", r"\textasciicircum{}")
    # Dollar sign: escape literal $ (e.g., "$300 billion")
    text = text.replace("$", r"\$")
    # Restore tilde
    text = text.replace("@@TILDE@@", r"$\sim$")

    # Restore protected content
    for i, p in enumerate(protected):
        text = text.replace(f"@@PROTECTED{i}@@", p)

    return text


def apply_unicode_replacements(text):
    """Replace Unicode symbols with LaTeX equivalents."""
    for src, dst in UNICODE_MAP:
        text = text.replace(src, dst)
    return text


def convert_inline_formatting(text):
    """Convert markdown inline formatting to LaTeX."""
    # Code: `...` → \texttt{...}
    text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', text)
    # Bold+italic: ***...*** → \textbf{\textit{...}}
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    # Bold: **...** → \textbf{...}
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # Italic: *...* → \textit{...}
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', text)
    # Links: [text](url) → text\footnote{\url{url}}
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'\1\\footnote{\\url{\2}}', text)
    # Remove markdown links without URLs
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    return text


def convert_citations(text):
    """Convert [N] citation patterns to LaTeX cite-style."""
    # Already in [N] format — just keep them
    return text


def process_line(text):
    """Full pipeline for processing a line of body text."""
    text = apply_unicode_replacements(text)
    text = convert_inline_formatting(text)
    text = escape_latex(text)
    text = convert_citations(text)
    return text


def resolve_image_path(rel_path):
    """Resolve an image path relative to docs/paper/ to an absolute path."""
    candidates = [
        os.path.normpath(os.path.join(PROJECT_ROOT, "docs", "paper", rel_path)),
        os.path.normpath(os.path.join(PROJECT_ROOT, rel_path.lstrip("./"))),
        os.path.join(FIGURES_DIR, os.path.basename(rel_path)),
        os.path.join(FIGURES_DIR, "ai_generated", os.path.basename(rel_path)),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def parse_table(lines):
    """Parse markdown table lines into (headers, rows)."""
    headers = []
    rows = []
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        # Skip separator line
        if all(set(c) <= {"-", ":", " "} for c in cells if c):
            continue
        if not headers:
            headers = cells
        else:
            rows.append(cells)
    return headers, rows


def make_label(text, prefix=""):
    """Create a LaTeX label from text."""
    label = re.sub(r'[^a-zA-Z0-9]', '_', text.lower())
    label = re.sub(r'_+', '_', label).strip("_")
    if prefix:
        return f"{prefix}:{label[:40]}"
    return label[:40]


def generate_latex():
    """Parse the markdown and produce LaTeX source."""
    with open(PAPER_MD, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    tex = []

    # ─── Preamble ────────────────────────────────────────────────────────
    tex.append(r"""\documentclass[11pt,letterpaper]{article}

% ── Fonts ──
\usepackage{newtxtext}

% ── Math (load amssymb before newtxmath to avoid \Bbbk clash) ──
\usepackage{amsmath}
\usepackage{amssymb}
\let\Bbbk\relax
\usepackage{newtxmath}

% ── Layout ──
\usepackage[margin=1in]{geometry}
\usepackage{setspace}
\singlespacing
\setlength{\parskip}{0.4em}

% ── Headers/footers ──
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small\itshape Chughtai --- Closed-Loop 40 Hz Entrainment}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\fancypagestyle{plain}{%
  \fancyhf{}
  \fancyfoot[C]{\thepage}
  \renewcommand{\headrulewidth}{0pt}
}

% ── Graphics/tables ──
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{longtable}
\usepackage{caption}
\captionsetup{font=small, labelfont=bf}

% ── Misc ──
\usepackage{enumitem}
\usepackage{hyperref}
\hypersetup{
  colorlinks=true,
  linkcolor=black,
  citecolor=black,
  urlcolor=blue,
  pdfauthor={Amaar Chughtai},
  pdftitle={Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment}
}
\usepackage{url}
\usepackage{float}

\begin{document}
""")

    i = 0
    figure_counter = 0
    table_counter = 0
    in_abstract = False
    in_references = False
    in_list = False
    list_type = None  # "itemize" or "enumerate"
    pending_figure_label = None  # For **Figure N.** lines preceding an image
    skip_next_star_figure_caption = False

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            tex.append(f"\\end{{{list_type}}}")
            tex.append("")
            in_list = False
            list_type = None

    while i < len(lines):
        line = lines[i]

        # ── Skip metadata at the end ──
        if line.strip().startswith("Word count:") or line.strip().startswith("Figures:") \
                or line.strip().startswith("Tables:") or line.strip().startswith("Last verified:"):
            i += 1
            continue

        # ── Horizontal rule → skip ──
        if line.strip() == "---":
            close_list()
            i += 1
            continue

        # ── Empty line ──
        if not line.strip():
            if not in_list:
                # don't add too many blank lines
                if tex and tex[-1].strip() != "":
                    tex.append("")
            i += 1
            continue

        # ── Title: # ──
        if re.match(r'^# ', line) and not re.match(r'^## ', line):
            close_list()
            title_text = line[2:].strip()
            title_text = apply_unicode_replacements(title_text)
            title_text = escape_latex(title_text)
            tex.append(r"\title{" + title_text + "}")
            i += 1
            continue

        # ── Author line ──
        if line.strip().startswith("**Amaar"):
            close_list()
            author = re.sub(r'\*\*(.+?)\*\*', r'\1', line.strip())
            tex.append(r"\author{" + escape_latex(author) + "}")
            tex.append(r"\date{}")
            tex.append(r"\maketitle")
            tex.append(r"\thispagestyle{plain}")
            tex.append("")
            i += 1
            continue

        # ── Keywords line ──
        if line.strip().startswith("**Keywords"):
            close_list()
            kw_text = line.strip()
            kw_text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', kw_text)
            kw_text = apply_unicode_replacements(kw_text)
            kw_text = escape_latex(kw_text)
            tex.append(r"\vspace{0.5em}")
            tex.append(r"\noindent " + kw_text)
            tex.append("")
            i += 1
            continue

        # ── Section: ## ──
        sec_match = re.match(r'^## (.+)', line)
        if sec_match and not line.startswith("### "):
            close_list()
            sec_text = sec_match.group(1).strip()

            if sec_text == "Abstract":
                tex.append(r"\begin{abstract}")
                in_abstract = True
                i += 1
                # Collect abstract paragraphs
                abstract_paras = []
                while i < len(lines):
                    if lines[i].strip().startswith("**Keywords"):
                        break
                    if lines[i].strip() == "---":
                        break
                    if lines[i].strip():
                        abstract_paras.append(process_line(lines[i].strip()))
                    i += 1
                tex.append("\n".join(abstract_paras))
                tex.append(r"\end{abstract}")
                tex.append("")
                in_abstract = False
                # Process keywords if present
                if i < len(lines) and lines[i].strip().startswith("**Keywords"):
                    kw_line = lines[i].strip()
                    kw_line = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', kw_line)
                    kw_line = apply_unicode_replacements(kw_line)
                    kw_line = escape_latex(kw_line)
                    tex.append(r"\vspace{0.5em}")
                    tex.append(r"\noindent " + kw_line)
                    tex.append("")
                    i += 1
                continue

            if sec_text == "References":
                in_references = True
                tex.append(r"\section*{References}")
                tex.append(r"\begin{enumerate}[label={[\arabic*]}, leftmargin=2em, itemsep=2pt, parsep=0pt]")
                i += 1
                # Collect references
                while i < len(lines):
                    rl = lines[i].strip()
                    if rl.startswith("Word count") or rl.startswith("Figures:") \
                            or rl.startswith("Tables:") or rl.startswith("Last verified"):
                        i += 1
                        continue
                    if rl == "---":
                        i += 1
                        continue
                    if not rl:
                        i += 1
                        continue
                    # Parse reference: [N] text
                    ref_match = re.match(r'^\[(\d+)\]\s*(.*)', rl)
                    if ref_match:
                        ref_text = ref_match.group(2)
                        ref_text = apply_unicode_replacements(ref_text)
                        ref_text = convert_inline_formatting(ref_text)
                        ref_text = escape_latex(ref_text)
                        # Convert URLs in references
                        ref_text = re.sub(
                            r'(https?://[^\s,]+)',
                            r'\\url{\1}',
                            ref_text
                        )
                        tex.append(r"\item " + ref_text)
                    i += 1
                tex.append(r"\end{enumerate}")
                tex.append("")
                in_references = False
                continue

            # Unnumbered sections
            unnumbered_sections = ["Data and Code Availability", "Acknowledgments",
                                   "Acknowledgements", "Supplementary Material"]
            sec_label = re.sub(r'^\d+\.\s*', '', sec_text)
            sec_label_processed = process_line(sec_label)

            if sec_label in unnumbered_sections:
                tex.append(r"\section*{" + sec_label_processed + "}")
            else:
                tex.append(r"\section{" + sec_label_processed + "}")
            tex.append("")
            i += 1
            continue

        # ── Subsection: ### ──
        subsec_match = re.match(r'^### (.+)', line)
        if subsec_match and not line.startswith("#### "):
            close_list()
            sub_text = subsec_match.group(1).strip()
            sub_label = re.sub(r'^\d+\.\d+\s*', '', sub_text)
            tex.append(r"\subsection{" + process_line(sub_label) + "}")
            tex.append("")
            i += 1
            continue

        # ── Subsubsection: #### ──
        subsub_match = re.match(r'^#### (.+)', line)
        if subsub_match:
            close_list()
            subsub_text = subsub_match.group(1).strip()
            subsub_label = re.sub(r'^\d+\.\d+\.\d+\s*', '', subsub_text)
            tex.append(r"\subsubsection{" + process_line(subsub_label) + "}")
            tex.append("")
            i += 1
            continue

        # ── Figure label line: **Figure N.** text (before an image) ──
        fig_label_match = re.match(r'^\*\*Figure\s+(\d+)\.\*\*\s*(.*)', line.strip())
        if fig_label_match:
            close_list()
            # Check if next non-empty line is an image
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip().startswith("!["):
                pending_figure_label = fig_label_match.group(1)
                i += 1
                continue
            # If no image follows, just skip this line
            i += 1
            continue

        # ── Image: ![alt](path) ──
        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if img_match:
            close_list()
            figure_counter += 1
            alt_text = img_match.group(1)
            img_rel = img_match.group(2)
            img_abs = resolve_image_path(img_rel)

            # Collect caption from following *Figure N. ...* lines
            caption_parts = []
            j = i + 1
            while j < len(lines):
                cl = lines[j].strip()
                if not cl:
                    j += 1
                    continue
                # Caption line starts with *Figure
                if cl.startswith("*Figure") or cl.startswith("*Table"):
                    cap = cl
                    # Strip outer italics
                    if cap.startswith("*") and cap.endswith("*"):
                        cap = cap[1:-1]
                    caption_parts.append(cap)
                    j += 1
                    continue
                break

            caption_text = " ".join(caption_parts) if caption_parts else alt_text
            caption_text = process_line(caption_text)

            fig_label = make_label(alt_text or f"figure{figure_counter}", "fig")

            tex.append(r"\begin{figure}[htbp]")
            tex.append(r"\centering")
            if img_abs:
                tex.append(r"\includegraphics[width=0.85\textwidth]{" + img_abs + "}")
            else:
                tex.append(r"% [Image not found: " + img_rel + "]")
            tex.append(r"\caption{" + caption_text + "}")
            tex.append(r"\label{" + fig_label + "}")
            tex.append(r"\end{figure}")
            tex.append("")

            pending_figure_label = None
            i = j
            continue

        # ── Table: starts with | ──
        if line.strip().startswith("|"):
            close_list()

            # Look back for table caption
            table_caption = None
            for k in range(i - 1, max(i - 5, -1), -1):
                prev = lines[k].strip()
                if not prev or prev == "---":
                    continue
                if prev.startswith("|"):
                    break
                if "Table" in prev or "table" in prev:
                    table_caption = prev
                    break
                break

            # Collect all table lines
            table_lines = []
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                table_lines.append(lines[j])
                j += 1

            # Also collect any italic note after the table
            table_note = None
            table_note_end = j  # Track where the note ends so we can skip past it
            if j < len(lines) and lines[j].strip() == "":
                k = j + 1
                if k < len(lines) and lines[k].strip().startswith("*") and \
                        not lines[k].strip().startswith("**") and \
                        not lines[k].strip().startswith("*Figure"):
                    note = lines[k].strip()
                    if note.startswith("*") and note.endswith("*"):
                        note = note[1:-1]
                    table_note = note
                    table_note_end = k + 1  # Skip past the note line

            headers, rows = parse_table(table_lines)
            if headers:
                table_counter += 1
                n_cols = len(headers)

                # Process caption — strip "Table N." prefix since LaTeX adds its own
                if table_caption:
                    cap = table_caption
                    cap = re.sub(r'\*\*(.+?)\*\*', r'\1', cap)
                    # Remove "Table N." or "Table N:" prefix
                    cap = re.sub(r'^Table\s+\d+[.:]\s*', '', cap)
                    cap = process_line(cap) if cap.strip() else ""
                else:
                    cap = ""

                tab_label = make_label(cap or f"table_{table_counter}", "tab")

                # Determine column spec — use p{} columns for wide tables
                if n_cols > 5:
                    # Wide table: use footnotesize and auto-width columns
                    col_spec = "l" * n_cols
                    font_size = r"\footnotesize"
                else:
                    col_spec = "l" + "c" * (n_cols - 1)
                    font_size = r"\small"

                tex.append(r"\begin{table}[htbp]")
                tex.append(r"\centering")
                if cap:
                    tex.append(r"\caption{" + cap + "}")
                else:
                    tex.append(r"\caption{}")
                tex.append(r"\label{" + tab_label + "}")
                tex.append(font_size)
                # For wide tables, use resizebox
                if n_cols > 5:
                    tex.append(r"\resizebox{\textwidth}{!}{")
                tex.append(r"\begin{tabular}{" + col_spec + "}")
                tex.append(r"\toprule")

                # Headers
                proc_headers = [process_line(h) for h in headers]
                tex.append(" & ".join([r"\textbf{" + h + "}" for h in proc_headers]) + r" \\")
                tex.append(r"\midrule")

                # Rows
                for row in rows:
                    proc_cells = []
                    for idx, cell in enumerate(row):
                        pc = process_line(cell)
                        # Bold entire row if it starts with ** in markdown
                        if cell.strip().startswith("**") and cell.strip().endswith("**"):
                            pc = r"\textbf{" + process_line(cell.strip()[2:-2]) + "}"
                        proc_cells.append(pc)
                    # Pad if fewer cells
                    while len(proc_cells) < n_cols:
                        proc_cells.append("")
                    tex.append(" & ".join(proc_cells) + r" \\")

                tex.append(r"\bottomrule")
                tex.append(r"\end{tabular}")
                if n_cols > 5:
                    tex.append("}")  # close resizebox

                if table_note:
                    tex.append(r"\vspace{0.3em}")
                    tex.append(r"\par\small\textit{" + process_line(table_note) + "}")

                tex.append(r"\end{table}")
                tex.append("")

            i = table_note_end if table_note else j
            continue

        # ── Standalone caption line *Figure N...* not following image → skip ──
        if re.match(r'^\*Figure\s+\d+', line.strip()) or re.match(r'^\*Table\s+\d+', line.strip()):
            i += 1
            continue

        # ── Bullet list: - item ──
        bullet_match = re.match(r'^(\s*)[-*]\s+(.+)', line)
        if bullet_match:
            if not in_list or list_type != "itemize":
                close_list()
                tex.append(r"\begin{itemize}[nosep]")
                in_list = True
                list_type = "itemize"
            item_text = process_line(bullet_match.group(2).strip())
            tex.append(r"  \item " + item_text)
            i += 1
            continue

        # ── Numbered list: N. item ──
        num_match = re.match(r'^(\d+)\.\s+(.+)', line.strip())
        if num_match:
            if not in_list or list_type != "enumerate":
                close_list()
                tex.append(r"\begin{enumerate}[nosep]")
                in_list = True
                list_type = "enumerate"
            item_text = process_line(num_match.group(2).strip())
            tex.append(r"  \item " + item_text)
            i += 1
            continue

        # ── If we were in a list and this is not a list item, close it ──
        if in_list:
            close_list()

        # ── "Summary of Key Findings" subsection ──
        if line.strip().startswith("### Summary"):
            tex.append(r"\subsection*{" + process_line(line.strip()[4:]) + "}")
            tex.append("")
            i += 1
            continue

        # ── Standalone equation lines (short lines with = sign, math-like content) ──
        eq_line = line.strip()
        if (re.match(r'^[A-Za-z_]+\s*=\s*', eq_line) and
                len(eq_line) < 100 and
                not eq_line.startswith("**") and
                not eq_line.startswith("#") and
                '=' in eq_line):
            # Check if surrounded by blank lines (equation-like context)
            prev_blank = (i == 0 or not lines[i - 1].strip())
            next_blank = (i + 1 >= len(lines) or not lines[i + 1].strip())
            if prev_blank and next_blank:
                # Convert to LaTeX equation using specific known patterns
                eq_text = eq_line
                # Known equation: MI = D_KL(P, U) / log(N)
                if "D_KL" in eq_text:
                    eq_text = r"MI = \frac{D_{KL}(P, U)}{\log(N)}"
                # Known equation: z = (PAC_current - mu_baseline) / sigma_baseline
                elif "PAC_current" in eq_text and "mu_baseline" in eq_text:
                    eq_text = r"z = \frac{PAC_{\text{current}} - \mu_{\text{baseline}}}{\sigma_{\text{baseline}}}"
                else:
                    # Generic: wrap subscripts
                    eq_text = re.sub(r'_(\w+)', r'_{\1}', eq_text)
                    eq_text = eq_text.replace("log(", r"\log(")
                tex.append(r"\begin{equation}")
                tex.append("  " + eq_text)
                tex.append(r"\end{equation}")
                tex.append("")
                i += 1
                continue

        # ── Skip bold table/figure caption lines that precede a table or image ──
        if re.match(r'^\*\*(Table|Figure)\s+\d+', line.strip()):
            # Check if a table or image follows within next few lines
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and (lines[j].strip().startswith("|") or lines[j].strip().startswith("![")):
                i += 1
                continue

        # ── Regular paragraph ──
        if line.strip():
            para_lines = [line.strip()]
            j = i + 1
            while j < len(lines):
                nl = lines[j].strip()
                if not nl:
                    break
                if nl.startswith("#"):
                    break
                if nl.startswith("|"):
                    break
                if nl.startswith("!["):
                    break
                if nl == "---":
                    break
                if re.match(r'^[-*]\s+', nl):
                    break
                if re.match(r'^\d+\.\s+', nl):
                    break
                if nl.startswith("**Figure ") and nl.endswith("**"):
                    break
                if nl.startswith("*Figure "):
                    break
                if nl.startswith("**Table "):
                    break
                para_lines.append(nl)
                j += 1
            para_text = " ".join(para_lines)
            para_text = process_line(para_text)
            if para_text.strip():
                tex.append(para_text)
                tex.append("")
            i = j
            continue

        i += 1

    close_list()

    tex.append(r"\end{document}")

    return "\n".join(tex)


def fix_common_issues(tex_source):
    """Post-process the LaTeX source to fix common issues."""

    # Fix double-escaped underscores
    tex_source = tex_source.replace(r"\\_", r"\_")

    # Fix escaped underscores inside \url{}
    def fix_url_underscores(match):
        content = match.group(1)
        content = content.replace(r"\_", "_")
        return r"\url{" + content + "}"
    tex_source = re.sub(r'\\url\{([^}]*)\}', fix_url_underscores, tex_source)

    # Fix escaped underscores inside \label{}
    def fix_label_underscores(match):
        content = match.group(1)
        content = content.replace(r"\_", "_")
        return r"\label{" + content + "}"
    tex_source = re.sub(r'\\label\{([^}]*)\}', fix_label_underscores, tex_source)

    # Fix escaped underscores inside \includegraphics paths
    def fix_includegraphics_underscores(match):
        prefix = match.group(1)
        content = match.group(2)
        content = content.replace(r"\_", "_")
        return prefix + "{" + content + "}"
    tex_source = re.sub(
        r'(\\includegraphics\[[^\]]*\])\{([^}]*)\}',
        fix_includegraphics_underscores,
        tex_source
    )

    # Fix \& inside URLs
    def fix_url_ampersands(match):
        content = match.group(1)
        content = content.replace(r"\&", "&")
        return r"\url{" + content + "}"
    tex_source = re.sub(r'\\url\{([^}]*)\}', fix_url_ampersands, tex_source)

    # Fix \% inside URLs
    def fix_url_percents(match):
        content = match.group(1)
        content = content.replace(r"\%", "%")
        return r"\url{" + content + "}"
    tex_source = re.sub(r'\\url\{([^}]*)\}', fix_url_percents, tex_source)

    # Wrap bare URLs (not already inside \url{})
    tex_source = re.sub(
        r'(?<!\\url\{)(https?://[^\s,\)]+)(?!\})',
        r'\\url{\1}',
        tex_source
    )
    # Fix any escaped chars inside newly wrapped URLs
    def fix_all_url_escapes(match):
        content = match.group(1)
        content = content.replace(r"\_", "_")
        content = content.replace(r"\&", "&")
        content = content.replace(r"\%", "%")
        content = content.replace(r"\#", "#")
        return r"\url{" + content + "}"
    tex_source = re.sub(r'\\url\{([^}]*)\}', fix_all_url_escapes, tex_source)

    # Fix p<0.001 → $p < 0.001$
    tex_source = re.sub(r'(?<!\$)p\s*<\s*0\.001', r'$p < 0.001$', tex_source)
    tex_source = re.sub(r'(?<!\$)p\s*=\s*0\.\d+', lambda m: '$' + m.group(0) + '$', tex_source)

    # Fix N=35 etc. in statistical context
    tex_source = re.sub(r'(?<!\$)N\s*=\s*(\d+)', r'$N = \1$', tex_source)

    # Fix g=+X.XX (Hedges' g)
    tex_source = re.sub(r'(?<!\$)g\s*=\s*([+\-]?\d+\.\d+)', r'$g = \1$', tex_source)

    # Fix W=0
    tex_source = re.sub(r'(?<!\$)W\s*=\s*(\d+)', r'$W = \1$', tex_source)

    # Fix n=17 etc
    tex_source = re.sub(r'(?<!\$)\bn\s*=\s*(\d+)', r'$n = \1$', tex_source)

    # Fix r=0.45 etc (correlation)
    tex_source = re.sub(r'(?<!\$)\br\s*=\s*(\d+\.\d+)', r'$r = \1$', tex_source)

    # Fix double dollars
    tex_source = tex_source.replace("$$", "$ $")

    # Fix triple-or-more newlines
    tex_source = re.sub(r'\n{4,}', '\n\n\n', tex_source)

    return tex_source


def main():
    print(f"Reading: {PAPER_MD}")
    if not os.path.exists(PAPER_MD):
        print(f"ERROR: Markdown file not found: {PAPER_MD}")
        sys.exit(1)

    print("Converting markdown to LaTeX...")
    tex_source = generate_latex()

    print("Post-processing LaTeX source...")
    tex_source = fix_common_issues(tex_source)

    print(f"Writing: {OUTPUT_TEX}")
    with open(OUTPUT_TEX, "w", encoding="utf-8") as f:
        f.write(tex_source)

    tex_size = os.path.getsize(OUTPUT_TEX)
    print(f"  .tex file size: {tex_size / 1024:.1f} KB")

    # Compile with tectonic
    if not os.path.exists(TECTONIC):
        print(f"WARNING: tectonic not found at {TECTONIC}")
        print("  Skipping PDF compilation. You can compile manually:")
        print(f"  {TECTONIC} {OUTPUT_TEX}")
        return

    print(f"\nCompiling with tectonic...")
    tex_dir = os.path.dirname(OUTPUT_TEX)
    try:
        result = subprocess.run(
            [TECTONIC, OUTPUT_TEX],
            cwd=tex_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print("ERROR: tectonic compilation failed!")
            print("STDOUT:", result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            sys.exit(1)
        else:
            print("  Compilation successful!")
            if result.stderr:
                # Show warnings (truncated)
                warnings = [l for l in result.stderr.split('\n') if 'warning' in l.lower()]
                if warnings:
                    print(f"  ({len(warnings)} warnings)")
    except subprocess.TimeoutExpired:
        print("ERROR: tectonic compilation timed out (300s)")
        sys.exit(1)

    # Report results
    if os.path.exists(OUTPUT_PDF):
        pdf_size = os.path.getsize(OUTPUT_PDF)
        print(f"\nOutput PDF: {OUTPUT_PDF}")
        print(f"  File size: {pdf_size / 1024 / 1024:.2f} MB")

        # Count pages from the tectonic log file
        log_path = OUTPUT_TEX.replace(".tex", ".log")
        page_count = None
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="replace") as lf:
                    log_text = lf.read()
                m = re.search(r'Output written.*?\((\d+)\s*page', log_text)
                if m:
                    page_count = int(m.group(1))
            except Exception:
                pass
        if page_count:
            print(f"  Page count: {page_count}")
        else:
            print("  Page count: (unable to determine)")
    else:
        print(f"WARNING: PDF not found at {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
