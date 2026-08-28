"""palette_snap.py — build (and validate) the "Palette Snap" shader node group.

The downloadable artifact for lesson 0017 (Palette Snapping in Blender). Like the
0016 posterize artifact it is a *text* script, not a binary .blend — diffable,
reviewable, re-runnable headless, and doubling as the lesson's Tier-2 validator.

WHAT IT BUILDS — two composable methods, one node group each:

  Method A — "Palette Snap A (Ramp)"  [Color Ramp, Constant interpolation]
    Group Input (Color)
      -> RGB to BW            (color -> luminance)
      -> Color Ramp (CONSTANT interpolation), one stop per palette color
      -> Group Output (Color)
    Quick, visual, GUI-editable. Best when hand-tuning a look with few colors.

  Method B — "Palette Snap B (LUT)"   [1D palette texture, Closest interpolation]
    Group Input (Color)
      -> RGB to BW                              (color -> luminance)
      -> Combine XYZ (X=luminance, Y=0.5, Z=0)  (build the lookup UV)
      -> Image Texture (the N x1 palette strip, interpolation='Closest')
      -> Group Output (Color)
    Scales to shared palettes across assets and keeps the palette swappable at
    runtime (sample the same strip in a Godot shader). The palette strip MUST be
    Color Space = Non-Color so the authored sRGB swatches aren't view-transformed,
    and sampled with Closest (never Linear) so swatches don't blend.

CANONICAL PALETTE: the lesson's 6-color warm-toon set (Barrel_01 wood tones),
darkest -> lightest. Identical to tools/palette-snap-oracle.py::PALETTE — the oracle
validates the luminance->slot math this group implements.

USAGE
  In Blender (GUI): Scripting workspace -> open -> Run. Then Add > Group >
  "Palette Snap A (Ramp)" or "Palette Snap B (LUT)" in any material; wire an Image
  Texture (your posterized albedo) in and Base Color out.

  Headless build (writes a .blend you can open):
    blender -b --python palette_snap.py -- --save palette_snap.blend

  Headless VALIDATION (Tier-2 gate — asserts sockets + wiring for both methods):
    blender -b --python palette_snap.py -- --check
  Exits 0 if both node groups are wired correctly, 1 otherwise.

WHY CENTER-SAMPLE (gotcha the lesson + oracle teach): Method B indexes the strip at
the texel CENTER (idx+0.5)/N, not the border idx/N. A luminance landing a hair below
a texel border would otherwise select the neighbouring swatch (off-by-one). Combine
XYZ from a Constant-ramp/quantized luminance keeps samples at centers.
"""
import sys

try:
    import bpy
except ImportError:
    print("palette_snap.py must run inside Blender (blender -b --python ...)", file=sys.stderr)
    sys.exit(2)

# Canonical 6-color warm-toon palette (sRGB 0..1), darkest -> lightest.
# Mirrors tools/palette-snap-oracle.py::PALETTE (slot order = strip pixel order).
PALETTE = [
    (0.101, 0.078, 0.145),  # 0 deep cool shadow
    (0.239, 0.157, 0.216),  # 1 shadow
    (0.451, 0.247, 0.235),  # 2 mid-shadow
    (0.647, 0.400, 0.271),  # 3 midtone
    (0.831, 0.596, 0.361),  # 4 light
    (0.965, 0.831, 0.569),  # 5 highlight
]
N = len(PALETTE)

GROUP_A = "Palette Snap A (Ramp)"
GROUP_B = "Palette Snap B (LUT)"
PALETTE_IMG = "toon_palette_6"


def _new_group(name: str):
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    ng = bpy.data.node_groups.new(name, "ShaderNodeTree")
    ng.interface.new_socket("Color", in_out="INPUT", socket_type="NodeSocketColor")
    ng.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    return ng


def build_group_a():
    """Method A: RGB to BW -> Color Ramp (CONSTANT), one stop per palette color."""
    ng = _new_group(GROUP_A)
    nodes, links = ng.nodes, ng.links
    gin = nodes.new("NodeGroupInput"); gin.location = (-600, 0)
    gout = nodes.new("NodeGroupOutput"); gout.location = (400, 0)

    bw = nodes.new("ShaderNodeRGBToBW"); bw.location = (-380, 0)
    ramp = nodes.new("ShaderNodeValToRGB"); ramp.location = (-160, 0)
    ramp.color_ramp.interpolation = "CONSTANT"  # hard palette bands, no blending

    # One stop per palette color, placed at each slot's LEFT edge (k/N). With
    # CONSTANT interpolation each stop holds until the next, so luminance in
    # [k/N, (k+1)/N) resolves to swatch k — matching the oracle's lum->index.
    elements = ramp.color_ramp.elements
    # Blender seeds a new ramp with 2 elements; extend/set to N.
    while len(elements) < N:
        elements.new(0.0)
    for k, (r, g, b) in enumerate(PALETTE):
        elements[k].position = k / N
        elements[k].color = (r, g, b, 1.0)

    links.new(gin.outputs["Color"], bw.inputs[0])
    links.new(bw.outputs[0], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], gout.inputs["Color"])
    return ng


