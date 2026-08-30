---
id: "183"
title: "Public library: rename examples/ → library/ and serve it by default"
status: in_progress
blocked_by: []
priority: high
tags: [platform]
---

# Public library: rename `examples/` → `library/` and serve it by default

## Context

**Decided by ADR 0012 (accepted 2026-08-28).** Adopt the two-tier content model:
today's `examples/` is renamed to `library/` and promoted to be the shipped,
growing public topic library. Generating a topic produces committable files under
`library/{domain}/`. A fresh clone serves the committed library, not an empty
auto-created `workspace/` — this **supersedes** #071's "all user content in
gitignored `workspace/`" and #245/ADR 0011's empty-first-launch serve default.

**Re-scoped (2026-08-29):** this ticket is now the *mechanical* half — the rename
plus the serve-default flip. The *local user-state model* (committed SR
definitions vs gitignored review state, completion badges, merge-on-update) moved
to **#255**, which is blocked by this ticket. #198 (multi-workspace index links)
is also blocked by this rename. #184 (private `.user/` overlay) stays blocked by
this ticket.

Blockers 213/214/221 (the ink + bake lessons this library ships) are all done, so
this is frontier-ready.

## What to build

### 1. `git mv examples library`

### 2. Update every LIVE functional literal (verified blast radius, review 2026-08-29)

> **Grep BOTH patterns** — the codebase builds paths as `Path / "examples"` (no slash),
> so `examples/` alone misses ~6 files. Use `git grep -n '"examples"'` AND
> `git grep -n 'examples/'` scoped to code/config (`':!*.md' ':!.tickets/'`).

Each of these resolves to a real path and breaks after the move:

- **`mise.toml`** — `verify` task (`--workspace examples/oidc-rust`,
  `examples/workout-fundamentals`, `examples/godot-gamedev` in the check-svg-vars
  step); `maps:regenerate` task (`for map in examples/*/maps/*.MAP.md`); **`:158`
  `sources` watch glob `examples/*/maps/*.MAP.md` (added 2026-08-29 review)**. Leave the
  `workspace/maps` branch alone (that's the private live workspace, not renamed).
- **`tools/serve.py:158`** — `MAPS_DIR` fallback `examples/iceberg-workspace/maps`.
- **`tools/verify-interactive.py:65,66,320`** (was :313 — line drift)
- **`tools/verify-links.py:69`** (3 globs; was :67)
- **`tools/lint-html.py:29`**
- **`tools/check-lesson-code.py:46`** (`DEFAULT_LESSONS_GLOB`)
- **`tools/test_map_parser.py:14,15,16`**
- **`tools/bake-export-oracle.py:26`**, **`tools/control-maps-oracle.py:32`**,
  **`tools/control-maps-drift.py:34`**
- **`tools/ink-gd-sync.py:20,22,24,26,28,30,32,34`** (8 lines, not 5)
- **`tools/verify-blender.py:44-47`**
- **ADDED (missing from original §2, review 2026-08-29 — all LIVE, break on rename):**
  - **`tools/generate_global_map.py:154`** — `scan_dir = PROJECT_ROOT / "examples"` default (post-#183 tool)
  - **`tools/check-maps-forest.py:46`** — `scan = ROOT / "examples"` default (post-#183 tool)
  - **`tools/migrate-add-lesson-actions.py:101`** — `(PROJECT_ROOT / "examples").iterdir()` `--all` loop (post-#183 tool)
  - **`tools/check-map-edges.py:146`** — `glob("examples/*/lessons/*-map.html")`
  - **`tools/migrate_strip_status.py:41`** — `glob("examples/**/*.MAP.md")`
  - **`tools/migrate_map_ids.py:113`** — `glob("examples/**/*.MAP.md")`
- Docstring/usage literals (non-blocking, fix for accuracy):
  check-lesson.py, check-svg-vars.py, check-topic-completeness.py,
  backfill-criteria.py, init_workspace.py, jargon-annotate.py,
  migrate-add-breadcrumbs.py, generate_index_page.py:63 (comment),
  generate_global_map.py:14, check-maps-forest.py:20, migrate-add-lesson-actions.py:18,
  migrate_strip_status.py:14, questions.py:37.

### 3. Serve-default flip (ADR 0012)

- **`tools/serve.py:141-156`** — first-launch branch currently defaults to the
  private `workspace/` and else-branch auto-creates an empty `workspace/` via
  `init_workspace(default=True)`. Change the default so a fresh clone serves
  `library/` (a chosen topic, or an aggregated index — coordinate the "serve the
  whole library at once" piece with #198, which owns multi-workspace mounting).
  ADR 0011's pure-Python scaffolding implementation stays; only *what is served by
  default* changes.

### 4. Docs

- **`README.md:72-75`** (example-workspace table links).
- **`AGENTS.md:23`** (workspace-layout line — reframe: `library/` is the public
  library, not "test fixtures"), **`:109`** (Constraint "Use examples/ only for
  demo fixtures" — contradicts ADR 0012, rewrite), **`:125`** (serve restart
  example), **`:150`** (`examples/README.md` reference — file renames too).
- **`.kiro/skills/{generate-topic,godot-validation,teach}/SKILL.md`** — `examples/`
  path references.
- Rewrite the AGENTS.md workspace contract (the "workspace/ is THE live workspace,
  gitignored, auto-created on first serve" lines) to match ADR 0012.

### 5. Confirm gitignore

After the 2026-08-28 `/workspace/` anchoring, `library/` is tracked with no
`git add -f`. Confirm only `/workspace/` and `.user/` remain ignored.

## Out of scope (moved / owned elsewhere)

- Local user-state model, completion badges, SR shared-vs-local split → **#255**.
- Multi-workspace serving (mount all domains at once) → **#198**.
- Private `.user/` overlay → **#184**.
- `.memory/**` and `.tickets/**` markdown mention `examples/` as historical record
  — do NOT rewrite them.

## Acceptance criteria

- [ ] `git mv examples library` done; `library/` tracked without `git add -f`
- [ ] All live functional literals in §2 updated; `mise run verify` EXIT 0
- [ ] `tools/serve.py` first-launch serves `library/` content, not an empty
      auto-created `workspace/` (supersedes ADR 0011 default)
- [ ] README, AGENTS.md (lines 23/109/125/150 + workspace contract), and the three
      SKILL.md files updated to `library/` and reframed per ADR 0012
- [ ] `examples/README.md` renamed to `library/README.md`; internal refs updated
- [ ] `.gitignore` ignores only `/workspace/` (+ `.user/` when #184 lands)
- [ ] No `examples/` literal remains in functional code/config (docstrings may lag,
      tracked separately); grep `examples/` in tools/ + mise.toml is clean of live paths

## Validation

`mise run verify` EXIT 0 after the rename; `mise run serve` on a simulated fresh
clone (no `workspace/`) serves `library/` content; `grep -rn "examples/" tools/ mise.toml`
shows no live path literals.
