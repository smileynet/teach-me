#!/usr/bin/env bash
# Initialize a fresh learning workspace.
# Creates the required directory structure with assets symlink.
# Safe to run multiple times — won't overwrite existing files.
#
# Usage:
#   tools/init-workspace.sh                    # creates workspace/ at project root
#   tools/init-workspace.sh --path examples/my-topic  # creates at custom location

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$PROJECT_ROOT/assets/workspace-template"

# Parse --path argument
WORKSPACE="$PROJECT_ROOT/workspace"
while [[ $# -gt 0 ]]; do
  case $1 in
    --path)
      WORKSPACE="$2"
      # Make relative paths absolute from project root
      if [[ "$WORKSPACE" != /* ]]; then
        WORKSPACE="$PROJECT_ROOT/$WORKSPACE"
      fi
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: init-workspace.sh [--path <workspace-dir>]"
      exit 1
      ;;
  esac
done

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

# Create assets symlink (relative path so it's portable)
if [ ! -L "$WORKSPACE/assets" ] && [ ! -d "$WORKSPACE/assets" ]; then
  # Compute relative path from workspace to project assets/
  ASSETS_ABS="$PROJECT_ROOT/assets"
  # Use python for reliable relative path computation
  REL_PATH=$(python3 -c "
import os.path
print(os.path.relpath('$ASSETS_ABS', '$WORKSPACE'))
")
  ln -s "$REL_PATH" "$WORKSPACE/assets"
fi

# Generate placeholder index page so the workspace is immediately browsable
if [ ! -f "$WORKSPACE/lessons/index.html" ]; then
  WORKSPACE_NAME=$(basename "$WORKSPACE")
  cat > "$WORKSPACE/lessons/index.html" <<EOF
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lessons — $WORKSPACE_NAME</title>
  <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
  <main class="lesson-container">
    <h1>📚 $WORKSPACE_NAME</h1>
    <p>No lessons yet. Generate a topic map to get started.</p>
    <p><em>Run the teach skill or <code>mise run map:generate</code> to create your first map.</em></p>
  </main>
  <script src="../assets/lesson-actions.js" data-domain="$WORKSPACE_NAME"></script>
</body>
</html>
EOF
fi

echo "✓ Workspace ready at: $WORKSPACE"
echo ""
echo "Next steps:"
echo "  1. Edit MISSION.md with your learning goal"
echo "  2. Run: mise run serve"
echo "  3. Generate your first topic map"
