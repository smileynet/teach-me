# godot-asset-pipeline — Third-Party Asset Manifest

Every third-party 3D asset used in this track, its source, license, and the lesson(s) that use it.
All are **CC0 1.0** — free for any use, attribution not legally required. We credit anyway (README
`## Credits` + each lesson's page footer). Every asset row here has its kit `License.txt` committed
beside the vendored files.

| Asset | Source kit | Publisher | License | Topics | Vendored path |
|-------|-----------|-----------|---------|--------|---------------|
| `chair` | Furniture Kit 2.1 | Kenney (kenney.nl) | CC0 1.0 | 1 (also reused 2–4) | `reference/code/first-import-happy-path/chair.glb` + `reference/blender/chair.blend` |

## Notes

- **`.blend` is derived from the `.glb`, not the FBX.** Kenney ships **ASCII FBX**, which Blender's
  `import_scene.fbx` does not support ("ASCII FBX files are not supported"). The `.glb` imports
  cleanly, so `make-blend` derives `chair.blend` from `chair.glb`; `export-godot-glb` re-emits the
  committed `chair.glb`. (Confirmed 2026-09-07.)
- Assets committed as **plain git blobs** (small; not Git LFS — Pages doesn't serve LFS content).
- Later topics add: Nature Kit mesh (topic 5 LOD); Animated Characters Bundle `characterSmall` +
  clips + skins + `characterMedium` retarget sibling (topics 6–7). Add rows when vendored.
