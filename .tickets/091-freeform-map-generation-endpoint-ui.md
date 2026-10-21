---
id: "091"
title: "Feature: free-form map generation endpoint + UI"
status: open
blocked_by: ["090"]
priority: medium
validation_criteria:
  - "curl POST /api/generate-map {topic:'how DNS resolution works',mode:'greenfield'} returns 202 {id,stream_url}; SSE done event carries a redirect to lessons/{domain}-map.html"
  - "Generated MAP.md passes map_parser.validate() with 0 errors and 5-9 topics (verify via the endpoint, not a hand-written map)"
  - "SAFE_PROMPT_RE/MAX_PROMPT_LEN applied ONLY to the user topic field; the format scaffold is injected server-side (prompt with #[]{} chars must still work)"
  - "Playwright: on a map page, type a topic in the sticky-footer input, click Generate, progress modal streams, browser redirects to the new map HTML"
  - "Playwright: checking 'Unrelated topic?' then Generate shows a confirmation warning before generating"
---

# Feature: free-form map generation endpoint + UI

## What to build

TBD

## Acceptance criteria

- [ ] TBD
