---
id: "026"
title: "Spike: lesson-review checklist skill"
status: open
priority: high
blocked_by: ["020", "021", "023"]
type: spike
---

# Spike: lesson-review checklist skill

## Hypothesis

A post-authoring review skill that checks lessons against quality criteria catches issues the teach skill's guidance alone doesn't prevent. Codifies "did you actually do the things?" into a verifiable pass.

## What to build

1. Create `lesson-review` skill that checks a written lesson against:
   - [ ] Opens with problem/gap (not solution-first)
   - [ ] End-state preview present
   - [ ] At least one inline SVG diagram
   - [ ] Sentence lengths within constraint (flag > 25 words)
   - [ ] Callbacks to prior lessons where concepts recur
   - [ ] Primary source linked
   - [ ] "What's Next" section present
   - [ ] Quiz or challenge present
   - [ ] Glossary terms annotated (jargon skill ran)
2. Run it against lesson 1 and report findings

## Baseline

Currently there's no post-authoring quality gate. The teach skill has guidance but nothing verifies compliance.

## Compare against

- Does the checklist catch real issues?
- Is it useful or just bureaucratic?
- Should any checks be automated (reading level script) vs judgment calls?

## Acceptance criteria

- [ ] `lesson-review` skill created with the checklist
- [ ] Run against lesson 1, findings reported
- [ ] Clear distinction between automatable checks and judgment checks
- [ ] Before/after: lesson 1 with vs without the review pass applied

## Depends on

Tickets 020, 021, 023 — the checklist references patterns from those spikes.
