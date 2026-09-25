import json,re,base64,runpy,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;io=runpy.run_path(str(R/'export-neutral.py'));mask=set(map(tuple,json.loads((R/'art027-eye-mask.json').read_text())['coordinatesXY']));report={}
for wing,n in [('A','neutral'),('B','soft-light'),('C','soft-peak')]:
 base=io['read_png'](R/'art026-core'/(n+'.png'))[2]
 for eye in ('open','half','closed'):
  f=R/'art027-frames'/f'{wing}-{eye}.png';w,h,rows=io['read_png'](f);assert (w,h)==(96,104) and f.read_bytes()[24:26]==bytes([8,6]);assert {r[i] for r in rows for i in range(3,384,4)}=={0,255}
  assert all(rows[y][4*x:4*x+4]==base[y][4*x:4*x+4] for y in range(104) for x in range(96) if (x,y) not in mask)
  if eye=='open':assert f.read_bytes()==(R/'art026-core'/(n+'.png')).read_bytes()
  report[f.name]={'outsideEyeDiff':0,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
for f,digest in json.loads((R/'art027-protection.json').read_text()).items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==digest
html=(R/'art027-demo.html').read_text(encoding='utf-8');images=json.loads(re.search(r'const images=(.*);',html)[1])
for key,uri in images.items():assert base64.b64decode(uri.split(',')[1])==(R/'art027-frames'/(key+'.png')).read_bytes()
(R/'art027-check-report.json').write_text(json.dumps({'frames':report,'ART026Unchanged':True,'rawEmbeddedPNG':9,'nativeAcceptance':False},indent=2),encoding='utf-8');print('PASS:9 PNG CRC/RGBA8/96x104/binary alpha; eye-only differences; exact open bytes; ART026 preserved; actual HTML embedded bytes')
