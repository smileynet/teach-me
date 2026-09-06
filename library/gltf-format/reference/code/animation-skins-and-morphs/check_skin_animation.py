#!/usr/bin/env python3
"""check_skin_animation.py — read a glTF's skin + animations and check the taught contracts.

Companion artifact for lesson 05 (animation-skins-and-morphs). Skinning re-poses one bind-pose
mesh through a matrix chain (AnimatedPos = JointWorld · InverseBind · RestPos); animation drives
joint transforms via channels + samplers. This tool makes that concrete on a REAL rigged asset
(no Godot, no Blender): it parses a `.glb`/`.gltf`, PRINTS the skin + per-animation channel/sampler
summary, then ASSERTS the spec contracts the lesson teaches.

    python check_skin_animation.py Wizard.glb
    python check_skin_animation.py --json Wizard.glb

Asserts:
  - each skin's inverseBindMatrices accessor is MAT4 / FLOAT(5126) with count >= number of joints
  - a skinned primitive carries JOINTS_0 + WEIGHTS_0 vertex attributes
  - each animation channel's sampler + target.node resolve in range
  - each sampler's input is a SCALAR / FLOAT(5126) time accessor; output resolves
  - each sampler's interpolation is one of LINEAR / STEP / CUBICSPLINE
  - for CUBICSPLINE, output.count == 3 * input.count (in-tangent, value, out-tangent per key)

Exit codes: 0 = parsed + all contracts hold, 1 = a contract failed, 2 = not a glTF/GLB.
"""
from __future__ import annotations

import json
import struct
import sys

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942
COMPONENT_FLOAT = 5126
INTERPOLATIONS = {"LINEAR", "STEP", "CUBICSPLINE"}


