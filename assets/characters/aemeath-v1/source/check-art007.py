"""ART-007 fixed conversion and read-only comparison. Writes only source/art007-*.

Usage: python -B source/check-art007.py v1 (or v2).
ROI rectangles are conservative inspection regions, not segmentation masks.
No region is copied into the candidate, repainted, or individually aligned.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('png', ROOT / 'export-neutral.py')
png = importlib.util.module_from_spec(spec)
spec.loader.exec_module(png)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def occupied(rows, box=(0, 0, 95, 103)):
    x0, y0, x1, y1 = box
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if rows[y][x * 4 + 3]}


def bounds(points):
    return [min(x for x, y in points), min(y for x, y in points), max(x for x, y in points), max(y for x, y in points)] if points else None


def compare(a, b, box):
    x0, y0, x1, y1 = box
    alpha_changes, rgb_changes, deltas, large = [], 0, [], 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            pa, pb = a[y][x * 4:x * 4 + 4], b[y][x * 4:x * 4 + 4]
            if pa[3] != pb[3]:
                alpha_changes.append([x, y, pa[3], pb[3]])
            if pa[3] and pb[3]:
                delta = max(abs(pa[i] - pb[i]) for i in range(3))
                deltas.append(delta)
                rgb_changes += delta > 0
                large += delta > 24
    return {'rectangleInclusive': box, 'alphaChangedCount': len(alpha_changes),
            'alphaChangesXYNeutralCandidate': alpha_changes, 'commonOpaquePixelCount': len(deltas),
            'rgbChangedCommonOpaquePixels': rgb_changes, 'rgbMaxChannelDelta': max(deltas, default=0),
            'rgbMeanMaxChannelDelta': round(sum(deltas) / max(1, len(deltas)), 3), 'rgbPixelsMaxDeltaAbove24': large}


def main(version):
    assert version in ('v1', 'v2')
    prefix = f'art007-trial-{version}'
    source = ROOT / f'{prefix}-source.png'
    protected = [ROOT.parent / 'manifest.json', *sorted((ROOT.parent / 'frames').glob('*.png'))]
    initial = {str(p.relative_to(ROOT.parent)): sha(p) for p in protected}
    neutral = ROOT.parent / 'frames/neutral.png'
    assert sha(neutral) == '5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d'
    w, h, rows = png.read_png(source)
    report = {'source': source.name, 'sourceSize': [w, h], 'sourceSha256': sha(source), 'protectedHashes': initial,
              'expectedSourceSize': [1205, 1306], 'sampling': 'full canvas center-nearest floor((2*x+1)*1205/(2*96)); analogous y/104',
              'alphaThreshold': 128, 'integerOffset': [0, 5], 'anchorReferenceOnly': [48, 94]}
    report_path = ROOT / f'{prefix}-report.json'
    if (w, h) != (1205, 1306):
        report.update(result='FAIL', reason='source canvas mismatch; no adaptive conversion performed')
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report)); return
    output = [bytearray(384) for _ in range(104)]
    clipped = 0
    for y in range(104):
        sy = ((2 * y + 1) * h) // 208
        for x in range(96):
            sx = ((2 * x + 1) * w) // 192
            pixel = rows[sy][sx * 4:sx * 4 + 4]
            if pixel[3] < 128:
                continue
            if y + 5 >= 104:
                clipped += 1
            else:
                output[y + 5][x * 4:x * 4 + 4] = pixel[:3] + b'\xff'
    candidate = ROOT / f'{prefix}-96.png'
    png.write_png(candidate, 96, 104, output)
    ow, oh, verified = png.read_png(candidate)
    _, _, base = png.read_png(neutral)
    alpha = sorted({r[i] for r in verified for i in range(3, 384, 4)})
    bbox = bounds(occupied(verified))
    feet = bounds(occupied(verified, (38, 80, 57, 103)))
    rois = {'crownAndUpperHair': (20, 18, 75, 47), 'sideOrnament': (61, 39, 78, 59), 'fixedHead': (0, 0, 95, 68)}
    diffs = {name: compare(base, verified, box) for name, box in rois.items()}
    feathers = {}
    for name, box in [('left', (0, 82, 33, 103)), ('right', (62, 82, 95, 103))]:
        before, after = occupied(base, box), occupied(verified, box)
        b0, b1 = bounds(before), bounds(after)
        def directed(a, b):
            return max((min(max(abs(x - xx), abs(y - yy)) for xx, yy in b) for x, y in a - b), default=0)
        feathers[name] = {'neutralBounds': b0, 'candidateBounds': b1,
                          'inwardExtremeShift': b1[0] - b0[0] if name == 'left' else b0[2] - b1[2],
                          'opaqueSetChebyshevDistance': max(directed(before, after), directed(after, before)),
                          'alphaChangedCount': len(before ^ after)}
    checks = {'sourceCanvasMatches': True, 'staticRgba8Crc': True, 'frameSize': (ow, oh) == (96, 104),
              'binaryAlphaNonempty': alpha == [0, 255], 'under256KiB': candidate.stat().st_size <= 262144,
              'noCroppedOpaqueSamples': clipped == 0, 'margins': 4 <= bbox[0] <= bbox[2] <= 91 and 4 <= bbox[1] <= bbox[3] <= 99,
              'crownTopY22': bbox[1] == 22, 'feetBottomY93': feet[3] == 93,
              'fixedHeadAlphaUnchanged': diffs['fixedHead']['alphaChangedCount'] == 0,
              'featherInwardShiftWithin2': all(0 <= f['inwardExtremeShift'] <= 2 for f in feathers.values()),
              'featherOpaqueDistanceWithin2': all(f['opaqueSetChebyshevDistance'] <= 2 for f in feathers.values()),
              'localFeatherShapeChange': any(f['alphaChangedCount'] > 0 for f in feathers.values())}
    report.update(candidate=candidate.name, candidateSha256=sha(candidate), frameBytes=candidate.stat().st_size,
                  frameSize=[ow, oh], alphaValues=alpha, inclusiveBounds=bbox, centralFeetBounds=feet,
                  clippedOpaqueSamples=clipped, regions=diffs, feathers=feathers, checks=checks,
                  result='PASS_GEOMETRY_PENDING_VISUAL' if all(checks.values()) else 'FAIL',
                  failedChecks=[key for key, value in checks.items() if not value])
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    # Inspection preview only: left approved neutral, right unmodified candidate, exact 4x replication.
    preview = []
    for y in range(104):
        row = base[y] + verified[y]
        enlarged = bytearray(b''.join(row[i:i + 4] * 4 for i in range(0, len(row), 4)))
        preview.extend([enlarged] * 4)
    png.write_png(ROOT / f'{prefix}-compare-4x.png', 768, 416, preview)
    assert initial == {str(p.relative_to(ROOT.parent)): sha(p) for p in protected}
    print(json.dumps({key: report[key] for key in ('sourceSize', 'frameBytes', 'inclusiveBounds', 'centralFeetBounds', 'feathers', 'checks', 'result')}, indent=2))
    print('Head RGB/alpha:', json.dumps({n: {k:v for k,v in d.items() if not isinstance(v, (list,tuple))} for n,d in diffs.items()}))


if __name__ == '__main__':
    main(sys.argv[1])
