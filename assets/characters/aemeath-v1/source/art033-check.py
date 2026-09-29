from pathlib import Path
import json,runpy,hashlib,re,base64
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'art032-png.py'));load=lambda p:io['read_png'](p)[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m={k:set(map(tuple,v)) for k,v in json.loads((R/'art033-mask.json').read_text()).items()};out={}
def warm(r,mask):return sum(r[y][4*x]>120 and r[y][4*x]>r[y][4*x+1]*1.1 and r[y][4*x+1]>r[y][4*x+2]*1.2 and r[y][4*x+2]<140 for x,y in mask if y>=90)
for f in sorted((R/'art033-frames').glob('*.png')):
 w,h,r=io['read_png'](f);a=load(R/'art032-frames'/f.name);assert(w,h)==(96,104) and f.read_bytes()[24:26]==bytes([8,6]);assert{row[i] for row in r for i in range(3,384,4)}=={0,255}
 assert all(r[y][4*x+3]==a[y][4*x+3] for y in range(104) for x in range(96)),f.name+' alpha changed'
 kind='mouth' if f.stem.startswith('annoyed-') else 'left' if f.stem.startswith('left-') else 'right' if f.stem.startswith('right-') else None;mask=m['mouthXY' if kind=='mouth' else kind+'FootXY'] if kind else set();diff={(x,y) for y in range(104) for x in range(96) if r[y][4*x:4*x+4]!=a[y][4*x:4*x+4]};assert diff<=mask
 if not kind:assert f.read_bytes()==(R/'art032-frames'/f.name).read_bytes()
 info={'sha256':sha(f),'outsideMaskDiff':0,'changedPixels':len(diff),'alphaExact':True}
 if kind in ['left','right']:
  assert all(r[y][4*x:4*x+4]==a[y][4*x:4*x+4] for x,y in mask if max(a[y][4*x:4*x+3])<=70)
  info['ankleOrangePixels']={'before':warm(a,mask),'after':warm(r,mask)}
  info['legBottom']={side:max(y for y in range(84,104) for x in xs if r[y][4*x+3]) for side,xs in [('left',range(41,48)),('right',range(48,55))]}
 out[f.stem]=info
# The actual tiny PNG, not only the generator source, must contain a one-row downturn.
a=load(R/'art033-frames/annoyed-annoyed-A.png');pink={(x,y) for x,y in m['mouthXY'] if a[y][4*x]>180 and a[y][4*x+1]<150 and a[y][4*x]-a[y][4*x+1]>60};expected={(47,66),(48,66),(46,67),(49,67)};assert pink==expected,('mouth not clear4-pixel downturn',pink)
for wing in 'BCH':
 b=load(R/f'art033-frames/annoyed-annoyed-{wing}.png');assert all(a[y][4*x:4*x+4]==b[y][4*x:4*x+4] for x,y in m['mouthXY'])
for p,d in json.loads((R/'art033-protection.json').read_text()).items():assert sha(Path(p))==d
assert (R/'art033-track.js').read_bytes()==(R/'art032-track.js').read_bytes();assert (R/'art033-timing.json').read_bytes()==(R/'art032-timing.json').read_bytes()
html=(R/'art033-demo.html').read_text(encoding='utf-8');match=re.search(r'const images=(.*),oldImages=(.*),\$=id=>',html);new=json.loads(match[1]);old=json.loads(match[2]);assert len(new)==len(old)==62
for version,images in [('new',new),('old',old)]:
 for k,u in images.items():
  kind,n=k.split(':');folder='art029-frames' if kind=='idle' else 'art033-frames' if version=='new' else 'art032-frames';assert base64.b64decode(u.split(',')[1])==(R/folder/(n+'.png')).read_bytes()
assert (R/'art033-track.js').read_text(encoding='utf-8-sig') in html
report={'status':'PASS_TARGETED_CHECKS','frames':out,'actualMouthPinkXY':sorted(pink),'allOriginalAlphaExact':True,'unchangedControllerAndTiming':True,'beforeAfterSameLogicalFrame':True,'protectedInputsUnchanged':True,'imagegenCalls':3,'compositeVersions':1,'nativeAcceptance':False};(R/'art033-check-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'mouth':sorted(pink),'left':out['left-panic-A'],'right':out['right-panic-A'],'unchangedPNGCount':sum(v['changedPixels']==0 for v in out.values()),'embeddedNewAndOld':[len(new),len(old)]},indent=2))
