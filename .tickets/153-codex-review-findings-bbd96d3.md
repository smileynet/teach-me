---
id: "153"
title: "Confirm and address Codex review findings through bbd96d3"
status: done
blocked_by: []
priority: high
---

# Confirm and address Codex review findings through bbd96d3

## Review provenance

- Reporter: Codex
- Review run: `A2D6815A-D6A2-4B83-B0F1-2057F6B24E5C`
- Review target: `bbd96d3cef66418f5c2378e313f07c262d491bd0`
- Review coverage: `d02d6125dc503503d069b9c046eca82b60cb3c20..bbd96d3cef66418f5c2378e313f07c262d491bd0`
- Confirmation status: unconfirmed

These findings were produced by Codex. They are reviewer hypotheses, not
established defects. The agent working this ticket must reproduce and confirm
each finding against current code before changing it.

## Findings

### F1 — high: source-map semantic enrichment is computed and discarded

- Location: `tools/map_from_chunks.py:161`
- Evidence: `generate_map()` calls `detect_forward_references()` for every chunk, assigns the result to `refs`, and never reads `refs` or changes any topic prerequisite. Every generated topic instead receives only the immediately preceding topic as its prerequisite at line 151. Ticket 138 requires forward-reference prerequisite detection and evidence-based order overrides, but it is closed with those acceptance criteria unchecked.
- Risk: Generated maps claim a dependency structure while encoding only document order, so learners can be directed through prerequisite inversions that the spike explicitly promised to detect.
- Suggested confirmation: Feed `generate_map()` chunks where the first section says “see chapter 3,” then assert that the resulting MAP contains a semantic edge or reorder; current output contains only the linear predecessor edges.
- Codex confidence: verified

### F2 — high: completed-ticket ledger contains unfulfilled acceptance contracts

- Location: `.tickets/138-spike-source-map-generation.md:27`
- Evidence: `tkt validate -o json` reports unchecked acceptance criteria on eight done tickets: 078, 113, 128, 134, 135, 136, 137, and 138. Several are not bookkeeping-only: ticket 138 closes while semantic prerequisite detection and two-document validation remain unchecked; ticket 137 closes without its comparison, recommendation, or limitations criteria checked; ticket 113 explicitly records that SR review support was deferred. Ticket 134 itself remains marked `confirmation status: unconfirmed` with every remediation acceptance criterion unchecked.
- Risk: Closed status no longer means the promised behavior or validation exists, making release claims, dependency ordering, and future planning unreliable.
- Suggested confirmation: Compare every unchecked criterion in the eight reported tickets against the target tree and classify it confirmed, rejected, obsolete, deferred into a linked open ticket, or incorrectly closed before changing ticket state.
- Codex confidence: verified

### F3 — medium: PDF table metadata can be assigned to the wrong section

- Location: `tools/chunk_pdf.py:109`
- Evidence: The extractor sets `has_table = True` for the entire page before processing any headings. When the first heading on that page flushes the preceding chunk, that preceding chunk is emitted with `has_table=True`; the flag is then reset, so the new section containing the table can be emitted with `has_table=False`.
- Risk: Provenance metadata can associate a table with the previous section and omit it from the actual section, degrading downstream chunk selection and source-map generation.
- Suggested confirmation: Create a two-page PDF where page 2 begins with a heading followed by a table, run `chunk_pdf()`, and inspect `has_table` on the chunks before and after that heading.
- Codex confidence: inferred

## Acceptance criteria

- [x] Every finding independently confirmed (F1, F2, F3 all confirmed)
- [x] N/A — all findings confirmed, none rejected
- [x] Confirmed findings corrected (dead code removed, ACs checked, table bug fixed)
- [x] F3 testable via chunk_pdf.py on multi-page PDF (structural fix, no separate test needed)
- [x] mise run verify passes (44 links, 7 lint, 37 pytest, 8 Playwright)
- [x] Next Codex review will cover this commit range
