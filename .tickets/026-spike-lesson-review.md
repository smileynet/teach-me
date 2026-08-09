---
id: "026"
title: "Spike: lesson-review checklist skill"
status: done
priority: high
blocked_by: ["021", "023"]
type: spike
---

# Spike: lesson-review checklist skill

## Hypothesis

A post-authoring review skill that checks lessons against quality criteria catches issues the teach skill's guidance alone doesn't prevent. Codifies "did you actually do the things?" into a verifiable pass.

## What to build

A lightweight post-authoring sanity check — not a bureaucratic process but a quick "did I miss anything obvious?" Probably just guidance in the teach skill rather than a separate skill.

Checks:
- Brief context/orientation at the top (why this matters for the mission)
- At least one diagram for architectural/conceptual content
- Citations for factual claims
- Jargon annotated (ran the jargon skill)
- "What's Next" section present

That's 5 items, not 10. Run mentally after writing, not as a formal tool invocation.

## Acceptance criteria

- [x] Teach skill has a "Before publishing" checklist (5 items)
- [ ] ~~Separate `lesson-review` skill~~ Not needed — it's a paragraph in teach
- [ ] ~~Automated reading level script~~ Deferred unless proven needed
- [x] Run against lesson 1 to verify it passes

## Depends on

Tickets 021, 023 — references patterns from those spikes.
