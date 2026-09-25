"""Compose generated local repairs only through explicit feather masks."""
import hashlib
import json
import runpy
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FORMAL=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
png=runpy.run_path(str(ROOT/'export-neutral.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:png['read_png'](p)[2]
window={(x,y) for y in range(89,98) for x in [*range(18,27),*range(69,78)]}
known={'soft-light':{(20,92),(20,93),(75,92),(75,93)},'soft-peak':{(76,90)}}
protected={str(p):sha(p) for p in [FORMAL/'manifest.json',*sorted((FORMAL/'frames').glob('*.png'))]}
def occ(rows):return {(x,y) for y in range(104) for x in range(96) if rows[y][x*4+3]}
report={'windowCoordinates':sorted(window),'candidates':{}}
maskversion=1 if '--mask1' in sys.argv else 2
for name in known:
    original=ROOT/f'art021-{name}-original.png';base=load(original)
    assert original.read_bytes()==(FORMAL/f'frames/{name}.png').read_bytes()
    # Retain existing prong gaps; allow only original feather pixels and diagnosed defects.
    mask=(occ(base)&window)|known[name]
    if maskversion==2:
        # Freeze tips and inner feather silhouette. Repair only the seam/connection bands.
        band={(x,y) for y in (range(91,95) if name=='soft-light' else range(89,92)) for x in [19,20,21,74,75,76]}
        band|={(x,y) for y in range(90,93) for x in [23,24,71,72]}
        mask &= band
        assert known[name]<=mask
    mr=[bytearray(384) for _ in range(104)]
    for x,y in mask:mr[y][x*4:x*4+4]=bytes((255,255,255,255))
    maskpath=ROOT/f'art021-{name}-mask-v{maskversion}.png';png['write_png'](maskpath,96,104,mr)
    for version in [1,2]:
        source=ROOT/f'art021-{name}-v{version}-source.png'
        if not source.exists():continue
        w,h,raw=png['read_png'](source)
        assert abs((w/h)/(96/104)-1)<0.02, 'Generated aspect/alignment must be reviewed'
        donor=[bytearray(384) for _ in range(104)]
        clipped=0
        for y in range(104):
            for x in range(96):
                p=raw[(2*y+1)*h//208][(2*x+1)*w//192*4:(2*x+1)*w//192*4+4]
                if p[3]>=128:
                    if y+5>=104:clipped+=1
                    else:donor[y+5][x*4:x*4+4]=p[:3]+b'\xff'
        assert clipped==0
        png['write_png'](ROOT/f'art021-{name}-v{version}-donor.png',96,104,donor)
        out=[bytearray(r) for r in base]
        for x,y in mask:out[y][x*4:x*4+4]=donor[y][x*4:x*4+4]
        tag=f'v{version}'+('-m2' if maskversion==2 else '')
        dest=ROOT/f'art021-{name}-{tag}-96.png';png['write_png'](dest,96,104,out)
        assert png['read_png'](dest)==(96,104,out)
        changes={(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4]!=base[y][x*4:x*4+4]}
        assert not changes-mask and not changes-window
        entry={'sourceSize':[w,h],'sourceSha256':sha(source),'originalSha256':sha(original),'outputSha256':sha(dest),'bytes':dest.stat().st_size,'format':'96x104 RGBA8 alpha0/255','sampling':'pixel-center nearest,alpha128,existing whole-image registration(0,+5),not wing deformation','maskVersion':maskversion,'maskSha256':sha(maskpath),'maskCoordinatesXY':sorted(mask),'clippedOpaqueSamples':clipped,'changedPixels':len(changes),'outsideWindowRgbaChanges':0,'outsideMaskRgbaChanges':0,'clearedOpaqueXY':sorted(occ(base)-occ(out)),'addedOpaqueXY':sorted(occ(out)-occ(base)),'knownPoints':{f'{x},{y}':list(out[y][x*4:x*4+4]) for x,y in sorted(known[name])},'protectedWindowPixelsOutsideMask':len(window-mask)}
        report['candidates'][f'{name}-{tag}']=entry
        print(json.dumps({k:v for k,v in entry.items() if k not in ['maskCoordinatesXY','clearedOpaqueXY']},indent=2))
assert protected=={p:sha(Path(p)) for p in protected}
report['formalProtectedHashesUnchanged']=protected
(ROOT/'art021-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
