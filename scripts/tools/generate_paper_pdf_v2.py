#!/usr/bin/env python3
"""
Generate publication-grade PDF from RESEARCH_PAPER.md using fpdf2.
V2: Fixes header overlap, table formatting, R^2 rendering, figure labels,
    keywords placement, and overall visual cohesion.
"""

import re
import os
from fpdf import FPDF

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAPER_MD = os.path.join(PROJECT_ROOT, "submission", "paper", "RESEARCH_PAPER.md")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
OUTPUT_PDF = os.path.join(PROJECT_ROOT, "submission", "paper", "RESEARCH_PAPER_v2.pdf")

# Font config
FONT = "TNR"
FONT_FILES = {
    "": "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "B": "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    "I": "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
    "BI": "/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf",
}

# Layout
LEFT_MARGIN = 25
RIGHT_MARGIN = 25
TOP_MARGIN = 25
BOTTOM_MARGIN = 25
BODY_SIZE = 10
LINE_H = 4.8
PAGE_W = 215.9  # letter


def clean(text):
    """Strip markdown formatting and normalize unicode for PDF rendering."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
    # Keep common superscripts that render in Times New Roman
    # Only flatten obscure ones
    sups = str.maketrans('\u2070\u2074\u2075\u2077\u2078\u2079',
                         '045789')
    text = text.translate(sups)
    # TNR doesn't have superscript 6 or superscript minus — replace them
    text = text.replace('\u2076', '6')
    text = text.replace('\u207b', '-')
    # Replace x10⁻⁶ pattern with x10-6
    text = re.sub(r'[×x]\s*10[\-]6', ' x10^-6', text)
    text = text.replace('\u2014', ' \u2014 ')
    text = text.replace('\u2013', '\u2013')
    text = text.replace('\u2019', "'")
    text = text.replace('\u201c', '"')
    text = text.replace('\u201d', '"')
    text = text.replace('\u03b2', '\u03b2')  # keep beta
    text = text.replace('\u03b8', '\u03b8')  # keep theta
    text = text.replace('\u03c3', '\u03c3')  # keep sigma
    text = text.replace('\u03c6', '\u03c6')  # keep phi
    text = text.replace('\u03b4', '\u03b4')  # keep delta
    return text.strip()


def resolve_img(rel_path):
    """Resolve image path relative to submission/paper/."""
    candidates = [
        os.path.normpath(os.path.join(PROJECT_ROOT, "submission", "paper", rel_path)),
        os.path.normpath(os.path.join(PROJECT_ROOT, rel_path.lstrip('./'))),
        os.path.join(FIGURES_DIR, os.path.basename(rel_path)),
        os.path.join(FIGURES_DIR, "ai_generated", os.path.basename(rel_path)),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


class PaperPDF(FPDF):

    def __init__(self):
        super().__init__("P", "mm", "letter")
        self.set_auto_page_break(True, BOTTOM_MARGIN)
        self.set_margins(LEFT_MARGIN, TOP_MARGIN, RIGHT_MARGIN)
        for style, path in FONT_FILES.items():
            self.add_font(FONT, style, path)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_y(10)
        self.set_font(FONT, "I", 7.5)
        self.set_text_color(130, 130, 130)
        self.cell(0, 4, "Chughtai \u2014 Closed-Loop 40 Hz Entrainment for Alzheimer\u2019s Disease",
                  align="C")
        self.set_draw_color(200, 200, 200)
        self.line(LEFT_MARGIN, 16, PAGE_W - RIGHT_MARGIN, 16)
        self.set_y(TOP_MARGIN)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT, "", 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, str(self.page_no()), align="C")

    # ---- writing helpers ----

    def title_block(self, title, author):
        self.set_font(FONT, "B", 15)
        self.multi_cell(0, 6.5, title, align="C")
        self.ln(4)
        self.set_font(FONT, "", 11)
        self.cell(0, 5, author, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)
        cx = PAGE_W / 2
        self.set_draw_color(0, 0, 0)
        self.line(cx - 25, self.get_y(), cx + 25, self.get_y())
        self.ln(6)

    def abstract_block(self, text):
        self.set_font(FONT, "B", 10)
        self.cell(0, 5, "Abstract", new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)
        indent = 30
        w = PAGE_W - indent - RIGHT_MARGIN
        self.set_left_margin(indent)
        self.set_x(indent)
        self.set_font(FONT, "", 9)
        self.multi_cell(w, 4, text, align="J")
        self.set_left_margin(LEFT_MARGIN)
        self.ln(4)
        self.set_draw_color(0, 0, 0)
        self.line(LEFT_MARGIN, self.get_y(), PAGE_W - RIGHT_MARGIN, self.get_y())
        self.ln(6)

    def section(self, text):
        if self.get_y() > self.h - 40:
            self.add_page()
        self.ln(3)
        self.set_font(FONT, "B", 12)
        self.multi_cell(0, 5.5, text, align="L")
        self.ln(2)

    def subsection(self, text):
        if self.get_y() > self.h - 35:
            self.add_page()
        self.ln(2)
        self.set_font(FONT, "B", 10.5)
        self.multi_cell(0, 5, text, align="L")
        self.ln(1)

    def subsubsection(self, text):
        self.ln(1.5)
        self.set_font(FONT, "BI", 10)
        self.multi_cell(0, 4.5, text, align="L")
        self.ln(0.5)

    def body(self, text):
        self.set_font(FONT, "", BODY_SIZE)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, LINE_H, text, align="J")
        self.ln(1.5)

    def bold_para(self, bold, rest):
        self.set_font(FONT, "B", BODY_SIZE)
        self.write(LINE_H, bold + " ")
        self.set_font(FONT, "", BODY_SIZE)
        self.write(LINE_H, rest)
        self.ln(LINE_H + 1.5)

    def bullet(self, text):
        self.set_font(FONT, "", 9.5)
        x0 = LEFT_MARGIN + 5
        self.set_x(x0)
        self.cell(4, LINE_H, "\u2022")
        self.multi_cell(PAGE_W - RIGHT_MARGIN - x0 - 4, LINE_H, text, align="L")
        self.ln(0.5)

    def numbered(self, num, text):
        self.set_font(FONT, "", 9.5)
        x0 = LEFT_MARGIN + 5
        self.set_x(x0)
        self.cell(7, LINE_H, f"{num}.")
        self.multi_cell(PAGE_W - RIGHT_MARGIN - x0 - 7, LINE_H, text, align="L")
        self.ln(0.5)

    def figure(self, img_path, caption):
        if not img_path or not os.path.exists(img_path):
            self.body(f"[Figure not found: {img_path}]")
            return
        max_w = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN - 10
        if self.get_y() + 70 > self.h - BOTTOM_MARGIN:
            self.add_page()
        self.ln(3)
        self.image(img_path, x=LEFT_MARGIN + 5, w=max_w)
        self.ln(2)
        # Caption in italic
        self.set_font(FONT, "I", 8.5)
        self.set_text_color(50, 50, 50)
        cap_margin = LEFT_MARGIN + 8
        self.set_left_margin(cap_margin)
        self.set_x(cap_margin)
        self.multi_cell(PAGE_W - cap_margin - RIGHT_MARGIN - 3, 3.8, caption, align="J")
        self.set_left_margin(LEFT_MARGIN)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def table(self, headers, rows, caption=None):
        if caption:
            self.set_font(FONT, "B", 9)
            self.multi_cell(0, 4.5, caption, align="L")
            self.ln(1)

        n = len(headers)
        avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN

        # Determine if this is a wide table (>5 columns or long content)
        total_content = sum(max(len(h), max((len(r[i]) if i < len(r) else 0) for r in rows) if rows else 0) for i, h in enumerate(headers))
        is_wide = n > 5 or total_content > 200
        font_size = 6 if is_wide else 7.5
        row_h = 4 if is_wide else 4.5
        hdr_font = 6.5 if is_wide else 7.5

        # Smart column sizing based on content
        max_lens = []
        for i, h in enumerate(headers):
            col_max = len(h)
            for r in rows:
                if i < len(r):
                    col_max = max(col_max, len(r[i]))
            max_lens.append(col_max)

        total = sum(max_lens) or 1
        col_w = [max(l / total * avail, 12) for l in max_lens]
        sw = sum(col_w)
        if sw > avail:
            col_w = [w * avail / sw for w in col_w]

        # Check page fit
        needed = (len(rows) + 2) * (row_h + 1) + 6
        if self.get_y() + needed > self.h - BOTTOM_MARGIN:
            self.add_page()

        # Header
        self.set_font(FONT, "B", hdr_font)
        self.set_fill_color(235, 235, 235)
        self.set_draw_color(160, 160, 160)
        x0 = LEFT_MARGIN
        self.set_x(x0)
        for i, h in enumerate(headers):
            txt = clean(h.strip())
            # Don't truncate headers — they are important labels
            self.cell(col_w[i], row_h + 0.5, txt, border=1, fill=True, align="C")
        self.ln()

        # Rows
        self.set_font(FONT, "", font_size)
        for row in rows:
            self.set_x(x0)
            for i, cell_val in enumerate(row):
                w = col_w[i] if i < len(col_w) else col_w[-1]
                txt = clean(cell_val.strip())
                # Truncate content to fit cell width
                max_chars = int(w / (font_size * 0.22))
                if len(txt) > max_chars:
                    txt = txt[:max_chars - 2] + ".."
                al = "L" if i == 0 else "C"
                self.cell(w, row_h, txt, border=1, align=al)
            self.ln()
        self.ln(3)

    def ref_line(self, text):
        self.set_font(FONT, "", 7.5)
        self.multi_cell(0, 3.5, text, align="L")
        self.ln(0.5)


def parse_table(lines):
    """Parse markdown table lines into headers and data rows."""
    headers = []
    rows = []
    for line in lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if all(set(c) <= {'-', ':', ' '} for c in cells if c):
            continue  # separator
        if not headers:
            headers = cells
        else:
            rows.append(cells)
    return headers, rows


def generate():
    pdf = PaperPDF()
    pdf.add_page()

    with open(PAPER_MD, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    i = 0
    in_table = False
    table_lines = []
    table_cap = None

    while i < len(lines):
        line = lines[i]

        # Skip bottom metadata
        if line.startswith('Word count:') or line.startswith('Figures:') or \
           line.startswith('Tables:') or line.startswith('Last verified:') or \
           line.startswith('References:'):
            i += 1
            continue

        # Title
        if line.startswith('# ') and not line.startswith('## '):
            pdf.title_block(clean(line[2:]), "")
            i += 1
            continue

        # Author
        if line.startswith('**Amaar'):
            pdf.title_block("", clean(line))
            i += 1
            continue

        # HR
        if line.strip() == '---':
            i += 1
            continue

        # Section ##
        if line.startswith('## ') and not line.startswith('### '):
            sec = clean(line[3:])

            if sec == 'Abstract':
                i += 1
                paras = []
                while i < len(lines) and not lines[i].startswith('**Keywords'):
                    if lines[i].strip() and lines[i].strip() != '---':
                        paras.append(clean(lines[i]))
                    i += 1
                pdf.abstract_block(' '.join(paras))
                # Skip keywords line (don't render in body per user request)
                if i < len(lines) and lines[i].startswith('**Keywords'):
                    i += 1
                continue

            elif sec == 'References':
                pdf.section("References")
                i += 1
                while i < len(lines):
                    rl = lines[i].strip()
                    if rl.startswith('Word count') or rl.startswith('Figures:') or \
                       rl.startswith('Tables:') or rl.startswith('Last verified') or \
                       rl.startswith('References:') or rl == '---':
                        i += 1
                        continue
                    if rl:
                        pdf.ref_line(clean(rl))
                    i += 1
                continue
            else:
                pdf.section(sec)
                i += 1
                continue

        # Subsection ###
        if line.startswith('### ') and not line.startswith('#### '):
            pdf.subsection(clean(line[4:]))
            i += 1
            continue

        # Subsubsection ####
        if line.startswith('#### '):
            pdf.subsubsection(clean(line[5:]))
            i += 1
            continue

        # Figures
        if line.strip().startswith('!['):
            match = re.search(r'!\[.*?\]\((.*?)\)', line)
            if match:
                img = resolve_img(match.group(1))
                # Collect caption from following italic lines
                cap_parts = []
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('*') and \
                      not lines[j].strip().startswith('**'):
                    cl = lines[j].strip()
                    if cl.startswith('*') and cl.endswith('*'):
                        cl = cl[1:-1]
                    cap_parts.append(clean(cl))
                    j += 1
                pdf.figure(img, ' '.join(cap_parts))
                i = j
                continue
            i += 1
            continue

        # Skip standalone figure label lines like "**Figure N.**"
        if re.match(r'\*\*Figure \d+\.\*\*', line.strip()):
            i += 1
            continue

        # Standalone caption lines
        if line.strip().startswith('*Figure') or line.strip().startswith('*Table'):
            i += 1
            continue

        # Table start
        if line.strip().startswith('|') and not in_table:
            in_table = True
            table_lines = [line]
            # Look back for table caption — take only the FIRST "Table" line found
            table_cap = None
            for k in range(i - 1, max(i - 5, -1), -1):
                prev = lines[k].strip()
                if prev and not prev.startswith('|') and prev != '---':
                    if 'Table' in prev or 'table' in prev:
                        if not table_cap:  # Only take the first one
                            table_cap = clean(prev)
                    break
            i += 1
            continue

        if in_table:
            if line.strip().startswith('|'):
                table_lines.append(line)
                i += 1
                continue
            else:
                in_table = False
                hdrs, rws = parse_table(table_lines)
                if hdrs:
                    pdf.table([clean(h) for h in hdrs],
                              [[clean(c) for c in r] for r in rws],
                              table_cap)
                table_lines = []
                table_cap = None
                continue

        # Bold-start paragraphs — skip if it's a table/figure caption (will be handled by table parser)
        bm = re.match(r'\*\*(.+?)\*\*\s*(.*)', line.strip())
        if bm and line.strip() and not line.startswith('#'):
            bp = bm.group(1)
            rest = bm.group(2)
            # Skip if this is a table/figure caption right before a table
            is_caption = (bp.startswith('Table ') or bp.endswith(':') or bp.endswith(':.'))
            if is_caption:
                # Check if a table follows within the next 3 lines
                peek = i + 1
                while peek < min(i + 4, len(lines)) and not lines[peek].strip():
                    peek += 1
                if peek < len(lines) and lines[peek].strip().startswith('|'):
                    # This bold line is a table caption — skip it (table parser will pick it up)
                    i += 1
                    continue
            j = i + 1
            while j < len(lines) and lines[j].strip() and \
                  not lines[j].startswith('#') and not lines[j].startswith('|') and \
                  not lines[j].startswith('!') and not lines[j].startswith('**') and \
                  not lines[j].startswith('---') and not lines[j].startswith('- '):
                rest += ' ' + lines[j].strip()
                j += 1
            pdf.bold_para(clean(bp) + ".", clean(rest))
            i = j
            continue

        # Bullets
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            pdf.bullet(clean(line.strip()[2:]))
            i += 1
            continue

        # Numbered list
        nm = re.match(r'^(\d+)\.\s+(.+)', line.strip())
        if nm:
            pdf.numbered(nm.group(1), clean(nm.group(2)))
            i += 1
            continue

        # Regular paragraph
        if line.strip():
            para = [line.strip()]
            j = i + 1
            while j < len(lines):
                nl = lines[j].strip()
                if not nl or nl.startswith('#') or nl.startswith('|') or \
                   nl.startswith('!') or nl.startswith('---') or \
                   nl.startswith('- ') or nl.startswith('* ') or \
                   re.match(r'^\d+\.', nl) or nl.startswith('**Figure') or \
                   nl.startswith('**Table'):
                    break
                para.append(nl)
                j += 1
            text = clean(' '.join(para))
            if text:
                pdf.body(text)
            i = j
            continue

        i += 1

    pdf.output(OUTPUT_PDF)
    print(f"PDF generated: {OUTPUT_PDF}")
    print(f"Pages: {pdf.page_no()}")
    print(f"Size: {os.path.getsize(OUTPUT_PDF) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    generate()
