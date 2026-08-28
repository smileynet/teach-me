"""control_maps.py — bake the toon control maps mk_toon_lite.gdshader samples.

Downloadable artifact for lesson 0018 (Authoring Toon Control Maps — Noise & Threshold).
A *text* bpy script (not a binary .blend): diffable, re-runnable headless, and doubles as
the lesson's Tier-2 validator. It builds the TWO maps mk_toon_lite actually samples in
its light() function (the 1D lighting ramp is a DIFFERENT shader, toon_ramp.gdshader —
its own lesson, #246):

  noise_map      — a tileable 256x256 Non-Color noise texture. mk_toon_lite reads its
                   red channel, recenters to [-0.5,0.5], scales by `noise_strength`
                   (default 0.04, range 0.0-0.25), and adds it to NdotL before floor()
                   banding: breaks up otherwise straight band edges.
                       noise_bias = (texture(noise_map, UV*noise_scale).r - 0.5) * noise_strength
  threshold_map  — derived from the Barrel_01 ARM texture's RED channel (= AO). Read
                   Non-Color; mk_toon_lite reads .r, recenters to [-0.5,0.5] (FIXED
                   magnitude, no strength uniform), and adds it to the same banding input:
                       threshold_bias = texture(threshold_map, UV*threshold_map_scale).r - 0.5
                   Darker AO -> negative bias -> shadow boundary reached earlier (deeper
                   shade in creases). "Free" spatial shadow variation from baked geometry.

TILEABLE NOISE (the 4D-noise trick): a flat 2D noise sampled by UV seams at the tile
edges. Mapping the two UV axes onto two orthogonal CIRCLES in 4D noise input makes u=0
and u=1 (and v=0/v=1) map to the SAME 4D point, so opposite edges match by construction.
Blender's Noise Texture in 4D mode exposes the W input; we drive (X,Y,Z,W) from
sin/cos(2*pi*u) and sin/cos(2*pi*v).

USAGE
  Build + save a .blend:      blender -b --python control_maps.py -- --save control_maps.blend
  Bake the PNGs + sidecar:    blender -b --python control_maps.py -- --bake OUTDIR
  Tier-2 validate wiring:     blender -b --python control_maps.py -- --check
      Exits 0 if the noise node group + threshold setup are wired correctly, 1 otherwise.

The --bake pass measures each map from img.pixels (inside Blender, where pixels are free)
and writes control-maps-sidecar.json next to the PNGs — the Tier-1 stdlib oracle
(tools/control-maps-oracle.py) asserts contracts against that sidecar, and the Pillow
drift-check (tools/control-maps-drift.py) re-measures the committed PNGs against it.
"""
import sys
import json
import math
from pathlib import Path

try:
    import bpy
except ImportError:
    print("control_maps.py must run inside Blender (blender -b --python ...)", file=sys.stderr)
    sys.exit(2)

NOISE_GROUP = "Tileable Noise 4D"
NOISE_RES = 256
ARM_REL = "test-scene/assets/polyhaven/Barrel_01/textures/Barrel_01_explosive_arm_1k.jpg"
SIDECAR = "control-maps-sidecar.json"


