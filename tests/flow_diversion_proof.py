"""Offline Blender proof; no network, external assets or production imports.
Run: blender -b --factory-startup --disable-autoexec --python-exit-code 1
     --python tests/flow_diversion_proof.py -- --out /fresh/path --lock /shared/lock
"""
from pathlib import Path
import argparse, fcntl, hashlib, json, math, sys
import bpy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--lock', required=True)
    args = ap.parse_args(sys.argv[sys.argv.index('--')+1:])
    lock = open(args.lock, 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('NOT_RUN: render lock busy', flush=True)
        raise SystemExit(73)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'blender'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    from hybrid_stage import material, held_camera, fit_held_camera, camera_signature
    from flow_diversion import FlowDiversion
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.render_aa = '16'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = 'BOTH'
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.threads_mode, scene.render.threads = 'FIXED', 4
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Standard'
    flow = FlowDiversion(material('water', (.18,.62,.57,1)),
                         material('banks', (.58,.47,.23,1)),
                         material('sill', (.20,.21,.23,1)))
    def snapshot():
        return [(o.hide_render, tuple(tuple(v.co) for v in o.data.vertices)) for o in flow.objects]
    for p in [0, .31, .7, .8, 1]:
        flow.update(p); before = snapshot()
        flow.update(1-p, False); flow.update(p)
        assert snapshot() == before
        assert all(math.isfinite(x) for o in flow.objects for v in o.data.vertices for x in v.co)
    invalid = 0
    for p in [-.1, 1.1, float('nan'), float('inf')]:
        try: flow.update(p)
        except ValueError: invalid += 1
    assert invalid == 4
    # Every surface is a single indexed connected strip, not isolated rectangles.
    for mesh in [flow.channel.data, flow.spill.data]:
        adjacency = {v.index:set() for v in mesh.vertices}
        for edge in mesh.edges:
            a,b = edge.vertices; adjacency[a].add(b); adjacency[b].add(a)
        seen, stack = set(), [0]
        while stack:
            v = stack.pop()
            if v in seen: continue
            seen.add(v); stack.extend(adjacency[v]-seen)
        assert len(seen) == len(mesh.vertices)
    flow.update(.69); assert flow.spill.hide_render
    flow.update(1); assert not flow.spill.hide_render
    tip = (flow.spill.data.vertices[-1].co + flow.spill.data.vertices[-2].co)/2
    assert (tip-flow.end).length < 1e-5
    assert flow.label_anchors['normal_outlet'] != flow.label_anchors['landward_overflow']
    camera = held_camera(scene, (7,-12,12), (1,-.5,0))
    fit_held_camera(scene, camera, flow.objects, flow.update,
                    phases=[0,.6,.8,1], safe=(.08,.08,.92,.92))
    signature = camera_signature(camera)
    frames = []
    for i,p in enumerate([0,.6,1]):
        flow.update(p); assert camera_signature(camera)==signature
        path=out/f'flow-{i:02d}.png';scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        assert path.is_file()
        frames.append(dict(file=path.name,phase=p,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    report=dict(engine=scene.render.engine,AA=16,shadows=True,cavity=True,
        resolution=[1280,720],native_frames=frames,
        connected_meshes=2,invalid_inputs_rejected=invalid,
        reverse_seek_geometry='PASS',visibility_restore='PASS',held_camera='PASS',
        final_branch_endpoint='PASS',fluid_simulation=False,
        source_fidelity='NOT_APPLICABLE: generic asset',
        visual_review='NOT_RUN',continuous_motion='NOT_RUN: three native stills',
        source_hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in
            ['blender/flow_diversion.py','blender/hybrid_stage.py','tests/flow_diversion_proof.py']})
    (out/'proof.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)
    lock.close()

if __name__ == '__main__': main()
