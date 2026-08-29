---
id: "254"
title: "Curate CONTEXT.md: move 10 non-glossary entries to AGENTS/specs"
status: open
blocked_by: []
priority: medium
tags: ["docs"]
validation_criteria: "CONTEXT.md contains only disambiguation entries (all have _Avoid_); the 10 flagged entries relocated to their correct owners; AGENTS.md stays <=150 lines (trim if needed); no knowledge lost."
---

# Curate CONTEXT.md: move 10 non-glossary entries to AGENTS/specs

## Intent source
`/project-cleanup` Phase 3 (2026-08-29). A fresh subagent applied the glossary gate to all 27
CONTEXT.md entries: **17 keep / 10 move / 0 delete**. `CONTEXT.md` is a glossary — entries must
resolve WHICH MEANING of an ambiguous term is used (signalled by `_Avoid_`). Ten entries instead
describe HOW something works (mechanism/gotcha/spec) and belong elsewhere.

## What to build

Relocate the 10 flagged entries to their correct owners, then delete them from CONTEXT.md. Preserve
the exact content (supersede, don't obliterate — the knowledge is correct, just misfiled).

### MOVE → AGENTS.md Constraints (6) — gotchas / environment facts
- **glTF slot-driven color space** — sRGB albedo vs Non-Color control maps on import
- **Preact singleton** — all Preact packages must resolve to one instance (vendored import map)
- **GitHub Pages symlinks** — `cp -rL` when assembling `_site/` (Pages rejects symlinks)
- **GitHub Pages environment protection** — Pages rejects tag-ref deploys; main-only + tag-detection step
- **Blocking head script** — synchronous `<head>` script reads prefs before paint (FOUC prevention)
- **ATTENUATION (Godot shader)** — combines distance falloff AND shadow state, not just distance

### MOVE → .memory/specs/ (4) — interface / implementation contracts
- **Mask color (diagram cards)** — slate gray #585b70 for occluded label masks
- **MAP.md domain field** — `domain:` frontmatter MUST match the MAP.md filename (else index 404)
- **Preferences module** — signal-based single source of truth for reading prefs (localStorage key)
- **Page shell** — planned single mount entry point (ticket 127, not yet implemented)

### KEEP in CONTEXT.md (17) — legitimate disambiguation
Entries 2–18 (teach-me, Teaching workspace, teach, quiz-me, wait-what, Mission, Learning record, ZPD,
Storage strength, Reference doc, Socratic gate, Jargon skill, Scaffold, Criteria-based answer,
Progressive overload, Research-first, Casual exploration posture) — all have `_Avoid_` and resolve
term ambiguity. Leave untouched.

## Budget constraint (why this is a ticket, not an inline cleanup)
AGENTS.md is at 148/150 lines. Adding 6 Constraints entries pushes it over — so this needs the
`agents-md-authoring` trim gate (consolidate/trim existing Constraints while adding these, OR extract
a Constraints section to a linked `.memory/specs/` file). Do NOT blindly append and blow the budget.
Some AGENTS-bound entries may already be implied by existing lines — dedupe on the way in.

## Out of scope
- Editing the 17 KEEP entries (they're correct)
- Rewriting AGENTS.md structure beyond fitting these 6 + staying <=150 (that's a separate concern)

## Acceptance criteria

- [ ] The 6 gotcha entries relocated into AGENTS.md Constraints (deduped against existing lines)
- [ ] AGENTS.md remains <= 150 lines (trim/consolidate or extract per agents-md-authoring if needed)
- [ ] The 4 spec entries relocated to `.memory/specs/` (create the files; one per concern or a grouped doc)
- [ ] All 10 entries removed from CONTEXT.md; the 17 KEEP entries untouched
- [ ] CONTEXT.md entries all carry `_Avoid_` (or are unambiguous project-term definitions) — no orphan mechanisms
- [ ] No knowledge lost (each moved entry's content preserved at its new home)
