#!/usr/bin/env python3
"""
Generate publication-grade PDF from RESEARCH_PAPER.md using fpdf2.

Produces a professional two-column journal-style layout with:
- Times New Roman font family
- Two-column body text (single-column abstract/title)
- Proper figure placement with captions
- Formatted tables
- Numbered references
- Headers and page numbers
"""

import re
import os
import textwrap
from fpdf import FPDF

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAPER_MD = os.path.join(PROJECT_ROOT, "submission", "paper", "RESEARCH_PAPER.md")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
OUTPUT_PDF = os.path.join(PROJECT_ROOT, "submission", "paper", "RESEARCH_PAPER.pdf")


class ResearchPaperPDF(FPDF):
    """Publication-grade research paper PDF generator."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="letter")
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(left=20, top=20, right=20)
        # Use Unicode TTF fonts for full character support
        self.add_font("DejaVu", "", "/System/Library/Fonts/Supplemental/Times New Roman.ttf", uni=True)
        self.add_font("DejaVu", "B", "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf", uni=True)
        self.add_font("DejaVu", "I", "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf", uni=True)
        self.add_font("DejaVu", "BI", "/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf", uni=True)
        # Track state
        self.in_abstract = False
        self.current_section = ""

    def header(self):
        if self.page_no() > 1:
            self.set_font("DejaVu", "I", 8)
            self.set_text_color(100, 100, 100)
            header_text = "Chughtai -- Closed-Loop 40 Hz Entrainment for Alzheimer's Disease"
            self.cell(0, 6, header_text, align="C")
            self.ln(2)
            self.set_draw_color(180, 180, 180)
            self.line(20, self.get_y(), self.w - 20, self.get_y())
            self.ln(4)
            self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, str(self.page_no()), align="C")

    def write_title(self, title):
        """Write the paper title centered."""
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 7, title, align="C")
        self.ln(3)

    def write_author(self, author):
        """Write author name centered."""
        self.set_font("DejaVu", "", 12)
        self.cell(0, 6, author, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        # Divider line
        self.set_draw_color(0, 0, 0)
        mid = self.w / 2
        self.line(mid - 30, self.get_y(), mid + 30, self.get_y())
        self.ln(6)

    def write_abstract(self, text):
        """Write abstract in single column, indented, with italic label."""
        self.set_font("DejaVu", "B", 11)
        self.cell(0, 5, "Abstract", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        # Indent abstract
        left_margin = 25
        right_margin = 25
        self.set_left_margin(left_margin)
        self.set_right_margin(right_margin)
        self.set_x(left_margin)
        self.set_font("DejaVu", "", 9.5)
        self.multi_cell(self.w - left_margin - right_margin, 4.2, text, align="J")
        # Reset margins
        self.set_left_margin(20)
        self.set_right_margin(20)
        self.ln(3)

    def write_keywords(self, keywords):
        """Write keywords line."""
        left_margin = 25
        self.set_left_margin(left_margin)
        self.set_x(left_margin)
        self.set_font("DejaVu", "B", 9)
        self.write(4, "Keywords: ")
        self.set_font("DejaVu", "I", 9)
        self.write(4, keywords)
        self.set_left_margin(20)
        self.ln(8)
        # Divider
        self.set_draw_color(0, 0, 0)
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(6)

    def write_section_header(self, text):
        """Write a major section header (## level)."""
        self.ln(4)
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5.5, text, align="L")
        self.ln(2)

    def write_subsection_header(self, text):
        """Write a subsection header (### level)."""
        self.ln(3)
        self.set_font("DejaVu", "B", 10.5)
        self.multi_cell(0, 5, text, align="L")
        self.ln(1)

    def write_subsubsection_header(self, text):
        """Write a sub-subsection header (#### level)."""
        self.ln(2)
        self.set_font("DejaVu", "BI", 10)
        self.multi_cell(0, 4.5, text, align="L")
        self.ln(1)

    def write_body_text(self, text):
        """Write body paragraph text."""
        self.set_font("DejaVu", "", 10)
        self.set_text_color(0, 0, 0)
        # Handle bold/italic inline
        self.multi_cell(0, 4.5, text, align="J")
        self.ln(1.5)

    def write_bold_paragraph(self, bold_part, rest):
        """Write a paragraph starting with bold text."""
        self.set_font("DejaVu", "B", 10)
        self.write(4.5, bold_part)
        self.set_font("DejaVu", "", 10)
        self.write(4.5, rest)
        self.ln(5)

    def write_figure(self, img_path, caption, fig_num):
        """Insert a figure with caption."""
        if not os.path.exists(img_path):
            self.write_body_text(f"[Figure {fig_num}: {img_path} not found]")
            return

        self.ln(4)
        # Draw a light box around figure area
        self.set_draw_color(200, 200, 200)

        # Calculate image width (full column width minus small margins)
        img_w = self.w - 44  # 22mm margin each side
        x_pos = 22

        # Check if we need a new page
        if self.get_y() + 80 > self.h - 25:
            self.add_page()

        self.image(img_path, x=x_pos, w=img_w)
        self.ln(2)

        # Caption
        self.set_font("DejaVu", "", 8.5)
        self.set_text_color(60, 60, 60)
        self.set_left_margin(25)
        self.set_right_margin(25)
        self.set_x(25)
        self.multi_cell(self.w - 50, 3.8, caption, align="J")
        self.set_left_margin(20)
        self.set_right_margin(20)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def write_table(self, headers, rows, caption=None):
        """Write a formatted table."""
        self.ln(2)
        if caption:
            self.set_font("DejaVu", "B", 9)
            self.multi_cell(0, 4, caption, align="L")
            self.ln(1)

        # Calculate column widths
        available_w = self.w - 40
        n_cols = len(headers)
        col_w = available_w / n_cols

        # Adjust column widths based on content
        col_widths = []
        for i, h in enumerate(headers):
            max_len = len(h)
            for row in rows:
                if i < len(row):
                    max_len = max(max_len, len(row[i]))
            col_widths.append(max_len)

        total = sum(col_widths)
        col_widths = [w / total * available_w for w in col_widths]

        # Check if table fits on page
        table_height = (len(rows) + 1) * 5 + 4
        if self.get_y() + table_height > self.h - 25:
            self.add_page()

        # Header row
        self.set_font("DejaVu", "B", 8)
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(180, 180, 180)

        x_start = 20
        self.set_x(x_start)
        for i, h in enumerate(headers):
            w = col_widths[i]
            self.cell(w, 5, h.strip(), border=1, fill=True, align="C")
        self.ln()

        # Data rows
        self.set_font("DejaVu", "", 7.5)
        for row in rows:
            self.set_x(x_start)
            for i, cell_text in enumerate(row):
                w = col_widths[i] if i < len(col_widths) else col_widths[-1]
                # Bold the first column if it seems like a label
                align = "C" if i > 0 else "L"
                cell_text_clean = cell_text.strip().replace("**", "")
                self.cell(w, 4.5, cell_text_clean, border=1, align=align)
            self.ln()

        self.ln(3)


