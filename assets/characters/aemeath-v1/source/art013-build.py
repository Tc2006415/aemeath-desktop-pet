"""ART-013 four-item medium wing loop; accepted sources only, no imagegen."""
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:png['read_png'](p)[2]
source=ROOT/'art011-package'
package=ROOT/'art013-package'
frames=package/'frames'
frames.mkdir(parents=True,exist_ok=True)
protected=[ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png')),*sorted(source.rglob('*.*'))]
before={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
raw=(source/'manifest.json').read_bytes()
start=raw.index(b'"drag-hold":')
end=raw.index(b'"drag-release":',start)
chunk=raw[start:end].replace(b'frames/hold-light-half.png',b'frames/hold-up-half.png',1).replace(b'frames/hold-peak-closed.png',b'frames/hold-mid-closed.png',1).replace(b'frames/hold-light-half.png',b'frames/hold-down-half.png',1)
updated=raw[:start]+chunk+raw[end:]
(package/'manifest.json').write_bytes(updated)
manifest=json.loads(updated)
original=json.loads(raw)
assert manifest['packageVersion']=='0.4.0'
for action in original['actions']:
    if action!='drag-hold':assert manifest['actions'][action]==original['actions'][action]
assert raw[:start]==updated[:start] and raw[end:]==updated[start+len(chunk):]
used={f['path'] for a in manifest['actions'].values() for f in a['frames']}
copied={}
for name in used:
    p=source/name
    if p.exists():
        (package/name).write_bytes(p.read_bytes())
        copied[name]={'source':str(p.relative_to(ROOT)),'sha256':sha(p)}
hold=load(source/'frames/hold-half.png')
neutral=load(source/'frames/neutral.png')
maskset=lambda path:{(x,y) for y,row in enumerate(load(path)) for x in range(96) if row[x*4+3]}
face=maskset(ROOT/'art011-face-mask.png')
body=maskset(ROOT/'art011-hold-mask.png')
wing=maskset(ROOT/'art012-wing-mask-v1.png')
assert not body&face and not wing&face and not wing&body
reports={}
for name,p in [('hold-up-half',ROOT/'art012-up-v2-96.png'),('hold-down-half',ROOT/'art012-down-v1-96.png'),('hold-mid-closed',source/'frames/smile-closed.png')]:
    if name=='hold-mid-closed':
        out=[bytearray(r) for r in hold]
        donor=load(p)
        for x,y in face:out[y][x*4:x*4+4]=donor[y][x*4:x*4+4]
        png['write_png'](frames/f'{name}.png',96,104,out)
        mask=body|face
    else:
        (frames/f'{name}.png').write_bytes(p.read_bytes())
        out=load(p)
        mask=body|face|wing
    changes={(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4]!=neutral[y][x*4:x*4+4]}
    assert not changes-mask
    assert all(out[y][x*4:x*4+4]==hold[y][x*4:x*4+4] for y in range(104) for x in range(96) if (x,y) not in face|wing)
    mr=[bytearray(384) for _ in range(104)]
    for x,y in mask:mr[y][x*4:x*4+4]=b'\xff\xff\xff\xff'
    png['write_png'](ROOT/f'art013-{name}-union-mask.png',96,104,mr)
    reports[name]={'source':str(p.relative_to(ROOT)),'sourceSha256':sha(p),'outputSha256':sha(frames/f'{name}.png'),'changedPixelsFromNeutral':len(changes),'outsideUnionRgbaChanges':0,'maskComponents':['body','face']+([] if name=='hold-mid-closed' else ['wing']),'maskCoordinatesXY':sorted(mask,key=lambda p:(p[1],p[0]))}
for component,p in [('body',ROOT/'art011-hold-mask.png'),('face',ROOT/'art011-face-mask.png'),('wing',ROOT/'art012-wing-mask-v1.png')]:
    (ROOT/f'art013-{component}-mask.png').write_bytes(p.read_bytes())
for name in ['hold-half','hold-surprise','pickup-surprise','release-half','release-closed']:
    (ROOT/f'art013-{name}-union-mask.png').write_bytes((ROOT/f'art011-{name}-union-mask.png').read_bytes())
assert len(list(frames.glob('*.png')))==13 and len(used)==13
checks={}
for f in frames.glob('*.png'):
    w,h,rows=png['read_png'](f)
    assert (w,h)==(96,104) and f.stat().st_size<=262144
    assert sorted({row[i] for row in rows for i in range(3,384,4)})==[0,255]
    checks[f.name]={'sha256':sha(f),'bytes':f.stat().st_size}
for p in (ROOT/'art010-baseline/frames').glob('*.png'):assert p.read_bytes()==(frames/p.name).read_bytes()
for a,times in [('drag-pickup',[80,80,100,100]),('drag-hold',[180]*4),('drag-release',[80,100,120,160])]:
    assert [f['durationMs'] for f in manifest['actions'][a]['frames']]==times
assert manifest['actions']['drag-pickup']['frames'][-1]['path']==manifest['actions']['drag-hold']['frames'][0]['path']
assert manifest['actions']['drag-release']['frames'][-1]['path']==manifest['actions']['idle-soft']['frames'][0]['path']
assert before=={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report={'newImagegenCalls':0,'copiedFrames':copied,'newFrames':reports,'pngChecks':checks,'manifestSha256':sha(package/'manifest.json'),'preservedManifestOutsideHoldBytes':True,'baselineFivePngBytesPreserved':True,'protectedFilesUnchanged':True,'protectedHashes':before}
(ROOT/'art013-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS: 13 PNG, 6 actions; pickup/release unchanged; hold middle/up/middle/down 720ms; explicit mask unions, outside0')
