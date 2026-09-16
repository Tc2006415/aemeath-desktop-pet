// Deliberately geometric diagnostic pixels, not character artwork. No external dependencies.
import { mkdirSync, writeFileSync } from 'node:fs';
import { deflateSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../assets/diagnostic/', import.meta.url));
mkdirSync(root + '/frames', { recursive: true });
function chunk(type, data) {
  const name = Buffer.from(type); let crc = 0xffffffff;
  for (const b of Buffer.concat([name, data])) {
    crc ^= b;
    for (let i = 0; i < 8; i++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  const head = Buffer.alloc(4), tail = Buffer.alloc(4);
  head.writeUInt32BE(data.length); tail.writeUInt32BE((~crc) >>> 0);
  return Buffer.concat([head, name, data, tail]);
}
for (const [index, name] of ['neutral', 'pose-a', 'pose-b'].entries()) {
  const raw = Buffer.alloc(104 * (96 * 4 + 1));
  for (let y = 0; y < 104; y++) for (let x = 0; x < 96; x++) {
    // Transparent margin; source-pixel grid, one/two/three bars and a fixed anchor cross.
    let color = null;
    if (x >= 8 && x < 88 && y >= 8 && y < 88) {
      color = [[46, 132, 204], [238, 157, 51], [111, 184, 102]][index];
      if (x % 8 === 0 || y % 8 === 0) color = [28, 35, 44];
      for (let bar = 0; bar <= index; bar++) if (x >= 23 + bar * 18 && x < 30 + bar * 18 && y >= 28 && y < 65) color = [255, 255, 255];
    }
    if ((x === 48 && y >= 90 && y <= 98) || (y === 94 && x >= 44 && x <= 52)) color = [255, 64, 128];
    if (color) { const offset = y * 385 + 1 + x * 4; raw.set([...color, 255], offset); }
  }
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(96); ihdr.writeUInt32BE(104, 4); ihdr[8] = 8; ihdr[9] = 6;
  writeFileSync(root + `/frames/${name}.png`, Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]));
}
const frame = (name, durationMs) => ({ path: `frames/${name}.png`, durationMs });
const action = (playback, frames) => ({ playback, origin: 'diagnostic', frames });
writeFileSync(root + '/manifest.json', JSON.stringify({ schemaVersion: 1, packageId: 'diagnostic-v1', packageVersion: '0.1.0', packageKind: 'diagnostic', sourceScale: 1, frameSize: { width: 96, height: 104 }, anchor: { x: 48, y: 94 }, fallbackAction: 'neutral', actions: {
  neutral: action('loop', [frame('neutral', 1000)]),
  'idle-soft': action('loop', [frame('neutral', 400), frame('pose-a', 200)]),
  'idle-smile': action('once', [frame('pose-b', 300), frame('neutral', 200)])
}}, null, 2) + '\n');