# ─────────────────────────────────────────────────────────────────────────────
# Node group: tileable 4D noise
# ─────────────────────────────────────────────────────────────────────────────
def build_noise_group():
    """Build the 'Tileable Noise 4D' group: Tex Coord UV -> 4D circle map -> Noise 4D.

    UV (u,v) -> (sin2piu, cos2piu, sin2piv, cos2piv) into a 4D Noise Texture. Because
    sin/cos are 2*pi periodic, the u=0 and u=1 samples coincide -> seamless in U (and V).
    """
    if NOISE_GROUP in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[NOISE_GROUP])
    ng = bpy.data.node_groups.new(NOISE_GROUP, "ShaderNodeTree")
    ng.interface.new_socket("Fac", in_out="OUTPUT", socket_type="NodeSocketFloat")

    nodes, links = ng.nodes, ng.links
    gout = nodes.new("NodeGroupOutput"); gout.location = (600, 0)

    texco = nodes.new("ShaderNodeTexCoord"); texco.location = (-800, 0)
    sep = nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-600, 0)
    links.new(texco.outputs["UV"], sep.inputs["Vector"])

    def circle(axis_out, tau_node_x):
        """Return (sin, cos) nodes for 2*pi*axis."""
        mul = nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = 2.0 * math.pi
        mul.location = (-420, tau_node_x)
        links.new(axis_out, mul.inputs[0])
        s = nodes.new("ShaderNodeMath"); s.operation = "SINE"; s.location = (-240, tau_node_x + 40)
        c = nodes.new("ShaderNodeMath"); c.operation = "COSINE"; c.location = (-240, tau_node_x - 40)
        links.new(mul.outputs[0], s.inputs[0])
        links.new(mul.outputs[0], c.inputs[0])
        return s, c

    su, cu = circle(sep.outputs["X"], 200)
    sv, cv = circle(sep.outputs["Y"], -200)

    combine = nodes.new("ShaderNodeCombineXYZ"); combine.location = (-40, 120)
    links.new(su.outputs[0], combine.inputs["X"])
    links.new(cu.outputs[0], combine.inputs["Y"])
    links.new(sv.outputs[0], combine.inputs["Z"])

    noise = nodes.new("ShaderNodeTexNoise"); noise.location = (200, 0)
    noise.noise_dimensions = "4D"
    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 2.0
    links.new(combine.outputs["Vector"], noise.inputs["Vector"])
    links.new(cv.outputs[0], noise.inputs["W"])   # 4th axis = cos(2*pi*v)
    links.new(noise.outputs["Fac"], gout.inputs["Fac"])
    return ng


def _emit_material(fac_socket_owner_group=None, image_node=None):
    """A material that emits `fac`/image color, for Emit baking."""
    mat = bpy.data.materials.new("CtrlMapBake")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    if fac_socket_owner_group:
        g = nt.nodes.new("ShaderNodeGroup"); g.node_tree = fac_socket_owner_group
        nt.links.new(g.outputs["Fac"], emit.inputs["Color"])
    elif image_node:
        nt.links.new(image_node.outputs["Color"], emit.inputs["Color"])
    return mat, nt


def _bake_plane(mat, out_img):
    bpy.ops.mesh.primitive_plane_add(size=2)
    plane = bpy.context.active_object
    plane.data.materials.clear()
    plane.data.materials.append(mat)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode="OBJECT")
    bt = mat.node_tree.nodes.new("ShaderNodeTexImage"); bt.image = out_img
    bt.select = True
    mat.node_tree.nodes.active = bt
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 4
    bpy.ops.object.bake(type="EMIT")
    bpy.data.objects.remove(plane, do_unlink=True)


def _measure(img):
    """Measure sidecar properties from img.pixels (RGBA flat, row-major)."""
    w, h = img.size
    px = list(img.pixels)
    reds = px[0::4]
    rmin, rmax = min(reds), max(reds)

    def at(x, y, c):
        return px[(y * w + x) * 4 + c]

    # Edge match (tileability): compare opposite edges on the red channel.
    left_right = max(abs(at(0, y, 0) - at(w - 1, y, 0)) for y in range(h))
    top_bottom = max(abs(at(x, 0, 0) - at(x, h - 1, 0)) for x in range(w))
    edge_max_diff = max(left_right, top_bottom)

    return {
        "w": w, "h": h,
        "colorspace": img.colorspace_settings.name,
        "r_min": round(rmin, 5), "r_max": round(rmax, 5),
        "edge_max_diff": round(edge_max_diff, 5),
    }


