#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${TMPDIR:-/tmp}/rffl-owners-draft-strategy-smoke"
mkdir -p "$OUT_DIR"

python3 "$SKILL_DIR/scripts/validate_cheat_sheet.py" \
  "$SKILL_DIR/examples/sample-cheat-sheet.json" --strict

python3 "$SKILL_DIR/scripts/render_cheat_sheet.py" \
  "$SKILL_DIR/examples/sample-cheat-sheet.json" \
  --output "$OUT_DIR/sample-output.pdf"

if command -v pdftoppm >/dev/null 2>&1 || command -v mutool >/dev/null 2>&1; then
  "$SKILL_DIR/scripts/preview_pdf.sh" "$OUT_DIR/sample-output.pdf" "$OUT_DIR/preview" >/dev/null
fi

printf 'Smoke test passed.\nPDF: %s\nManifest: %s\n' \
  "$OUT_DIR/sample-output.pdf" "$OUT_DIR/sample-output.manifest.json"
