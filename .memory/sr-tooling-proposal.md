# Spaced Repetition Tooling Proposal

Based on research into 34 jobs-to-be-done across learner/teacher/system/lifecycle roles, CLI prior art (repeater, cert-pepper, Orbit), analytics best practices, and content lifecycle patterns.

## Design Principles

1. **The workspace IS the deck.** Cards live alongside lessons (JSONL), not in a separate app. The teach skill creates them; they're versioned with git.
2. **Explain-to-colleague, not flashcard recall.** Our question format tests understanding via articulation, not recognition.
3. **SM-2 now, FSRS migration path.** Review history stored from day one enables future optimization.
4. **Minimal viable analytics.** Three metrics that drive behavior, not 12 dashboards nobody reads.
5. **Lifecycle-aware.** Cards tied to lessons — update when lessons change, retire when mastered.

---

## Proposed Scripts (tools/)

### Existing (already built)

| Script | Purpose |
|--------|---------|
| `tools/sm2.py` | SM-2 scheduling algorithm (pure functions) |
| `tools/questions.py` | JSONL card storage, CRUD, due-card queries |
| `tools/review.py` | CLI: show due, record reviews, stats |

### New Scripts to Add

#### `tools/sr-status.py` — "git status for memory"

Quick health check, designed to run at session start or via mise task.

```
$ python tools/sr-status.py

📚 Spaced Repetition Status
  Topic: iceberg-on-aws
  Cards: 12 total (8 active, 2 mastered, 1 suspended, 1 new)
  Due today: 3 cards
  Overdue: 1 card (2 days late)
  Estimated knowledge: 78% (avg retrievability of active cards)
  Leeches: 1 card lapsed 4+ times → consider rewriting

  Next review in: now (3 cards waiting)
```

