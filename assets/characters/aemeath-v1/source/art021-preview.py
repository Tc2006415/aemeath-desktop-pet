"""Embed original neutral and two selected repaired PNGs; original idle timing."""
import base64
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FORMAL=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
paths={'neutral':FORMAL/'frames/neutral.png','soft-light':ROOT/'art021-soft-light-v1-m2-96.png','soft-peak':ROOT/'art021-soft-peak-v1-m2-96.png','old-light':ROOT/'art021-soft-light-original.png','old-peak':ROOT/'art021-soft-peak-original.png'}
images={n:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for n,p in paths.items()}
frames=json.loads((FORMAL/'manifest.json').read_bytes())['actions']['idle-soft']['frames']
assert sum(f['durationMs'] for f in frames)==1400
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ART-021 翅尾修复候选</title><style>body{font:15px system-ui;margin:14px;background:#eee;color:#222}button{padding:7px;font:inherit}h1{font-size:22px}p{margin:6px 0}.row{display:flex;gap:12px}.box{padding:8px;background:#f0efeb}.dark{background:#1d222c;color:white}img{image-rendering:pixelated}.s2{width:192px;height:208px}.s3{width:288px;height:312px}.images{display:flex;align-items:flex-end;gap:4px}.crop{position:relative;width:200px;height:130px;overflow:hidden;background:#1d222c}.crop img{position:absolute;width:960px;height:1040px;max-width:none;top:-870px}.old{font-size:13px}#status{background:white;padding:8px}</style>
<h1>ART-021 · idle-soft翅尾局部修复候选</h1><p>原neutral与修订light/peak，1400ms原时序。网页非原生验收；原图/候选PNG字节内嵌，不插值/位移。</p><button id="replay">重播</button><button id="pause">暂停</button><button id="neutral">neutral</button><button id="light">修light</button><button id="peak">修peak</button><p id="status"></p>
<div class="row"><div class="box">浅底1× / 2× / 3×<div class="images"><img id="l1"><img id="l2" class="s2"><img id="l3" class="s3"></div></div><div class="box dark">深底1× / 2× / 3×<div class="images"><img id="d1"><img id="d2" class="s2"><img id="d3" class="s3"></div></div></div>
<p>下方原→修对照，左右窗口均10×辅助；原正常分叉空隙保留，只有诊断5点从透明变为生成像素。</p><div class="row" id="compare"></div>
<script>
const images=IMAGES,frames=FRAMES;let start=performance.now(),elapsed=0,paused=false;
function draw(){let t=paused?elapsed:performance.now()-start,r=t%1400,i=0;while(i<frames.length-1&&r>=frames[i].durationMs)r-=frames[i++].durationMs;const n=frames[i].path.slice(7,-4);for(const id of ['l1','l2','l3','d1','d2','d3'])document.getElementById(id).src=images[n];document.querySelector('#status').textContent=`${paused?'暂停':'播放'} ${Math.floor(t)}ms · 项${i+1} ${n} · 周期${Math.floor(t/1400)}`;requestAnimationFrame(draw)}
function jump(t){paused=true;elapsed=t;document.querySelector('#pause').textContent='继续'}document.querySelector('#replay').onclick=()=>{start=performance.now();paused=false;document.querySelector('#pause').textContent='暂停'};document.querySelector('#pause').onclick=()=>{if(paused){start=performance.now()-elapsed;paused=false}else{elapsed=performance.now()-start;paused=true}document.querySelector('#pause').textContent=paused?'继续':'暂停'};document.querySelector('#neutral').onclick=()=>jump(0);document.querySelector('#light').onclick=()=>jump(400);document.querySelector('#peak').onclick=()=>jump(550);
document.querySelector('#compare').innerHTML=['old-light','soft-light','old-peak','soft-peak'].map(n=>`<div><p>${n}</p><img src="${images[n]}"><div class="crop"><img style="left:-140px" src="${images[n]}"></div><div class="crop"><img style="left:-620px" src="${images[n]}"></div></div>`).join('');draw();
</script></html>'''
html=html.replace('IMAGES',json.dumps(images)).replace('FRAMES',json.dumps(frames))
(ROOT/'art021-inspection.html').write_text(html,encoding='utf-8')
assert all(base64.b64decode(images[n].split(',')[1])==p.read_bytes() for n,p in paths.items())
(ROOT/'art021-preview-report.json').write_text(json.dumps({'sources':{n:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for n,p in paths.items()},'originalIdleSoftFrames':frames,'durationMs':1400,'embeddedBytesMatch':True,'nativeAcceptance':False},indent=2)+'\n',encoding='utf-8')
print('PASS unchanged1400ms, raw5 embedded PNGs')
