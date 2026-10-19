import bpy, json, sys
from pathlib import Path
root=Path(__file__).resolve().parent
kit=root/'blender'
sys.path.insert(0,str(kit))
from append_assets import append_collection
expected={
 'prince-core-people.blend':{'White Ruler','White Ordinary','White Soldier','Black Ruler','Black Ordinary','Black Soldier'},
 'prince-core-props.blend':{'Agreement','Net','Veil','Gate','House','Snare'},
}
result={}
for filename,names in expected.items():
 path=kit/filename; imported=[]
 for name in sorted(names):
  c=append_collection(str(path),name)
  assert c is not None
  imported.append(c.name)
 assert set(imported)==names,(filename,imported)
 result[filename]={'collections':imported,'status':'PASS'}
print('FRESH_FACTORY_APPEND='+json.dumps(result))
