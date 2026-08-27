#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <input.pdf> <output-directory>" >&2
  exit 2
fi

PDF="$1"
OUT="$2"
mkdir -p "$OUT"

if command -v pdftoppm >/dev/null 2>&1; then
  pdftoppm -png -r 150 "$PDF" "$OUT/page"
  echo "$OUT"
elif command -v mutool >/dev/null 2>&1; then
  mutool draw -r 150 -o "$OUT/page-%d.png" "$PDF"
  echo "$OUT"
else
  echo "No PDF renderer found. Install poppler (pdftoppm) or MuPDF (mutool)." >&2
  exit 1
fi
