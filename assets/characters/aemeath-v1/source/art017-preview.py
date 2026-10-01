"""Local comparison loop only, without changing hold/release or sprite pixels."""
import base64
import hashlib
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
paths={'b4':'art014-v1-96.png','old':'art015-b7-v1-96.png','up':'art013-package/frames/hold-up-half.png'}
for v in [1,2]:
    if (ROOT/f'art017-v{v}-96.png').exists():paths[f'v{v}']=f'art017-v{v}-96.png'
frames={k:png['read_png'](ROOT/v)[2] for k,v in paths.items()}
images={k:'data:image/png;base64,'+base64.b64encode((ROOT/v).read_bytes()).decode() for k,v in paths.items()}
metrics={}
for k,rows in frames.items():
    sides={}
    for side in ['left','right']:
        pts={(x,y) for y in range(78,104) for x in range(96) if rows[y][x*4+3] and (x<=26 if side=='left' else x>=69)}
        short={(x,y) for x,y in pts if y>=90 and (14<=x<=26 if side=='left' else 69<=x<=81)}
        sides[side]={'outerX':(min if side=='left' else max)(x for x,y in pts),'shortFeatherBottomProxy':max(y for x,y in short),'shortRoiOpaqueCount':len(short),'rowExtentsY90to102':{str(y):[min(x for x,z in short if z==y),max(x for x,z in short if z==y)] for y in range(90,103) if any(z==y for x,z in short)}}
    metrics[k]=sides
for v in [k for k in paths if k.startswith('v')]:
    for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
        for scale in [1,3]:
            out=[]
            for y in range(104):
                row=bytearray()
                for k in ['b4','old',v,'up']:
                    for x in range(96):
                        p=frames[k][y][x*4:x*4+4];row.extend((p if p[3] else bytes(bg))*scale)
                out.extend([row]*scale)
            png['write_png'](ROOT/f'art017-{v}-compare-{theme}-{scale}x.png',384*scale,104*scale,out)
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ART-017 B7局部修绘对照</title><style>body{font:15px system-ui;margin:14px;background:#eee;color:#222}button,select{font:inherit;padding:7px}h1{font-size:22px;margin:8px 0}p{margin:7px 0}.themes{display:flex;gap:12px}.theme{background:#f0efeb;padding:8px}.dark{background:#1d222c;color:white}.pair{display:flex;gap:5px}.big{width:288px;height:312px}img{image-rendering:pixelated}#status{padding:8px;background:white}.strip img{width:96px;height:104px}</style>
<h1>ART-017 · B4 ⇄ B7 ⇄ 高位 · 新旧同步对照</h1><p>网页局部视觉探针，非原生验收；端姿态原字节，无位移、插值或混合。不改hold/release时序。</p>
<label>候选 <select id="candidate">OPTIONS</select></label><select id="speed" aria-label="播放速度"><option value="slow">观察速度：各120ms</option><option value="probe">原探针片段：50/50/100/50ms</option></select><button id="reset">重播</button><button id="pause">暂停</button><button id="step">下一项</button><p id="status"></p>
<div class="themes"><div class="theme">浅底3×<div class="pair"><div>旧B7路径<br><img id="oldLight" class="big"></div><div>新B7路径<br><img id="newLight" class="big"></div></div><div class="pair">1×旧<img id="oldOne">新<img id="newOne"></div></div><div class="theme dark">深底3×<div class="pair"><div>旧B7路径<br><img id="oldDark" class="big"></div><div>新B7路径<br><img id="newDark" class="big"></div></div><div class="pair">1×旧<img id="oldOneDark">新<img id="newOneDark"></div></div></div>
<p>点击定位：<button id="b4">B4</button><button id="b7">B7上行</button><button id="up">原高位</button><button id="back">B7回程</button></p><p>静态并排顺序：B4 / 旧B7 / 新B7 / 原高位</p><div id="strip" class="strip"></div>
<script>
const images=IMAGES,candidate=document.querySelector('#candidate'),speed=document.querySelector('#speed');let epoch=performance.now(),elapsed=0,paused=false,current=0;
function durations(){return speed.value==='slow'?[120,120,120,120]:[50,50,100,50]}
function render(){let t=paused?elapsed:performance.now()-epoch,d=durations(),total=d.reduce((a,b)=>a+b,0),r=t%total,i=0;while(i<3&&r>=d[i])r-=d[i++];current=i;let old=['b4','old','up','old'][i],fresh=['b4',candidate.value,'up',candidate.value][i];for(const id of ['oldLight','oldDark','oldOne','oldOneDark'])document.getElementById(id).src=images[old];for(const id of ['newLight','newDark','newOne','newOneDark'])document.getElementById(id).src=images[fresh];document.querySelector('#status').textContent=`${paused?'暂停':'播放'} · ${Math.floor(t)}ms · 项${i+1} ${['B4','B7上行','原高位','B7回程'][i]} · 往返${Math.floor(t/total)}次 · ${candidate.value}`;requestAnimationFrame(render)}
function jump(i){paused=true;elapsed=durations().slice(0,i).reduce((a,b)=>a+b,0);document.querySelector('#pause').textContent='继续'}
function reset(){epoch=performance.now();elapsed=0;paused=false;document.querySelector('#pause').textContent='暂停';document.querySelector('#strip').innerHTML=['b4','old',candidate.value,'up'].map(k=>`<img src="${images[k]}" alt="${k}">`).join('')}
document.querySelector('#reset').onclick=reset;candidate.onchange=reset;speed.onchange=reset;document.querySelector('#pause').onclick=()=>{if(paused){epoch=performance.now()-elapsed;paused=false}else{elapsed=performance.now()-epoch;paused=true}document.querySelector('#pause').textContent=paused?'继续':'暂停'};document.querySelector('#step').onclick=()=>jump((current+1)%4);for(const [i,id]of ['b4','b7','up','back'].entries())document.getElementById(id).onclick=()=>jump(i);reset();render();
</script></html>'''
html=html.replace('OPTIONS',''.join(f'<option value="{k}">{k}</option>' for k in paths if k.startswith('v'))).replace('IMAGES',json.dumps(images))
(ROOT/'art017-inspection.html').write_text(html,encoding='utf-8')
report={'sources':{k:{'path':v,'sha256':hashlib.sha256((ROOT/v).read_bytes()).hexdigest()} for k,v in paths.items()},'contourProxies':metrics,'embeddedBytesMatch':all(base64.b64decode(images[k].split(',')[1])==(ROOT/v).read_bytes() for k,v in paths.items()),'shortFeatherProxyNote':'ROI lower silhouette, not anatomical length or same-point tracking'}
(ROOT/'art017-contour-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2))
