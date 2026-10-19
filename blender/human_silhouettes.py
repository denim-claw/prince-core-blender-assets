"""Reusable minimal human silhouette assets for Machiavelli chapter scenes.

Blender 4.5+; coordinate convention: local +Z up, local -Y toward camera.
Original procedural geometry, no external model dependency. This is a clean visual
asset, not a motion-capture rig. See README.md for roles, scale and limitations.
"""
import bpy, math
from mathutils import Vector

WHITE=(.88,.91,.92,1.0)
BLACK=(.025,.032,.038,1.0)
CROWN=(.55,.41,.16,1.0)


def _mat(name, color):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=color
    m.use_nodes=True
    nodes=m.node_tree.nodes; nodes.clear()
    e=nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value=color
    out=nodes.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(e.outputs[0],out.inputs['Surface'])
    return m


def _mesh(name, verts, faces, material, collection):
    mesh=bpy.data.meshes.new(name+'Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    ob=bpy.data.objects.new(name,mesh); collection.objects.link(ob); return ob


def _capsule(name, a, b, radius, material, collection, sides=12):
    """Create a tapered, rounded-looking limb segment between local-space points."""
    a,b=Vector(a),Vector(b); axis=(b-a).normalized(); u=axis.cross(Vector((0,1,0)))
    if u.length<1e-5: u=axis.cross(Vector((1,0,0)))
    u.normalize(); v=axis.cross(u).normalized()
    verts=[]
    for center,r in ((a,radius*.88),(a.lerp(b,.12),radius),(a.lerp(b,.88),radius*.82),(b,radius*.58)):
        for i in range(sides):
            q=center+r*(math.cos(i*math.tau/sides)*u+math.sin(i*math.tau/sides)*v); verts.append(tuple(q))
    faces=[]
    for ring in range(3):
        for i in range(sides):
            j=(i+1)%sides; faces.append((ring*sides+i,ring*sides+j,(ring+1)*sides+j,(ring+1)*sides+i))
    faces.extend([tuple(reversed(range(sides))),tuple(range(3*sides,4*sides))])
    return _mesh(name,verts,faces,material,collection)


def create_person(collection, name='Person', role='ordinary', tone='white', scale=1.0):
    """Create a recognizably human, minimally marked figure, ~2 Blender units tall.

    role: ordinary | ruler | soldier. Only ruler gets a small crown; ordinary and
    soldier get a single narrow belt. `tone` is white or black. Returns root Empty.
    Meshes are named and collected for later rigging/material overrides.
    """
    if role not in {'ordinary','ruler','soldier'}: raise ValueError('unknown role '+role)
    if tone not in {'white','black'}: raise ValueError('tone must be white or black')
    body=_mat('Silhouette '+tone,WHITE if tone=='white' else BLACK)
    beltmat=_mat('Role cue belt '+tone,BLACK if tone=='white' else WHITE)
    crownmat=_mat('Role cue crown',CROWN)
    root=bpy.data.objects.new(name+' root',None); collection.objects.link(root); root.scale=(scale,)*3
    def parent(ob): ob.parent=root; return ob
    # Torso, shoulder bridge and neck are restrained, connected anatomical masses.
    parent(_capsule(name+' torso',(0,0,.83),(0,0,1.48),.235,body,collection,16))
    parent(_capsule(name+' shoulder line',(-.29,0,1.43),(.29,0,1.43),.12,body,collection,12))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=(0,0,1.79))
    head=bpy.context.object; head.name=name+' head'; head.scale=(.175,.16,.205); head.data.materials.append(body)
    for c in list(head.users_collection): c.objects.unlink(head)
    collection.objects.link(head); parent(head)
    # Legs separated clearly at silhouette scale; feet rest at z=0.
    for side in (-1,1):
        x=side*.115
        parent(_capsule(name+f' leg {side}',(x,0,.88),(side*.16,0,.08),.105,body,collection,12))
        parent(_capsule(name+f' foot {side}',(side*.16,0,.09),(side*.16,-.20,.075),.09,body,collection,12))
        parent(_capsule(name+f' arm {side}',(side*.25,0,1.42),(side*.31,-.02,.88),.085,body,collection,12))
        parent(_capsule(name+f' hand {side}',(side*.31,-.02,.9),(side*.31,-.025,.77),.065,body,collection,10))
    if role in {'ordinary','soldier'}:
        belt=_mesh(name+' simple belt',[(-.20,-.55,.98),(.20,-.55,.98),(.20,-.55,1.06),(-.20,-.55,1.06)],[(0,1,2,3)],beltmat,collection);belt.parent=root
    if role=='ruler':
        # Tiny, readable three-point crown; no robe, jewelry or armor.
        _mesh(name+' small crown', [(-.17,-.01,1.97),(.17,-.01,1.97),(-.17,-.01,2.12),(-.055,-.01,2.04),(0,-.01,2.15),(.055,-.01,2.04),(.17,-.01,2.12)],
              [(0,1,6,5,4,3,2)],crownmat,collection).parent=root
    root['asset_role']=role; root['asset_tone']=tone; root['asset_scale_height']=2.15*scale
    return root


def create_role_set(collection, prefix='Prince', tone='white', scale=1.0):
    """Create reusable ruler, citizen and soldier collections under one parent."""
    result={}
    for role in ('ruler','ordinary','soldier'):
        sub=bpy.data.collections.new(prefix+' '+role.title()); collection.children.link(sub)
        result[role]=create_person(sub,prefix+' '+role.title(),role,tone,scale)
    return result
