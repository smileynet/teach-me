---
id: "071"
title: "Feature: repo cleanup — workspace separation, examples reorganization"
status: done
priority: high
blocked_by: []
type: feature
---

# Feature: repo cleanup for public publishing

## What to build

Separate user-generated content from source code so the repo is publishable and users can generate content without polluting the source.

### 1. Workspace separation

Move user content into a gitignored `workspace/` directory:
```
workspace/              ← gitignored, user's learning space
  MISSION.md
  RESOURCES.md
  lessons/
  reference/
  learning-records/
  maps/                 ← generated MAP.md files go here
```

Add `mise run init-workspace` that scaffolds a fresh workspace from a template.

### 2. Examples reorganization

Keep demonstrative content in `examples/` committed to the repo:
```
examples/
  maps/                 ← MAP.md samples (all 3 states represented)
  iceberg-workspace/    ← the existing Iceberg example (full workspace)
  roguelike-rust/       ← existing
  workout-fundamentals/ ← existing
```

### 3. Tool path updates

Update serve.py, map_parser imports, and mise tasks to look for MAP.md in `workspace/maps/` (or configurable path).

### 4. .gitignore updates

```
workspace/
.scratch/
.references/
```

## Acceptance criteria

- [x] Fresh clone + `mise run init-workspace` produces a working empty workspace
- [x] `mise run serve` serves from workspace/ not root
- [x] Examples still work (map pages load from examples/)
- [x] Existing Iceberg content moved to examples/ as a reference
- [x] `mise run verify` still passes
- [x] No personal data in committed files (MISSION.md etc. are in workspace/)

## Validation

- **E2E:** Fresh clone → `mise install && mise run setup && mise run init-workspace` → `mise run serve` → navigate to index page → verify it works with empty workspace
- **Regression:** `mise run verify` passes after reorganization