def load_gltf(path: str) -> tuple[dict, bytes | None]:
    """Return (gltf_json_dict, binary_blob_or_None) for a .glb or .gltf file — stdlib only."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"glTF":
        return json.loads(data), None
    if len(data) < 12:
        raise ValueError("file too small to be a GLB")
    magic, version, total_len = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise ValueError(f"bad GLB magic 0x{magic:08X} (expected 'glTF')")
    if version != 2:
        raise ValueError(f"GLB container version {version} != 2 (this is not glTF 2.0)")
    gltf = blob = None
    offset = 12
    while offset < total_len:
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        payload = data[offset:offset + chunk_len]
        offset += chunk_len
        if chunk_type == CHUNK_JSON:
            gltf = json.loads(payload)
        elif chunk_type == CHUNK_BIN:
            blob = payload
    if gltf is None:
        raise ValueError("GLB has no JSON chunk")
    return gltf, blob


def _in_range(idx, arr) -> bool:
    return isinstance(idx, int) and 0 <= idx < len(arr)


def check(gltf: dict) -> tuple[dict, list[str]]:
    """Assert the skin + animation contracts the lesson teaches. Returns (metrics, errors)."""
    errors: list[str] = []
    accessors = gltf.get("accessors", [])
    nodes = gltf.get("nodes", [])
    skins = gltf.get("skins", [])
    meshes = gltf.get("meshes", [])
    animations = gltf.get("animations", [])

    # --- skins: inverse-bind-matrices contract ---
    for si, skin in enumerate(skins):
        joints = skin.get("joints", [])
        ibm = skin.get("inverseBindMatrices")
        if ibm is None:
            continue  # legal (identity IBMs) — the lesson teaches the explicit case
        if not _in_range(ibm, accessors):
            errors.append(f"skin[{si}].inverseBindMatrices {ibm} out of range")
            continue
        acc = accessors[ibm]
        if acc.get("type") != "MAT4":
            errors.append(f"skin[{si}] IBM accessor type {acc.get('type')} != MAT4")
        if acc.get("componentType") != COMPONENT_FLOAT:
            errors.append(f"skin[{si}] IBM componentType {acc.get('componentType')} != FLOAT(5126)")
        if acc.get("count", 0) < len(joints):
            errors.append(f"skin[{si}] IBM count {acc.get('count')} < joints {len(joints)}")

    # --- a skinned primitive must carry JOINTS_0 + WEIGHTS_0 ---
    if skins:
        skinned_prim_ok = False
        for mesh in meshes:
            for prim in mesh.get("primitives", []):
                attrs = prim.get("attributes", {})
                if "JOINTS_0" in attrs and "WEIGHTS_0" in attrs:
                    skinned_prim_ok = True
        if not skinned_prim_ok:
            errors.append("asset has skins but no primitive carries JOINTS_0 + WEIGHTS_0")

    # --- animations: channels + samplers ---
    for ai, anim in enumerate(animations):
        samplers = anim.get("samplers", [])
        for ci, chan in enumerate(anim.get("channels", [])):
            if not _in_range(chan.get("sampler"), samplers):
                errors.append(f"animation[{ai}].channel[{ci}].sampler out of range")
                continue
            node = chan.get("target", {}).get("node")
            if node is not None and not _in_range(node, nodes):
                errors.append(f"animation[{ai}].channel[{ci}].target.node {node} out of range")
        for spi, samp in enumerate(samplers):
            si_in, si_out = samp.get("input"), samp.get("output")
            if not _in_range(si_in, accessors):
                errors.append(f"animation[{ai}].sampler[{spi}].input out of range")
                continue
            if not _in_range(si_out, accessors):
                errors.append(f"animation[{ai}].sampler[{spi}].output out of range")
                continue
            in_acc = accessors[si_in]
            if in_acc.get("type") != "SCALAR" or in_acc.get("componentType") != COMPONENT_FLOAT:
                errors.append(f"animation[{ai}].sampler[{spi}] input is not a FLOAT SCALAR time accessor")
            interp = samp.get("interpolation", "LINEAR")
            if interp not in INTERPOLATIONS:
                errors.append(f"animation[{ai}].sampler[{spi}] interpolation {interp!r} invalid")
            elif interp == "CUBICSPLINE":
                out_acc = accessors[si_out]
                if out_acc.get("count", 0) != 3 * in_acc.get("count", 0):
                    errors.append(f"animation[{ai}].sampler[{spi}] CUBICSPLINE output.count "
                                  f"{out_acc.get('count')} != 3 * input.count {in_acc.get('count')}")

    interps = sorted({s.get("interpolation", "LINEAR")
                      for a in animations for s in a.get("samplers", [])})
    metrics = {
        "skins": len(skins),
        "joints": [len(s.get("joints", [])) for s in skins],
        "animations": len(animations),
        "channels": sum(len(a.get("channels", [])) for a in animations),
        "interpolations": interps,
        "has_morph": any("targets" in p for m in meshes for p in m.get("primitives", [])),
    }
    return metrics, errors


def print_summary(gltf: dict, metrics: dict) -> None:
    print(f"  skins: {metrics['skins']} (joints: {metrics['joints']})")
    print(f"  animations: {metrics['animations']}  channels: {metrics['channels']}  "
          f"interpolation: {', '.join(metrics['interpolations']) or 'n/a'}")
    print(f"  morph targets present: {metrics['has_morph']}")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv[1:]
    if len(args) != 1:
        print("usage: python check_skin_animation.py [--json] <file.glb|file.gltf>", file=sys.stderr)
        return 2

    gltf, _ = load_gltf(args[0])
    metrics, errors = check(gltf)

    if as_json:
        print(json.dumps({"status": "pass" if not errors else "fail",
                          "metrics": metrics, "errors": errors}, indent=2))
        return 0 if not errors else 1

    print(f"Parsed {args[0]}:")
    print_summary(gltf, metrics)
    if errors:
        print("\nFAIL — a skin/animation contract broke:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\ncheck_skin_animation: skin IBM + animation channels/samplers hold.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"check_skin_animation ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
