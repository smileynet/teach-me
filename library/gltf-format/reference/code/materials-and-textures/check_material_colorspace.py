#!/usr/bin/env python3
"""check_material_colorspace.py — read a glTF's materials and check the color-space contract.

Companion artifact for lesson 04 (materials-and-textures). glTF has NO per-slot color-space
FLAG — the transfer function of a texture is defined by the SLOT that references it (spec §3.6.3):

  sRGB slots   : baseColorTexture, emissiveTexture           (color — sRGB-decoded before lighting)
  linear slots : normalTexture, metallicRoughnessTexture,    (data — used as-is)
                 occlusionTexture

So the file itself can't tell an engine which space an image is in; the engine decides from the
slot. This tool makes that concrete: it parses a `.glb`/`.gltf` (stdlib only — no Godot, no
Pillow), PRINTS the per-material slot→color-space table, then ASSERTS the one thing that is a
genuine bug — an image reused across an sRGB slot AND a linear slot (a color-space conflict: the
engine cannot decode the same bytes both ways).

    python check_material_colorspace.py cube_orm.glb
    python check_material_colorspace.py --json cube_orm.glb

Exit codes: 0 = parsed + no color-space conflict, 1 = a conflict found, 2 = not a glTF/GLB.
"""
from __future__ import annotations

import json
import struct
import sys

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942

# The family each slot implies (spec §5.19–5.22). No flag in the file carries this.
SRGB_SLOTS = ("baseColorTexture", "emissiveTexture")
LINEAR_SLOTS = ("normalTexture", "metallicRoughnessTexture", "occlusionTexture")


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


def _image_of(gltf: dict, tex_index: int) -> int | None:
    """Resolve a texture index → its image (source) index, or None if out of range."""
    textures = gltf.get("textures", [])
    if not (0 <= tex_index < len(textures)):
        return None
    return textures[tex_index].get("source")


def _slot_texture(material: dict, slot: str) -> dict | None:
    """A slot lives either at the material root (normal/occlusion) or under pbrMetallicRoughness."""
    if slot in material:
        return material[slot]
    return material.get("pbrMetallicRoughness", {}).get(slot)


def check_colorspace(gltf: dict) -> tuple[dict, list[str]]:
    """Assert no image is used across an sRGB and a linear slot. Returns (metrics, errors)."""
    errors: list[str] = []
    srgb_images: set[int] = set()
    linear_images: set[int] = set()
    n_textures = len(gltf.get("textures", []))

    for mi, material in enumerate(gltf.get("materials", [])):
        for slot in SRGB_SLOTS + LINEAR_SLOTS:
            tex = _slot_texture(material, slot)
            if tex is None:
                continue
            idx = tex.get("index")
            if idx is None or not (0 <= idx < n_textures):
                errors.append(f"material[{mi}].{slot}.index {idx} out of range (0..{n_textures - 1})")
                continue
            img = _image_of(gltf, idx)
            if img is None:
                errors.append(f"material[{mi}].{slot} → texture {idx} has no valid image source")
                continue
            (srgb_images if slot in SRGB_SLOTS else linear_images).add(img)

    conflict = sorted(srgb_images & linear_images)
    for img in conflict:
        errors.append(f"image[{img}] is used in BOTH an sRGB and a linear slot — "
                      f"the engine cannot decode the same bytes both ways (color-space conflict)")

    metrics = {
        "srgb_images": sorted(srgb_images),
        "linear_images": sorted(linear_images),
        "conflicts": conflict,
    }
    return metrics, errors


def print_table(gltf: dict) -> None:
    """Print the per-material slot→color-space table (the teaching output)."""
    materials = gltf.get("materials", [])
    if not materials:
        print("  (no materials — nothing to map)")
        return
    for mi, material in enumerate(materials):
        name = material.get("name", f"material[{mi}]")
        print(f"  {name}:")
        for slot in SRGB_SLOTS + LINEAR_SLOTS:
            tex = _slot_texture(material, slot)
            if tex is None:
                continue
            family = "sRGB  " if slot in SRGB_SLOTS else "linear"
            img = _image_of(gltf, tex.get("index", -1))
            print(f"    {slot:<26} {family}  → image {img}")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv[1:]
    if len(args) != 1:
        print("usage: python check_material_colorspace.py [--json] <file.glb|file.gltf>", file=sys.stderr)
        return 2

    gltf, _ = load_gltf(args[0])
    metrics, errors = check_colorspace(gltf)

    if as_json:
        print(json.dumps({
            "status": "pass" if not errors else "fail",
            "metrics": metrics,
            "errors": errors,
        }, indent=2))
        return 0 if not errors else 1

    print(f"Parsed {args[0]}:")
    print_table(gltf)
    if errors:
        print("\nFAIL — color-space contract broken:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\ncheck_material_colorspace: every image stays within one color-space family; no conflict.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"check_material_colorspace ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
