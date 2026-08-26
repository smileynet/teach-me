---
id: "132"
title: "Explore: additional interactive activity types (label-diagram, code-playground, scenario-sim)"
status: open
blocked_by: ["117"]
priority: low
tags: [platform]
---

# Explore: additional interactive activity types

## Context

Ticket 117 ships 3 core interactive types (sequence, match, fill-in-blank). This ticket explores what comes next based on how those land with users.

## Candidates to explore

- **Label the diagram** — drag labels onto SVG positions (needs coordinate mapping system)
- **Code playground** — editable code snippets with eval/validation (sandboxed)
- **Scenario simulation** — multi-step "what happens if..." with branching outcomes
- **Spot the bug** — presented with broken code/config, identify the issue
- **Comparison table** — fill in a matrix (e.g., "which format supports X, Y, Z?")
- **Timeline ordering** — variant of sequence with visual timeline representation

## Acceptance criteria

- [ ] User testing feedback on the 3 shipped types informs which to build next
- [ ] At least one additional type prototyped and evaluated
- [ ] Decision recorded as ADR if adding new question type infrastructure
