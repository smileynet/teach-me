#!/usr/bin/env python3
"""check_extensions.py — read a glTF's extensions and check the used/required contract.

Companion artifact for lesson 06 (extensions-and-optimization). glTF grows through extensions;
`extensionsUsed` lists everything present (a viewer MAY ignore any of it), `extensionsRequired`
lists what a viewer MUST understand or it SHOULD NOT load the asset. The one decision that governs
the split: *does the core still render without this extension?* — no ⇒ Required, yes ⇒ Used-only.

This tool parses a `.glb`/`.gltf` (stdlib only — no Godot, no Node), prints a per-extension
table (required? / has a core-glTF fallback?), then asserts the contract:

  - extensionsRequired MUST be a subset of extensionsUsed (spec §3.12)
  - a COMPRESSION extension (Draco / meshopt / KTX2-basisu) present in Used but NOT Required is an
    ERROR — its buffer bytes are unreadable without the decoder, so marking it optional is a lie
  - a MATERIAL extension (KHR_materials_*) in Required is a NOTE, not an error — the asset still
    loads and falls back to base metal-rough, so forcing rejection is usually a mistake (but legal)

    python check_extensions.py truck-green.glb
    python check_extensions.py --json truck-green.glb

Exit codes: 0 = contract holds, 1 = a contract error, 2 = not a glTF/GLB.
"""
from __future__ import annotations

import json
import struct
import sys

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942

# Compression extensions rewrite buffer/image bytes — no core-glTF fallback, so they MUST be required.
COMPRESSION_EXTS = {"KHR_draco_mesh_compression", "EXT_meshopt_compression", "KHR_texture_basisu"}
# Material extensions layer onto the core metal-rough model, which is always a valid fallback.
MATERIAL_EXT_PREFIX = "KHR_materials_"


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


def classify(name: str) -> str:
    if name in COMPRESSION_EXTS:
        return "compression"
    if name.startswith(MATERIAL_EXT_PREFIX):
        return "material"
    return "other"


def check(gltf: dict) -> tuple[dict, list[str], list[str]]:
    """Assert the used/required contract. Returns (metrics, errors, notes)."""
    used = list(gltf.get("extensionsUsed", []))
    required = set(gltf.get("extensionsRequired", []))
    used_set = set(used)
    errors: list[str] = []
    notes: list[str] = []

    # spec §3.12: required must be a subset of used
    for ext in required:
        if ext not in used_set:
            errors.append(f"extensionsRequired '{ext}' is not in extensionsUsed (spec §3.12)")

    # a compression ext must be required (no fallback — the bytes are unreadable without the decoder)
    for ext in used:
        if classify(ext) == "compression" and ext not in required:
            errors.append(f"'{ext}' is a compression extension in extensionsUsed but NOT required — "
                          f"a non-supporting viewer would read garbage; it must be required")

    # a material ext in required is usually a mistake (core metal-rough is a valid fallback) — a NOTE
    for ext in sorted(required):
        if classify(ext) == "material":
            notes.append(f"'{ext}' is a material extension marked required — core metal-rough is a "
                         f"valid fallback, so this needlessly rejects non-supporting viewers (legal, but review)")

    metrics = {
        "extensionsUsed": used,
        "extensionsRequired": sorted(required),
        "classes": {ext: classify(ext) for ext in used},
    }
    return metrics, errors, notes


def print_table(metrics: dict, required: set) -> None:
    used = metrics["extensionsUsed"]
    if not used:
        print("  (no extensions)")
        return
    print(f"  {'extension':<34} {'class':<12} required?  has-fallback?")
    for ext in used:
        cls = metrics["classes"][ext]
        req = "yes" if ext in required else "no"
        fallback = "no" if cls == "compression" else ("yes" if cls == "material" else "—")
        print(f"  {ext:<34} {cls:<12} {req:<9}  {fallback}")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv[1:]
    if len(args) != 1:
        print("usage: python check_extensions.py [--json] <file.glb|file.gltf>", file=sys.stderr)
        return 2

    gltf, _ = load_gltf(args[0])
    metrics, errors, notes = check(gltf)

    if as_json:
        print(json.dumps({"status": "pass" if not errors else "fail",
                          "metrics": metrics, "errors": errors, "notes": notes}, indent=2))
        return 0 if not errors else 1

    print(f"Parsed {args[0]}:")
    print_table(metrics, set(metrics["extensionsRequired"]))
    for n in notes:
        print(f"  NOTE: {n}")
    if errors:
        print("\nFAIL — the extension contract is broken:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\ncheck_extensions: extensionsRequired ⊆ used and every no-fallback extension is required.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"check_extensions ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
