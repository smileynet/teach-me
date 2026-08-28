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
5. **Runtime in headless/batch mode** — When no standalone tool exists, use the actual runtime (Godot headless, Unity batch mode). This is the floor, not a fallback.

### When no validator exists (the gdshader problem)

Some domain-specific languages lack CLI tooling entirely. Strategy:

1. **Use the runtime itself** — if the language has a headless/batch mode (Godot, Unity), that's your validator. It catches everything a learner will hit.
2. **Clone all prior art** — search GitHub for `{language} linter`, `{language} LSP`, `tree-sitter-{language}`. Understand the landscape.
3. **Don't build a custom type checker** — regex-based linters give false confidence. They catch errors the runtime already catches instantly, while missing every semantic bug that actually breaks the learner's experience (wrong coordinate space, missing render mode, logic errors).
4. **Visual confirmation is non-negotiable** — for shaders and visual code, "compiles" ≠ "correct". You must look at the output on a real mesh.

## Integration Pattern

```
mise run verify
  → tools/check-lesson.py (HTML structure, links, accessibility)
  → Runtime validation (per-language, using the actual compiler/runtime):
      → .gdshader → Godot headless import (test-scene project at gdhelper-pipeline/test-scene)
      → .gd      → Godot headless import (same project)
      → .py      → python -m py_compile (syntax) + mypy (types)
      → .rs      → rustc --check (full)
      → .ts      → tsc --noEmit (full)
```

**The golden rule: validate code using the same tool the learner uses.** If the learner will open it in Godot, validate it in Godot. If they'll compile with rustc, validate with rustc. Homebrewed regex linters give false confidence — they catch errors the real tool already catches, while missing every semantic and architectural bug that actually breaks the learner's experience.

### For Godot shaders specifically

A test project exists at `D:\code\gdhelper-pipeline\test-scene`. Validation means:
1. Copy the shader to the test project's `shaders/` directory
2. Apply it to a test mesh (the sidewalk, building, or character)
3. Visually confirm: textures appear on correct faces, lighting matches other toon shaders, no invisible geometry
4. Only THEN copy the validated shader to `reference/code/{lesson-slug}/`

This catches what no linter can: wrong coordinate spaces, missing render modes, semantic mismatches between fragment() and light(), and architectural issues with the shader pipeline.

### For ink lesson GDScript specifically

Ink lessons ship a `story_player.gd` that drives the inkgd runtime. Compiling the
story (`ink:validate`) and replaying it in bink (`ink:play`, `ink:transcripts`)
covers the **story logic** — but NOT the Godot integration code. bink is not Godot;
it cannot catch a player that reads the wrong property, mishandles the async
`loaded` signal, or drops per-line tags.

`mise run ink:validate-gd` closes that gap. It runs the shipped players in real
Godot 4 headless (`tools/ink-gd-sync.py` copies the shipped reference in, then
`tools/ink-gd-run.py` drives `ink-test-project/scenes/validate_runtime.tscn`):
instantiate each lesson's player scene, `await` the `loaded` signal, drive the
choice sequence, and assert observable node state (text shown, speaker label set,
`# hidden` line suppressed, ending reached). Exit 0 = pass, 1 = a real runtime
defect. Skips gracefully if Godot is absent.

This is the inkgd analogue of the shader visual gate — the "runs correctly in the
target runtime" tier. It found a real bug the golden transcript missed: a player
reading `current_text` after `continue_story_maximally()` gets only the LAST line
(bink's transcript captures the continue *return value*, which is the full text —
so the story looked correct while the Godot player silently dropped lines). Add a
per-lesson check to `validate_runtime.gd` when a lesson ships a new player.

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
- Building regex-based type checkers when the runtime is available (false confidence — catches what the runtime already catches, misses what actually matters)
- Treating "compiles without errors" as sufficient validation for visual code (shaders can compile perfectly while producing invisible geometry, wrong lighting, or mirrored textures)
