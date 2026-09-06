#!/usr/bin/env python3
"""map_to_nodes.py — show the engine scene-node tree a glTF file would import into.

Companion artifact for lesson 03 (consuming-gltf-engine-import). An engine doesn't
"open" a glTF — it *translates* the file's object graph into its own scene-node types,
once, on import, using a fixed concept->node dictionary. This tool makes that dictionary
concrete: it parses a .glb/.gltf with the standard library alone (no Godot, no
third-party deps), PRINTS the engine nodes the importer would build, then ASSERTS the
mapping claims the lesson teaches.

    python map_to_nodes.py Wizard.glb
    python map_to_nodes.py --json Wizard.glb

The node names use Godot's vocabulary (MeshInstance3D, Skeleton3D, AnimationPlayer, ...)
because Godot is the lesson's worked example — but the *shape* (one engine node per glTF
concept, keyed by index) is universal: three.js, Babylon, and Unity glTFast all do the
same thing (glTFast literally keys a `Dictionary<uint, GameObject>` by glTF node index).

Exit codes: 0 = parsed + all mapping asserts hold, 1 = an assert failed, 2 = not a glTF/GLB.
"""
from __future__ import annotations

import json
import struct
import sys

# --- GLB container constants (Khronos glTF 2.0 spec, section 4.4) ---
GLB_MAGIC = 0x46546C67   # the four bytes 'glTF', read little-endian
CHUNK_JSON = 0x4E4F534A  # 'JSON'
CHUNK_BIN = 0x004E4942   # 'BIN\0'

# The fixed concept->node dictionary the lesson teaches (Godot's vocabulary, one
# consumer of many). Only `scene/node -> Node3D` is [L4:inferred] (Node3D is the
# *recommended* root, not mandated); the rest are [L4:verified] against the Godot RST.
GLTF_MESH_NODE = "MeshInstance3D"
GLTF_SKIN_NODE = "Skeleton3D"          # + a Skin resource
GLTF_MATERIAL_NODE = "StandardMaterial3D"
GLTF_ANIMATION_NODE = "AnimationPlayer"
GLTF_CAMERA_NODE = "Camera3D"
GLTF_LIGHT_NODE = {                    # KHR_lights_punctual type -> Light3D subclass
    "directional": "DirectionalLight3D",
    "point": "OmniLight3D",
    "spot": "SpotLight3D",
}


def load_gltf(path: str) -> tuple[dict, bytes | None]:
    """Return (gltf_json_dict, binary_blob_or_None) for a .glb or .gltf file — stdlib only."""
    with open(path, "rb") as f:
        data = f.read()

    # A .gltf file *is* JSON — no container to unwrap.
    if data[:4] != b"glTF":
        return json.loads(data), None

    # A .glb file is a tiny little-endian binary container:
    #   12-byte header (magic, version, total length) + length-prefixed chunks.
    if len(data) < 12:
        raise ValueError("file too small to be a GLB")
    magic, version, total_len = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise ValueError(f"bad GLB magic 0x{magic:08X} (expected 'glTF')")
    if version != 2:
        raise ValueError(f"GLB container version {version} != 2 (this is not glTF 2.0)")
    if total_len != len(data):
        raise ValueError(f"header length {total_len} != actual file size {len(data)}")

    gltf: dict | None = None
    blob: bytes | None = None
    offset = 12
    while offset < total_len:
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        payload = data[offset:offset + chunk_len]
        offset += chunk_len
        if chunk_type == CHUNK_JSON:
            gltf = json.loads(payload)     # trailing 0x20 space padding is valid JSON whitespace
        elif chunk_type == CHUNK_BIN:
            blob = payload
        # Any other chunk type is a future extension — the spec says: ignore it.

    if gltf is None:
        raise ValueError("GLB has no JSON chunk")
    return gltf, blob


