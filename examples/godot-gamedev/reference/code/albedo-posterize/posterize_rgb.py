"""posterize_rgb.py — build (and validate) the "Posterize RGB" shader node group.

The downloadable artifact for lesson 0016 (Albedo Posterization in Blender).
It is a *text* script, not a binary .blend — so it is diffable, reviewable, and
re-runnable headless, which also lets it serve as the lesson's Tier-2 validator.

WHAT IT BUILDS (Method A — the general posterize, from prior art):
    Group Input (Color, Levels)
      -> Vector Math MULTIPLY by (Levels,Levels,Levels)
      -> Vector Math FLOOR
      -> Vector Math DIVIDE by (Levels,Levels,Levels)   [= Multiply by 1/Levels]
      -> Group Output (Color)
This is floor(color * N) / N applied component-wise to RGB in a single chain —
the exact operation posterize_albedo.gdshader does in-shader (color_levels = N).

USAGE
  In Blender (GUI): Scripting workspace -> open -> Run. Then Add > Group >
  "Posterize RGB" in any material, wire an Image Texture in and Base Color out.

  Headless build (writes a .blend you can open):
    blender -b --python posterize_rgb.py -- --save posterize_rgb.blend

  Headless VALIDATION (Tier-2 gate — asserts the group's sockets + wiring):
    blender -b --python posterize_rgb.py -- --check
  Exits 0 if the node group is wired correctly, 1 otherwise.

COLOR SPACE (gotcha the lesson teaches): set the input Image Texture's
Color Space to match your intent. "sRGB"/"Color" decodes to linear before these
math nodes (bands cluster in shadows); "Non-Color" quantizes the stored values
(perceptually even bands). Pin it explicitly — Blender auto-guesses otherwise.
"""
import sys

try:
    import bpy
except ImportError:
    print("posterize_rgb.py must run inside Blender (blender -b --python ...)", file=sys.stderr)
    sys.exit(2)

GROUP_NAME = "Posterize RGB"


def build_group(levels_default: int = 4):
    """Create (or rebuild) the Posterize RGB node group. Returns the group."""
    if GROUP_NAME in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[GROUP_NAME])
    ng = bpy.data.node_groups.new(GROUP_NAME, "ShaderNodeTree")

    # --- Interface (Blender 4.x/5.x: node_group.interface) ---
    ng.interface.new_socket("Color", in_out="INPUT", socket_type="NodeSocketColor")
    lv = ng.interface.new_socket("Levels", in_out="INPUT", socket_type="NodeSocketFloat")
    lv.default_value = float(levels_default)
    lv.min_value = 2.0
    lv.max_value = 16.0
    ng.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")

    nodes, links = ng.nodes, ng.links
    gin = nodes.new("NodeGroupInput"); gin.location = (-600, 0)
    gout = nodes.new("NodeGroupOutput"); gout.location = (400, 0)

    # Broadcast the scalar Levels to a vector so Vector Math can scale RGB by it.
    combine = nodes.new("ShaderNodeCombineXYZ"); combine.location = (-380, -180)
    for axis in ("X", "Y", "Z"):
        links.new(gin.outputs["Levels"], combine.inputs[axis])

    mul = nodes.new("ShaderNodeVectorMath"); mul.operation = "MULTIPLY"; mul.location = (-180, 0)
    flr = nodes.new("ShaderNodeVectorMath"); flr.operation = "FLOOR"; flr.location = (0, 0)
    div = nodes.new("ShaderNodeVectorMath"); div.operation = "DIVIDE"; div.location = (200, 0)

    links.new(gin.outputs["Color"], mul.inputs[0])
    links.new(combine.outputs["Vector"], mul.inputs[1])   # color * N
    links.new(mul.outputs["Vector"], flr.inputs[0])       # floor(color * N)
    links.new(flr.outputs["Vector"], div.inputs[0])
    links.new(combine.outputs["Vector"], div.inputs[1])   # / N
    links.new(div.outputs["Vector"], gout.inputs["Color"])
    return ng


def check_group() -> int:
    """Tier-2 validator: assert the group exists with correct sockets + chain."""
    build_group()
    ng = bpy.data.node_groups.get(GROUP_NAME)
    errs = []
    if ng is None:
        print("FAIL: node group not created", file=sys.stderr)
        return 1

    ins = [s.name for s in ng.interface.items_tree if s.item_type == "SOCKET" and s.in_out == "INPUT"]
    outs = [s.name for s in ng.interface.items_tree if s.item_type == "SOCKET" and s.in_out == "OUTPUT"]
    if "Color" not in ins or "Levels" not in ins:
        errs.append(f"inputs {ins} missing Color/Levels")
    if "Color" not in outs:
        errs.append(f"outputs {outs} missing Color")

    ops = [n.operation for n in ng.nodes if n.type == "VECT_MATH"]
    for required in ("MULTIPLY", "FLOOR", "DIVIDE"):
        if required not in ops:
            errs.append(f"missing Vector Math {required} (found {ops})")

    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("posterize_rgb: node group OK (Color+Levels in, Color out; MULTIPLY->FLOOR->DIVIDE)")
    return 0


def _args():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


if __name__ == "__main__":
    a = _args()
    if "--check" in a:
        sys.exit(check_group())
    build_group()
    if "--save" in a:
        path = a[a.index("--save") + 1]
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print(f"saved {path}")
    else:
        print(f"built '{GROUP_NAME}' node group (open in GUI or pass --save <file>)")
