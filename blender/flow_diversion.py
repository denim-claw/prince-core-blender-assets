"""Connected diversion and distinct landward overflow, original MIT geometry.

Extracted/adapted from an original native explainer implementation. No production
imports, narration, book data, fonts or external models. Fixed illustrative layout
in world XYZ (+Z up), not a fluid solver or a quantitative flood-protection model.
Caller owns the scene/camera and screen-space labels. Import never clears a scene.
"""
import math
import bpy
from mathutils import Vector
from hybrid_stage import ease


def _mesh(name, count, material):
    data = bpy.data.meshes.new(name)
    data.from_pydata([(0, 0, 0)] * (count * 2), [],
                     [(2*i, 2*i+1, 2*i+3, 2*i+2) for i in range(count-1)])
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.modifiers.new('illustrative thickness', 'SOLIDIFY').thickness = .07
    return obj


def _box(name, xyz, size, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz)
    obj = bpy.context.object
    obj.name, obj.scale = name, size
    obj.data.materials.append(material)
    return obj


class FlowDiversion:
    """One connected L channel plus a separate branch across a lowered bank.

    update(p, visible=True): finite normalized p in [0,1], pure/reverse seekable.
    Normal downstream exit is NOT the landward spill. Channel fills before spill.
    label_anchors returns world points for caller's screen-space composition.
    Does not depict buildings, damage, risk probabilities or contact mechanics.
    """
    def __init__(self, water_material, bank_material, sill_material):
        self.channel = _mesh('connected inlet turn and outlet', 33, water_material)
        self.spill = _mesh('separate landward overflow', 25, water_material)
        self.banks = [
            _box('outer bank', (1.1, -2.9, .08), (5.1, .16, .24), bank_material),
            _box('inner bank before sill', (.185, -2.05, .08), (3.67, .20, .24), bank_material),
            _box('inner bank after sill', (3.265, -2.05, .08), (.97, .20, .24), bank_material),
            _box('lowered crossing', (2.40, -2.05, .015), (.76, .20, .10), sill_material),
        ]
        self.start = Vector((2.40, -2.48, .225))
        self.elbow = Vector((2.40, -1.92, .225))
        self.end = Vector((4.05, -.44, .13))
        self.objects = [self.channel, self.spill, *self.banks]
        self.update(0)

    @property
    def label_anchors(self):
        return {'inlet': (-1.25, 1.6, .22),
                'normal_outlet': (3.7, -2.48, .22),
                'landward_overflow': (2.4, -2.02, .23)}

    def update(self, p, visible=True):
        if not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError('finite normalized phase in [0,1] required')
        inlet, outlet = ease(p, .15, .32), ease(p, .32, .75)
        right, left = -1.45 + .475 * max(.015, inlet), -1.50
        level = .17 + .05 * ease(p, .15, .70)
        pairs = []
        for j in range(16):
            y = 1.8 - (1.8 + 2.155) * j / 16
            pairs.append(((right, y), (left, y)))
        pairs.append(((right, -2.155), (left, -2.805)))
        end = max(right + .015, -1.24 + 4.94 * outlet)
        for j in range(1, 17):
            pairs.append(((right+(end-right)*j/16, -2.155),
                          (left+(end-left)*j/16, -2.805)))
        for j, pair in enumerate(pairs):
            for side, (x, y) in enumerate(pair):
                self.channel.data.vertices[2*j+side].co = (
                    x, y, level + .018 * math.sin(j*.65-p*12))
        self.channel.data.update()
        q = ease(p, .70, .90)
        for j in range(25):
            u = j / 24 * q
            if u < .36:
                center = self.start.lerp(self.elbow, u/.36)
                across = Vector((.34, 0, 0))
            else:
                center = self.elbow.lerp(self.end, (u-.36)/.64)
                across = Vector((.24, -.24, 0))
            for side, sign in [(0, -1), (1, 1)]:
                self.spill.data.vertices[2*j+side].co = center + across * sign
        self.spill.data.update()
        for obj in self.objects:
            obj.hide_render = not visible
        self.spill.hide_render = not visible or p < .70
