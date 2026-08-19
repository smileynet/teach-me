# Toon Banding — Code Files

Final-state shader files from [Lesson 4: Toon Banding](../../lessons/0004-toon-banding.html).

| File | Description |
|------|-------------|
| `toon_test.gdshader` | Starting point — two-band hard cut using `step()` |
| `toon_smoothstep.gdshader` | Approach A — soft edge with controllable threshold and softness |
| `toon_bands.gdshader` | Approach B — N configurable evenly-spaced bands via the modulo trick |
| `toon_ramp.gdshader` | Approach C — artist-paintable 1D gradient texture as lighting curve |

All files use `max()` instead of `+=` for multi-light safety (see lesson exercise).
