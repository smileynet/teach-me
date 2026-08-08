#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

# render-diagrams.sh — Render .mmd (Mermaid) and .d2 files to SVG
# Outputs to assets/generated/
#
# Usage: tools/render-diagrams.sh [input-dir]
#   input-dir defaults to ./diagrams/
#
# Requires one of:
#   - d2 (brew install d2) — preferred, zero-dep
#   - mmdc via Python (pip install mmdc) — browserless Mermaid

INPUT_DIR="${1:-./diagrams}"
OUTPUT_DIR="./assets/generated"

mkdir -p "$OUTPUT_DIR"

if [ ! -d "$INPUT_DIR" ]; then
  echo "No $INPUT_DIR directory found. Nothing to render."
  exit 0
fi

rendered=0
errors=0

# Render .d2 files
if command -v d2 &>/dev/null; then
  for f in "$INPUT_DIR"/*.d2; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .d2)
    echo "  d2: $f → $OUTPUT_DIR/$base.svg"
    if d2 "$f" "$OUTPUT_DIR/$base.svg" 2>/dev/null; then
      ((rendered++))
    else
      echo "  ERROR: failed to render $f"
      ((errors++))
    fi
  done
else
  d2_files=("$INPUT_DIR"/*.d2)
  if [ ${#d2_files[@]} -gt 0 ]; then
    echo "WARNING: .d2 files found but d2 not installed. Run: brew install d2"
  fi
fi

# Render .mmd files
if command -v mmdc &>/dev/null; then
  for f in "$INPUT_DIR"/*.mmd; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .mmd)
    echo "  mermaid: $f → $OUTPUT_DIR/$base.svg"
    if mmdc -i "$f" -o "$OUTPUT_DIR/$base.svg" 2>/dev/null; then
      ((rendered++))
    else
      echo "  ERROR: failed to render $f"
      ((errors++))
    fi
  done
elif command -v npx &>/dev/null; then
  for f in "$INPUT_DIR"/*.mmd; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .mmd)
    echo "  mermaid (npx): $f → $OUTPUT_DIR/$base.svg"
    if npx -y @mermaid-js/mermaid-cli mmdc -i "$f" -o "$OUTPUT_DIR/$base.svg" 2>/dev/null; then
      ((rendered++))
    else
      echo "  ERROR: failed to render $f"
      ((errors++))
    fi
  done
else
  mmd_files=("$INPUT_DIR"/*.mmd)
  if [ ${#mmd_files[@]} -gt 0 ]; then
    echo "WARNING: .mmd files found but no Mermaid renderer installed."
    echo "  Option A (recommended): pip install mmdc"
    echo "  Option B: npm install -g @mermaid-js/mermaid-cli"
  fi
fi

echo ""
echo "Done: $rendered rendered, $errors errors."
[ "$errors" -eq 0 ]
