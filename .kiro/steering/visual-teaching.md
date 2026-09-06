# Visual Teaching Guidelines

When creating lessons with diagrams or visual aids, follow these evidence-based rules.

## Core Principles (Mayer, Paivio, Sweller)

1. **Every visual has an instructional purpose.** No decoration. If removing it wouldn't hurt understanding, remove it. (Coherence principle, d=0.70)
2. **Labels go ON the diagram.** Never separate a visual from its explanation. (Spatial contiguity, d=0.79)
3. **5-9 elements max per diagram.** Break complex systems into progressive layers. (Cognitive load theory)
4. **Dual code everything.** Every diagram has a one-line verbal summary above it. (Dual coding, Paivio 1986)
5. **Consistent visual vocabulary.** Same color/shape means same thing across ALL lessons. (Signaling principle, d=0.46)
6. **Static over animated.** Animation only for inherently temporal processes. (Tversky et al., 2002)

## Code Block Pedagogy

Code examples are teaching tools, not reference dumps. Every code block requires narrative framing — the prose around it earns the code's place in the lesson.

### Required Framing

1. **Lead-in** (before code): Name the problem or goal this code addresses. One sentence minimum. "We're replacing X with Y because..." or "To solve [limitation from above]..."
2. **Bridge** (between sequential blocks): Explain what limitation or insight motivates the next version. Don't repeat what the code says — explain what *drove* the change.
3. **Connect-back** (after code): Tie the implementation to the concept being taught. "This is [concept] in action" or "Notice how [mechanism] achieves [goal]."

Not every block needs all three — a single standalone example needs lead-in and connect-back. Sequential blocks building on each other need bridges between them.

### Story Arc

A section with multiple code blocks tells a story. Each block should advance the narrative:
- What couldn't we do before? (motivation)
- What does this block add? (contribution)
- What can't we do yet? (sets up the next block)

The reader should feel *progress* through the code, not a list of alternatives dumped without context.

### Anti-Patterns

- Code block preceded only by "Here's the code:" or "Add this:"
- Two code blocks back-to-back with no narrative between them
- Explanation after code that merely restates what each line does
- Showing modifications without stating which file and what changed conceptually

### Diff-Style Code (ticket #157)

When showing modifications to existing code:
- State which file is being modified
- Use red/green diff markers for removed/added lines
- Before the diff: explain *what* you're replacing and *why* (the concept, not the syntax)
- After the diff: state the observable result ("Now when you adjust the slider, the shadow edge...")

### Code Block Metadata (ticket #168)

Tag `<pre>` blocks with file information for automated extraction:

```html
<pre data-file="toon_bands.gdshader"><code>shader_type spatial;
...</code></pre>

<pre data-file="toon_test.gdshader" data-mode="diff"><code>
 // context lines
<span style="color:var(--error)">-removed</span>
<span style="color:var(--success)">+added</span>
</code></pre>
```

- `data-file` — target filename (required for extractable code blocks)
- `data-mode` — `complete` (default, full file), `diff` (patch previous state), `fragment` (illustration only, skip extraction)
- `data-highlight` — comma-separated line numbers or ranges to emphasize (e.g., `"3,5-7"`)
- `data-caption` — brief description of what this block shows (used in extracted README and file labels)

Blocks without `data-file` are treated as inline illustrations and not extracted.

### Downloadable Code Files

Every lesson that names files in code blocks MUST produce those files as downloadable artifacts at `reference/code/{lesson-slug}/`. The lesson includes a "Code Files" section (before "What's Next") with download links using the `download` attribute:

```html
<h2>Code Files</h2>
<p>Download the final-state files from this lesson:</p>
<ul>
  <li><a href="../reference/code/{lesson-slug}/filename.ext" download><code>filename.ext</code></a> — description</li>
</ul>
```

The contract: if you name a file in a `data-file` attribute, the reader can download its final state. Each file represents the fully-assembled version after all diffs in the lesson are applied.

Include a `README.md` in the code directory listing each file with its purpose.

