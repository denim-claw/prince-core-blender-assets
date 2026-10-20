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

## Coequal multiline group → shared alternatives

`blender/group_fork.py` adds **one** bounded helper, `CoequalGroupFork`: a complete rectangular group, one common stem and two or more outgoing reveal arrows. Unlike `Conjunction` (many required inputs → one output), this represents **one equal-status list → multiple alternatives**. Both branches apply to every list member, including the upper line of a wrapped label. It asserts neither exclusivity nor causation, necessity, sufficiency or equal probability. Keep those meanings in explicit scene-specific wording.

```python
from group_fork import CoequalGroupFork
fork = CoequalGroupFork(
    "Shared list", ("Alpha", "Beta", "Gamma", "Delta", "Epsilon"),
    rows=((0, 1, 2), (3, 4)), bounds=(-2.6, .5, 2.6, 1.8),
    junction=(0, 0, -.15), targets=((-2, 0, -1.65), (2, 0, -1.65)),
    mat=teal, warning_mat=red)
fork.update(1)
# fork.label_rows returns text, exhaustive item indices and LOCAL row anchors.
# Project anchors through the held camera and composite text in screen space.
```

Use XZ, +Z up, view from -Y, with an optional common parent. Rows must partition distinct nonempty items exactly once in original order. The junction is below the container and targets below the junction. Supply target points **on destination boundaries**, not node centers. The helper does not create destination nodes, import fonts or auto-fit text; caller-owned composition must check width, occlusion and meaning. Original `Human`-style anatomy/gait is already covered by `Actor`, so no second person implementation or replacement static library is added.

Run the new generic proof (Python 3/Pillow, no externally supplied font needed):

```sh
python tests/group_fork_proof.py \
  --blender /path/to/blender \
  --lock /path/to/shared-render.lock \
  --out /path/to/fresh-group-proof
```

The launcher uses the same nonblocking shared-lock policy as the original proof below (busy exit 73, no output directory). It produces four native 1280×720 Workbench AA16 PNGs at phases 0, .45, 1, .45, screen-space English labels and reports. Tests reject eight malformed memberships/layouts without leaving geometry, check all five members, closed boundary/common stem, both actual arrow tips attached to visible destination sphere tops under a translated parent, sampled bounds, frozen camera and reverse-seek transforms. The repeated phase has zero decoded RGB difference on the tested machine (PNG hashes can differ due to metadata); start-to-settled mean pixel difference is 1.015333839699074. `tests/group-fork-proof-summary.json` and `previews/group-fork-contact.png` preserve the measured record. One full-size settled frame was visually checked; this is **not** continuous-animation, source-fidelity, reading-time or user aesthetic approval. Existing six-frame hybrid regressions also ran unchanged.

## Connected flow and residual overflow

`blender/flow_diversion.py` provides `FlowDiversion(water_material, bank_material,
sill_material)`: a single indexed L-shaped inlet/turn/outlet plus a separately
connected landward branch over a lowered bank. Call `update(p, visible=True)` with
finite `p` in [0,1]. Normal drainage and overflow have distinct `label_anchors` for
caller-owned screen-space labels. Reverse seeks restore geometry and visibility.
Import does not clear the caller's scene. Requires only Blender and `hybrid_stage.py`.

This is a fixed-layout kinematic illustration, **not fluid simulation**, flood-risk
estimation, or proof of tree contact. No book text, chapter scenes, audio, models or
private production paths are included. The three native stills in
`previews/flow-diversion-contact.png` are a technical preview, not visual approval.

```sh
blender -b --factory-startup --disable-autoexec --python-exit-code 1 \
  --python tests/flow_diversion_proof.py -- \
  --out /path/to/fresh-flow-proof --lock /path/to/shared-render.lock
```

The actual isolated-copy proof rendered 1280x720 Workbench AA16 with shadows/cavity,
checked both indexed mesh components, rejected four invalid phase values, and
verified reverse-seek geometry, visibility restoration, held camera and spill-end
placement. Its measured report is `tests/flow-diversion-proof-summary.json`.
Continuous motion and independent visual review were not run.

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
