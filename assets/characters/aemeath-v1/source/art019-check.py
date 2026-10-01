"""File-level contract audit, independent of the production loader."""
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
package=ROOT/'art019-package'
def unique(pairs):
    result={}
    for k,v in pairs:
        assert k not in result, f'duplicate key {k}'
        result[k]=v
    return result
m=json.loads((package/'manifest.json').read_bytes(),object_pairs_hook=unique)
assert m['schemaVersion']==2 and m['packageVersion']=='0.4.0'
assert m['packageId']=='aemeath-v1' and m['packageKind']=='character' and m['sourceScale']==1
assert m['frameSize']=={'width':96,'height':104} and m['anchor']=={'x':48,'y':94}
base=json.loads((ROOT/'art013-package/manifest.json').read_bytes())
formal=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
f=json.loads((formal/'manifest.json').read_bytes())
assert f['packageVersion']=='0.3.0'
for k in ['neutral','idle-soft','idle-smile']:assert m['actions'][k]==f['actions'][k]==base['actions'][k]
assert m['actions']['drag-pickup']==base['actions']['drag-pickup']
assert m['actions']['drag-release']['frames']==base['actions']['drag-release']['frames']
png=runpy.run_path(str(ROOT/'export-neutral.py'))
sources=json.loads((ROOT/'art019-source-report.json').read_bytes())['sources']
files={str(p.relative_to(package)).replace('\\','/') for p in (package/'frames').glob('*.png')}
assert len(files)==16 and files==set(sources)
for name in files:
    p=package/name
    assert p.read_bytes()==(ROOT/sources[name]['path']).read_bytes()
    w,h,rows=png['read_png'](p)
    assert (w,h)==(96,104) and {r[i] for r in rows for i in range(3,len(r),4)}=={0,255}
    assert p.stat().st_size<=262144
for p in (formal/'frames').glob('*.png'):assert p.read_bytes()==(package/'frames'/p.name).read_bytes()
for p in (ROOT/'art013-package/frames').glob('*.png'):assert p.read_bytes()==(package/'frames'/p.name).read_bytes()
actions=m['actions'];entries=actions['drag-release']['entrySequences']
assert set(entries)==files
expected={'hold-up-half':620,'hold-bridge-high':580,'hold-bridge-mid':540,'hold-bridge-low':500,'hold-half':460,'hold-down-half':500,'hold-mid-closed':460,'hold-surprise':500,'pickup-surprise':500,'neutral':160,'release-closed':380,'release-half':280,'soft-light':200,'soft-peak':200,'smile-half':200,'smile-closed':200}
checks={}
def validate(items):
    assert 0<len(items)<=64
    for item in items:
        assert set(item)=={'path','durationMs'} and item['path'] in files
        assert type(item['durationMs']) is int and 0<item['durationMs']<=60000
    assert sum(i['durationMs'] for i in items)<=60000
for name,action in actions.items():
    assert set(action)==({'origin','playback','frames','entrySequences'} if name=='drag-release' else {'origin','playback','frames'})
    validate(action['frames'])
for name,items in entries.items():
    validate(items)
    duration=sum(i['durationMs'] for i in items)
    assert items[0]['path']==name and items[-1]['path']=='frames/neutral.png'
    assert duration==expected[Path(name).stem]
    # Half-open deadline: last frame at end-1, complete exactly at end.
    def sample(t):
        for i,item in enumerate(items):
            if t<item['durationMs']:return i
            t-=item['durationMs']
        return None
    assert sample(0)==0 and sample(duration-1)==len(items)-1 and sample(duration) is None
    checks[name]={'items':len(items),'durationMs':duration,'firstMatchesKey':True,'lastNeutral':True,'fileLevelDeadlineChecks':True}
hold=actions['drag-hold']['frames']
mapping={'mid':'hold-half','b2':'hold-bridge-low','b4':'hold-bridge-mid','b7':'hold-bridge-high','up':'hold-up-half','down':'hold-down-half','closed':'hold-mid-closed'}
probe=json.loads((ROOT/'art018-build-report.json').read_bytes())['timing']['hold']
assert hold==[{'path':f'frames/{mapping[n]}.png','durationMs':d} for n,d in probe]
tails={
 'hold-up-half':['hold-up-half','hold-bridge-high','hold-bridge-mid','hold-bridge-low'],
 'hold-bridge-high':['hold-bridge-high','hold-bridge-mid','hold-bridge-low'],
 'hold-bridge-mid':['hold-bridge-mid','hold-bridge-low'],
 'hold-bridge-low':['hold-bridge-low'],
 'hold-down-half':['hold-down-half'],'hold-surprise':['hold-surprise'],'pickup-surprise':['pickup-surprise']}
R=actions['drag-release']['frames']
for name,prefix in tails.items():assert entries[f'frames/{name}.png']==[{'path':f'frames/{n}.png','durationMs':40} for n in prefix]+R
assert entries['frames/hold-half.png']==R
assert entries['frames/hold-mid-closed.png']==[{'path':'frames/hold-mid-closed.png','durationMs':80}]+R[1:]
assert entries['frames/neutral.png']==R[-1:]
assert entries['frames/release-closed.png']==R[1:]
assert entries['frames/release-half.png']==R[2:]
for name in ['soft-light','soft-peak','smile-half','smile-closed']:assert entries[f'frames/{name}.png']==[{'path':f'frames/{name}.png','durationMs':40}]+R[-1:]
assert len(hold)==20 and sum(i['durationMs'] for i in hold)==1440
assert [i for i,f in enumerate(hold) if f['path']=='frames/hold-mid-closed.png']==[18]
assert hold[18]['durationMs']==100
assert hold[0]['path']==actions['drag-pickup']['frames'][-1]['path']
assert actions['drag-release']['frames'][-1]['path']==actions['idle-soft']['frames'][0]['path']
basecount=sum(len(a['frames']) for a in actions.values());entrycount=sum(len(s) for s in entries.values())
assert (basecount,entrycount)==(41,63) and basecount+entrycount==104
assert sum((package/name).stat().st_size for name in files)<=8388608
report={'passed':True,'schemaVersion':2,'packageVersion':'0.4.0','pngCount':16,'baseItems':basecount,'entryItems':entrycount,'totalItems':104,'holdMs':1440,'baseReleaseMs':460,'baseline03FivePngsAndThreeActionsUnchanged':True,'allOriginal13PngsUnchanged':True,'entries':checks,'manifestSha256':hashlib.sha256((package/'manifest.json').read_bytes()).hexdigest(),'productionLoaderRun':False,'note':'File-level PNG CRC/alpha/metadata/source/coverage/deadline audit; not production loader or native acceptance.'}
(ROOT/'art019-check-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='entries'},indent=2))
