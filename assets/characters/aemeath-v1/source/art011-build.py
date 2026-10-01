"""ART-011 candidate only: accepted pixels and explicit feather masks, no painting."""
import hashlib
import json
import runpy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
package=ROOT/'art011-body-only-package'
frames=package/'frames'
frames.mkdir(parents=True,exist_ok=True)
baseline=ROOT/'art010-baseline'
protected=[ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png'))]
before={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report={'newImagegenCalls':0,'formalHashes':before,'copiedFrames':{},'composites':{},'actions':{}}
for source in (baseline/'frames').glob('*.png'):
    (frames/source.name).write_bytes(source.read_bytes())
    assert (frames/source.name).read_bytes()==source.read_bytes()
    report['copiedFrames'][source.name]={'source':str(source.relative_to(ROOT)),'sha256':sha(source)}
for name,source in [('pickup','art010-pickup-v1-96.png'),('hold','art010-hold-v2-96.png'),('release','art010-release-r1-96.png')]:
    src=ROOT/source
    (frames/f'{name}.png').write_bytes(src.read_bytes())
    report['copiedFrames'][name+'.png']={'source':source,'sha256':sha(src)}
    masksource=ROOT/({'pickup':'art010-pickup-v1-mask.png','hold':'art010-hold-v2-mask.png','release':'art010-release-r1-mask.png'}[name])
    (ROOT/f'art011-{name}-mask.png').write_bytes(masksource.read_bytes())
    report['copiedFrames'][name+'.png']['maskSource']=masksource.name
hold=png['read_png'](frames/'hold.png')[2]
neutral=png['read_png'](frames/'neutral.png')[2]
for level in ['light','peak']:
    source=baseline/f'frames/soft-{level}.png'
    moving=png['read_png'](source)[2]
    maskpath=ROOT/f'art009-v1-soft-{level}-mask.png'
    maskrows=png['read_png'](maskpath)[2]
    mask={(x,y) for y in range(104) for x in range(96) if maskrows[y][x*4+3]}
    assert all((x<24 or x>71) and y>=83 for x,y in mask)
    out=[bytearray(r) for r in hold]
    for x,y in mask:
        out[y][x*4:x*4+4]=moving[y][x*4:x*4+4]
    dest=frames/f'hold-{level}.png'
    png['write_png'](dest,96,104,out)
    (ROOT/f'art011-hold-{level}-mask.png').write_bytes(maskpath.read_bytes())
    changed={(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4]!=hold[y][x*4:x*4+4]}
    assert changed and not changed-mask
    report['composites'][dest.name]={'baseSha256':sha(frames/'hold.png'),'donor':str(source.relative_to(ROOT)),'donorSha256':sha(source),'maskSha256':sha(maskpath),'outputSha256':sha(dest),'changedPixels':len(changed),'outsideMaskRgbaChanges':len(changed-mask),'maskCoordinatesXY':sorted(mask,key=lambda p:(p[1],p[0]))}
actions={}
for name,mode,poses,times in [
    ('drag-pickup','once',['neutral','hold','pickup','hold'],[80,80,100,100]),
    ('drag-hold','loop',['hold','hold-light','hold-peak','hold-light'],[180,180,180,180]),
    ('drag-release','once',['hold','release','release','neutral'],[80,100,120,160])]:
    actions[name]={'origin':'original','playback':mode,'frames':[{'path':f'frames/{p}.png','durationMs':t} for p,t in zip(poses,times)]}
    report['actions'][name]={'durationMs':sum(times),'items':len(times),'uniqueImages':len(set(poses))}
raw=(baseline/'manifest.json').read_bytes()
newline=b'\r\n' if b'\r\n' in raw else b'\n'
insert=raw.rfind(newline+b'  }')
assert insert>0
addition=json.dumps(actions,indent=2).splitlines()[1:-1]
addition=newline.join(('  '+line).encode() for line in addition)
modified=raw[:insert]+b','+newline+addition+raw[insert:]
modified=modified.replace(b'"packageVersion": "0.3.0"',b'"packageVersion": "0.4.0"',1)
(package/'manifest.json').write_bytes(modified)
assert raw==modified.replace(b','+newline+addition,b'',1).replace(b'"packageVersion": "0.4.0"',b'"packageVersion": "0.3.0"',1)
manifest=json.loads(modified)
original=json.loads(raw)
for name,action in original['actions'].items():
    assert action==manifest['actions'][name]
assert manifest['fallbackAction']=='neutral' and manifest['anchor']=={'x':48,'y':94}
report['baselineManifestPreservedExceptVersionAndAppendedActions']=True
report['pngChecks']={}
for f in frames.glob('*.png'):
    w,h,rows=png['read_png'](f)
    assert (w,h)==(96,104) and f.stat().st_size<=256*1024
    assert sorted({r[i] for r in rows for i in range(3,384,4)})==[0,255]
    headChanges=sum(rows[y][x*4:x*4+4]!=neutral[y][x*4:x*4+4] for y in range(75) for x in range(96))
    if f.stem in ['pickup','hold','release','hold-light','hold-peak']:
        assert headChanges==0
    report['pngChecks'][f.name]={'sha256':sha(f),'bytes':f.stat().st_size,'size':[w,h],'alpha':[0,255],'yBelow75ChangesFromNeutral':headChanges}
for a in manifest['actions'].values():
    for f in a['frames']:
        assert (package/f['path']).is_file()
assert before=={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
report['formalFilesUnchanged']=True
(ROOT/'art011-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actions':report['actions'],'pngCount':len(report['pngChecks']),'baselineBytesPreserved':True,'formalUnchanged':True},indent=2))