def clean_markdown(text):
    """Remove markdown formatting for plain text output."""
    # Remove bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove italic
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove inline code
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Remove image references
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove link syntax but keep text
    text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
    # Clean up unicode
    text = text.replace('β', 'beta')
    text = text.replace('×', 'x')
    text = text.replace('≈', '~')
    text = text.replace('≥', '>=')
    text = text.replace('≤', '<=')
    text = text.replace('±', '+/-')
    text = text.replace('µ', 'u')
    text = text.replace('\u2014', ' -- ')
    text = text.replace('\u2013', '-')
    text = text.replace('\u2019', "'")
    text = text.replace('\u201c', '"')
    text = text.replace('\u201d', '"')
    text = text.replace('⁻', '-')
    text = text.replace('⁶', '6')
    text = text.replace('⁻⁶', '-6')
    text = text.replace('¹', '1')
    text = text.replace('²', '2')
    text = text.replace('³', '3')
    text = text.replace('⁴', '4')
    text = text.replace('⁵', '5')
    text = text.replace('φ', 'phi')
    text = text.replace('σ', 'sigma')
    text = text.replace('δ', 'delta')
    text = text.replace('Aβ', 'A-beta')
    text = text.replace('∆', 'Delta')
    return text.strip()


def parse_table(lines):
    """Parse a markdown table into headers and rows."""
    headers = []
    rows = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if i == 0 or not headers:
            # Check if this is a separator line
            if all(set(c.strip()) <= {'-', ':', ' '} for c in cells):
                continue
            if not headers:
                headers = cells
            else:
                rows.append(cells)
        else:
            # Check if separator
            if all(set(c.strip()) <= {'-', ':', ' '} for c in cells):
                continue
            rows.append(cells)
    return headers, rows


