from pathlib import Path
import json,runpy,hashlib
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'art032-png.py'));load=lambda p:io['read_png'](p)[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'art032-mask.json').read_text());m={k:set(map(tuple,v)) for k,v in m.items()};roots=set(map(tuple,json.loads((R/'art026-mask-definition.json').read_text())['fixedRootCoordinatesXY']))
expr=load(R/'art032-annoyed-face-donor-v1.png');panic=load(R/'art011-surprise-v1-donor.png');eyes=set(map(tuple,json.loads((R/'art027-eye-mask.json').read_text())['coordinatesXY']));mouth=m['faceXY']-eyes
sources={'left':'art032-panic-left-donor-v2.png','right':'art032-panic-right-donor-v1.png','annoyed':'art032-annoyed-body-donor-v1.png'}
bodies={k:load(R/v) for k,v in sources.items()};high=load(R/'art032-release-wings-donor-v1.png');out=R/'art032-frames';out.mkdir(exist_ok=True);report={'generationCalls':6,'compositeVersion':1,'frames':{}}
for body,face in [('left','panic'),('right','panic'),('annoyed','annoyed'),('normal','normal')]:
 for wing in 'ABCH':
  base=R/'art026-core'/({'A':'neutral','B':'soft-light','C':'soft-peak','H':'neutral'}[wing]+'.png');a=load(base);rows=[bytearray(r) for r in a];mask=set()
  if body!='normal':
   bm=m['armsXY']|(m['legsXY'] if body in ('left','right') else set());mask|=bm
   for x,y in bm:rows[y][4*x:4*x+4]=bodies[body][y][4*x:4*x+4]
  if face in ('panic','annoyed'):
   fm=mouth if face=='panic' else m['faceXY'];mask|=fm;src=panic if face=='panic' else expr
   for x,y in fm:rows[y][4*x:4*x+4]=src[y][4*x:4*x+4]
  if wing=='H':
   wm=m['releaseWingXY']-roots;mask|=wm
   for x,y in wm:rows[y][4*x:4*x+4]=high[y][4*x:4*x+4]
  stem=f'{body}-{face}-{wing}';f=out/(stem+'.png');io['write_png'](f,96,104,rows)
  changed={(x,y) for y in range(104) for x in range(96) if rows[y][4*x:4*x+4]!=a[y][4*x:4*x+4]};assert changed<=mask
  report['frames'][stem]={'base':base.name,'body':body,'face':face,'wing':wing,'changes':len(changed),'outsideMaskDiff':0,'sha256':sha(f),'legBottom':{side:max(y for y in range(84,104) for x in xs if rows[y][4*x+3]) for side,xs in [('left',range(41,48)),('right',range(48,55))]}}
  if (body,wing) in [('left','B'),('right','C'),('annoyed','A'),('annoyed','H')]:io['write_png'](R/f'art032-{body}-{wing}-8x.png',768,832,[bytearray(b''.join(r[i:i+4]*8 for i in range(0,384,4))) for r in rows for _ in range(8)])
# Recognized half blink is used only for 120ms release softening, never the held mood.
(out/'normal-half-B.png').write_bytes((R/'art027-frames/B-half.png').read_bytes())
report['frames']['normal-half-B']={'base':'soft-light.png','body':'normal','face':'half','wing':'B','sha256':sha(out/'normal-half-B.png')}
(R/'art032-build-report.json').write_text(json.dumps(report,indent=2));(R/'art032-timing.json').write_text(json.dumps({'panicMs':[60,140,140,140,140,80],'heldWingLoopMs':[400,150,550,150,150],'releaseMs':[60,100,100,120,160],'heldMood':'annoyed until release','earlyRelease':'captured last rendered PNG first','idleAfterRelease':'new epoch resets wink/blink/hem'},indent=2));print('composite v1:17 PNGs; six imagegen calls; fixed-mask composition only')
