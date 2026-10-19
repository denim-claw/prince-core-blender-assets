# Prince Core Blender Assets

Reusable, lightweight Blender assets for narrated explainers. This repository contains only original procedural people/prop generators and their native `.blend` outputs, plus Unity's separately licensed CC0 fire/smoke flipbooks. It does **not** include any third-party animal models, chapter-specific source assets, narration, video, credentials, or private production data.

## Contents

- `blender/prince-core-people.blend` — six static human silhouettes: white/black ruler, ordinary person, soldier. Rulers have a small crown; ordinary/soldiers have a contrasting belt.
- `blender/prince-core-props.blend` — agreement sheet, net, veil, gate, house, snare. Symbolic starter props; stage them to fit the actual source action.
- `blender/human_silhouettes.py`, `blender/narrative_props.py` — original procedural Blender Python generators.
- `blender/append_assets.py` — append a named collection from a `.blend` library.
- `previews/` — actual 1280×720 contact sheets for the people and props.
- `textures/fire-cc0/` — four Unity CC0 flipbook atlases and exact license/manifest.

## Use

Requires Blender 4.5+. In a Blender Python script:

```python
import sys
sys.path.insert(0, "/path/to/this-repository/blender")
from append_assets import append_collection
people = append_collection("/path/to/this-repository/blender/prince-core-people.blend", "White Ruler")
props = append_collection("/path/to/this-repository/blender/prince-core-props.blend", "Net")
```

The six people and six prop collections use local origins. Human meshes are static and unrigged: they are not appropriate for natural walking or complex interaction without a separately validated rig. Contact sheets are indexes, not finished scene designs. Keep each shot's camera fixed; change framing at hard cuts only.

For provenance, build instructions, hashes and validation scope, see `MANIFEST.json` and `ASSET-CATALOG.json`. Regenerate the `.blend` files from the scripts with Blender 4.5.14. Re-run `verify_library.py` after every rebuild.

## Licenses

Original procedural scripts and generated people/prop libraries: MIT, see `LICENSE`.
Unity flipbook textures: CC0-1.0, see `textures/fire-cc0/CC0-1.0.txt` and its manifest. License terms are not interchangeable. No other third-party material is included.
