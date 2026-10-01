"""Five-level visual evidence and silhouette proxy; no new character pixels."""
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
report=json.loads((ROOT/'art015-report.json').read_text(encoding='utf-8'))
paths=[ROOT/'art013-package/frames/hold-half.png']
selected={}
for pose in ['b2','b7']:
    # v2 overcorrected both poses; retain v1 as the best available trial.
    selected[pose]=ROOT/f'art015-{pose}-v1-96.png'
paths.extend([selected['b2'],ROOT/'art014-v1-96.png',selected['b7'],ROOT/'art013-package/frames/hold-up-half.png'])
decoded=[png['read_png'](p)[2] for p in paths]
levels=[]
for p,rows in zip(paths,decoded):
    tips={}
    for side in ['left','right']:
        pts={(x,y) for y in range(78,104) for x in range(96) if rows[y][x*4+3] and (x<=23 if side=='left' else x>=72)}
        extreme=(min if side=='left' else max)(x for x,y in pts)
        pts={(x,y) for x,y in pts if (x<=extreme+1 if side=='left' else x>=extreme-1)}
        tips[side]=sum(y for x,y in pts)/len(pts)
    levels.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tipMeanY':tips})
for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
    for scale in [1,3]:
        result=[]
        for y in range(104):
            row=bytearray()
            for picture in decoded:
                for x in range(96):
                    pixel=picture[y][x*4:x*4+4]
                    row.extend((pixel if pixel[3] else bytes(bg))*scale)
            result.extend([row]*scale)
        dest=ROOT/f'art015-five-{theme}-{scale}x.png'
        png['write_png'](dest,480*scale,104*scale,result)
        assert png['read_png'](dest)==(480*scale,104*scale,result)
steps={side:[round(levels[i]['tipMeanY'][side]-levels[i+1]['tipMeanY'][side],3) for i in range(4)] for side in ['left','right']}
report['fiveLevelOrder']=levels
report['adjacentUpwardTipProxySteps']=steps
report['tipProxyMonotonic']=all(v>0 for values in steps.values() for v in values)
report['allAdjacentTipProxyStepsWithin3']=all(0<v<=3 for values in steps.values() for v in values)
(ROOT/'art015-five-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'levels':levels,'steps':steps,'monotonic':report['tipProxyMonotonic'],'within3':report['allAdjacentTipProxyStepsWithin3']},indent=2))
