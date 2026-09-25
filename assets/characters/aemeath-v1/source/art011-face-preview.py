"""Neutral/pickup-surprise/hold-half/release-closed contact sheets."""
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
names=['neutral','pickup-surprise','hold-half','release-closed']
decoded=[png['read_png'](ROOT/f'art011-package/frames/{n}.png')[2] for n in names]
for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
    for scale in [1,3]:
        out=[]
        for y in range(104):
            row=bytearray()
            for picture in decoded:
                for x in range(96):
                    p=picture[y][x*4:x*4+4]
                    row.extend((p if p[3] else bytes(bg))*scale)
            out.extend([row]*scale)
        png['write_png'](ROOT/f'art011-expression-keys-{theme}-{scale}x.png',384*scale,104*scale,out)
print('Keys:',names)
