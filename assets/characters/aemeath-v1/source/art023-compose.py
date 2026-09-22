"""Only permitted format conversion and explicit local composite; zero registration."""
import hashlib,json,runpy,sys
from pathlib import Path
R=Path(__file__).resolve().parent
p=runpy.run_path(str(R/'export-neutral.py'))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
v=int(sys.argv[1]) if len(sys.argv)>1 else 1
config=json.loads((R/'art023-mask-definition.json').read_text())
mask={tuple(q) for q in config['maskCoordinatesXY']}
roots={tuple(q) for q in config['fixedRootCoordinatesXY']}
original=R/'art023-original-neutral.png'; base=p['read_png'](original)[2]
source=R/f'art023-v{v}-source.png'; w,h,raw=p['read_png'](source)
assert abs((w/h)/(96/104)-1)<0.02
donor=[bytearray(384) for _ in range(104)]
for y in range(104):
    for x in range(96):
        q=raw[(2*y+1)*h//208][(2*x+1)*w//192*4:(2*x+1)*w//192*4+4]
        if q[3]>=128:donor[y][4*x:4*x+4]=q[:3]+b'\xff'
p['write_png'](R/f'art023-v{v}-donor-96.png',96,104,donor)
out=[bytearray(r) for r in base]
for x,y in mask:out[y][4*x:4*x+4]=donor[y][4*x:4*x+4]
dest=R/f'art023-v{v}-candidate-96.png';p['write_png'](dest,96,104,out)
changes={(x,y) for y in range(104) for x in range(96) if out[y][4*x:4*x+4]!=base[y][4*x:4*x+4]}
assert not changes-mask and not changes&roots
assert all(8<=x<=35 or 60<=x<=87 for x,y in changes)
assert all(78<=y<=99 for x,y in changes)
assert p['read_png'](dest)==(96,104,out)
report={'generation':v,'compositeVersion':v,'maskVersion':1,'sourceSHA':sha(source),'sourceSize':[w,h],'originalSHA':sha(original),'donorSHA':sha(R/f'art023-v{v}-donor-96.png'),'candidateSHA':sha(dest),'maskSHA':config['maskSHA'],'format':'96x104 RGBA8 alpha0/255','conversion':'whole canvas pixel-center nearest and alpha128 only; no translation, rotation or warp','changedPixels':len(changes),'outsideMaskRgbaChanges':0,'fixedRootRgbaChanges':0,'outsideEnvelopeRgbaChanges':0,'changedXY':sorted(changes),'formalProtectedUnchanged':all(sha(Path(f))==s for f,s in config['formalProtectedSHA'].items()),'visualAcceptance':'pending'}
assert report['formalProtectedUnchanged']
(R/f'art023-v{v}-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print({k:v for k,v in report.items() if k!='changedXY'})
