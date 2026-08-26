---
id: "063"
title: "Research: free-form topic generation from the map page"
status: open
priority: medium
blocked_by: []
type: research
tags: [platform]
---

# Research: free-form topic generation from the map page

## Problem

Users currently can only generate pre-defined topics from the graph or leads-to section. There's no way to say "I want to learn about X" directly from the map page and have it generate a new domain map on the spot.

## Proposed UX

Add a free-form text field (below the graph or in a persistent footer) where the user types a topic and clicks "Generate." Two modes:

### Related topic (default, checkbox unchecked)
- Generates a new domain map that **links to the current domain**
- Sets `parent` to the current domain in the new MAP.md
- Leverages existing concepts (the new map can reference prereqs from the current domain)
- Auto-adds the new domain to the current map's `leads_to`
- Takes user to the new map when done

### Greenfield topic (checkbox: "Unrelated topic?")
- When checked and user clicks Generate: **confirmation warning** — "This will create a standalone domain map with no connection to your current learning. Continue?"
- Generates a fresh MAP.md with `parent: null`, `depth: 0`
- Does NOT modify the current map's `leads_to`
- Takes user to the new map when done

## Questions to answer

1. **Prompt construction:** What prompt to kiro-cli produces a good MAP.md? Test with 3-5 topics. Does it reliably generate the frontmatter + topic blocks format?
2. **Filename convention:** Where does the new map land? `examples/maps/{slug}.MAP.md` + `lessons/{slug}-map.html`? Or just the HTML?
3. **Parent linking:** When generating a related topic, what context should the prompt include from the parent domain? Full MAP.md? Just the orientation + topic titles?
4. **Navigation after generation:** Auto-redirect works (we have `_genCreatedFile`). But if kiro-cli generates a MAP.md and then the map page HTML in sequence, which file do we navigate to?
5. **Input validation:** Same `SAFE_PROMPT_RE` as existing generate? Or more permissive for free-form input?
6. **UI placement:** Below the graph? Sticky footer? Inside the "From here, you could explore" section?

## Deliverable

A findings file answering the above + proposed ticket breakdown (spikes/features). Expected shape:
- Spike: prompt engineering for MAP.md generation (test 3-5 topics)
- Feature: free-form input UI + related/greenfield toggle
- Feature: parent-linking on generation (update current map's leads_to)

## Validation

- **Research complete:** All 6 questions answered with evidence (test output, screenshots)
- **Tickets created:** Follow-on spikes/features filed with e2e validation criteria