**JTBD covered:** L1 (know what's due), L5 (memory health), S6 (per-prompt stats), S7 (leech detection)

#### `tools/sr-check.py` — Scan for prompt quality issues

Validates the question bank against known-good patterns.

```
$ python tools/sr-check.py

Checking iceberg-on-aws.jsonl (12 cards)...
  ⚠ Card abc123: prompt starts with "What is" — prefer "Explain why" format
  ⚠ Card def456: expected_answer > 200 chars — may not be atomic
  ✓ Card ghi789: good (explain type, atomic, has provenance)
  ⚠ Card jkl012: lapsed 4 times — flagged as leech
  ✓ 9/12 cards pass quality checks
  
Suggestions:
  • Rewrite leech jkl012 or suspend it
  • Consider splitting def456 into two atomic cards
```

**JTBD covered:** T4 (leech detection), T7 (validate prompt quality), S7 (leech detection)

#### `tools/sr-lifecycle.py` — Content lifecycle operations

Bulk operations: suspend, retire, update provenance, handle lesson changes.

```
$ python tools/sr-lifecycle.py suspend --card-id abc123
$ python tools/sr-lifecycle.py retire --min-interval 180
$ python tools/sr-lifecycle.py sync-lessons   # flag cards whose source section changed
$ python tools/sr-lifecycle.py reset --card-id abc123   # re-enter learning
```

**JTBD covered:** L6 (skip/defer), L8 (graduate), S8 (lesson lifecycle hooks), bulk operations

#### `tools/sr-analytics.py` — Minimal viable analytics

Three metrics that actually drive behavior change:

```
$ python tools/sr-analytics.py

📊 Knowledge State (iceberg-on-aws)
  
  Estimated knowledge: 78% (retrievability-weighted)
  True retention: 85% (of reviews in last 14 days)
  
  🟢 Strong (R > 0.9): 5 concepts
  🟡 Decaying (R 0.7-0.9): 3 concepts — review soon
  🔴 Weak (R < 0.7): 2 concepts — priority review
  
  What's decaying:
    1. manifest-list layer separation (R=0.72, due yesterday)
    2. optimistic concurrency retry (R=0.68, due 2 days ago)
  
  Activity: 3 reviews this week (streak: 2 days)
  Load forecast: ~2 reviews/day for next 7 days
```

**JTBD covered:** L5 (memory health), S6 (per-prompt stats), I6 (coverage gaps)

---

## Proposed mise Tasks

```toml
[tasks.sr]
description = "Show SR status (what's due, health summary). Pass topic slug to filter."
run = "python tools/sr-status.py"

[tasks."sr:review"]
description = "Start a review session. Pass topic slug to narrow, or review all due."
run = "python tools/review.py"

[tasks."sr:stats"]
description = "Show analytics (knowledge state, retention, what's decaying)"
run = "python tools/sr-analytics.py"

[tasks."sr:check"]
description = "Validate question bank quality (leech detection, format issues)"
run = "python tools/sr-check.py"

[tasks."sr:lifecycle"]
description = "Card lifecycle operations (suspend, retire, sync-lessons)"
run = "python tools/sr-lifecycle.py"
```

**Usage pattern:**
- `mise run sr` — daily check at session start ("do I have reviews?")
- `mise run sr -- iceberg-on-aws` — status for one topic
- `mise run sr -- --list` — show all topics with due counts
- `mise run sr:review` — review all due cards (interleaved, recommended)
- `mise run sr:review -- iceberg-on-aws` — review one topic only
- `mise run sr:stats` — periodic health check
- `mise run sr:stats -- iceberg-on-aws` — analytics for one topic
- `mise run sr:check` — after writing a lesson (quality gate)
- `mise run sr:lifecycle sync-lessons` — after editing a lesson

---

## Proposed Skill Updates

### teach skill — additions

```markdown
## After Publishing a Lesson

After the lesson and reference doc are written:
1. Generate 3-5 SR questions (already in workflow ✓)
2. Run `mise run sr:check` to validate question quality
3. If any warnings, fix before committing
```

### quiz-me skill — additions

```markdown
## Review Mode Integration

When the learner asks for a review (or at session start if cards are due):
1. Run `python tools/review.py` to get due cards
2. Present each card as a conversational question
3. After the learner explains, rate quality (0-5) and record via review.py
4. If a card is leeching (4+ lapses), note in NOTES.md for the teach skill to address
```

### New skill: `sr-review` (or integrate into quiz-me)

Trigger: "review", "what's due", "spaced repetition", "practice"

```markdown
## Process

1. Check status: `python tools/sr-status.py`
2. If nothing due: "Nothing to review — your knowledge is holding! Next review due [date]."
3. If cards due: Present each as a conversation:
   - Show prompt
   - Wait for learner to explain
   - Assess quality (map their response to 0-5)
   - Record review
   - Give brief feedback + source link
4. After session: summarize what was strong/weak
5. If leeches detected: flag for the next teach session
```

---

## JTBD Coverage Map

| Job | Covered by | Status |
|-----|-----------|--------|
| L1: Know what's due | `sr-status.py`, `mise run sr` | **Proposed** |
| L2: Review in terminal | `review.py` + quiz-me skill | ✅ Built |
| L3: Review in context | Card provenance (lesson_id, section) | ✅ Built |
| L4: Honest difficulty signal | SM-2 quality 0-5 | ✅ Built |
| L5: Memory health dashboard | `sr-analytics.py` | **Proposed** |
| L6: Skip/defer | `sr-lifecycle.py suspend` | **Proposed** |
| L7: Trust the schedule | SM-2 (FSRS later) | ✅ Built |
| L8: Graduate items | mastered flag at >180d interval | ✅ Built |
| L9: Cross-lesson interleaving | `get_all_due_cards()` | ✅ Built |
| L10: Understanding-level prompts | explain-to-colleague format | ✅ Built |
| T1: Write prompts inline | teach skill generates per-lesson | ✅ Built |
| T2: Multiple prompt types | explain/compare/apply/predict | ✅ Built |
| T3: Stable identity | UUID per card | ✅ Built |
| T4: Detect leeches | `sr-check.py` | **Proposed** |
| T5: Progressive introduction | Cards created per-lesson, due immediately | ✅ Built |
| T6: Auto-suggest prompts | teach skill generates | ✅ Built |
| T7: Validate quality | `sr-check.py` | **Proposed** |
| T8: Link to objectives | tags + lesson_id provenance | ✅ Built |
| S1: Scan for prompts | questions.py reads JSONL | ✅ Built |
| S2: Plain file state | JSONL + reviews.jsonl | ✅ Built |
| S3: Modern algorithm | SM-2 now, FSRS later (history stored) | ✅ Built |
| S4: Handle delayed reviews | sorted by overdue | ✅ Built |
| S5: Stable identity | UUID (could add meaning-hash later) | ✅ Built |
| S6: Per-prompt stats | review history in reviews.jsonl | ✅ Built |
| S7: Leech detection | `sr-check.py` (4+ lapses) | **Proposed** |
| S8: Lesson lifecycle hooks | `sr-lifecycle.py sync-lessons` | **Proposed** |
| S9: CLI integration | review.py, mise tasks | **Proposed** |
| S10: Reminder at session start | `sr-status.py` in session start | **Proposed** |
| S11: Interleaved review | `get_all_due_cards()` mixes topics | ✅ Built |
| I1: Gate progression on retention | Future — gate in teach skill | **Future** |
| I2: Feed into learning records | Future — write LR after sustained mastery | **Future** |
| I3: Integrate with quiz-me | quiz-me appends gap cards | ✅ Built |
| I4: Cross-session persistence | JSONL files on disk, git versioned | ✅ Built |
| I5: Compose with mise | mise tasks proposed | **Proposed** |
| I6: Coverage gap reporting | `sr-analytics.py` | **Proposed** |

**Score: 20/34 built, 10/34 proposed here, 4/34 future work**

---

## Implementation Priority

| Priority | What | Why |
|----------|------|-----|
| 1 | `sr-status.py` + `mise run sr` | Cheapest high-value add — makes SR visible at session start |
| 2 | Topic filtering across all SR commands | Core UX: `--topic` narrows, no arg = all (research-backed) |
| 3 | `sr-check.py` + quality gate in teach skill | Prevents bad cards from entering rotation |
| 4 | `sr-analytics.py` retrievability estimate | "What do I actually know right now?" |
| 5 | `sr-lifecycle.py` suspend/retire/sync | Operational necessity once cards accumulate |
| 6 | FSRS migration | After 50+ reviews accumulated, optimize parameters |

---

## Topic/Category Filtering (research-backed design)

### Principle: Interleaved by default, focused on request

Research shows interleaved review (mixing topics) produces stronger long-term retention (d=0.83–1.05) than blocked review. Default to reviewing all due cards across all topics. Filtering is explicit opt-in.

### CLI syntax (follows repeater/pytest/cargo convention)

```bash
# Default: review all due cards (interleaved across topics)
mise run sr:review

# Narrow to one topic (positional = scope narrowing)
mise run sr:review -- iceberg-on-aws

# Status for one topic
mise run sr -- iceberg-on-aws

# Stats for one topic
mise run sr:stats -- iceberg-on-aws

# List available topics with card counts
mise run sr -- --list
```

### Implementation across all scripts

Every SR script accepts an optional positional topic slug:

```python
# In review.py, sr-status.py, sr-analytics.py, etc.
parser.add_argument("topic", nargs="?", default=None,
                    help="Topic slug to filter (default: all topics)")
parser.add_argument("--list", "-l", action="store_true",
                    help="List topics with due/total counts")
```

Behavior:
- **No argument** → operates on ALL topics (interleaved)
- **Topic slug** → filters to that topic only
- **`--list`** → shows available topics with counts, no review

### Filtered reviews DO affect scheduling

Following Anki's "reschedule" default: when you review a card via topic filter, it updates the card's SM-2 state and interval normally. This is the safe default — the alternative (Mochi's "cramming" mode where reviews don't count) is only needed for exam prep scenarios we don't have.

### Why not tags?

Our taxonomy is simple: one topic per teaching workspace (e.g., `iceberg-on-aws`). The topic slug IS the filename (`learning-records/questions/<slug>.jsonl`). Tags exist within cards for finer filtering later, but the primary axis is topic. This follows the filesystem-as-taxonomy pattern that CLI users already understand.

### Future: tag-based sub-filtering

If a learner wants to review only "query-planning" cards within iceberg-on-aws:

```bash
mise run sr:review -- iceberg-on-aws --tag query-planning
```

This is a later addition — topic filtering covers the primary JTBD.

---

## Future Work (not proposing now)

- **Progression gating** (I1): Block next lesson until prior material hits 90% retrievability. Needs more experience to calibrate.
- **Learning record integration** (I2): Auto-write a learning record when a concept sustains >3 month interval.
- **Meaning-hash identity** (repeater pattern): Hash prompt content instead of UUID, so editing a card's wording preserves schedule. Useful but adds complexity.
- **FSRS migration script**: Take reviews.jsonl, train FSRS parameters, swap scheduler. Wait for 50+ reviews minimum.
- **Activity heatmap**: GitHub-style SVG calendar showing review days. Nice but cosmetic.

---

## Sources

- [repeater](https://github.com/shaankhosla/repeater) — closest CLI prior art (Rust, FSRS, markdown-first)
- [cert-pepper](https://github.com/cert-pepper/cert-pepper) — FSRS + BKT + AI explanations
- [Anki Review Heatmap](https://github.com/glutanimate/review-heatmap) — analytics visualization
- [FSRS in 100 Lines](https://borretti.me/article/implementing-fsrs-in-100-lines) — migration target
- [Gwern: Spaced Repetition](https://gwern.net/spaced-repetition) — literature review
- [Orbit](https://github.com/andymatuschak/orbit) — embedded-in-prose model
- [Anki docs: Card States](https://docs.ankiweb.net/getting-started.html) — lifecycle reference
