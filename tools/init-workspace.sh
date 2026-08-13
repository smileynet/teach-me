#!/usr/bin/env bash
# Initialize a fresh learning workspace.
# Creates the required directory structure with assets symlink.
# Safe to run multiple times — won't overwrite existing files.
#
# Usage:
#   tools/init-workspace.sh                           # creates workspace/ at project root (default)
#   tools/init-workspace.sh --path examples/my-topic  # creates at custom location
#   tools/init-workspace.sh --default                 # creates workspace/ with generic (topic-agnostic) content

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$PROJECT_ROOT/assets/workspace-template"

# Parse arguments
WORKSPACE="$PROJECT_ROOT/workspace"
DEFAULT_MODE=false
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
    --default)
      DEFAULT_MODE=true
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: init-workspace.sh [--path <workspace-dir>] [--default]"
      exit 1
      ;;
  esac
done

if [ -d "$WORKSPACE/lessons" ]; then
  echo "Workspace already exists at: $WORKSPACE"
  echo "  lessons/: $(ls "$WORKSPACE/lessons/"*.html 2>/dev/null | wc -l | tr -d ' ') lesson files"
  echo "  maps/:    $(ls "$WORKSPACE/maps/"*.MAP.md 2>/dev/null | wc -l | tr -d ' ') map files"
  exit 0
fi

echo "Creating workspace at: $WORKSPACE"
mkdir -p "$WORKSPACE"/{lessons/quiz,reference,learning-records/questions,maps}

# Copy template files or write defaults (only if they don't exist)
if [ "$DEFAULT_MODE" = true ]; then
  # Generic, topic-agnostic workspace for first-time users
  if [ ! -f "$WORKSPACE/MISSION.md" ]; then
    cat > "$WORKSPACE/MISSION.md" <<'EOF'
# Learning Workspace

This is your personal learning workspace. Topics you explore will generate
lessons, maps, quizzes, and reference docs here.

To get started, tell your AI assistant what you'd like to learn.
EOF
  fi
  if [ ! -f "$WORKSPACE/RESOURCES.md" ]; then
    cat > "$WORKSPACE/RESOURCES.md" <<'EOF'
# Resources

Verified sources for topics in this workspace. Populated automatically as you explore new domains.
EOF
  fi
else
  for f in MISSION.md RESOURCES.md; do
    if [ ! -f "$WORKSPACE/$f" ]; then
      cp "$TEMPLATE/$f" "$WORKSPACE/$f"
    fi
  done
fi

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
