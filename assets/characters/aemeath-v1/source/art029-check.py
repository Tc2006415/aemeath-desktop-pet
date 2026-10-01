from pathlib import Path
import runpy,json,hashlib,base64,re
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'export-neutral.py'));load=lambda f:io['read_png'](f)[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();cfg=json.loads((R/'art029-mask.json').read_text());mask=set(map(tuple,cfg['coordinatesXY']));roots=set(map(tuple,cfg['fixedConnectionsXY']));report={}
for f in (R/'art029-frames').glob('*.png'):
 key,pose=f.stem.rsplit('-',1);base=load(R/'art028-frames'/(key+'.png'));w,h,r=io['read_png'](f);assert(w,h)==(96,104) and f.read_bytes()[24:26]==bytes([8,6]);assert{q[i] for q in r for i in range(3,384,4)}=={0,255}
 assert all(r[y][4*x:4*x+4]==base[y][4*x:4*x+4] for y in range(104) for x in range(96) if(x,y)not in mask)
 if pose=='base':assert f.read_bytes()==(R/'art028-frames'/(key+'.png')).read_bytes()
 occupied={q for q in mask|roots if r[q[1]][q[0]*4+3]};reached=occupied&roots;stack=list(reached)
 while stack:
  x,y=stack.pop()
  for dx in [-1,0,1]:
   for dy in [-1,0,1]:
    q=x+dx,y+dy
    if q in occupied and q not in reached:reached.add(q);stack.append(q)
 assert occupied<=reached
 edge=[]
 for x in [34,35,36,37,38,57,58,59,60,61]:
  before=max(y for y in range(86,93) if base[y][4*x+3]);after=max(y for y in range(86,93) if r[y][4*x+3]);edge.append(before-after)
 assert all(0<=d<=2 for d in edge),edge
 report[f.name]={'sha256':sha(f),'outsideHemDiff':0,'connectionIntact':True,'columnLiftPx':edge}
for f,d in json.loads((R/'art029-protection.json').read_text()).items():assert sha(Path(f))==d
html=(R/'art029-demo.html').read_text(encoding='utf-8');images=json.loads(re.search(r'const images=(.*);',html)[1]);assert len(images)==45
for n,u in images.items():assert base64.b64decode(u.split(',')[1])==(R/'art029-frames'/(n+'.png')).read_bytes()
assert (R/'art028-engine.js').read_text(encoding='utf-8-sig') in html
assert (R/'art029-track.js').read_text(encoding='utf-8-sig') in html
(R/'art029-check-report.json').write_text(json.dumps({'status':'PASS','frames':report,'protectedInputsUnchanged':True,'originalEngineUnchanged':True},indent=2),encoding='utf-8');print('PASS45 PNGs:format/CRC/alpha,hem-only,connected ends,0..2px lifts,original inputs+engine,HTML bytes')
