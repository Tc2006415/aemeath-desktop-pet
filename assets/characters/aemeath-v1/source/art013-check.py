"""Read-back verification of final candidate, embedded preview and real host evidence."""
import base64
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
package=ROOT/'art013-package'
manifest=json.loads((package/'manifest.json').read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
neutral=png['read_png'](package/'frames/neutral.png')[2]
checks={}
for path in (ROOT/'art010-baseline/frames').glob('*.png'):
    assert path.read_bytes()==(package/'frames'/path.name).read_bytes()
for path in (package/'frames').glob('*.png'):
    w,h,rows=png['read_png'](path)
    assert (w,h)==(96,104) and path.stat().st_size<=262144
    assert sorted({r[i] for r in rows for i in range(3,384,4)})==[0,255]
    if path.stem.startswith(('hold-','pickup-','release-')):
        maskrows=png['read_png'](ROOT/f'art013-{path.stem}-union-mask.png')[2]
        mask={(x,y) for y in range(104) for x in range(96) if maskrows[y][x*4+3]}
        changes={(x,y) for y in range(104) for x in range(96) if rows[y][x*4:x*4+4]!=neutral[y][x*4:x*4+4]}
        assert not changes-mask
        checks[path.stem]={'changedPixels':len(changes),'outsideMaskRgbaChanges':0}
html=(ROOT/'art013-inspection.html').read_text(encoding='utf-8')
for p in (package/'frames').glob('*.png'):
    assert 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() in html
log=[json.loads(s) for s in (ROOT/'art013-host-hold.jsonl').read_text(encoding='utf-8-sig').splitlines()]
run=json.loads((ROOT/'art013-host-run.json').read_text(encoding='utf-8-sig'))
assert run['exitCode']==0 and run['manifestSha256'].lower()==sha(package/'manifest.json')
loads=[e for e in log if e['kind']=='package-loaded']
assert len(loads)==1 and loads[0]['data']['Version']=='0.4.0' and loads[0]['data']['disabled']==[]
sequence=[]
for e in log:
    if e['kind']=='frame' and e['data']['Action']=='drag-hold':
        if not sequence or sequence[-1]['index']!=e['data']['FrameIndex']:
            sequence.append({'ms':e['ms'],'index':e['data']['FrameIndex']})
wraps=sum(a['index']==3 and b['index']==0 for a,b in zip(sequence,sequence[1:]))
assert wraps>=3 and {e['index'] for e in sequence}=={0,1,2,3}
assert not any(e['kind'] in ('package-rejected','position-error') for e in log)
assert any(e['kind']=='shutdown' for e in log)
for name,times in [('drag-pickup',[80,80,100,100]),('drag-hold',[180]*4),('drag-release',[80,100,120,160])]:
    assert [f['durationMs'] for f in manifest['actions'][name]['frames']]==times
    for f in manifest['actions'][name]['frames']:assert (package/f['path']).is_file()
decoded=[png['read_png'](package/f['path'])[2] for f in manifest['actions']['drag-hold']['frames']]
for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
    for scale in [1,3]:
        out=[]
        for y in range(104):
            row=bytearray()
            for picture in decoded:
                for x in range(96):
                    p=picture[y][x*4:x*4+4]
                    row.extend((p if p[3] else bytes(bg))*scale)
            out.extend([row]*scale)
        png['write_png'](ROOT/f'art013-hold-{theme}-{scale}x.png',384*scale,104*scale,out)
report={'maskChecks':checks,'previewContainsExactCandidatePngBytes':True,'actualHostPid':run['pid'],'actualHostExit':0,'hostCompletedHoldLoops':wraps,'hostSequence':sequence,'manifestSha256':sha(package/'manifest.json')}
(ROOT/'art013-check-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='hostSequence'},indent=2))
