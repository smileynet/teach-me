# Code Validation for Teaching Content

When writing lessons that include executable code, **validate every code block before publishing.** A learner encountering broken code loses trust in the material and conflates "I don't understand this" with "this doesn't work" — the worst possible confusion for learning.

## The Validation Contract

Every lesson with code blocks MUST have:
1. **Final-state files** at `reference/code/{lesson-slug}/` — the assembled output after all diffs applied
2. **A validation step** that confirms those files are syntactically and semantically correct
3. **Integration with `mise run verify`** — validation runs automatically, not manually

## Finding Validation Tools (any language)

Before writing code-based lessons for a new domain, research validation tooling:

### Discovery checklist

| Question | Where to look |
|----------|---------------|
| Does the language have a CLI compiler/interpreter? | Official docs — `rustc --check`, `python -c`, `tsc --noEmit` |
| Is there a standalone linter? | Package registries — `eslint`, `clippy`, `flake8`, `golangci-lint` |
| Does the editor tooling expose a CLI? | LSP servers sometimes have `--check` modes |
| Can the runtime validate without executing? | `python -m py_compile`, `ruby -c`, `perl -c` |
| Is there a type checker? | `mypy`, `pyright`, `flow`, `tsc` |

### Priority order (most to least reliable)

1. **Official compiler/interpreter** — `rustc`, `go build`, `javac`, `gcc`. Always right.
2. **Language-specific linter** — `eslint`, `clippy`, `shellcheck`. Catches more than syntax.
3. **LSP in check mode** — When no CLI exists, wrap the LSP's diagnostic endpoint.
4. **Type checker** — For dynamic languages where the runtime won't catch mismatches.
5. **Custom validator** — Build one using the language's type system data (last resort).

### When no validator exists (the gdshader problem)

Some domain-specific languages lack CLI tooling entirely. Strategy:

1. **Clone all prior art** — search GitHub for `{language} linter`, `{language} LSP`, `tree-sitter-{language}`
2. **Study what exists** — dispatch subagents to read each repo's architecture
3. **Extract reusable data** — builtin type definitions, keyword lists, AST schemas
4. **Build a minimal checker** — even syntax + known-type validation catches 80% of real errors
5. **Integrate the runtime** — if the language has a headless/batch mode (Godot, Unity), use it for full validation in CI

### The 80/20 rule for custom validators

A simple type checker that knows:
- What variables exist in each scope (builtins + declared)
- What type each variable is
- What operators are valid between which types

...catches the majority of bugs learners will hit. You don't need a full compiler — you need enough to catch `vec2 = vec3` assignment errors.

## Integration Pattern

```
mise run verify
  → tools/check-lesson.py (HTML structure, links, accessibility)
  → tools/validate-code.py (per-language validation of reference/code/ files)
      → .gdshader → tools/validate-shaders.py (type-aware)
      → .gd      → gdparse --check (syntax)
      → .py      → python -m py_compile (syntax) + mypy (types)
      → .rs      → rustc --check (full)
      → .ts      → tsc --noEmit (full)
```

Each language handler:
1. Discovers files by extension in `reference/code/`
2. Runs the best available validator
3. Reports errors with file + line number
4. Returns structured results (pass/fail per file)

## When Adopting a New Teaching Domain

Before generating the first lesson:

1. **Identify the code languages** the lessons will use
2. **For each language:** find or build a validator (see discovery checklist)
3. **Add a handler** to the validation pipeline
4. **Run validation on the first lesson** before publishing

This is a hard gate — don't publish code-based lessons without validation tooling in place. A broken first impression is worse than a delayed lesson.

## Anti-patterns

- Publishing code without running it through any validator ("it looks right")
- Relying on the agent's parametric knowledge of syntax ("I'm confident this compiles")
- Testing only the final file when lessons show incremental diffs (each intermediate state matters)
- Skipping validation for "simple" code blocks (the triplanar bug was 3 characters wrong)
