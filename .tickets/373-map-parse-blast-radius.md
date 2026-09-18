---
id: "373"
title: "Isolate malformed-MAP parse failures in _map_for_domain (one bad file 500s all domains)"
status: in_progress
blocked_by: []
priority: medium
type: bug
tags: ["server", "robustness", "risk-review"]
validation_criteria:
  - "A malformed MAP.md breaks only its own domain's status API, never other domains'"
---

# Isolate malformed-MAP parse failures in _map_for_domain (one bad file 500s all domains)

## Intent

One malformed or truncated `*.MAP.md` anywhere in the served tree must degrade only its own
domain, not take down status reads/writes for every domain.

## Context (found 2026-09-18 risk review of the 2026-09-16/17 window)

`tools/serve.py:119-131` resolves a domain by parsing EVERY map in the context on each request,
with no exception handling:

```python
def _map_for_domain(domain: str):
    matches = []
    for path in CONTEXT.maps:
        parsed = load_map(path)          # raises ValueError on bad frontmatter
        if parsed.domain == domain:
            matches.append((path, parsed))
```

`load_map` raises `ValueError("No valid frontmatter in ...")` (`tools/map_parser.py:229`). Because
the loop parses all maps before matching, a single malformed MAP.md makes `_map_for_domain`
raise for EVERY domain — `GET/POST /api/map/{domain}/...` (including progress writes) become
unhandled-exception 500s for healthy domains too.

Introduced by `ea1251b` (2026-09-16, "route library status by map identity") and carried through
`0a5cc44`'s WorkspaceContext refactor (`CONTEXT.maps`). The pre-`ea1251b` code
(`MAPS_DIR.glob(f"*{domain}*MAP.md")` + `candidates[0]`) parsed only the first filename match,
so a bad file broke only its own domain. The identity-based routing itself is correct — the
old glob could select the WRONG map (the reason for the rewrite); the gap is error isolation.

**Currently NOT triggered**: verified 2026-09-18 — all 13 committed MAPs are healthy (id-line
count equals topic count in every file; no duplicate `domain:` values, so the "Ambiguous" 404
path cannot fire). The trigger is any future malformed/truncated MAP.md commit.

Secondary latent path in the same resolver: topics whose `id:` line is missing or invalid get an
**ephemeral random ULID per parse** (`tools/map_parser.py:264-266`). A status POST resolved
against an ephemeral id writes an overlay key no later parse will ever reproduce — the write
succeeds but the status silently never persists. (Related but distinct: #351 covers SR card
identity, not MAP node ids; #371 notes the `tkt`-side mint-before-commit rule already in AGENTS.md.)

## What to build

Wrap per-map parsing so a malformed map surfaces as a 404/422 diagnostic for its own domain
(and ideally a startup/scan warning naming the file) while other domains keep serving. Decide
the write-path behavior for ephemeral ids: reject with an actionable error (run
`tools/migrate_map_ids.py`) rather than silently persisting an orphan overlay key.

## Acceptance criteria

- [ ] With one malformed MAP.md in the tree, `GET /api/map/{healthy-domain}` still returns 200 with data
- [ ] The malformed map's own domain returns a clear 404/422 naming the broken file, not an unhandled 500
- [ ] A fixture test covers the malformed-map case (tmp workspace, one bad + one good MAP)
- [ ] `POST /api/map/{domain}/{slug}/status` against a topic whose MAP lacks a valid persisted id fails loudly with a remediation hint (migrate_map_ids) instead of writing an orphan overlay key

## References

- Commits `ea1251b`, `0a5cc44`; `tools/serve.py:119-131`; `tools/map_parser.py:229, 264-266`
- Complementary: #354 (request-boundary validation of the same API), #351 (SR card identity)
