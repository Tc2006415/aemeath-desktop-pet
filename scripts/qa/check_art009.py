"""Read-only QA decoder and mask checks, independent of ART export modules."""
import base64
import hashlib
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'assets/characters/aemeath-v1/source'
PACKAGE = SOURCE / 'art009-v1-package'


def png(path):
    raw = path.read_bytes()
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    offset, compressed, kinds = 8, bytearray(), []
    while offset < len(raw):
        size = struct.unpack_from('>I', raw, offset)[0]
        kind = raw[offset+4:offset+8]
        data = raw[offset+8:offset+8+size]
        crc = struct.unpack_from('>I', raw, offset+8+size)[0]
        assert zlib.crc32(kind+data) & 0xffffffff == crc, (path, 'CRC')
        kinds.append(kind)
        if kind == b'IHDR':
            w, h, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', data)
            assert (w, h, depth, color, compression, filtering, interlace) == (96,104,8,6,0,0,0)
        if kind == b'IDAT': compressed.extend(data)
        offset += size+12
    assert kinds[0] == b'IHDR' and kinds[-1] == b'IEND' and b'acTL' not in kinds
    packed = zlib.decompress(compressed)
    assert len(packed) == h*(1+w*4)
    prior, result = bytearray(w*4), []
    for y in range(h):
        begin = y*(w*4+1); method = packed[begin]; assert method <= 4
        row = bytearray(packed[begin+1:begin+1+w*4])
        for i in range(len(row)):
            left = row[i-4] if i >= 4 else 0
            up = prior[i]; upper_left = prior[i-4] if i >= 4 else 0
            if method == 0: predictor = 0
            elif method == 1: predictor = left
            elif method == 2: predictor = up
            elif method == 3: predictor = (left+up)//2
            else:
                p = left+up-upper_left
                distances = [abs(p-left), abs(p-up), abs(p-upper_left)]
                predictor = [left,up,upper_left][distances.index(min(distances))]
            row[i] = (row[i]+predictor) & 255
        result.extend(tuple(row[i:i+4]) for i in range(0,len(row),4)); prior = row
    assert {p[3] for p in result} == {0,255}
    assert len(raw) <= 262144
    return result


def occupied(pixels):
    return {(i%96,i//96) for i,p in enumerate(pixels) if p[3]}


def distance(a,b):
    return max(min(max(abs(x-u),abs(y-v)) for u,v in b) for x,y in a)


base = png(PACKAGE/'frames/neutral.png')
assert (PACKAGE/'frames/neutral.png').read_bytes() == (SOURCE.parent/'frames/neutral.png').read_bytes()
assert hashlib.sha256((PACKAGE/'frames/neutral.png').read_bytes()).hexdigest() == '5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d'
assert (PACKAGE/'frames/soft-peak.png').read_bytes() == (SOURCE/'art008-v2-96.png').read_bytes()
results = []
for name in ['neutral','soft-light','soft-peak','smile-half','smile-closed']:
    path = PACKAGE/f'frames/{name}.png'; pixels = png(path); points = occupied(pixels)
    bounds = [min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]
    foot = max(y for x,y in points if 38<=x<=57 and y>=80)
    assert bounds[0]>0 and bounds[2]<95 and bounds[1]==22 and bounds[3]<103 and foot==93
    changed = {i for i,p in enumerate(pixels) if p != base[i]}
    alpha = sum(p[3]!=q[3] for p,q in zip(pixels,base))
    entry = dict(name=name, bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bounds=bounds, footY=foot, changed=len(changed), alphaChanged=alpha)
    if name != 'neutral':
        mask = png(SOURCE/f'art009-v1-{name}-mask.png')
        allowed = {i for i,p in enumerate(mask) if p[3]}
        assert not changed-allowed
        entry.update(maskPixels=len(allowed), outsideMask=len(changed-allowed))
        if name.startswith('smile'):
            assert alpha == 0
            assert all(32<=i%96<=63 and 56<=i//96<=67 for i in changed)
        else:
            assert all(i//96>=83 and (i%96<=23 or i%96>=72) for i in changed)
            entry['featherDistances'] = []
            for lo,hi in [(0,33),(62,95)]:
                a = {(x,y) for x,y in occupied(base) if lo<=x<=hi and y>=82}
                b = {(x,y) for x,y in points if lo<=x<=hi and y>=82}
                entry['featherDistances'].append(max(distance(a,b),distance(b,a)))
    results.append(entry)
manifest = json.loads((PACKAGE/'manifest.json').read_text())
assert manifest['packageVersion']=='0.3.0' and manifest['anchor']=={'x':48,'y':94}
assert set(manifest['actions'])=={'neutral','idle-soft','idle-smile'}
for action,durations,mode in [('idle-soft',[400,150,150,400,150,150],'loop'),('idle-smile',[120,120,500,120,120,220],'once')]:
    clip=manifest['actions'][action]
    assert [f['durationMs'] for f in clip['frames']]==durations and clip['playback']==mode
html = (SOURCE/'art009-v1-inspection.html').read_text(encoding='utf-8')
embedded_manifest, _ = json.JSONDecoder().raw_decode(html.split('const pack=',1)[1])
embedded_images, _ = json.JSONDecoder().raw_decode(html.split(', images=',1)[1])
assert embedded_manifest == manifest
assert set(embedded_images) == {f'frames/{r["name"]}.png' for r in results}
for name,uri in embedded_images.items():
    assert base64.b64decode(uri.split(',',1)[1]) == (PACKAGE/name).read_bytes()
report = dict(candidate=str(PACKAGE), checks='PASS', previewEmbeddedBytes='match candidate manifest and all five PNGs', frames=results)
out = ROOT/'artifacts/qa006-pixels.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
