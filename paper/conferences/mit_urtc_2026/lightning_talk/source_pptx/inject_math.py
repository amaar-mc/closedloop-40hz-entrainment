"""Replace placeholder text boxes (text "EQ_NAME@size") with native PowerPoint equations.

PowerPoint stores an equation text box as mc:AlternateContent: the Choice holds the shape with an
a14:m math zone, the Fallback the same shape as plain text for viewers without math support.

  python inject_math.py deck.pptx out.pptx
"""
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from omml import EQUATIONS  # noqa: E402

MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
A14 = "http://schemas.microsoft.com/office/drawing/2010/main"
MARK = re.compile(r"EQ_[A-Z_]+@[0-9.]+")


def rewrite_slide(xml):
    count = 0

    def fix(m):
        nonlocal count
        sp = m.group(0)
        mk = MARK.search(sp)
        if not mk:
            return sp
        name, size = mk.group(0).split("@")
        build, fallback_text = EQUATIONS[name]
        body = re.search(r"(<p:txBody>)(.*?)(</p:txBody>)", sp, re.S)
        head = re.match(r"(\s*<a:bodyPr.*?(?:/>|</a:bodyPr>)\s*(?:<a:lstStyle/>)?)", body.group(2), re.S)
        choice = sp[:body.start(2)] + head.group(1) + build(float(size)) + sp[body.end(2):]
        fallback = sp.replace(mk.group(0), fallback_text)
        count += 1
        return (f'<mc:AlternateContent xmlns:mc="{MC}"><mc:Choice xmlns:a14="{A14}" Requires="a14">'
                f'{choice}</mc:Choice><mc:Fallback>{fallback}</mc:Fallback></mc:AlternateContent>')

    out = re.sub(r"<p:sp>.*?</p:sp>", fix, xml, flags=re.S)
    return out, count


def main(src, dst):
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(src) as z:
        z.extractall(tmp)
        names = z.namelist()
    total = 0
    for f in sorted((tmp / "ppt" / "slides").glob("slide*.xml")):
        xml = f.read_text(encoding="utf-8")
        new, n = rewrite_slide(xml)
        if n:
            f.write_text(new, encoding="utf-8")
            print(f"{f.name}: {n} equation(s)")
            total += n
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for name in names:  # keep the original part order ([Content_Types].xml first)
            z.write(tmp / name, name)
    shutil.rmtree(tmp)
    print(f"injected {total} equations -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
