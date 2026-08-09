# Worked Example Ideas

Teaching workspace examples to validate the skill across diverse domains. Each represents a different learning shape (knowledge-heavy vs skills-heavy, technical vs physical, solo vs community-dependent).

## Current fixture

| Topic | Domain | Status |
|-------|--------|--------|
| Apache Iceberg on AWS | Cloud data engineering | ✅ Active (test fixture) |

## Candidates

| Topic | Domain | Learning shape | Why it tests something different |
|-------|--------|---------------|----------------------------------|
| Making roguelikes in Rust | Game dev + programming | Knowledge → skills (code, iterate, play) | Tests a build-and-iterate loop; output is runnable software |
| Training an AI model to play StarCraft | Reinforcement learning + AI | Knowledge-heavy (math, theory) → experiment | Tests long theoretical ramp before any hands-on payoff |
| Personalized workout routines | Fitness / health | Skills-heavy (physical practice) | Tests real-world action steps agent can't verify; wisdom from communities matters most |
| Building a square foot garden | Gardening / DIY | Seasonal constraints, physical project | Tests time-bound learning (can't skip seasons); reference docs are books, not URLs |
| Making Blender assets and shaders in the style of Esoteric Ebb | 3D art + shader programming | Visual/creative + technical | Tests teaching aesthetic judgment (not just correctness); reference is visual, not textual; requires tool proficiency (Blender nodes, GLSL) |

## Selection criteria for new examples

Pick examples that stress-test different aspects:

- **Can the agent verify success?** (code runs ✓ / garden grows ✗)
- **Is the primary source textual or visual?** (docs ✓ / YouTube tutorials, art references)
- **Is practice physical or digital?** (keyboard ✓ / body, tools, soil)
- **Does it need community/wisdom?** (solo-learnable vs needs feedback from practitioners)
- **What's the time horizon?** (one afternoon vs months/seasons)
- **Is "correct" objective or subjective?** (tests pass vs "looks good in that style")

## SR stress-test analysis

How do the spaced repetition features hold up across these domains?

| Domain | Question style works? | Answer criteria works? | Risk |
|--------|----------------------|----------------------|------|
| **Iceberg on AWS** | ✅ "Why does X..." | ✅ "Should mention: mechanism" | None — this is our home turf |
| **Roguelikes in Rust** | ✅ "Why structure ECS this way?" | ⚠️ Code cards need `prompt_code` | Code review ≠ concept review — need both modes |
| **RL / StarCraft** | ⚠️ Math intuition hard to prompt for | ⚠️ "Should mention: gradient clipping prevents catastrophic updates" works, but learner may not trust self-grade on math | Long ramp before questions make sense |
| **Workout routines** | ✅ "Why does progressive overload work?" | ✅ Conceptual criteria work fine | SR covers the WHY, not the DID-YOU-DO-IT. That's fine — SR doesn't track practice, it tracks understanding |
| **Square foot garden** | ✅ "Why companion planting?" | ✅ "Should mention: nitrogen + pest deterrence" | Seasonal timing makes spacing tricky — concepts learned in spring reviewed in winter |
| **Blender / Esoteric Ebb** | ⚠️ "Why does this node setup produce bloom?" works. "Does this look right?" doesn't. | ⚠️ Technical nodes = criteria work. Aesthetic judgment = can't self-grade | Split: technical understanding (SR) vs aesthetic eye (needs visual reference + community feedback) |

### What this tells us

1. **SR is correctly scoped to conceptual understanding.** It doesn't need to verify skill execution or aesthetic judgment — that's what the Socratic gate and community wisdom are for.
2. **The "Could you explain this?" framing works universally.** Even for physical skills (workout) or creative skills (Blender), there's a conceptual layer ("why does this approach work?") that SR handles well.
3. **Code-heavy domains benefit from `prompt_code` fields** — the spike 037 work directly enables roguelike/Rust and RL/Python questions.
4. **The criteria-based answer format scales** — "Should mention: X + Y" works for mechanism, math intuition, biology, and design reasoning alike.
5. **The gap is practice tracking, not concept review.** If we ever need "did you do 3 sets" or "did you render the shader," that's a different system (habit tracker / project milestones), not SR.

### Recommended next example topics (priority order)

1. **Roguelikes in Rust** — tests code-heavy SR cards, build-and-iterate workflow, and the `prompt_code` field we just built. Close enough to our tooling to validate without a huge leap.
2. **Workout fundamentals** — tests the boundary between conceptual SR ("why progressive overload?") and physical practice the agent can't verify. Validates that our system correctly stays in its lane.
3. **Blender/Esoteric Ebb** — tests visual reference, aesthetic judgment, and the split between technical understanding (node graphs, GLSL — SR works) and creative eye (SR doesn't). Hardest test.

## Notes

- The Blender/Esoteric Ebb example is particularly interesting because it tests visual style reference (how does the agent teach an aesthetic?) and shader node graphs (visual programming, not text code)
- Workout routines test the "wisdom" pillar hardest — the agent should delegate to communities early
- StarCraft RL tests the longest knowledge ramp before the learner can do anything meaningful
