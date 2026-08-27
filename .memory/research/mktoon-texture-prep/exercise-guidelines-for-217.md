# Exercise Guidelines for Lesson 0015 (Ticket #217)

## 1. What the Exercise MUST Test (the Win Statement)

The lesson's Win is: **the learner can analyze PBR texture sets and identify what fights toon shading.**

The exercise must test THIS — not syntax, not gotchas, not detail recall. Specifically:
- Can the learner look at texture channels and identify which create problems under toon banding?
- Can they articulate WHY continuous texture detail conflicts with discrete shading?
- Can they decide what to keep, discard, or simplify?

The ticket's proposed exercise (show two textures, ask which channels are problematic) aligns well — it's application over recall.

## 2. Good Patterns vs Anti-Patterns

### Good patterns (use these):

- **Trade-off reasoning:** "Your art director needs X. Which texture channels are causing problems, and why can't you just keep them all?" 
- **Near-transfer with misconception probing:** "A colleague says 'just turn off the normal map and the toon shader will look fine.' Why doesn't that fully solve the problem? What else needs attention?"
- **Predict:** "If you feed this high-frequency albedo texture into a 3-band toon shader, what visual artifact do you expect to see?"
- **Teach-back:** "Explain to a junior dev why roughness maps are irrelevant to mk_toon_lite in 2-3 sentences"

### Anti-patterns (DO NOT):

- Testing a gotcha from a note/warning callout (e.g., "what hint does the normal map need?" — that's SR material)
- Testing debugging of an error that wasn't the lesson's focus (e.g., "why is the texture washed out?" — source_color hint is peripheral)
- Questions answerable from general programming knowledge (e.g., "what does a normal map encode?")
- Multi-part questions testing 4 different things
- Testing detail recall ("name the 3 enemies") — test APPLICATION of that knowledge instead

### Strongest design technique:

**Near-transfer with misconception probing.** Embed a common wrong belief:

> "A colleague converted their PBR barrel asset by just assigning the albedo texture and disabling the normal map. The toon shading still looks noisy. Why? What's the actual source of the problem, and what would you recommend?"

This tests whether the learner understands that albedo ITSELF can contain continuous gradients that fight banding — not just normal maps.

## 3. Callout Structure for This Lesson

| Callout type | Where to place | Content for 0015 |
|-------------|----------------|------------------|
| **Key concept** (`.key-concept`) | Top, one per lesson | "PBR textures encode continuous properties; toon shaders discretize. Continuous detail + discrete shading = noise." |
| **Decision** (`.note` with `<strong>When to use which:</strong>`) | After presenting the keep/discard/simplify analysis | Decision criteria for each PBR channel: albedo (keep, simplify), normal (simplify or discard), roughness/metallic (discard), AO (repurpose as threshold_map) |
| **New concept** | At first use of "threshold_map" or "band edge noise" | Brief inline definition |
| **Gotcha/Warning** | After code showing texture assignment | `source_color` hint requirement, normal map `hint_normal` gap |
| **FYI/Alternative** | After committing to the "indie middle ground" approach | Reference that AAA studios (Guilty Gear, Genshin) author for toon from scratch |

### Placement rules:
- Decisions go AFTER presenting both approaches (not before)
- Gotchas go immediately after the code they apply to
- FYI/Alternatives go after the lesson has committed to its approach
- Never stack multiple note callouts back-to-back

### Required structure for decision callouts:
1. Name both approaches (one sentence each)
2. When to use each (concrete criteria)
3. Default recommendation for beginners

## 4. Code Block Rules That Apply

- **Every code block needs narrative framing:** lead-in (what problem), connect-back (tie to concept)
- **Sequential blocks need bridges:** explain what drove the change between them
- **Diff-style code:** state which file, use red/green markers, explain what you're replacing and why BEFORE the diff, state observable result AFTER
- **`data-file` metadata required** on extractable blocks (e.g., shader uniform references)
- **Downloadable files contract:** if any `data-file` attribute is used, final-state files must exist at `reference/code/{lesson-slug}/`
- **Story arc:** each block advances a narrative (what couldn't we do → what this adds → what's next)

### Specific to this lesson:
- Shader code showing mk_toon_lite uniforms should be `data-mode="fragment"` (illustration, not full shader)
- The lesson references existing shaders — show relevant snippets with context, not full dumps
- Any texture assignment GDScript should use `data-file` if the learner will replicate it
