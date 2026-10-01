from pathlib import Path
import runpy,json,hashlib,re,base64
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'export-neutral.py'));load=lambda f:io['read_png'](f)[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();mask=set(map(tuple,json.loads((R/'art028-mask.json').read_text())['coordinatesXY']));report={}
for f in sorted((R/'art028-frames').glob('*.png')):
 wing,pose=f.stem.split('-');base=load(R/'art026-core'/({'A':'neutral','B':'soft-light','C':'soft-peak'}[wing]+'.png'));w,h,r=io['read_png'](f);assert(w,h)==(96,104) and f.read_bytes()[24:26]==bytes([8,6]);assert{q[i] for q in r for i in range(3,384,4)}=={0,255}
 if pose in ('mid','wink'):
  assert all(r[y][4*x:4*x+4]==base[y][4*x:4*x+4] for y in range(104) for x in range(96) if(x,y)not in mask)
  # Fixed center neckline remains opaque across changed/fixed row boundary.
  assert all(r[y][4*x+3]==255 for y in range(70,77) for x in range(44,52))
 else:assert f.read_bytes()==(R/'art027-frames'/f.name).read_bytes()
 report[f.name]={'sha256':sha(f),'outsideHeadMaskDiff':0,'format':'96x104 RGBA8 alpha0/255'}
for f,d in json.loads((R/'art028-protection.json').read_text()).items():assert sha(Path(f))==d
html=(R/'art028-demo.html').read_text(encoding='utf-8');images=json.loads(re.search(r'const images=(.*);',html)[1]);assert len(images)==15
for n,u in images.items():assert base64.b64decode(u.split(',')[1])==(R/'art028-frames'/(n+'.png')).read_bytes()
assert (R/'art028-engine.js').read_text(encoding='utf-8-sig') in html
(R/'art028-check-report.json').write_text(json.dumps({'status':'PASS','frames':report,'protectedInputsUnchanged':True,'neckSeamOpaque':True,'embeddedOriginalPNGs':15,'nativeAcceptance':False},indent=2),encoding='utf-8');print('PASS 15 PNGs:format/CRC/alpha,head-mask protection,opaque neck seam,original inputs and actual HTML bytes')
