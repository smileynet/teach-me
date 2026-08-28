#!/usr/bin/env bash
# Thin passthrough to the pure-Python workspace initializer (ticket #245).
# The real logic lives in tools/init_workspace.py so first-launch works without
# a bash/python3/symlink dependency on Windows. Kept for POSIX callers and
# muscle memory; forwards all args unchanged.
#
# Usage:
#   tools/init-workspace.sh                           # creates workspace/ (default)
#   tools/init-workspace.sh --path examples/my-topic  # custom location
#   tools/init-workspace.sh --default                 # generic first-launch content

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Prefer the project venv interpreter, fall back to python3 then python.
if [ -x "$SCRIPT_DIR/../.venv/bin/python" ]; then
  PY="$SCRIPT_DIR/../.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
else
  PY="python"
fi

exec "$PY" "$SCRIPT_DIR/init_workspace.py" "$@"
