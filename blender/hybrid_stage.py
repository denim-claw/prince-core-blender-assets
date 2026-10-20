"""Small native explainer toolkit. Original procedural code; SPDX-License-Identifier: MIT.

Blender 4.5+, +Z up, -Y front. No imports from a production build, models or fonts.
Actors are articulated primitive meshes, NOT skinned rigs or foot-lock IK.
Relations accept local coordinates under an optional common parent.
"""
import math

import bpy
from mathutils import Vector


def ease(p, start=0.12, end=0.72):
    if end <= start:
        raise ValueError('end must exceed start')
    q = max(0.0, min(1.0, (p - start) / (end - start)))
    return q * q * (3 - 2 * q)


def material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = color
    m.use_nodes = True
    node = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    node.inputs['Base Color'].default_value = color
    node.inputs['Roughness'].default_value = 0.85
    return m


def _sphere(name, location, scale, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8)
    ob = bpy.context.object
    ob.name, ob.parent = name, parent
    ob.location, ob.scale = location, scale
    ob.data.materials.append(mat)
    for polygon in ob.data.polygons:
        polygon.use_smooth = True
    return ob


def segment(name, mat, radius=0.035, parent=None):
    """Unit-depth mesh: its two cap centers are exactly local z=-.5 and +.5."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=1)
    ob = bpy.context.object
    ob.name, ob.parent = name, parent
    ob.data.materials.append(mat)
    return ob


def set_segment(ob, a, b):
    """Place a unit-depth segment without cumulative scale or orientation errors."""
    a, b = Vector(a), Vector(b)
    d = b - a
    ob.location = (a + b) / 2
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler() if d.length else (0, 0, 0)
    ob.scale = (1, 1, d.length)
    ob.hide_render = d.length < 1e-8


class Relation:
    """Pure seekable reveal/intact/break/require/blocked/compare connector.

    require uses three dashes, explicitly no arrowhead. Both outer dash endpoints
    attach at q=1 (unlike evenly spaced dashes ending short of the destination).
    break starts intact, removes the middle and exposes an X. blocked never reaches
    its destination. a/b may change on every update, e.g. moving node anchors.
    """
    MODES = {'reveal', 'intact', 'break', 'require', 'blocked', 'compare'}

    def __init__(self, name, a, b, mat, warning_mat, mode='reveal', parent=None):
        if mode not in self.MODES:
            raise ValueError('unknown relation mode: ' + mode)
        self.a, self.b, self.mode = Vector(a), Vector(b), mode
        self.parts = [segment(name + ' shaft', mat, parent=parent) for _ in range(3)]
        self.cross = [segment(name + ' interruption', warning_mat, parent=parent) for _ in range(2)]
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=.10, depth=.24)
        self.head = bpy.context.object
        self.head.name, self.head.parent = name + ' direction', parent
        self.head.data.materials.append(mat)
        self.update(0)

    @property
    def objects(self):
        return self.parts + self.cross + [self.head]

    def update(self, p, a=None, b=None):
        if a is not None:
            self.a = Vector(a)
        if b is not None:
            self.b = Vector(b)
        a, b = self.a, self.b
        d = b - a
        if d.length < 1e-6:
            raise ValueError('relation endpoints must differ')
        q = 1.0 if self.mode in {'intact', 'break'} else ease(p)
        for ob in self.objects:
            # Reset even hidden parts: seek determinism includes inactive geometry.
            ob.location, ob.rotation_euler, ob.scale = (0, 0, 0), (0, 0, 0), (1, 1, 1)
            ob.hide_render = True
        intervals = [(0, q)]
        broken = self.mode == 'break' and ease(p, .38, .67) > .05
        if self.mode == 'break':
            intervals = [(0, .43), (.57, 1)] if broken else [(0, 1)]
        elif self.mode == 'require':
            intervals = [(lo, min(q, hi)) for lo, hi in ((0, .27), (.365, .635), (.73, 1)) if q > lo]
        elif self.mode == 'blocked':
            intervals = [(0, min(q, .43))]
        for ob, (lo, hi) in zip(self.parts, intervals):
            set_segment(ob, a + d * lo, a + d * hi)
        mid = (a + b) / 2
        # Cross is in the XZ diagram plane; intended for frontal abstract stages.
        for ob, sign in zip(self.cross, (-1, 1)):
            set_segment(ob, mid + Vector((-.12, -.05, sign * .12)),
                        mid + Vector((.12, -.05, -sign * .12)))
            ob.hide_render = not (broken or (self.mode == 'blocked' and q >= .43))
        self.head.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        self.head.location = a + d * q - d.normalized() * .12
        self.head.hide_render = self.mode in {'require', 'blocked', 'compare'} or q < .1
        return {'q': q, 'broken': broken, 'blocked': self.mode == 'blocked'}


class Conjunction:
    """Two or more required inputs joined to an output; NOT sufficient permission.

    Coordinates are attachment points, not node centers. Keep the explicit qualifier
    in the screen-space labels. No permission arrows are created.
    """
    def __init__(self, name, inputs, junction, output, mat, warning_mat):
        if len(inputs) < 2:
            raise ValueError('conjunction needs at least two inputs')
        self.links = [Relation(name + ' input', a, junction, mat, warning_mat, 'require') for a in inputs]
        self.links.append(Relation(name + ' output', junction, output, mat, warning_mat, 'require'))

    @property
    def objects(self):
        return [ob for link in self.links for ob in link.objects]

    def update(self, p):
        for link in self.links:
            link.update(p)


class Actor:
    """Adult-proportioned procedural figure with shoulder pivots and posed legs.

    pose() overwrites every driven transform (reverse-seek safe). Gait is symbolic;
    no armature, skin, grasp solver, natural gait or world-space foot lock.
    """
    def __init__(self, name, mat, accent):
        self.root = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(self.root)
        self.arms, self.legs = [], []
        for part, loc, size in (
            ('torso', (0, 0, 1.16), (.24, .135, .34)),
            ('pelvis', (0, 0, .91), (.20, .13, .15)),
            ('head', (0, 0, 1.65), (.115, .105, .15)),
            ('neck', (0, 0, 1.45), (.06, .06, .09)),
        ):
            _sphere(name + ' ' + part, loc, size, mat, self.root)
        _sphere(name + ' belt', (0, 0, .96), (.208, .14, .028), accent, self.root)
        for side in (-1, 1):
            pivot = bpy.data.objects.new(name + ' shoulder', None)
            bpy.context.scene.collection.objects.link(pivot)
            pivot.parent, pivot.location = self.root, (side * .255, 0, 1.34)
            _sphere(name + ' arm', (0, 0, -.28), (.063, .065, .28), mat, pivot)
            self.arms.append((side, pivot))
            upper = _sphere(name + ' thigh', (0, 0, 0), (.078, .08, .22), mat, self.root)
            lower = _sphere(name + ' calf', (0, 0, 0), (.06, .065, .22), mat, self.root)
            foot = _sphere(name + ' foot', (0, 0, 0), (.085, .14, .055), mat, self.root)
            self.legs.append((side, upper, lower, foot))
        self.pose()

    def pose(self, location=(0, 0, 0), turn=0.0, walk=0.0, gesture=0.0):
        self.root.location, self.root.rotation_euler = location, (0, 0, turn)
        for side, pivot in self.arms:
            pivot.rotation_euler = (-.30 * math.sin(walk) * side, -side * gesture, 0)
        for side, upper, lower, foot in self.legs:
            phase = walk + (math.pi if side < 0 else 0)
            fy = .19 * math.cos(phase) if walk else -.015
            fz = .055 + (.10 * max(0, math.sin(phase)) if walk else 0)
            hip, ankle = Vector((side * .105, 0, .89)), Vector((side * .105, fy, fz + .035))
            delta = ankle - hip
            knee = (hip + ankle) / 2 + Vector((0, -math.sqrt(max(0, .435**2 - (delta.length / 2)**2)), 0))
            for ob, a, b in ((upper, hip, knee), (lower, knee, ankle)):
                ob.location = (a + b) / 2
                ob.scale.z = (b - a).length / 2 + .025
                ob.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
            foot.location = (side * .105, fy - .045, fz)


def held_camera(scene, location, target):
    data = bpy.data.cameras.new('held camera')
    camera = bpy.data.objects.new('held camera', data)
    scene.collection.objects.link(camera)
    data.type = 'ORTHO'
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = camera
    return camera


def camera_signature(camera):
    return [*camera.location, *camera.rotation_euler, camera.data.ortho_scale, camera.data.lens]


def fit_held_camera(scene, camera, objects, update, phases=(0, .25, .5, .75, 1),
                    safe=(.08, .19, .92, .80)):
    """Fit one orthographic camera to sampled motion bounds, then leave it frozen.

    safe=(left,bottom,right,top) in normalized image coordinates. Reserves header,
    footer and side room; not a continuous-motion proof or automatic label solver.
    Supply all meaningful extrema, exclude ground explicitly, use square pixels.
    """
    left, bottom, right, top = safe
    if not (0 <= left < right <= 1 and 0 <= bottom < top <= 1):
        raise ValueError('invalid safe rectangle')
    if camera.data.type != 'ORTHO':
        raise ValueError('orthographic camera required')
    if camera.data.sensor_fit == 'VERTICAL' or camera.data.shift_x or camera.data.shift_y:
        raise ValueError('unshifted AUTO/HORIZONTAL camera required')
    if scene.render.pixel_aspect_x != scene.render.pixel_aspect_y:
        raise ValueError('square pixels required')
    rotation = camera.rotation_euler.to_matrix()
    inv = rotation.transposed()
    samples = []
    for p in phases:
        update(p)
        bpy.context.view_layer.update()
        for ob in objects:
            if ob.type == 'MESH' and not ob.hide_render:
                samples.extend(inv @ (ob.matrix_world @ Vector(c)) for c in ob.bound_box)
    if not samples:
        raise ValueError('no visible mesh bounds')
    xmin, xmax = min(v.x for v in samples), max(v.x for v in samples)
    ymin, ymax = min(v.y for v in samples), max(v.y for v in samples)
    aspect = scene.render.resolution_x / scene.render.resolution_y
    # Blender ortho_scale spans the wider dimension for landscape sensor AUTO.
    if aspect < 1:
        raise ValueError('landscape or square render required')
    width = max((xmax - xmin) / (right - left),
                (ymax - ymin) * aspect / (top - bottom)) * 1.04
    camera.data.ortho_scale = max(width, .01)
    local = inv @ camera.location
    local.x = (xmin + xmax) / 2 - ((left + right) / 2 - .5) * width
    local.y = (ymin + ymax) / 2 - ((bottom + top) / 2 - .5) * width / aspect
    camera.location = rotation @ local
    bpy.context.view_layer.update()
    return camera_signature(camera)