def generate_pdf():
    """Main PDF generation function."""
    pdf = ResearchPaperPDF()
    pdf.add_page()

    # Read the markdown
    with open(PAPER_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    i = 0
    in_table = False
    table_lines = []
    table_caption = None
    skip_metadata = False  # Skip the metadata at bottom

    while i < len(lines):
        line = lines[i]

        # Skip end metadata
        if line.startswith('Word count:') or line.startswith('Figures:') or line.startswith('Tables:') or line.startswith('Last verified:'):
            i += 1
            continue

        # Title (# level)
        if line.startswith('# ') and not line.startswith('## '):
            title = clean_markdown(line[2:])
            pdf.write_title(title)
            i += 1
            continue

        # Author
        if line.startswith('**Amaar'):
            author = clean_markdown(line)
            pdf.write_author(author)
            i += 1
            continue

        # Horizontal rule - skip
        if line.strip() == '---':
            i += 1
            continue

        # Section header (##)
        if line.startswith('## ') and not line.startswith('### '):
            section = clean_markdown(line[3:])
            if section == 'Abstract':
                # Collect abstract text
                i += 1
                abstract_text = []
                while i < len(lines) and not lines[i].startswith('**Keywords'):
                    if lines[i].strip() and not lines[i].startswith('---'):
                        abstract_text.append(clean_markdown(lines[i]))
                    i += 1
                pdf.write_abstract(' '.join(abstract_text))
                # Keywords
                if i < len(lines) and lines[i].startswith('**Keywords'):
                    kw = clean_markdown(lines[i])
                    kw = kw.replace('Keywords: ', '').replace('Keywords:', '')
                    pdf.write_keywords(kw)
                    i += 1
                continue
            elif section == 'References':
                # Special handling for references section
                pdf.write_section_header(section)
                i += 1
                while i < len(lines):
                    rline = lines[i].strip()
                    if rline.startswith('Word count') or rline.startswith('Figures:') or rline.startswith('Tables:') or rline.startswith('References:') or rline.startswith('Last verified'):
                        i += 1
                        continue
                    if rline == '---':
                        i += 1
                        continue
                    if rline:
                        ref_text = clean_markdown(rline)
                        pdf.set_font("DejaVu", "", 8)
                        pdf.multi_cell(0, 3.5, ref_text, align="L")
                        pdf.ln(0.8)
                    i += 1
                continue
            else:
                pdf.write_section_header(section)
                i += 1
                continue

        # Subsection (###)
        if line.startswith('### ') and not line.startswith('#### '):
            sub = clean_markdown(line[4:])
            pdf.write_subsection_header(sub)
            i += 1
            continue

        # Sub-subsection (####)
        if line.startswith('#### '):
            subsub = clean_markdown(line[5:])
            pdf.write_subsubsection_header(subsub)
            i += 1
            continue

        # Figure references
        if line.strip().startswith('!['):
            # Extract image path
            match = re.search(r'!\[.*?\]\((.*?)\)', line)
            if match:
                img_rel = match.group(1)
                # Resolve path relative to submission/paper/
                img_path = os.path.normpath(os.path.join(PROJECT_ROOT, "submission", "paper", img_rel))
                if not os.path.exists(img_path):
                    # Try from project root
                    img_path = os.path.normpath(os.path.join(PROJECT_ROOT, img_rel.lstrip('../')))
                if not os.path.exists(img_path):
                    # Try results/figures directly
                    basename = os.path.basename(img_rel)
                    img_path = os.path.join(FIGURES_DIR, basename)

                # Get caption from next lines
                caption = ""
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('*') and not lines[j].strip().startswith('**'):
                    cap_line = lines[j].strip()
                    if cap_line.startswith('*') and cap_line.endswith('*'):
                        cap_line = cap_line[1:-1]
                    caption += clean_markdown(cap_line) + " "
                    j += 1

                # Extract figure number
                fig_match = re.search(r'Figure (\d+)', caption)
                fig_num = fig_match.group(1) if fig_match else "?"

                pdf.write_figure(img_path, caption.strip(), fig_num)
                i = j
                continue
            i += 1
            continue

        # Figure caption lines (already handled above, skip if standalone)
        if line.strip().startswith('*Figure') or line.strip().startswith('*Table'):
            # Skip standalone captions (already captured with figure)
            i += 1
            continue

        # Table detection
        if line.strip().startswith('|') and not in_table:
            in_table = True
            table_lines = [line]
            # Check if previous non-empty line is a table caption
            for k in range(i - 1, max(i - 4, -1), -1):
                prev = lines[k].strip()
                if prev and not prev.startswith('|') and not prev == '---':
                    if 'Table' in prev or 'table' in prev:
                        table_caption = clean_markdown(prev)
                    break
            i += 1
            continue

        if in_table:
            if line.strip().startswith('|'):
                table_lines.append(line)
                i += 1
                continue
            else:
                # End of table
                in_table = False
                headers, rows = parse_table(table_lines)
                if headers:
                    clean_headers = [clean_markdown(h) for h in headers]
                    clean_rows = [[clean_markdown(c) for c in r] for r in rows]
                    pdf.write_table(clean_headers, clean_rows, table_caption)
                table_lines = []
                table_caption = None
                # Don't increment i, process current line
                continue

        # Bold-start paragraphs (like **Contribution 1:** ...)
        bold_match = re.match(r'\*\*(.+?)\*\*\s*(.*)', line.strip())
        if bold_match and line.strip() and not line.startswith('#'):
            bold_part = bold_match.group(1)
            rest = bold_match.group(2)
            # Check for continuation lines
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith('#') and not lines[j].startswith('|') and not lines[j].startswith('!') and not lines[j].startswith('**') and not lines[j].startswith('---') and not lines[j].startswith('- '):
                rest += ' ' + lines[j].strip()
                j += 1
            pdf.write_bold_paragraph(clean_markdown(bold_part) + " ", clean_markdown(rest))
            i = j
            continue

        # Bullet points
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            bullet_text = clean_markdown(line.strip()[2:])
            pdf.set_font("DejaVu", "", 9.5)
            pdf.set_x(25)
            pdf.cell(5, 4.5, chr(8226))  # bullet character
            pdf.multi_cell(0, 4.5, bullet_text, align="L")
            pdf.ln(0.5)
            i += 1
            continue

        # Numbered list
        num_match = re.match(r'^(\d+)\.\s+(.+)', line.strip())
        if num_match:
            num = num_match.group(1)
            list_text = clean_markdown(num_match.group(2))
            pdf.set_font("DejaVu", "", 9.5)
            pdf.set_x(25)
            pdf.cell(8, 4.5, f"{num}.")
            pdf.multi_cell(0, 4.5, list_text, align="L")
            pdf.ln(0.5)
            i += 1
            continue

        # Regular paragraph text
        if line.strip():
            # Collect full paragraph
            para_lines = [line.strip()]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line or next_line.startswith('#') or next_line.startswith('|') or next_line.startswith('!') or next_line.startswith('---') or next_line.startswith('- ') or next_line.startswith('* ') or re.match(r'^\d+\.', next_line) or next_line.startswith('**Figure') or next_line.startswith('**Table'):
                    break
                para_lines.append(next_line)
                j += 1

            para_text = ' '.join(para_lines)
            para_text = clean_markdown(para_text)
            if para_text:
                pdf.write_body_text(para_text)
            i = j
            continue

        i += 1

    # Save
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    pdf.output(OUTPUT_PDF)
    print(f"PDF generated: {OUTPUT_PDF}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    generate_pdf()
