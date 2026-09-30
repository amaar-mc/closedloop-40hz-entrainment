#!/bin/sh
# Rebuild the FIRST (web/HTML) design into previous/. The current deck is the PowerPoint file; see ../build_pptx.sh.
#   source/build_web.sh   (uses $PYTHON, default: the repo's .venv-reliability interpreter)
# Needs: Python with numpy/matplotlib, Node.js, Google Chrome, poppler (pdftoppm).
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
PYTHON="${PYTHON:-$REPO/.venv-reliability/bin/python}"
NAME="previous/URTC2026_LT-ID1269_Chughtai_v1-web"

"$PYTHON" "$HERE/source/make_figures.py" --repo "$REPO" --recon "$HERE/analysis" --out "$HERE/source/fig"
cd "$HERE/source"
[ -d node_modules ] || npm install --silent
node build_deck.js
./render.sh "$HERE/$NAME.pdf"
