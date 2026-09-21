"""Read back packaged PNGs, masks and actual host logs; produce contact sheets."""
import json
import hashlib
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
package=ROOT/'art011-package'
pack=json.loads((package/'manifest.json').read_bytes())
for p in (ROOT/'art010-baseline/frames').glob('*.png'):
    assert p.read_bytes()==(package/'frames'/p.name).read_bytes()
runs=json.loads((ROOT/'art011-expression-host-runs.json').read_text(encoding='utf-8-sig'))
assert all(r['exitCode']==0 and r['manifestSha256'].lower()==hashlib.sha256((package/'manifest.json').read_bytes()).hexdigest() for r in runs)
base=png['read_png'](package/'frames/neutral.png')[2]
checks={}
expressions=json.loads((ROOT/'art011-expression-report.json').read_text())
assert len(list((package/'frames').glob('*.png')))==12
for name in expressions['frames']:
    rows=png['read_png'](package/f'frames/{name}.png')[2]
    masks=[name+'-union']
    mask=set()
    for m in masks:
        mr=png['read_png'](ROOT/f'art011-{m}-mask.png')[2]
        mask|={(x,y) for y in range(104) for x in range(96) if mr[y][x*4+3]}
    changes={(x,y) for y in range(104) for x in range(96) if rows[y][x*4:x*4+4]!=base[y][x*4:x*4+4]}
    assert not changes-mask
    assert all(y>=75 or 32<=x<=63 and 56<=y<=67 for x,y in changes)
    checks[name]={'changes':len(changes),'outsideMaskChanges':len(changes-mask),'maskComponents':masks}
host={}
for action,total,times in [('drag-pickup',360,[80,80,100,100]),('drag-hold',720,[180]*4),('drag-release',460,[80,100,120,160])]:
    clip=pack['actions'][action]
    assert [f['durationMs'] for f in clip['frames']]==times and sum(times)==total
    log=[json.loads(line) for line in (ROOT/f'art011-expression-host-{action}.jsonl').read_text(encoding='utf-8-sig').splitlines()]
    loaded=[e for e in log if e['kind']=='package-loaded']
    assert len(loaded)==1 and loaded[0]['data']['Version']=='0.4.0' and loaded[0]['data']['disabled']==[]
    indices=sorted({e['data']['FrameIndex'] for e in log if e['kind']=='frame' and e['data']['Action']==action})
    assert indices==[0,1,2,3]
    assert any(e['kind']=='shutdown' for e in log)
    assert not any(e['kind'] in ('package-rejected','position-error') for e in log)
    host[action]={'indices':indices,'loadedVersion':'0.4.0','disabled':[]}
    decoded=[png['read_png'](package/f['path'])[2] for f in clip['frames']]
    for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
        for scale in [1,3]:
            out=[]
            for y in range(104):
                row=bytearray()
                for image in decoded:
                    for x in range(96):
                        p=image[y][x*4:x*4+4]
                        row.extend((p if p[3] else bytes(bg))*scale)
                out.extend([row]*scale)
            png['write_png'](ROOT/f'art011-{action}-{theme}-{scale}x.png',384*scale,104*scale,out)
summary={'neutralRelativeMaskChecks':checks,'actualHostLogs':host,'holdUniquePngBytes':len({(package/f['path']).read_bytes() for f in pack['actions']['drag-hold']['frames']})}
assert summary['holdUniquePngBytes']==3
(ROOT/'art011-check-report.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
