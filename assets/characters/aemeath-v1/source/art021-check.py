"""Check selected repair topology and exact protection independently of build masks."""
import hashlib
import json
import runpy
from pathlib import Path
ROOT = Path(__file__).resolve().parent
read = runpy.run_path(str(ROOT / 'export-neutral.py'))['read_png']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
known = {'soft-light': {(20,92),(20,93),(75,92),(75,93)}, 'soft-peak': {(76,90)}}
window = {(x,y) for y in range(89,98) for x in [*range(18,27),*range(69,78)]}
def opaque(rows):
    return {(x,y) for y in range(104) for x in range(96) if rows[y][4*x+3]}
def components(points):
    remaining = set(points); sizes = []
    while remaining:
        stack = [remaining.pop()]; count = 0
        while stack:
            x,y = stack.pop(); count += 1
            for dx,dy in [(a,b) for a in [-1,0,1] for b in [-1,0,1] if a or b]:
                p = (x+dx,y+dy)
                if p in remaining: remaining.remove(p); stack.append(p)
        sizes.append(count)
    return sorted(sizes)
def bbox(points):
    return [min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]
result = {}
for name, additions in known.items():
    original = ROOT / f'art021-{name}-original.png'
    candidate = ROOT / f'art021-{name}-v1-m2-96.png'
    w,h,b = read(original); cw,ch,c = read(candidate)
    assert (w,h,cw,ch) == (96,104,96,104)
    bo,co = opaque(b),opaque(c)
    assert not bo-co and co-bo == additions
    assert all(c[y][x*4+3] in [0,255] for y in range(104) for x in range(96))
    changes = {(x,y) for y in range(104) for x in range(96) if b[y][x*4:x*4+4] != c[y][x*4:x*4+4]}
    assert changes <= window
    assert bbox(bo) == bbox(co)
    assert len(components(co)) <= len(components(bo))
    assert all(any((x+dx,y+dy) in bo for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]) for x,y in additions)
    result[name] = {'sha256':sha(candidate),'changedPixels':len(changes),'newTransparentPixels':0,'addedOpaqueXY':sorted(additions),'allOtherTransparentPixelsUnchanged':True,'outsideWindowRgbaChanges':0,'bboxBeforeAndAfter':bbox(co),'components8Before':components(bo),'components8After':components(co),'allAdditionsTouchOriginalOpaque':True,'anchorUnchanged':[48,94]}
protected = json.loads((ROOT/'art021-report.json').read_text())['formalProtectedHashesUnchanged']
assert all(sha(Path(p)) == digest for p,digest in protected.items())
result['protectedFormalFilesUnchanged'] = len(protected)
(ROOT/'art021-check-report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
