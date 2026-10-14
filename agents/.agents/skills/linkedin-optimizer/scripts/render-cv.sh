#!/usr/bin/env bash
# Render a CV HTML file to PDF (headless Chrome/Chromium) and optionally .docx (macOS textutil, else pandoc).
# Usage: render-cv.sh <cv.html> <output-dir> [--docx]
set -euo pipefail

html="${1:?usage: render-cv.sh <cv.html> <output-dir> [--docx]}"
outdir="${2:?usage: render-cv.sh <cv.html> <output-dir> [--docx]}"
docx="${3:-}"

[[ -f "$html" ]] || { echo "not found: $html" >&2; exit 1; }
mkdir -p "$outdir"
html_abs="$(cd "$(dirname "$html")" && pwd)/$(basename "$html")"
name="$(basename "$html" .html)"
pdf="$outdir/$name.pdf"

chrome=""
for c in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "$(command -v google-chrome 2>/dev/null || true)" \
  "$(command -v chromium 2>/dev/null || true)" \
  "$(command -v chromium-browser 2>/dev/null || true)"; do
  [[ -n "$c" && -x "$c" ]] && { chrome="$c"; break; }
done
[[ -n "$chrome" ]] || { echo "Chrome/Chromium not found" >&2; exit 1; }

"$chrome" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$pdf" "file://$html_abs" >/dev/null 2>&1
echo "PDF: $pdf"

if [[ "$docx" == "--docx" ]]; then
  out="$outdir/$name.docx"
  if command -v textutil >/dev/null; then
    textutil -convert docx -output "$out" "$html_abs"
  elif command -v pandoc >/dev/null; then
    pandoc "$html_abs" -o "$out"
  else
    echo "no textutil/pandoc; skipped .docx" >&2; exit 0
  fi
  echo "DOCX: $out"
fi
