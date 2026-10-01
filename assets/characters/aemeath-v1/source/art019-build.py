"""Build ADR004 schema2 source candidate using byte-identical accepted PNGs."""
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PM=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/'art013-package';dest=ROOT/'art019-package'
adr=PM/'docs/adr/0004-release-entry-sequences.md'
(ROOT/'art019-frozen-adr.md').write_bytes(adr.read_bytes())
baseline=PM/'assets/characters/aemeath-v1'
assert json.loads((baseline/'manifest.json').read_bytes())['packageVersion']=='0.3.0'
protected=[ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png')),source/'manifest.json',*sorted((source/'frames').glob('*.png')),baseline/'manifest.json',*sorted((baseline/'frames').glob('*.png'))]
before={str(p):sha(p) for p in protected}
(dest/'frames').mkdir(parents=True,exist_ok=True)
sources={p.name:p for p in (source/'frames').glob('*.png')}
assert len(sources)==13
sources.update({'hold-bridge-low.png':ROOT/'art015-b2-v1-96.png','hold-bridge-mid.png':ROOT/'art014-v1-96.png','hold-bridge-high.png':ROOT/'art017-v1-96.png'})
for name,p in sources.items():(dest/'frames'/name).write_bytes(p.read_bytes())
manifest=json.loads((source/'manifest.json').read_bytes())
manifest['schemaVersion']=2
def frame(name,ms):return {'path':f'frames/{name}.png','durationMs':ms}
def seq(items):return [frame(name,ms) for name,ms in items]
L,M,H='hold-bridge-low','hold-bridge-mid','hold-bridge-high'
cycle=seq([('hold-half',80),(L,50),(M,50),(H,50),('hold-up-half',100),(H,50),(M,50),(L,50),('hold-half',100),('hold-down-half',140)])
hold=cycle+copy.deepcopy(cycle);hold[18]=frame('hold-mid-closed',100)
manifest['actions']['drag-hold']['frames']=hold
R=manifest['actions']['drag-release']['frames']
entries={}
def entry(name,items):entries[f'frames/{name}.png']=copy.deepcopy(items)
for name,bridges in [('hold-up-half',[H,M,L]),(H,[M,L]),(M,[L]),(L,[])]:entry(name,seq([(name,40)]+[(b,40) for b in bridges])+R)
entry('hold-half',R)
entry('hold-mid-closed',seq([('hold-mid-closed',80),('release-closed',100),('release-half',120),('neutral',160)]))
for name in ['hold-down-half','hold-surprise','pickup-surprise']:entry(name,[frame(name,40)]+R)
entry('neutral',[frame('neutral',160)])
entry('release-closed',seq([('release-closed',100),('release-half',120),('neutral',160)]))
entry('release-half',seq([('release-half',120),('neutral',160)]))
for name in ['soft-light','soft-peak','smile-half','smile-closed']:entry(name,seq([(name,40),('neutral',160)]))
manifest['actions']['drag-release']['entrySequences']=entries
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
assert before=={str(p):sha(p) for p in protected}
report={'adrCommit':'22799b4','adrSha256':sha(adr),'manifestSha256':sha(dest/'manifest.json'),'sources':{f'frames/{n}':{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for n,p in sources.items()},'baseline03ManifestSha256':sha(baseline/'manifest.json'),'protectedHashesUnchanged':before,'imagegenCalls':0,'pixelEdits':0}
(ROOT/'art019-source-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(report['manifestSha256'])
