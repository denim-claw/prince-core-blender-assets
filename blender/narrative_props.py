"""Reusable original simple props for Prince XV/XVII/XVIII. +Z up; factories return roots."""
import bpy, math
from mathutils import Vector

def mat(name,rgba,alpha=None):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=rgba;m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba;p.inputs['Roughness'].default_value=.85
 if alpha is not None:p.inputs['Alpha'].default_value=alpha;m.surface_render_method='DITHERED'
 return m
def root(c,n,loc):o=bpy.data.objects.new(n,None);c.objects.link(o);o.location=loc;return o
def cube(c,n,loc,size,material,parent):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for x in list(o.users_collection):x.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(material);o.parent=parent;return o
def rod(c,n,a,b,r,material,parent):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
 for x in list(o.users_collection):x.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(material);o.parent=parent;return o
def make_agreement(c,location=(0,0,0)):
 r=root(c,'Agreement document',location);paper=mat('Paper gray',(.72,.73,.70,1));ink=mat('Ink',(.08,.09,.10,1));cube(c,'Document',(0,0,.08),(1.25,.08,.85),paper,r)
 for z in (.28,.14,0,-.14):cube(c,'Text stroke',(0,-.052,z),(.62,.012,.018),ink,r)
 return r
def make_net(c,location=(0,0,0),width=1.8,height=1.45):
 r=root(c,'Simple net',location);cord=mat('Net cord',(.20,.22,.22,1));n=8
 for i in range(n+1):
  x=-width/2+width*i/n;rod(c,'Net vertical',(x,0,0),(x,0,height),.012,cord,r);z=height*i/n;rod(c,'Net horizontal',(-width/2,0,z),(width/2,0,z),.012,cord,r)
 return r
def make_veil(c,location=(0,0,0),width=1.1,height=1.7):
 r=root(c,'Plain disguise veil',location);cloth=mat('Veil neutral',(.62,.65,.66,1),.42)
 xs=[-width/2,-width/4,0,width/4,width/2];zs=[height,height*.54,height*.15,height*.52,height];verts=[]
 for row in range(4):
  t=row/3
  for i,x in enumerate(xs):verts.append((x,-.07*math.sin(t*math.pi),height*(1-t)+zs[i]*t))
 faces=[]
 for row in range(3):
  for i in range(4):a=row*5+i;faces.append((a,a+1,a+6,a+5))
 mesh=bpy.data.meshes.new('Draped veil mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(cloth);o=bpy.data.objects.new('Plain draped veil',mesh);c.objects.link(o);o.parent=r;return r
def make_gate(c,location=(0,0,0),width=2.5,height=2.5):
 r=root(c,'Plain gate',location);stone=mat('Gate neutral stone',(.30,.32,.33,1))
 for x in (-width/2,width/2):cube(c,'Gate post',(x,0,height/2),(.18,.2,height),stone,r)
 cube(c,'Gate lintel',(0,0,height),(width+.18,.2,.18),stone,r);return r
def make_house(c,location=(0,0,0),width=2.4,depth=1.8,height=1.8):
 r=root(c,'Plain house',location);wall=mat('House neutral',(.34,.36,.37,1));roof=mat('Roof muted',(.23,.25,.26,1));cube(c,'House body',(0,0,height/2),(width,depth,height),wall,r);front=mat('Door and window shadow',(.10,.12,.13,1));cube(c,'Plain door',(0,-depth/2-.025,.48),(.38,.035,.9),front,r)
 for x in (-.63,.63):cube(c,'Plain window',(x,-depth/2-.03,1.25),(.32,.035,.28),front,r)
 for s in (-1,1):o=cube(c,'Roof panel',(s*width/4,0,height+.28),(width*.76,depth*1.18,.12),roof,r);o.rotation_euler.y=s*.42
 return r
def make_snare(c,location=(0,0,0),radius=.45):
 r=root(c,'Plain snare',location);cord=mat('Snare dark cord',(.13,.15,.16,1));bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.025,major_segments=32,minor_segments=8);o=bpy.context.object;o.name='Snare loop';o.rotation_euler.x=math.pi/2
 for x in list(o.users_collection):x.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(cord);o.parent=r;rod(c,'Snare stake',(-radius,-.05,0),(radius,-.05,.28),.025,cord,r);return r
