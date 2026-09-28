from pathlib import Path
import runpy,json,hashlib
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'export-neutral.py'));load=lambda f:io['read_png'](f)[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();mask=set(map(tuple,json.loads((R/'art029-mask.json').read_text())['coordinatesXY']));out=R/'art029-frames';out.mkdir(exist_ok=True);donors={};report={'generationCalls':3,'overallCompositeVersion':2,'sources':{},'frames':{}}
for pose,ver in [('light',1),('upper',2)]:
 src=R/f'art029-{pose}-source-v{ver}.png';w,h,raw=io['read_png'](src);assert w==h
 donor=[bytearray(384) for _ in range(104)]
 for y in range(48):
  for x in range(48):
   v=raw[(2*y+1)*h//96][(2*x+1)*w//96*4:(2*x+1)*w//96*4+4]
   if v[3]>=128:donor[y+56][(x+24)*4:(x+24)*4+4]=v[:3]+b'\xff'
 assert max(y for y in range(80,104) for x in range(42,54) if donor[y][4*x+3])==93
 io['write_png'](R/f'art029-{pose}-donor-96.png',96,104,donor);donors[pose]=donor
 report['sources'][pose]={'sha256':sha(src),'size':[w,h],'offset':[0,0],'feetY':93,'leftLowerEdgeY':[max([y for y in range(86,93) if donor[y][4*x+3]] or [0]) for x in range(34,39)]}
for src in sorted((R/'art028-frames').glob('*.png')):
 base=load(src)
 for pose in ['base','light','upper']:
  rows=[bytearray(r) for r in base];dest=out/(src.stem+'-'+pose+'.png')
  if pose=='base':dest.write_bytes(src.read_bytes())
  else:
   for x,y in mask:
    selected='upper' if pose=='upper' and x in (38,57) else 'light'
    rows[y][4*x:4*x+4]=donors[selected][y][4*x:4*x+4]
   io['write_png'](dest,96,104,rows)
  changes={(x,y) for y in range(104) for x in range(96) if rows[y][4*x:4*x+4]!=base[y][4*x:4*x+4]};assert changes<=mask
  report['frames'][dest.name]={'sha256':sha(dest),'changes':len(changes),'outsideHemDiff':0}
for pose in ['base','light','upper']:
 r=load(out/f'A-open-{pose}.png');big=[bytearray(b''.join(row[i:i+4]*6 for i in range(0,384,4))) for row in r for _ in range(6)];io['write_png'](R/f'art029-{pose}-6x.png',576,624,big)
(R/'art029-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'sources':report['sources'],'frameCount':len(report['frames']),'sample':{k:v for k,v in report['frames'].items() if k.startswith('A-open')}},indent=2))
