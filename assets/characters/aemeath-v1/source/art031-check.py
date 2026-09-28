from pathlib import Path
import json,runpy,hashlib,re,base64
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'export-neutral.py'));load=lambda p:io['read_png'](p)[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads((R/'art031-mask.json').read_text());foot=set(map(tuple,cfg['footXY']));mouth=set(map(tuple,cfg['mouthXY']));allowed=foot|mouth;meta=json.loads((R/'art031-build-report.json').read_text());results={};errors=[]
def ensure(v,msg):
 if not v:errors.append(msg)
def boundary(s):return {p for p in s if any((p[0]+dx,p[1]+dy) not in s for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)])}
def distance(a,b):return max(min(max(abs(x-u),abs(y-v)) for u,v in b) for x,y in a)
for stem,data in meta['frames'].items():
 f=R/'art031-frames'/(stem+'.png');w,h,r=io['read_png'](f);a=load(R/'art029-frames'/data['base']);ensure((w,h)==(96,104) and f.read_bytes()[24:26]==bytes([8,6]),stem+' format');ensure({q[i] for q in r for i in range(3,384,4)}=={0,255},stem+' alpha')
 diff={(x,y) for y in range(104) for x in range(96) if r[y][x*4:x*4+4]!=a[y][x*4:x*4+4]};ensure(diff<=allowed,stem+' protected diff');local={'outsideMaskDiff':len(diff-allowed),'sha256':sha(f),'changes':len(diff)}
 if data['foot']:
  old={(x,y) for x,y in foot if a[y][x*4+3]};new={(x,y) for x,y in foot if r[y][x*4+3]};d=max(distance(boundary(old),boundary(new)),distance(boundary(new),boundary(old)))
  holes=[(x,y) for x,y in foot if not r[y][x*4+3] and all(r[y+dy][(x+dx)*4+3] for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)])]
  ensure(d<=2,stem+' contour >2px');ensure(max(y for x,y in new)<=93,stem+' extends legs');ensure(not holes,stem+' alpha hole');ensure(abs(len(new)-len(old))<=2,stem+' area change >2');ensure(all(r[y][x*4+3] for x,y in old if y==90),stem+' attachment broken')
  local['feet']={'oldArea':len(old),'newArea':len(new),'contourChebyshevMax':d,'bottomY':max(y for x,y in new),'holes':holes,'silhouetteRemoved':sorted(old-new),'silhouetteAdded':sorted(new-old)}
 if stem.endswith('neutral'):ensure(f.read_bytes()==(R/'art029-frames'/data['base']).read_bytes(),stem+' neutral not original')
 if stem.endswith('hold-entry'):ensure(f.read_bytes()==(R/'art031-frames'/(stem.replace('hold-entry','pickup')+'.png')).read_bytes(),stem+' terminal differs')
 results[stem]=local
for path,digest in json.loads((R/'art031-protection.json').read_text()).items():ensure(sha(Path(path))==digest,'protected input changed '+path)
html=(R/'art031-demo.html').read_text(encoding='utf-8');imgs=json.loads(re.search(r'const images=(.*);',html)[1]);ensure(len(imgs)==81,'embed count')
for key,u in imgs.items():
 kind,n=key.split(':');folder='art029-frames' if kind=='idle' else 'art031-frames';ensure(base64.b64decode(u.split(',')[1])==(R/folder/(n+'.png')).read_bytes(),'embed '+key)
risks={}
for n in ['A-open-base','B-open-base','C-open-base','A-half-base','A-closed-base','C-wink-upper','B-open-light','C-open-upper']:
 wing,pose,hem=n.split('-');a=load(R/'art029-frames'/(n+'.png'));b=load(R/'art031-frames'/f'{wing}-{hem}-neutral.png');risks[n]=sum(a[y][x*4:x*4+4]!=b[y][x*4:x*4+4] for y in range(104) for x in range(96))
report={'status':'FAIL' if errors else 'PASS','errors':errors,'frames':results,'sourceToFirstDiff':risks,'rawEmbeddedPNGs':len(imgs),'nativeAcceptance':False,'visualFootAcceptance':False,'taskAcceptance':'FAIL_B_TOE_TUCK'};(R/'art031-check-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'errors':errors,'representativeFeet':results['A-base-pickup'].get('feet'),'sourceToFirstDiff':risks},indent=2));raise SystemExit(bool(errors))
