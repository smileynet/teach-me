#!/usr/bin/env bash
# Migrate hardcoded hex colors in SVG elements to CSS custom properties.
# Idempotent — safe to run multiple times.
#
# Usage:
#   tools/migrate-svg-vars.sh examples/oidc-rust/lessons/0001-oidc-auth-flows.html
#   tools/migrate-svg-vars.sh --workspace examples/oidc-rust

set -euo pipefail

migrate_file() {
  local f="$1"
  sed -i \
    -e 's/stroke="#2563eb"/stroke="var(--svg-primary)"/g' \
    -e 's/fill="#2563eb"/fill="var(--svg-primary)"/g' \
    -e 's/fill="#1e40af"/fill="var(--svg-primary-text)"/g' \
    -e 's/fill="#dbeafe"/fill="var(--svg-primary-fill)"/g' \
    -e 's/stroke="#16a34a"/stroke="var(--svg-success)"/g' \
    -e 's/fill="#16a34a"/fill="var(--svg-success)"/g' \
    -e 's/fill="#166534"/fill="var(--svg-success-text)"/g' \
    -e 's/fill="#dcfce7"/fill="var(--svg-success-fill)"/g' \
    -e 's/stroke="#d97706"/stroke="var(--svg-warning)"/g' \
    -e 's/fill="#d97706"/fill="var(--svg-warning)"/g' \
    -e 's/fill="#92400e"/fill="var(--svg-warning-text)"/g' \
    -e 's/fill="#fef3c7"/fill="var(--svg-warning-fill)"/g' \
    -e 's/stroke="#dc2626"/stroke="var(--svg-error)"/g' \
    -e 's/fill="#dc2626"/fill="var(--svg-error)"/g' \
    -e 's/fill="#991b1b"/fill="var(--svg-error-text)"/g' \
    -e 's/fill="#fef2f2"/fill="var(--svg-error-fill)"/g' \
    -e 's/stroke="#6b7280"/stroke="var(--svg-neutral)"/g' \
    -e 's/fill="#6b7280"/fill="var(--svg-neutral)"/g' \
    -e 's/fill="#f3f4f6"/fill="var(--svg-neutral-fill)"/g' \
    -e 's/fill="#374151"/fill="var(--svg-text)"/g' \
    -e 's/stroke="#374151"/stroke="var(--svg-text)"/g' \
    -e 's/stroke="#94a3b8"/stroke="var(--svg-line)"/g' \
    -e 's/fill="#94a3b8"/fill="var(--svg-line)"/g' \
    "$f"
  echo "  ✓ $(basename "$f")"
}

if [[ "${1:-}" == "--workspace" ]]; then
  ws="${2:-.}"
  echo "Migrating lessons in: $ws"
  for f in "$ws"/lessons/*.html; do
    [[ "$(basename "$f")" == *-map.html ]] && continue
    [[ "$(basename "$f")" == index.html ]] && continue
    migrate_file "$f"
  done
elif [[ $# -eq 0 ]]; then
  echo "Usage: migrate-svg-vars.sh <file> [file...]"
  echo "       migrate-svg-vars.sh --workspace <path>"
  exit 1
else
  for f in "$@"; do
    migrate_file "$f"
  done
fi
