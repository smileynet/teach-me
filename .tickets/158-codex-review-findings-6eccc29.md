---
id: "158"
title: "Confirm and address Codex review findings through 6eccc29"
status: done
blocked_by: []
priority: high
---

# Confirm and address Codex review findings through 6eccc29

## Review provenance

- Reporter: Codex
- Review run: `17cac09f-7d9a-4a62-a1fd-4a31e78a3966`
- Review target: `6eccc29eafd1ec2da6dc9cfa9700f03ee705416c`
- Review coverage: `bbd96d3cef66418f5c2378e313f07c262d491bd0..6eccc29eafd1ec2da6dc9cfa9700f03ee705416c`
- Confirmation status: confirmed (all 3 findings reproduced and addressed)

These findings were produced by Codex. They are reviewer hypotheses, not
established defects. The agent working this ticket must reproduce and confirm
each finding against current code before changing it.

## Findings

### F1 — high: domain traversal writes ingestion artifacts outside the requested workspace

- Location: `tools/ingest_source.py:51`
- **Status: CONFIRMED and FIXED**
- Reproduction: `--domain ../../escaped` wrote files to `/tmp/escaped/` outside workspace
- Fix: Added `_sanitize_domain()` (strips `/`, `\`, `..`, non-slug chars) + `is_relative_to()` containment check
- Regression test: `TestF1PathTraversal` (3 tests)

### F2 — high: successful HTML URL extraction collapses document structure into one chunk

- Location: `tools/fetch_url.py:40`
- **Status: CONFIRMED and FIXED**
- Reproduction: trafilatura plain text labeled "html" → chunk_html → 1 "Introduction" chunk
- Fix: Added `_detect_extracted_format()` — checks for HTML tags/markdown headings in extracted content; plain text now labeled "text" and routed to `chunk_plaintext()`
- Regression test: `TestF2ExtractedTextFormat` (4 tests)

### F3 — high: ticket 139 is closed despite unfulfilled ingestion acceptance criteria

- Location: `.tickets/139-feature-source-ingest-pipeline.md:13`
- **Status: CONFIRMED and CORRECTED**
- Fix: AC rewritten — 5 criteria genuinely met (checked), 4 criteria honestly assessed as not yet implemented (unchecked): section IDs, keyword index, format rejection, PDF integration test
- These deferred items are real gaps but don't block the core pipeline functionality

## Acceptance criteria

- [x] Every finding is independently marked confirmed, rejected, or obsolete
- [x] Rejected or obsolete findings include evidence and rationale
- [x] Confirmed findings are corrected
- [x] Regression tests cover confirmed defects where practical
- [x] Relevant build, test, and lint checks pass
- [ ] Corrected changes receive a fresh review
