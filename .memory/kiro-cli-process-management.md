# kiro-cli Process Management

Findings from spike 058 (2026-08-11). Critical for any code that spawns kiro-cli as a subprocess.

## Process Tree

```
kiro-cli              (shell wrapper — thin launcher)
  └── kiro-cli-chat   (actual worker binary)
        ├── MCP server: playwright
        └── MCP server: notion
```

## SIGTERM Behavior

| Kill target | Result |
|-------------|--------|
| `kiro-cli` (wrapper) | Wrapper dies. `kiro-cli-chat` + MCP servers reparent to PID 1. **Orphans.** |
| `kiro-cli-chat` (worker) | Worker + all MCP servers terminate cleanly. **Correct.** |
| Process group (`os.killpg`) | Everything dies cleanly. **Correct.** |

## Recommended Cancellation Pattern

```python
proc = subprocess.Popen(
    ['kiro-cli', 'chat', '--no-interactive', ...],
    start_new_session=True,  # creates new process group
)

# To cancel cleanly:
os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
```

Exit code on SIGTERM: **143** (128 + 15) or **-15** (Python's representation).

## Output Buffering

kiro-cli buffers output internally — lines arrive in bursts, not as they're generated.
`stdbuf -oL` and `PYTHONUNBUFFERED=1` do not help. Design for phase-level progress, not token streaming.

## ANSI Escape Codes

`NO_COLOR=1` does **not** suppress ANSI codes. Always strip with:

```python
import re
ANSI_RE = re.compile(r"\x1b\[\??[0-9;]*[a-zA-Z]")
def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)
```
