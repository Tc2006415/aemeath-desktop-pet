"""Read only the fixed ART-011 expressive candidate and accepted PM baseline."""
import base64
import hashlib
import json
from pathlib import Path
from png_readonly import png

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'artifacts/qa007-art-395fce2/assets/characters/aemeath-v1/source'
PACKAGE = SOURCE/'art011-package'
LIVE = Path('C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source/art011-package')
BASELINE = ROOT/'artifacts/qa007-production-164856a/assets/characters/aemeath-v1'
read = lambda p: png(p)[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pack = json.loads((PACKAGE/'manifest.json').read_bytes())
assert sha(PACKAGE/'manifest.json') == 'b76f67cee1464425c3881f3f401217a2c44e3b5e43bcd245bd4a4bc6915beedb'
assert {p.relative_to(PACKAGE) for p in PACKAGE.rglob('*') if p.is_file()} == {p.relative_to(LIVE) for p in LIVE.rglob('*') if p.is_file()}
for p in PACKAGE.rglob('*'):
    if p.is_file(): assert p.read_bytes() == (LIVE/p.relative_to(PACKAGE)).read_bytes()
original = json.loads((BASELINE/'manifest.json').read_bytes())
assert original['packageVersion']=='0.3.0' and pack['packageVersion']=='0.4.0'
assert pack['anchor']=={'x':48,'y':94} and len(pack['actions'])==6
for name,clip in original['actions'].items(): assert pack['actions'][name]==clip
for p in (BASELINE/'frames').glob('*.png'): assert p.read_bytes()==(PACKAGE/'frames'/p.name).read_bytes()
base=read(PACKAGE/'frames/neutral.png')
face={i for i,p in enumerate(read(SOURCE/'art011-face-mask.png')) if p[3]}
assert len(face)==222 and all(32<=i%96<=63 and 56<=i//96<=67 for i in face)
report={'candidateCommit':'395fce2504bde5e792739a4e9d83a0544300a4dd','productionCommit':'164856a2d5c362d23ec3c2bc2949382a8f6755cd','manifestSha256':sha(PACKAGE/'manifest.json'),'liveMatchesSnapshot':True,'baselineFivePngsAndThreeActionsUnchanged':True,'frames':{}}
# Check surprise source sampling independently, without executing ART generation/export code.
w,h,source=png(SOURCE/'art011-surprise-v1-source.png',expected_size=None)
donor=read(SOURCE/'art011-surprise-v1-donor.png')
for y in range(104):
    for x in range(96):
        expected=(0,0,0,0)
        if y>=5:
            p=source[((2*(y-5)+1)*h//208)*w + (2*x+1)*w//192]
            if p[3]>=128: expected=(*p[:3],255)
        assert donor[y*96+x]==expected
for path in sorted((PACKAGE/'frames').glob('*.png')):
    pixels=read(path); visible=[(i%96,i//96) for i,p in enumerate(pixels) if p[3]]
    bounds=[min(x for x,y in visible),min(y for x,y in visible),max(x for x,y in visible),max(y for x,y in visible)]
    assert bounds[0]>0 and bounds[2]<95 and bounds[1]==22 and bounds[3]<103
    changed={i for i,p in enumerate(pixels) if p!=base[i]}
    entry={'sha256':sha(path),'bytes':path.stat().st_size,'bounds':bounds,'rgbaChanges':len(changed)}
    name=path.stem
    if name not in ['neutral','soft-light','soft-peak','smile-half','smile-closed']:
        bodyname,expression=name.rsplit('-',1)
        body=read(SOURCE/f'art011-body-only-package/frames/{bodyname}.png') # donor evidence only, never host target
        expr=donor if expression=='surprise' else read(BASELINE/f'frames/smile-{expression}.png')
        union={i for i,p in enumerate(read(SOURCE/f'art011-{name}-union-mask.png')) if p[3]}
        components=['hold',bodyname] if bodyname.startswith('hold-') else [bodyname]
        expected_union=set(face)
        for component in components:
            expected_union|={i for i,p in enumerate(read(SOURCE/f'art011-{component}-mask.png')) if p[3]}
        assert union==expected_union and not changed-union
        assert all(p==(expr[i] if i in face else body[i]) for i,p in enumerate(pixels))
        assert all(p[3]==body[i][3] for i,p in enumerate(pixels))
        assert all(i//96>=75 or i in face for i in changed)
        entry.update(outsideUnion=0,faceAlphaChanges=0,faceChanges=sum(p!=body[i] for i,p in enumerate(pixels)),unionPixels=len(union))
    report['frames'][name]=entry
assert len(report['frames'])==12
for action,times,mode in [('drag-pickup',[80,80,100,100],'once'),('drag-hold',[180]*4,'loop'),('drag-release',[80,100,120,160],'once')]:
    clip=pack['actions'][action]
    assert [f['durationMs'] for f in clip['frames']]==times and clip['playback']==mode
hold=[(PACKAGE/f['path']).read_bytes() for f in pack['actions']['drag-hold']['frames']]
assert len(set(hold))==3 and hold[1]==hold[3]
assert pack['actions']['drag-pickup']['frames'][-1]['path']==pack['actions']['drag-hold']['frames'][0]['path']==pack['actions']['drag-release']['frames'][0]['path']
assert pack['actions']['drag-release']['frames'][-1]['path']=='frames/neutral.png'
html=(SOURCE/'art011-inspection.html').read_text(encoding='utf-8')
embedded,_=json.JSONDecoder().raw_decode(html.split('const pack=',1)[1])
images,_=json.JSONDecoder().raw_decode(html.split('images=',1)[1])
assert embedded==pack and len(images)==12
for name,data in images.items(): assert base64.b64decode(data.split(',',1)[1])==(PACKAGE/name).read_bytes()
report.update(checks='PASS',previewMatchesCandidate=True,holdUniqueFrames=3,surpriseSourceSamplingMatches=True)
(ROOT/'artifacts/qa007-pixels.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
