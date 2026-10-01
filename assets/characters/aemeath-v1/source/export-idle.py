"""ART-006: authorized nearest-neighbor/alpha/integer alignment only."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('neutral_export', ROOT / 'export-neutral.py')
png = importlib.util.module_from_spec(spec)
spec.loader.exec_module(png)
NAMES = ['soft-a', 'soft-b', 'smile-half', 'smile-closed']


def main():
    neutral = ROOT.parent / 'frames/neutral.png'
    neutral_hash = hashlib.sha256(neutral.read_bytes()).hexdigest()
    assert neutral_hash == '5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d'
    _, _, base = png.read_png(neutral)
    report = []
    for name in NAMES:
        source = ROOT / f'{name}-generated-v1.png'
        w, h, rows = png.read_png(source)
        output = [bytearray(96 * 4) for _ in range(104)]
        clipped = 0
        for y in range(104):
            sy = min(h - 1, ((2 * y + 1) * h) // (2 * 104))
            for x in range(96):
                sx = min(w - 1, ((2 * x + 1) * w) // (2 * 96))
                pixel = rows[sy][sx * 4:sx * 4 + 4]
                if pixel[3] < 128:
                    continue
                if y + 5 >= 104:
                    clipped += 1
                    continue
                output[y + 5][x * 4:x * 4 + 4] = pixel[:3] + b'\xff'
        assert clipped == 0
        dest = ROOT.parent / 'frames' / f'{name}.png'
        png.write_png(dest, 96, 104, output)
        ow, oh, verified = png.read_png(dest)
        alpha = {row[i] for row in verified for i in range(3, 384, 4)}
        assert (ow, oh) == (96, 104) and alpha == {0, 255}
        assert dest.stat().st_size <= 256 * 1024
        points = [(x, y) for y, row in enumerate(verified) for x in range(96) if row[x * 4 + 3]]
        bbox = [min(x for x, y in points), min(y for x, y in points), max(x for x, y in points), max(y for x, y in points)]
        diff = [(x, y) for y in range(104) for x in range(96) if verified[y][x * 4:x * 4 + 4] != base[y][x * 4:x * 4 + 4]]
        head_alpha_diff = sum(verified[y][x * 4 + 3] != base[y][x * 4 + 3] for y in range(22, 56) for x in range(96))
        feet_y = max(y for x, y in points if 38 <= x < 58)
        assert feet_y == 93
        assert 4 <= bbox[0] and bbox[2] <= 91 and 4 <= bbox[1] and bbox[3] <= 99
        preview = [bytearray(b''.join(row[i:i + 4] * 4 for i in range(0, 384, 4))) for row in output for _ in range(4)]
        png.write_png(ROOT / f'{name}-preview-4x.png', 384, 416, preview)
        report.append({'frame': dest.name, 'source': source.name, 'sourceSize': [w, h],
                       'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                       'sampling': 'full canvas pixel-center nearest neighbor to 96x104; no crop',
                       'alphaThreshold': 128, 'integerOffset': [0, 5], 'clippedOpaqueSamples': clipped,
                       'frameSize': [ow, oh], 'frameBytes': dest.stat().st_size, 'alphaValues': sorted(alpha),
                       'inclusiveBounds': bbox, 'centralFeetBottomY': feet_y,
                       'changedPixelsVsNeutral': len(diff),
                       'headRegionChangedPixels': sum(y < 69 for x, y in diff),
                       'upperHeadAlphaChangesRows22to55': head_alpha_diff,
                       'frameSha256': hashlib.sha256(dest.read_bytes()).hexdigest()})
    assert hashlib.sha256(neutral.read_bytes()).hexdigest() == neutral_hash
    (ROOT / 'idle-export-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
