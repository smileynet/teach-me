> Recorded at eebded8, before adoption: paths cite the old `.memory/` layout.

# teach-me: adopt-project Steps 1-3 findings

Target: `~/code/teach-me` @ `eebded8` (fast-forwarded from local `40478a1`: the local clone was 13
commits behind `origin/main`; upstream landed 2026-10-21 and touched AGENTS.md, `.memory/adr/0019`,
`.memory/research/063-*`, skills/steering. The FF was clean, no local commits). Remote:
`https://github.com/smileynet/teach-me` (**public**: GitHub API returns 200 unauthenticated; GitHub
Pages deploys via `.github/workflows/pages.yml`). Untracked `.kiro/settings/` left alone (not under
`.memory/`).

## Step 1: survey and classification

- **Archetype:** 2 (mature bespoke) leaning 4. It has its own 152-line AGENTS.md (19,193 bytes), a
  44-line consumer-facing CLAUDE.md, a live tkt board (396 tickets, `.tickets/config.toml` with
  `close.require_resolution = true`), a crew-research `.memory/` (107 tracked files: CONTEXT.md,
  18 ADRs, 2 specs, 1 spec-like loose file, 1 loose note, 33 ink-reference docs, 51 research files),
  `.kiro/` (13 skills, 3 steering, 3 agents), `.agents/skills/` (9 symlinks into `.kiro/skills`),
  `.codex/review-marker.json` (review-new-work marker), `.githooks/pre-commit` (runs `mise run verify`).
- **Polarity:** incumbent present -> **subsume**. The tracker is already tkt, so nothing to migrate;
  `tkt init --write` only adds the AGENTS block.
