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

## Additional references (comparanda — explore alongside asm_book)

Three more repos to clone + weigh when shaping the domain. They span the design space
(beginner intro / ARM64-on-Apple / x86 systems) so the proposal can decide scope + which
audience asm_book best serves. Explore for pedagogy + code style; asm_book stays the spine.

- **hackclub/some-assembly-required** (https://github.com/hackclub/some-assembly-required) —
  MIT, 3.6k stars. An *approachable ~30-min intro* to assembly (x86-leaning): Markdown
  `guide/` + `code/` examples, even a Spanish translation. VALUE: the gentlest on-ramp —
  contrast its "spark curiosity in 30 min" framing against asm_book's deeper C→asm bridge.
  Good model for a lightweight FIRST lesson / orientation. Consider as the "what is assembly
  and why care" hook that precedes asm_book's mechanics.
- **below/HelloSilicon** (https://github.com/below/HelloSilicon) — 5k stars, 16 chapters.
  ARM64 on **Apple Silicon**: codes along with the Apress book "Programming with 64-Bit ARM
  Assembly Language," adapting every Linux sample to Darwin (clang/`as` syntax vs GNU `as`,
  `lldb` vs `gdb`, Mach-O vs ELF, `ADRP/@PAGE` addressing, Darwin syscall numbers on X16/0x80
  vs Linux X8/svc, variadic-on-stack ABI divergence). VALUE: the DEFINITIVE Linux↔Darwin
  ARM64 delta reference — directly reinforces asm_book's own Apple-Silicon chapter + macro
  suite. Use to make any ARM64 lesson genuinely cross-platform (the toolchain-validation
  question spans both `as/ld` and `clang/ld -lSystem`).
- **cirosantilli/x86-bare-metal-examples** (https://github.com/cirosantilli/x86-bare-metal-examples) —
  GPL-v3 (code) / **CC BY-SA v4 (learning material — attribution required if we quote)**,
  5.4k stars. Dozens of *minimal bare-metal OSes* teaching **x86 SYSTEM programming**: BIOS
  interrupts, real/protected/long modes, GDT/IDT, paging, PIC/PIT, segmentation — "one
  minimal concept per OS," QEMU-run. VALUE: a DIFFERENT scope from asm_book (x86 ring-0
  bare-metal vs ARM64 userland-via-CRT). Decide in the proposal: is this a SEPARATE domain
  (`x86-bare-metal` / systems programming) rather than part of the ARM64 track? Its QEMU
  "boot an image" validation model is also a concrete answer to the toolchain-gate question
  for a systems-flavored track. **License note:** CC BY-SA is share-alike — quoting its prose
  needs attribution; prefer teaching the concept + citing over copying.

**Cross-repo decision for the proposal:** these span 3 axes — beginner-intro (hackclub) vs
deep-bridge (asm_book) vs Apple-platform (HelloSilicon) vs x86-systems (cirosantilli). The
proposal should decide whether teach-me wants ONE ARM64-userland domain (asm_book spine +
hackclub hook + HelloSilicon cross-platform), and whether x86-bare-metal is a distinct
future domain rather than in-scope here. Assembly ISA + platform + ring are the axes.

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

- [ ] All 4 repos cloned into `.references/` + REFERENCES.md rehydrate entries; license/provenance recorded (note asm_book dual-license + cirosantilli CC BY-SA attribution requirement)
- [ ] asm_book tree explored and TOC verified (complete vs not-yet-written chapters noted); the 3 comparanda skimmed for pedagogy + scope
- [ ] Fit assessment against teach-me posture (casual/discovery, research-first, runnable artifact)
- [ ] Scope decision: ONE ARM64-userland domain (asm_book spine + hackclub hook + HelloSilicon cross-platform) vs. x86-bare-metal as a distinct future domain
- [ ] Proposed domain shape: slug/title, single-vs-parent+sub-maps, topic list + prereq spine
- [ ] Artifact-validation plan for assembly (toolchain/CI approach — the runtime-gate analogue; consider cirosantilli's QEMU-boot model for any systems track)
- [ ] Ingest-vs-hand-authored-map recommendation
- [ ] Written proposal (ADR or `.scratch/` doc) with a go/no-go recommendation; NO lessons generated

## Notes

- Exploration/proposal only; lesson generation is a separate ticket after sign-off.
- Assembly is a strong fit for the C→asm "bridge" pedagogy but the toolchain-validation
  question is the real gate (can't ship a lesson whose runnable artifact we can't compile).
- 4 reference repos span the design space: hackclub (beginner intro), asm_book (ARM64 C→asm
  bridge — the spine), HelloSilicon (ARM64 Apple Silicon / Darwin deltas), cirosantilli (x86
  bare-metal systems). Licenses differ — asm_book dual, HelloSilicon check, cirosantilli
  GPL-v3 code + CC-BY-SA-v4 learning material (attribution on quote).
