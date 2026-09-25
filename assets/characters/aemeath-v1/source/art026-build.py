"""Decode explicit two-cell source; preserve A; reuse identical generated wing pixels."""
import hashlib,json,runpy
from pathlib import Path
R=Path(__file__).resolve().parent;F=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
p=runpy.run_path(str(R/'export-neutral.py'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
protected={str(f):sha(f) for f in [F/'manifest.json',*sorted((F/'frames').glob('*.png'))]}
cfg=json.loads((R/'art023-mask-definition.json').read_text());mask={tuple(q) for q in cfg['maskCoordinatesXY']};roots={tuple(q) for q in cfg['fixedRootCoordinatesXY']}
(R/'art026-wing-mask-v1.png').write_bytes((R/'art023-mask-v1.png').read_bytes())
(R/'art026-mask-definition.json').write_text(json.dumps({'maskCoordinatesXY':sorted(mask),'fixedRootCoordinatesXY':sorted(roots),'source':'unchanged ART023 semantic mask','maskSHA':sha(R/'art026-wing-mask-v1.png')},indent=2)+'\n',encoding='utf-8')
A=R/'art026-neutral-A.png';assert sha(A)=='e2f90c5dc97a24b9dc7714776d575fafe56791b9dc568e03f152b111badbe6c8'
base=p['read_png'](A)[2]
source=R/'art026-BC-v3-source.png';w,h,raw=p['read_png'](source)
assert (w,h)==(1536,1024) and h%2==0
core=R/'art026-core';core.mkdir(exist_ok=True);(core/'neutral.png').write_bytes(A.read_bytes())
report={'sourceSHA':sha(source),'sourceSize':[w,h],'sourceCells':{'B':[0,0,1536,512],'C':[0,512,1536,1024]},'logicalPlacement':[0,72,96,104],'sampling':'pixel-center nearest each96x32 cell; alpha128; integer offset(0,0); no deformation','generationCalls':3,'compositeVersions':{'B':1,'C':1},'maskSHA':sha(R/'art026-wing-mask-v1.png'),'formalProtectedSHA':protected,'frames':{}}
for index,(pose,n,smile) in enumerate([('B','soft-light','smile-half'),('C','soft-peak','smile-closed')]):
    donor=[bytearray(384) for _ in range(104)]
    for y in range(32):
        for x in range(96):
            q=raw[index*512+(2*y+1)*512//64][(2*x+1)*1536//192*4:(2*x+1)*1536//192*4+4]
            if q[3]>=128:donor[y+72][4*x:4*x+4]=q[:3]+b'\xff'
    p['write_png'](R/f'art026-{pose}-v3-donor-96.png',96,104,donor)
    # Before compositing, source feet are at original y93 and both fixed root cuffs remain opaque.
    footy=max(y for y in range(80,104) for x in range(40,56) if donor[y][4*x+3])
    assert footy==93
    rootAlphaDiff=sum(bool(donor[y][4*x+3])!=bool(base[y][4*x+3]) for x,y in roots)
    out=[bytearray(row) for row in base]
    for x,y in mask:out[y][4*x:4*x+4]=donor[y][4*x:4*x+4]
    p['write_png'](core/f'{n}.png',96,104,out)
    facebase=p['read_png'](F/f'frames/{smile}.png')[2];face=[bytearray(row) for row in facebase]
    for x,y in mask:face[y][4*x:4*x+4]=out[y][4*x:4*x+4]
    p['write_png'](core/f'{smile}.png',96,104,face)
    changes=[(x,y) for y in range(104) for x in range(96) if base[y][4*x:4*x+4]!=out[y][4*x:4*x+4]]
    assert set(changes)<=mask and not set(changes)&roots
    assert all(face[y][4*x:4*x+4]==facebase[y][4*x:4*x+4] for y in range(104) for x in range(96) if (x,y) not in mask)
    assert all(face[y][4*x:4*x+4]==out[y][4*x:4*x+4] for x,y in mask)
    report['frames'][pose]={'candidate':n+'.png','sha256':sha(core/f'{n}.png'),'smile':smile+'.png','smileSHA':sha(core/f'{smile}.png'),'donorSHA':sha(R/f'art026-{pose}-v3-donor-96.png'),'sourceFeetY':footy,'sourceRootAlphaDiff':rootAlphaDiff,'changedVsA':len(changes),'outsideMaskRgbaDiff':0,'fixedRootRgbaDiff':0,'smileOutsideMaskDiffVsFormal':0,'smileWingExactMatch':True,'changedXY':changes}
manifest=json.loads((F/'manifest.json').read_bytes())
timing={n:manifest['actions'][n]['frames'] for n in ['idle-soft','idle-smile']}
(R/'art026-timing.json').write_text(json.dumps(timing,indent=2)+'\n',encoding='utf-8')
assert protected=={f:sha(Path(f)) for f in protected}
report['formalUnchanged']=True;report['AByteIdentical']=True
(R/'art026-build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:({n:{a:b for a,b in q.items() if a!='changedXY'} for n,q in v.items()} if k=='frames' else v) for k,v in report.items() if k!='formalProtectedSHA'},indent=2))
