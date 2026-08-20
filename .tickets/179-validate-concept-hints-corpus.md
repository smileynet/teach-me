---
id: "179"
title: "Validate concept hints against real corpora (Rust, code-design)"
status: open
blocked_by: ["175"]
priority: high
---

# Validate concept hints against real corpora (Rust, code-design)

## Context

Ticket #175 implemented 6 quality fixes to concept_hints.py — but validation was against the unit test fixtures only (4 short caching chunks). The acceptance criteria require validation against real corpora to confirm the fixes eliminate the noise observed in production.

This is the final gate before closing #175.

## What to do

Run `concept_hints.py` against two real corpora and verify each acceptance criterion:

### Corpus 1: Rust by Example (9+ chunks)

Source: Previously ingested chunks at `source-chunks/rust.json` (or re-ingest from Rust by Example)

**Verify:**
- [ ] No boilerplate terms in top 10 ("min read", "eat", "charge of freeing" must be absent)
- [ ] Near-synonyms merged ("borrow"/"borrowing"/"borrowed" → single entry)
- [ ] Generic terms excluded (anything in >50% of chunks)
- [ ] At least 2 of 3 L-levels present in output
- [ ] Edge suggestions reference domain-specific concepts only

### Corpus 2: Code Design (Ousterhout / A Philosophy of Software Design)

Source: Previously ingested or create from test fixture

**Verify:**
- [ ] "complexity" gets L1 (foundational — mentioned early, everywhere)
- [ ] "red flag" patterns get L2/L3 (more advanced, appear later)
- [ ] Generic terms ("code", "system", "design") filtered or low-ranked
- [ ] L-level differentiation reflects actual difficulty hierarchy

### Corpus 3: Godot Toon Shaders (from this session's lessons)

Create chunks from the two adopted lessons and verify:
- [ ] "NdotL", "step", "smoothstep" concepts extracted correctly
- [ ] "shader_type", "uniform" treated as structural (not concepts)
- [ ] "modulo trick", "curve texture" recognized as distinct approaches

## How to run

```bash
# If source-chunks exist:
python tools/concept_hints.py source-chunks/rust.json --topic ownership --domain rust --output .scratch/concepts/rust-ownership.json

# From the toon shader lessons:
python tools/concept_hints.py --from-lesson examples/godot-gamedev/lessons/0004-toon-banding.html --output .scratch/concepts/toon-banding.json
```

Inspect output manually. Report pass/fail for each criterion.

## Acceptance criteria

- [ ] Rust corpus: 0 boilerplate terms in top 10
- [ ] Rust corpus: synonyms merged
- [ ] Rust corpus: 2+ L-levels present
- [ ] Code-design corpus: "complexity" = L1
- [ ] Code-design corpus: "red flag" = L2 or L3
- [ ] All edge suggestions are domain-specific (no "why does understanding 'approach' matter")
- [ ] 46/46 concept extraction tests still pass after any tweaks
- [ ] Close #175 after all validations pass
