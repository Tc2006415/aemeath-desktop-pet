import base64,hashlib,json,re,runpy
from pathlib import Path
R=Path(__file__).resolve().parent
io=runpy.run_path(str(R/'export-neutral.py'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads((R/'art026-mask-definition.json').read_text());mask=set(map(tuple,cfg['maskCoordinatesXY']));roots=set(map(tuple,cfg['fixedRootCoordinatesXY']))
build=json.loads((R/'art026-build-report.json').read_text());core=R/'art026-core'; frames={}
for f in sorted(core.glob('*.png')):
 w,h,rows=io['read_png'](f);assert (w,h)==(96,104) and f.read_bytes()[24:26]==bytes([8,6]);assert {r[i] for r in rows for i in range(3,384,4)}=={0,255}
 frames[f.stem]={(x,y):bytes(rows[y][4*x:4*x+4]) for y in range(h) for x in range(w)}
assert len(frames)==5 and sha(core/'neutral.png')=='e2f90c5dc97a24b9dc7714776d575fafe56791b9dc568e03f152b111badbe6c8'
A=frames['neutral'];report={'frames':{},'formalUnchanged':True}
def components(points,diagonal):
 todo=set(points);out=[];ds=[(a,b) for a in (-1,0,1) for b in (-1,0,1) if (a or b) and (diagonal or abs(a)+abs(b)==1)]
 while todo:
  seed=todo.pop();group={seed};stack=[seed]
  while stack:
   x,y=stack.pop()
   for dx,dy in ds:
    q=x+dx,y+dy
    if q in todo:todo.remove(q);group.add(q);stack.append(q)
  out.append(group)
 return out
window={(x,y) for y in range(76,98) for x in range(7,89)}
def holes(frame):
 return [c for c in components({q for q in window if not frame[q][3]},False) if not any(x in (7,88) or y in (76,97) for x,y in c)]
baseholes=set().union(*holes(A)) if holes(A) else set()
basecomponents=components({q for q,p in A.items() if p[3]},True)
for n in ('soft-light','soft-peak'):
 f=frames[n];changes={q for q in A if A[q]!=f[q]};assert changes<=mask and not changes&roots
 comps=components({q for q,p in f.items() if p[3]},True)
 newisolated=[c for c in comps if c&mask and not any(c&b and b-mask for b in basecomponents)]
 newholes=[c for c in holes(f) if not c<=baseholes]
 report['frames'][n]={'changed':len(changes),'newIsolatedComponents':[sorted(c) for c in newisolated],'newClosedHoles':[sorted(c) for c in newholes],'sha256':sha(core/(n+'.png'))}
 assert not newisolated
 # Four-neighbour alpha pinholes are review findings, not hidden or silently repaired.
F=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
for n,wing in [('smile-half','soft-light'),('smile-closed','soft-peak')]:
 rows=io['read_png'](F/'frames'/(n+'.png'))[2]
 assert all(frames[n][q]==frames[wing][q] for q in mask)
 assert all(frames[n][(x,y)]==bytes(rows[y][4*x:4*x+4]) for x,y in A if (x,y) not in mask)
for path,digest in build['formalProtectedSHA'].items():assert sha(Path(path))==digest
html=(R/'art026-demo.html').read_text(encoding='utf-8');m=re.search(r'const images=(.*?),timing=(.*?);\n',html);images=json.loads(m[1]);timing=json.loads(m[2]);formal=json.loads((F/'manifest.json').read_bytes())
for k,folder in [('new',core),('old',F/'frames')]:
 for n,uri in images[k].items():assert base64.b64decode(uri.split(',')[1])==(folder/(n+'.png')).read_bytes()
for n,total in [('idle-soft',1400),('idle-smile',1200)]:
 assert timing[n]==formal['actions'][n]['frames'];assert sum(f['durationMs'] for f in timing[n])==total
 assert timing[n][0]['path']==timing[n][-1]['path']=='frames/neutral.png'
report.update({'AByteIdentical':True,'maskProtection':True,'smileWingExact':True,'rawEmbeddedPngs':10,'cycleMs':[1400,1200],'loopSeamSameA':True,'nativeAcceptance':False,'reviewStatus':'first draft with four-neighbour single-pixel alpha gaps; not production acceptance'})
(R/'art026-check-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