def bake_all(outdir: str):
    out = Path(outdir).resolve(); out.mkdir(parents=True, exist_ok=True)
    sidecar = {"schema": 1, "generated_by": "control_maps.py", "maps": {}}

    # ---- noise map ----
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ng = build_noise_group()
    noise_img = bpy.data.images.new("toon_noise", width=NOISE_RES, height=NOISE_RES, alpha=False)
    noise_img.colorspace_settings.name = "Non-Color"
    mat, _ = _emit_material(fac_socket_owner_group=ng)
    _bake_plane(mat, noise_img)
    noise_img.filepath_raw = str(out / "toon_noise.png"); noise_img.file_format = "PNG"; noise_img.save()
    sidecar["maps"]["noise"] = {**_measure(noise_img), "role": "noise", "tileable_expected": True}

    # ---- threshold map (from ARM red = AO) ----
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm_path = Path(ARM_REL).resolve()
    arm = bpy.data.images.load(str(arm_path))
    arm.colorspace_settings.name = "Non-Color"
    aw, ah = arm.size
    thr_img = bpy.data.images.new("toon_threshold", width=aw, height=ah, alpha=False)
    thr_img.colorspace_settings.name = "Non-Color"
    tex = None
    mat = bpy.data.materials.new("ThrBake"); mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = arm; tex.interpolation = "Closest"
    # broadcast the ARM red channel to RGB (threshold map is a grayscale-from-AO map)
    sepc = nt.nodes.new("ShaderNodeSeparateColor")
    comb = nt.nodes.new("ShaderNodeCombineColor")
    emit = nt.nodes.new("ShaderNodeEmission"); out_m = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], sepc.inputs["Color"])
    for ch in ("Red", "Green", "Blue"):
        nt.links.new(sepc.outputs["Red"], comb.inputs[ch])
    nt.links.new(comb.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out_m.inputs["Surface"])
    _bake_plane(mat, thr_img)
    thr_img.filepath_raw = str(out / "toon_threshold.png"); thr_img.file_format = "PNG"; thr_img.save()
    # AO correlation: baked red should track the ARM red it was derived from.
    tp = list(thr_img.pixels)[0::4]
    ap = list(arm.pixels)[0::4]
    n = min(len(tp), len(ap))
    ao_corr = _pearson(tp[:n], ap[:n])
    sidecar["maps"]["threshold"] = {**_measure(thr_img), "role": "threshold",
                                    "ao_corr": round(ao_corr, 4), "source": "ARM.r (AO)"}

    (out / SIDECAR).write_text(json.dumps(sidecar, indent=2))
    print(f"baked {out/'toon_noise.png'}, {out/'toon_threshold.png'}, {out/SIDECAR}")
    for name, m in sidecar["maps"].items():
        print(f"  {name}: {m['w']}x{m['h']} {m['colorspace']} edge_max_diff={m['edge_max_diff']}"
              + (f" ao_corr={m.get('ao_corr')}" if 'ao_corr' in m else ""))


def _pearson(a, b):
    n = len(a)
    if n == 0:
        return 0.0
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da and db else 0.0


def check_group() -> int:
    """Tier-2 validator: assert the noise group is wired and 4D, ARM source exists."""
    build_noise_group()
    ng = bpy.data.node_groups.get(NOISE_GROUP)
    errs = []
    if ng is None:
        errs.append("noise group not created")
    else:
        noise_nodes = [n for n in ng.nodes if n.type == "TEX_NOISE"]
        if not noise_nodes:
            errs.append("no Noise Texture node in group")
        elif noise_nodes[0].noise_dimensions != "4D":
            errs.append(f"noise dimensions {noise_nodes[0].noise_dimensions} != 4D")
        if not any(n.type == "TEX_COORD" for n in ng.nodes):
            errs.append("no Texture Coordinate (UV) node")
        sines = [n for n in ng.nodes if n.type == "MATH" and n.operation == "SINE"]
        cosines = [n for n in ng.nodes if n.type == "MATH" and n.operation == "COSINE"]
        if len(sines) < 2 or len(cosines) < 2:
            errs.append(f"expected 2 sine + 2 cosine (circle map), got {len(sines)}s/{len(cosines)}c")
    if not Path(ARM_REL).resolve().exists():
        errs.append(f"ARM texture missing at {ARM_REL}")
    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"control_maps: OK — '{NOISE_GROUP}' (4D circle-mapped noise) wired; ARM source present")
    return 0


def _args():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


if __name__ == "__main__":
    a = _args()
    if "--check" in a:
        sys.exit(check_group())
    if "--bake" in a:
        bake_all(a[a.index("--bake") + 1])
    else:
        build_noise_group()
        if "--save" in a:
            path = a[a.index("--save") + 1]
            bpy.ops.wm.save_as_mainfile(filepath=path)
            print(f"saved {path}")
        else:
            print(f"built '{NOISE_GROUP}' (open in GUI, or pass --bake OUTDIR / --save FILE)")
