"""Final ART-011 expressive package, explicit face/body mask union."""
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:png['read_png'](p)[2]
package=ROOT/'art011-package'
frames=package/'frames'
frames.mkdir(parents=True,exist_ok=True)
baseline=ROOT/'art010-baseline'
body=ROOT/'art011-body-only-package'
base=load(baseline/'frames/neutral.png')
protected=[ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png'))]
before={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
for p in (baseline/'frames').glob('*.png'):
    (frames/p.name).write_bytes(p.read_bytes())
maskrows=load(ROOT/'art009-v1-smile-half-mask.png')
face={(x,y) for y in range(104) for x in range(96) if maskrows[y][x*4+3]}
assert len(face)==222 and all(32<=x<=63 and 56<=y<=67 for x,y in face)
(ROOT/'art011-face-mask.png').write_bytes((ROOT/'art009-v1-smile-half-mask.png').read_bytes())
source=ROOT/'art011-surprise-v1-source.png'
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
assert clipped==0
png['write_png'](ROOT/'art011-surprise-v1-donor.png',96,104,donor)
expressions={'surprise':donor,'half':load(baseline/'frames/smile-half.png'),'closed':load(baseline/'frames/smile-closed.png')}
report={'newImagegenCalls':1,'surpriseSourceSha256':sha(source),'sampling':'pixel-center nearest neighbor to96x104, alpha128, offset(0,+5)','clippedOpaqueSamples':clipped,'faceMaskPixels':len(face),'faceMaskCoordinatesXY':sorted(face,key=lambda p:(p[1],p[0])),'formalHashes':before,'frames':{}}
for bodyname,expression in [('hold','surprise'),('pickup','surprise'),('hold','half'),('hold-light','half'),('hold-peak','closed'),('release','closed'),('release','half')]:
    br=load(body/f'frames/{bodyname}.png')
    dr=expressions[expression]
    out=[bytearray(r) for r in br]
    for x,y in face:
        assert dr[y][x*4+3]==br[y][x*4+3]==255
        out[y][x*4:x*4+4]=dr[y][x*4:x*4+4]
    masks=['hold',bodyname] if bodyname.startswith('hold-') else [bodyname]
    union=set(face)
    for m in masks:
        mr=load(ROOT/f'art011-{m}-mask.png')
        moving={(x,y) for y in range(104) for x in range(96) if mr[y][x*4+3]}
        assert not moving&face
        union|=moving
    name=f'{bodyname}-{expression}'
    maskpng=[bytearray(384) for _ in range(104)]
    for x,y in union:maskpng[y][x*4:x*4+4]=b'\xff\xff\xff\xff'
    png['write_png'](ROOT/f'art011-{name}-union-mask.png',96,104,maskpng)
    dest=frames/f'{name}.png'
    png['write_png'](dest,96,104,out)
    changed={(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4]!=base[y][x*4:x*4+4]}
    facechanged={(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4]!=br[y][x*4:x*4+4]}
    assert not changed-union and not facechanged-face
    assert all(out[y][x*4+3]==br[y][x*4+3] for y in range(104) for x in range(96))
    assert sorted({r[i] for r in out for i in range(3,384,4)})==[0,255] and dest.stat().st_size<=262144
    report['frames'][name]={'bodySource':str((body/f'frames/{bodyname}.png').relative_to(ROOT)),'bodySha256':sha(body/f'frames/{bodyname}.png'),'expressionSource':'art011-surprise-v1-donor.png' if expression=='surprise' else f'art010-baseline/frames/smile-{expression}.png','outputSha256':sha(dest),'bytes':dest.stat().st_size,'faceChanges':len(facechanged),'faceAlphaChanges':0,'totalChanges':len(changed),'outsideUnionChanges':0,'unionMask':f'art011-{name}-union-mask.png','bodyMaskComponents':masks}
actions={}
for name,mode,poses,times in [
    ('drag-pickup','once',['neutral','hold-surprise','pickup-surprise','hold-half'],[80,80,100,100]),
    ('drag-hold','loop',['hold-half','hold-light-half','hold-peak-closed','hold-light-half'],[180]*4),
    ('drag-release','once',['hold-half','release-closed','release-half','neutral'],[80,100,120,160])]:
    actions[name]={'origin':'original','playback':mode,'frames':[{'path':f'frames/{p}.png','durationMs':t} for p,t in zip(poses,times)]}
raw=(baseline/'manifest.json').read_bytes()
nl=b'\r\n' if b'\r\n' in raw else b'\n'
idx=raw.rfind(nl+b'  }')
addition=nl.join(('  '+s).encode() for s in json.dumps(actions,indent=2).splitlines()[1:-1])
updated=(raw[:idx]+b','+nl+addition+raw[idx:]).replace(b'"packageVersion": "0.3.0"',b'"packageVersion": "0.4.0"',1)
assert updated.replace(b','+nl+addition,b'',1).replace(b'"packageVersion": "0.4.0"',b'"packageVersion": "0.3.0"',1)==raw
(package/'manifest.json').write_bytes(updated)
assert before=={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report['baselineManifestBytesPreservedExceptVersionAndNewActions']=True
report['formalUnchanged']=True
(ROOT/'art011-expression-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS: 12 PNG / 6 actions; original five bytes retained; seven expression/body composites; mask outside 0, face alpha changes 0')
