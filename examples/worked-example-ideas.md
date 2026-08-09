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

## Notes

- The Blender/Esoteric Ebb example is particularly interesting because it tests visual style reference (how does the agent teach an aesthetic?) and shader node graphs (visual programming, not text code)
- Workout routines test the "wisdom" pillar hardest — the agent should delegate to communities early
- StarCraft RL tests the longest knowledge ramp before the learner can do anything meaningful
