"""Preview the final schema2 package bytes, not a separately authored timing table."""
import base64
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
package=ROOT/'art019-package'
manifest=json.loads((package/'manifest.json').read_bytes())
images={f'frames/{p.name}':'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for p in (package/'frames').glob('*.png')}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ART-019 schema2最终候选预览</title><style>body{font:15px system-ui;margin:16px;background:#eee;color:#222}button,select,input{font:inherit;padding:7px;margin:2px}h1{font-size:22px}p{margin:7px 0}.stage{display:flex;gap:10px}.box{background:#f0efeb;padding:8px}.dark{background:#1d222c;color:white}img{image-rendering:pixelated}.big{width:288px;height:312px}#status{background:white;padding:8px}.strip{display:flex;gap:3px;flex-wrap:wrap}.tile{font-size:12px}.tile img{display:block;width:48px;height:52px}</style>
<h1>ART-019 · schema2 / 0.4.0真实候选</h1><p>全部图与时序直接来自最终候选包。网页数组播放，不代表真实宿主加载、源帧选路或原生拖动验收。</p><p>16张图 · 基础41项 + 入口63项 = 104项 · hold1440ms · 中位直接R460ms</p>
<select id="mode" aria-label="动作或入口"></select><button id="replay">重播</button><button id="pause">暂停</button><button id="step">下一项</button><label>时间ms<input id="time" type="number" value="0" min="0"></label><button id="seek">定位并暂停</button>
<p id="status"></p><div class="stage"><div class="box">浅底3×<br><img id="light" class="big"></div><div class="box dark">深底3×<br><img id="dark" class="big"></div><div class="box">浅底1×<br><img id="one"></div><div class="box dark">深底1×<br><img id="oneDark"></div></div><p>入口由源PNG路径选择；每条数组首图等于源图，末图neutral。低位入口不强切高位。点击下方任一项暂停检查。</p><div class="strip" id="strip"></div>
<script>
const pack=PACKAGE,images=IMAGES,mode=document.querySelector('#mode');let epoch=performance.now(),elapsed=0,paused=false,currentIndex=0;
for(const name of Object.keys(pack.actions)){const o=document.createElement('option');o.value='action:'+name;o.textContent='动作 '+name;mode.append(o)}for(const name of Object.keys(pack.actions['drag-release'].entrySequences)){const o=document.createElement('option');o.value='entry:'+name;o.textContent='源入口 '+name;mode.append(o)}mode.value='action:drag-hold';
function selected(){let key=mode.value.slice(mode.value.indexOf(':')+1);return mode.value.startsWith('entry:')?{frames:pack.actions['drag-release'].entrySequences[key],playback:'once'}:pack.actions[key]}
const total=a=>a.reduce((s,f)=>s+f.durationMs,0);
function clock(){return paused?elapsed:performance.now()-epoch}
function draw(){const a=selected(),duration=total(a.frames),t=clock(),done=a.playback==='once'&&t>=duration;let rem=a.playback==='loop'?t%duration:t,i=0;while(i<a.frames.length-1&&rem>=a.frames[i].durationMs)rem-=a.frames[i++].durationMs;currentIndex=i;let path=done?'frames/neutral.png':a.frames[i].path;for(const id of ['light','dark','one','oneDark'])document.getElementById(id).src=images[path];document.querySelector('#status').textContent=`${paused?'暂停':'播放'} · ${Math.floor(t)}ms · ${done?'已结束':'项'+(i+1)} · ${path} · 总长${duration}ms · 翼周期${mode.value==='action:drag-hold'?Math.floor(t/720):0}`;requestAnimationFrame(draw)}
function jump(t){paused=true;elapsed=t;document.querySelector('#time').value=t;document.querySelector('#pause').textContent='继续'}
function reset(){epoch=performance.now();elapsed=0;paused=false;document.querySelector('#pause').textContent='暂停';const box=document.querySelector('#strip');box.replaceChildren();let start=0;selected().frames.forEach((f,i)=>{const t=start,b=document.createElement('button');b.className='tile';b.innerHTML=`<img src="${images[f.path]}">#${i+1} ${f.durationMs}ms<br>${f.path.replace('frames/','')}`;b.onclick=()=>jump(t);box.append(b);start+=f.durationMs;})}
mode.onchange=reset;document.querySelector('#replay').onclick=reset;document.querySelector('#pause').onclick=()=>{if(paused){epoch=performance.now()-elapsed;paused=false}else{elapsed=clock();paused=true}document.querySelector('#pause').textContent=paused?'继续':'暂停'};document.querySelector('#seek').onclick=()=>jump(Number(document.querySelector('#time').value));document.querySelector('#step').onclick=()=>{const a=selected();jump(total(a.frames.slice(0,currentIndex+1)))};reset();draw();
</script></html>'''
html=html.replace('PACKAGE',json.dumps(manifest)).replace('IMAGES',json.dumps(images))
(ROOT/'art019-inspection.html').write_text(html,encoding='utf-8')
assert json.loads(re.search(r'const pack=(.*?),images=',html).group(1))==manifest
embedded=json.loads(re.search(r',images=(.*?),mode=',html).group(1))
assert all(base64.b64decode(v.split(',')[1])==(package/k).read_bytes() for k,v in embedded.items())
report={'embeddedPngCount':len(embedded),'manifestMatchesFinalPackage':True,'allEmbeddedPngBytesMatch':True,'manifestSha256':hashlib.sha256((package/'manifest.json').read_bytes()).hexdigest(),'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'nativeRuntimeVerified':False}
(ROOT/'art019-preview-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
