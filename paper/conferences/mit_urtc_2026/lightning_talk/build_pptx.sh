#!/bin/sh
# Rebuild the editable PowerPoint deck from the results files. This overwrites
# URTC2026_LT-ID1269_Chughtai.pptx, so any edits made in PowerPoint are lost; after you start editing
# in PowerPoint, treat the .pptx as the master and export the PDF from PowerPoint instead.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
PYTHON="${PYTHON:-$REPO/.venv-reliability/bin/python}"
NAME="URTC2026_LT-ID1269_Chughtai"
"$PYTHON" "$HERE/source_pptx/make_figures_v2.py" --repo "$REPO" --recon "$HERE/analysis" --out "$HERE/source_pptx/fig"
cd "$HERE/source"
[ -d node_modules ] || npm install --silent
NODE_PATH="$HERE/source/node_modules" node "$HERE/source_pptx/build_native.js" "$HERE/source_pptx/fig" "$HERE/SPEAKER_SCRIPT.md" "$HERE/source_pptx/raw.pptx"
python3 "$HERE/source_pptx/inject_math.py" "$HERE/source_pptx/raw.pptx" "$HERE/$NAME.pptx"
rm -f "$HERE/source_pptx/raw.pptx"
