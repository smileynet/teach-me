---
id: "205"
title: "Fix loose-end warning in lesson 01 ink story"
status: done
blocked_by: ["200"]
priority: high
type: fix
tags: [ink]
---

# Fix loose-end warning in lesson 01 ink story

## Resolution (2026-08-25)

**Resolved by #207.** The loose-end warnings were caused by the false "fallthrough" teaching — knots without exit diverts. The #207 rewrite added proper `-> END` / `-> scene_two` exits to all knots, eliminating the compiler warnings.

Verification: `mise run ink:validate:strict` → 2 files, 0 errors, 0 warnings (PASSED).

## Problem

`01_flow_and_knots.ink` triggers "Apparent loose end where flow runs out" at lines 3 & 7 in Inky. The story runs correctly but the warning confuses learners — the first thing they see when opening the reference file is a yellow warning.

## To investigate

1. Reproduce in Inky — identify exact source lines
2. Check if it's inklecate version mismatch (compiler v19 vs inkgd runtime)
3. Determine idiomatic fix (gather after choices? restructure knot endings?)
4. Apply fix, recompile, verify warning-free in Inky

## Blocked by

#199 (ink-validate) — once we have validation tooling, this fix can be verified automatically.
