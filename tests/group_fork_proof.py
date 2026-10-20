"""Offline native group/fork regression; no private scene, fonts, source or audio.

SPDX-License-Identifier: MIT. Run with Python 3/Pillow and explicit Blender/lock/out.
The same file is invoked in a clean factory-startup Blender process for geometry.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native(out):
    import bpy
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    sys.path.insert(0, str(ROOT / 'blender'))
    from group_fork import CoequalGroupFork
    from hybrid_stage import _sphere, camera_signature, held_camera, material

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.render_aa = '16'
    shading = scene.display.shading
    shading.light, shading.color_type = 'STUDIO', 'MATERIAL'
    shading.show_shadows = shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.background_type, shading.background_color = 'VIEWPORT', (.025, .028, .032)
    scene.view_settings.view_transform = 'Standard'
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.threads_mode, scene.render.threads = 'FIXED', 4
    ivory = material('boundary', (.86, .87, .85, 1))
    teal = material('alternatives', (.18, .62, .57, 1))
    red = material('warning', (.65, .19, .18, 1))
    spec = dict(name='Shared list', items=('Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon'),
                rows=((0, 1, 2), (3, 4)), bounds=(-2.6, .5, 2.6, 1.8),
                junction=(0, 0, -.15), targets=((-2, 0, -1.65), (2, 0, -1.65)),
                mat=teal, warning_mat=red)
    rejected = 0
    for bad in ({'rows': ((0, 1, 2), (4,))}, {'rows': ((0, 1, 2), (2, 3, 4))},
                {'rows': ((0, 1, 2), ())}, {'targets': ((0, 0, -2),)},
                {'targets': ((0, 0, -2), (0, 0, -2))},
                {'junction': (0, 0, 1)}, {'bounds': (-2, 1, 2, 0)},
                {'targets': ((-2, 1, -2), (2, 0, -2))}):
        before = len(bpy.data.objects)
        try:
            CoequalGroupFork(**{**spec, **bad})
        except ValueError:
            rejected += 1
        else:
            raise AssertionError(('invalid spec accepted', bad))
        assert len(bpy.data.objects) == before, 'invalid constructor left geometry'
    parent = bpy.data.objects.new('common parent', None)
    scene.collection.objects.link(parent)
    parent.location = (.25, .3, .1)
    group = CoequalGroupFork(**spec, parent=parent)
    # Caller-owned destination nodes: each target is exactly the top surface point.
    markers = [_sphere('destination', target + Vector((0, 0, -.12)),
                       (.12, .08, .12), ivory, parent) for target in group.targets]
    assert len(group.outline) == 4 and len(group.branches) == 2
    assert [i for row in group.label_rows for i in row['indices']] == list(range(5))
    for row in group.label_rows:
        x, y, z = row['anchor']
        assert -2.6 < x < 2.6 and .5 < z < 1.8 and y == 0
    camera = held_camera(scene, (.25, -20, 0), (.25, 0, 0))
    camera.data.ortho_scale = 9
    signature = camera_signature(camera)

    def snap():
        return [(tuple(o.location), tuple(o.rotation_euler), tuple(o.scale), o.hide_render)
                for o in group.objects]

    def cap(ob, sign):
        return ob.matrix_world @ Vector((0, 0, sign * .5))

    errors = []
    for p in (0, .45, .78, .98, 1, .2, 1):
        state = group.update(p)
        assert state['branch_scope'] == [list(group.items)] * 2
        a = snap()
        group.update(1 - p)
        group.update(p)
        assert a == snap(), 'reverse seek differs'
        bpy.context.view_layer.update()
        errors += [(cap(group.stem, -1) - parent.matrix_world @ group.source).length,
                   (cap(group.stem, 1) - parent.matrix_world @ group.junction).length]
        for i in range(4):
            errors.append((cap(group.outline[i], 1) - cap(group.outline[(i + 1) % 4], -1)).length)
        if p >= .78:
            for branch, target, marker in zip(group.branches, group.targets, markers):
                errors += [(cap(branch.parts[0], -1) - cap(group.stem, 1)).length,
                           (cap(branch.parts[0], 1) - parent.matrix_world @ target).length,
                           (marker.matrix_world @ Vector((0, 0, 1)) - parent.matrix_world @ target).length,
                           (branch.head.matrix_world @ Vector((0, 0, .12))
                            - parent.matrix_world @ target).length]
                assert not branch.head.hide_render
    assert max(errors) < 2e-6, errors
    labels = []
    for row in group.label_rows:
        v = world_to_camera_view(scene, camera, parent.matrix_world @ Vector(row['anchor']))
        labels.append({'text': row['text'], 'xy': [v.x * 1280, (1 - v.y) * 720]})
    for text, pos in zip(('Option A', 'Option B'), group.targets):
        v = world_to_camera_view(scene, camera, parent.matrix_world @ (pos + Vector((0, 0, -.4))))
        labels.append({'text': text, 'xy': [v.x * 1280, (1 - v.y) * 720]})
    frames = []
    for i, p in enumerate((0, .45, 1, .45)):
        group.update(p)
        bpy.context.view_layer.update()
        assert camera_signature(camera) == signature
        for ob in group.objects + markers:
            if not ob.hide_render:
                for corner in ob.bound_box:
                    v = world_to_camera_view(scene, camera, ob.matrix_world @ Vector(corner))
                    assert .04 < v.x < .96 and .12 < v.y < .9, (ob.name, tuple(v))
        path = out / ('native-%02d.png' % i)
        scene.render.filepath = str(path)
        start = time.monotonic()
        bpy.ops.render.render(write_still=True)
        frames.append({'file': path.name, 'phase': p, 'sha256': sha(path),
                       'seconds': time.monotonic() - start})
    report = {'status': 'PASS', 'blender': bpy.app.version_string,
              'engine': scene.render.engine, 'AA': 16, 'resolution': [1280, 720],
              'shadows': True, 'cavity': True, 'items': list(group.items),
              'rows': [list(r) for r in group.rows], 'branch_scope': state['branch_scope'],
              'rejected_invalid_specs': rejected, 'max_endpoint_error': max(errors),
              'reverse_transform_seek': 'PASS', 'sampled_bounds': 'PASS',
              'camera_signature': signature, 'frames': frames, 'labels': labels}
    (out / 'native-report.json').write_text(json.dumps(report, indent=2))


def compose(out):
    from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
    report = json.loads((out / 'native-report.json').read_text())
    font = ImageFont.load_default(size=30)
    frames = []
    images = []
    for entry in report['frames']:
        path = out / entry['file']
        assert sha(path) == entry['sha256']
        with Image.open(path) as src:
            src.load()
            image = src.convert('RGB')
        assert image.size == (1280, 720)
        images.append(image.copy())
        draw = ImageDraw.Draw(image)
        labels = [{'text': 'One coequal list / shared alternatives', 'xy': [640, 45]},
                  *report['labels'], {'text': 'Generic sampled proof - no source text', 'xy': [640, 675]}]
        boxes = []
        for label in labels:
            box = draw.textbbox(label['xy'], label['text'], font=font, anchor='mm', stroke_width=1)
            assert 20 < box[0] < box[2] < 1260 and 10 < box[1] < box[3] < 710
            for other in boxes:
                assert box[2] <= other[0] or other[2] <= box[0] or box[3] <= other[1] or other[3] <= box[1]
            boxes.append(box)
            draw.text(label['xy'], label['text'], font=font, anchor='mm', fill='white')
        target = out / ('labelled-' + path.name)
        image.save(target)
        with Image.open(target) as decoded:
            decoded.load()
        frames.append({'file': target.name, 'phase': entry['phase'], 'sha256': sha(target), 'text_boxes': boxes})
    delta = sum(ImageStat.Stat(ImageChops.difference(images[0], images[2])).mean) / 3
    repeat = sum(ImageStat.Stat(ImageChops.difference(images[1], images[3])).mean) / 3
    assert delta > .1 and repeat < .01, (delta, repeat)
    contact = Image.new('RGB', (1280, 720))
    for i, entry in enumerate(frames):
        with Image.open(out / entry['file']) as image:
            contact.paste(image.resize((640, 360), Image.Resampling.LANCZOS), ((i % 2) * 640, (i // 2) * 360))
    contact.save(out / 'contact-sheet.png')
    report.update({'composed_frames': frames, 'start_settled_pixel_delta': delta,
                   'reverse_rerender_pixel_delta': repeat,
                   'contact_sha256': sha(out / 'contact-sheet.png'),
                   'source_sha256': {p: sha(ROOT / p) for p in ('blender/group_fork.py', 'tests/group_fork_proof.py', 'blender/hybrid_stage.py')},
                   'limits': ['four sampled stills (one repeated phase), not continuous animation',
                              'group membership and attachment tested, not source fidelity or causal logic',
                              'no automatic font fit/occlusion solver; caller supplies labels/targets',
                              'no full-user/aesthetic/phone reading-time approval']})
    (out / 'proof-report.json').write_text(json.dumps(report, indent=2))
    print('GROUP_FORK_PROOF_PASS ' + json.dumps({'native_frames': len(frames), 'invalid_specs_rejected': report['rejected_invalid_specs'],
                                               'max_endpoint_error': report['max_endpoint_error'], 'pixel_delta': delta, 'repeat_delta': repeat}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', type=Path)
    parser.add_argument('--lock', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--native', action='store_true', help=argparse.SUPPRESS)
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)
    if args.native:
        native(args.out)
        return 0
    if args.blender is None or args.lock is None:
        parser.error('--blender and --lock required')
    import fcntl
    with args.lock.open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('RENDER_NOT_RUN: shared lock busy', file=sys.stderr)
            return 73
        if args.out.exists():
            parser.error('choose a fresh output directory')
        args.out.mkdir(parents=True)
        command = [str(args.blender.resolve()), '--background', '--factory-startup', '--disable-autoexec',
                   '--python-exit-code', '1', '--python', str(Path(__file__).resolve()), '--', '--native', '--out', str(args.out.resolve())]
        with (args.out / 'blender.log').open('w') as log:
            rc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
        if rc:
            print('NATIVE_FAILED: inspect blender.log', file=sys.stderr)
            return rc
        compose(args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
