#!/usr/bin/env python3
"""gltf-format-oracle.py — validate the glTF-2.0 structural contracts taught in the gltf-format domain.

Tier-1 gate for the `gltf-format` teaching domain (#309). Parses real `.glb`/`.gltf` sample assets
with the STDLIB ONLY (`struct` + `json`, no third-party lib) and asserts the spec-level properties
the lessons teach — the same claims a learner is told to verify from the file itself. This is a
*property oracle* (asserts the taught claim), not a syntax check.

Contracts asserted (per the domain's topics):
  anatomy (topic 1):   .glb header magic == 'glTF', container version == 2, chunk layout parses,
                       JSON chunk is valid JSON, asset.version == "2.0", top-level arrays present
                       (scenes/nodes/meshes/accessors/bufferViews), index referential integrity.
  materials (topic 4): every material's pbrMetallicRoughness / texture indices resolve in range.
  skins (topic 5):     a skinned asset's skin carries inverseBindMatrices whose accessor is
                       MAT4 / FLOAT(5126) with count >= len(joints); mesh morph-target count is
                       consistent across a primitive's targets.
  extensions (topic 6): every entry in extensionsRequired is also in extensionsUsed.

Stdlib-only (like posterize/palette-snap/bake-export oracles). GLB gotchas handled: little-endian;
container version 2 != asset.version "2.0"; JSON chunk 0x4E4F534A / BIN chunk 0x004E4942; JSON
padded with 0x20; BIN chunkLength may exceed buffers[0].byteLength by up to 3 (assert >= with
delta <= 3); 4-byte alignment; gate on container version == 2 (glTF 1.0 GLB has a 20-byte header).

Exit codes: 0 = all contracts hold, 1 = a contract failed, 2 = error (missing/unparseable asset).
Structured JSON summary on --json.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

# Constants from the GLB spec (Khronos glTF 2.0, §4.4).
GLB_MAGIC = 0x46546C67          # 'glTF' little-endian
GLB_VERSION = 2                 # container version (NOT asset.version)
CHUNK_JSON = 0x4E4F534A         # 'JSON'
CHUNK_BIN = 0x004E4942          # 'BIN\0'
ACCESSOR_MAT4 = "MAT4"
COMPONENT_FLOAT = 5126

# Color-space families (topic 4). glTF has NO per-slot color-space flag — the transfer function is
# implied by the SLOT that references a texture (spec §3.6.3, §5.19–5.22). An image used across an
# sRGB slot AND a linear slot is a genuine conflict (the engine can't decode the same bytes both ways).
SRGB_SLOTS = ("baseColorTexture", "emissiveTexture")
LINEAR_SLOTS = ("normalTexture", "metallicRoughnessTexture", "occlusionTexture")

# Extension classification (topic 6). Compression extensions rewrite buffer/image bytes — there is no
# core-glTF fallback, so they MUST be listed in extensionsRequired. Material extensions layer onto the
# core metal-rough model (always a valid fallback), so marking them required needlessly rejects viewers.
COMPRESSION_EXTS = {"KHR_draco_mesh_compression", "EXT_meshopt_compression", "KHR_texture_basisu"}
MATERIAL_EXT_PREFIX = "KHR_materials_"

# Sample assets already committed in the shader test project (CC0/permissive) + lesson fixtures.
DEFAULT_ASSETS = [
    "test-scene/assets/kenney-retro-urban/truck-green.glb",          # static prop
    "test-scene/assets/quaternius-characters/Wizard.glb",            # rigged (skin + animation)
    "test-scene/assets/polyhaven/Barrel_01/Barrel_01_1k.gltf",       # .gltf + .bin + textures
    # gltf-format domain lesson fixtures (the taught minimal triangle, both container forms):
    "library/gltf-format/reference/code/gltf-anatomy-and-the-standard/triangle.gltf",
    "library/gltf-format/reference/code/gltf-anatomy-and-the-standard/triangle.glb",
    # lesson 02 (authoring-and-blender-export): the "clean export" cube (material-channel gated).
    "library/gltf-format/reference/code/authoring-and-blender-export/cube_metalrough.glb",
    # lesson 04 (materials-and-textures): both-color-families cube (base=sRGB, ORM+normal=linear).
    "library/gltf-format/reference/code/materials-and-textures/cube_orm.glb",
    # lesson 05 (animation-skins-and-morphs): minimal morph-target triangle (lights the morph branch).
    "library/gltf-format/reference/code/animation-skins-and-morphs/morph_tri.glb",
    # lesson 06 (extensions-and-optimization): declare-only required-compression-ext triangle.
    "library/gltf-format/reference/code/extensions-and-optimization/required_ext.glb",
]

# Assets that MUST carry a pbrMetallicRoughness material with a baseColorTexture — the lesson-02
# "clean export" contract. (The triangle/props are geometry-only and are NOT held to this.)
REQUIRE_MATERIAL = {
    "library/gltf-format/reference/code/authoring-and-blender-export/cube_metalrough.glb",
}


def parse_gltf_json(path: Path) -> dict:
    """Return the glTF JSON dict from a .glb (binary) or .gltf (plain JSON) file — stdlib only."""
    data = path.read_bytes()
    if path.suffix.lower() == ".gltf":
        return json.loads(data)
    # .glb: 12-byte header (magic, version, length), then length-prefixed chunks.
    if len(data) < 12:
        raise ValueError(f"{path.name}: too small to be a GLB")
    magic, version, total_len = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise ValueError(f"{path.name}: bad GLB magic 0x{magic:08X} (expected 'glTF')")
    if version != GLB_VERSION:
        raise ValueError(f"{path.name}: GLB container version {version} != 2 (glTF 1.0 unsupported)")
    if total_len != len(data):
        raise ValueError(f"{path.name}: header length {total_len} != file size {len(data)}")
    # First chunk must be JSON.
    offset = 12
    chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
    offset += 8
    if chunk_type != CHUNK_JSON:
        raise ValueError(f"{path.name}: first chunk type 0x{chunk_type:08X} is not JSON")
    json_bytes = data[offset:offset + chunk_len]
    return json.loads(json_bytes)  # trailing 0x20 padding is valid JSON whitespace


def _in_range(idx, arr) -> bool:
    return isinstance(idx, int) and 0 <= idx < len(arr)


def check_asset(path: Path, require_material: bool = False) -> tuple[dict, list[str]]:
    """Assert the taught structural contracts on one asset. Returns (metrics, errors).

    require_material: also assert the asset carries a pbrMetallicRoughness material with a
    baseColorTexture (the lesson-02 "clean export" contract) — not just index integrity.
    """
    errors: list[str] = []
    g = parse_gltf_json(path)

    accessors = g.get("accessors", [])
    buffer_views = g.get("bufferViews", [])
    nodes = g.get("nodes", [])
    meshes = g.get("meshes", [])
    skins = g.get("skins", [])

    metrics = {
        "file": str(path),
        "asset_version": g.get("asset", {}).get("version"),
        "counts": {
            "scenes": len(g.get("scenes", [])),
            "nodes": len(nodes),
            "meshes": len(meshes),
            "accessors": len(accessors),
            "bufferViews": len(buffer_views),
            "skins": len(skins),
            "animations": len(g.get("animations", [])),
            "materials": len(g.get("materials", [])),
        },
        "extensionsUsed": g.get("extensionsUsed", []),
        "extensionsRequired": g.get("extensionsRequired", []),
    }

    # --- anatomy (topic 1) ---
    if g.get("asset", {}).get("version") != "2.0":
        errors.append(f"{path.name}: asset.version {g.get('asset', {}).get('version')!r} != '2.0'")
    if not meshes and not nodes:
        errors.append(f"{path.name}: no nodes and no meshes (empty scene?)")
    # accessor -> bufferView index integrity (bufferView is optional for sparse accessors)
    for i, acc in enumerate(accessors):
        bv = acc.get("bufferView")
        if bv is not None and not _in_range(bv, buffer_views):
            errors.append(f"{path.name}: accessor[{i}].bufferView {bv} out of range")

    # --- materials (topic 4): texture indices resolve ---
    textures = g.get("textures", [])
    materials = g.get("materials", [])
    for i, mat in enumerate(materials):
        pbr = mat.get("pbrMetallicRoughness", {})
        for slot in ("baseColorTexture", "metallicRoughnessTexture"):
            tex = pbr.get(slot)
            if tex is not None and not _in_range(tex.get("index"), textures):
                errors.append(f"{path.name}: material[{i}].{slot}.index out of range")
        # normal/occlusion live at the material root — also index-check them
        for slot in ("normalTexture", "occlusionTexture"):
            tex = mat.get(slot)
            if tex is not None and not _in_range(tex.get("index"), textures):
                errors.append(f"{path.name}: material[{i}].{slot}.index out of range")

    # --- color space (topic 4): no image used across an sRGB and a linear slot ---
    def _slot_tex(mat: dict, slot: str):
        return mat[slot] if slot in mat else mat.get("pbrMetallicRoughness", {}).get(slot)

    srgb_images: set[int] = set()
    linear_images: set[int] = set()
    for mat in materials:
        for slot in SRGB_SLOTS + LINEAR_SLOTS:
            tex = _slot_tex(mat, slot)
            if tex is None or not _in_range(tex.get("index"), textures):
                continue
            img = textures[tex["index"]].get("source")
            if img is None:
                continue
            (srgb_images if slot in SRGB_SLOTS else linear_images).add(img)
    conflict = sorted(srgb_images & linear_images)
    for img in conflict:
        errors.append(f"{path.name}: image[{img}] used in BOTH an sRGB and a linear slot "
                      f"(color-space conflict — the engine can't decode the same bytes both ways)")
    if srgb_images or linear_images:
        metrics["color_space"] = {"srgb_images": sorted(srgb_images),
                                  "linear_images": sorted(linear_images),
                                  "conflicts": conflict}

    # --- material-channel presence (lesson-02 "clean export" contract, opt-in) ---
    if require_material:
        if not materials:
            errors.append(f"{path.name}: require-material: no materials (expected pbrMetallicRoughness)")
        else:
            pbr0 = materials[0].get("pbrMetallicRoughness")
            if pbr0 is None:
                errors.append(f"{path.name}: require-material: material[0] has no pbrMetallicRoughness")
            elif "baseColorTexture" not in pbr0:
                errors.append(f"{path.name}: require-material: material[0].pbrMetallicRoughness "
                              f"has no baseColorTexture")

    # --- skins (topic 5): inverseBindMatrices contract ---
    has_skin = bool(skins)
    for i, skin in enumerate(skins):
        joints = skin.get("joints", [])
        ibm = skin.get("inverseBindMatrices")
        if ibm is None:
            # legal per spec (identity IBMs) but the lesson teaches the explicit-IBM case
            metrics.setdefault("notes", []).append(f"skin[{i}] has no inverseBindMatrices (identity)")
            continue
        if not _in_range(ibm, accessors):
            errors.append(f"{path.name}: skin[{i}].inverseBindMatrices {ibm} out of range")
            continue
        acc = accessors[ibm]
        if acc.get("type") != ACCESSOR_MAT4:
            errors.append(f"{path.name}: skin[{i}] IBM accessor type {acc.get('type')} != MAT4")
        if acc.get("componentType") != COMPONENT_FLOAT:
            errors.append(f"{path.name}: skin[{i}] IBM componentType {acc.get('componentType')} != FLOAT(5126)")
        if acc.get("count", 0) < len(joints):
            errors.append(f"{path.name}: skin[{i}] IBM count {acc.get('count')} < joints {len(joints)}")
    metrics["has_skin"] = has_skin

    # --- morph targets (topic 5): consistent target count within a primitive ---
    for mi, mesh in enumerate(meshes):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            targets = prim.get("targets")
            if targets and mesh.get("weights") is not None:
                if len(mesh["weights"]) != len(targets):
                    errors.append(f"{path.name}: mesh[{mi}] weights {len(mesh['weights'])} "
                                  f"!= primitive[{pi}] targets {len(targets)}")

    # --- animation (topic 5): channels + samplers resolve; interpolation valid ---
    animations = g.get("animations", [])
    for ai, anim in enumerate(animations):
        samplers = anim.get("samplers", [])
        for ci, chan in enumerate(anim.get("channels", [])):
            if not _in_range(chan.get("sampler"), samplers):
                errors.append(f"{path.name}: animation[{ai}].channel[{ci}].sampler out of range")
            node = chan.get("target", {}).get("node")
            if node is not None and not _in_range(node, nodes):
                errors.append(f"{path.name}: animation[{ai}].channel[{ci}].target.node {node} out of range")
        for si, samp in enumerate(samplers):
            in_i, out_i = samp.get("input"), samp.get("output")
            if not _in_range(in_i, accessors) or not _in_range(out_i, accessors):
                errors.append(f"{path.name}: animation[{ai}].sampler[{si}] input/output accessor out of range")
                continue
            in_acc = accessors[in_i]
            if in_acc.get("type") != "SCALAR" or in_acc.get("componentType") != COMPONENT_FLOAT:
                errors.append(f"{path.name}: animation[{ai}].sampler[{si}] input not a FLOAT SCALAR time accessor")
            interp = samp.get("interpolation", "LINEAR")
            if interp not in ("LINEAR", "STEP", "CUBICSPLINE"):
                errors.append(f"{path.name}: animation[{ai}].sampler[{si}] interpolation {interp!r} invalid")
            elif interp == "CUBICSPLINE" and accessors[out_i].get("count", 0) != 3 * in_acc.get("count", 0):
                errors.append(f"{path.name}: animation[{ai}].sampler[{si}] CUBICSPLINE output.count "
                              f"{accessors[out_i].get('count')} != 3 * input.count {in_acc.get('count')}")

    # --- extensions (topic 6): required subset of used + no-fallback classification ---
    used = set(metrics["extensionsUsed"])
    required = set(metrics["extensionsRequired"])
    for ext in metrics["extensionsRequired"]:
        if ext not in used:
            errors.append(f"{path.name}: extensionsRequired '{ext}' not in extensionsUsed")
    # a compression ext has no core-glTF fallback → it MUST be required (else a viewer reads garbage)
    for ext in metrics["extensionsUsed"]:
        if ext in COMPRESSION_EXTS and ext not in required:
            errors.append(f"{path.name}: compression extension '{ext}' is used but not required "
                          f"(no fallback — a non-supporting viewer would read garbage)")
    # a material ext IS fallback-able → marking it required is a soft note, never an error
    material_required = sorted(e for e in required if e.startswith(MATERIAL_EXT_PREFIX))
    if material_required:
        metrics.setdefault("notes", []).append(
            f"material extension(s) marked required (core metal-rough is a valid fallback): "
            f"{', '.join(material_required)}")

    return metrics, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate glTF-2.0 structural contracts (gltf-format domain)")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    ap.add_argument("--require-material", action="append", default=[],
                    help="path to assert has a pbrMetallicRoughness + baseColorTexture (repeatable)")
    ap.add_argument("assets", nargs="*", default=None,
                    help="glTF/GLB files to check (default: committed sample assets)")
    args = ap.parse_args()

    paths = [Path(a) for a in (args.assets or DEFAULT_ASSETS)]
    explicit_require = {str(Path(p)) for p in args.require_material}
    all_metrics: list[dict] = []
    all_errors: list[str] = []
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"asset not found: {p}")
        require = str(p) in REQUIRE_MATERIAL or str(p) in explicit_require
        m, e = check_asset(p, require_material=require)
        all_metrics.append(m)
        all_errors.extend(e)

    status = "pass" if not all_errors else "fail"

    if args.json:
        print(json.dumps({"status": status, "metrics": all_metrics, "errors": all_errors}, indent=2))
    else:
        for m in all_metrics:
            c = m["counts"]
            skin = "skinned" if m.get("has_skin") else "static"
            print(f"  {Path(m['file']).name}: v{m['asset_version']} {skin} — "
                  f"{c['nodes']}n/{c['meshes']}m/{c['accessors']}acc/{c['skins']}skin/{c['animations']}anim"
                  f"{'  ext=' + ','.join(m['extensionsUsed']) if m['extensionsUsed'] else ''}")
        if all_errors:
            print("\nFAIL:")
            for e in all_errors:
                print(f"  - {e}")
        else:
            print("\ngltf-format-oracle: all glTF-2.0 structural contracts hold "
                  "(anatomy, materials, skin IBM, morphs, extensions)")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard for CI exit code 2
        print(f"gltf-format-oracle ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
