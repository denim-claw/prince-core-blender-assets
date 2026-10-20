import bpy, hashlib, json, sys
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'MANIFEST.json').read_text())
checked=0
for section in ('libraries','source_files','previews','fire_assets','verification_files'):
 for name,expected_file in manifest.get(section,{}).items():
  path=root/('textures/fire-cc0/'+name if section=='fire_assets' else name)
  data=path.read_bytes()
  assert len(data)==expected_file['bytes'],path
  assert hashlib.sha256(data).hexdigest()==expected_file['sha256'],path
  checked+=1
print('MANIFEST_HASHES_PASS='+str(checked))
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
