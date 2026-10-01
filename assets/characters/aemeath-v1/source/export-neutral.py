"""Deterministic, dependency-free ART-005 format conversion; no painted pixels."""
import hashlib
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT, THRESHOLD, DX, DY = 96, 104, 128, 0, 5


def read_png(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    pos, payload = 8, bytearray()
    while pos < len(data):
        size = struct.unpack_from('>I', data, pos)[0]
        kind, chunk = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + size]
        assert zlib.crc32(kind + chunk) == struct.unpack_from('>I', data, pos + 8 + size)[0]
        if kind == b'IHDR':
            w, h, depth, color, comp, filt, inter = struct.unpack('>IIBBBBB', chunk)
            assert (depth, color, comp, filt, inter) == (8, 6, 0, 0, 0)
        assert kind != b'acTL'
        if kind == b'IDAT':
            payload.extend(chunk)
        pos += size + 12
    raw = zlib.decompress(payload)
    stride = w * 4
    assert len(raw) == h * (stride + 1)
    rows, prev = [], bytearray(stride)
    for y in range(h):
        start = y * (stride + 1)
        mode, row = raw[start], bytearray(raw[start + 1:start + 1 + stride])
        assert mode in range(5)
        for i in range(stride):
            a, b, c = (row[i - 4] if i >= 4 else 0), prev[i], (prev[i - 4] if i >= 4 else 0)
            p = a + b - c
            pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
            predictor = a if pa <= pb and pa <= pc else b if pb <= pc else c
            row[i] = (row[i] + (0, a, b, (a + b) // 2, predictor)[mode]) & 255
        rows.append(row)
        prev = row
    return w, h, rows


def write_png(path, w, h, rows):
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(b''.join(b'\0' + row for row in rows), 9)) + chunk(b'IEND', b''))


def main():
    source = ROOT / 'neutral-generated-v3-edge-cleanup.png'
    w, h, rows = read_png(source)
    output = [bytearray(WIDTH * 4) for _ in range(HEIGHT)]
    clipped = 0
    for y in range(HEIGHT):
        sy = min(h - 1, ((2 * y + 1) * h) // (2 * HEIGHT))
        for x in range(WIDTH):
            sx = min(w - 1, ((2 * x + 1) * w) // (2 * WIDTH))
            pixel = rows[sy][sx * 4:sx * 4 + 4]
            if pixel[3] < THRESHOLD:
                continue
            tx, ty = x + DX, y + DY
            if not (0 <= tx < WIDTH and 0 <= ty < HEIGHT):
                clipped += 1
                continue
            output[ty][tx * 4:tx * 4 + 4] = pixel[:3] + b'\xff'
    assert clipped == 0, 'Integer translation would crop visible pixels'
    frame = ROOT.parent / 'frames' / 'neutral.png'
    frame.parent.mkdir(exist_ok=True)
    write_png(frame, WIDTH, HEIGHT, output)
    ow, oh, decoded = read_png(frame)
    alpha = [row[i] for row in decoded for i in range(3, len(row), 4)]
    assert (ow, oh) == (96, 104) and set(alpha) == {0, 255}
    assert frame.stat().st_size <= 256 * 1024
    points = [(x, y) for y, row in enumerate(decoded) for x in range(WIDTH) if row[x * 4 + 3]]
    bbox = [min(x for x, y in points), min(y for x, y in points), max(x for x, y in points), max(y for x, y in points)]
    preview = [bytearray(b''.join(row[i:i + 4] * 4 for i in range(0, len(row), 4))) for row in output for _ in range(4)]
    write_png(ROOT / 'neutral-preview-4x.png', WIDTH * 4, HEIGHT * 4, preview)
    report = {'source': source.name, 'sourceSize': [w, h], 'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'sampling': 'pixel-center nearest neighbor: floor((2*x+1)*sourceWidth/(2*96)); same for y/104',
              'alphaThreshold': THRESHOLD, 'integerOffset': [DX, DY], 'clippedOpaqueSamples': clipped,
              'frameSize': [ow, oh], 'frameBytes': frame.stat().st_size, 'alphaValues': sorted(set(alpha)),
              'opaquePixels': alpha.count(255), 'inclusiveBounds': bbox, 'frameSha256': hashlib.sha256(frame.read_bytes()).hexdigest()}
    (ROOT / 'neutral-export-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
