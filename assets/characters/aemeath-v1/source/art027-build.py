import runpy,json,hashlib,base64
from pathlib import Path
R=Path(__file__).resolve().parent;p=runpy.run_path(str(R/'export-neutral.py'));load=lambda f:p['read_png'](f)[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
mask=set(map(tuple,json.loads((R/'art027-eye-mask.json').read_text())['coordinatesXY']));out=R/'art027-frames';out.mkdir(exist_ok=True)
w,h,raw=p['read_png'](R/'art027-closed-source-v1.png');assert w==h
closed=[bytearray(384) for _ in range(104)]
for y in range(48):
 for x in range(48):
  v=raw[(2*y+1)*h//96][(2*x+1)*w//96*4:(2*x+1)*w//96*4+4]
  closed[y+40][(x+24)*4:(x+24)*4+4]=v[:3]+bytes([255 if v[3]>=128 else 0])
p['write_png'](R/'art027-closed-donor-96.png',96,104,closed)
halfsource=R/'art009-v1-package/frames/smile-half.png';half=load(halfsource)
report={'generationCalls':1,'compositeVersionsPerEyePose':{'half':1,'closed':1},'closedSourceSize':[w,h],'closedSourceSHA':sha(R/'art027-closed-source-v1.png'),'halfSource':str(halfsource),'halfSourceSHA':sha(halfsource),'maskPixels':len(mask),'frames':{}}
for wing,n in [('A','neutral'),('B','soft-light'),('C','soft-peak')]:
 src=R/'art026-core'/(n+'.png');base=load(src)
 for eye,donor in [('open',base),('half',half),('closed',closed)]:
  rows=[bytearray(r) for r in base]
  for x,y in mask:rows[y][4*x:4*x+4]=donor[y][4*x:4*x+4]
  dest=out/f'{wing}-{eye}.png'
  if eye=='open':dest.write_bytes(src.read_bytes())
  else:p['write_png'](dest,96,104,rows)
  changed=[(x,y) for y in range(104) for x in range(96) if rows[y][4*x:4*x+4]!=base[y][4*x:4*x+4]]
  assert set(changed)<=mask
  assert all(rows[y][4*x+3]==255 for x,y in mask)
  report['frames'][dest.name]={'sha256':sha(dest),'changes':len(changed),'outsideEyeDiff':0}
# Inspection enlargement uses exact repetition, not generated art.
for eye in ('half','closed'):
 rows=load(out/f'A-{eye}.png');big=[bytearray(b''.join(r[i:i+4]*6 for i in range(0,384,4))) for r in rows for _ in range(6)]
 p['write_png'](R/f'art027-{eye}-6x.png',576,624,big)
(R/'art027-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
