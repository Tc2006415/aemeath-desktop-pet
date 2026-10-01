"""Single in-between wing trial; existing mask, imagegen donor, no procedural posing."""
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:png['read_png'](p)[2]
basepath=ROOT/'art013-package/frames/hold-half.png'
uppath=ROOT/'art013-package/frames/hold-up-half.png'
base,up=load(basepath),load(uppath)
maskpath=ROOT/'art012-wing-mask-v1.png'
mr=load(maskpath)
mask={(x,y) for y in range(104) for x in range(96) if mr[y][x*4+3]}
(ROOT/'art014-mask-v1.png').write_bytes(maskpath.read_bytes())
def occupied(rows):return {(x,y) for y in range(104) for x in range(96) if rows[y][x*4+3]}
def bounds(p):return [min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p)] if p else None
def tips(rows):
    points=occupied(rows)
    result={}
    for side in ['left','right']:
        p={(x,y) for x,y in points if y>=78 and (x<=23 if side=='left' else x>=72)}
        extreme=min(x for x,y in p) if side=='left' else max(x for x,y in p)
        t={(x,y) for x,y in p if x<=extreme+1} if side=='left' else {(x,y) for x,y in p if x>=extreme-1}
        result[side]={'outermostTwoColumnsBounds':bounds(t),'meanY':round(sum(y for x,y in t)/len(t),3)}
    return result
protected=[ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png')),*sorted((ROOT/'art013-package').rglob('*.*'))]
before={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report={'base':str(basepath.relative_to(ROOT)),'baseSha256':sha(basepath),'upperEndpoint':str(uppath.relative_to(ROOT)),'upperSha256':sha(uppath),'maskSource':maskpath.name,'maskSha256':sha(maskpath),'maskVersion':1,'maskCoordinatesXY':sorted(mask,key=lambda p:(p[1],p[0])),'baseTipProxy':tips(base),'upperTipProxy':tips(up),'anchor':[48,94],'candidates':{}}
for version in [1,2]:
    source=ROOT/f'art014-v{version}-source.png'
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
    png['write_png'](ROOT/f'art014-v{version}-donor.png',96,104,donor)
    assert clipped==0
    out=[bytearray(r) for r in base]
    for x,y in mask:out[y][x*4:x*4+4]=donor[y][x*4:x*4+4]
    dest=ROOT/f'art014-v{version}-96.png'
    png['write_png'](dest,96,104,out)
    assert png['read_png'](dest)==(96,104,out), 'PNG CRC / decoded RGBA readback'
    changed={(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4]!=base[y][x*4:x*4+4]}
    assert changed and not changed-mask
    assert all(y>=78 and (x<=30 or x>=65) for x,y in changed)
    assert sorted({r[i] for r in out for i in range(3,384,4)})==[0,255] and dest.stat().st_size<=262144
    old,new=occupied(base),occupied(out)
    metric=tips(out)
    for side in ['left','right']:
        metric[side]['fromBaseY']=round(metric[side]['meanY']-tips(base)[side]['meanY'],3)
        metric[side]['remainingToUpperY']=round(tips(up)[side]['meanY']-metric[side]['meanY'],3)
    entry={'sourceSha256':sha(source),'outputSha256':sha(dest),'size':[96,104],'bytes':dest.stat().st_size,'alpha':[0,255],'sampling':'pixel-center nearest96x104, alpha128, integer offset(0,+5)','clippedOpaqueSamples':clipped,'changedPixels':len(changed),'outsideMaskRgbaChanges':0,'clearedOpaque':len(old-new),'addedOpaque':len(new-old),'bounds':bounds(new),'tipProxy':metric,'newDonorOpaqueOutsideWingRegion':sorted((occupied(donor)-old)-mask & {(x,y) for y in range(78,104) for x in range(96) if x<=30 or x>=65})}
    report['candidates'][f'v{version}']=entry
    print(json.dumps(entry,indent=2))
    decoded=[base,out,up]
    for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
        for scale in [1,3]:
            output=[]
            for y in range(104):
                row=bytearray()
                for picture in decoded:
                    for x in range(96):
                        p=picture[y][x*4:x*4+4]
                        row.extend((p if p[3] else bytes(bg))*scale)
                output.extend([row]*scale)
            png['write_png'](ROOT/f'art014-v{version}-{theme}-{scale}x.png',288*scale,104*scale,output)
assert before=={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report['protectedHashesUnchanged']=before
report['pngCrcAndRgbaReadback']='passed for candidate PNGs'
(ROOT/'art014-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
