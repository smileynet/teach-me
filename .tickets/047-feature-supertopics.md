---
id: "047"
title: "Feature: supertopics — 'where does this lead?' discovery"
status: open
priority: low
blocked_by: []
type: feature
---

# Feature: supertopics (leads_to)

## What to build

After completing a domain (all topics in MAP.md done), or on request ("where does this lead?"), present what domains this knowledge unlocks.

## Design

### Data model

MAP.md frontmatter includes:
```yaml
leads_to:
  - data-governance
  - streaming-architectures
  - platform-engineering
```

These are domain slugs — potential future MAP.md files. They don't need to exist yet.

### When surfaced

1. **After domain completion:** "You've covered the map. This knowledge opens up: [list with one-line descriptions]. Want to explore one?"
2. **On request:** "where does this lead?" / "what's next after this?" → read leads_to, briefly explain each
3. **At lesson endings (optional):** Subtle mention: "This connects to [supertopic] — something to explore later"

### Framing

Always as opportunity, never obligation:
- ✓ "This knowledge makes [X] accessible when you're ready"
- ✗ "You should learn [X] next"
- ✗ "Prerequisites for [X] complete — proceed?"

### Starting a supertopic

Learner: "start data-governance" → agent generates a new root MAP.md for that domain, treating it as a fresh big request. The `unlocked_by` field in the new MAP.md references the completed domain.

## Acceptance criteria

- [ ] leads_to in MAP.md frontmatter parsed and accessible
- [ ] Presented at domain completion with one-line descriptions
- [ ] "where does this lead?" works mid-domain too
- [ ] Learner can start a leads_to domain (generates new MAP.md)
- [ ] Never framed as obligation — always opportunity language

## Validation

- **Unit:** `load_map` returns correct `leads_to` list from frontmatter. Parser handles empty leads_to gracefully.
- **Integration:** `/api/map/{domain}` response includes `leads_to` field. POST to generate a leads_to domain creates a new MAP.md file detectable by `load_map`.
- **E2E (Playwright):** Navigate to map page → scroll to "Where This Leads" → click a domain → verify generation modal appears → after mock generation → verify new map page loads. Verify language uses "accessible" / "becomes possible" not "you should" / "required".
