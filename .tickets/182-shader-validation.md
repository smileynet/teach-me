---
id: "182"
title: "Shader validation tooling for lesson code blocks"
status: open
blocked_by: []
priority: high
---

# Shader validation tooling for lesson code blocks

## Context

Lesson 0005 shipped with a shader error (`MODEL_MATRIX * vec4(NORMAL, 0.0)` pattern instead of `MODEL_NORMAL_MATRIX * NORMAL`). A learner encountered "Error at line 8: Invalid arguments to operator '=': 'vec2, vec3'" — a broken learning experience that could have been caught by automated validation.

Every code-based lesson must have its shader/script code validated before shipping. The `reference/code/{lesson-slug}/` files already contain extracted final-state code — we need a tool that validates them.

## Problem

No mature CLI linter exists for Godot's .gdshader format. Standard GLSL tools (glslangValidator) are incompatible because Godot adds `shader_type`, `render_mode`, engine builtins (MODEL_MATRIX, ALBEDO, etc.), and uniform hints.

## Prior Art (cloned to .references/)

| Repo | Language | Maturity | Type Checking | CLI Mode | Verdict |
|------|----------|----------|---------------|----------|---------|
| gdshader-lsp-cpp | C++ | Production (4.5–4.7) | Full (60+ diagnostics, 4-pass pipeline) | No (LSP only) | **Best source of truth** — JSON builtin data reusable |
| gdshader-lsp | Rust | Alpha (mid-rewrite) | Basic (assignment types, swizzles) | No (LSP only) | Good builtin catalogs, not production-ready |
| gdshader-language-server | Go | Early WIP (v0.6) | None | No | Only completion/hover; parser can't handle real shaders |
| godot-gdshader-toolkit | Python | Vaporware | None | Declared but empty | 0 bytes of implementation |
| tree-sitter-gdshader | JS/C | Syntax only | None | `tree-sitter parse` | Catches syntax errors, misses all semantic issues |

### Key Reusable Assets

1. **gdshader-lsp-cpp's JSON builtin data** (`src/gdshader/data/*.json`) — 115K+ of structured builtin definitions covering ALL shader types/stages with types, docs, qualifiers. Can power a lightweight Python type checker without needing the C++ binary.
2. **gdshader-lsp-cpp's diagnostic taxonomy** — 60+ error codes organized by category (lexical, semantic, shader-specific, warnings). Ready-made "common mistakes" reference.
3. **Rust LSP's builtin catalogs** (`memory/functions.rs`, `memory/variables.rs`) — 80+ functions with overloaded signatures, per-stage variable lists with types.

## Approaches (ranked by feasibility)

### A. Godot headless validation (most accurate)

Extract shader files → place in minimal Godot project scaffold → `godot --headless --import --quit` → parse stderr for errors.

- **Pros:** 100% accurate, catches all type errors, uses actual compiler
- **Cons:** Requires Godot binary (~60-100MB), slow (~3-5s startup), needs project scaffolding

### B. gdshader-lsp-cpp as CLI lint (fastest standalone)

Extract shaders → send LSP `textDocument/diagnostic` requests to the bundled binary → parse responses.

- **Pros:** Fast, cross-platform binaries available, covers Godot 4.5-4.6 builtins
- **Cons:** LSP-only interface needs wrapper, unclear builtin completeness

### C. godot-gdshader-toolkit (most Pythonic)

pip install → run linter on extracted files. Has pre-commit hooks and GitHub Action.

- **Pros:** Python (matches our toolchain), CI-native
- **Cons:** Very new (1 star), unknown quality

### D. Custom type-checker (teach-me specific)

Parse shader files for known patterns, check type consistency of assignments using a simple type propagation engine.

- **Pros:** Catches the exact class of bug we hit, no external deps
- **Cons:** Incomplete coverage, maintenance burden

## Recommended Approach

**Phase 1 (immediate): Python type checker using C++ LSP's JSON data**

1. Extract the builtin JSON data from `gdshader-lsp-cpp` into `tools/lib/gdshader_builtins/`
2. Write `tools/validate-shaders.py` that:
   - Parses `.gdshader` files (regex + simple state machine — enough for type declarations and assignments)
   - Validates: `shader_type` present, all variables used are declared or builtin, assignment types match (vec2≠vec3)
   - Reports errors with line numbers matching Godot's output format
3. Integrate into `mise run verify`

**Phase 2 (later): gdshader-lsp-cpp as LSP lint wrapper**

Write a thin Python LSP client that sends `textDocument/diagnostic` to the C++ binary. Gives full semantic analysis. Requires building the binary (SCons + CMake) or CI artifact download.

**Phase 3 (CI): Godot headless validation**

For release-level confidence, `godot --headless --import --quit` validates shaders with the actual compiler. Add as optional CI step.

## What to build

1. **`tools/validate-shaders.py`** — extracts `.gdshader` files from `reference/code/` dirs and validates them
2. Integration with `mise run verify` pipeline
3. At minimum: syntax validation + type checking of varying/uniform assignments
4. Stretch: full Godot headless CI step

## Acceptance criteria

- [ ] All `.gdshader` files in `reference/code/` are validated by `mise run verify`
- [ ] Type mismatches (vec2/vec3, mat3/mat4) are caught
- [ ] Missing uniform declarations are caught
- [ ] `shader_type` presence validated
- [ ] Tool runs without requiring Godot installed (for basic checks)
- [ ] Integration with check-lesson.py or standalone `validate-shaders` command
- [ ] Known Godot builtins (MODEL_MATRIX, NORMAL, VERTEX, etc.) recognized with correct types
