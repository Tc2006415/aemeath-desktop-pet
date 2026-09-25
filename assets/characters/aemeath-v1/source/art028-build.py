import runpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;p=runpy.run_path(str(R/'export-neutral.py'));load=lambda f:p['read_png'](f)[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
mask=set(map(tuple,json.loads((R/'art028-mask.json').read_text())['coordinatesXY']));out=R/'art028-frames';out.mkdir(exist_ok=True);report={'generationCalls':3,'overallCompositeVersion':1,'poses':{}}
for pose,ver in [('mid',2),('wink',1)]:
 src=R/f'art028-{pose}-source-v{ver}.png';w,h,raw=p['read_png'](src);assert w==h
 donor=[bytearray(384) for _ in range(104)]
 for y in range(64):
  for x in range(64):
   v=raw[(2*y+1)*h//128][(2*x+1)*w//128*4:(2*x+1)*w//128*4+4]
   if v[3]>=128:donor[y+16][(x+16)*4:(x+16)*4+4]=v[:3]+b'\xff'
 p['write_png'](R/f'art028-{pose}-donor-96.png',96,104,donor)
 report['poses'][pose]={'sourceSize':[w,h],'sourceSHA':sha(src),'integerOffset':[0,0],'frames':{}}
 for wing,n in [('A','neutral'),('B','soft-light'),('C','soft-peak')]:
  base=load(R/'art026-core'/(n+'.png'));rows=[bytearray(r) for r in base]
  for x,y in mask:rows[y][4*x:4*x+4]=donor[y][4*x:4*x+4]
  f=out/f'{wing}-{pose}.png';p['write_png'](f,96,104,rows)
  changes={(x,y) for y in range(104) for x in range(96) if rows[y][4*x:4*x+4]!=base[y][4*x:4*x+4]};assert changes<=mask
  report['poses'][pose]['frames'][wing]={'sha256':sha(f),'changed':len(changes),'outsideMaskDiff':0}
 rows=load(out/f'A-{pose}.png');big=[bytearray(b''.join(r[i:i+4]*6 for i in range(0,384,4))) for r in rows for _ in range(6)];p['write_png'](R/f'art028-{pose}-6x.png',576,624,big)
for f in (R/'art027-frames').glob('*.png'):(out/f.name).write_bytes(f.read_bytes())
(R/'art028-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
