import hashlib,json,runpy
from pathlib import Path
R=Path(__file__).resolve().parent
F=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
read=runpy.run_path(str(R/'export-neutral.py'))['read_png']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads((R/'art024-mask-definition.json').read_text());mask={tuple(q) for q in cfg['maskCoordinatesXY']};roots={tuple(q) for q in cfg['fixedRootCoordinatesXY']}
a=read(R/'art024-neutral-A.png')[2]
assert sha(R/'art024-neutral-A.png')=='e2f90c5dc97a24b9dc7714776d575fafe56791b9dc568e03f152b111badbe6c8'
def occ(r):return {(x,y) for y in range(104) for x in range(96) if r[y][4*x+3]}
def comps(points,diagonal=True):
    rem=set(points);result=[]
    steps=[(dx,dy) for dx in [-1,0,1] for dy in [-1,0,1] if (dx or dy) and (diagonal or abs(dx)+abs(dy)==1)]
    while rem:
        stack=[rem.pop()];c=set(stack)
        while stack:
            x,y=stack.pop()
            for dx,dy in steps:
                q=x+dx,y+dy
                if q in rem:rem.remove(q);stack.append(q);c.add(q)
        result.append(c)
    return sorted(result,key=len)
def holes(r):
    transparent={(x,y) for y in range(104) for x in range(96)}-occ(r)
    return [c for c in comps(transparent,False) if not any(x in [0,95] or y in [0,103] for x,y in c) and c&mask]
report={'generationCalls':{'B':2,'C':0},'compositeVersions':{'B':2,'C':0},'AApprovedUnchanged':True,'coreFiveDelivered':False,'CAndSmileNotProduced':'B exhausted both attempts without retaining A feather identity; stop, no synthetic fallback','AComponents8':[len(c) for c in comps(occ(a))],'AEditableOpaqueCount':len(occ(a)&mask),'trials':{}}
oldholes=set().union(*holes(a)) if holes(a) else set()
for v in [1,2]:
    f=R/f'art024-B-v{v}-candidate-96.png';w,h,b=read(f)
    assert (w,h)==(96,104) and {k for row in b for k in row[3::4]}=={0,255}
    changed={(x,y) for y in range(104) for x in range(96) if a[y][4*x:4*x+4]!=b[y][4*x:4*x+4]}
    assert changed<=mask and not changed&roots
    cc=comps(occ(b));small=[sorted(c) for c in cc[:-1]]
    entry={'sha256':sha(f),'changedPixelsVsA':len(changed),'maskOutsideRgbaDiff':0,'fixedRootsRgbaDiff':0,'headFaceBodyFeetProtected':True,'editableOpaqueCount':len(occ(b)&mask),'AOriginalOpaqueCleared':len((occ(a)-occ(b))&mask),'components8':[len(c) for c in cc],'isolatedComponentsXY':small,'newClosedTransparentComponents4XY':[sorted(c) for c in holes(b) if not c<=oldholes],'formatPass':True,'visualPass':False,'reason':('wing pixels mostly lost; isolated blocks' if v==1 else 'three-feather identity lost, shortened and over-raised instead of gentle lift')}
    report['trials'][str(v)]=entry
    p=R/f'art024-B-v{v}-report.json';d=json.loads(p.read_text());d['visualGate']='FAIL: '+entry['reason'];p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
assert all(sha(Path(f))==s for f,s in cfg['formalProtectedSHA'].items())
manifest=json.loads((F/'manifest.json').read_bytes())
(R/'art024-formal-manifest.json').write_bytes((F/'manifest.json').read_bytes())
report['formal17SHAUnchanged']=True
report['idleTimingsUnchanged']={n:sum(f['durationMs'] for f in manifest['actions'][n]['frames']) for n in ['idle-soft','idle-smile']}
report['releaseEntryEnds']={n:{'first':f[0],'last':f[-1],'durationMs':sum(q['durationMs'] for q in f)} for n,f in manifest['actions']['drag-release']['entrySequences'].items()}
assert len(report['releaseEntryEnds'])==16
(R/'art024-check-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='releaseEntryEnds'},indent=2))