- **Role split (the important call):** this repo is a **product users clone and open in an agent**
  (README.md:14-21 "Open in Kiro CLI, Claude Code, Codex..."; CLAUDE.md:3 "When a user opens this
  project, help them learn"). So the 13 `.kiro/skills`, 3 steering files, `.agents/skills`, CLAUDE.md
  and the learner-facing half of AGENTS.md (Workflow rows "New user arrives", "User names a topic")
  are **shipped artifacts** as well as agent layer. Reshape AGENTS.md conservatively; do not
  restructure skills.
- **Crew-research name collisions in `.kiro/skills` / `.agents/skills`: none** (checked all 13 names
  against `~/code/crew-research/atomics/skills/`). Two names collide with **grey-matter** skills:
  `teach`, `wait-what` (grey-matter `skills/productivity/`). These are this product's own
  (shipped) skills; kept (J5).
- **Not examined:** content of `library/` lessons (244 files), `test-scene/` (450), `ink-test-project/`
  (233), the 396 ticket bodies beyond greps, tools/ internals beyond greps.

## Conformance-audit Phase 1

### Safe-auto-fix

| id | Artifact | Finding | Rule |
|---|---|---|---|
| S1 | `.gitignore:5` | Plain `.references/` makes a README negation unreachable. Change to `.references/*` + `!.references/README.md`; keep `.scratch/` line as-is. | repo-hygiene.md § .references |
| S2 | `.references/README.md` (absent) | The canonical rehydration index is root `REFERENCES.md` (19 `git clone` lines, parsed by `tools/rehydrate.py` / `mise run rehydrate`). Five local dirs are NOT in it (H3). Write a README that points at REFERENCES.md, and marks non-public clones as owner-local without naming them (public repo). Do not add them to REFERENCES.md (see J1). | repo-hygiene.md § .references |
| S3 | `CONTRIBUTING.md:24` | Layout line `.memory/ — Persistent knowledge (glossary, ADRs)`; relocation leftover. Reword to the new homes (`GLOSSARY.md`, `docs/adr/`, `docs/agents/`). | relocation.md step 4 (convention mention reworded) |
| S4 | `.kiro/agents/godot_editor.json:23` | Resource `file://examples/godot-gamedev/reference/code/**/*.gdshader`; `examples/` was renamed `library/` (#183) and the glob matches nothing. `library/godot-gamedev/reference/code/*/*.gdshader` exists. Rewrite to `file://library/godot-gamedev/...`. | link/path resolution where installed |
| S5 | `tools/split-ink-docs.py:5,18,349` | Default `--output .memory/ink-reference/`. The relocate script rewrites repo-rooted mentions; verify after apply that it reads `docs/agents/ink-reference/`, else hand-fix. | relocation.md (config is not evidence) |

CLAUDE.md is present (not a pointer), so no pointer is added (J4).

### Needs judgment

| id | Finding | Evidence |
|---|---|---|
| J1 | **Non-public material in a public repo.** Research notes and shipped library pages carried non-public material (details redacted here; resolved by a later privacy scrub). Purge of history is out of adoption scope (history rewrite + force-push). | `curl api.github.com/repos/smileynet/teach-me` -> 200 |
| J2 | **87 tracked binaries, no LFS** (35 glb, 28 png, 15 jpg, 4 gltf, 3 bin, 1 woff2, 1 blend; largest ~1.2 MB `test-scene/assets/quaternius-characters/*.glb`). `.gitignore:23-26` deliberately commits `library/**/*.png` because Pages serves them; an LFS move needs `lfs: true` in the Pages checkout or the site serves pointer stubs. | `git ls-files` by ext; `git lfs ls-files` empty; `.gitattributes` has only `*.sh eol=lf` |
| J3 | **Ticket-close rule contradicts tkt.** AGENTS.md:89 says edit `status: done` by hand because "`tkt close` has a config validation bug". Observed: `tkt close 089 --check-all --resolution probe --dry-run` -> "Would close 089 ... Would commit and push" (tkt 0.3.1); upstream commits 749f524/eebded8 "chore(tickets): close 359/360" are `tkt close` output. The tkt block (and grey-matter rule) say reach done only via `tkt close`. AGENTS.proposed replaces the row with `tkt close` + the kept Resolution rule; confirm. | L1 dry-run + git log |
| J4 | **CLAUDE.md is a drifted consumer copy, not a pointer.** CLAUDE.md:14 `tools/init-workspace.sh` (ADR 0011 made init pure Python: `tools/init_workspace.py`, AGENTS.md:53); CLAUDE.md:11 "no populated workspace/MISSION.md" vs teach SKILL.md:19,28 (`.user/learner-profile.md`, MISSION.md legacy); "save to NOTES.md" (CLAUDE.md:15, AGENTS.md:83) vs teach SKILL.md:55,62 (prefs in learner-profile). `.agents/skills/` exposes 9 of 13 skills (missing asset-conversion, godot-validation, lesson-validation, serve-workspace) while CLAUDE.md:18 says skills are "in .agents/skills/". `.kiro/agents/default.json:6-8` loads `file://MISSION.md`, `NOTES.md` from the repo root (none exist there). | file:line as cited |
| J5 | **Skill distribution lineage.** AGENTS.md:3 and GLOSSARY "teach-me" say skills are "ported to crew-research for global deployment"; crew-research is retired, and grey-matter ships its own `teach`/`wait-what` (`grey-matter/skills/productivity/`). Same-named project skills shadow the global ones in sessions here (intended for a product). Decide the new port target and whether grey-matter's copies track these. AGENTS.md:137 points at global `skill-authoring` (crew-research; grey-matter equivalent: `writing-for-agents`); AGENTS.proposed swaps it. | file:line as cited |
| J6 | **Stale paths in steering/docs (no steering edits in adoption).** `.kiro/steering/visual-teaching.md:130` cites `.kiro/skills/writing-style` (does not exist); AGENTS.md:70 and `mise.toml:233` describe `map:global` as generating a forest map, but `tools/generate_global_map.py:2-6` only writes the redirect stub (#276); `assets/scaffolds/README.md:3` says the teach skill reads these "templates" while AGENTS.md:20 says boilerplate lives in `tools/lib/page_template.py`. | file:line as cited |
| J7 | Glossary verdicts below: 3 stale/contradicted entries. | table below |

Info (no ticket): ADR numbering skips 0006; `.codex/review-marker.json` is a review-new-work
marker (keep); `.githooks/pre-commit` runs the full `mise run verify` (adoption commit will run it).

## Glossary verdicts (`.memory/CONTEXT.md`, 23 terms)

| Term | Verdict | Evidence |
|---|---|---|
| teach-me | **stale** | "deploying globally via crew-research": crew-research retired (J5); AGENTS.md:3 |
| Teaching workspace | **contradicted** | "a per-topic directory holding mission, resources, lessons, learning records" vs AGENTS.md:25 (ONE live `workspace/` per machine, all topics) and teach SKILL.md:12-14 (shareable curriculum split from private `.user/` state; mission in `.user/learner-profile.md` :28; records in `.user/learning-records/`, LEARNING-RECORD-FORMAT.md:3) |
| teach | confirmed | teach SKILL.md:3; ADR 0019 narrows it to the conversational engine (AGENTS.md:31) |
| quiz-me | confirmed | quiz-me SKILL.md:10 ("not a grilling session") |
| wait-what | confirmed | wait-what SKILL.md description |
| Mission | confirmed | teach SKILL.md:28 ("Don't produce a lesson without a mission"); location moved to `.user/learner-profile.md`, definition is location-free |
| Learning record | confirmed | LEARNING-RECORD-FORMAT.md:3,15 |
| ZPD | confirmed | teach SKILL.md:20,68 |
| Storage strength | confirmed | teach SKILL.md:140 |
| Reference doc | confirmed | teach SKILL.md:142 |
| Socratic gate | confirmed | quiz-me SKILL.md:22; AGENTS.md:111 |
| Jargon skill | confirmed | jargon SKILL.md:46-59 (three gates) |
| Scaffold | **stale** | `assets/scaffolds/` exists (lesson/quiz/reference/quick-check.html) but AGENTS.md:15,20: boilerplate source of truth is `tools/lib/page_template.py`; scaffolds are "content-pattern examples" (J6) |
| Criteria-based answer | confirmed | generate-topic references/sr-question-authoring.md:30; quiz-me SKILL.md:115 |
| Progressive overload | confirmed | library/workout-fundamentals/MISSION.md, RESOURCES.md |
| Research-first | confirmed | ADR 0002:1-9 |
| Casual exploration posture | confirmed | ADR 0001:7 |
| Aggregate index | confirmed | library/index.html; ADR 0016:49 |
| Tree view / Map view | confirmed | library/global-map.html redirects to `index.html?view=map` |
| Global / forest map | confirmed | tools/generate_global_map.py:2-6 writes only the redirect stub (but AGENTS.md:70 is stale, J6) |
| Domain map | confirmed | library/*/lessons/*-map.html |
| Status overlay | confirmed | tools/lib/overlay.py:24,52 |
| Demo-status fixture | confirmed | library/{godot-gamedev,iceberg-workspace,ink-godot}/demo-status.json |

Contradictions recorded as characterized fact (not fixed): the workspace model moved to a
curriculum + private `.user/` overlay (ADR 0012) and a single per-machine `workspace/`, while the
glossary, CLAUDE.md and AGENTS.md:83 still describe root-level MISSION.md / NOTES.md.

## Migration-finding tickets

1. **Review migration finding: non-public material is published in the public repo and Pages site**
   J1. Scrub the current tree (research notes + shipped library pages) and decide whether to purge
   history (owner decision, force-push).
2. **Review migration finding: 87 binaries tracked without Git LFS**
   J2. Decide LFS for glb/png/jpg/blend/bin (current tree only); if adopted, set `lfs: true` in
   `.github/workflows/pages.yml` checkout and add the `git lfs install` gotcha. History migration is
   a separate owner decision.
3. **Review migration finding: AGENTS.md told agents to hand-edit tickets to done**
   J3. The adoption replaced AGENTS.md:89's hand-edit rule with `tkt close` (dry-run works on tkt
   0.3.1). Confirm the old "config validation bug" is gone; keep `close.require_resolution`.
4. **Review migration finding: CLAUDE.md and .agents/skills drifted from the shipped workflow**
   J4. CLAUDE.md cites `tools/init-workspace.sh`, root MISSION.md/NOTES.md; `.agents/skills` lacks 4
   skills; `default.json` loads root MISSION/NOTES/RESOURCES that don't exist. Decide: CLAUDE.md as a
   pointer vs a maintained consumer copy; symlink coverage; NOTES.md vs learner-profile.
5. **Review migration finding: skills still say they port to crew-research**
   J5. Decide the port target now that crew-research is retired, and how grey-matter's `teach` /
   `wait-what` relate to this repo's (shadowing in this repo is expected for the product).
6. **Review migration finding: stale paths in steering, mise task text, and scaffold docs**
   J6. `visual-teaching.md:130` writing-style path; `map:global` description (AGENTS.md:70,
   mise.toml:233) vs the redirect-stub script; `assets/scaffolds/README.md:3` vs page_template.py.
7. **Review migration finding: staged glossary terms and contradicted entries**
   J7 + glossary-staged.md. Confirm/correct/reject 5 staged terms; rewrite or confirm the stale
   entries teach-me, Teaching workspace, Scaffold (verdict table in findings.md).

## Baseline

Run at `eebded8`:
- `mise run verify` (17 steps incl. pytest 82, Playwright interactive 20 checks, ink replay 5/5,
  lesson code 10 compiled/26 skipped) -> **PASSED** (~25 s). Also the pre-commit hook.
- `.venv/bin/python -m pytest tests -q` -> **209 passed**.
- `relocate-knowledge.mjs check-links .` -> 610 md files, **22 broken** (7 in `.memory/ink-reference`
  (upstream doc names), 1 `.memory/research`, 2 ticket 028, 1 assets/workspace-template, 11 library
  reference READMEs pointing at `../../lessons/`).
- `tkt validate --brief` -> **pass (127 findings)** (accepted `missing-resolution` baseline, #285).

## Hygiene

- **H1 binaries without LFS:** 87 (J2).
- **H2 sensitive tracked content:** J1 (non-public research material, also in shipped library pages). No credentials-like files found. No tracked `.scratch/`.
- **H3 `.references/`** (gitignored as a plain dir; README absent). Root `REFERENCES.md` is the
  committed index (19 clone lines). Local dirs not in it:
  - five owner-local clones of non-public repos (not named: this repo is public)
  None of the 19 REFERENCES.md clones are currently present locally.
- **H4 project copies of crew-research skills:** none. grey-matter name overlaps: `teach`, `wait-what`
  (kept, shipped).
