"""One coequal list, one shared source, multiple outgoing alternatives.

SPDX-License-Identifier: MIT. Blender 4.5+, original procedural geometry only.
XZ diagram plane, +Z up, view from -Y; all coordinates are common-parent local.
Screen-space text is deliberately returned as metadata, never world-space font data.
"""
import math

from mathutils import Vector

from hybrid_stage import Relation, segment, set_segment


class CoequalGroupFork:
    """An outlined equal-status enumeration with one common stem and fork.

    items: distinct nonempty labels. rows: an exact ordered partition of item
    indices (e.g. ((0, 1, 2), (3, 4))). bounds: (left, bottom, right, top) in XZ.
    junction: (x, 0, z), below the container. targets: two or more distinct
    attachment points below the junction, on caller-owned destination boundaries.

    Both outgoing arrows apply to the WHOLE group, not only the last label row.
    They show alternatives; no exclusivity, causal/necessary/sufficient condition,
    equal probability, or logical AND is encoded. This is not Conjunction.
    Caller must supply the intended wording and separately validate text width.
    """
    def __init__(self, name, items, rows, bounds, junction, targets, mat,
                 warning_mat, parent=None):
        items = tuple(items)
        rows = tuple(tuple(row) for row in rows)
        targets = tuple(Vector(t) for t in targets)
        left, bottom, right, top = bounds
        junction = Vector(junction)
        flat = [i for row in rows for i in row]
        if (not items or any(not isinstance(s, str) or not s.strip() for s in items)
                or len(set(items)) != len(items)):
            raise ValueError('items must be distinct nonempty labels')
        if (not rows or any(not row for row in rows)
                or any(type(i) is not int for i in flat)
                or flat != list(range(len(items)))):
            raise ValueError('rows must partition every item exactly once, in order')
        values = [left, bottom, right, top, *junction, *(v for t in targets for v in t)]
        if not all(math.isfinite(v) for v in values):
            raise ValueError('finite coordinates required')
        if not (left < right and bottom < top and left < junction.x < right
                and abs(junction.y) < 1e-8 and junction.z < bottom):
            raise ValueError('ordered rectangle and a coplanar junction below it required')
        if (len(targets) < 2 or len({tuple(t) for t in targets}) != len(targets)
                or any(abs(t.y) > 1e-8 or t.z >= junction.z for t in targets)):
            raise ValueError('at least two distinct coplanar targets below junction required')
        self.items, self.rows = items, rows
        self.bounds, self.junction, self.targets = tuple(bounds), junction, targets
        self.source = Vector((junction.x, 0, bottom))
        self.outline = []
        corners = [(left, 0, bottom), (right, 0, bottom),
                   (right, 0, top), (left, 0, top)]
        for i in range(4):
            ob = segment(name + ' group boundary', mat, radius=.022, parent=parent)
            set_segment(ob, corners[i], corners[(i + 1) % 4])
            self.outline.append(ob)
        self.stem = segment(name + ' common stem', mat, radius=.025, parent=parent)
        set_segment(self.stem, self.source, junction)
        self.branches = [Relation(name + ' alternative ' + str(i + 1), junction,
                                  target, mat, warning_mat, 'reveal', parent)
                         for i, target in enumerate(targets)]
        self.update(0)

    @property
    def objects(self):
        return self.outline + [self.stem] + [o for r in self.branches for o in r.objects]

    @property
    def label_rows(self):
        """Row item indices/text and centered LOCAL anchors for screen composition.

        Project anchors through the held camera after applying any common parent.
        Container membership is explicit; text fit/occlusion remains caller-owned.
        """
        left, bottom, right, top = self.bounds
        return [{'indices': list(row), 'text': ' / '.join(self.items[i] for i in row),
                 'anchor': [(left + right) / 2, 0,
                            top - (j + .5) * (top - bottom) / len(self.rows)]}
                for j, row in enumerate(self.rows)]

    def update(self, p):
        """Seekable branch reveal; boundary/common stem remain present at all phases."""
        for branch in self.branches:
            branch.update(p)
        return {'group_members': list(self.items),
                'branch_scope': [list(self.items) for _ in self.branches]}
