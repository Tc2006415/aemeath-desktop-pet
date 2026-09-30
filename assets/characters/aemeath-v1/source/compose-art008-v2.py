"""ART-008 explicitly authorized pixel replacement; existing generated art only."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('art007', ROOT / 'check-art007.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
png = api.png


def main():
    neutral = ROOT.parent / 'frames/neutral.png'
    donor = ROOT / 'art007-trial-v1-96.png'
    protected = [ROOT.parent / 'manifest.json', *sorted((ROOT.parent / 'frames').glob('*.png'))]
    hashes = {str(p.relative_to(ROOT.parent)): api.sha(p) for p in protected}
    assert api.sha(neutral) == '5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d'
    assert api.sha(donor) == 'ea7b18fe821f32e9bf0586d122eb02f017c69e42528a411fbde44e03d885deac'
    _, _, base = png.read_png(neutral)
    _, _, moving = png.read_png(donor)
    # Contour union + a one-pixel collar inside explicit lower-feather-only domains.
    # Left domains include the lifted outer tip at (17,83); right mirrors x -> 95-x.
    domains = set()
    for y in range(83, 99):
        left = 15 if y <= 84 else 12 if y <= 87 else 8
        for x in range(left, 24):
            domains.add((x, y)); domains.add((95 - x, y))
    union = (api.occupied(base) | api.occupied(moving)) & domains
    mask = {(x, y) for x, y in domains if any((x + dx, y + dy) in union for dx in (-1, 0, 1) for dy in (-1, 0, 1))}
    out = [bytearray(row) for row in base]
    mask_rows = [bytearray(384) for _ in range(104)]
    for x, y in mask:
        out[y][x * 4:x * 4 + 4] = moving[y][x * 4:x * 4 + 4]  # Includes transparent clearing.
        mask_rows[y][x * 4:x * 4 + 4] = b'\xff\xff\xff\xff'
    dest = ROOT / 'art008-v2-96.png'
    png.write_png(dest, 96, 104, out)
    png.write_png(ROOT / 'art008-v2-mask.png', 96, 104, mask_rows)
    w, h, out = png.read_png(dest)
    changed = {(x, y) for y in range(104) for x in range(96) if out[y][x * 4:x * 4 + 4] != base[y][x * 4:x * 4 + 4]}
    before, after = api.occupied(base), api.occupied(out)
    seam = {(x, y) for x, y in mask if any((x + dx, y + dy) not in mask for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)))}
    opaque_seam_changes = [(x,y) for x,y in seam if (x,y) in before and (x,y) in after and (x,y) in changed]
    alpha_seam_changes = [(x,y) for x,y in seam if ((x,y) in before) != ((x,y) in after)]
    report = {'base': neutral.name, 'baseSha256': api.sha(neutral), 'donor': donor.name, 'donorSha256': api.sha(donor),
              'output': dest.name, 'outputSha256': api.sha(dest), 'size': [w,h], 'bytes': dest.stat().st_size,
              'maskRule': 'union of base/donor opaque contours + 1px collar, clipped to listed domains; direct RGBA replacement including zero alpha',
              'domainLeftInclusive': {'y83to84': [15,23], 'y85to87': [12,23], 'y88to98': [8,23]},
              'domainRight': 'mirror x -> 95-x; no pixels x24..71 or y<83 are eligible',
              'maskPixels': len(mask), 'maskCoordinatesXY': sorted(mask, key=lambda p:(p[1],p[0])),
              'changedPixels': len(changed), 'outsideMaskRgbaChanges': len(changed-mask),
              'headRgbaChanges': sum(y<69 for x,y in changed), 'bodyFeetCentralRgbaChanges': sum(24<=x<=71 for x,y in changed),
              'oldOpaqueCleared': len(before-after), 'newOpaqueAdded': len(after-before),
              'bounds': api.bounds(after), 'footBottomY': api.bounds(api.occupied(out,(38,80,57,103)))[3],
              'anchorReference': [48,94], 'seamCommonOpaqueChangedXY': sorted(opaque_seam_changes),
              'seamAlphaChangedXY': sorted(alpha_seam_changes), 'protectedHashes': hashes,
              'alphaValues': sorted({r[i] for r in out for i in range(3,384,4)})}
    feathers = {}
    for name, box in [('left',(0,82,33,103)),('right',(62,82,95,103))]:
        a,b=api.occupied(base,box),api.occupied(out,box)
        ba,bb=api.bounds(a),api.bounds(b)
        distance=max(max((min(max(abs(x-xx),abs(y-yy)) for xx,yy in b) for x,y in a-b),default=0),
                     max((min(max(abs(x-xx),abs(y-yy)) for xx,yy in a) for x,y in b-a),default=0))
        feathers[name]={'neutralBounds':ba,'compositeBounds':bb,'inwardShift':bb[0]-ba[0] if name=='left' else ba[2]-bb[2],
                        'opaqueSetChebyshevDistance':distance,'alphaChanges':len(a^b)}
    report['feathers']=feathers
    assert (w,h)==(96,104) and report['alphaValues']==[0,255] and report['bytes']<=262144
    assert not changed-mask and not report['headRgbaChanges'] and not report['bodyFeetCentralRgbaChanges']
    assert report['bounds'][1]==22 and report['footBottomY']==93 and all(1<=f['inwardShift']<=2 for f in feathers.values())
    assert report['oldOpaqueCleared']>0 and report['newOpaqueAdded']>0
    report['formatAndProtectedPixels']='PASS; visual seam/alternation assessment recorded separately'
    (ROOT/'art008-v2-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for scale in (1,4):
        for name,bg in [('light',(245,245,245)),('dark',(35,39,47))]:
            preview=[]
            for y in range(104):
                row=base[y]+out[y]
                rgba=[row[i:i+4] if row[i+3] else bytes((*bg,255)) for i in range(0,len(row),4)]
                enlarged=bytearray(b''.join(p*scale for p in rgba))
                preview.extend([enlarged]*scale)
            png.write_png(ROOT/f'art008-v2-{name}-{scale}x.png',192*scale,104*scale,preview)
    data=[base64.b64encode(p.read_bytes()).decode() for p in (neutral,dest)]
    html='''<!doctype html><meta charset="utf-8"><title>ART-008 单帧接缝检查</title><style>body{font:18px system-ui;margin:24px;background:#eee;color:#222}section{display:flex;gap:20px;flex-wrap:wrap}.panel{background:#f5f5f5;padding:16px}.dark{background:#23272f;color:white}img{image-rendering:pixelated}button{font:inherit;padding:8px;margin:8px}small{display:block}</style>
<h1>ART-008 v2 · neutral / 羽饰试样</h1><p>仅下部羽饰合成，未进入正式包。1×及4×浅深底；每600ms交替。</p><button id="toggle">暂停</button><button id="base">neutral</button><button id="trial">试样</button><p id="state"></p><section id="panels"></section>
<script>const frames=DATA;let frame=0,playing=true;const panels=document.querySelector('#panels');for(const scale of [1,4])for(const dark of [false,true]){let p=document.createElement('div');p.className='panel'+(dark?' dark':'');p.innerHTML=`<small>${dark?'深':'浅'}底 ${scale}×</small><img width="${96*scale}" height="${104*scale}">`;panels.append(p)}function draw(){for(const img of document.images)img.src='data:image/png;base64,'+frames[frame];document.querySelector('#state').textContent=(playing?'交替播放':'暂停')+' · '+(frame?'试样':'neutral')}function stop(i){playing=false;frame=i;draw()}document.querySelector('#base').onclick=()=>stop(0);document.querySelector('#trial').onclick=()=>stop(1);document.querySelector('#toggle').onclick=()=>{playing=!playing;draw()};setInterval(()=>{if(playing){frame=1-frame;draw()}},600);draw();</script>'''
    (ROOT/'art008-v2-inspection.html').write_text(html.replace('DATA',json.dumps(data)),encoding='utf-8')
    assert hashes=={str(p.relative_to(ROOT.parent)):api.sha(p) for p in protected}
    print(json.dumps({k:v for k,v in report.items() if k not in ('maskCoordinatesXY','protectedHashes','seamCommonOpaqueChangedXY','seamAlphaChangedXY')},indent=2))
    print('Seam changed common-opaque:',opaque_seam_changes,'alpha:',alpha_seam_changes)


if __name__=='__main__':
    main()
