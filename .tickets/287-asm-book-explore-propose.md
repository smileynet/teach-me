---
id: "287"
title: "Clone, explore, and propose a domain for pkivolowitz/asm_book (ARM64 assembly)"
status: open
blocked_by: []
priority: medium
tags: [content, source-ingest, research]
---

# Clone, explore, and propose a domain for pkivolowitz/asm_book (ARM64 assembly)

Explore `pkivolowitz/asm_book` as a candidate teaching domain and PROPOSE (don't build)
a domain shape. Exploration + proposal only — lesson generation is a separate follow-up
after sign-off.

**Sequencing:** do this AFTER the shader lesson track (#216 / #222 / #253 / #227) completes.

## Source

- Repo: https://github.com/pkivolowitz/asm_book (MIT-ish; check LICENSE.md — dual license
  file present). ~3.3k stars, actively maintained, 334 commits.
- "A Gentle Introduction to Assembly Language Programming" — teaches **ARM64 / AARCH64 /
  ARM V8** assembly by BRIDGING from C/C++ knowledge the reader already has. Author: Perry
  Kivolowitz (19 yrs CS teaching). Note: AI-assisted edits post-2026-04-19 (git history).
- Content is Markdown per chapter (each chapter = a `README.md` in a topic folder), with
  parallel PDFs and runnable `.S` assembly + `.c` driver examples. Clone-and-run toolchain:
  `gcc`/`g++` + `gdb` (Linux) or `clang` + `lldb` (macOS); a portability macro suite for
  Linux/macOS calling conventions.

## Structure (from README TOC — verify on clone)

- **Section 1 — Bridging C/C++ → asm** (~9 chapters, the pedagogical spine): kickstart,
  hello world, if, loops (while/for/continue/break), interludes (registers, load/store,
  ldr, register sizes, hex), switch, functions (calling/params/CRT calls), FizzBuzz,
  structs (alignment/defining/using/this), const. Folder: `section_1/`.
- **Section 2 — Floating point** (`section_2/float/`): what FP numbers are, registers,
  truncation/rounding, literals, fmov, half precision. (NEON SIMD = not-yet-written.)
- **Section 3 — Bit manipulation** (`section_3/`): bit fields (with/without/review),
  endianness.
- **Section 4 — "More stuff"** (`more/`): Apple Silicon, Apple/Linux convergence, variadic
  functions, system calls under the hood, strlen for C, calling asm from Python, atomics,
  jump tables, argv, spin-locks; plus a "Debugging" lecture (PPTX).
- **Projects** (`projects/`): FizzBuzz, first_project, DIRENT (structs), PI (FP), SINE (FP+
  functions), SNOW (particle animation), WALKIES (pointers/looping) — candidate hands-on
  challenges (#115 territory).

## What to do (explore + propose)

1. **Clone into `.references/`** (gitignored; add to REFERENCES.md for rehydrate). Confirm
   license permits deriving teaching material; record provenance.
2. **Explore**: read the section READMEs; confirm the TOC above against the actual tree;
   note which chapters are complete vs `not_written_yet.md` stubs (NEON, etc.).
3. **Assess fit** against teach-me's posture (interest-driven casual discovery; research-
   first; runnable-artifact-per-lesson, ADR 0010). Key questions to answer in the proposal:
   - Domain slug + title + one-line description; is it ONE domain or a parent with sub-maps
     (e.g. `arm64-assembly` parent → `float`, `bit-manipulation` sub-maps)?
   - Topic list + prereq edges derived from the section structure (the C→asm bridge is a
     natural prereq spine).
   - **Runnable-artifact tier**: assembly needs a real toolchain to validate. Propose the
     validation approach — a `.references/asm_book`-adjacent build harness (`gcc -c *.S`)?
     Does CI have aarch64 (cross-assemble with `aarch64-linux-gnu-as`)? This is the analogue
     of the shader/ink runtime gate and MUST be answered before any lesson ships.
   - Source-ingest path: chapters are Markdown — could feed `tools/ingest_source.py` for a
     MAP + concept hints, but the hand-authored TOC may beat auto-chunking. Propose which.
4. **Write the proposal** (an ADR or a `.scratch/` proposal doc, per the grill/planning
   norms) with the domain shape, topic/prereq map sketch, artifact-validation plan, and a
   go/no-go recommendation. Do NOT generate lessons.

## Acceptance criteria

- [ ] Repo cloned into `.references/` + REFERENCES.md rehydrate entry; license/provenance recorded
- [ ] Actual tree explored and TOC verified (complete vs not-yet-written chapters noted)
- [ ] Fit assessment against teach-me posture (casual/discovery, research-first, runnable artifact)
- [ ] Proposed domain shape: slug/title, single-vs-parent+sub-maps, topic list + prereq spine
- [ ] Artifact-validation plan for assembly (toolchain/CI approach — the runtime-gate analogue)
- [ ] Ingest-vs-hand-authored-map recommendation
- [ ] Written proposal (ADR or `.scratch/` doc) with a go/no-go recommendation; NO lessons generated

## Notes

- Exploration/proposal only; lesson generation is a separate ticket after sign-off.
- Assembly is a strong fit for the C→asm "bridge" pedagogy but the toolchain-validation
  question is the real gate (can't ship a lesson whose runnable artifact we can't compile).
