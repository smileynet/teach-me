#!/usr/bin/env bash
# Initialize a fresh learning workspace.
# Creates workspace/ with the required directory structure.
# Safe to run multiple times — won't overwrite existing files.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKSPACE="$PROJECT_ROOT/workspace"
TEMPLATE="$PROJECT_ROOT/assets/workspace-template"

if [ -d "$WORKSPACE/lessons" ]; then
  echo "Workspace already exists at: $WORKSPACE"
  echo "  lessons/: $(ls "$WORKSPACE/lessons/"*.html 2>/dev/null | wc -l) lesson files"
  echo "  maps/:    $(ls "$WORKSPACE/maps/"*.MAP.md 2>/dev/null | wc -l) map files"
  exit 0
fi

echo "Creating workspace at: $WORKSPACE"
mkdir -p "$WORKSPACE"/{lessons/quiz,reference,learning-records/questions,maps}

# Copy template files (only if they don't exist)
for f in MISSION.md RESOURCES.md; do
  if [ ! -f "$WORKSPACE/$f" ]; then
    cp "$TEMPLATE/$f" "$WORKSPACE/$f"
  fi
done

# Copy shared assets symlink (lessons reference ../assets/)
if [ ! -L "$WORKSPACE/assets" ] && [ ! -d "$WORKSPACE/assets" ]; then
  ln -s "$PROJECT_ROOT/assets" "$WORKSPACE/assets"
fi

echo "✓ Workspace ready"
echo ""
echo "Next steps:"
echo "  1. Edit workspace/MISSION.md with your learning goal"
echo "  2. Run: mise run serve"
echo "  3. Open: http://localhost:8787/lessons/index.html"
echo "  4. Generate your first topic from the map page"
