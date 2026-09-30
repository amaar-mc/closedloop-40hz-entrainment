#!/bin/sh
# Render deck.html to a 13.333 x 7.5 in PDF with headless Chrome, then rasterize for review.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="${1:-$HERE/deck.pdf}"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --allow-file-access-from-files \
  --user-data-dir="$HERE/.chrome-profile" --virtual-time-budget=5000 \
  --print-to-pdf="$OUT" "file://$HERE/deck.html" 2>/dev/null
pdfinfo "$OUT" | grep -E "Pages|Page size"
