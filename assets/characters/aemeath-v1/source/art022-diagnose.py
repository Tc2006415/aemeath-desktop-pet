"""Read-only pixel comparison and byte-preserving original-frame evidence."""
import base64
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FORMAL=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
SHOT=Path('C:/Users/bigxi/AppData/Local/Temp/codex-clipboard-ca3c24ec-3368-4d81-ae62-fd2b8154be22.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=runpy.run_path(str(ROOT/'export-neutral.py'))['read_png']
paths=[FORMAL/'manifest.json',*sorted((FORMAL/'frames').glob('*.png'))]
before={str(p):sha(p) for p in paths}
manifest=json.loads(paths[0].read_bytes())
assert len(paths)==17 and manifest['packageVersion']=='0.4.0'
assert sha(FORMAL/'frames/soft-light.png')=='bc9fe556ac774ad2ca7c77d03446cdc451159819712e7e4fc9b8b245b48dcd70'
assert sha(FORMAL/'frames/soft-peak.png')=='79d227136f70d87ccea3d7efa2ae94759f8868890c3ef87a984c2d8fcf045be2'
copies={}
for p in paths:
    dest=ROOT/('art022-formal-'+p.name)
    dest.write_bytes(p.read_bytes()); assert dest.read_bytes()==p.read_bytes()
    copies[p.stem]=dest
(ROOT/'art022-user-screenshot.png').write_bytes(SHOT.read_bytes())
rows={n:read(p)[2] for n,p in copies.items() if n!='manifest'}
neutral=rows['neutral']
regions={'whole':lambda x,y:True,'lowerSides':lambda x,y:y>=76 and (x<=35 or x>=60),'innerSideBand':lambda x,y:76<=y<=98 and (24<=x<=35 or 60<=x<=71),'outerSideBand':lambda x,y:76<=y<=98 and (x<=23 or x>=72)}
diff={}
for name,r in rows.items():
    points=[(x,y) for y in range(104) for x in range(96) if r[y][4*x:4*x+4]!=neutral[y][4*x:4*x+4]]
    diff[name]={'rgbaDiffVsNeutral':{n:sum(fn(x,y) for x,y in points) for n,fn in regions.items()},'diffBBox':([min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)] if points else None)}
usage={n:[] for n in rows}
for action,a in manifest['actions'].items():
    sequences={'frames':a['frames'],**a.get('entrySequences',{})}
    for sequence,frames in sequences.items():
        for i,f in enumerate(frames): usage[Path(f['path']).stem].append({'action':action,'sequence':sequence,'index':i,'durationMs':f['durationMs']})
report={'formalVersion':'0.4.0','requiredRepairCommit':'52ef940','protectedSHA':before,'screenshotSHA':sha(SHOT),'regionDefinitions':{'lowerSides':'y>=76, x<=35 or x>=60 (diagnostic rectangle, not an edit mask)','innerSideBand':'y76..98, x24..35 or x60..71','outerSideBand':'y76..98, x0..23 or x72..95'},'diffVsNeutral':diff,'usage':usage,'copiesByteIdentical':True}
(ROOT/'art022-evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
img=lambda p:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
order=['neutral','soft-light','soft-peak','smile-half','smile-closed','hold-surprise','pickup-surprise','hold-half','hold-bridge-low','hold-bridge-mid','hold-bridge-high','hold-up-half','hold-down-half','hold-mid-closed','release-closed','release-half']
cards=''.join(f'<article><h3>{n}</h3><div class="pair"><img width="288" height="312" src="{img(copies[n])}"><img class="dark" width="96" height="104" src="{img(copies[n])}"></div><p>下侧区域对neutral差分 {diff[n]["rgbaDiffVsNeutral"]["lowerSides"]}</p></article>' for n in order)
html='''<!doctype html><meta charset="utf-8"><title>ART-022 原图定位</title><style>body{font:15px system-ui;background:#f0efeb;margin:16px}img{image-rendering:pixelated}h1{font-size:22px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}article{border:1px solid #bbb;padding:8px}h3{margin:4px}.pair{display:flex;align-items:end}.dark{background:#1d222c}button{padding:8px}#compare{display:flex;gap:12px}#status{font-family:monospace}</style><h1>ART-022 原图定位 · 无修改像素</h1><p>PM修复后0.4，16张原PNG字节内嵌；此页是现状证据，不是新动作效果图。</p><div id="compare"><div>用户截图<br><img width="397" height="414" src="SCREEN"></div><div>正式 smile-closed 4×<br><img width="384" height="416" src="SMILE"></div></div><h2>原动作对照</h2><button id="soft">idle-soft 1400ms</button><button id="smile">idle-smile 1200ms 重播</button><p id="status"></p><img id="player" width="288" height="312"><h2>正式16帧：3×浅底 / 1×深底</h2><div class="grid">CARDS</div><script>const images=IMAGES,actions=ACTIONS;let current='idle-soft',start=performance.now();document.querySelector('#soft').onclick=()=>{current='idle-soft';start=performance.now()};document.querySelector('#smile').onclick=()=>{current='idle-smile';start=performance.now()};function tick(){const a=actions[current],total=a.frames.reduce((s,f)=>s+f.durationMs,0),t=performance.now()-start;let r=a.playback==='loop'?t%total:Math.min(t,total-1),i=0;while(i<a.frames.length-1&&r>=a.frames[i].durationMs)r-=a.frames[i++].durationMs;document.querySelector('#player').src=images[a.frames[i].path];document.querySelector('#status').textContent=current+' '+Math.floor(t)+'ms '+a.frames[i].path+' / '+total+'ms';requestAnimationFrame(tick)}tick()</script>'''
html=html.replace('SCREEN',img(SHOT)).replace('SMILE',img(copies['smile-closed'])).replace('CARDS',cards).replace('IMAGES',json.dumps({'frames/'+n+'.png':img(copies[n]) for n in order})).replace('ACTIONS',json.dumps(manifest['actions']))
(ROOT/'art022-inspection.html').write_text(html,encoding='utf-8')
assert before=={str(p):sha(p) for p in paths}
print(json.dumps(diff,indent=2))
print('PASS formal17 unchanged; byte-identical16 originals; repaired soft hashes; original manifest usage mapped')
