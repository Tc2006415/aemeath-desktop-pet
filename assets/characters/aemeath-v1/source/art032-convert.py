from pathlib import Path
import runpy,json,hashlib
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'art032-png.py'));report={}
for name,x0,y0,size in [('panic-left',32,72,32),('panic-right',32,72,32),('annoyed-body',32,72,32),('annoyed-face',28,44,40),('release-wings',0,56,96)]:
 files=sorted(R.glob(f'art032-{name}-source-v*.png'))
 for src in files:
  w,h,raw=io['read_png'](src);assert w==h
  rows=[bytearray(384) for _ in range(104)]
  for y in range(min(size,104-y0)):
   for x in range(size):
    sx=(2*x+1)*w//(2*size);sy=(2*y+1)*h//(2*size);v=raw[sy][4*sx:4*sx+4]
    if v[3]>=128:rows[y+y0][4*(x+x0):4*(x+x0)+4]=v[:3]+b'\xff'
  target=R/(src.stem.replace('source','donor')+'.png');io['write_png'](target,96,104,rows)
  report[src.name]={'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sourceSize':[w,h],'map':[x0,y0,size],'offset':[0,0],'donor':target.name}
  if 'face' not in name and 'wing' not in name:
   report[src.name]['legBottom']={side:max([y for y in range(84,104) for x in xs if rows[y][4*x+3]],default=None) for side,xs in [('left',range(41,48)),('right',range(48,55))]}

(R/'art032-source-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
