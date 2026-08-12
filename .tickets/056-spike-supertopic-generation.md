---
id: "056"
title: "Spike: actionable supertopics — generate leads_to domains from the map page"
status: open
priority: medium
blocked_by: []
type: spike
---

# Spike: actionable supertopics (leads_to generation)

## What to test

Can the "Where This Leads" section on the map page have clickable items that either navigate to an existing domain map or offer to generate one?

## Design (from research)

### Three states for leads_to items

1. **Ready** (MAP.md exists) — solid card, click navigates to the domain map
2. **Generatable** (no MAP.md yet) — dashed border, "Generate" action, shows CLI command
3. **Horizon** (prerequisites unmet from this domain) — muted, shows what needs completing first

### Placeholder approach

Don't trigger generation on exploratory click. Instead:
1. Click → show a lightweight preview (title + what it covers, estimated scope)
2. "Generate this domain" button → modal with CLI command (same pattern as topic generation)
3. Generation produces MAP.md first (the plan), then orientation lesson

### Multi-step generation

Supertopics are BIGGER than topics — a full MAP.md + orientation lesson. The modal should reflect this:

```
kiro-cli chat "teach me about streaming architectures"
```

This triggers the full teach skill → detects broad topic → generates MAP.md → writes orientation lesson. Same flow as the original big-request handling.

## What to build in the spike

Update `generate_map_page.py` to render the "Where This Leads" section with:
- For each leads_to slug: check if `{slug}.MAP.md` exists at project root
- If exists: render as a link card → that domain's map page
- If not: render with dashed border + "Generate domain" button + modal

## Success criteria

- [x] leads_to items are clickable cards (not just a bullet list) — done: buttons that trigger generation modal
- [ ] Existing domains link to their map page
- [x] Non-existing domains show "Generate domain" with generation modal — done: triggers live kiro-cli generation
- [ ] Visual distinction between the three states (ready/generatable/horizon)
- [x] Works with the data-analytics map (5 leads_to items, none exist yet) — done

## Partial resolution (2026-08-11)

The "generatable" state is fully working — leads_to items are buttons that trigger the generation modal with live SSE. But existing domain detection (linking to other map pages) and the horizon state (prerequisites unmet) are not implemented. Those need the MAP.md parser (ticket 043, now done) to determine which domains exist and what their prereqs are.

## Validation (remaining work)

- **Integration:** `/api/maps` endpoint returns list of existing domain MAP.md files; page JS calls it on load and updates leads_to button states
- **E2E (Playwright):** Load map page with one existing leads_to domain (create a test MAP.md) → verify that item renders as a link (not generate button). Load with a non-existing domain → verify generate button. Verify visual distinction between states.
