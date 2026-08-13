#!/usr/bin/env bash
# Release process for teach-me.
# Creates a git tag and GitHub release with changelog notes.
#
# Usage:
#   tools/release.sh 0.1.0        # release v0.1.0
#   tools/release.sh 0.2.0 --dry  # preview without creating anything
#
# Gates (all must pass):
#   1. Working tree is clean
#   2. Version is valid semver
#   3. Version > last tag
#   4. Changelog has entry for this version
#   5. mise run verify passes

set -euo pipefail

VERSION="${1:-}"
DRY_RUN="${2:-}"

if [[ -z "$VERSION" ]]; then
  echo "Usage: tools/release.sh <version> [--dry]"
  echo "  e.g., tools/release.sh 0.2.0"
  echo ""
  echo "Current tags:"
  git tag --sort=-v:refname | head -5
  exit 1
fi

TAG="v${VERSION}"

# Gate 1: Clean working tree
if [[ -n "$(git status --porcelain)" ]]; then
  echo "✗ Working tree is not clean. Commit or stash changes first."
  exit 1
fi
echo "✓ Working tree clean"

# Gate 2: Valid semver (basic check)
if ! echo "$VERSION" | grep -qP '^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'; then
  echo "✗ Invalid semver: $VERSION"
  exit 1
fi
echo "✓ Valid semver: $VERSION"

# Gate 3: Version > last tag
LAST_TAG=$(git tag --sort=-v:refname | head -1)
if [[ -n "$LAST_TAG" ]] && [[ "$(printf '%s\n%s' "$LAST_TAG" "$TAG" | sort -V | tail -1)" == "$LAST_TAG" ]]; then
  echo "✗ Version $TAG is not greater than last tag $LAST_TAG"
  exit 1
fi
echo "✓ $TAG > $LAST_TAG"

# Gate 4: Changelog entry exists
if ! grep -q "## \[$VERSION\]" CHANGELOG.md; then
  echo "✗ No CHANGELOG.md entry for [$VERSION]"
  echo "  Add: ## [$VERSION] — $(date +%Y-%m-%d)"
  exit 1
fi
echo "✓ CHANGELOG entry found for $VERSION"

# Gate 5: Verification passes
echo "Running mise run verify..."
if ! mise run verify > /dev/null 2>&1; then
  echo "✗ mise run verify failed"
  exit 1
fi
echo "✓ Verification passed"

# Extract release notes from CHANGELOG
NOTES=$(awk "/^## \[$VERSION\]/{found=1; next} /^## \[/{found=0} found" CHANGELOG.md)

echo ""
echo "═══════════════════════════════════════"
echo "Release: $TAG"
echo "═══════════════════════════════════════"
echo ""
echo "$NOTES"
echo ""

if [[ "$DRY_RUN" == "--dry" ]]; then
  echo "[DRY RUN] Would create tag $TAG and GitHub release"
  exit 0
fi

# Create tag
git tag -a "$TAG" -m "Release $TAG"
echo "✓ Created tag: $TAG"

# Push tag
git push origin "$TAG"
echo "✓ Pushed tag to origin"

# Create GitHub release
if command -v gh &> /dev/null; then
  gh release create "$TAG" \
    --title "$TAG" \
    --notes "$NOTES"
  echo "✓ GitHub release created"
else
  echo "⚠ gh CLI not found — create the GitHub release manually at:"
  echo "  https://github.com/smileynet/teach-me/releases/new?tag=$TAG"
fi

echo ""
echo "🎉 Released $TAG"
