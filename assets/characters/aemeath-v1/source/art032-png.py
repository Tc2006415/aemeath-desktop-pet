"""PNG RGB/RGBA format reader; no artwork operations."""
import struct,zlib
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
            assert depth==8 and color in (2,6) and (comp,filt,inter)==(0,0,0)
            channels=3 if color==2 else 4
        assert kind != b'acTL'
        if kind == b'IDAT':
            payload.extend(chunk)
        pos += size + 12
    raw = zlib.decompress(payload)
    stride = w * channels
    assert len(raw) == h * (stride + 1)
    rows, prev = [], bytearray(stride)
    for y in range(h):
        start = y * (stride + 1)
        mode, row = raw[start], bytearray(raw[start + 1:start + 1 + stride])
        assert mode in range(5)
        for i in range(stride):
            a, b, c = (row[i - channels] if i >= channels else 0), prev[i], (prev[i - channels] if i >= channels else 0)
            p = a + b - c
            pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
            predictor = a if pa <= pb and pa <= pc else b if pb <= pc else c
            row[i] = (row[i] + (0, a, b, (a + b) // 2, predictor)[mode]) & 255
        rows.append(row)
        prev = row
    if channels==3:
        rows=[bytearray(b"".join(row[i:i+3]+b"\xff" for i in range(0,len(row),3))) for row in rows]
    return w, h, rows


def write_png(path, w, h, rows):
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(b''.join(b'\0' + row for row in rows), 9)) + chunk(b'IEND', b''))
