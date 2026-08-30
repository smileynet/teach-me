# Flow & Knots — Code Files

Reference story from [Lesson 1: Flow & Knots](../../lessons/0001-ink-flow-and-knots.html).

| File | Description |
|------|-------------|
| `01_flow_and_knots.ink` | Complete reference story: 4 knots, 2 choices, converging paths |

## Concepts demonstrated

- **Knots** (`=== name ===`) — named sections as story structure
- **Diverts** (`-> name`) — sending flow between knots
- **Loose ends** — every path must end with a divert or `-> END`; knots never fall through to the next knot
- **Basic choices** (`* [text] -> knot`) — branching that leads to different knots
- **Convergence** — multiple paths arriving at the same destination knot
- **Comments** (`//`, `/* */`) — annotations ignored by the runtime
- **`-> END`** — terminating the story

## How to test

Open in Inky (inklestudios.com/ink) or compile with inklecate:

```bash
inklecate -o 01_flow_and_knots.ink.json 01_flow_and_knots.ink
```

Play both paths in Inky's preview to verify convergence at the meeting knot.
