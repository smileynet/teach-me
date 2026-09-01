#!/usr/bin/env bash
# assemble-site.sh (#280) — the SINGLE source of the GitHub Pages `_site` assembly.
#
# Both the deploy workflow (.github/workflows/pages.yml) AND the local dry-run
# (tools/site-dry-run.py) call this, so the dry-run exercises the EXACT deploy logic — no
# re-implementation to drift (the "Uniform Build" pattern; ADR-028 extraction). YAML keeps
# only the control plane (checkout, Setup Pages, artifact upload); this script owns turning
# the committed tree into the validated `_site` output.
#
# Usage:  bash tools/assemble-site.sh <output-dir>     # e.g. _site
# Run from the repo root (paths are repo-relative). Requires bash (git-bash on Windows) —
# uses heredocs, `cp -rL` symlink-deref, and `find -prune` that PowerShell can't replicate.
set -euo pipefail

SITE="${1:-_site}"
mkdir -p "$SITE"

# Copy runtime assets to a target, dropping authoring-only artifacts that are not part of
# the served site (scaffolds/ + workspace-template/ hold HTML with {{placeholder}} links;
# showcase.html + svg-patterns.md are design/dev docs). cp -rL dereferences symlinks
# (GitHub Pages rejects symlinks in the artifact).
copy_assets() {
  local dest="$1"
  cp -rL assets/. "$dest"
  rm -rf "$dest/scaffolds" "$dest/workspace-template"
  rm -f  "$dest/showcase.html" "$dest/svg-patterns.md"
}

# Shared assets at the deploy root — satisfies the two aggregate pages
# (library/index.html + library/global-map.html) whose `../assets` resolves one level above
# library/.
mkdir -p "$SITE/assets"
copy_assets "$SITE/assets/"

# The whole committed library, verbatim, under $SITE/library/. Pages hosting adds the
# /{repo}/ subpath — do NOT nest the site further.
mkdir -p "$SITE/library"
cp -rL library/. "$SITE/library/"

# Every domain-scoped page emits `../assets` (or ../../, ../../../) that all resolve to
# library/{domain}/assets/. The #198 symlink stubs were deleted, so place a real assets copy
# at each domain root. Loop only real domain dirs (those containing lessons/) to skip
# index.html / global-map.html / README.
for d in "$SITE"/library/*/; do
  if [ -d "${d}lessons" ]; then
    copy_assets "${d}assets/"
  fi
done

# Static analogue of serve.py's `_root_index` normalizer: lesson/reference/quiz pages emit an
# "All Lessons" breadcrumb to a per-domain `lessons/index.html`. Post-#281 all shipped domains
# commit one, so this loop is a FORWARD-LOOKING fallback — a future domain added without a
# per-domain index would 404 that breadcrumb, so backfill a redirect to the domain map. The
# stub lives at {domain}/lessons/index.html and the map at {domain}/{domain}-map.html — one
# dir UP — so the target needs `../` to escape lessons/ (#280 fix: was missing, would 404).
for d in "$SITE"/library/*/; do
  [ -d "${d}lessons" ] || continue
  idx="${d}lessons/index.html"
  if [ ! -f "$idx" ]; then
    map="../$(basename "$d")-map.html"
    cat > "$idx" <<HTML
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=${map}">
<link rel="canonical" href="${map}"><title>Lessons</title></head>
<body><p>Redirecting to the <a href="${map}">lessons map</a>&hellip;</p></body></html>
HTML
  fi
done

# Root landing: redirect /teach-me/ to the generated aggregate index. Document-relative
# target (no <base>, survives the subpath). Retires the stale docs/index.html.
cat > "$SITE/index.html" <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=library/index.html">
  <link rel="canonical" href="library/index.html">
  <title>Teach Me</title>
</head>
<body>
  <p>Redirecting to the <a href="library/index.html">library</a>&hellip;</p>
</body>
</html>
HTML

# Do not publish ANY private overlay. The `.user/` tree is always private (status overlay, SR
# data, private lessons) and never ships. Post-#279 the shipped demo progress lives in
# committed `library/*/demo-status.json` fixtures (baked into the page at generate time +
# inlined in #page-data), so stripping ALL `.user/` at any depth is safe — nothing under
# `.user/` is needed for the deployed demo counts.
find "$SITE" -type d -name .user -prune -exec rm -rf {} + 2>/dev/null || true

# Bypass Jekyll (serve _-prefixed and .-prefixed files verbatim)
touch "$SITE/.nojekyll"

echo "✓ assembled $SITE"
