"""ART-010: authorized deterministic conversion and explicit central-body compositing."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('png', ROOT / 'export-neutral.py')
png = importlib.util.module_from_spec(spec)
spec.loader.exec_module(png)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    baseline = ROOT / 'art010-baseline'
    manifest = json.loads((baseline / 'manifest.json').read_text(encoding='utf-8-sig'))
    assert manifest['packageVersion'] == '0.3.0'
    neutral = baseline / 'frames/neutral.png'
    assert sha(neutral) == '5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d'
    _, _, base = png.read_png(neutral)
    protected = [ROOT.parent / 'manifest.json', *sorted((ROOT.parent / 'frames').glob('*.png'))]
    before = {str(p.relative_to(ROOT.parent)): sha(p) for p in protected}
    report = {'baselinePmCommit': 'a2442f3bd023a97fae70727e21f62af97b5adf68', 'baselineSource': 'C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1', 'baselineHashes': {str(p.relative_to(baseline)): sha(p) for p in baseline.rglob('*') if p.is_file()}, 'anchor': [48,94], 'conversion': {'nearest': 'floor((2*x+1)*sourceWidth/(2*96)); equivalent y/104', 'alphaThreshold': 128, 'offset': [0,5]}, 'formalHashesBefore': before, 'poses': {}}
    for pose, version in [('pickup',1), ('hold',1), ('hold',2), ('release',1)]:
        prefix = f'art010-{pose}-v{version}'
        source = ROOT / f'{prefix}-source.png'
        if not source.exists():
            continue
        w,h,rows = png.read_png(source)
        assert (w,h) == (1205,1306), (pose,w,h)
        donor = [bytearray(384) for _ in range(104)]
        clipped = 0
        for y in range(104):
            for x in range(96):
                p = rows[(2*y+1)*h//208][(2*x+1)*w//192*4:(2*x+1)*w//192*4+4]
                if p[3] < 128:
                    continue
                if y+5 >= 104:
                    clipped += 1
                else:
                    donor[y+5][x*4:x*4+4] = p[:3] + b'\xff'
        assert clipped == 0
        png.write_png(ROOT / f'{prefix}-donor.png',96,104,donor)
        # Explicit torso/arms/legs domain. All y<75, x<35 and x>60 stay immutable.
        mask = {(x,y) for y in range(75,98) for x in range(35,61)}
        out = [bytearray(r) for r in base]
        maskrows = [bytearray(384) for _ in range(104)]
        for x,y in mask:
            out[y][x*4:x*4+4] = donor[y][x*4:x*4+4]
            maskrows[y][x*4:x*4+4] = b'\xff\xff\xff\xff'
        dest = ROOT / f'{prefix}-96.png'
        png.write_png(dest,96,104,out)
        png.write_png(ROOT / f'{prefix}-mask.png',96,104,maskrows)
        changed = {(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4] != base[y][x*4:x*4+4]}
        assert changed and not changed-mask
        assert dest.stat().st_size <= 256*1024
        alpha = sorted({r[i] for r in out for i in range(3,384,4)})
        assert alpha == [0,255]
        occupied = [(x,y) for y in range(104) for x in range(96) if out[y][x*4+3]]
        seam = [(x,y) for x,y in changed if x in (35,60) or y in (75,97)]
        info = {'attempt':1,'maskVersion':1,'sourceSha256':sha(source),'outputSha256':sha(dest),'bytes':dest.stat().st_size,'size':[96,104],'alpha':alpha,'clippedOpaqueSamples':clipped,'changedPixels':len(changed),'maskCoordinatesXY': sorted(mask,key=lambda p:(p[1],p[0])),'outsideMaskRgbaChanges':len(changed-mask),'headRgbaChanges':sum(y<75 for x,y in changed),'bounds':[min(x for x,y in occupied),min(y for x,y in occupied),max(x for x,y in occupied),max(y for x,y in occupied)],'centralFootBottomY':max(y for x,y in occupied if 41<=x<=54 and y>=85),'changedMaskBoundaryXY': sorted(seam)}
        info['attempt'] = version
        report['poses'][f'{pose}-v{version}'] = info
        print(pose, json.dumps({k:v for k,v in info.items() if k not in ('maskCoordinatesXY','changedMaskBoundaryXY')}))
    assert before == {str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
    report['formalFilesUnchanged'] = True
    (ROOT / 'art010-v1-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__':
    main()
