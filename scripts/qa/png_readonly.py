"""QA-only PNG reader; no writes or ART module dependencies."""
import struct
import zlib

def png(path, expected_size=(96,104)):
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
            assert (depth, color, compression, filtering, interlace) == (8,6,0,0,0)
            if expected_size is not None: assert (w,h)==expected_size
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
    if expected_size is not None: assert {p[3] for p in result} == {0,255}
    if expected_size is not None: assert len(raw) <= 262144
    return w, h, result
