from pathlib import Path
import runpy,json,hashlib
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'export-neutral.py'));load=lambda f:io['read_png'](f)[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();cfg=json.loads((R/'art030-mask.json').read_text());body=set(map(tuple,cfg['bodyXY']));face=set(map(tuple,cfg['faceXY']));A=load(R/'art026-core/neutral.png');out=R/'art030-frames';out.mkdir(exist_ok=True);donors={};report={'generationCalls':2,'overallCompositeVersion':1,'sources':{},'frames':{}}
for pose in ['loose','tuck']:
 src=R/f'art030-{pose}-source-v1.png';w,h,raw=io['read_png'](src);assert w==h
 donor=[bytearray(384) for _ in range(104)]
 for y in range(48):
  for x in range(48):
   v=raw[(2*y+1)*h//96][(2*x+1)*w//96*4:(2*x+1)*w//96*4+4]
   if v[3]>=128:donor[y+56][(x+24)*4:(x+24)*4+4]=v[:3]+b'\xff'
 io['write_png'](R/f'art030-{pose}-donor-96.png',96,104,donor);donors[pose]=donor;report['sources'][pose]={'sha256':sha(src),'size':[w,h],'offset':[0,0]}
expr={'surprise':load(R/'art011-surprise-v1-donor.png'),'half':load(R/'art027-frames/A-half.png')}
report['expressionSources']={n:sha(R/f) for n,f in [('surprise','art011-surprise-v1-donor.png'),('half','art027-frames/A-half.png')]}
(out/'neutral.png').write_bytes((R/'art026-core/neutral.png').read_bytes())
for n,pose,e in [('surprise','loose','surprise'),('pickup','tuck','surprise'),('hold-entry','loose','half')]:
 rows=[bytearray(r) for r in A]
 for x,y in body:rows[y][4*x:4*x+4]=donors[pose][y][4*x:4*x+4]
 for x,y in face:rows[y][4*x:4*x+4]=expr[e][y][4*x:4*x+4]
 io['write_png'](out/(n+'.png'),96,104,rows)
 changed={(x,y) for y in range(104) for x in range(96) if rows[y][4*x:4*x+4]!=A[y][4*x:4*x+4]};assert changed<=body|face
 report['frames'][n]={'bodySource':pose,'expression':e,'sha256':sha(out/(n+'.png')),'changes':len(changed),'outsideMaskDiff':0,'feetY':max(y for y in range(84,104) for x in range(40,57) if rows[y][4*x+3])}
 big=[bytearray(b''.join(r[i:i+4]*6 for i in range(0,384,4))) for r in rows for _ in range(6)];io['write_png'](R/f'art030-{n}-6x.png',576,624,big)
(R/'art030-timing.json').write_text(json.dumps([{'name':n,'durationMs':d} for n,d in [('neutral',80),('surprise',80),('pickup',100),('hold-entry',100)]],indent=2),encoding='utf-8');(R/'art030-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
