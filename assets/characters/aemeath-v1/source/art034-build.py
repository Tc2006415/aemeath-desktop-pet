"""ART034 composite v1: only crop/NN sampling, alpha threshold and frozen masks."""
from pathlib import Path
import runpy,json,shutil
R=Path(__file__).resolve().parent
api=runpy.run_path(str(R/'art032-png.py'));read,write=api['read_png'],api['write_png']
mask=json.loads((R/'art034-mask.json').read_text(encoding='utf-8-sig'))
mw,mh,mr=read(R/'art034-mouth-generated.png')
sw,sh,sr=read(R/'art034-symbol-generated.png')
out=R/'art034-frames';out.mkdir(exist_ok=True)
for f in sorted((R/'art033-frames').glob('*.png')):
 if not f.name.startswith('annoyed-'):
  shutil.copyfile(f,out/f.name);continue
 w,h,rows=read(f)
 for x,y in mask['mouthXY']:
  sx=int((x-40+.5)*mw/16);sy=int((y-58+.5)*mh/16)
  rows[y][4*x:4*x+3]=mr[sy][4*sx:4*sx+3]
 for x,y in mask['symbolXY']:
  # Full generated glyph has 40px cells; exact donor crop [585,468,905,788).
  sx=585+(x-74)*40+20;sy=468+(y-28)*40+20
  p=bytearray(sr[sy][sx*4:sx*4+4]);p[3]=255 if p[3]>=128 else 0
  if p[3]:rows[y][x*4:x*4+4]=p
 write(out/f.name,w,h,rows)
for wing in ['C','H']:
 shutil.copyfile(R/'art033-frames'/f'annoyed-annoyed-{wing}.png',out/f'transition-annoyed-{wing}.png')
track=(R/'art033-track.js').read_text(encoding='utf-8-sig').replace('ART032','ART034')
track=track.replace("'pose:annoyed-annoyed-C'][i]","'pose:transition-annoyed-C'][i]")
(R/'art034-track.js').write_text(track,encoding='utf-8')
shutil.copyfile(R/'art033-timing.json',R/'art034-timing.json')
print('Composite v1: 4 changed annoyed frames, 13 identical frames, 2 unchanged transition aliases; 19 total.')
