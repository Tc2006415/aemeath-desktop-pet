"""ART-012: fixed-canvas conversion and explicit lower-wing-only composites."""
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
basepath=ROOT/'art011-package/frames/hold-half.png'
_,_,base=png['read_png'](basepath)
def occupied(rows):
    return {(x,y) for y in range(104) for x in range(96) if rows[y][x*4+3]}
def bounds(points):
    return [min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)] if points else None
def wingmetrics(rows):
    points=occupied(rows)
    result={}
    for side in ['left','right']:
        p={(x,y) for x,y in points if y>=78 and (x<=23 if side=='left' else x>=72)}
        extreme=min(x for x,y in p) if side=='left' else max(x for x,y in p)
        tips={(x,y) for x,y in p if x<=extreme+1} if side=='left' else {(x,y) for x,y in p if x>=extreme-1}
        result[side]={'outerWingBounds':bounds(p),'outermostTwoColumnsTipBounds':bounds(tips),'tipMeanY':round(sum(y for x,y in tips)/len(tips),3)}
    return result
mask=set()
for y in range(78,103):
    hi=23 if y<=84 else 26 if y<=88 else 30
    for lx in range(4,hi+1):
        for x in (lx,95-lx):
            r,g,b,a=base[y][x*4:x*4+4]
            assert not (r>130 and r>g*1.2 and b>g*1.12), 'Mask must not cover baseline pink hair'
            mask.add((x,y))
mr=[bytearray(384) for _ in range(104)]
for x,y in mask:mr[y][x*4:x*4+4]=b'\xff\xff\xff\xff'
png['write_png'](ROOT/'art012-wing-mask-v1.png',96,104,mr)
protected=[ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png')),*sorted((ROOT/'art011-package').rglob('*.png')),ROOT/'art011-package/manifest.json']
before={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report={'base':str(basepath.relative_to(ROOT)),'baseSha256':sha(basepath),'anchor':[48,94],'baseWingMetrics':wingmetrics(base),'maskVersion':1,'maskRule':'left x4..23/y78..84, x4..26/y85..88, x4..30/y89..102; mirrored x->95-x. Entire central x31..64 and y<78 immutable. No baseline pink pixel permitted.','maskCoordinatesXY':sorted(mask,key=lambda p:(p[1],p[0])),'sources':{},'protectedHashes':before}
for name in ['up-v1','up-v2','down-v1','down-v2']:
    source=ROOT/f'art012-{name}-source.png'
    if not source.exists():continue
    w,h,raw=png['read_png'](source)
    assert (w,h)==(1205,1306)
    donor=[bytearray(384) for _ in range(104)]
    clipped=0
    for y in range(104):
        for x in range(96):
            p=raw[(2*y+1)*h//208][(2*x+1)*w//192*4:(2*x+1)*w//192*4+4]
            if p[3]<128:continue
            if y+5>=104:clipped+=1
            else:donor[y+5][x*4:x*4+4]=p[:3]+b'\xff'
    png['write_png'](ROOT/f'art012-{name}-donor.png',96,104,donor)
    entry={'sourceSha256':sha(source),'sourceSize':[w,h],'sampling':'pixel-center nearest96x104, alpha128, integer offset(0,+5)','clippedOpaqueSamples':clipped}
    report['sources'][name]=entry
    if name=='up-v1':
        entry['status']='rejected: huge upward angle and roots raised to hair; retained source/donor only, not clipped into usable candidate'
        continue
    if clipped:
        entry['status']='rejected: conversion would crop opaque pixels'
        continue
    out=[bytearray(r) for r in base]
    for x,y in mask:out[y][x*4:x*4+4]=donor[y][x*4:x*4+4]
    dest=ROOT/f'art012-{name}-96.png'
    png['write_png'](dest,96,104,out)
    changed={(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4]!=base[y][x*4:x*4+4]}
    old,new=occupied(base),occupied(out)
    assert changed and not changed-mask
    assert not any(y<78 or 31<=x<=64 for x,y in changed)
    assert sorted({r[i] for r in out for i in range(3,384,4)})==[0,255]
    assert dest.stat().st_size<=262144
    margins={'left':min(x for x,y in new),'right':95-max(x for x,y in new),'top':min(y for x,y in new),'bottom':103-max(y for x,y in new)}
    entry.update({'status':'candidate pending visual review','outputSha256':sha(dest),'bytes':dest.stat().st_size,'size':[96,104],'alpha':[0,255],'changedPixels':len(changed),'outsideMaskRgbaChanges':len(changed-mask),'oldOpaqueCleared':len(old-new),'newOpaqueAdded':len(new-old),'bounds':bounds(new),'transparentMargins':margins,'wingMetrics':wingmetrics(out),'newDonorOpaqueOutsideOuterWingMaskXY':sorted((occupied(donor)-old)-mask & {(x,y) for y in range(65,104) for x in range(96) if x<=23 or x>=72})})
    print(name,json.dumps({k:v for k,v in entry.items() if k not in ('newDonorOpaqueOutsideOuterWingMaskXY',)}))
assert before=={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report['protectedFilesUnchanged']=True
(ROOT/'art012-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
