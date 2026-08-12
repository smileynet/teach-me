# AGENTS.md — teach-me

Test bed for learning-oriented agent skills. Refined here, then ported to crew-research for global deployment.

## Workspace Layout

```
.kiro/skills/       — agent skills (teach, quiz-me, wait-what, jargon, visual-qa, theme, etc.)
.kiro/steering/     — visual-teaching guidelines
.memory/            — persistent knowledge (CONTEXT.md glossary, ADRs, research findings)
.scratch/           — ephemeral (gitignored) — only visual-qa output regenerated on run
.references/        — cloned reference repos (gitignored, rehydrate via mise run rehydrate)
tools/              — project scripts (draw-diagram, visual-qa, theme-preview, render-diagrams, sr-*)
palettes/           — color palette definitions (JSON)
lessons/            — HTML lessons (the teaching output)
reference/          — compressed reference docs (scannable work artifacts, alongside lessons)
learning-records/   — what the learner has demonstrated understanding of
assets/             — shared components (style.css, glossary, quiz, progressive-reveal, theme-toggle)
.tickets/           — local ticket tracking
examples/           — test fixtures and example workspaces (MAP.md samples, topic examples)
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
| Install deps | `mise run setup` | drawsvg + graphviz + playwright + rich via uv |
| Generate diagram | `mise run draw -- --type flow --data '{...}'` | SVG to stdout (builtin layout) |
| Generate complex diagram | `mise run draw -- --type graph --backend graphviz --data '{...}'` | Auto-layout via Graphviz |
| Render .mmd/.d2 | `mise run render-diagrams` | Batch render to assets/generated/ |
| SR status | `mise run sr` | What's due, health summary |
| SR review | `mise run sr:review` | Review all due (or `-- topic-slug` for one topic) |
| SR quality check | `mise run sr:check` | Leech detection, prompt format issues |
| SR analytics | `mise run sr:analytics` | Knowledge %, what's decaying, load forecast |
| SR lifecycle | `mise run sr:lifecycle -- suspend ID` | Suspend, retire, reset, sync-lessons |
| Visual QA | `mise run visual-qa` | Exercise all components, report pass/fail |
| Theme preview | `mise run theme-preview -- --palette palettes/purple-night.json` | Preview + contrast validation |
| Health check | `mise run doctor` | Verify tools, venv, references |
| Smoke test | `mise run verify` | Quick draw-diagram test |
| Clone references | `mise run rehydrate` | Clone repos from REFERENCES.md |
| Open lesson | `mise run open-lesson` | Open latest lesson in browser |
| Quick-check page | `mise run sr:quick-check -- [topic] [--all]` | Generate quick-check review HTML from due SR cards |
| Topic quiz page | `python tools/generate-quiz-page.py --lesson-id ID --title T --lesson-file F --map-page M` | Generate standalone quiz page for a topic (all questions, not just due) |
| Export to Anki | `mise run sr:export-anki -- [topic] [--output path]` | Export cards to .apkg |
| Generate map page | `mise run map:generate -- <MAP.md> [--output path]` | Interactive map HTML from MAP.md |
| Generate index | `mise run index:generate -- [--scan-dir path]` | All Lessons dashboard from MAP.md files |

## Workflow

| Situation | Action |
|-----------|--------|
| Writing a lesson | Teach skill produces lesson + reference doc + SR questions + glossary JSON |
| After a lesson | Run jargon skill to annotate domain terms |
| After UI changes | `mise run visual-qa` to verify components still work |
| Before progression | quiz-me for Socratic dialog (learner explains, agent probes) |
| Reviewing retention | `mise run sr:review` (all topics) or `mise run sr:review -- topic-slug` |
| Leaving a ticket | Ticket is DONE (all AC checked) or OPEN with an update note. No partial closes. No moving on with unchecked boxes. |
| Validating work | Validate from the user's perspective (Playwright click-through, curl the endpoint, load the page). Prefer linters, syntax checkers, and templates over formal test suites. Only write maintained tests for libraries with multiple consumers (e.g., map_parser.py). |
| Session start | `mise run sr` to check if cards are due before new material |
| After writing questions | `mise run sr:check` as quality gate |
| Checking knowledge health | `mise run sr:analytics` for decay alerts and load forecast |
| Card is leeching | Suspend via `mise run sr:lifecycle -- suspend ID`, rewrite the prompt |
| New domain term | Add to `.memory/CONTEXT.md` immediately |
| Significant decision | Write ADR in `.memory/adr/NNNN-slug.md` |
| Changing colors | Use theme skill (preview → validate contrast → apply) |
| Complex diagram needed | Use `--backend graphviz` for cycles, state machines, 9+ nodes |

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
| Don't omit lesson-actions.js | Every lesson includes `<script src="../assets/lesson-actions.js">` — provides consistent nav + quiz buttons |
| Don't ship silent buttons | Interactive buttons must have visible hover state + click feedback (animation, color change, or navigation) |

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