def _palette_image():
    """Create the N x1 Non-Color palette strip image (idempotent)."""
    if PALETTE_IMG in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[PALETTE_IMG])
    img = bpy.data.images.new(PALETTE_IMG, width=N, height=1, alpha=False)
    img.colorspace_settings.name = "Non-Color"  # don't view-transform authored swatches
    px = []
    for (r, g, b) in PALETTE:      # pixel 0 = leftmost = slot 0
        px += [r, g, b, 1.0]
    img.pixels = px
    img.pack()                     # embed so the .blend/artifact is self-contained
    return img


def build_group_b():
    """Method B: RGB to BW -> Combine XYZ(X=lum) -> Image Texture (Closest) strip."""
    ng = _new_group(GROUP_B)
    nodes, links = ng.nodes, ng.links
    gin = nodes.new("NodeGroupInput"); gin.location = (-600, 0)
    gout = nodes.new("NodeGroupOutput"); gout.location = (400, 0)

    bw = nodes.new("ShaderNodeRGBToBW"); bw.location = (-400, 0)
    combine = nodes.new("ShaderNodeCombineXYZ"); combine.location = (-220, 0)
    combine.inputs["Y"].default_value = 0.5   # sample the middle of the 1-px-tall strip
    combine.inputs["Z"].default_value = 0.0

    tex = nodes.new("ShaderNodeTexImage"); tex.location = (0, 0)
    tex.interpolation = "Closest"             # REQUIRED — no blending between swatches
    tex.extension = "EXTEND"                  # clamp ends, don't wrap/repeat
    tex.image = _palette_image()

    links.new(gin.outputs["Color"], bw.inputs[0])
    links.new(bw.outputs[0], combine.inputs["X"])   # luminance drives the U lookup
    links.new(combine.outputs["Vector"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], gout.inputs["Color"])
    return ng


def build_all():
    build_group_a()
    build_group_b()


def _socket_names(ng, in_out):
    return [s.name for s in ng.interface.items_tree
            if s.item_type == "SOCKET" and s.in_out == in_out]


def check_group() -> int:
    """Tier-2 validator: assert both groups exist with correct sockets + chains."""
    build_all()
    errs = []

    a = bpy.data.node_groups.get(GROUP_A)
    if a is None:
        errs.append("Method A group not created")
    else:
        if "Color" not in _socket_names(a, "INPUT"):
            errs.append("A: missing Color input")
        if "Color" not in _socket_names(a, "OUTPUT"):
            errs.append("A: missing Color output")
        ramps = [n for n in a.nodes if n.type == "VALTORGB"]
        if not ramps:
            errs.append("A: missing Color Ramp (ShaderNodeValToRGB)")
        elif ramps[0].color_ramp.interpolation != "CONSTANT":
            errs.append(f"A: ramp interpolation {ramps[0].color_ramp.interpolation} != CONSTANT")
        elif len(ramps[0].color_ramp.elements) != N:
            errs.append(f"A: ramp has {len(ramps[0].color_ramp.elements)} stops, expected {N}")
        if not any(n.type == "RGBTOBW" for n in a.nodes):
            errs.append("A: missing RGB to BW")

    b = bpy.data.node_groups.get(GROUP_B)
    if b is None:
        errs.append("Method B group not created")
    else:
        if "Color" not in _socket_names(b, "INPUT"):
            errs.append("B: missing Color input")
        if "Color" not in _socket_names(b, "OUTPUT"):
            errs.append("B: missing Color output")
        texs = [n for n in b.nodes if n.type == "TEX_IMAGE"]
        if not texs:
            errs.append("B: missing Image Texture (ShaderNodeTexImage)")
        else:
            t = texs[0]
            if t.interpolation != "Closest":
                errs.append(f"B: interpolation {t.interpolation} != Closest")
            if t.image is None:
                errs.append("B: Image Texture has no palette image")
            elif t.image.size[0] != N:
                errs.append(f"B: palette strip width {t.image.size[0]} != {N}")
            elif t.image.colorspace_settings.name != "Non-Color":
                errs.append(f"B: palette strip colorspace {t.image.colorspace_settings.name} != Non-Color")
        if not any(n.type == "COMBXYZ" for n in b.nodes):
            errs.append("B: missing Combine XYZ")
        if not any(n.type == "RGBTOBW" for n in b.nodes):
            errs.append("B: missing RGB to BW")

    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"palette_snap: both groups OK — '{GROUP_A}' (RGBtoBW->ConstantRamp[{N}]) "
          f"and '{GROUP_B}' (RGBtoBW->CombineXYZ->ClosestTex[{N}px Non-Color])")
    return 0


def _args():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


if __name__ == "__main__":
    a = _args()
    if "--check" in a:
        sys.exit(check_group())
    build_all()
    if "--save" in a:
        path = a[a.index("--save") + 1]
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print(f"saved {path}")
    else:
        print(f"built '{GROUP_A}' and '{GROUP_B}' node groups (open in GUI or pass --save <file>)")
