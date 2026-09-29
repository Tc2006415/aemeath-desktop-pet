from pathlib import Path
import runpy,json,hashlib,re,base64
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'art032-png.py'));load=lambda p:io['read_png'](p)[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m={k:set(map(tuple,v)) for k,v in json.loads((R/'art032-mask.json').read_text()).items()};eyes=set(map(tuple,json.loads((R/'art027-eye-mask.json').read_text())['coordinatesXY']));roots=set(map(tuple,json.loads((R/'art026-mask-definition.json').read_text())['fixedRootCoordinatesXY']));meta=json.loads((R/'art032-build-report.json').read_text());report={}
for n,v in meta['frames'].items():
 f=R/'art032-frames'/(n+'.png');w,h,r=io['read_png'](f);a=load(R/'art026-core'/v['base']);assert(w,h)==(96,104) and f.read_bytes()[24:26]==bytes([8,6]);assert{row[i] for row in r for i in range(3,384,4)}=={0,255}
 allowed=set()
 if v['body']!='normal':allowed|=m['armsXY']
 if v['body'] in ['left','right']:allowed|=m['legsXY']
 if v['face']=='panic':allowed|=m['faceXY']-eyes
 elif v['face']=='annoyed':allowed|=m['faceXY']
 elif v['face']=='half':allowed|=eyes
 if v['wing']=='H':allowed|=m['releaseWingXY']-roots
 diff={(x,y) for y in range(104) for x in range(96) if r[y][x*4:x*4+4]!=a[y][x*4:x*4+4]};assert diff<=allowed,n+' protected pixels'
 assert all(r[y][4*x:4*x+4]==a[y][4*x:4*x+4] for x,y in roots)
 assert all(r[y][4*x+3] for y in range(73,78) for x in range(44,52))
 bottom={side:max(y for y in range(84,104) for x in xs if r[y][4*x+3]) for side,xs in [('left',range(41,48)),('right',range(48,55))]};assert max(bottom.values())<=95
 # Feet must remain connected to the body, rather than separate floating donor fragments.
 opaque={(x,y) for y in range(104) for x in range(96) if r[y][4*x+3]};seen={(47,75)};todo=list(seen)
 while todo:
  x,y=todo.pop()
  for p in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
   if p in opaque and p not in seen:seen.add(p);todo.append(p)
 feet={(x,y) for x,y in opaque if 41<=x<=54 and 87<=y};assert feet<=seen,n+' detached feet'
 report[n]={'sha256':sha(f),'outsideMaskDiff':0,'legBottom':bottom,'neckAndRootsExact':True,'feetConnected':True}
# Constant held body/mood across all wing phases, with the last and first loop phase both A.
a=load(R/'art032-frames/annoyed-annoyed-A.png')
for wing in 'BC':
 b=load(R/f'art032-frames/annoyed-annoyed-{wing}.png');assert all(a[y][4*x:4*x+4]==b[y][4*x:4*x+4] for y in range(104) for x in range(96) if (x,y) not in m['wingXY'])
for path,d in json.loads((R/'art032-protection.json').read_text()).items():assert sha(Path(path))==d
html=(R/'art032-demo.html').read_text(encoding='utf-8');imgs=json.loads(re.search(r'const images=(.*),\$=id=>',html)[1]);assert len(imgs)==62
for key,u in imgs.items():
 kind,n=key.split(':');folder='art029-frames' if kind=='idle' else 'art032-frames';assert base64.b64decode(u.split(',')[1])==(R/folder/(n+'.png')).read_bytes()
assert len(list(R.glob('art032-*-source-v*.png')))==6
out={'status':'PASS_FORMAT_PROTECTION_TRANSITIONS_ONLY','frames':report,'embeddedActualPNGs':62,'generationCalls':6,'compositeVersions':1,'heldFaceBodyConstant':True,'loopSeam':'same A PNG at both sides','nativeAcceptance':False,'visualLimitations':['hand lift/curl weak after frozen mask','downturned mouth lost at coarse sampling; annoyance mostly brow','generated stockings/shoe local layer shifts need user review','source wink/head and hem reset seam remains']};(R/'art032-check-report.json').write_text(json.dumps(out,indent=2));print(json.dumps({'status':out['status'],'pngs':len(report),'embedded':62,'feet':{n:v['legBottom'] for n,v in report.items() if n in ['left-panic-B','right-panic-C','annoyed-annoyed-A']},'heldFaceBodyConstant':True,'protectedInputsUnchanged':True},indent=2))
