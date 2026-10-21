---
id: "092"
title: "Feature: parent-linking on related topic generation"
status: open
blocked_by: ["091"]
priority: medium
validation_criteria:
  - "Related-mode generation (Unrelated unchecked) produces a MAP.md with parent={current-domain} and depth={parent-depth+1}, validated by map_parser"
  - "Parent map's leads_to gains the new child domain idempotently (running twice does not duplicate); verified by re-parsing the parent MAP.md"
  - "new map_parser.add_leads_to(path,slug,why) unit-exercised: adds when absent, no-op when present"
  - "Greenfield mode leaves all other maps' leads_to untouched (diff the parent MAP.md before/after — no change)"
  - "Parent map HTML regenerated after linking so the new leads_to entry appears on the rendered parent page"
---

# Feature: parent-linking on related topic generation

## What to build

TBD

## Acceptance criteria

- [ ] TBD
