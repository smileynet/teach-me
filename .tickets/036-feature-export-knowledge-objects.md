---
id: "036"
title: "Feature: export self-contained knowledge objects for sharing"
status: done
priority: low
blocked_by: []
type: feature
tags: [platform]
---

# Feature: export self-contained knowledge objects for sharing

## What to build

Export everything a learner produced about a topic into a single, self-contained artifact another person can consume: lessons, reference docs, diagrams, glossary, SR questions, and knowledge snapshots bundled together.

## Why

A completed teaching workspace is a knowledge artifact — not just for the original learner, but for anyone studying the same domain. Exporting it as a portable bundle lets:
- Colleagues onboard faster (read the lessons + reference docs)
- New learners start with curated material instead of from scratch
- Teams share domain knowledge in a structured, versioned format

## Design sketch

### Export format

A zip/directory containing:

```
export/iceberg-on-aws/
  lessons/           — HTML lessons (self-contained, CSS inlined or bundled)
  reference/         — reference docs
  questions/         — SR question bank (JSONL)
  glossary.json      — all terms defined during the topic
  MANIFEST.md        — what's included, topic description, prerequisites
  README.md          — how to use this knowledge object
```

### Command

```bash
python tools/sr-export.py <topic> --format knowledge-object --output iceberg-on-aws.zip
```

### Import

```bash
python tools/sr-import.py iceberg-on-aws.zip --into ~/code/new-workspace/
```

Unpacks into the target workspace, merges glossary, imports questions with fresh UUIDs.

## Open questions

- Should lessons be fully self-contained (inline CSS/JS) or reference shared assets?
- Include learning records / knowledge snapshots? (Reveals what the original learner struggled with — useful or TMI?)
- Version the export format?
- How to handle lessons that reference external URLs that may go stale?

## Acceptance criteria

- [x] Export command bundles lessons + references + questions + glossary
- [x] Output is self-contained (no broken relative links)
- [x] MANIFEST.md describes contents and prerequisites
- [x] Import into a fresh workspace works (questions get new UUIDs, glossary merges)
- [x] Lessons render correctly without the original workspace's assets

## Resolution (closed 2026-08-11)

Superseded by the MAP.md + domain pages model. With per-domain map pages, generated lessons, and the All Lessons index — sharing a domain IS sharing the `*.MAP.md` + `lessons/` directory. No separate export format needed. The map page + lessons + questions ARE the portable knowledge object.