def build_mapping(g: dict) -> dict:
    """Walk the glTF object graph and report the engine nodes an importer would build.

    Returns a metrics dict counting each engine-node type. This mirrors what every
    runtime does: one engine node per glTF node (indexed), plus resources for skins,
    materials, and animations.
    """
    nodes = g.get("nodes", [])
    lights = g.get("extensions", {}).get("KHR_lights_punctual", {}).get("lights", [])

    node3d = len(nodes)                                             # every glTF node -> a scene node
    mesh_instances = sum(1 for n in nodes if "mesh" in n)           # node w/ mesh -> MeshInstance3D
    skeletons = len(g.get("skins", []))                             # skin -> Skeleton3D (+ Skin)
    materials = len(g.get("materials", []))                         # material -> StandardMaterial3D
    cameras = len(g.get("cameras", []))                             # camera -> Camera3D
    animation_players = 1 if g.get("animations") else 0            # animations -> one AnimationPlayer
    light_nodes = [GLTF_LIGHT_NODE.get(l.get("type"), "Light3D") for l in lights]

    return {
        "node3d": node3d,
        "mesh_instance3d": mesh_instances,
        "skeleton3d": skeletons,
        "standard_material3d": materials,
        "camera3d": cameras,
        "animation_player": animation_players,
        "light3d": light_nodes,
    }


def assert_mapping(g: dict) -> list[str]:
    """Assert the mapping claims the lesson teaches. Returns a list of failures (empty = pass).

    These are the referential-integrity contracts a real importer relies on to build a
    valid scene — the same subset the domain gltf-format-oracle.py checks. If any fail,
    the importer would produce a broken or incomplete scene tree.
    """
    errors: list[str] = []
    nodes = g.get("nodes", [])
    meshes = g.get("meshes", [])
    skins = g.get("skins", [])
    materials = g.get("materials", [])

    # Every glTF mesh must be referenced by some node — an orphan mesh becomes no MeshInstance3D.
    referenced_meshes = {n["mesh"] for n in nodes if "mesh" in n}
    for mi in range(len(meshes)):
        if mi not in referenced_meshes:
            errors.append(f"mesh[{mi}] is not referenced by any node (would import as nothing)")

    # Every glTF skin must be used by a skinned node — an unused skin builds no Skeleton3D binding.
    used_skins = {n["skin"] for n in nodes if "skin" in n}
    for si in range(len(skins)):
        if si not in used_skins:
            errors.append(f"skin[{si}] is not used by any node (Skeleton3D would bind nothing)")

    # Every material a primitive references must resolve — a dangling index breaks StandardMaterial3D.
    for mi, mesh in enumerate(meshes):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            m = prim.get("material")
            if m is not None and not (0 <= m < len(materials)):
                errors.append(f"mesh[{mi}].primitive[{pi}].material {m} out of range")

    return errors


def print_tree(g: dict, metrics: dict) -> None:
    """Print the engine scene tree the importer would build, in the lesson's vocabulary."""
    print("  Engine scene the importer would build (Godot node types, one consumer of many):")
    print(f"    Node3D            x{metrics['node3d']:<4} (one per glTF node; scene root)")
    print(f"    MeshInstance3D    x{metrics['mesh_instance3d']:<4} (nodes carrying a mesh)")
    print(f"    Skeleton3D        x{metrics['skeleton3d']:<4} (one per skin, + a Skin resource)")
    print(f"    StandardMaterial3D x{metrics['standard_material3d']:<3} (one per glTF material)")
    print(f"    Camera3D          x{metrics['camera3d']:<4}")
    print(f"    AnimationPlayer   x{metrics['animation_player']:<4} "
          f"(holds all {len(g.get('animations', []))} glTF animation(s))")
    if metrics["light3d"]:
        print(f"    Light3D           x{len(metrics['light3d']):<4} ({', '.join(metrics['light3d'])})")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv[1:]
    if len(args) != 1:
        print("usage: python map_to_nodes.py [--json] <file.glb|file.gltf>", file=sys.stderr)
        return 2
    path = args[0]

    gltf, _ = load_gltf(path)
    metrics = build_mapping(gltf)
    errors = assert_mapping(gltf)

    if as_json:
        print(json.dumps({
            "status": "pass" if not errors else "fail",
            "metrics": metrics,
            "errors": errors,
        }, indent=2))
        return 0 if not errors else 1

    print(f"Parsed {path}:")
    print_tree(gltf, metrics)
    if errors:
        print("\nFAIL — the mapping contract does not hold:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nmap_to_nodes: every glTF concept maps to an engine node; the mapping holds.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"map_to_nodes ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
