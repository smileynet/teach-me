# test-scene — Godot Shader Validation Project

Minimal Godot 4.7 project for validating lesson shaders. Open in the Godot editor to:
1. Confirm all shaders compile without errors
2. Apply shaders to test meshes and visually confirm they work
3. Use the MCP addon (godot_ai) for fine-grained programmatic control from AI agents

## Usage

### Manual validation (open in editor)

```bash
# Open in Godot editor
godot --path test-scene --editor
```

Apply shaders from `shaders/` to the meshes in `scenes/shader_test.tscn`. Verify:
- Textures appear on correct faces
- Lighting responds correctly (toon bands visible)
- Outlines render as expected (apply as next_pass)
- No invisible geometry

### Headless validation (CI/automated)

```bash
# Import-only validation (catches compilation errors)
godot --headless --editor --import --quit --path test-scene
```

### MCP control (from AI agent)

The godot_ai addon enables MCP communication when the editor is running.
Agents can:
- Create/modify materials programmatically
- Assign shaders to meshes
- Take screenshots for visual verification
- Read shader compilation errors from the editor log

## Shaders

All shaders in `shaders/` are copied from `examples/godot-gamedev/reference/code/`.
They should match 1:1 — the source of truth is the lesson reference code.

## Updating

When lesson shaders change, copy them here:
```powershell
Copy-Item examples\godot-gamedev\reference\code\*\*.gdshader test-scene\shaders\
```