### Exercise Design (Check Your Understanding)

The in-lesson exercise tests **comprehension of major concepts** — not detail recall, not gotchas, not edge cases. It's the learner's moment to prove they understood the lesson's central idea.

**The exercise must test the lesson's Win statement.** If the Win says "you can implement three approaches and explain when to use each," the exercise asks the learner to choose between approaches given constraints — not debug a syntax error.

**Rules:**
1. **Core concepts only** — test the main teaching arc, not peripheral details
2. **Application over recall** — "given this situation, what would you do?" not "what does X stand for?"
3. **Built from lesson content** — use the same code/concepts the lesson introduced, not new unrelated scenarios
4. **One exercise, one concept** — don't cram multiple unrelated questions

**Good exercise patterns:**
- "Your art director needs X. Which approach from this lesson achieves it, and why can't the others?" (trade-off reasoning)
- "A colleague shows you this [incomplete/broken version]. What's missing, and which function provides it?" (pipeline understanding)
- "Explain to a junior dev how [core mechanism] works in 2-3 sentences" (teach-back)
- "Predict: if you change [key parameter] from A to B, what visual change do you see?" (mental model)

**Anti-patterns:**
- Testing a gotcha from a "note" or "warning" callout (that's SR question material, not the exercise)
- Testing debugging of an error that wasn't the lesson's focus
- Questions answerable from general programming knowledge (not specific to this lesson)
- Multi-part questions that test 4 different things

**Design technique — near-transfer with misconception probing (Agarwal 2019, Wiliam 2015):**

The strongest exercise is a **near-transfer** scenario: same mechanism as the lesson, slightly different context. This tests whether the learner has an operational mental model they can apply — not just recall of the exact example shown.

To probe deeper, embed a common misconception in the scenario and ask the learner to explain *why it fails*:

> "A colleague tried [approach that reflects common wrong belief]. It doesn't work. Why not, and what should they do instead?"

This "explain the wrong answer" pattern (a) requires understanding the mechanism, (b) can't be answered by pattern-matching the lesson text, and (c) surfaces whether the learner has crossed the threshold concept. If they can explain why the wrong approach fails, they understand the principle — not just the recipe.

**Separation of concerns:**
- **In-lesson exercise** → tests the ONE core concept, uses the lesson's own code, takes 1-2 minutes
- **SR questions** → test details, gotchas, edge cases, connections — distributed over time via spaced repetition
- **Quiz page** → mixed difficulty, multiple archetypes, covers the full lesson breadth

## Prose Hygiene (low cognitive load, no AI slop)

Lesson prose is read once, cold, by someone learning. Every sentence adds load. Four rules, from a
2026-09-06 prose audit of the gltf-format track (`.kiro/skills/writing-style` is the general reference):

1. **Say it once.** If a heading and the sentence under it make the same claim, or a paragraph restates
   the one before it, cut one. The worst offenders repeat a thesis phrase 3–4× ("the bytes are unreadable
   without me", "one engine node per glTF node") — state it once where it's crispest, then reference it.
   Restatement is the clearest AI tell.
2. **Show difficulty, don't assert it.** Ban "everyone trips on", "notoriously", "the tricky part", "the
   classic X" — they tell the reader to feel confused before they've engaged, and they're unverifiable.
   Replace with the concrete reason it's hard ("Three levels of indirection sit between 'draw this
   triangle' and the raw bytes"). Same for unsourced ranks ("the #1 cause" → "the most common cause").
3. **One idea per sentence for the load-bearing explanation.** Break a colon-then-comma pile-up (3–4
   clauses) into short sentences. "A buffer is raw bytes. A bufferView is a window. An accessor reads that
   window as N typed elements." beats one comma-chained sentence.
4. **One em-dash per paragraph, one notation per list.** Em-dash density is the top structural tell —
   cap at one per paragraph (use a colon or a period instead). Don't mix arrow notation and prose in the
   same bullet list. Also cut: "not just X but Y" frames, filler ("the trick is", "richer", "reportedly"),
   and meta-narration about the document ("this capstone turns...", "so it gets its own section").

After authoring or editing lesson prose, dispatch a prose-check subagent (see `/prose-check`) against
these rules — a fresh reviewer with no context catches restatement and slop the author is blind to.

## Callout Hierarchy (Asides, Alternatives, Notes)

Lessons contain information at different urgency levels. Use the right callout type so learners can triage what needs attention now vs. what's reference for later.

### Callout Types (ordered by reader urgency)

| Type | CSS class | When to use | Reader action |
|------|-----------|-------------|---------------|
| **Key concept** | `.key-concept` | The lesson's core takeaway. One per lesson, at the top. | "This is what I'm here to learn" |
| **Decision** | `.note` with `<strong>When to use which:</strong>` | The learner must choose between approaches. Give criteria. | "I need to pick one — what are my constraints?" |
| **New concept** | `.note` with `<strong>New concept — {name}:</strong>` | Introducing a term/idea not covered in a prior lesson | "File this — I'll need it in 30 seconds" |
| **Comparison** | `.comparison` | Side-by-side pros/cons of approaches just shown | "Which one fits my situation?" |
| **Gotcha/Warning** | `.note` with `<strong>Why X?</strong>` or `<strong>Performance note:</strong>` | Something will bite you if you ignore it | "Don't skip this" |
| **FYI/Alternative** | `.note` with `<strong>Alternative:</strong>` | There's another way, but the lesson chose differently | "Good to know, not blocking" |

### Decision Guidance (the most important callout type)

When a lesson presents alternatives, **always include decision criteria** — never just describe the options. The learner needs to know WHEN to pick each one, not just WHAT they are.

**Required structure for decision callouts:**

1. **Name both approaches** — one sentence each, what they do
2. **When to use each** — concrete criteria (not "it depends"). Constraints, project shape, or observable conditions that make the choice obvious
3. **Default recommendation** — if one is safer/simpler for beginners, say so explicitly ("Use X unless you have a specific reason for Y")

**Example (good):**
> **When to use which:**
> - Explicit varying — safe default. Use when combining triplanar with other vertex effects.
> - `world_vertex_coords` — simpler for pure-triplanar, fragment-only materials.
> - **Rule of thumb:** If your shader has `light()` or modifies VERTEX, use varyings.

**Example (bad):**
> **Alternative:** You could also use `world_vertex_coords`. It's simpler but has trade-offs.

The bad version forces the learner to figure out the decision criteria themselves — which is the instructor's job.

### Placement Rules

- **Decisions** go immediately after presenting both approaches (not before — the learner needs context)
- **New concepts** go at first use, inline with the content that needs them (spatial contiguity)
- **Gotchas** go immediately after the code they apply to (not in a "tips" section at the end)
- **FYI/Alternatives** go after the lesson has committed to its approach — they're escape hatches, not forks in the road

### Anti-patterns

- A bare "Alternative:" that describes what exists without saying when to use it
- "Note:" followed by important decision criteria buried in a paragraph (promote to Decision)
- Multiple note callouts back-to-back (reader glazes over — merge or promote the important one)
- Gotchas that belong in SR questions, not the lesson flow (if it's not blocking comprehension, defer it)

## Color Vocabulary

Colors are defined as CSS custom properties in `assets/style.css` (light + dark variants). Use `var(--svg-*)` in inline SVGs — never hardcode hex.

| Color | Meaning | Variable (stroke) | Variable (fill) | Variable (text) |
|-------|---------|-------------------|-----------------|-----------------|
| Blue | Primary component, input, the thing being discussed | `--svg-primary` | `--svg-primary-fill` | `--svg-primary-text` |
| Green | Success, output, healthy state | `--svg-success` | `--svg-success-fill` | `--svg-success-text` |
| Amber | Warning, caution, operational concern | `--svg-warning` | `--svg-warning-fill` | `--svg-warning-text` |
| Red | Error, anti-pattern, problem | `--svg-error` | `--svg-error-fill` | `--svg-error-text` |
| Gray | Infrastructure, neutral, supporting | `--svg-neutral` | `--svg-neutral-fill` | `--svg-neutral-text` |

Additional variables: `--svg-line` (connector lines), `--svg-text` (general text).

Light mode resolves to the original hex values (blue=#2563eb, green=#16a34a, etc.). Dark mode resolves to lighter/desaturated variants appropriate for dark backgrounds.

## Diagram Selection

| Content type | Tool | Command |
|-------------|------|---------|
| Architecture layers | `draw-diagram.py --type stack` | Vertical layered stack |
| Data/request flows | `draw-diagram.py --type flow` | Left-to-right pipeline |
| Service maps | `draw-diagram.py --type hub` | Central hub with radial spokes |
| Fan-out/fan-in, dependency graphs (≤8 nodes) | `draw-diagram.py --type graph` | Auto-ranked nodes with edges, groups |
| Cyclic graphs, state machines, 9+ nodes | `draw-diagram.py --type graph --backend graphviz` | Auto-layout via Graphviz (dot/neato/fdp) |
| Network topologies (undirected) | `draw-diagram.py --type graph --backend graphviz --engine neato` | Force-directed layout |
| Custom layout, annotated detail | Raw inline SVG | Use patterns from `assets/svg-patterns.md` |
| Sequence diagrams (multi-actor message flows) | D2 CLI | `d2 input.d2 output.svg` |
| Step-by-step buildup of a diagram | Progressive reveal | `data-step` attrs + `assets/progressive-reveal.js` |

## Anti-Patterns (DO NOT)

- Decorative images that don't teach (increases cognitive load, PMC 2024)
- Diagram on one part of the page, explanation on another (split-attention effect)
- Text that merely restates what the visual shows (redundancy principle)
- Complex diagrams with 10+ elements at one level (overloads working memory)
- Inconsistent colors/shapes between lessons
- D2 sketch mode for inline SVGs (3-4x file size: 78-98KB vs 19-26KB normal mode — use normal mode by default, sketch only for standalone files where approachability outweighs size)

## Accessibility (WCAG 2.1 compliance)

Every informative SVG requires:
- `role="img"` on the `<svg>` element
- `<title>` as first child with a brief description of what the diagram shows
- `aria-labelledby` linking to the title's ID
- `viewBox` only (no fixed width/height) — responsive scaling via CSS `max-width:100%; height:auto`

**Color independence:** Do not rely on color alone to convey meaning. Every color-coded element must also have a text label. The color vocabulary reinforces meaning — it does not carry it.

**Progressive reveal accessibility:** When using `data-step` for step-through diagrams, ensure `aria-live="polite"` on the container so screen readers announce new content as steps advance.

**The `--title` flag on draw-diagram.py handles all of the above automatically.** For hand-written SVGs, follow the accessibility pattern in `assets/svg-patterns.md`.

## Implementation

- Read `assets/svg-patterns.md` for reusable SVG snippets
- Inline SVG directly in lesson HTML (zero dependencies)
- Use `draw-diagram.py` for standard types — outputs accessible, responsive SVG to stdout
- For complex auto-layout (sequence diagrams, state machines), use D2: `d2 input.d2 output.svg`
- Render `.mmd`/`.d2` batch files with `tools/render-diagrams.sh` (outputs to `assets/generated/`)

## Single-Axis Preferences

When adding user preferences to the reading panel, each control should modify ONE behavior axis — not introduce modal switching. Apply this when:

- A proposed toggle would change the DOM structure (e.g., "Flow vs Sections" was wrong; "start collapsed" was right)
- A proposed mode switch can be decomposed into independent booleans (e.g., "cards + collapsible" is two axes, not one mode)
- Two options share most behavior and differ only in a default value (that's a preference, not a mode)

Don't apply this to genuinely distinct page types (map page vs lesson page) or features that require coordinated multi-property changes (theme dark/light is one axis despite changing many CSS vars).
