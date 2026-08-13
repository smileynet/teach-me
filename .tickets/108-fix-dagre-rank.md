---
id: "108"
title: "Fix dagre rank placement for parallel branches"
type: fix
status: open
priority: low
blocked_by: []
work_order: 11
---

# Fix dagre rank placement for parallel branches

## Problem

When two topics share the same parent (e.g., blender-npr-shaders and godot-shader-language both depend on esoteric-ebb-breakdown), dagre places them at different ranks instead of the same rank. This makes the DAG look linear when it should show parallel tracks.

Current behavior: godot-shader-language renders at rank 4 (same as baking-for-export) instead of rank 2 (same as blender-npr-shaders).

## Desired behavior

Nodes with the same set of parents should appear at the same vertical rank (same Y position), showing they can be explored in parallel.

## Research

- `.scratch/research/dagre-layout-customization.md` — dagre has NO native rank=same constraint
- HassanMojab/dagre fork adds `layer` property per node (cloned at `.references/dagre-fork`)
- Workarounds: post-layout Y-alignment for siblings, or use the fork

## Options

1. **Post-layout alignment** — after dagre layout, find nodes that share all parents and set their Y to the max of the group. Simple, no dependency change.
2. **dagre fork** — use HassanMojab fork with `layer` property. More correct but adds a non-standard dep.
3. **Accept it** — the current layout is readable, just not optimal. Cosmetic issue.

## Acceptance Criteria

- [ ] Nodes sharing the same parent(s) render at the same Y position
- [ ] No overlaps introduced by the fix
- [ ] Works for the blender-godot-shaders map (7 nodes, 2 parallel branches)
