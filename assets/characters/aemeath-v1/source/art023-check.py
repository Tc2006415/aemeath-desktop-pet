"""Verify preservation/format separately from failed visual acceptance."""
import hashlib,json,runpy
from pathlib import Path
R=Path(__file__).resolve().parent
read=runpy.run_path(str(R/'export-neutral.py'))['read_png']
cfg=json.loads((R/'art023-mask-definition.json').read_text())
mask={tuple(q) for q in cfg['maskCoordinatesXY']}; roots={tuple(q) for q in cfg['fixedRootCoordinatesXY']}
base=read(R/'art023-original-neutral.png')[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def opaque(rows):return {(x,y) for y in range(104) for x in range(96) if rows[y][4*x+3]}
def components(points):
    rem=set(points); out=[]
    while rem:
        stack=[rem.pop()]; component=[]
        while stack:
            x,y=stack.pop();component.append((x,y))
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    q=x+dx,y+dy
                    if q in rem:rem.remove(q);stack.append(q)
        out.append(len(component))
    return sorted(out)
report={'imagegenCalls':2,'totalCompositeVersions':2,'distinctSemanticMasks':1,'visualGate':'FAIL both attempts; not selected; stop at cap','candidates':{}}
for v in [1,2]:
    f=R/f'art023-v{v}-candidate-96.png';w,h,r=read(f)
    assert (w,h)==(96,104)
    assert {q for row in r for q in row[3::4]}=={0,255}
    changed={(x,y) for y in range(104) for x in range(96) if r[y][4*x:4*x+4]!=base[y][4*x:4*x+4]}
    assert changed<=mask and not changed&roots
    assert all(78<=y<=99 and (8<=x<=35 or 60<=x<=87) for x,y in changed)
    assert all(r[y]==base[y] for y in range(78))
    assert all(r[y][31*4:65*4]==base[y][31*4:65*4] for y in range(104))
    report['candidates'][str(v)]={'sha256':sha(f),'changedPixels':len(changed),'outsideSemanticMaskRgbaDiff':0,'fixedRootsRgbaDiff':0,'headFaceBodyHandsFeetProtected':True,'anchor':[48,94],'components8':components(opaque(r)),'newOpaqueAboveRootBottom':sorted((opaque(r)-opaque(base))&{(x,y) for x in range(96) for y in range(78,85)}),'sourceFile':f'art023-v{v}-source.png','donorFile':f'art023-v{v}-donor-96.png','formatPass':True,'visualPass':False}
    old=json.loads((R/f'art023-v{v}-report.json').read_text());old['visualAcceptance']='FAIL: root junction protrudes; inner feather still vertical; not selected'
    (R/f'art023-v{v}-report.json').write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8')
assert all(sha(Path(f))==s for f,s in cfg['formalProtectedSHA'].items())
report['formal17FilesUnchanged']=True
(R/'art023-check-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
