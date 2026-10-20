# Prince Core Blender Assets

Reusable, lightweight Blender assets and native staging helpers for narrated explainers. Includes only original procedural people/prop generators, their native `.blend` outputs, generic demo code/previews, and Unity's separately licensed CC0 fire/smoke flipbooks. No third-party animal models, production scenes, book text, storyboard, narration, video, credentials or private production data.

## Contents

- `blender/prince-core-people.blend` — six **static, unrigged** human silhouettes: white/black ruler, ordinary person, soldier. Rulers have a small crown; ordinary/soldiers have a contrasting belt.
- `blender/prince-core-props.blend` — agreement sheet, net, veil, gate, house, snare. Symbolic starter props; stage them to fit the actual action.
- `blender/human_silhouettes.py`, `blender/narrative_props.py` — original procedural generators. Existing assets are unchanged.
- `blender/append_assets.py` — append a named collection from a `.blend` library.
- `blender/hybrid_stage.py` — small portable native toolkit: articulated primitive actor, seekable intact/broken/revealed/blocked/required/comparison links, multi-input required-condition junction, sampled-motion held-camera fit.
- `blender/demo_hybrid.py` — generic abstract diagram and concrete actor/house proof. Reuses `narrative_props.make_house`; does not import any production renderer.
- `run_hybrid_proof.py` — nonblocking render-lock launcher, screen-space Korean-label composition and proof checks.
- `previews/` — actual people/props indexes and a six-sample native hybrid contact sheet.
- `tests/hybrid-proof-summary.json` — compact measured proof, source/frame hashes, review scope and limits. Full regenerated proofs stay in your chosen output directory.
- `textures/fire-cc0/` — four Unity CC0 flipbook atlases and exact license/manifest.

## Append existing assets

Requires Blender 4.5+. In a Blender Python script:

```python
import sys
sys.path.insert(0, "/path/to/this-repository/blender")
from append_assets import append_collection
people = append_collection("/path/to/this-repository/blender/prince-core-people.blend", "White Ruler")
props = append_collection("/path/to/this-repository/blender/prince-core-props.blend", "Net")
```

The six people and six prop collections use local origins. The old human libraries remain static/unrigged. The **separate** new `Actor` has procedural shoulder pivots and posed leg segments, not an armature or skin. Neither system claims natural walking, world-space foot-lock IK or a grasp/contact solver. Contact sheets are indexes, not finished scene designs. The original house is intentionally a rough starter; its roof panels can read as split/raised.

## Native toolkit API

Inside Blender, after adding the repository's `blender` directory to `sys.path`:

```python
from hybrid_stage import Actor, Relation, Conjunction, material
ivory = material("ivory", (.86, .87, .85, 1))
teal = material("relation", (.18, .62, .57, 1))
red = material("interruption", (.65, .19, .18, 1))
actor = Actor("Visitor", ivory, teal)
actor.pose(location=(-2, 0, 0), turn=0.0, walk=1.2, gesture=0.3)
link = Relation("required input", (-2, 0, 1), (2, 0, 1), teal, red, mode="require")
link.update(1.0)  # both outer endpoints attached; no permission arrowhead
```

- `Relation(..., mode=..., parent=None)`: `reveal`, `intact`, `break`, `require`, `blocked`, `compare`. `update(p, a=None, b=None)` overwrites hidden and visible transforms, accepts moving attachment points, and supports arbitrary/reverse seeking. Nonidentical endpoints required. Optional parent uses common parent-local coordinates. Break/blocked X markers assume an XZ diagram viewed from -Y. A broken link retains its direction tip; required/comparison/blocked links have none.
- `Conjunction(name, inputs, junction, output, mat, warning_mat)`: at least two input attachment points joined through an explicit required-condition junction. `update(p)` reveals all required paths. These are necessary conditions, **not** sufficient permission; keep the direct qualifier in the label. Use endpoints on your node boundaries (or a shared junction center).
- `set_segment(ob, a, b)`: exact cap-center placement for the unit-depth mesh returned by `segment`; not for arbitrary imported meshes.
- `held_camera(scene, location, target)` and `fit_held_camera(scene, camera, objects, update, phases=..., safe=...)`: unshifted AUTO/HORIZONTAL orthographic landscape/square-pixel camera. Fits the union of supplied visible mesh corners across sampled motion, reserves a normalized safe rectangle, then freezes the camera. Supply all extrema and exclude ground. This is not continuous-motion bounds proof or an automatic text layout solver.
- `camera_signature(camera)`, `ease(p, start=.12, end=.72)`: fixed-camera and pure-time helpers.

