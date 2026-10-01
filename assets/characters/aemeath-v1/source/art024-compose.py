"""ART024 local generated RGBA only, no pose synthesis or registration."""
import hashlib,json,runpy,sys
from pathlib import Path
R=Path(__file__).resolve().parent
F=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
p=runpy.run_path(str(R/'export-neutral.py'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
pose,v=sys.argv[1],int(sys.argv[2]);assert pose in ['B','C'] and v in [1,2]
cfg=json.loads((R/'art024-mask-definition.json').read_text());mask={tuple(q) for q in cfg['maskCoordinatesXY']};roots={tuple(q) for q in cfg['fixedRootCoordinatesXY']}
assert sha(R/'art024-neutral-A.png')=='e2f90c5dc97a24b9dc7714776d575fafe56791b9dc568e03f152b111badbe6c8'
base=p['read_png'](R/'art024-neutral-A.png')[2]
source=R/f'art024-{pose}-v{v}-source.png';w,h,raw=p['read_png'](source)
assert abs((w/h)/(96/104)-1)<0.02
donor=[bytearray(384) for _ in range(104)]
for y in range(104):
    for x in range(96):
        q=raw[(2*y+1)*h//208][(2*x+1)*w//192*4:(2*x+1)*w//192*4+4]
        if q[3]>=128:donor[y][4*x:4*x+4]=q[:3]+b'\xff'
out=[bytearray(row) for row in base]
for x,y in mask:out[y][4*x:4*x+4]=donor[y][4*x:4*x+4]
p['write_png'](R/f'art024-{pose}-v{v}-donor-96.png',96,104,donor)
dest=R/f'art024-{pose}-v{v}-candidate-96.png';p['write_png'](dest,96,104,out)
changes={(x,y) for y in range(104) for x in range(96) if base[y][4*x:4*x+4]!=out[y][4*x:4*x+4]}
assert changes<=mask and not changes&roots
assert all(78<=y<=99 and (8<=x<=35 or 60<=x<=87) for x,y in changes)
assert all(sha(Path(f))==s for f,s in cfg['formalProtectedSHA'].items())
report={'pose':pose,'version':v,'sourceSHA':sha(source),'sourceSize':[w,h],'donorSHA':sha(R/f'art024-{pose}-v{v}-donor-96.png'),'candidateSHA':sha(dest),'maskSHA':sha(R/'art024-wing-mask-v1.png'),'changedPixelsVsA':len(changes),'changedXY':sorted(changes),'outsideMaskRgbaDiff':0,'fixedRootRgbaDiff':0,'format':'96x104 RGBA8 alpha0/255','conversion':'pixel-center nearest,alpha128; no translation/warp/pose transform','formalProtected17Unchanged':True,'visualGate':'pending'}
(R/f'art024-{pose}-v{v}-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print({k:q for k,q in report.items() if k!='changedXY'})
