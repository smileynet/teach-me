---
id: "200"
title: "Skill: ink-validate — compile and lint .ink files"
status: done
blocked_by: []
priority: high
type: feature
---

# Skill: ink-validate — compile and lint .ink files

## Context

Ink lessons produce `.ink` story files as reference artifacts (ADR 0010). We need a validation skill that catches compile errors AND warnings (like "loose end" flow issues) before stories ship to learners. This is the ink equivalent of `godot --headless --import` for shaders.

## What to build

A skill and/or tool that:
1. Compiles all `.ink` files in the reference project via inklecate
2. Reports errors (hard failures) vs warnings (loose ends, unreachable content)
3. Optionally plays through stories to verify all paths reach `-> END`
4. Integrates with `mise run verify`

## Acceptance criteria

- [ ] `mise run ink:validate` compiles all `.ink` files in ink-test-project/stories/
- [ ] Errors cause non-zero exit (blocks lesson completion)
- [ ] Warnings are reported but don't block (with option to promote to errors)
- [ ] Integrates with generate-topic Phase 4 verification gate
- [ ] Skill doc at `.kiro/skills/ink-validate/SKILL.md`