Concrete events use actors/meaningful props; abstract relations use concise direct Korean labels and meaningful connectors in the same native Blender pipeline. Avoid arbitrary numbered badges and legend indirection. Hold each camera; change framing only at hard cuts. The demo renders two independent held shots, not a camera transition. Titles/labels are composited in screen space **after** rendering native mesh geometry, not world-space text planes.

## Run the real offline proof

Dependencies: Blender 4.5+ (tested 4.5.14 LTS), Python 3, Pillow, a separately installed Korean-capable font. On Linux/macOS the runner uses `fcntl.flock`. No downloads or network access are required by the code.

```sh
python run_hybrid_proof.py \
  --blender /path/to/blender \
  --font /path/to/korean-font.ttf \
  --lock /path/to/shared-render.lock \
  --out /path/to/fresh-proof-directory
```

For a font collection use `--font-index N`. Use the **same existing shared lock** as your other Blender production jobs. Busy lock exits **73**, reports `RENDER_NOT_RUN`, and creates no output; it does not wait or bypass the lock. Existing output directories are refused to avoid mixed proofs. The launcher passes `--background --factory-startup --disable-autoexec --python-exit-code 1`.

Output: six native 1280×720 PNGs (three phases per shot), six labelled PNGs, `native-report.json`, `proof-report.json`, `contact-sheet.png`, `blender.log`. No audio, video, source model or `.blend` output. Workbench studio shading, AA 16, shadows and cavity are explicit—not EEVEE. Reports include frame hashes, render timings, frozen camera signatures, sampled mesh/label bounds, pixel differences, articulated vertex displacement, reverse-seek checks and actual settled connector cap/tip attachment errors. Necessary-condition dashes include the destination endpoint, fixing an end-short-of-node pattern; tests also include changing endpoints and conjunction attachment.

The bundled proof record is a six-still sampled technical/visual review, **not** full animation watching, full-user QA, natural-gait validation or aesthetic approval. The roof starter remains rough and the approach is modest; no arrival/contact is demonstrated. A failed native render leaves its log in the new output directory and returns nonzero. Correct the error and choose a fresh directory.

To verify all manifest-listed hashes and append the original twelve collections in a fresh process:

```sh
/path/to/blender --background --factory-startup --disable-autoexec \
  --python-exit-code 1 --python verify_library.py
```

This append-only verification does not render. For provenance, hashes and validation scope, see `MANIFEST.json` and `ASSET-CATALOG.json`. The `.blend` files originated from the procedural generators with Blender 4.5.14; the new toolkit does not rebuild or replace those libraries.

## Licenses and release boundary

Original procedural scripts, generated people/prop libraries and generic proof preview: MIT, see `LICENSE`. Unity flipbook textures: **CC0-1.0**, see `textures/fire-cc0/CC0-1.0.txt` and its manifest. These terms are not interchangeable. Installed fonts/Pillow/Blender are runtime dependencies, not bundled assets; use appropriately licensed fonts. See `THIRD_PARTY_NOTICES.md`.

No third-party character models/data, packed production `.blend`, chapter-specific source, storyboard, narration, audio or video are cleared by this repository. They remain excluded; the generic preview does not lift a source-model release hold.
