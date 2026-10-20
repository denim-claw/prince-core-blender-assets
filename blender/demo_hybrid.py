"""Native generic proof + assertions; run with the repository's run_hybrid_proof.py.

SPDX-License-Identifier: MIT. No chapter/source/narration dependencies.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hybrid_stage import (Actor, Conjunction, Relation, _sphere, camera_signature,
                          ease, fit_held_camera, held_camera, material)
from narrative_props import cube, make_house


def transform_signature(objects):
    return [(o.name, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale), o.hide_render)
            for o in objects]


def connector_tests(mat, warning):
    """Settled actual cap-center and tip tests; no visual inference from names."""
    errors = []
    links = []
    for mode in sorted(Relation.MODES):
        link = Relation('test ' + mode, (-2, 0, 0), (2, 0, 1), mat, warning, mode)
        links.append(link)
        # Non-monotonic seeking with dynamically changing attachment points.
        for p in (0, .5, 1, .25, 1):
            a, b = Vector((-2, 0, p)), Vector((2 + p, 0, 1))
            link.update(p, a, b)
            first = transform_signature(link.objects)
            link.update(1 - p)
            link.update(p, a, b)
            assert first == transform_signature(link.objects), mode
        bpy.context.view_layer.update()
        visible = [ob for ob in link.parts if not ob.hide_render]
        caps = [(ob.matrix_world @ Vector((0, 0, -.5)),
                 ob.matrix_world @ Vector((0, 0, .5))) for ob in visible]
        errors.append((caps[0][0] - link.a).length)
        if mode != 'blocked':
            errors.append((caps[-1][1] - link.b).length)
        if mode == 'require':
            assert len(caps) == 3 and link.head.hide_render
            assert (caps[1][0] - caps[0][1]).length > .1
        if mode == 'break':
            assert len(caps) == 2 and not link.cross[0].hide_render
            assert (caps[1][0] - caps[0][1]).length > .1
            link.update(0)
            assert len([o for o in link.parts if not o.hide_render]) == 1
        if mode == 'blocked':
            assert (caps[-1][1] - link.b).length > 1 and link.head.hide_render
        if mode in {'reveal', 'intact', 'break'}:
            link.update(1)
            bpy.context.view_layer.update()
            errors.append((link.head.matrix_world @ Vector((0, 0, .12)) - link.b).length)
    conjunction = Conjunction('test both', [(-2, 0, 1), (-2, 0, -1)], (0, 0, 0), (2, 0, 0), mat, warning)
    conjunction.update(1)
    bpy.context.view_layer.update()
    for link in conjunction.links:
        errors.append((link.parts[-1].matrix_world @ Vector((0, 0, .5)) - link.b).length)
        assert link.head.hide_render
    assert max(errors) < 2e-6, errors
    for ob in [o for link in links for o in link.objects] + conjunction.objects:
        bpy.data.objects.remove(ob, do_unlink=True)
    return {'modes': sorted(Relation.MODES), 'max_endpoint_error': max(errors),
            'moving_anchors_reverse_seek': 'PASS', 'conjunction_attachment': 'PASS'}


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.render_aa = '16'
    shading = scene.display.shading
    shading.light, shading.color_type = 'STUDIO', 'MATERIAL'
    shading.show_shadows = shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.show_specular_highlight = False
    shading.background_type, shading.background_color = 'VIEWPORT', (.025, .028, .032)
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.threads_mode, scene.render.threads = 'FIXED', 4
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.view_settings.view_transform = 'Standard'
    return scene


def render_shot(out, kind, report):
    scene = setup()
    white = material('ivory', (.86, .87, .85, 1))
    teal = material('connection', (.18, .62, .57, 1))
    red = material('interruption', (.65, .19, .18, 1))
    dark = material('ground', (.08, .09, .10, 1))
    if kind == 'abstract':
        report['connector_tests'] = connector_tests(teal, red)
        nodes = [(-4, 0, 1.7), (4, 0, 1.7), (-4, 0, -.4), (-4, 0, -1.8), (0, 0, -1.1), (4, 0, -1.1)]
        for i, point in enumerate(nodes):
            _sphere('concept', point, (.16, .10, .16), white)
        bond = Relation('trust link', (-3.8, 0, 1.7), (3.8, 0, 1.7), teal, red, 'break')
        both = Conjunction('required conditions', [(-3.8, 0, -.4), (-3.8, 0, -1.8)],
                           (0, 0, -1.1), (3.8, 0, -1.1), teal, red)
        def update(p):
            bond.update(p)
            both.update(p)
        labels = [('신뢰', (-4, 0, 2.25)), ('협력', (4, 0, 2.25)),
                  ('자료 확보', (-4, 0, .12)), ('내용 확인', (-4, 0, -2.36)),
                  ('모두 필요', (0, 0, -.5)), ('검토', (4, 0, -.5))]
        camera = held_camera(scene, (0, -20, 0), (0, 0, 0))
        fit_extra = [Vector(p) for _, p in labels]
        # Include label anchors in fit as small visible node-sized proxy bounds.
        proxies = [_sphere('label fit proxy', p, (.55, .01, .18), white) for p in fit_extra]
        focal = [o for o in scene.objects if o.type == 'MESH']
        signature = fit_held_camera(scene, camera, focal, update, safe=(.12, .24, .88, .77))
        for ob in proxies:
            bpy.data.objects.remove(ob, do_unlink=True)
        labels_for = lambda p: labels + [('연결 유지' if p < .4 else '연결 단절', (0, 0, 2.25))]
        title = '추상 관계 · 직접 이름으로 표시'
        footer = '조건은 모두 필요 · 충분조건이나 허가를 뜻하지 않음'
    else:
        actor = Actor('Visitor', white, teal)
        house = make_house(scene.collection, location=(2, .7, 0))
        ground = cube(scene.collection, 'ground', (0, 0, -.12), (30, 20, .24), dark, None)
        def update(p):
            q = ease(p)
            actor.pose((-3 + 1.7 * q, -.8, 0), turn=1.1,
                       walk=q * 10 if 0 < q < 1 else 0, gesture=.55 * ease(p, .65, .95))
        camera = held_camera(scene, (0, -18, 9), (0, 0, 1))
        focal = [o for o in scene.objects if o.type == 'MESH' and o != ground]
        signature = fit_held_camera(scene, camera, focal, update, phases=tuple(i / 20 for i in range(21)))
        labels_for = lambda p: [('방문자', (-3 + 1.7 * ease(p), -.8, 2.15)), ('집', (2, .7, 2.95))]
        title, footer = '구체 행동 · 사람이 집으로 접근', '관절형 절차 메시 · 자연 보행이나 접촉 IK 아님'
        update(.35)
        bpy.context.view_layer.update()
        thigh = actor.legs[0][1]
        pos_a = thigh.matrix_world @ thigh.data.vertices[0].co
        local_a = thigh.matrix_local @ thigh.data.vertices[0].co
        update(.65)
        bpy.context.view_layer.update()
        displacement = (thigh.matrix_world @ thigh.data.vertices[0].co - pos_a).length
        local_displacement = (thigh.matrix_local @ thigh.data.vertices[0].co - local_a).length
        assert displacement > .1 and local_displacement > .001
        report['actor_vertex_displacement'] = displacement
        report['actor_limb_local_displacement'] = local_displacement
    objects = [o for o in scene.objects if o.type in {'MESH', 'EMPTY'}]
    for p in (0, .25, .5, .75, 1):
        update(p)
        sig = transform_signature(objects)
        update(1 - p)
        update(p)
        assert sig == transform_signature(objects), (kind, p)
    rows = []
    for index, p in enumerate((0, .5, 1)):
        update(p)
        bpy.context.view_layer.update()
        # Do the real traversal before the repeated callback probe (closure safety).
        bounds = []
        for ob in objects:
            if ob.type != 'MESH' or ob.hide_render or ob.name == 'ground':
                continue
            projected = [world_to_camera_view(scene, camera, ob.matrix_world @ Vector(c)) for c in ob.bound_box]
            box = [min(v.x for v in projected), min(v.y for v in projected),
                   max(v.x for v in projected), max(v.y for v in projected)]
            assert box[0] > .04 and box[2] < .96 and box[1] > .12 and box[3] < .88, (ob.name, box)
            bounds.append({'object': ob.name, 'box': box})
        saved = transform_signature(objects)
        update(1 - p)
        update(p)
        bpy.context.view_layer.update()
        assert saved == transform_signature(objects)
        assert camera_signature(camera) == signature
        projected_labels = []
        for text, point in labels_for(p):
            xy = world_to_camera_view(scene, camera, Vector(point))
            projected_labels.append({'text': text, 'xy': [xy.x * 1280, (1 - xy.y) * 720]})
        path = out / f'{kind}-{index}.png'
        scene.camera = camera
        scene.render.filepath = str(path)
        start = time.monotonic()
        bpy.ops.render.render(write_still=True)
        rows.append({'file': path.name, 'phase': p, 'seconds': time.monotonic() - start,
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'labels': projected_labels,
                     'title': title, 'footer': footer, 'bounds': bounds})
    report[kind] = {'camera_signature': signature, 'transform_determinism': 'PASS', 'frames': rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.out.mkdir(parents=True, exist_ok=True)
    report = {'blender': bpy.app.version_string, 'engine': 'BLENDER_WORKBENCH',
              'dimensions': [1280, 720], 'AA': 16, 'shadows': True, 'cavity': True,
              'audio': False, 'scope': 'six sampled stills; not continuous-animation or full-user QA'}
    for kind in ('abstract', 'concrete'):
        render_shot(args.out, kind, report)
    (args.out / 'native-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print('HYBRID_NATIVE_PASS ' + json.dumps(report['connector_tests']))


if __name__ == '__main__':
    main()
