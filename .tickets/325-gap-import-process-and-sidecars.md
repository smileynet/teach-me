---
id: "325"
title: "godot-asset-pipeline topic 3: import-process-and-sidecars"
status: open
blocked_by: ["305", "324"]
validation_criteria:
  - "Lesson 02: from a working prop → 'edited source / committed / teammate broke' → .import sidecar (commit) vs .godot/ cache (don't), UID, auto-reimport on MD5, ResourceLoader vs FileAccess. Lands back at same prop safe to iterate+share"
  - "Runnable artifact (committed sidecar + .gitignore + loader.gd) + asset:validate-gd L2 assertion (delete cache → auto-reimport regenerates; load() path works)"
  - "Reference doc + SR cards + glossary JSON; passes mise run verify"
tags: ["content"]
---

# godot-asset-pipeline topic 3: import-process-and-sidecars

## Context

Track spiral topic 3 (#305). Win → complication → resolution → win. Design:
`.scratch/proposals/305-godot-asset-pipeline-setup.md`.

## What to build

- **Start from the win**: "You have a prop imported and rendering correctly."
- **Harder case**: "You edited the source and nothing updated / you committed the wrong files / a
  teammate's checkout broke."
- **Resolve**: what import *generates* — the `.import` sidecar (commit it) vs the `.godot/imported/`
  cache (don't); UID (`uid://`) for safe file moves; auto-reimport on source MD5 change;
  `ResourceLoader`/`load()` vs `FileAccess` (FileAccess breaks in exported builds).
- **Land back**: the same working prop, now safe to iterate on and share.

## Acceptance criteria

- [ ] Lesson `03-import-process-and-sidecars.html` in the spiral shape
- [ ] Runnable artifact (committed sidecar + `.gitignore` + `loader.gd`) + `asset:validate-gd` L3 assertion (delete cache → auto-reimport regenerates; `load()` path works)
- [ ] Reference doc + SR cards + glossary JSON
- [ ] Passes `mise run verify`
