from pathlib import Path
import json,runpy,hashlib,re,base64
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'export-neutral.py'));load=lambda f:io['read_png'](f)[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();cfg=json.loads((R/'art030-mask.json').read_text());mask=set(map(tuple,cfg['bodyXY']+cfg['faceXY']));A=load(R/'art026-core/neutral.png');report={}
for f in (R/'art030-frames').glob('*.png'):
 w,h,r=io['read_png'](f);assert(w,h)==(96,104) and f.read_bytes()[24:26]==bytes([8,6]);assert{q[i] for q in r for i in range(3,384,4)}=={0,255}
 assert all(r[y][4*x:4*x+4]==A[y][4*x:4*x+4] for y in range(104) for x in range(96) if(x,y)not in mask)
 assert all(r[y][4*x+3] for y in range(73,77) for x in range(44,52))
 assert not any(r[y][4*x+3] for y in range(99,104) for x in range(35,61))
 if f.stem=='neutral':assert f.read_bytes()==(R/'art026-core/neutral.png').read_bytes()
 report[f.name]={'sha256':sha(f),'outsideMaskDiff':0,'neckSeamOpaque':True}
wing=set(map(tuple,json.loads((R/'art026-mask-definition.json').read_text())['maskCoordinatesXY']));assert not wing&mask
for f in (R/'art030-frames').glob('*.png'):
 r=load(f);assert all(r[y][4*x:4*x+4]==A[y][4*x:4*x+4] for x,y in wing)
for f,d in json.loads((R/'art030-protection.json').read_text()).items():assert sha(Path(f))==d
risks={}
for n in ['A-open-base','B-open-base','C-open-base','A-half-base','A-closed-base','C-wink-upper','B-open-light','C-open-upper']:
 r=load(R/'art029-frames'/(n+'.png'));diff=[(x,y) for y in range(104) for x in range(96) if r[y][4*x:4*x+4]!=A[y][4*x:4*x+4]];risks[n]={'sourceToNeutralChangedPixels':len(diff),'seamRisk':bool(diff)}
html=(R/'art030-demo.html').read_text(encoding='utf-8');imgs=json.loads(re.search(r'const images=(.*);',html)[1]);assert len(imgs)==49
for key,u in imgs.items():
 k,n=key.split(':');folder='art029-frames' if k=='idle' else 'art030-frames';assert base64.b64decode(u.split(',')[1])==(R/folder/(n+'.png')).read_bytes()
assert (R/'art030-track.js').read_text(encoding='utf-8-sig') in html
(R/'art030-check-report.json').write_text(json.dumps({'status':'PASS','frames':report,'sourceSeams':risks,'v2WingExact':True,'protectedInputsUnchanged':True,'rawEmbeddedPNGs':49,'nativeAcceptance':False},indent=2),encoding='utf-8');print(json.dumps({'status':'PASS','frames':4,'format':'96x104 RGBA8 alpha0/255','fixedRegionAndWingExact':True,'sourceSeams':risks},indent=2))
