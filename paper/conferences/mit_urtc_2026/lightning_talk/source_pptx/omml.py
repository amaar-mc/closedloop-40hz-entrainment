"""Tiny builder for native PowerPoint equations (OMML inside DrawingML text).

Equations are written straight as OMML so they open as real, editable PowerPoint equations
(double-click to edit) set in Cambria Math.
"""

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _italic_char(c):
    """Map a Latin or Greek letter to its Unicode mathematical-italic form (how PowerPoint stores it)."""
    if "A" <= c <= "Z":
        return chr(0x1D434 + ord(c) - ord("A"))
    if "a" <= c <= "z":
        return "ℎ" if c == "h" else chr(0x1D44E + ord(c) - ord("a"))
    greek = {"ρ": "\U0001D70C", "ϕ": "\U0001D719", "φ": "\U0001D711", "π": "\U0001D70B", "Δ": "\U0001D6E5"}
    return greek.get(c, c)


class Style:
    def __init__(self, size_pt, color="16202A"):
        self.sz = int(round(size_pt * 100))
        self.color = color

    def rpr(self, italic):
        return (f'<a:rPr lang="en-US" sz="{self.sz}" b="0" i="{1 if italic else 0}" dirty="0">'
                f'<a:solidFill><a:srgbClr val="{self.color}"/></a:solidFill>'
                f'<a:latin typeface="Cambria Math" panose="02040503050406030204" pitchFamily="18" charset="0"/>'
                f'</a:rPr>')


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def v(text, st):
    """Italic math variable(s), e.g. v('N', st)."""
    return (f'<m:r>{st.rpr(True)}<m:t>{_esc("".join(_italic_char(c) for c in text))}</m:t></m:r>')


def t(text, st):
    """Upright math text: numbers, operators, names like PLV, words like 'sound'."""
    return (f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr>{st.rpr(False)}<m:t>{_esc(text)}</m:t></m:r>')


def sub(base, s):
    return f'<m:sSub><m:e>{base}</m:e><m:sub>{s}</m:sub></m:sSub>'


def sup(base, s):
    return f'<m:sSup><m:e>{base}</m:e><m:sup>{s}</m:sup></m:sSup>'


def subsup(base, s, p):
    return f'<m:sSubSup><m:e>{base}</m:e><m:sub>{s}</m:sub><m:sup>{p}</m:sup></m:sSubSup>'


def frac(num, den, small=False):
    typ = '<m:fPr><m:type m:val="lin"/></m:fPr>' if False else ''
    return f'<m:f>{typ}<m:num>{num}</m:num><m:den>{den}</m:den></m:f>'


def nary(chr_, lo, hi, body):
    return (f'<m:nary><m:naryPr><m:chr m:val="{chr_}"/><m:limLoc m:val="undOvr"/>'
            f'<m:grow m:val="1"/></m:naryPr><m:sub>{lo}</m:sub><m:sup>{hi}</m:sup><m:e>{body}</m:e></m:nary>')


def delim(body, beg="(", end=")"):
    return (f'<m:d><m:dPr><m:begChr m:val="{beg}"/><m:endChr m:val="{end}"/><m:grow m:val="1"/></m:dPr>'
            f'<m:e>{body}</m:e></m:d>')


def bar(body):
    return f'<m:bar><m:barPr><m:pos m:val="top"/></m:barPr><m:e>{body}</m:e></m:bar>'


def omath(*parts):
    return f'<m:oMath>{"".join(parts)}</m:oMath>'


def para(omaths, jc="left"):
    """One DrawingML paragraph holding a display equation (one or more stacked oMath lines)."""
    lines = "".join(omaths)
    return (f'<a:p><a14:m><m:oMathPara xmlns:m="{M_NS}"><m:oMathParaPr><m:jc m:val="{jc}"/></m:oMathParaPr>'
            f'{lines}</m:oMathPara></a14:m></a:p>')


# ---------------------------------------------------------------------------------------------
# The deck's display equations
# ---------------------------------------------------------------------------------------------
def eq_plv(size=16):
    st = Style(size)
    ss = Style(size * 0.72)  # PowerPoint scales scripts itself; runs keep the base size
    ss = st
    return para([omath(
        sub(t("PLV", st), v("ab", st)), t("=", st),
        delim(
            frac(t("1", st), v("N", st))
            + nary("∑", v("n", st) + t("=1", st), v("N", st),
                   sup(v("e", st), t("i", st) + t("Δ", st) + sub(v("ϕ", st), v("ab", st)) + delim(v("n", st)))),
            "|", "|"),
    )])


def eq_ck(size=16):
    st = Style(size)
    return para([omath(
        sub(v("C", st), v("k", st)), t("=", st),
        subsup(bar(t("PLV", st)), v("k", st), t("sound", st)), t("−", st),
        subsup(t("PLV", st), v("k", st), t("silence", st)),
    )])


def eq_early_later(size=16):
    st = Style(size)
    half = frac(t("1", st), t("2", st))
    return para([
        omath(sub(v("C", st), t("early", st)), t("=", st), half,
              delim(sub(v("C", st), t("1", st)) + t("+", st) + sub(v("C", st), t("2", st)))),
        omath(sub(v("C", st), t("later", st)), t("=", st), frac(t("1", st), t("2", st)),
              delim(sub(v("C", st), t("4", st)) + t("+", st) + sub(v("C", st), t("5", st)))),
    ])


def eq_session_diff(size=16):
    st = Style(size)
    return para([omath(
        delim(sup(t("PLV", st), t("sound", st)) + t("−", st) + sup(t("PLV", st), t("silence", st)), "⟨", "⟩"),
        t(" = +0.077", st),
    )])


EQUATIONS = {
    "EQ_PLV": (eq_plv, "PLV_ab = |(1/N) Σ_{n=1..N} e^(i Δϕ_ab(n))|"),
    "EQ_CK": (eq_ck, "C_k = mean PLV(sound, k) − PLV(silence, k)"),
    "EQ_EARLY_LATER": (eq_early_later, "C_early = (C_1 + C_2)/2; C_later = (C_4 + C_5)/2"),
    "EQ_SESSION": (eq_session_diff, "⟨PLV(sound) − PLV(silence)⟩ = +0.077"),
}
