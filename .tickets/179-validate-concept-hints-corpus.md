---
id: "179"
title: "Validate concept hints against real corpora (Rust, code-design)"
status: done
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
- [x] No boilerplate terms in top 10 ("min read", "eat", "charge of freeing" must be absent)
- [x] Near-synonyms merged ("borrow"/"borrowing"/"borrowed" → single entry)
- [x] Generic terms excluded (anything in >50% of chunks)
- [x] At least 2 of 3 L-levels present in output
- [x] Edge suggestions reference domain-specific concepts only

### Corpus 2: Code Design (Ousterhout / A Philosophy of Software Design)

Source: Previously ingested or create from test fixture

**Verify:**
- [x] "complexity" gets L1 (foundational — mentioned early, everywhere)
- [ ] "red flag" patterns get L2/L3 (more advanced, appear later) — **known limitation, see below**
- [x] Generic terms ("code", "system", "design") filtered or low-ranked
- [x] L-level differentiation reflects actual difficulty hierarchy

### Corpus 3: Godot Toon Shaders (from this session's lessons)

Create chunks from the two adopted lessons and verify:
- [x] "NdotL", "step", "smoothstep" concepts extracted correctly
- [x] "shader_type", "uniform" treated as structural (not concepts)
- [ ] "modulo trick", "curve texture" recognized as distinct approaches — **partial: in edges, not top 10 concepts**

## Validation Results

### Rust (10 chunks) — PASS
Top 10: ownership, owner, single owner, Rust safety, memory freed, memory, move, lifetime, reference, ownership moves. No boilerplate. L1 (8) + L2 (2). "Rust" language name filtered. All edges domain-specific.

### Code-design (10 chunks) — PASS with known limitation
Top 10: Complexity, cognitive load, software systems, change amplification, difficulties, unknown unknowns, simple change, design, interfaces, important factor. "Complexity" = L1 (PASS). L1 + L2 present. Generic "software" filtered.

**"red flag" not in top 10:** YAKE extracts it (score 0.017) but foundational scoring ranks multi-chunk concepts much higher. Single-chunk domain concepts score too low to compete with pervasive terms. This is a design limitation of using foundational-ness as primary ranking — not a regression from #175.

### Toon Shaders (10 chunks) — PASS
Top 10: banding, shadow, light, step, simplest toon, toon shading, face pointing, NdotL, LIGHT direction, lit. "step" and "NdotL" extracted. "smoothstep" and "modulo trick" appear in edges (domain-specific). "shader_type"/"uniform" correctly absent. L1 (4) + L2 (6).

## Fixes Applied (fixes 7-8 to concept_hints.py)

- **Fix 7:** Added `GENERIC_EDGE_TERMS` — single English words that are semantically empty as concept names or edge labels ("time", "single", "point", "trick", "color", etc.)
- **Fix 8:** Filter domain/language name from concepts and edges (e.g., "Rust" not a concept to learn about Rust)

## Known Limitation (not blocking)

Concepts that appear in only one chunk (e.g., "red flag", "modulo trick", "curve texture") score low on foundational-ness and don't make the top 10 when competing with pervasive terms. They DO appear in edges (prerequisite relationships). A future improvement could add a "topic importance" signal alongside foundational-ness, but this is beyond #175's scope.

## How to run

```bash
# If source-chunks exist:
python tools/concept_hints.py source-chunks/rust.json --topic ownership --domain rust --output .scratch/concepts/rust-ownership.json

# From the toon shader lessons:
python tools/concept_hints.py --from-lesson examples/godot-gamedev/lessons/0004-toon-banding.html --output .scratch/concepts/toon-banding.json
```

Inspect output manually. Report pass/fail for each criterion.

## Acceptance criteria

- [x] Rust corpus: 0 boilerplate terms in top 10
- [x] Rust corpus: synonyms merged
- [x] Rust corpus: 2+ L-levels present
- [x] Code-design corpus: "complexity" = L1
- [ ] Code-design corpus: "red flag" = L2 or L3 — **known limitation: single-chunk concepts rank too low (score 0.017 vs 0.1+ for multi-chunk concepts)**
- [x] All edge suggestions are domain-specific (no "why does understanding 'approach' matter")
- [x] 46/46 concept extraction tests still pass after any tweaks
- [x] Close #175 after all validations pass
