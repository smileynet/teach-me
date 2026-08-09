# AGENTS.md — teach-me

Test bed for learning-oriented agent skills. Refined here, then ported to crew-research for global deployment.

## Workspace Layout

```
.kiro/skills/       — agent skills (teach, quiz-me, wait-what, jargon, visual-qa, theme, etc.)
.kiro/steering/     — visual-teaching guidelines
.memory/            — persistent knowledge (CONTEXT.md glossary, ADRs, research findings)
.scratch/           — ephemeral (gitignored) — only visual-qa output regenerated on run
.references/        — cloned reference repos (gitignored, rehydrate via mise run rehydrate)
tools/              — project scripts (draw-diagram, visual-qa, theme-preview, render-diagrams)
palettes/           — color palette definitions (JSON)
lessons/            — HTML lessons (the teaching output)
reference/          — compressed reference docs (scannable work artifacts, alongside lessons)
learning-records/   — what the learner has demonstrated understanding of
assets/             — shared components (style.css, glossary, quiz, progressive-reveal, theme-toggle)
.tickets/           — local ticket tracking
```

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| teach | `/teach`, "teach me", "next lesson" | Multi-session learning with stateful workspace |
| quiz-me | `/quiz-me`, "test me" | Socratic dialog — learner explains, agent probes |
| wait-what | `/wait-what`, "I don't understand" | Re-explain when comprehension fails |
| jargon | `/jargon`, "annotate terms" | Post-authoring: annotate domain jargon with tooltips |
| visual-qa | "visual qa", "check the ui" | Exercise components, capture screenshots, report |
| theme | "theme", "colors", "palette" | Preview, validate, and apply color palettes |
| draw-diagram | "draw diagram", "generate SVG" | Generate inline SVG teaching diagrams |
| browse-and-verify | "validate link", "check this URL" | Dispatch browser agent for URL validation |

## Commands

| Task | Command | What it does |
|------|---------|-------------|
| Install deps | `mise run setup` | drawsvg + playwright via uv |
| Generate diagram | `mise run draw -- --type flow --data '{...}'` | SVG to stdout |
| Render .mmd/.d2 | `mise run render-diagrams` | Batch render to assets/generated/ |
| Visual QA | `mise run visual-qa` | Exercise all components, report pass/fail |
| Theme preview | `mise run theme-preview -- --palette palettes/purple-night.json` | Preview + contrast validation |
| Health check | `mise run doctor` | Verify tools, venv, references |
| Smoke test | `mise run verify` | Quick draw-diagram test |
| Clone references | `mise run rehydrate` | Clone repos from REFERENCES.md |
| Open lesson | `mise run open-lesson` | Open latest lesson in browser |

## Workflow

| Situation | Action |
|-----------|--------|
| Writing a lesson | Teach skill produces lesson + reference doc + glossary JSON in one pass |
| After a lesson | Run jargon skill to annotate domain terms |
| After UI changes | `mise run visual-qa` to verify components still work |
| Before progression | quiz-me for Socratic dialog (learner explains, agent probes) |
| New domain term | Add to `.memory/CONTEXT.md` immediately |
| Significant decision | Write ADR in `.memory/adr/NNNN-slug.md` |
| Changing colors | Use theme skill (preview → validate contrast → apply) |

## Constraints

| Don't | Do instead |
|-------|-----------|
| Don't accumulate scratch files | Promote to `.memory/` or delete after use |
| Don't put implementation details in CONTEXT.md | Use ADRs for decisions with rationale |
| Don't commit .scratch/ or .references/ | Both are gitignored |
| Don't load Playwright MCP in default agent | Dispatch to `browser` specialist |
| Don't assume subagent tool trust inherits | Each specialist needs its own `allowedTools` |
| Don't teach from parametric memory | Cite sources in every lesson |
| Don't invent specific numbers | Cite or frame as general |
| Don't ask recall questions in gates | Ask "explain to [person] why..." |

## Environment

- Codex sandbox (bwrap) fails: `bwrap: loopback: Failed RTM_NEWADDR`. Use `codex exec --dangerously-bypass-approvals-and-sandbox`.
- Playwright MCP requires headless mode (no X server).
- Bedrock image limit: >20 images in conversation history triggers 2000px max. Resize to ≤768px; dispatch fresh subagents for image analysis in long sessions.

## Skill Format (kiro-cli)

Skills live in `.kiro/skills/<name>/SKILL.md`. Frontmatter:
```yaml
name: skill-name
description: "What it does. Trigger: trigger phrases."
metadata:
  type: process|protocol|reference
  invocation: user-only|both
  practice: null
```
Skills auto-loaded via `skill://.kiro/skills/**/SKILL.md`.

## Design Posture (ADR 0001)

The teach skill's posture is **knowledgeable colleague at a whiteboard** — not course instructor. Informal, mission-driven, direct. Tone: assumes intelligence, doesn't over-explain motivation, gets to mechanics quickly.

## When Blocked

1. Check `.memory/` for prior decisions and context
2. Check `.references/` for patterns in reference repos
3. If domain term is ambiguous — ask, then record in CONTEXT.md
4. If architecture choice needed — write ADR with options, propose to user

## Test Fixture

The root-level teaching workspace (MISSION.md, RESOURCES.md, lessons/, reference/, learning-records/) is the **Iceberg on AWS** example — a real teaching session used as a test fixture. See `examples/README.md` for what to test feature changes against.
