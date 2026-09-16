---
id: "331"
title: "Repair the red site-dry-run deploy gate"
status: done
priority: high
blocked_by: []
type: fix
tags: ["arch-review"]
---

# Repair the red site-dry-run deploy gate

## Why

2026-09-16 architecture review: `mise run site-dry-run` exits 1 today, and the two newest library domains (gltf-format, godot-asset-pipeline) shipped without the #280 pre-release gate passing. Worse, #280's shipped "latent bug fix" is itself wrong in substance. ADR-0015's pre-release enforcement is red.

## Findings (all verified against source 2026-09-16)

1. **Text-file asset stubs.** `library/gltf-format/assets` and `library/godot-asset-pipeline/assets` are ASCII text files containing `../../assets` — the Windows symlink-stub hack that #198's resolution claims was deleted and ADR-0015 lists as a retired workaround. Deploy survives only because `assemble-site.sh` uses `cp -rL` (dereferences); plain-HTTP serving on Windows (ADR 0003) hands browsers a dead text file. The dry-run currently dies here: `cp: cannot stat '.../_site/library/gltf-format/assets/': Not a directory`.
2. **Wrong redirect target.** `tools/assemble-site.sh:60` writes the missing-index redirect target as `../{domain}-map.html`, but committed map pages live at `{domain}/lessons/{domain}-map.html` (`library/*/lessons/*-map.html` = 11 files; `library/*/*-map.html` = 0). The redirect 404s. `tools/site-dry-run.py:141` asserts the wrong string as "the #280 fix". Dormant only because every domain currently ships an index.
3. **Stale domain count.** `tools/site-dry-run.py:110` hard-asserts exactly 6 domains with lessons; there are 7.

## What to build

- Delete the two text-stub `assets` entries (pages are document-relative per ADR-0015; they should need no assets symlink). Confirm served pages still resolve `../assets` via serve.py's `_nested_assets` normalizer.
- Fix the missing-index redirect target in `assemble-site.sh` to `{domain}/lessons/{domain}-map.html` and update the dry-run assertion to match reality.
- Make the domain-count check derive from the actual `library/` scan instead of a hardcoded number.

Regeneration gotchas (idempotent re-bake rules, tracked-inputs-only) live in `.memory/specs/environment-gotchas.md` → "Generated artifacts / regeneration" — read before regenerating anything.

## Acceptance criteria

- [x] `library/gltf-format/assets` and `library/godot-asset-pipeline/assets` are gone (or are real dirs); `mise run serve` on a fresh clone still serves those domains' pages with working `../assets` resolution
- [x] Missing-index redirect in a scratch copy points at `{domain}/lessons/{domain}-map.html` and the target file exists
- [x] `tools/site-dry-run.py` domain check derives from a `library/` scan (no hardcoded count)
- [x] `mise run site-dry-run` exits 0
- [x] `mise run verify` passes after any regeneration

## Resolution

Deleted the two Windows text-stub `assets` entries; local serving now relies on the ADR-0015 shared-asset normalizer rather than an invalid filesystem shim. Corrected the fallback redirect to the sibling `{domain}-map.html` file and replaced the hard-coded domain count with discovery. The dry-run now builds an isolated index-less domain fixture and proves that its generated redirect reaches an existing map. Updated ADR 0015 to describe the live gate. Evidence: `mise run site-dry-run` → 12/12 assertions pass; library-root requests for both repaired domain pages and `../assets/style.css` returned four HTTP 200s; `mise run verify` → passed (43 map tests, 20 interactive checks, 5 Ink transcript fixtures).
