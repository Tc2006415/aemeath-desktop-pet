"""ART-010R: existing donor only; retain neutral chest including tapered gold tip."""
import base64
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
png = runpy.run_path(str(ROOT/'export-neutral.py'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
basepath = ROOT/'art010-baseline/frames/neutral.png'
donorpath = ROOT/'art010-release-v1-donor.png'
oldpath = ROOT/'art010-release-v1-96.png'
base = png['read_png'](basepath)[2]
donor = png['read_png'](donorpath)[2]
protected = [ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png')),ROOT/'art010-pickup-v1-96.png',ROOT/'art010-hold-v2-96.png',oldpath,donorpath]
before = {str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
mask = {(x,y) for y in range(83,95) for x in range(38,58)
        if not (y==83 and 45<=x<=50 or y==84 and 46<=x<=49)}
out = [bytearray(r) for r in base]
maskrows = [bytearray(384) for _ in range(104)]
for x,y in mask:
    out[y][x*4:x*4+4] = donor[y][x*4:x*4+4]
    maskrows[y][x*4:x*4+4] = b'\xff\xff\xff\xff'
dest = ROOT/'art010-release-r1-96.png'
png['write_png'](dest,96,104,out)
png['write_png'](ROOT/'art010-release-r1-mask.png',96,104,maskrows)
changed = {(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4] != base[y][x*4:x*4+4]}
assert changed and not changed-mask
assert not any(y<83 for x,y in changed)
assert all(base[y][x*4:x*4+4]==out[y][x*4:x*4+4] for y in (83,84) for x in range(46,50))
assert sorted({r[i] for r in out for i in range(3,384,4)}) == [0,255]
occupied = {(x,y) for y in range(104) for x in range(96) if out[y][x*4+3]}
foot = max(y for x,y in occupied if 38<=x<=57 and y>=85)
assert foot == 93 and min(y for x,y in occupied)==22
assert dest.stat().st_size<=256*1024
assert before=={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report={'maskVersion':1,'newImagegenCalls':0,'baseSha256':sha(basepath),'donorSha256':sha(donorpath),'outputSha256':sha(dest),'size':[96,104],'anchor':[48,94],'alpha':[0,255],'bytes':dest.stat().st_size,'maskRule':'x38..57/y83..94, excluding x45..50 at y83 and x46..49 at y84 to retain full neutral white diamond and gold tip','maskCoordinatesXY':sorted(mask,key=lambda p:(p[1],p[0])),'changedPixels':len(changed),'outsideMaskRgbaChanges':len(changed-mask),'yBelow83RgbaChanges':sum(y<83 for x,y in changed),'crownTopY':22,'footBottomY':foot,'protectedHashesUnchanged':before}
(ROOT/'art010-release-r1-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('maskCoordinatesXY','protectedHashesUnchanged')},indent=2))
items=[basepath,oldpath,dest]
for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
    decoded=[png['read_png'](p)[2] for p in items]
    for scale in [1,4]:
        rows=[]
        for y in range(104):
            row=bytearray()
            for picture in decoded:
                for x in range(96):
                    pixel=picture[y][x*4:x*4+4]
                    row.extend((pixel if pixel[3] else bytes(bg))*scale)
            rows.extend([row]*scale)
        png['write_png'](ROOT/f'art010-release-r1-{theme}-{scale}x.png',288*scale,104*scale,rows)
urls={n:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for n,p in zip(['neutral','old-release','revised-release'],items)}
html='''<!doctype html><meta charset="utf-8"><title>ART-010R release</title><style>body{font:16px system-ui;background:#eee}img{image-rendering:pixelated}.card{display:inline-block;padding:12px;background:#f0efeb}.dark{background:#1d222c}.big{width:384px;height:416px}button{padding:12px;margin:5px}</style><h1>ART-010R · neutral / 旧release / 修订release</h1><nav></nav><h2 id="state"></h2><div class="card"><img class="big"><img></div><div class="card dark"><img class="big"><img></div><script>const images=DATA;function show(n){document.querySelector('#state').textContent=n;document.querySelectorAll('img').forEach(i=>i.src=images[n]);}for(const n of Object.keys(images)){const b=document.createElement('button');b.textContent=n;b.onclick=()=>show(n);document.querySelector('nav').append(b);}show('revised-release');</script>'''
(ROOT/'art010-release-r1-preview.html').write_text(html.replace('DATA',json.dumps(urls)),encoding='utf-8')
