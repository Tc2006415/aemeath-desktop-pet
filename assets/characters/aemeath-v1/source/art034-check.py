from pathlib import Path
import runpy,json,hashlib,re
R=Path(__file__).resolve().parent
read=runpy.run_path(str(R/'art032-png.py'))['read_png']
mask=json.loads((R/'art034-mask.json').read_text(encoding='utf-8-sig'))
mouth=set(map(tuple,mask['mouthXY']));symbol=set(map(tuple,mask['symbolXY']));allowed=mouth|symbol
px=lambda r,x,y:bytes(r[y][x*4:x*4+4])
protected=json.loads((R/'art034-protection.json').read_text(encoding='utf-8-sig'))
for p,digest in protected.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,p
stats={};annoyed=[]
for f in sorted((R/'art034-frames').glob('*.png')):
 w,h,rows=read(f);assert (w,h)==(96,104)
 assert {p for row in rows for p in row[3::4]}<={0,255}
 oldname=f.name.replace('transition-','annoyed-');base=R/'art033-frames'/oldname
 _,_,old=read(base)
 changes={(x,y) for y in range(h) for x in range(w) if px(rows,x,y)!=px(old,x,y)}
 if f.name.startswith('annoyed-'):
  assert changes<=allowed
  assert all(px(rows,x,y)[3]==px(old,x,y)[3] for x,y in mouth)
  glyph={(x,y) for x,y in symbol if px(rows,x,y)[3]}
  opaque={(x,y) for y in range(h) for x in range(w) if px(old,x,y)[3]}
  assert all(px(old,x,y)[3]==0 for x,y in symbol)
  clearance=min(max(abs(x-a),abs(y-b)) for x,y in glyph for a,b in opaque)
  assert clearance>=7 and len(glyph)==16
  assert all(px(rows,x,y)[0]>px(rows,x,y)[1] and px(rows,x,y)[2]>px(rows,x,y)[1] for x,y in glyph)
  signature=[px(rows,x,y).hex() for x,y in sorted(allowed)];annoyed.append(signature)
  stats[f.name]={'changed':len(changes),'mouth':len(changes&mouth),'glyph':len(glyph),'clearance':clearance}
 else:
  assert not changes and f.read_bytes()==base.read_bytes()
  assert all(px(rows,x,y)[3]==0 for x,y in symbol)
assert len(annoyed)==4 and all(x==annoyed[0] for x in annoyed)
assert len(list((R/'art034-frames').glob('*.png')))==19
assert (R/'art034-timing.json').read_bytes()==(R/'art033-timing.json').read_bytes()
html=(R/'art034-demo.html').read_text(encoding='utf-8');m=re.search(r'const images=(.*?),oldImages=(.*?),\$=id=>',html)
new,old=map(json.loads,m.groups());assert len(new)==len(old)==64 and set(new)==set(old)
assert all(new[k]==old[k] for k in new if not k.startswith('pose:annoyed-'))
print(json.dumps({'protectedFiles':len(protected),'outsideMaskChanges':0,'frames':19,'changedFrames':stats,'previewKeys':64},indent=2))
