from pathlib import Path
import json,runpy,hashlib
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'art032-png.py'));load=lambda p:io['read_png'](p)[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m={k:set(map(tuple,v)) for k,v in json.loads((R/'art033-mask.json').read_text()).items()};donors={};report={'generationCalls':3,'compositeVersion':1,'sources':{},'frames':{}}
for name,y0 in [('mouth',59),('left',80),('right',80)]:
 src=R/f'art033-{name}-source.png';w,h,r=io['read_png'](src);assert w==h;rows=[bytearray(384) for _ in range(104)]
 for y in range(16):
  for x in range(16):
   sx=(2*x+1)*w//32;sy=(2*y+1)*h//32;v=r[sy][4*sx:4*sx+4]
   if v[3]>=128:rows[y+y0][4*(x+40):4*(x+40)+4]=v[:3]+b'\xff'
 f=R/f'art033-{name}-donor.png';io['write_png'](f,96,104,rows);donors[name]=rows;report['sources'][name]={'sha256':sha(src),'sourceSize':[w,h],'logicalCrop':[40,58 if name=='mouth' else 80,16,16],'offset':[0,1 if name=='mouth' else 0]}
out=R/'art033-frames';out.mkdir(exist_ok=True)
for f in sorted((R/'art032-frames').glob('*.png')):
 old=load(f);rows=[bytearray(r) for r in old];kind='mouth' if f.stem.startswith('annoyed-') else 'left' if f.stem.startswith('left-') else 'right' if f.stem.startswith('right-') else None;used=[];skipped=[]
 if kind:
  mask=m['mouthXY' if kind=='mouth' else kind+'FootXY']
  for x,y in mask:
   if kind!='mouth' and max(old[y][4*x:4*x+3])<=70:continue
   v=donors[kind][y][4*x:4*x+4]
   if not v[3]:skipped.append([x,y]);continue
   rows[y][4*x:4*x+3]=v[:3];used.append([x,y])
  io['write_png'](out/f.name,96,104,rows)
 else:(out/f.name).write_bytes(f.read_bytes())
 changes=sum(rows[y][4*x:4*x+4]!=old[y][4*x:4*x+4] for y in range(104) for x in range(96));report['frames'][f.stem]={'kind':kind,'changes':changes,'usedXY':used,'transparentDonorSkippedXY':skipped,'sha256':sha(out/f.name)}
 if f.stem in ['annoyed-annoyed-A','left-panic-B','right-panic-C']:
  io['write_png'](R/f'art033-{f.stem}-8x.png',768,832,[bytearray(b''.join(r[i:i+4]*8 for i in range(0,384,4))) for r in rows for _ in range(8)])
(R/'art033-build-report.json').write_text(json.dumps(report,indent=2));print('Composite1,17PNGs,original alpha retained; mouth and foot interiors only');print({k:{'changes':v['changes'],'skipped':len(v['transparentDonorSkippedXY'])} for k,v in report['frames'].items() if k.endswith('-A')})
