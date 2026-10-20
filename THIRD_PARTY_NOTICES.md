# Third-party notices

## Unity VFX Image Sequences / Flipbooks

The four image sequences in `textures/fire-cc0/` are by Unity Technologies / Unity Labs Paris and are made available under CC0-1.0. Official announcement: https://unity.com/blog/engine-platform/free-vfx-image-sequences-flipbooks. Exact source archives, source TGA hashes, converted PNG hashes, dimensions, and license evidence are recorded in `textures/fire-cc0/manifest.json`. The legal dedication is copied in `textures/fire-cc0/CC0-1.0.txt`.

These textures are not covered by the repository's MIT license. All other bundled code and procedural people/prop assets are locally authored for this project, as documented in the root manifest.

## Native hybrid toolkit

`blender/hybrid_stage.py`, `blender/demo_hybrid.py` and `run_hybrid_proof.py` contain only original procedural geometry/staging code and generic demonstrations, under the root MIT license. No third-party model, production scene, narration, source text, storyboard, audio or video is incorporated. Existing people/prop libraries and all four Unity textures retain their original notices and hashes.

The proof runner uses a separately installed Korean-capable font supplied by the user and Pillow. Neither font files nor Pillow are bundled. The generic raster preview was rendered using Noto Sans CJK (SIL Open Font License 1.1); it does not contain the font software. Obtain and comply with the license of any font you supply. No third-party character models or unreleased source `.blend` files are included.

## Coequal group/fork helper and proof

`blender/group_fork.py` and `tests/group_fork_proof.py` are original MIT code, generalizing a common outlined multiline list and shared-branch staging pattern. They depend only on the existing original native toolkit, Blender, and (for raster composition) the separately installed Pillow runtime. No production module is copied/imported, no new person/animal model or source scene is bundled, and existing static libraries are unchanged.

`previews/group-fork-contact.png` is an original generic native render with English screen-space labels. This proof uses Pillow's installed default font; no font software or Pillow package is redistributed. Respect the licenses of your installed runtime dependencies. The original MIT code / Unity CC0 texture boundary is unchanged. Third-party animal models/rigs, packed production scenes, book material, storyboards, speech/audio/video, credentials and private paths remain excluded; rendering permission is not source redistribution clearance.
