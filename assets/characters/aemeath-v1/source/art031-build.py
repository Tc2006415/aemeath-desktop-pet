from pathlib import Path
import runpy,json,hashlib
R=Path(__file__).resolve().parent
io=runpy.run_path(str(R/'export-neutral.py'));load=lambda p:io['read_png'](p)[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads((R/'art031-mask.json').read_text());foot=set(map(tuple,cfg['footXY']));mouth=set(map(tuple,cfg['mouthXY']))
src=R/'art031-foot-source-v1.png';w,h,raw=io['read_png'](src);assert w==h
donor=[bytearray(384) for _ in range(104)]
for y in range(32):
 for x in range(32):
  sx=(2*x+1)*w//64;sy=(2*y+1)*h//64;v=raw[sy][4*sx:4*sx+4]
  if v[3]>=128:donor[y+72][4*(x+32):4*(x+32)+4]=v[:3]+b'\xff'
io['write_png'](R/'art031-foot-donor-96.png',96,104,donor)
expr=load(R/'art011-surprise-v1-donor.png');out=R/'art031-frames';out.mkdir(exist_ok=True)
report={'generationCalls':2,'compositeVersion':1,'sourceSHA256':sha(src),'sourceDimensions':[w,h],'mapping':'pixel-center nearest square to32x32 at32,72; alpha128; offset0','mouthSourceSHA256':sha(R/'art011-surprise-v1-donor.png'),'rejectedSourceV2SHA256':sha(R/'art031-foot-source-v2-rejected.png'),'visualFootAcceptance':False,'frames':{}}
for wing in 'ABC':
 for hem in ['base','light','upper']:
  for i,pose in enumerate(['neutral','surprise','pickup','hold-entry']):
   actual=wing if i==0 else {'A':'B','B':'C','C':'C'}[wing]
   base=R/'art029-frames'/f'{actual}-open-{hem}.png';rows=load(base)
   if i:
    for x,y in mouth:rows[y][4*x:4*x+4]=expr[y][4*x:4*x+4]
   if i>=2:
    for x,y in foot:rows[y][4*x:4*x+4]=donor[y][4*x:4*x+4]
   f=out/f'{wing}-{hem}-{pose}.png'
   if i==0:f.write_bytes(base.read_bytes())
   else:io['write_png'](f,96,104,rows)
   report['frames'][f.stem]={'base':base.name,'mouth':bool(i),'foot':i>=2,'sha256':sha(f)}
   if wing=='A' and hem=='base':io['write_png'](R/f'art031-{pose}-8x.png',768,832,[bytearray(b''.join(row[k:k+4]*8 for k in range(0,384,4))) for row in rows for _ in range(8)])
(R/'art031-build-report.json').write_text(json.dumps(report,indent=2))
(R/'art031-timing.json').write_text(json.dumps([{'name':n,'durationMs':d} for n,d in [('neutral',80),('surprise',80),('pickup',100),('hold-entry',100)]],indent=2))
print('Built36 PNGs; composite v1; model is approved ART029; only mouth/foot donors used')
