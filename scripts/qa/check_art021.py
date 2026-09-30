"""QA-010 independent read-only PNG/provenance checks; never writes pixels."""
import base64, hashlib, json, re, sys
from pathlib import Path
from png_readonly import png

source, formal, output = map(Path, sys.argv[1:4])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = {'soft-light': 'bc9fe556ac774ad2ca7c77d03446cdc451159819712e7e4fc9b8b245b48dcd70', 'soft-peak': '79d227136f70d87ccea3d7efa2ae94759f8868890c3ef87a984c2d8fcf045be2'}
known = {'soft-light': {(20,92),(20,93),(75,92),(75,93)}, 'soft-peak': {(76,90)}}
window = {(x,y) for y in range(89,98) for x in [*range(18,27),*range(69,78)]}
report = {}
for name in expected:
    original = source/f'art021-{name}-original.png'
    candidate = source/f'art021-{name}-v1-m2-96.png'
    assert original.read_bytes() == (formal/f'frames/{name}.png').read_bytes()
    assert sha(candidate) == expected[name]
    a, b = png(original)[2], png(candidate)[2]
    mask = png(source/f'art021-{name}-mask-v2.png')[2]
    donor = png(source/f'art021-{name}-v1-donor.png')[2]
    w,h,raw = png(source/f'art021-{name}-v1-source.png',None)
    # Reconstruct the documented whole-image sampling in memory, not an output image.
    reconstructed = [(0,0,0,0)]*(96*104)
    for y in range(104):
        for x in range(96):
            pixel = raw[((2*y+1)*h//208)*w+(2*x+1)*w//192]
            if pixel[3] >= 128:
                assert y+5 < 104, 'clipped opaque sample'
                reconstructed[(y+5)*96+x] = (*pixel[:3],255)
    assert reconstructed == donor, 'donor provenance mismatch'
    allowed = {(i%96,i//96) for i,p in enumerate(mask) if p[3]}
    assert allowed <= window
    changes,added,cleared,gaps = [],[],[],[]
    for i,(old,new) in enumerate(zip(a,b)):
        xy = (i%96,i//96)
        assert new == (donor[i] if xy in allowed else old), 'not exact masked composition'
        if old != new: changes.append(xy)
        if not old[3] and new[3]: added.append(xy)
        if old[3] and not new[3]: cleared.append(xy)
        if xy in window and not old[3] and xy not in known[name]:
            assert new == old; gaps.append(xy)
    assert set(added) == known[name] and not cleared
    assert len(changes) == (33 if name=='soft-light' else 30)
    assert set(changes) <= allowed
    report[name] = dict(sha256=sha(candidate),rgbaChanges=len(changes),maskPixels=len(allowed),outsideMaskChanges=0,outsideWindowChanges=0,added=added,cleared=cleared,preservedTransparentWindowPixels=len(gaps),donorReconstruction=True,changes=changes)

html = (source/'art021-inspection.html').read_text(encoding='utf-8')
images = json.loads(re.search(r'const images=(.*?),frames=',html).group(1))
paths = {'neutral':formal/'frames/neutral.png','soft-light':source/'art021-soft-light-v1-m2-96.png','soft-peak':source/'art021-soft-peak-v1-m2-96.png','old-light':source/'art021-soft-light-original.png','old-peak':source/'art021-soft-peak-original.png'}
assert set(images)==set(paths)
for name,path in paths.items(): assert base64.b64decode(images[name].split(',')[1])==path.read_bytes()
frames = json.loads(re.search(r',frames=(.*?);let start=',html).group(1))
manifest = json.loads((formal/'manifest.json').read_bytes())
assert frames == manifest['actions']['idle-soft']['frames']
assert [(f['path'],f['durationMs']) for f in frames]==[(f'frames/{n}.png',t) for n,t in [('neutral',400),('soft-light',150),('soft-peak',150),('soft-peak',400),('soft-light',150),('neutral',150)]]
report['preview'] = dict(sha256=sha(source/'art021-inspection.html'),embeddedBytes=5,timingMs=1400)
report['formalHashes'] = {p.name:sha(p) for p in [formal/'manifest.json',*sorted((formal/'frames').glob('*.png'))]}
output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
